import json
from typing import Dict, Any, List
from supabase import Client
from app.database import get_supabase
from app.services.agent_service import agent_service
from app.services.ollama_service import ollama_service


class MemoryAgent:
    def __init__(self):
        pass

    def create_execution(self, project_id: str) -> Dict[str, Any]:
        return agent_service.create_execution(
            project_id=project_id,
            agent_type="memory_organizer",
            input_data={}
        )

    def run_async(self, execution_id: str):
        import threading
        thread = threading.Thread(target=self.run, args=(execution_id,))
        thread.daemon = True
        thread.start()

    def run(self, execution_id: str):
        try:
            agent_service.update_execution(execution_id, "running")

            supabase: Client = get_supabase()
            execution = agent_service.get_execution(execution_id)
            project_id = execution["project_id"]

            project_result = supabase.table("projects").select("*").eq("id", project_id).execute()
            if not project_result.data:
                raise Exception("Project not found")

            project = project_result.data[0]

            conversations_result = supabase.table("conversations").select("*").eq("project_id", project_id).execute()
            conversations = conversations_result.data or []

            all_messages = []
            for conv in conversations:
                messages_result = supabase.table("messages").select("*").eq("conversation_id", conv["id"]).execute()
                all_messages.extend(messages_result.data or [])

            memory_result = supabase.table("project_memory").select("*").eq("project_id", project_id).execute()
            existing_memory = memory_result.data or []

            organized_memory = self.organize_project_data(project, all_messages, existing_memory)

            self.save_organized_memory(supabase, project_id, organized_memory)

            output_data = {
                "memories_created": len(organized_memory),
                "project_title": project.get("title"),
                "conversations_processed": len(conversations),
                "messages_processed": len(all_messages)
            }

            agent_service.update_execution(
                execution_id,
                "completed",
                output_data=output_data
            )

        except Exception as e:
            agent_service.update_execution(
                execution_id,
                "failed",
                error_message=str(e)
            )

    def organize_project_data(
        self,
        project: Dict[str, Any],
        messages: List[Dict[str, Any]],
        existing_memory: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        conversation_text = self.format_conversation_history(messages)
        existing_memory_text = self.format_existing_memory(existing_memory)

        prompt = f"""Analyze this project data and create structured memory entries.

Project:
- Title: {project.get('title', 'N/A')}
- Description: {project.get('description', 'N/A')}
- Goals: {project.get('goals', 'N/A')}
- Tags: {', '.join(project.get('tags', []) or ['None'])}

Existing Memory:
{existing_memory_text}

Recent Conversations:
{conversation_text}

Create memory entries in these categories:
1. context - Project background, team info
2. decisions - Key decisions made
3. todos - Action items needed
4. facts - Important facts, requirements
5. concepts - Technical concepts, terminology

Return as JSON array like:
[
  {{"memory_type": "context", "title": "Project Overview", "content": {{"summary": "..."}}}},
  {{"memory_type": "decisions", "title": "Technology Choice", "content": {{"decision": "...", "rationale": "..."}}}}
]

Only return valid JSON, no other text."""

        messages_for_llm = [{"role": "user", "content": prompt}]
        system_prompt = "You are a helpful assistant that organizes project information into structured JSON."

        response = ollama_service.chat(messages_for_llm, system_prompt)
        response_text = response.get("content", "[]")

        try:
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                memory_entries = json.loads(response_text[json_start:json_end])
                if isinstance(memory_entries, list):
                    return memory_entries
        except json.JSONDecodeError:
            pass

        return []

    def format_conversation_history(self, messages: List[Dict[str, Any]]) -> str:
        if not messages:
            return "No conversation history yet."

        formatted = []
        for msg in messages[-50:]:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            formatted.append(f"[{role.upper()}]: {content}")

        return "\n".join(formatted)

    def format_existing_memory(self, memory: List[Dict[str, Any]]) -> str:
        if not memory:
            return "No existing memory."

        formatted = []
        for mem in memory:
            mem_type = mem.get("memory_type", "unknown")
            title = mem.get("title", "Untitled")
            content = mem.get("content", {})

            if isinstance(content, dict):
                content_str = json.dumps(content, indent=2)
            else:
                content_str = str(content)

            formatted.append(f"\n[{mem_type.upper()} - {title}]:\n{content_str}\n")

        return "\n".join(formatted)

    def save_organized_memory(
        self,
        supabase: Client,
        project_id: str,
        organized_memory: List[Dict[str, Any]]
    ):
        for mem in organized_memory:
            memory_entry = {
                "project_id": project_id,
                "memory_type": mem.get("memory_type", "context"),
                "title": mem.get("title", "Untitled"),
                "content": mem.get("content", {})
            }
            supabase.table("project_memory").insert(memory_entry).execute()


memory_agent = MemoryAgent()
