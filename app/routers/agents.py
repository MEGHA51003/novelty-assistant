from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from supabase import Client
from app.database import get_supabase
from app.schemas.agent import AgentExecutionCreate, AgentExecutionResponse
from app.utils.helpers import get_current_user
from app.agents.memory_agent import memory_agent

router = APIRouter(prefix="/api", tags=["agents"])


def verify_project_access(project_id: str, user_id: str, supabase: Client) -> bool:
    result = supabase.table("projects").select("id").eq("id", project_id).eq("user_id", user_id).execute()
    return len(result.data) > 0


@router.post("/projects/{project_id}/agents/organize", response_model=AgentExecutionResponse)
async def trigger_memory_organizer(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    if not verify_project_access(project_id, current_user["id"], supabase):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    execution = memory_agent.create_execution(project_id)

    memory_agent.run_async(execution["id"])

    return execution


@router.get("/agents/{execution_id}", response_model=AgentExecutionResponse)
async def get_agent_status(
    execution_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    result = supabase.table("agent_executions").select("*, projects(user_id)").eq("id", execution_id).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent execution not found"
        )

    execution = result.data[0]
    if execution["projects"]["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent execution not found"
        )

    return execution


@router.get("/projects/{project_id}/agents", response_model=List[AgentExecutionResponse])
async def list_project_agents(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    if not verify_project_access(project_id, current_user["id"], supabase):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    result = supabase.table("agent_executions").select("*").eq("project_id", project_id).order("created_at", desc=True).execute()
    return result.data or []
