from typing import Literal

from pydantic import BaseModel, Field


class BuildMaterialOption(BaseModel):
    value: str
    label: str


class BuildGenerateRequest(BaseModel):
    template_id: str = Field(..., description="Identificador de la plantilla base")
    prompt: str = Field(default="", description="Indicaciones opcionales para modificar la plantilla")
    size: Literal["small", "medium", "large"] = Field(default="medium")
    main_material: str | None = Field(default=None, description="Material principal del cuerpo de la construccion")
    secondary_materials: list[str] = Field(default_factory=list, description="Materiales secundarios para vigas y detalles")
    extensions: list[str] = Field(default_factory=list, description="Extensiones opcionales para la construccion")


class BlockPlacement(BaseModel):
    x: int
    y: int
    z: int
    block: str
    state: dict[str, str | bool] = Field(default_factory=dict)


class BuildMetadata(BaseModel):
    template_id: str
    template_label: str
    category: str
    size: Literal["small", "medium", "large"]
    selected_main_material: str | None
    selected_secondary_materials: list[str]
    selected_extensions: list[str]
    prompt_used: str
    width: int
    depth: int
    height: int
    applied_features: list[str]
    materials: dict[str, str]
    block_count: int


class BuildGenerateResponse(BaseModel):
    metadata: BuildMetadata
    blocks: list[BlockPlacement]


class BuildTemplateSummary(BaseModel):
    id: str
    label: str
    category: str
    default_size: Literal["small", "medium", "large"]
    supported_sizes: list[Literal["small", "medium", "large"]]
    default_main_material: str | None
    max_secondary_materials: int
    default_secondary_materials: list[str]
    main_material_options: list[BuildMaterialOption]
    secondary_material_options: list[BuildMaterialOption]
    supported_extensions: list[str]
    default_prompt: str
    size_prompts: dict[str, str]
    supported_features: list[str]
