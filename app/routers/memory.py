from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from supabase import Client
from app.database import get_supabase
from app.schemas.memory import MemoryCreate, MemoryUpdate, MemoryResponse
from app.utils.helpers import get_current_user

router = APIRouter(prefix="/api", tags=["memory"])


def verify_project_access(project_id: str, user_id: str, supabase: Client) -> bool:
    result = supabase.table("projects").select("id").eq("id", project_id).eq("user_id", user_id).execute()
    return len(result.data) > 0


@router.get("/projects/{project_id}/memory", response_model=List[MemoryResponse])
async def list_project_memory(
    project_id: str,
    memory_type: str = None,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    if not verify_project_access(project_id, current_user["id"], supabase):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    query = supabase.table("project_memory").select("*").eq("project_id", project_id)

    if memory_type:
        query = query.eq("memory_type", memory_type)

    result = query.order("created_at", desc=True).execute()
    return result.data or []


@router.post("/projects/{project_id}/memory", response_model=MemoryResponse)
async def create_memory(
    project_id: str,
    memory_data: MemoryCreate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    if not verify_project_access(project_id, current_user["id"], supabase):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    memory = {
        "project_id": project_id,
        "memory_type": memory_data.memory_type,
        "title": memory_data.title,
        "content": memory_data.content
    }

    result = supabase.table("project_memory").insert(memory).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create memory"
        )

    return result.data[0]


@router.put("/memory/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: str,
    memory_data: MemoryUpdate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    mem_result = supabase.table("project_memory").select("project_id").eq("id", memory_id).execute()
    if not mem_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found"
        )

    if not verify_project_access(mem_result.data[0]["project_id"], current_user["id"], supabase):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found"
        )

    update_data = {k: v for k, v in memory_data.model_dump().items() if v is not None}

    if update_data:
        result = supabase.table("project_memory").update(update_data).eq("id", memory_id).execute()
        return result.data[0]

    return mem_result.data[0]


@router.delete("/memory/{memory_id}")
async def delete_memory(
    memory_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    mem_result = supabase.table("project_memory").select("project_id").eq("id", memory_id).execute()
    if not mem_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found"
        )

    if not verify_project_access(mem_result.data[0]["project_id"], current_user["id"], supabase):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found"
        )

    supabase.table("project_memory").delete().eq("id", memory_id).execute()

    return {"message": "Memory deleted successfully"}
