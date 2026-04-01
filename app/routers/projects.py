from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from supabase import Client
from app.database import get_supabase
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectBriefResponse, BriefUpdate
from app.utils.helpers import get_current_user

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    result = supabase.table("projects").select("*").eq("user_id", current_user["id"]).order("created_at", desc=True).execute()
    return result.data or []


@router.post("", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    project = {
        "user_id": current_user["id"],
        "title": project_data.title,
        "description": project_data.description,
        "goals": project_data.goals,
        "reference_links": project_data.reference_links,
        "tags": project_data.tags
    }

    result = supabase.table("projects").insert(project).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project"
        )

    return result.data[0]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    result = supabase.table("projects").select("*").eq("id", project_id).eq("user_id", current_user["id"]).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return result.data[0]


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    existing = supabase.table("projects").select("*").eq("id", project_id).eq("user_id", current_user["id"]).execute()
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    update_data = {k: v for k, v in project_data.model_dump().items() if v is not None}

    if update_data:
        result = supabase.table("projects").update(update_data).eq("id", project_id).execute()
        return result.data[0]

    return existing.data[0]


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    result = supabase.table("projects").delete().eq("id", project_id).eq("user_id", current_user["id"]).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return {"message": "Project deleted successfully"}


@router.get("/{project_id}/brief", response_model=ProjectBriefResponse)
async def get_brief(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    result = supabase.table("projects").select("*").eq("id", project_id).eq("user_id", current_user["id"]).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    project = result.data[0]
    return {
        "id": project["id"],
        "title": project["title"],
        "description": project.get("description"),
        "goals": project.get("goals"),
        "reference_links": project.get("reference_links", []),
        "tags": project.get("tags", [])
    }


@router.put("/{project_id}/brief", response_model=ProjectBriefResponse)
async def update_brief(
    project_id: str,
    brief_data: BriefUpdate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    existing = supabase.table("projects").select("*").eq("id", project_id).eq("user_id", current_user["id"]).execute()
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    update_data = {}
    if brief_data.title is not None:
        update_data["title"] = brief_data.title
    if brief_data.brief_description is not None:
        update_data["description"] = brief_data.brief_description
    if brief_data.brief_goals is not None:
        update_data["goals"] = brief_data.brief_goals
    if brief_data.brief_reference_links is not None:
        update_data["reference_links"] = brief_data.brief_reference_links
    if brief_data.brief_tags is not None:
        update_data["tags"] = brief_data.brief_tags

    if update_data:
        result = supabase.table("projects").update(update_data).eq("id", project_id).execute()
        project = result.data[0]
    else:
        project = existing.data[0]

    return {
        "id": project["id"],
        "title": project["title"],
        "description": project.get("description"),
        "goals": project.get("goals"),
        "reference_links": project.get("reference_links", []),
        "tags": project.get("tags", [])
    }
