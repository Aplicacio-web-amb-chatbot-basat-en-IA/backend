from fastapi import APIRouter, Depends, HTTPException

from app.api.auth import get_current_user
from app.schemas.build_schema import (
    BuildGenerateRequest,
    BuildGenerateResponse,
    BuildTemplateSummary,
)
from app.services.build_generation_service import generate_build, list_build_templates


router = APIRouter()


@router.get("/templates", response_model=list[BuildTemplateSummary])
def get_build_templates(user=Depends(get_current_user)):
    return list_build_templates()


@router.post("/generate", response_model=BuildGenerateResponse)
def generate_construction(
    request: BuildGenerateRequest,
    user=Depends(get_current_user),
):
    try:
        return generate_build(
            template_id=request.template_id,
            prompt=request.prompt,
            size=request.size,
            main_material=request.main_material,
            secondary_materials=request.secondary_materials,
            extensions=request.extensions,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
