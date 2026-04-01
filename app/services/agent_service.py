from datetime import datetime
from typing import Dict, Any, Optional, List
from supabase import Client
from app.database import get_supabase


class AgentService:
    def __init__(self):
        pass

    def create_execution(
        self,
        project_id: str,
        agent_type: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        supabase: Client = get_supabase()

        execution = {
            "project_id": project_id,
            "agent_type": agent_type,
            "status": "pending",
            "input_data": input_data or {},
            "output_data": {},
            "created_at": datetime.utcnow().isoformat()
        }

        result = supabase.table("agent_executions").insert(execution).execute()

        if result.data:
            return result.data[0]
        raise Exception("Failed to create agent execution")

    def update_execution(
        self,
        execution_id: str,
        status: str,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        supabase: Client = get_supabase()

        update_data: Dict[str, Any] = {
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        }

        if status == "running":
            update_data["started_at"] = datetime.utcnow().isoformat()
        elif status in ["completed", "failed"]:
            update_data["completed_at"] = datetime.utcnow().isoformat()

        if output_data is not None:
            update_data["output_data"] = output_data

        if error_message is not None:
            update_data["error_message"] = error_message

        result = supabase.table("agent_executions").update(update_data).eq("id", execution_id).execute()

        if result.data:
            return result.data[0]
        raise Exception(f"Failed to update agent execution {execution_id}")

    def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        supabase: Client = get_supabase()
        result = supabase.table("agent_executions").select("*").eq("id", execution_id).execute()

        if result.data:
            return result.data[0]
        return None

    def get_project_executions(self, project_id: str) -> List[Dict[str, Any]]:
        supabase: Client = get_supabase()
        result = supabase.table("agent_executions").select("*").eq("project_id", project_id).order("created_at", desc=True).execute()
        return result.data or []


agent_service = AgentService()
