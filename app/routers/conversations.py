from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from supabase import Client
from app.database import get_supabase
from app.schemas.conversation import ConversationCreate, ConversationResponse, ConversationWithMessages
from app.utils.helpers import get_current_user

router = APIRouter(tags=["conversations"])


def verify_project_access(project_id: str, user_id: str, supabase: Client) -> bool:
    result = supabase.table("projects").select("id").eq("id", project_id).eq("user_id", user_id).execute()
    return len(result.data) > 0


@router.get("/api/projects/{project_id}/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    if not verify_project_access(project_id, current_user["id"], supabase):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    result = supabase.table("conversations").select("*").eq("project_id", project_id).order("created_at", desc=True).execute()
    return result.data or []


@router.post("/api/projects/{project_id}/conversations", response_model=ConversationResponse)
async def create_conversation(
    project_id: str,
    conversation_data: ConversationCreate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    if not verify_project_access(project_id, current_user["id"], supabase):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    conversation = {
        "project_id": project_id,
        "title": conversation_data.title or f"Conversation"
    }

    result = supabase.table("conversations").insert(conversation).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )

    return result.data[0]


@router.get("/api/conversations/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    conv_result = supabase.table("conversations").select("*").eq("id", conversation_id).execute()
    if not conv_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    conversation = conv_result.data[0]

    if not verify_project_access(conversation["project_id"], current_user["id"], supabase):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    messages_result = supabase.table("messages").select("*").eq("conversation_id", conversation_id).order("created_at").execute()

    return {
        **conversation,
        "messages": messages_result.data or []
    }


@router.delete("/api/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    conv_result = supabase.table("conversations").select("project_id").eq("id", conversation_id).execute()
    if not conv_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    if not verify_project_access(conv_result.data[0]["project_id"], current_user["id"], supabase):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    supabase.table("conversations").delete().eq("id", conversation_id).execute()

    return {"message": "Conversation deleted successfully"}
