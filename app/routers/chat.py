import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from supabase import Client
from app.database import get_supabase
from app.schemas.message import ChatRequest, ChatResponse, MessageResponse
from app.services.ollama_service import ollama_service
from app.services.gemini_service import gemini_service
from app.utils.helpers import get_current_user
router = APIRouter(prefix="/api/chat", tags=["chat"])
def verify_conversation_access(conversation_id: str, user_id: str, supabase: Client) -> dict:
    conv_result = supabase.table("conversations").select("*, projects(user_id, title, description, goals, reference_links, tags)").eq("id", conversation_id).execute()
    if not conv_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    conversation = conv_result.data[0]
    if conversation["projects"]["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    return conversation
def get_project_memory(project_id: str, supabase: Client) -> List[Dict[str, Any]]:
    result = supabase.table("project_memory").select("*").eq("project_id", project_id).execute()
    return result.data or []
def format_memory_context(memory: List[Dict[str, Any]]) -> str:
    if not memory:
        return ""
    formatted = []
    for mem in memory:
        mem_type = mem.get("memory_type", "unknown")
        title = mem.get("title", "Untitled")
        content = mem.get("content", {})
        if isinstance(content, dict):
            content_str = json.dumps(content, indent=2)
        else:
            content_str = str(content)
        formatted.append(f"[{mem_type.upper()}] {title}:\n{content_str}\n")
    return "\n".join(formatted)
def process_tool_call(tool_name: str, tool_input: Dict[str, Any], supabase: Client, project_id: str = None) -> Dict[str, Any]:
    if tool_name == "read_memory":
        project_id = tool_input.get("project_id")
        memory_type = tool_input.get("memory_type")
        query = supabase.table("project_memory").select("*").eq("project_id", project_id)
        if memory_type:
            query = query.eq("memory_type", memory_type)
        result = query.execute()
        return {"success": True, "memories": result.data or []}
    elif tool_name == "write_memory":
        project_id = tool_input.get("project_id")
        memory_type = tool_input.get("memory_type")
        title = tool_input.get("title")
        content = tool_input.get("content", {})
        memory_entry = {
            "project_id": project_id,
            "memory_type": memory_type,
            "title": title,
            "content": content
        }
        result = supabase.table("project_memory").insert(memory_entry).execute()
        return {"success": True, "id": result.data[0]["id"] if result.data else None}
    elif tool_name == "analyze_image":
        image_url = tool_input.get("image_url")
        question = tool_input.get("question")
        analysis = gemini_service.analyze_image_sync(image_url, question)
        return {"success": True, "analysis": analysis}
    return {"error": f"Unknown tool: {tool_name}"}
def extract_text_from_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
            elif isinstance(item, str):
                text_parts.append(item)
        return "\n".join(text_parts)
    if isinstance(content, dict):
        if content.get("type") == "text":
            return content.get("text", "")
        return str(content)
    return str(content)
@router.post("/{conversation_id}", response_model=ChatResponse)
async def chat(
    conversation_id: str,
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    conversation = verify_conversation_access(conversation_id, current_user["id"], supabase)
    user_message = {
        "conversation_id": conversation_id,
        "role": "user",
        "content": request.message,
        "metadata": {}
    }
    if request.image_url:
        user_message["metadata"]["image_url"] = request.image_url
    user_result = supabase.table("messages").insert(user_message).execute()
    if not user_result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save user message"
        )
    messages_result = supabase.table("messages").select("*").eq("conversation_id", conversation_id).order("created_at").execute()
    history = messages_result.data or []
    chat_messages = []
    for msg in history[:-1]:
        role = msg["role"]
        if role == "system":
            continue
        content = msg["content"]
        chat_messages.append({
            "role": role,
            "content": content
        })
    current_msg = history[-1]
    chat_messages.append({
        "role": "user",
        "content": current_msg["content"]
    })
    project = conversation["projects"]
    project_id = conversation["project_id"]
    memory = get_project_memory(project_id, supabase)
    memory_context = format_memory_context(memory)
    system_prompt = ollama_service.build_system_prompt(project, memory_context)
    # Tool Loop: Allow multiple tool executions
    max_tool_calls = 3
    final_response_text = None
    
    for iteration in range(max_tool_calls):
        response = ollama_service.chat(chat_messages, system_prompt)
        response_text = response.get("content", "")
        
        # Check for tool call
        tool_call = ollama_service.parse_tool_call(response_text)
        
        if tool_call:
            tool_name = tool_call.get("tool")
            tool_input = tool_call.get("input", {})
            
            # Ensure project_id is in tool input
            if "project_id" not in tool_input and project_id:
                tool_input["project_id"] = project_id
            
            # Execute tool
            tool_result = process_tool_call(tool_name, tool_input, supabase, project_id)
            
            # Add tool result to messages
            chat_messages.append({
                "role": "assistant",
                "content": response_text
            })
            chat_messages.append({
                "role": "user",
                "content": f"[TOOL_RESULT]\n{json.dumps(tool_result)}\n[/TOOL_RESULT]"
            })
            
            # Continue loop to get final response
            continue
        else:
            # No tool call - this is the final response
            final_response_text = response_text
            break
    else:
        # Max iterations reached
        final_response_text = final_response_text or "I've processed your request."
    # Clean up response (remove any tool call markers if still present)
    if final_response_text:
        final_response_text = re.sub(r'\[TOOL_CALL\].*?\[/TOOL_CALL\]', '', final_response_text, flags=re.DOTALL).strip()
    assistant_message = {
        "conversation_id": conversation_id,
        "role": "assistant",
        "content": final_response_text,
        "metadata": {}
    }
    assistant_result = supabase.table("messages").insert(assistant_message).execute()
    if not assistant_result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save assistant message"
        )
    return ChatResponse(
        message=MessageResponse(**user_result.data[0]),
        assistant_message=MessageResponse(**assistant_result.data[0])
    )
@router.get("/{conversation_id}/history")
async def get_chat_history(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    verify_conversation_access(conversation_id, current_user["id"], supabase)
    result = supabase.table("messages").select("*").eq("conversation_id", conversation_id).order("created_at").execute()
    return result.data or []