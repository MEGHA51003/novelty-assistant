from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from supabase import Client
from app.database import get_supabase
from app.schemas.image import ImageGenerateRequest, ImageResponse, ImageAnalyzeRequest
from app.utils.helpers import get_current_user
from app.services.image_service import image_service
from app.services.gemini_service import gemini_service

router = APIRouter(prefix="/api", tags=["images"])


def verify_project_access(project_id: str, user_id: str, supabase: Client) -> bool:
    result = supabase.table("projects").select("id").eq("id", project_id).eq("user_id", user_id).execute()
    return len(result.data) > 0


@router.post("/projects/{project_id}/images/generate", response_model=ImageResponse)
async def generate_image(
    project_id: str,
    request: ImageGenerateRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    if not verify_project_access(project_id, current_user["id"], supabase):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    result = await image_service.generate_image(request.prompt)

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Image generation failed")
        )

    image_record = {
        "project_id": project_id,
        "conversation_id": request.conversation_id,
        "prompt": request.prompt,
        "image_url": result["image_url"],
        "storage_type": result.get("model", "unknown")
    }

    db_result = supabase.table("images").insert(image_record).execute()

    if not db_result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save image"
        )

    return db_result.data[0]


@router.get("/projects/{project_id}/images", response_model=List[ImageResponse])
async def list_project_images(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    if not verify_project_access(project_id, current_user["id"], supabase):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    result = supabase.table("images").select("*").eq("project_id", project_id).order("created_at", desc=True).execute()
    return result.data or []


@router.post("/images/{image_id}/analyze")
async def analyze_image(
    image_id: str,
    request: ImageAnalyzeRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    img_result = supabase.table("images").select("*, projects(user_id)").eq("id", image_id).execute()

    if not img_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    image = img_result.data[0]
    if image["projects"]["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    analysis = gemini_service.analyze_image_sync(
        image_url=image["image_url"],
        question=request.question
    )

    supabase.table("images").update({
        "analysis_result": analysis,
        "analyzed_at": "now"
    }).eq("id", image_id).execute()

    return {"analysis": analysis}


@router.delete("/images/{image_id}")
async def delete_image(
    image_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    img_result = supabase.table("images").select("*, projects(user_id)").eq("id", image_id).execute()

    if not img_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    image = img_result.data[0]
    if image["projects"]["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    supabase.table("images").delete().eq("id", image_id).execute()

    return {"message": "Image deleted successfully"}
