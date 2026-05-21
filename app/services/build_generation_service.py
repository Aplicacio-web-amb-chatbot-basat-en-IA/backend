import json
from pathlib import Path

from app.schemas.build_schema import (
    BuildMaterialOption,
    BlockPlacement,
    BuildGenerateResponse,
    BuildMetadata,
    BuildTemplateSummary,
)
from app.services.retrieval_service import normalize_text


TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "build_templates"
Position = tuple[int, int, int]
SUPPORTED_SIZES = ("small", "medium", "large")

HORIZONTAL_DIRECTIONS = {
    "north": (0, 0, -1),
    "east": (1, 0, 0),
    "south": (0, 0, 1),
    "west": (-1, 0, 0),
}

NON_SOLID_BLOCKS = {
    "campfire",
    "cornflower",
    "dandelion",
    "glass_pane",
    "lantern",
    "lilac",
    "poppy",
    "vine",
}

FEATURE_PATTERNS = {
    "grande": ("grande", "amplia", "grandeza"),
    "de_piedra": ("casa de piedra", "hecha de piedra", "toda de piedra", "paredes de piedra"),
    "con_jardin": ("con jardin", "jardin", "huerto"),
    "dos_pisos": ("dos pisos", "2 pisos", "dos plantas", "2 plantas"),
    "decorada": ("decorada", "detallada", "bonita", "adornada"),
}

WOOD_FAMILY_BY_MATERIAL = {
    "dark_oak_log": "dark_oak",
    "dark_oak_planks": "dark_oak",
    "spruce_log": "spruce",
    "spruce_planks": "spruce",
    "oak_log": "oak",
    "oak_planks": "oak",
}

WOOD_FAMILY_BLOCKS = {
    "dark_oak": {
        "frame": "dark_oak_log",
        "frame_secondary": "stripped_dark_oak_log",
        "porch_wood": "dark_oak_log",
        "porch_beam": "dark_oak_log",
        "porch_planks": "dark_oak_planks",
        "porch_roof": "dark_oak_slab",
        "door": "dark_oak_door",
        "shutter": "dark_oak_trapdoor",
        "fence": "dark_oak_fence",
        "railing": "dark_oak_fence",
        "corbel": "dark_oak_stairs",
        "roof": "dark_oak_stairs",
        "roof_secondary": "dark_oak_slab",
        "roof_block": "dark_oak_planks",
        "roof_trim": "dark_oak_slab",
        "roof_edge": "dark_oak_stairs",
    },
    "spruce": {
        "frame": "spruce_log",
        "frame_secondary": "stripped_spruce_log",
        "porch_wood": "spruce_log",
        "porch_beam": "spruce_log",
        "porch_planks": "spruce_planks",
        "porch_roof": "spruce_slab",
        "door": "spruce_door",
        "shutter": "spruce_trapdoor",
        "fence": "spruce_fence",
        "railing": "spruce_fence",
        "corbel": "spruce_stairs",
        "roof": "spruce_stairs",
        "roof_secondary": "spruce_slab",
        "roof_block": "spruce_planks",
        "roof_trim": "spruce_slab",
        "roof_edge": "spruce_stairs",
    },
    "oak": {
        "frame": "oak_log",
        "frame_secondary": "stripped_oak_log",
        "porch_wood": "oak_log",
        "porch_beam": "oak_log",
        "porch_planks": "oak_planks",
        "porch_roof": "oak_slab",
        "door": "oak_door",
        "shutter": "oak_trapdoor",
        "fence": "oak_fence",
        "railing": "oak_fence",
        "corbel": "oak_stairs",
        "roof": "oak_stairs",
        "roof_secondary": "oak_slab",
        "roof_block": "oak_planks",
        "roof_trim": "oak_slab",
        "roof_edge": "oak_stairs",
    },
}

STONE_SECONDARY_BLOCKS = {
    "polished_andesite": {
        "foundation_mix": "polished_andesite",
        "foundation_accent": "polished_andesite_stairs",
        "roof": "polished_andesite_stairs",
        "roof_secondary": "polished_andesite_slab",
        "roof_block": "polished_andesite",
        "roof_trim": "polished_andesite_slab",
        "roof_edge": "polished_andesite_stairs",
        "porch_roof": "polished_andesite_slab",
        "path_secondary": "polished_andesite",
        "garden_post": "polished_andesite",
    },
    "cobblestone": {
        "foundation_mix": "cobblestone",
        "foundation_accent": "cobblestone_stairs",
        "roof": "cobblestone_stairs",
        "roof_secondary": "cobblestone_slab",
        "roof_block": "cobblestone",
        "roof_trim": "cobblestone_slab",
        "roof_edge": "cobblestone_stairs",
        "porch_roof": "cobblestone_slab",
        "path_secondary": "cobblestone",
        "chimney": "cobblestone_wall",
        "garden_post": "cobblestone",
    },
    "mossy_cobblestone": {
        "foundation_mix": "mossy_cobblestone",
        "foundation_accent": "mossy_cobblestone_stairs",
        "roof": "mossy_cobblestone_stairs",
        "roof_secondary": "mossy_cobblestone_slab",
        "roof_block": "mossy_cobblestone",
        "roof_trim": "mossy_cobblestone_slab",
        "roof_edge": "mossy_cobblestone_stairs",
        "porch_roof": "mossy_cobblestone_slab",
        "path_secondary": "mossy_cobblestone",
        "chimney": "cobblestone_wall",
        "garden_post": "mossy_cobblestone",
    },
}

MODERN_MAIN_MATERIAL_PRESETS = {
    "white_concrete": {
        "foundation": "stone_bricks",
        "walls": "white_concrete",
        "roof": "smooth_stone",
        "roof_slab": "smooth_stone_slab",
        "stairs": "stone_stairs",
        "pool_border": "smooth_stone",
        "terrace": "smooth_stone",
    },
    "quartz_block": {
        "foundation": "smooth_stone",
        "walls": "quartz_block",
        "roof": "smooth_quartz",
        "roof_slab": "quartz_slab",
        "stairs": "quartz_stairs",
        "pool_border": "smooth_stone",
        "terrace": "smooth_quartz",
    },
    "smooth_stone": {
        "foundation": "stone_bricks",
        "walls": "smooth_stone",
        "roof": "smooth_stone",
        "roof_slab": "smooth_stone_slab",
        "stairs": "stone_stairs",
        "pool_border": "smooth_stone",
        "terrace": "smooth_stone",
    },
    "light_gray_concrete": {
        "foundation": "stone_bricks",
        "walls": "light_gray_concrete",
        "roof": "smooth_stone",
        "roof_slab": "smooth_stone_slab",
        "stairs": "stone_stairs",
        "pool_border": "smooth_stone",
        "terrace": "smooth_stone",
    },
    "sandstone": {
        "foundation": "smooth_sandstone",
        "walls": "sandstone",
        "roof": "smooth_sandstone",
        "roof_slab": "sandstone_slab",
        "stairs": "sandstone_stairs",
        "pool_border": "smooth_sandstone",
        "terrace": "smooth_sandstone",
    },
}

MODERN_FRAME_SECONDARY_MATERIALS = {
    "black_concrete": {
        "frame": "black_concrete",
        "trim": "black_concrete",
    },
    "gray_concrete": {
        "frame": "gray_concrete",
        "trim": "gray_concrete",
    },
    "stone_bricks": {
        "frame": "stone_bricks",
        "trim": "stone_bricks",
    },
}

MODERN_WOOD_SECONDARY_MATERIALS = {
    "oak_planks": {
        "accent_wood": "oak_planks",
        "accent_log": "oak_log",
        "accent_slab": "oak_slab",
        "door": "oak_door",
    },
    "spruce_planks": {
        "accent_wood": "spruce_planks",
        "accent_log": "spruce_log",
        "accent_slab": "spruce_slab",
        "door": "spruce_door",
    },
    "dark_oak_planks": {
        "accent_wood": "dark_oak_planks",
        "accent_log": "dark_oak_log",
        "accent_slab": "dark_oak_slab",
        "door": "dark_oak_door",
    },
}

CASTLE_MAIN_MATERIAL_PRESETS = {
    "stone_bricks": {
        "foundation": "stone_bricks",
        "walls": "stone_bricks",
        "battlement": "stone_bricks",
        "slab": "stone_brick_slab",
        "stairs": "stone_brick_stairs",
        "trim": "polished_andesite",
        "courtyard_path": "cobblestone",
    },
    "deepslate_bricks": {
        "foundation": "deepslate_bricks",
        "walls": "deepslate_bricks",
        "battlement": "deepslate_bricks",
        "slab": "deepslate_brick_slab",
        "stairs": "deepslate_brick_stairs",
        "trim": "polished_andesite",
        "courtyard_path": "deepslate_bricks",
    },
    "polished_andesite": {
        "foundation": "polished_andesite",
        "walls": "polished_andesite",
        "battlement": "polished_andesite",
        "slab": "polished_andesite_slab",
        "stairs": "polished_andesite_stairs",
        "trim": "stone_bricks",
        "courtyard_path": "stone_bricks",
    },
    "cobblestone": {
        "foundation": "cobblestone",
        "walls": "cobblestone",
        "battlement": "cobblestone",
        "slab": "cobblestone_slab",
        "stairs": "cobblestone_stairs",
        "trim": "stone_bricks",
        "courtyard_path": "cobblestone",
    },
    "sandstone": {
        "foundation": "sandstone",
        "walls": "sandstone",
        "battlement": "sandstone",
        "slab": "sandstone_slab",
        "stairs": "sandstone_stairs",
        "trim": "smooth_sandstone",
        "courtyard_path": "smooth_sandstone",
    },
}

CASTLE_STONE_SECONDARY_MATERIALS = {
    "polished_andesite": {
        "trim": "polished_andesite",
        "courtyard_path": "polished_andesite",
    },
    "cobblestone": {
        "trim": "cobblestone",
        "courtyard_path": "cobblestone",
    },
    "mossy_cobblestone": {
        "trim": "mossy_cobblestone",
        "courtyard_path": "mossy_cobblestone",
    },
    "deepslate_bricks": {
        "trim": "deepslate_bricks",
        "courtyard_path": "deepslate_bricks",
    },
}

CASTLE_WOOD_SECONDARY_MATERIALS = {
    "dark_oak_planks": {
        "bridge": "dark_oak_planks",
        "bridge_slab": "dark_oak_slab",
        "door": "dark_oak_door",
    },
    "spruce_planks": {
        "bridge": "spruce_planks",
        "bridge_slab": "spruce_slab",
        "door": "spruce_door",
    },
    "oak_planks": {
        "bridge": "oak_planks",
        "bridge_slab": "oak_slab",
        "door": "oak_door",
    },
}

FARM_MAIN_MATERIAL_PRESETS = {
    "red_concrete": {
        "walls": "red_concrete",
        "gable": "red_concrete",
        "annex_walls": "red_concrete",
    },
    "bricks": {
        "walls": "bricks",
        "gable": "bricks",
        "annex_walls": "bricks",
    },
    "terracotta": {
        "walls": "terracotta",
        "gable": "terracotta",
        "annex_walls": "terracotta",
    },
    "spruce_planks": {
        "walls": "spruce_planks",
        "gable": "spruce_planks",
        "annex_walls": "spruce_planks",
    },
    "oak_planks": {
        "walls": "oak_planks",
        "gable": "oak_planks",
        "annex_walls": "oak_planks",
    },
}

FARM_STONE_SECONDARY_MATERIALS = {
    "stone_bricks": {
        "foundation": "stone_bricks",
        "trim": "stone_bricks",
        "path": "stone_bricks",
    },
    "cobblestone": {
        "foundation": "cobblestone",
        "trim": "cobblestone",
        "path": "cobblestone",
    },
    "polished_andesite": {
        "foundation": "polished_andesite",
        "trim": "polished_andesite",
        "path": "polished_andesite",
    },
}

FARM_WOOD_SECONDARY_MATERIALS = {
    "dark_oak_planks": {
        "roof": "dark_oak_stairs",
        "roof_slab": "dark_oak_slab",
        "wood": "dark_oak_planks",
        "log": "dark_oak_log",
        "fence": "dark_oak_fence",
        "gate": "dark_oak_fence_gate",
        "door": "dark_oak_door",
        "field_border": "dark_oak_planks",
    },
    "spruce_planks": {
        "roof": "spruce_stairs",
        "roof_slab": "spruce_slab",
        "wood": "spruce_planks",
        "log": "spruce_log",
        "fence": "spruce_fence",
        "gate": "spruce_fence_gate",
        "door": "spruce_door",
        "field_border": "spruce_planks",
    },
    "oak_planks": {
        "roof": "oak_stairs",
        "roof_slab": "oak_slab",
        "wood": "oak_planks",
        "log": "oak_log",
        "fence": "oak_fence",
        "gate": "oak_fence_gate",
        "door": "oak_door",
        "field_border": "oak_planks",
    },
}

MINE_MAIN_MATERIAL_PRESETS = {
    "stone": {
        "rock": "stone",
        "trim": "stone_bricks",
        "slab": "stone_slab",
        "stairs": "stone_stairs",
        "tunnel_floor": "stone",
    },
    "stone_bricks": {
        "rock": "stone_bricks",
        "trim": "polished_andesite",
        "slab": "stone_brick_slab",
        "stairs": "stone_brick_stairs",
        "tunnel_floor": "stone_bricks",
    },
    "cobblestone": {
        "rock": "cobblestone",
        "trim": "stone_bricks",
        "slab": "cobblestone_slab",
        "stairs": "cobblestone_stairs",
        "tunnel_floor": "cobblestone",
    },
    "andesite": {
        "rock": "andesite",
        "trim": "polished_andesite",
        "slab": "polished_andesite_slab",
        "stairs": "polished_andesite_stairs",
        "tunnel_floor": "andesite",
    },
    "deepslate_bricks": {
        "rock": "deepslate_bricks",
        "trim": "stone_bricks",
        "slab": "deepslate_brick_slab",
        "stairs": "deepslate_brick_stairs",
        "tunnel_floor": "deepslate_bricks",
    },
}

MINE_STONE_SECONDARY_MATERIALS = {
    "stone_bricks": {
        "trim": "stone_bricks",
        "tunnel_floor": "stone_bricks",
    },
    "polished_andesite": {
        "trim": "polished_andesite",
        "tunnel_floor": "polished_andesite",
    },
    "cobblestone": {
        "trim": "cobblestone",
        "tunnel_floor": "cobblestone",
    },
}

MINE_WOOD_SECONDARY_MATERIALS = {
    "oak_planks": {
        "wood": "oak_planks",
        "log": "oak_log",
        "wood_slab": "oak_slab",
        "wood_stairs": "oak_stairs",
        "fence": "oak_fence",
    },
    "spruce_planks": {
        "wood": "spruce_planks",
        "log": "spruce_log",
        "wood_slab": "spruce_slab",
        "wood_stairs": "spruce_stairs",
        "fence": "spruce_fence",
    },
    "dark_oak_planks": {
        "wood": "dark_oak_planks",
        "log": "dark_oak_log",
        "wood_slab": "dark_oak_slab",
        "wood_stairs": "dark_oak_stairs",
        "fence": "dark_oak_fence",
    },
}


def _load_templates() -> list[dict]:
    templates: list[dict] = []
    for file_path in sorted(TEMPLATES_DIR.glob("*.json")):
        templates.append(json.loads(file_path.read_text(encoding="utf-8")))
    return templates


def _material_options_from_template(template: dict, key: str) -> list[BuildMaterialOption]:
    return [BuildMaterialOption(**option) for option in template.get(key, [])]


def list_build_templates() -> list[BuildTemplateSummary]:
    return [
        BuildTemplateSummary(
            id=template["id"],
            label=template["label"],
            category=template["category"],
            default_size=template.get("default_size", "medium"),
            supported_sizes=template.get("supported_sizes", list(SUPPORTED_SIZES)),
            default_main_material=template.get("default_main_material"),
            max_secondary_materials=template.get("max_secondary_materials", 2),
            default_secondary_materials=template.get("default_secondary_materials", []),
            main_material_options=_material_options_from_template(template, "main_material_options"),
            secondary_material_options=_material_options_from_template(template, "secondary_material_options"),
            supported_extensions=template.get("supported_extensions", []),
            default_prompt=template.get("default_prompt", ""),
            size_prompts=template.get("size_prompts", {}),
            supported_features=template["supported_features"],
        )
        for template in _load_templates()
    ]


def _find_template(template_id: str) -> dict:
    for template in _load_templates():
        if template["id"] == template_id:
            return template
    raise LookupError(f"No existe la plantilla '{template_id}'")


def _parse_features(prompt: str) -> list[str]:
    normalized_prompt = normalize_text(prompt)
    applied: list[str] = []
    for feature, patterns in FEATURE_PATTERNS.items():
        if any(pattern in normalized_prompt for pattern in patterns):
            applied.append(feature)

    wood_house_phrases = (
        "casa de madera",
        "hecha de madera",
        "completamente de madera",
        "paredes de madera",
        "estructura de madera",
    )
    if any(phrase in normalized_prompt for phrase in wood_house_phrases):
        applied.append("de_madera")
    return applied


def _size_multiplier(size: str) -> int:
    if size == "small":
        return 0
    if size == "large":
        return 3
    return 1


def _resolve_dimensions(template: dict, size: str, features: list[str]) -> tuple[int, int, int]:
    multiplier = _size_multiplier(size)
    width = template["default_width"] + multiplier * 2
    depth = template["default_depth"] + multiplier * 2
    height = template["default_height"] + multiplier * 2

    if "grande" in features:
        width += 2
        depth += 2
        height += 1
    if "dos_pisos" in features:
        height += 4

    width = max(width, 7)
    depth = max(depth, 7)
    height = max(height, 5)
    return width, depth, height


def _build_size_profile(size: str, features: list[str]) -> dict[str, int | str]:
    if size == "small":
        wall_height = 4
        annex_height = 4
        porch_half_span = 3
        porch_post_inset = 1
        clear_entry_half_span = 1
        annex_width_extension = 3
        annex_start_offset = 6
        annex_roof_layers = 3
        chimney_height = 3
        dormer_style = "small"
    elif size == "large":
        wall_height = 6
        annex_height = 5
        porch_half_span = 5
        porch_post_inset = 2
        clear_entry_half_span = 2
        annex_width_extension = 5
        annex_start_offset = 3
        annex_roof_layers = 5
        chimney_height = 5
        dormer_style = "large"
    else:
        wall_height = 5
        annex_height = 4
        porch_half_span = 4
        porch_post_inset = 1
        clear_entry_half_span = 1
        annex_width_extension = 4
        annex_start_offset = 4
        annex_roof_layers = 4
        chimney_height = 4
        dormer_style = "medium"

    if "dos_pisos" in features:
        wall_height += 3
        annex_height += 1

    return {
        "wall_height": wall_height,
        "annex_height": annex_height,
        "porch_half_span": porch_half_span,
        "porch_post_inset": porch_post_inset,
        "clear_entry_half_span": clear_entry_half_span,
        "annex_width_extension": annex_width_extension,
        "annex_start_offset": annex_start_offset,
        "annex_roof_layers": annex_roof_layers,
        "chimney_height": chimney_height,
        "dormer_style": dormer_style,
    }


def _resolve_prompt_for_size(template: dict, size: str, prompt: str) -> str:
    prompt_text = prompt.strip()
    if prompt_text:
        return prompt_text

    size_prompts = template.get("size_prompts", {})
    if size in size_prompts:
        return size_prompts[size]

    return template.get("default_prompt", "")


def _allowed_material_values(template: dict, key: str) -> set[str]:
    return {option["value"] for option in template.get(key, [])}


def _normalize_material_selection(
    template: dict,
    main_material: str | None,
    secondary_materials: list[str] | None,
) -> tuple[str | None, list[str]]:
    allowed_main = _allowed_material_values(template, "main_material_options")
    allowed_secondary = _allowed_material_values(template, "secondary_material_options")
    max_secondary_materials = int(template.get("max_secondary_materials", 2))

    normalized_main = main_material or template.get("default_main_material")
    if normalized_main and normalized_main not in allowed_main:
        raise ValueError(f"Material principal no soportado: {normalized_main}")

    normalized_secondary: list[str] = []
    seen: set[str] = set()
    for material in (secondary_materials or template.get("default_secondary_materials", [])):
        if material not in allowed_secondary:
            raise ValueError(f"Material secundario no soportado: {material}")
        if material in seen:
            continue
        seen.add(material)
        normalized_secondary.append(material)

    if len(normalized_secondary) > max_secondary_materials:
        raise ValueError(f"Solo se permiten {max_secondary_materials} materiales secundarios como maximo")

    return normalized_main, normalized_secondary


def _normalize_extension_selection(template: dict, extensions: list[str] | None) -> list[str]:
    allowed_extensions = set(template.get("supported_extensions", []))
    normalized_extensions: list[str] = []
    seen: set[str] = set()
    for extension in extensions or []:
        if extension not in allowed_extensions:
            raise ValueError(f"Extension no soportada: {extension}")
        if extension in seen:
            continue
        seen.add(extension)
        normalized_extensions.append(extension)
    return normalized_extensions


def _apply_main_material(materials: dict[str, str], main_material: str | None) -> None:
    if not main_material:
        return

    if main_material == "calcite":
        materials["walls"] = "calcite"
        materials["wall_secondary"] = "calcite"
        materials["porch_planks"] = "calcite"
        materials["porch_roof"] = "oxidized_cut_copper_slab"
        return
    if main_material == "stone_bricks":
        materials["foundation"] = "stone_bricks"
        materials["foundation_mix"] = "stone_bricks"
        materials["walls"] = "stone_bricks"
        materials["wall_secondary"] = "stone_bricks"
        materials["roof"] = "stone_brick_stairs"
        materials["roof_secondary"] = "stone_brick_slab"
        materials["roof_block"] = "stone_bricks"
        materials["roof_trim"] = "stone_brick_slab"
        materials["roof_edge"] = "stone_brick_stairs"
        materials["porch_planks"] = "stone_bricks"
        materials["porch_roof"] = "stone_brick_slab"
        return
    if main_material == "bricks":
        materials["walls"] = "bricks"
        materials["wall_secondary"] = "bricks"
        materials["foundation_mix"] = "bricks"
        materials["roof"] = "brick_stairs"
        materials["roof_secondary"] = "brick_slab"
        materials["roof_block"] = "bricks"
        materials["roof_trim"] = "brick_slab"
        materials["roof_edge"] = "brick_stairs"
        materials["porch_planks"] = "bricks"
        materials["porch_roof"] = "brick_slab"
        return
    if main_material == "sandstone":
        materials["walls"] = "sandstone"
        materials["wall_secondary"] = "smooth_sandstone"
        materials["foundation_mix"] = "sandstone"
        materials["roof"] = "sandstone_stairs"
        materials["roof_secondary"] = "sandstone_slab"
        materials["roof_block"] = "sandstone"
        materials["roof_trim"] = "sandstone_slab"
        materials["roof_edge"] = "sandstone_stairs"
        materials["porch_planks"] = "sandstone"
        materials["porch_roof"] = "sandstone_slab"
        return

    family = WOOD_FAMILY_BY_MATERIAL.get(main_material)
    if not family:
        return

    materials["walls"] = main_material
    if family == "dark_oak":
        materials["wall_secondary"] = "stripped_dark_oak_wood"
    elif family == "spruce":
        materials["wall_secondary"] = "stripped_spruce_wood"
    else:
        materials["wall_secondary"] = "stripped_oak_wood"
    wood_mapping = WOOD_FAMILY_BLOCKS[family]
    for key in (
        "roof",
        "roof_secondary",
        "roof_block",
        "roof_trim",
        "roof_edge",
        "porch_planks",
        "porch_roof",
        "door",
        "shutter",
    ):
        materials[key] = wood_mapping[key]


def _apply_secondary_materials(materials: dict[str, str], secondary_materials: list[str]) -> None:
    if not secondary_materials:
        return

    primary_secondary = secondary_materials[0]
    secondary_accent = secondary_materials[1] if len(secondary_materials) > 1 else None

    if primary_secondary in WOOD_FAMILY_BY_MATERIAL:
        family = WOOD_FAMILY_BY_MATERIAL[primary_secondary]
        wood_mapping = WOOD_FAMILY_BLOCKS[family]
        for key in (
            "frame",
            "frame_secondary",
            "porch_wood",
            "porch_beam",
            "door",
            "shutter",
            "fence",
            "railing",
            "corbel",
            "roof_trim",
            "roof_edge",
        ):
            materials[key] = wood_mapping[key]
    elif primary_secondary in STONE_SECONDARY_BLOCKS:
        stone_mapping = STONE_SECONDARY_BLOCKS[primary_secondary]
        for key in ("foundation_mix", "foundation_accent", "path_secondary", "chimney", "garden_post"):
            if key in stone_mapping:
                materials[key] = stone_mapping[key]
        for key in ("roof_trim", "roof_edge"):
            if key in stone_mapping:
                materials[key] = stone_mapping[key]

    if secondary_accent and secondary_accent in STONE_SECONDARY_BLOCKS:
        accent_mapping = STONE_SECONDARY_BLOCKS[secondary_accent]
        for key in ("foundation_mix", "foundation_accent", "path_secondary", "chimney", "garden_post"):
            if key in accent_mapping:
                materials[key] = accent_mapping[key]


def _resolve_materials(
    template: dict,
    features: list[str],
    main_material: str | None,
    secondary_materials: list[str],
) -> dict[str, str]:
    base = dict(template["materials"])
    materials = {
        "foundation": "stone_bricks",
        "foundation_mix": "stone_bricks",
        "foundation_accent": "stone_brick_stairs",
        "frame": "dark_oak_log",
        "frame_secondary": "stripped_oak_log",
        "walls": "calcite",
        "wall_secondary": "calcite",
        "roof": "oxidized_cut_copper_stairs",
        "roof_secondary": "oxidized_cut_copper_slab",
        "roof_trim": "dark_oak_slab",
        "roof_block": "oxidized_cut_copper",
        "roof_edge": "dark_oak_stairs",
        "window_block": "glass",
        "windows": "glass_pane",
        "door": "spruce_door",
        "accent": "lantern",
        "shutter": "spruce_trapdoor",
        "path": "cobblestone",
        "path_secondary": "stone_bricks",
        "path_tertiary": "dirt_path",
        "chimney": "stone_brick_wall",
        "chimney_cap": "stone_brick_slab",
        "fence": "spruce_fence",
        "garden_wall": "stone_brick_wall",
        "garden_post": "stone_bricks",
        "leaves": "azalea_leaves",
        "vine": "vine",
        "flower_red": "poppy",
        "flower_blue": "cornflower",
        "flower_purple": "lilac",
        "flower_yellow": "dandelion",
        "porch_wood": "stripped_oak_log",
        "porch_beam": "dark_oak_log",
        "porch_planks": "spruce_planks",
        "porch_roof": "dark_oak_slab",
        "railing": "spruce_fence",
        "corbel": "dark_oak_stairs",
        "barrel": "barrel",
    }

    materials.update(base)

    if "de_piedra" in features:
        materials["walls"] = "stone_bricks"
        materials["wall_secondary"] = "stone_bricks"
        materials["frame"] = "stone_bricks"
        materials["frame_secondary"] = "stone_bricks"
        materials["roof"] = "deepslate_tile_stairs"
        materials["roof_secondary"] = "deepslate_tile_slab"
        materials["roof_trim"] = "stone_brick_slab"
        materials["roof_block"] = "deepslate_tiles"
        materials["roof_edge"] = "deepslate_tile_stairs"
        materials["foundation_accent"] = "stone_brick_stairs"
        materials["chimney"] = "stone_brick_wall"
        materials["chimney_cap"] = "brick_block"
        materials["porch_roof"] = "deepslate_tile_slab"
        materials["porch_wood"] = "spruce_log"
        materials["porch_beam"] = "spruce_log"
        materials["shutter"] = "spruce_trapdoor"
    if "de_madera" in features:
        materials["foundation"] = "stone_bricks"
        materials["foundation_mix"] = "cobblestone"
        materials["foundation_accent"] = "stone_brick_stairs"
        materials["walls"] = "spruce_planks"
        materials["wall_secondary"] = "stripped_oak_wood"
        materials["frame"] = "dark_oak_log"
        materials["frame_secondary"] = "stripped_dark_oak_log"
        materials["roof"] = "dark_oak_stairs"
        materials["roof_secondary"] = "dark_oak_slab"
        materials["roof_trim"] = "dark_oak_slab"
        materials["roof_block"] = "dark_oak_planks"
        materials["roof_edge"] = "dark_oak_stairs"
        materials["door"] = "dark_oak_door"
        materials["shutter"] = "dark_oak_trapdoor"
        materials["porch_wood"] = "dark_oak_log"
        materials["porch_beam"] = "dark_oak_log"
        materials["porch_planks"] = "spruce_planks"
        materials["porch_roof"] = "dark_oak_slab"
        materials["fence"] = "dark_oak_fence"
        materials["railing"] = "dark_oak_fence"
        materials["corbel"] = "dark_oak_stairs"
    if "decorada" in features:
        materials["accent"] = "lantern"

    _apply_main_material(materials, main_material)
    _apply_secondary_materials(materials, secondary_materials)
    return materials


def _resolve_modern_materials(
    template: dict,
    main_material: str | None,
    secondary_materials: list[str],
) -> dict[str, str]:
    materials = {
        "foundation": template["materials"].get("foundation", "stone_bricks"),
        "walls": template["materials"].get("walls", "white_concrete"),
        "frame": template["materials"].get("frame", "black_concrete"),
        "glass": template["materials"].get("glass", "glass"),
        "glass_pane": template["materials"].get("glass_pane", "glass_pane"),
        "accent_wood": template["materials"].get("accent_wood", "oak_planks"),
        "accent_log": template["materials"].get("accent_log", "oak_log"),
        "accent_slab": template["materials"].get("accent_slab", "oak_slab"),
        "roof": template["materials"].get("roof", "smooth_stone"),
        "roof_slab": template["materials"].get("roof_slab", "smooth_stone_slab"),
        "stairs": template["materials"].get("stairs", "stone_stairs"),
        "light": template["materials"].get("light", "lantern"),
        "leaf": template["materials"].get("leaf", "azalea_leaves"),
        "grass": template["materials"].get("grass", "grass_block"),
        "flower_red": template["materials"].get("flower_red", "poppy"),
        "flower_yellow": template["materials"].get("flower_yellow", "dandelion"),
        "pool_border": template["materials"].get("pool_border", "smooth_stone"),
        "pool_water": template["materials"].get("pool_water", "water"),
        "door": template["materials"].get("door", "dark_oak_door"),
        "trim": template["materials"].get("trim", "black_concrete"),
        "terrace": template["materials"].get("terrace", "smooth_stone"),
    }

    if main_material in MODERN_MAIN_MATERIAL_PRESETS:
        materials.update(MODERN_MAIN_MATERIAL_PRESETS[main_material])

    applied_frame = False
    applied_wood = False
    for material in secondary_materials:
        if not applied_frame and material in MODERN_FRAME_SECONDARY_MATERIALS:
            materials.update(MODERN_FRAME_SECONDARY_MATERIALS[material])
            applied_frame = True
            continue
        if not applied_wood and material in MODERN_WOOD_SECONDARY_MATERIALS:
            materials.update(MODERN_WOOD_SECONDARY_MATERIALS[material])
            applied_wood = True

    return materials


def _resolve_castle_materials(
    template: dict,
    main_material: str | None,
    secondary_materials: list[str],
) -> dict[str, str]:
    materials = {
        "foundation": template["materials"].get("foundation", "stone_bricks"),
        "walls": template["materials"].get("walls", "stone_bricks"),
        "battlement": template["materials"].get("battlement", "stone_bricks"),
        "slab": template["materials"].get("slab", "stone_brick_slab"),
        "stairs": template["materials"].get("stairs", "stone_brick_stairs"),
        "trim": template["materials"].get("trim", "polished_andesite"),
        "bridge": template["materials"].get("bridge", "dark_oak_planks"),
        "bridge_slab": template["materials"].get("bridge_slab", "dark_oak_slab"),
        "door": template["materials"].get("door", "dark_oak_door"),
        "bars": template["materials"].get("bars", "iron_bars"),
        "light": template["materials"].get("light", "lantern"),
        "ground": template["materials"].get("ground", "grass_block"),
        "courtyard_path": template["materials"].get("courtyard_path", "cobblestone"),
        "water": template["materials"].get("water", "water"),
        "leaf": template["materials"].get("leaf", "azalea_leaves"),
    }

    if main_material in CASTLE_MAIN_MATERIAL_PRESETS:
        materials.update(CASTLE_MAIN_MATERIAL_PRESETS[main_material])

    applied_stone = False
    applied_wood = False
    for material in secondary_materials:
        if not applied_stone and material in CASTLE_STONE_SECONDARY_MATERIALS:
            materials.update(CASTLE_STONE_SECONDARY_MATERIALS[material])
            applied_stone = True
            continue
        if not applied_wood and material in CASTLE_WOOD_SECONDARY_MATERIALS:
            materials.update(CASTLE_WOOD_SECONDARY_MATERIALS[material])
            applied_wood = True

    return materials


def _resolve_farm_materials(
    template: dict,
    main_material: str | None,
    secondary_materials: list[str],
) -> dict[str, str]:
    materials = {
        "foundation": template["materials"].get("foundation", "stone_bricks"),
        "walls": template["materials"].get("walls", "red_concrete"),
        "gable": template["materials"].get("gable", "red_concrete"),
        "annex_walls": template["materials"].get("annex_walls", "oak_planks"),
        "roof": template["materials"].get("roof", "dark_oak_stairs"),
        "roof_slab": template["materials"].get("roof_slab", "dark_oak_slab"),
        "trim": template["materials"].get("trim", "stone_bricks"),
        "wood": template["materials"].get("wood", "dark_oak_planks"),
        "log": template["materials"].get("log", "dark_oak_log"),
        "fence": template["materials"].get("fence", "dark_oak_fence"),
        "gate": template["materials"].get("gate", "dark_oak_fence_gate"),
        "door": template["materials"].get("door", "dark_oak_door"),
        "glass": template["materials"].get("glass", "glass"),
        "path": template["materials"].get("path", "cobblestone"),
        "field_border": template["materials"].get("field_border", "dark_oak_planks"),
        "soil": template["materials"].get("soil", "farmland"),
        "crop": template["materials"].get("crop", "moss_block"),
        "water": template["materials"].get("water", "water"),
        "grass": template["materials"].get("grass", "grass_block"),
        "light": template["materials"].get("light", "lantern"),
        "hay": template["materials"].get("hay", "hay_block"),
        "barrel": template["materials"].get("barrel", "barrel"),
        "leaf": template["materials"].get("leaf", "azalea_leaves"),
    }

    if main_material in FARM_MAIN_MATERIAL_PRESETS:
        materials.update(FARM_MAIN_MATERIAL_PRESETS[main_material])

    applied_stone = False
    applied_wood = False
    for material in secondary_materials:
        if not applied_stone and material in FARM_STONE_SECONDARY_MATERIALS:
            materials.update(FARM_STONE_SECONDARY_MATERIALS[material])
            applied_stone = True
            continue
        if not applied_wood and material in FARM_WOOD_SECONDARY_MATERIALS:
            materials.update(FARM_WOOD_SECONDARY_MATERIALS[material])
            applied_wood = True

    return materials


def _resolve_mine_materials(
    template: dict,
    main_material: str | None,
    secondary_materials: list[str],
) -> dict[str, str]:
    materials = {
        "rock": template["materials"].get("rock", "stone"),
        "trim": template["materials"].get("trim", "stone_bricks"),
        "slab": template["materials"].get("slab", "stone_slab"),
        "stairs": template["materials"].get("stairs", "stone_stairs"),
        "wood": template["materials"].get("wood", "oak_planks"),
        "log": template["materials"].get("log", "oak_log"),
        "wood_slab": template["materials"].get("wood_slab", "oak_slab"),
        "wood_stairs": template["materials"].get("wood_stairs", "oak_stairs"),
        "fence": template["materials"].get("fence", "oak_fence"),
        "glass": template["materials"].get("glass", "glass"),
        "bars": template["materials"].get("bars", "iron_bars"),
        "path": template["materials"].get("path", "dirt_path"),
        "ground": template["materials"].get("ground", "grass_block"),
        "dirt": template["materials"].get("dirt", "dirt"),
        "leaf": template["materials"].get("leaf", "azalea_leaves"),
        "light": template["materials"].get("light", "lantern"),
        "rail": template["materials"].get("rail", "rail"),
        "barrel": template["materials"].get("barrel", "barrel"),
        "tunnel_floor": template["materials"].get("tunnel_floor", "stone"),
    }

    if main_material in MINE_MAIN_MATERIAL_PRESETS:
        materials.update(MINE_MAIN_MATERIAL_PRESETS[main_material])

    applied_stone = False
    applied_wood = False
    for material in secondary_materials:
        if not applied_stone and material in MINE_STONE_SECONDARY_MATERIALS:
            materials.update(MINE_STONE_SECONDARY_MATERIALS[material])
            applied_stone = True
            continue
        if not applied_wood and material in MINE_WOOD_SECONDARY_MATERIALS:
            materials.update(MINE_WOOD_SECONDARY_MATERIALS[material])
            applied_wood = True

    return materials


def _add_block(blocks: dict[tuple[int, int, int], str], x: int, y: int, z: int, block: str) -> None:
    blocks[(x, y, z)] = block


def _remove_block(blocks: dict[tuple[int, int, int], str], x: int, y: int, z: int) -> None:
    blocks.pop((x, y, z), None)


def _neighbor(position: Position, direction: str) -> Position:
    dx, dy, dz = HORIZONTAL_DIRECTIONS[direction]
    x, y, z = position
    return x + dx, y + dy, z + dz


def _is_connectable(block: str | None) -> bool:
    return bool(block and block not in NON_SOLID_BLOCKS)


def _fill_rect(
    blocks: dict[tuple[int, int, int], str],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    y: int,
    block: str,
) -> None:
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            _add_block(blocks, x, y, z, block)


def _outline_rect(
    blocks: dict[tuple[int, int, int], str],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    y: int,
    block: str,
) -> None:
    for x in range(x1, x2 + 1):
        _add_block(blocks, x, y, z1, block)
        _add_block(blocks, x, y, z2, block)
    for z in range(z1, z2 + 1):
        _add_block(blocks, x1, y, z, block)
        _add_block(blocks, x2, y, z, block)


def _add_vertical_line(
    blocks: dict[tuple[int, int, int], str],
    x: int,
    z: int,
    y1: int,
    y2: int,
    block: str,
) -> None:
    for y in range(y1, y2 + 1):
        _add_block(blocks, x, y, z, block)


def _add_window_pair(
    blocks: dict[tuple[int, int, int], str],
    x: int,
    y: int,
    z: int,
    facing: str,
    materials: dict[str, str],
) -> None:
    _add_block(blocks, x, y, z, materials["windows"])
    if facing in {"north", "south"}:
        _add_block(blocks, x - 1, y, z, materials["shutter"])
        _add_block(blocks, x + 1, y, z, materials["shutter"])
    else:
        _add_block(blocks, x, y, z - 1, materials["shutter"])
        _add_block(blocks, x, y, z + 1, materials["shutter"])


def _add_glass_window(
    blocks: dict[Position, str],
    x: int,
    y: int,
    z: int,
    facing: str,
    materials: dict[str, str],
) -> None:
    _add_block(blocks, x, y, z, materials["window_block"])
    if facing in {"north", "south"}:
        _add_block(blocks, x - 1, y, z, materials["shutter"])
        _add_block(blocks, x + 1, y, z, materials["shutter"])
    else:
        _add_block(blocks, x, y, z - 1, materials["shutter"])
        _add_block(blocks, x, y, z + 1, materials["shutter"])


def _add_house_shell(
    blocks: dict[tuple[int, int, int], str],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    base_y: int,
    wall_height: int,
    materials: dict[str, str],
    upper_overhang: int,
) -> tuple[int, int, int, int]:
    _fill_rect(blocks, x1, x2, z1, z2, base_y, materials["foundation"])

    for y in range(base_y + 1, base_y + 3):
        for x in range(x1, x2 + 1):
            _add_block(
                blocks,
                x,
                y,
                z1,
                materials["foundation_mix"] if (x + y) % 3 == 0 else materials["foundation"],
            )
            _add_block(
                blocks,
                x,
                y,
                z2,
                materials["foundation_mix"] if (x + y + 1) % 3 == 0 else materials["foundation"],
            )
        for z in range(z1, z2 + 1):
            _add_block(
                blocks,
                x1,
                y,
                z,
                materials["foundation_mix"] if (z + y) % 3 == 0 else materials["foundation"],
            )
            _add_block(
                blocks,
                x2,
                y,
                z,
                materials["foundation_mix"] if (z + y + 1) % 3 == 0 else materials["foundation"],
            )

    upper_x1 = x1 - upper_overhang
    upper_x2 = x2 + upper_overhang
    upper_z1 = z1 - upper_overhang
    upper_z2 = z2 + upper_overhang
    beam_y = base_y + 3

    _outline_rect(blocks, upper_x1, upper_x2, upper_z1, upper_z2, beam_y, materials["frame"])

    for y in range(beam_y + 1, beam_y + wall_height + 1):
        for x in range(upper_x1, upper_x2 + 1):
            for z in range(upper_z1, upper_z2 + 1):
                if x not in (upper_x1, upper_x2) and z not in (upper_z1, upper_z2):
                    continue
                is_corner = x in (upper_x1, upper_x2) and z in (upper_z1, upper_z2)
                if is_corner or (x - upper_x1) % 4 == 0 or (z - upper_z1) % 4 == 0:
                    block = materials["frame"] if y % 2 else materials["frame_secondary"]
                else:
                    block = materials["wall_secondary"] if (x + z + y) % 5 == 0 else materials["walls"]
                _add_block(blocks, x, y, z, block)

    return upper_x1, upper_x2, upper_z1, upper_z2


def _add_house_door_and_windows(
    blocks: dict[tuple[int, int, int], str],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    base_y: int,
    wall_height: int,
    materials: dict[str, str],
) -> None:
    door_x = (x1 + x2) // 2
    left_door_x = door_x
    right_door_x = door_x + 1
    for x in (left_door_x, right_door_x):
        _remove_block(blocks, x, base_y + 1, z1)
        _remove_block(blocks, x, base_y + 2, z1)
        _remove_block(blocks, x, base_y + 3, z1)
        _remove_block(blocks, x, base_y + 1, z1 - 1)
        _remove_block(blocks, x, base_y + 2, z1 - 1)
    _add_block(blocks, left_door_x - 1, base_y + 2, z1, materials["frame_secondary"])
    _add_block(blocks, right_door_x + 1, base_y + 2, z1, materials["frame_secondary"])
    for step_x in range(left_door_x - 1, right_door_x + 2):
        _add_block(blocks, step_x, base_y + 1, z1 - 1, materials["foundation_accent"])
    _add_block(blocks, left_door_x, base_y + 1, z1 - 1, materials["door"])
    _add_block(blocks, left_door_x, base_y + 2, z1 - 1, materials["door"])
    _add_block(blocks, right_door_x, base_y + 1, z1 - 1, materials["door"])
    _add_block(blocks, right_door_x, base_y + 2, z1 - 1, materials["door"])

    window_y = base_y + 2
    _add_window_pair(blocks, x1 + 2, window_y, z1, "north", materials)
    _add_window_pair(blocks, x2 - 2, window_y, z1, "north", materials)
    _add_window_pair(blocks, x1 + 2, window_y, z2, "south", materials)
    _add_window_pair(blocks, x2 - 2, window_y, z2, "south", materials)
    _add_window_pair(blocks, x1, window_y, (z1 + z2) // 2, "west", materials)
    _add_window_pair(blocks, x2, window_y, (z1 + z2) // 2, "east", materials)

    if wall_height >= 5:
        upper_y = base_y + 5
        _add_glass_window(blocks, door_x, upper_y, z1 + 1, "north", materials)
        _add_glass_window(blocks, door_x + 1, upper_y, z1 + 1, "north", materials)
        _add_glass_window(blocks, door_x, upper_y, z2 - 1, "south", materials)
        _add_glass_window(blocks, door_x + 1, upper_y, z2 - 1, "south", materials)


def _add_front_porch(
    blocks: dict[tuple[int, int, int], str],
    x1: int,
    x2: int,
    z1: int,
    materials: dict[str, str],
) -> None:
    center_x = (x1 + x2) // 2
    porch_x1 = center_x - 3
    porch_x2 = center_x + 3
    porch_z1 = z1 - 2
    porch_z2 = z1 - 1

    _fill_rect(blocks, porch_x1, porch_x2, porch_z1, porch_z2, 1, materials["foundation"])
    _outline_rect(blocks, porch_x1, porch_x2, porch_z1, porch_z2, 2, materials["porch_wood"])

    left_post = center_x - 2
    right_post = center_x + 2
    for post_x in (left_post, right_post):
        _add_vertical_line(blocks, post_x, porch_z1, 2, 4, materials["porch_wood"])
        _add_vertical_line(blocks, post_x, porch_z2, 2, 3, materials["porch_wood"])

    for clear_x in range(center_x - 1, center_x + 2):
        for clear_y in range(2, 4):
            _remove_block(blocks, clear_x, clear_y, porch_z1)
            _remove_block(blocks, clear_x, clear_y, porch_z2)

    for x in range(porch_x1 - 1, porch_x2 + 2):
        _add_block(blocks, x, 5, porch_z1, materials["porch_roof"])
        _add_block(blocks, x, 5, porch_z2, materials["porch_roof"])
    for beam_x in range(left_post, right_post + 1):
        _add_block(blocks, beam_x, 4, porch_z1, materials["porch_wood"])

    _add_block(blocks, left_post, 3, porch_z2, materials["accent"])
    _add_block(blocks, right_post, 3, porch_z2, materials["accent"])


def _add_side_annex(
    blocks: dict[tuple[int, int, int], str],
    state_overrides: dict[Position, dict[str, str | bool]],
    x2: int,
    z1: int,
    z2: int,
    materials: dict[str, str],
) -> None:
    annex_x1 = x2 + 1
    annex_x2 = x2 + 3
    annex_z1 = z2 - 3
    annex_z2 = z2

    _fill_rect(blocks, annex_x1, annex_x2, annex_z1, annex_z2, 1, materials["foundation_mix"])
    for y in range(2, 4):
        for x in range(annex_x1, annex_x2 + 1):
            _add_block(blocks, x, y, annex_z1, materials["porch_wood"])
            _add_block(blocks, x, y, annex_z2, materials["porch_wood"])
        for z in range(annex_z1, annex_z2 + 1):
            _add_block(blocks, annex_x1, y, z, materials["porch_wood"])
            _add_block(blocks, annex_x2, y, z, materials["porch_wood"])

    for y in range(2, 4):
        _remove_block(blocks, annex_x1 + 1, y, annex_z1)
        _remove_block(blocks, annex_x1 + 1, y, annex_z2)
        _add_block(blocks, annex_x1 + 1, y, annex_z1, materials["window_block"])
        _add_block(blocks, annex_x1 + 1, y, annex_z2, materials["window_block"])

    for x in range(annex_x1 - 1, annex_x2 + 2):
        for z in range(annex_z1, annex_z2 + 1):
            if x in (annex_x1 - 1, annex_x2 + 1) or z in (annex_z1, annex_z2):
                _add_block(blocks, x, 4, z, materials["roof_secondary"])
                state_overrides[(x, 4, z)] = {"type": "bottom"}

    _add_block(blocks, annex_x2, 2, annex_z1 + 1, materials["barrel"])
    _add_block(blocks, annex_x2, 2, annex_z1 + 2, materials["barrel"])
    _add_block(blocks, annex_x1, 3, annex_z1 + 1, materials["window_block"])
    _add_block(blocks, annex_x1, 3, annex_z2 - 1, materials["window_block"])
    _add_block(blocks, annex_x2 + 1, 1, annex_z1 + 1, materials["leaves"])
    _add_block(blocks, annex_x2 + 1, 2, annex_z1 + 1, materials["vine"])
    _add_block(blocks, annex_x2 + 2, 1, annex_z1 + 1, materials["garden_post"])
    _add_block(blocks, annex_x2 + 2, 1, annex_z2 - 1, materials["garden_post"])


def _add_side_wall_windows(
    blocks: dict[Position, str],
    x2: int,
    z1: int,
    z2: int,
    materials: dict[str, str],
) -> None:
    side_x = x2
    for window_z in (z1 + 2, z1 + 5, z2 - 2):
        _remove_block(blocks, side_x, 2, window_z)
        _remove_block(blocks, side_x, 3, window_z)
        _add_block(blocks, side_x, 2, window_z, materials["window_block"])
        _add_block(blocks, side_x, 3, window_z, materials["windows"])
        _add_block(blocks, side_x - 1, 2, window_z, materials["shutter"])
        _add_block(blocks, side_x - 1, 3, window_z, materials["shutter"])


def _add_visible_front_entry(
    blocks: dict[Position, str],
    state_overrides: dict[Position, dict[str, str | bool]],
    x1: int,
    x2: int,
    z1: int,
    materials: dict[str, str],
) -> None:
    door_x = (x1 + x2) // 2
    left_door_x = door_x
    right_door_x = door_x + 1
    door_z = z1 - 1
    facade_z = z1 + 1

    for x in range(left_door_x - 2, right_door_x + 3):
        for y in range(1, 5):
            _remove_block(blocks, x, y, door_z)
            _remove_block(blocks, x, y, door_z - 1)
    for x in (left_door_x, right_door_x):
        _add_block(blocks, x, 1, door_z, materials["door"])
        _add_block(blocks, x, 2, door_z, materials["door"])
        state_overrides[(x, 1, door_z)] = {
            "facing": "east",
            "half": "lower",
            "hinge": "left" if x == left_door_x else "right",
            "open": False,
        }
        state_overrides[(x, 2, door_z)] = {
            "facing": "east",
            "half": "upper",
            "hinge": "left" if x == left_door_x else "right",
            "open": False,
        }
    for support_x in (left_door_x - 1, right_door_x + 1):
        _add_block(blocks, support_x, 1, facade_z, materials["porch_wood"])
        _add_block(blocks, support_x, 2, facade_z, materials["porch_wood"])
        _add_block(blocks, support_x, 3, facade_z, materials["porch_wood"])

    _add_block(blocks, left_door_x, 3, facade_z, materials["frame"])
    _add_block(blocks, right_door_x, 3, facade_z, materials["frame"])

    awning_x1 = left_door_x - 2
    awning_x2 = right_door_x + 2
    for x in range(awning_x1, awning_x2 + 1):
        _remove_block(blocks, x, 3, facade_z)
        _add_block(blocks, x, 4, facade_z, materials["roof_secondary"])
        state_overrides[(x, 4, facade_z)] = {"type": "bottom"}

    _add_block(blocks, awning_x1, 3, facade_z, materials["accent"])
    _add_block(blocks, awning_x2, 3, facade_z, materials["accent"])
    _add_block(blocks, left_door_x, 4, facade_z, materials["frame"])
    _add_block(blocks, right_door_x, 4, facade_z, materials["frame"])


def _add_front_feature_windows(
    blocks: dict[Position, str],
    x1: int,
    x2: int,
    z1: int,
    materials: dict[str, str],
) -> None:
    center_x = (x1 + x2) // 2
    door_left = center_x
    door_right = center_x + 1
    front_z = z1 - 1

    for window_x in (door_left - 3, door_right + 3):
        _remove_block(blocks, window_x, 2, front_z)
        _remove_block(blocks, window_x, 3, front_z)
        _add_block(blocks, window_x, 2, front_z, materials["window_block"])
        _add_block(blocks, window_x, 3, front_z, materials["windows"])

        _add_block(blocks, window_x - 1, 2, front_z, materials["shutter"])
        _add_block(blocks, window_x + 1, 2, front_z, materials["shutter"])
        _add_block(blocks, window_x - 1, 3, front_z, materials["shutter"])
        _add_block(blocks, window_x + 1, 3, front_z, materials["shutter"])

        _add_block(blocks, window_x, 1, front_z, materials["foundation_accent"])

    center_upper_z = front_z + 1
    for upper_x in (door_left, door_right):
        _remove_block(blocks, upper_x, 4, center_upper_z)
        _add_block(blocks, upper_x, 4, center_upper_z, materials["frame"])


def _add_house_detail_pass(
    blocks: dict[Position, str],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    materials: dict[str, str],
) -> None:
    center_x = (x1 + x2) // 2
    _add_block(blocks, center_x - 4, 1, z1 + 1, materials["barrel"])
    _add_block(blocks, center_x + 4, 1, z1 + 1, materials["barrel"])
    _add_block(blocks, center_x - 4, 2, z1 + 1, materials["accent"])
    _add_block(blocks, center_x + 4, 2, z1 + 1, materials["accent"])
    _add_block(blocks, x1 + 1, 1, z2 - 1, materials["flower_blue"])
    _add_block(blocks, x2 - 1, 1, z2 - 1, materials["flower_red"])
    _add_block(blocks, x1 + 2, 1, z1 + 2, materials["flower_yellow"])
    _add_block(blocks, x2 - 2, 1, z1 + 3, materials["flower_purple"])
    _add_block(blocks, x1 + 1, 2, z1 + 2, materials["accent"])
    _add_block(blocks, x2 - 1, 2, z1 + 3, materials["accent"])


def _add_gabled_roof(
    blocks: dict[tuple[int, int, int], str],
    state_overrides: dict[Position, dict[str, str | bool]],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    start_y: int,
    materials: dict[str, str],
) -> None:
    layer = 0
    while x1 + layer <= x2 - layer:
        left_x = x1 + layer
        right_x = x2 - layer
        roof_y = start_y + layer
        if left_x + 1 >= right_x:
            ridge_x = (left_x + right_x) // 2
            for z in range(z1, z2 + 1):
                _add_block(blocks, ridge_x, roof_y, z, materials["roof_secondary"])
                state_overrides[(ridge_x, roof_y, z)] = {"type": "bottom"}
            break
        for z in range(z1 - 1, z2 + 2):
            _add_block(blocks, left_x, roof_y, z, materials["roof"])
            state_overrides[(left_x, roof_y, z)] = {
                "facing": "east",
                "half": "bottom",
                "shape": "straight",
            }
            _add_block(blocks, right_x, roof_y, z, materials["roof"])
            state_overrides[(right_x, roof_y, z)] = {
                "facing": "west",
                "half": "bottom",
                "shape": "straight",
            }
        for z in (z1 - 1, z2 + 1):
            if left_x + 1 <= right_x - 1:
                for x in range(left_x + 1, right_x):
                    _add_block(blocks, x, roof_y, z, materials["roof_trim"])
                    state_overrides[(x, roof_y, z)] = {"type": "bottom"}
        layer += 1


def _add_chimney(
    blocks: dict[tuple[int, int, int], str],
    x: int,
    z: int,
    base_y: int,
    height: int,
    materials: dict[str, str],
) -> None:
    for y in range(base_y, base_y + height):
        _add_block(blocks, x, y, z, materials["chimney"])
    _add_block(blocks, x, base_y + height, z, materials["chimney_cap"])
    _add_block(blocks, x, base_y + height + 1, z, "campfire")


def _add_small_garden(
    blocks: dict[tuple[int, int, int], str],
    min_x: int,
    max_x: int,
    min_z: int,
    max_z: int,
    materials: dict[str, str],
) -> None:
    for x in range(min_x, max_x + 1):
        _add_block(blocks, x, 0, min_z, "grass_block")
        _add_block(blocks, x, 0, max_z, "grass_block")
    for z in range(min_z, max_z + 1):
        _add_block(blocks, min_x, 0, z, "grass_block")
        _add_block(blocks, max_x, 0, z, "grass_block")

    for x in range(min_x, max_x + 1, 3):
        _add_block(blocks, x, 1, min_z, materials["garden_post"])
        _add_block(blocks, x, 1, max_z, materials["garden_post"])
    for z in range(min_z, max_z + 1, 3):
        _add_block(blocks, min_x, 1, z, materials["garden_post"])
        _add_block(blocks, max_x, 1, z, materials["garden_post"])

    for x in range(min_x + 1, max_x):
        if x % 3 != 0:
            _add_block(blocks, x, 1, min_z, materials["fence"])
            _add_block(blocks, x, 1, max_z, materials["fence"])
    for z in range(min_z + 1, max_z):
        if z % 3 != 0:
            _add_block(blocks, min_x, 1, z, materials["fence"])
            _add_block(blocks, max_x, 1, z, materials["fence"])


def _add_path_and_lanterns(
    blocks: dict[tuple[int, int, int], str],
    center_x: int,
    start_z: int,
    gate_z: int,
    materials: dict[str, str],
) -> None:
    for offset, z in enumerate(range(gate_z, start_z + 1)):
        path_block = materials["path_secondary"] if offset % 2 == 0 else materials["path"]
        _add_block(blocks, center_x, 0, z, path_block)
        if z % 2 == 0:
            _add_block(blocks, center_x - 1, 0, z, materials["path_tertiary"])
        if z % 3 == 0:
            _add_block(blocks, center_x + 1, 0, z, materials["path"])

    for x, z in ((center_x - 2, start_z - 1), (center_x + 2, start_z - 1), (center_x - 3, gate_z + 1), (center_x + 3, gate_z + 1)):
        _add_block(blocks, x, 1, z, materials["garden_post"])
        _add_block(blocks, x, 2, z, materials["accent"])


def _add_greenery(
    blocks: dict[tuple[int, int, int], str],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    materials: dict[str, str],
) -> None:
    _add_block(blocks, x1 + 1, 1, z2 - 1, materials["leaves"])
    _add_block(blocks, x1 + 1, 2, z2 - 1, materials["vine"])
    _add_block(blocks, x2 - 1, 1, z1 + 2, materials["leaves"])
    _add_block(blocks, x2 - 1, 2, z1 + 2, materials["vine"])
    _add_block(blocks, x1 - 2, 1, z1 - 5, materials["flower_purple"])
    _add_block(blocks, x1 - 1, 1, z1 - 4, materials["flower_red"])
    _add_block(blocks, x1, 1, z1 - 5, materials["flower_blue"])
    _add_block(blocks, x2 + 1, 1, z1 + 1, materials["flower_yellow"])


def _add_small_tree(
    blocks: dict[tuple[int, int, int], str],
    x: int,
    z: int,
    materials: dict[str, str],
) -> None:
    _add_vertical_line(blocks, x, z, 1, 4, "oak_log")
    for leaf_x in range(x - 1, x + 2):
        for leaf_z in range(z - 1, z + 2):
            _add_block(blocks, leaf_x, 4, leaf_z, materials["leaves"])
            _add_block(blocks, leaf_x, 5, leaf_z, materials["leaves"])
    _add_block(blocks, x, 6, z, materials["leaves"])


def _fill_gable_faces(
    blocks: dict[Position, str],
    state_overrides: dict[Position, dict[str, str | bool]],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    wall_height: int,
    materials: dict[str, str],
) -> None:
    center_x = (x1 + x2) // 2
    half_span = center_x - x1

    for offset in range(half_span + 1):
        face_y = wall_height + 4 + offset
        left_x = x1 + offset
        right_x = x2 - offset
        if left_x == right_x:
            continue

        _add_block(blocks, left_x, face_y, z1, materials["roof"])
        state_overrides[(left_x, face_y, z1)] = {
            "facing": "east",
            "half": "bottom",
            "shape": "straight",
        }
        _add_block(blocks, right_x, face_y, z1, materials["roof"])
        state_overrides[(right_x, face_y, z1)] = {
            "facing": "west",
            "half": "bottom",
            "shape": "straight",
        }
        _add_block(blocks, left_x, face_y, z2, materials["roof"])
        state_overrides[(left_x, face_y, z2)] = {
            "facing": "east",
            "half": "bottom",
            "shape": "straight",
        }
        _add_block(blocks, right_x, face_y, z2, materials["roof"])
        state_overrides[(right_x, face_y, z2)] = {
            "facing": "west",
            "half": "bottom",
            "shape": "straight",
        }

        for x in range(left_x + 1, right_x):
            _add_block(blocks, x, face_y, z1, materials["walls"])
            _add_block(blocks, x, face_y, z2, materials["walls"])


def _add_reference_front_porch(
    blocks: dict[Position, str],
    state_overrides: dict[Position, dict[str, str | bool]],
    x1: int,
    x2: int,
    z1: int,
    materials: dict[str, str],
    size_profile: dict[str, int | str],
    add_decor: bool = False,
) -> tuple[int, int, int]:
    center_x = (x1 + x2) // 2
    porch_half_span = int(size_profile["porch_half_span"])
    porch_post_inset = int(size_profile["porch_post_inset"])
    clear_entry_half_span = int(size_profile["clear_entry_half_span"])
    porch_x1 = center_x - porch_half_span
    porch_x2 = center_x + porch_half_span
    porch_front_z = z1 - 2
    porch_back_z = z1 - 1

    _fill_rect(blocks, porch_x1, porch_x2, porch_front_z, porch_back_z, 3, materials["porch_planks"])

    for z, y in ((porch_front_z - 2, 1), (porch_front_z - 1, 2)):
        _add_block(blocks, center_x, y, z, materials["foundation_accent"])
        state_overrides[(center_x, y, z)] = {
            "facing": "south",
            "half": "bottom",
            "shape": "straight",
        }

    post_positions = (
        (porch_x1 + porch_post_inset, porch_front_z),
        (porch_x2 - porch_post_inset, porch_front_z),
        (porch_x1 + porch_post_inset, porch_back_z),
        (porch_x2 - porch_post_inset, porch_back_z),
    )
    for post_x, post_z in post_positions:
        _add_vertical_line(blocks, post_x, post_z, 1, 5, materials["porch_wood"])

    beam_z = porch_back_z
    for x in range(porch_x1, porch_x2 + 1):
        _add_block(blocks, x, 6, beam_z, materials["porch_beam"])
        _add_block(blocks, x, 7, porch_front_z, materials["porch_roof"])
        _add_block(blocks, x, 7, porch_back_z, materials["porch_roof"])
        state_overrides[(x, 7, porch_front_z)] = {"type": "bottom"}
        state_overrides[(x, 7, porch_back_z)] = {"type": "bottom"}

    for x in range(porch_x1, porch_x2 + 1):
        if center_x - clear_entry_half_span <= x <= center_x + clear_entry_half_span:
            continue
        _add_block(blocks, x, 4, porch_front_z, materials["railing"])

    if add_decor:
        for x in range(center_x - 3, center_x + 4):
            if center_x - clear_entry_half_span <= x <= center_x + clear_entry_half_span:
                continue
            _add_block(blocks, x, 4, porch_back_z, materials["leaves"])

        _add_block(blocks, center_x - 3, 5, porch_front_z, materials["accent"])
        _add_block(blocks, center_x + 3, 5, porch_front_z, materials["accent"])
        _add_block(blocks, center_x - 2, 4, porch_back_z, materials["flower_yellow"])
        _add_block(blocks, center_x + 2, 4, porch_back_z, materials["flower_purple"])

    return porch_x1, porch_x2, porch_front_z


def _add_reference_front_facade(
    blocks: dict[Position, str],
    state_overrides: dict[Position, dict[str, str | bool]],
    x1: int,
    x2: int,
    z1: int,
    materials: dict[str, str],
) -> None:
    center_x = (x1 + x2) // 2
    left_door_x = center_x
    right_door_x = center_x + 1
    door_z = z1

    for x in range(left_door_x, right_door_x + 1):
        for y in range(4, 6):
            _remove_block(blocks, x, y, door_z)
            _add_block(blocks, x, y, door_z, materials["door"])

    state_overrides[(left_door_x, 4, door_z)] = {
        "facing": "south",
        "half": "lower",
        "hinge": "left",
        "open": False,
    }
    state_overrides[(left_door_x, 5, door_z)] = {
        "facing": "south",
        "half": "upper",
        "hinge": "left",
        "open": False,
    }
    state_overrides[(right_door_x, 4, door_z)] = {
        "facing": "south",
        "half": "lower",
        "hinge": "right",
        "open": False,
    }
    state_overrides[(right_door_x, 5, door_z)] = {
        "facing": "south",
        "half": "upper",
        "hinge": "right",
        "open": False,
    }

    frame_positions = (
        (left_door_x - 1, 4, door_z),
        (left_door_x - 1, 5, door_z),
        (right_door_x + 1, 4, door_z),
        (right_door_x + 1, 5, door_z),
        (left_door_x, 6, door_z),
        (right_door_x, 6, door_z),
    )
    for x, y, z in frame_positions:
        _add_block(blocks, x, y, z, materials["frame_secondary"])

    for window_x1, window_x2 in ((x1 + 2, x1 + 3), (x2 - 3, x2 - 2)):
        for x in range(window_x1, window_x2 + 1):
            _add_block(blocks, x, 4, door_z, materials["window_block"])
            _add_block(blocks, x, 5, door_z, materials["windows"])
            _add_block(blocks, x, 3, door_z, materials["porch_planks"])
        _add_block(blocks, window_x1 - 1, 4, door_z, materials["shutter"])
        _add_block(blocks, window_x2 + 1, 4, door_z, materials["shutter"])
        _add_block(blocks, window_x1 - 1, 5, door_z, materials["shutter"])
        _add_block(blocks, window_x2 + 1, 5, door_z, materials["shutter"])

    for x in range(center_x - 2, center_x + 3):
        _add_block(blocks, x, 7, door_z, materials["wall_secondary"])
    _add_block(blocks, center_x - 1, 7, door_z, materials["window_block"])
    _add_block(blocks, center_x, 7, door_z, materials["window_block"])
    _add_block(blocks, center_x + 1, 7, door_z, materials["window_block"])
    _add_block(blocks, center_x - 2, 7, door_z, materials["frame"])
    _add_block(blocks, center_x + 2, 7, door_z, materials["frame"])


def _add_reference_side_windows(
    blocks: dict[Position, str],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    materials: dict[str, str],
    size_profile: dict[str, int | str],
) -> None:
    if size_profile["dormer_style"] == "small":
        window_positions = (z1 + 2, z2 - 2)
        lower_positions = ((x1 + x2) // 2,)
    elif size_profile["dormer_style"] == "large":
        window_positions = tuple(sorted({z1 + 2, z1 + 5, z1 + ((z2 - z1) // 2), z2 - 2}))
        lower_positions = (x1 + 2, (x1 + x2) // 2, x2 - 2)
    else:
        window_positions = (z1 + 2, z1 + 5, z2 - 2)
        lower_positions = (x1 + 2, x2 - 2)

    for z in window_positions:
        for y in (4, 5):
            _add_block(blocks, x2, y, z, materials["window_block"])
            _add_block(blocks, x1, y, z, materials["window_block"])
        _add_block(blocks, x2, 6, z, materials["windows"])
        _add_block(blocks, x1, 6, z, materials["windows"])
        _add_block(blocks, x2 - 1, 4, z, materials["shutter"])
        _add_block(blocks, x2 - 1, 5, z, materials["shutter"])
        _add_block(blocks, x1 + 1, 4, z, materials["shutter"])
        _add_block(blocks, x1 + 1, 5, z, materials["shutter"])

    for x in lower_positions:
        _add_block(blocks, x, 2, z1 + 1, materials["windows"])
        _add_block(blocks, x, 2, z2 - 1, materials["windows"])


def _add_reference_side_annex(
    blocks: dict[Position, str],
    state_overrides: dict[Position, dict[str, str | bool]],
    x2: int,
    z1: int,
    z2: int,
    materials: dict[str, str],
    size_profile: dict[str, int | str],
    add_decor: bool = False,
) -> None:
    annex_x1 = x2 + 1
    annex_x2 = x2 + int(size_profile["annex_width_extension"])
    annex_z1 = z1 + int(size_profile["annex_start_offset"])
    annex_z2 = z2
    annex_top_y = int(size_profile["annex_height"])
    annex_roof_layers = int(size_profile["annex_roof_layers"])

    _fill_rect(blocks, annex_x1, annex_x2, annex_z1, annex_z2, 1, materials["foundation"])

    for y in range(2, annex_top_y + 1):
        for x in range(annex_x1, annex_x2 + 1):
            _add_block(blocks, x, y, annex_z1, materials["frame"] if x in (annex_x1, annex_x2) else materials["walls"])
            _add_block(blocks, x, y, annex_z2, materials["frame"] if x in (annex_x1, annex_x2) else materials["walls"])
        for z in range(annex_z1, annex_z2 + 1):
            _add_block(blocks, annex_x1, y, z, materials["frame"])
            _add_block(blocks, annex_x2, y, z, materials["frame"])

    upper_window_rows = (3, 4) if annex_top_y <= 4 else (3, 4, 5)
    for y in upper_window_rows:
        _add_block(blocks, annex_x1 + 1, y, annex_z1, materials["window_block"])
        _add_block(blocks, annex_x2 - 1, y, annex_z2, materials["window_block"])
    _add_block(blocks, annex_x1 + 2, 3, annex_z1, materials["windows"])
    _add_block(blocks, annex_x2 - 2, 3, annex_z2, materials["windows"])

    for layer in range(annex_roof_layers):
        roof_x = annex_x1 - 1 + layer
        roof_y = 5 + layer
        for z in range(annex_z1 - 1, annex_z2 + 2):
            _add_block(blocks, roof_x, roof_y, z, materials["roof"])
            state_overrides[(roof_x, roof_y, z)] = {
                "facing": "west",
                "half": "bottom",
                "shape": "straight",
            }

    if add_decor:
        _add_block(blocks, annex_x2, 2, annex_z1 - 1, materials["barrel"])
        _add_block(blocks, annex_x2 + 1, 2, annex_z1, materials["barrel"])
        _add_block(blocks, annex_x2, 3, annex_z1, materials["accent"])
        _add_block(blocks, annex_x1 - 1, 2, annex_z2 - 1, materials["leaves"])
        _add_block(blocks, annex_x1 - 1, 3, annex_z2 - 1, materials["vine"])


def _add_reference_roof_details(
    blocks: dict[Position, str],
    state_overrides: dict[Position, dict[str, str | bool]],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    roof_start_y: int,
    materials: dict[str, str],
    size_profile: dict[str, int | str],
) -> None:
    center_x = (x1 + x2) // 2
    for z in range(z1, z2 + 1):
        _add_block(blocks, x1, roof_start_y - 1, z, materials["roof_edge"])
        _add_block(blocks, x2, roof_start_y - 1, z, materials["roof_edge"])

    dormer_z = z1 - 1
    dormer_style = str(size_profile["dormer_style"])
    if dormer_style == "small":
        frame_start = center_x - 1
        frame_end = center_x + 1
        window_columns = (center_x,)
        stair_left = center_x - 2
        stair_right = center_x + 2
    elif dormer_style == "large":
        frame_start = center_x - 2
        frame_end = center_x + 2
        window_columns = (center_x - 1, center_x + 1)
        stair_left = center_x - 3
        stair_right = center_x + 3
    else:
        frame_start = center_x - 1
        frame_end = center_x + 1
        window_columns = (center_x,)
        stair_left = center_x - 2
        stair_right = center_x + 2

    for x in range(frame_start, frame_end + 1):
        _add_block(blocks, x, roof_start_y - 1, dormer_z, materials["frame_secondary"])
    for x in window_columns:
        _add_block(blocks, x, roof_start_y - 1, dormer_z, materials["window_block"])
        _add_block(blocks, x, roof_start_y, dormer_z, materials["windows"])

    _add_block(blocks, stair_left, roof_start_y, dormer_z, materials["roof"])
    _add_block(blocks, stair_right, roof_start_y, dormer_z, materials["roof"])
    state_overrides[(stair_left, roof_start_y, dormer_z)] = {
        "facing": "east",
        "half": "bottom",
        "shape": "straight",
    }
    state_overrides[(stair_right, roof_start_y, dormer_z)] = {
        "facing": "west",
        "half": "bottom",
        "shape": "straight",
    }
    for x in range(frame_start, frame_end + 1):
        _add_block(blocks, x, roof_start_y + 1, dormer_z, materials["roof_secondary"])
        state_overrides[(x, roof_start_y + 1, dormer_z)] = {"type": "bottom"}


def _add_reference_ground_details(
    blocks: dict[Position, str],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    materials: dict[str, str],
) -> None:
    center_x = (x1 + x2) // 2
    _add_block(blocks, x2 - 1, 1, z2 + 1, materials["door"])
    _add_block(blocks, x2 - 1, 2, z2 + 1, materials["door"])
    _add_block(blocks, x1 + 1, 1, z2, materials["barrel"])
    _add_block(blocks, x1 + 2, 1, z2, materials["barrel"])
    _add_block(blocks, x1 + 1, 2, z2, materials["accent"])
    _add_block(blocks, x2 + 3, 1, z2 - 1, materials["barrel"])
    _add_block(blocks, x2 + 2, 1, z2 - 1, materials["barrel"])
    _add_block(blocks, x2 + 2, 1, z2, materials["flower_yellow"])
    _add_block(blocks, x2 + 1, 2, z2, materials["vine"])
    _add_block(blocks, center_x - 5, 1, z1 + 1, materials["flower_blue"])
    _add_block(blocks, center_x + 5, 1, z1 + 2, materials["flower_red"])


def _add_porch_extension(
    blocks: dict[Position, str],
    state_overrides: dict[Position, dict[str, str | bool]],
    porch_x1: int,
    porch_x2: int,
    porch_front_z: int,
    materials: dict[str, str],
) -> None:
    extension_front_z = porch_front_z - 1
    center_x = (porch_x1 + porch_x2) // 2

    _fill_rect(blocks, porch_x1 + 1, porch_x2 - 1, extension_front_z, porch_front_z, 3, materials["porch_planks"])

    for post_x in (porch_x1 + 1, porch_x2 - 1):
        _add_vertical_line(blocks, post_x, extension_front_z, 1, 5, materials["porch_wood"])

    for x in range(porch_x1, porch_x2 + 1):
        _add_block(blocks, x, 6, extension_front_z, materials["porch_beam"])
        _add_block(blocks, x, 7, extension_front_z, materials["porch_roof"])
        state_overrides[(x, 7, extension_front_z)] = {"type": "bottom"}

    for x in range(porch_x1 + 1, porch_x2):
        if center_x - 1 <= x <= center_x + 1:
            continue
        _add_block(blocks, x, 4, extension_front_z, materials["railing"])

    _add_block(blocks, porch_x1 + 2, 5, extension_front_z, materials["accent"])
    _add_block(blocks, porch_x2 - 2, 5, extension_front_z, materials["accent"])


def _add_stable_extension(
    blocks: dict[Position, str],
    state_overrides: dict[Position, dict[str, str | bool]],
    upper_x1: int,
    upper_z1: int,
    upper_z2: int,
    materials: dict[str, str],
    size_profile: dict[str, int | str],
) -> None:
    dormer_style = str(size_profile["dormer_style"])
    if dormer_style == "small":
        stable_width = 4
        stable_depth = 4
    elif dormer_style == "large":
        stable_width = 6
        stable_depth = 6
    else:
        stable_width = 5
        stable_depth = 5

    stable_x2 = upper_x1 - 2
    stable_x1 = stable_x2 - stable_width + 1
    stable_z1 = upper_z2 - stable_depth + 1
    stable_z2 = upper_z2 + 1

    _fill_rect(blocks, stable_x1, stable_x2, stable_z1, stable_z2, 0, materials["foundation"])

    for x in (stable_x1, stable_x2):
        for z in (stable_z1, stable_z2):
            _add_vertical_line(blocks, x, z, 1, 4, materials["frame"])

    for z in range(stable_z1, stable_z2 + 1):
        _add_block(blocks, stable_x1, 2, z, materials["frame"])
        _add_block(blocks, stable_x1, 3, z, materials["walls"])

    for x in range(stable_x1 + 1, stable_x2):
        _add_block(blocks, x, 2, stable_z1, materials["fence"])
        _add_block(blocks, x, 2, stable_z2, materials["fence"])
        _add_block(blocks, x, 1, stable_z1 + 1, materials["porch_planks"])

    entry_z = (stable_z1 + stable_z2) // 2
    for z in range(stable_z1 + 1, stable_z2):
        if z in (entry_z, entry_z + 1):
            continue
        _add_block(blocks, stable_x2, 2, z, materials["fence"])

    for layer in range(stable_width):
        roof_x = stable_x1 + layer
        roof_y = 5 + layer
        for z in range(stable_z1 - 1, stable_z2 + 2):
            _add_block(blocks, roof_x, roof_y, z, materials["roof"])
            state_overrides[(roof_x, roof_y, z)] = {
                "facing": "west",
                "half": "bottom",
                "shape": "straight",
            }

    _add_block(blocks, stable_x1 + 1, 1, entry_z, materials["barrel"])
    _add_block(blocks, stable_x1 + 2, 1, entry_z, materials["barrel"])
    _add_block(blocks, stable_x1 + 1, 2, stable_z2, materials["accent"])


def _add_modern_box_shell(
    blocks: dict[Position, str],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    floor_y: int,
    wall_top_y: int,
    materials: dict[str, str],
) -> None:
    _fill_rect(blocks, x1, x2, z1, z2, floor_y, materials["foundation"])
    for y in range(floor_y + 1, wall_top_y + 1):
        for x in range(x1, x2 + 1):
            _add_block(blocks, x, y, z1, materials["walls"])
            _add_block(blocks, x, y, z2, materials["walls"])
        for z in range(z1, z2 + 1):
            _add_block(blocks, x1, y, z, materials["walls"])
            _add_block(blocks, x2, y, z, materials["walls"])

    for corner in ((x1, z1), (x1, z2), (x2, z1), (x2, z2)):
        _add_vertical_line(blocks, corner[0], corner[1], floor_y + 1, wall_top_y + 1, materials["frame"])


def _add_modern_flat_roof(
    blocks: dict[Position, str],
    state_overrides: dict[Position, dict[str, str | bool]],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    roof_y: int,
    materials: dict[str, str],
) -> None:
    _fill_rect(blocks, x1, x2, z1, z2, roof_y, materials["roof"])
    for x in range(x1 - 1, x2 + 2):
        for z in (z1 - 1, z2 + 1):
            _add_block(blocks, x, roof_y + 1, z, materials["roof_slab"])
            state_overrides[(x, roof_y + 1, z)] = {"type": "bottom"}
    for z in range(z1, z2 + 1):
        for x in (x1 - 1, x2 + 1):
            _add_block(blocks, x, roof_y + 1, z, materials["roof_slab"])
            state_overrides[(x, roof_y + 1, z)] = {"type": "bottom"}


def _add_modern_glass_panel(
    blocks: dict[Position, str],
    x1: int,
    x2: int,
    y1: int,
    y2: int,
    z: int,
    materials: dict[str, str],
) -> None:
    for x in range(x1, x2 + 1):
        for y in range(y1, y2 + 1):
            _add_block(blocks, x, y, z, materials["glass"])


def _add_modern_side_glass_panel(
    blocks: dict[Position, str],
    x: int,
    z1: int,
    z2: int,
    y1: int,
    y2: int,
    materials: dict[str, str],
) -> None:
    for z in range(z1, z2 + 1):
        for y in range(y1, y2 + 1):
            _add_block(blocks, x, y, z, materials["glass"])


def _add_modern_planter(
    blocks: dict[Position, str],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    y: int,
    materials: dict[str, str],
    *,
    tall: bool = False,
    with_flowers: bool = False,
) -> None:
    _outline_rect(blocks, x1, x2, z1, z2, y, materials["trim"])
    inner_x1 = x1 + 1
    inner_x2 = x2 - 1
    inner_z1 = z1 + 1
    inner_z2 = z2 - 1

    if inner_x1 <= inner_x2 and inner_z1 <= inner_z2:
        _fill_rect(blocks, x1 + 1, x2 - 1, z1 + 1, z2 - 1, y, materials["terrace"])
        x_range = range(inner_x1, inner_x2 + 1)
        z_range = range(inner_z1, inner_z2 + 1)
    else:
        mid_x = (x1 + x2) // 2
        mid_z = (z1 + z2) // 2
        x_range = range(mid_x, mid_x + 1)
        z_range = range(mid_z, mid_z + 1)

    for x in x_range:
        for z in z_range:
            _add_block(blocks, x, y + 1, z, materials["leaf"])
            if tall:
                _add_block(blocks, x, y + 2, z, materials["leaf"])
            if with_flowers:
                flower = materials["flower_red"] if (x + z) % 2 == 0 else materials["flower_yellow"]
                _add_block(blocks, x, y + (3 if tall else 2), z, flower)


def _add_modern_pergola(
    blocks: dict[Position, str],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    base_y: int,
    materials: dict[str, str],
) -> None:
    top_y = base_y + 3
    for x, z in ((x1, z1), (x1, z2), (x2, z1), (x2, z2)):
        for y in range(base_y + 1, top_y + 1):
            _add_block(blocks, x, y, z, materials["accent_log"])

    for x in range(x1, x2 + 1):
        _add_block(blocks, x, top_y, z1, materials["accent_wood"])
        _add_block(blocks, x, top_y, z2, materials["accent_wood"])
    for z in range(z1, z2 + 1):
        _add_block(blocks, x1, top_y, z, materials["accent_wood"])
        _add_block(blocks, x2, top_y, z, materials["accent_wood"])

    for x in range(x1 + 1, x2):
        _add_block(blocks, x, top_y, z1 + 1, materials["accent_slab"])
        if z2 - z1 > 2:
            _add_block(blocks, x, top_y, z2 - 1, materials["accent_slab"])


def _add_modern_lounger(
    blocks: dict[Position, str],
    x: int,
    z: int,
    y: int,
    materials: dict[str, str],
) -> None:
    _add_block(blocks, x, y, z, materials["accent_wood"])
    _add_block(blocks, x + 1, y, z, materials["accent_wood"])
    _add_block(blocks, x + 1, y + 1, z, materials["roof_slab"])
    _add_block(blocks, x, y, z + 1, materials["accent_slab"])
    _add_block(blocks, x + 1, y, z + 1, materials["accent_slab"])


def _add_modern_terrace_extension(
    blocks: dict[Position, str],
    upper_x1: int,
    upper_x2: int,
    upper_z1: int,
    upper_z2: int,
    upper_top_y: int,
    materials: dict[str, str],
) -> None:
    terrace_y = upper_top_y + 2
    terrace_x1 = upper_x1 - 1
    terrace_x2 = upper_x2 + 1
    terrace_z1 = upper_z1 - 2
    terrace_z2 = upper_z1 + 4
    _fill_rect(blocks, terrace_x1, terrace_x2, terrace_z1, terrace_z2, terrace_y, materials["terrace"])

    for x in range(terrace_x1, terrace_x2 + 1):
        _add_block(blocks, x, terrace_y + 1, terrace_z1, materials["glass_pane"])
        _add_block(blocks, x, terrace_y + 1, terrace_z2, materials["glass_pane"])
    for z in range(terrace_z1 + 1, terrace_z2):
        _add_block(blocks, terrace_x1, terrace_y + 1, z, materials["glass_pane"])
        _add_block(blocks, terrace_x2, terrace_y + 1, z, materials["glass_pane"])

    pergola_x1 = terrace_x1 + 1
    pergola_x2 = min(terrace_x2 - 2, pergola_x1 + 4)
    pergola_z1 = terrace_z1 + 1
    pergola_z2 = terrace_z1 + 3
    _add_modern_pergola(blocks, pergola_x1, pergola_x2, pergola_z1, pergola_z2, terrace_y, materials)

    lounger_z = terrace_z2 - 2
    if terrace_x2 - terrace_x1 >= 5:
        _add_modern_lounger(blocks, terrace_x2 - 4, lounger_z, terrace_y + 1, materials)
        _add_modern_lounger(blocks, terrace_x2 - 2, lounger_z, terrace_y + 1, materials)

    _add_block(blocks, terrace_x2 - 1, terrace_y + 1, terrace_z1 + 2, materials["trim"])
    _add_block(blocks, terrace_x2 - 1, terrace_y + 2, terrace_z1 + 2, materials["light"])
    _add_modern_planter(blocks, terrace_x1 + 1, terrace_x1 + 3, terrace_z2 - 1, terrace_z2, terrace_y + 1, materials)
    _add_modern_planter(blocks, terrace_x2 - 3, terrace_x2 - 1, terrace_z2 - 1, terrace_z2, terrace_y + 1, materials)


def _add_modern_pool_extension(
    blocks: dict[Position, str],
    pool_x1: int,
    pool_x2: int,
    pool_z1: int,
    pool_z2: int,
    materials: dict[str, str],
) -> None:
    ext_x1 = max(pool_x1 - 1, 0)
    ext_x2 = pool_x2 + 4
    ext_z1 = pool_z1 - 3
    ext_z2 = pool_z2

    _fill_rect(blocks, ext_x1 - 1, ext_x2 + 1, ext_z1 - 1, ext_z2 + 2, 0, materials["pool_border"])
    _fill_rect(blocks, ext_x1, ext_x2 - 2, ext_z1, ext_z2, 0, materials["pool_water"])
    _fill_rect(blocks, ext_x2 - 1, ext_x2, ext_z1, ext_z2 + 1, 0, materials["terrace"])

    for z in range(ext_z1, ext_z2 + 2):
        _add_block(blocks, ext_x2 + 1, 0, z, materials["terrace"])
    for x in range(ext_x1 - 1, ext_x2 + 2):
        _add_block(blocks, x, 0, ext_z2 + 2, materials["terrace"])

    for z in range(ext_z1, ext_z2 + 1):
        _add_block(blocks, ext_x1 - 1, 1, z, materials["glass_pane"])
        _add_block(blocks, ext_x2 + 1, 1, z, materials["glass_pane"])

    _add_modern_lounger(blocks, ext_x2 - 1, ext_z1 + 1, 1, materials)
    _add_modern_lounger(blocks, ext_x2 - 1, ext_z1 + 3, 1, materials)
    _add_block(blocks, ext_x2 + 1, 1, ext_z1 + 2, materials["trim"])
    _add_block(blocks, ext_x2 + 1, 2, ext_z1 + 2, materials["light"])
    _add_block(blocks, ext_x2 + 1, 1, ext_z2 + 1, materials["trim"])
    _add_block(blocks, ext_x2 + 1, 2, ext_z2 + 1, materials["light"])


def _add_modern_garage_extension(
    blocks: dict[Position, str],
    x1: int,
    z1: int,
    z2: int,
    ground_height: int,
    materials: dict[str, str],
) -> None:
    garage_x1 = x1 - 7
    garage_x2 = x1 - 1
    garage_z1 = z1
    garage_z2 = z1 + min(6, z2 - z1)

    _add_modern_box_shell(blocks, garage_x1, garage_x2, garage_z1, garage_z2, 0, ground_height - 1, materials)

    door_open_x1 = garage_x1 + 1
    door_open_x2 = garage_x2 - 1
    for x in range(door_open_x1, door_open_x2 + 1):
        for y in range(1, ground_height - 1):
            _remove_block(blocks, x, y, garage_z1)
            _add_block(blocks, x, y, garage_z1, materials["glass"])
    for x in range(door_open_x1 - 1, door_open_x2 + 2):
        _add_block(blocks, x, ground_height - 1, garage_z1, materials["frame"])

    _fill_rect(blocks, garage_x1, garage_x2, garage_z1, garage_z2, ground_height, materials["roof"])
    for x in range(garage_x1 - 1, garage_x2 + 2):
        _add_block(blocks, x, ground_height + 1, garage_z1 - 1, materials["roof_slab"])
        _add_block(blocks, x, ground_height + 1, garage_z2 + 1, materials["roof_slab"])
    for z in range(garage_z1, garage_z2 + 1):
        _add_block(blocks, garage_x1 - 1, ground_height + 1, z, materials["roof_slab"])
        _add_block(blocks, garage_x2 + 1, ground_height + 1, z, materials["roof_slab"])

    driveway_z1 = garage_z1 - 5
    _fill_rect(blocks, garage_x1 + 1, garage_x2 - 1, driveway_z1, garage_z1 - 1, 0, materials["terrace"])
    for x in range(garage_x1 + 1, garage_x2, 2):
        _add_block(blocks, x, 0, driveway_z1 - 1, materials["trim"])
    _add_modern_planter(blocks, garage_x1, garage_x1 + 2, garage_z2 - 1, garage_z2 + 1, 0, materials)


def _add_modern_garden_extension(
    blocks: dict[Position, str],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    pool_z1: int,
    materials: dict[str, str],
) -> None:
    garden_x1 = x1 - 3
    garden_x2 = x2 + 3
    garden_z1 = pool_z1 - 4
    garden_z2 = z2 + 3

    for x in range(garden_x1, garden_x2 + 1):
        for z in range(garden_z1, garden_z2 + 1):
            if (x, 0, z) not in blocks:
                _add_block(blocks, x, 0, z, materials["grass"])

    path_x1 = x2 - 3
    path_x2 = x2 - 1
    _fill_rect(blocks, path_x1, path_x2, garden_z1 + 1, z1 - 1, 0, materials["terrace"])

    for z in range(garden_z1 + 1, z2 + 1):
        if z % 2 == 0:
            _add_block(blocks, x1 - 2, 1, z, materials["leaf"])
            _add_block(blocks, x1 - 2, 2, z, materials["leaf"])
        if z % 2 == 1:
            _add_block(blocks, x2 + 2, 1, z, materials["leaf"])
            _add_block(blocks, x2 + 2, 2, z, materials["leaf"])

    _add_modern_planter(blocks, x1 + 1, x1 + 3, z2 + 1, z2 + 2, 0, materials, with_flowers=True)
    _add_modern_planter(blocks, x2 - 3, x2 - 1, z2 + 1, z2 + 2, 0, materials, with_flowers=True)
    _add_modern_planter(blocks, x1 - 2, x1, garden_z1 + 1, garden_z1 + 3, 0, materials, tall=True)
    _add_block(blocks, path_x1, 1, z1 - 1, materials["light"])
    _add_block(blocks, path_x2, 1, z1 - 1, materials["light"])


def _add_modern_extra_decor(
    blocks: dict[Position, str],
    upper_x1: int,
    upper_x2: int,
    z1: int,
    z2: int,
    ground_height: int,
    materials: dict[str, str],
) -> None:
    canopy_y = ground_height + 1
    for x in range(upper_x2 - 3, upper_x2 + 1):
        _add_block(blocks, x, canopy_y, z1 - 1, materials["trim"])
        _add_block(blocks, x, canopy_y + 1, z1 - 1, materials["roof_slab"])
    _add_block(blocks, upper_x2 - 3, canopy_y, z1, materials["light"])
    _add_block(blocks, upper_x2 - 1, canopy_y, z1, materials["light"])

    feature_x = upper_x1 + 1
    for z in range(z1 + 1, min(z2, z1 + 5)):
        for y in range(ground_height + 1, ground_height + 4):
            if (z - z1) % 2 == 0:
                _add_block(blocks, feature_x, y, z, materials["accent_wood"])

    _add_modern_planter(blocks, upper_x1 + 1, upper_x1 + 3, z1 - 3, z1 - 2, 0, materials, with_flowers=True)
    _add_modern_planter(blocks, upper_x2 - 3, upper_x2 - 1, z2 + 1, z2 + 2, 0, materials)
    _add_block(blocks, upper_x1 + 2, ground_height + 1, z1 - 1, materials["light"])
    _add_block(blocks, upper_x2 - 2, ground_height + 1, z1 - 1, materials["light"])
    _add_block(blocks, upper_x1 + 2, ground_height + 6, z1 + 1, materials["glass"])
    _add_block(blocks, upper_x1 + 3, ground_height + 6, z1 + 1, materials["glass"])


def _add_castle_box_shell(
    blocks: dict[Position, str],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    floor_y: int,
    wall_top_y: int,
    materials: dict[str, str],
) -> None:
    _fill_rect(blocks, x1, x2, z1, z2, floor_y, materials["foundation"])
    for y in range(floor_y + 1, wall_top_y + 1):
        for x in range(x1, x2 + 1):
            _add_block(blocks, x, y, z1, materials["walls"])
            _add_block(blocks, x, y, z2, materials["walls"])
        for z in range(z1, z2 + 1):
            _add_block(blocks, x1, y, z, materials["walls"])
            _add_block(blocks, x2, y, z, materials["walls"])

    for corner_x, corner_z in ((x1, z1), (x1, z2), (x2, z1), (x2, z2)):
        _add_vertical_line(blocks, corner_x, corner_z, floor_y + 1, wall_top_y + 1, materials["trim"])


def _add_castle_battlements(
    blocks: dict[Position, str],
    state_overrides: dict[Position, dict[str, str | bool]],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    top_y: int,
    materials: dict[str, str],
) -> None:
    for x in range(x1, x2 + 1):
        for z in (z1, z2):
            _add_block(blocks, x, top_y + 1, z, materials["slab"])
            state_overrides[(x, top_y + 1, z)] = {"type": "bottom"}
            if (x - x1) % 2 == 0:
                _add_block(blocks, x, top_y + 2, z, materials["battlement"])
    for z in range(z1 + 1, z2):
        for x in (x1, x2):
            _add_block(blocks, x, top_y + 1, z, materials["slab"])
            state_overrides[(x, top_y + 1, z)] = {"type": "bottom"}
            if (z - z1) % 2 == 0:
                _add_block(blocks, x, top_y + 2, z, materials["battlement"])


def _add_castle_slit_window(
    blocks: dict[Position, str],
    x: int,
    z: int,
    y1: int,
    y2: int,
    materials: dict[str, str],
) -> None:
    for y in range(y1, y2 + 1):
        _add_block(blocks, x, y, z, materials["bars"])


def _add_castle_tower(
    blocks: dict[Position, str],
    state_overrides: dict[Position, dict[str, str | bool]],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    height: int,
    materials: dict[str, str],
) -> None:
    _add_castle_box_shell(blocks, x1, x2, z1, z2, 0, height, materials)
    if x2 - x1 >= 2:
        mid_x = (x1 + x2) // 2
        _add_castle_slit_window(blocks, mid_x, z1, 3, min(height - 2, 5), materials)
        _add_castle_slit_window(blocks, mid_x, z2, 3, min(height - 2, 5), materials)
    if z2 - z1 >= 2:
        mid_z = (z1 + z2) // 2
        _add_castle_slit_window(blocks, x1, mid_z, 3, min(height - 2, 5), materials)
        _add_castle_slit_window(blocks, x2, mid_z, 3, min(height - 2, 5), materials)
    _add_castle_battlements(blocks, state_overrides, x1, x2, z1, z2, height, materials)


def _add_castle_gate(
    blocks: dict[Position, str],
    state_overrides: dict[Position, dict[str, str | bool]],
    gate_x1: int,
    gate_x2: int,
    front_z: int,
    gate_depth: int,
    arch_height: int,
    materials: dict[str, str],
) -> None:
    for z in range(front_z, front_z + gate_depth):
        for x in range(gate_x1, gate_x2 + 1):
            for y in range(1, arch_height + 1):
                _remove_block(blocks, x, y, z)

    if gate_x2 - gate_x1 >= 1:
        door_x1 = gate_x1
        door_x2 = gate_x1 + 1
        door_z = front_z + gate_depth
        for x, hinge in ((door_x1, "left"), (door_x2, "right")):
            _add_block(blocks, x, 1, door_z, materials["door"])
            _add_block(blocks, x, 2, door_z, materials["door"])
            state_overrides[(x, 1, door_z)] = {"facing": "south", "half": "lower", "hinge": hinge, "open": False}
            state_overrides[(x, 2, door_z)] = {"facing": "south", "half": "upper", "hinge": hinge, "open": False}


def _add_castle_bridge(
    blocks: dict[Position, str],
    state_overrides: dict[Position, dict[str, str | bool]],
    gate_x1: int,
    gate_x2: int,
    front_z: int,
    length: int,
    materials: dict[str, str],
) -> None:
    z_start = front_z - length
    for z in range(z_start, front_z):
        for x in range(gate_x1, gate_x2 + 1):
            _add_block(blocks, x, 1, z, materials["bridge"])
        _add_block(blocks, gate_x1 - 1, 1, z, materials["bridge_slab"])
        _add_block(blocks, gate_x2 + 1, 1, z, materials["bridge_slab"])
        state_overrides[(gate_x1 - 1, 1, z)] = {"type": "bottom"}
        state_overrides[(gate_x2 + 1, 1, z)] = {"type": "bottom"}
        if (z - z_start) % 3 == 0:
            _add_block(blocks, gate_x1 - 1, 2, z, materials["trim"])
            _add_block(blocks, gate_x2 + 1, 2, z, materials["trim"])
        else:
            _add_block(blocks, gate_x1 - 1, 2, z, materials["bridge_slab"])
            _add_block(blocks, gate_x2 + 1, 2, z, materials["bridge_slab"])
            state_overrides[(gate_x1 - 1, 2, z)] = {"type": "bottom"}
            state_overrides[(gate_x2 + 1, 2, z)] = {"type": "bottom"}

        if (z - z_start) % 4 == 0:
            for y in range(0, 2):
                _add_block(blocks, gate_x1, y, z, materials["trim"])
                _add_block(blocks, gate_x2, y, z, materials["trim"])

    _add_block(blocks, gate_x1 - 1, 3, z_start + 1, materials["light"])
    _add_block(blocks, gate_x2 + 1, 3, z_start + 1, materials["light"])
    _add_block(blocks, gate_x1 - 1, 3, front_z - 2, materials["light"])
    _add_block(blocks, gate_x2 + 1, 3, front_z - 2, materials["light"])


def _add_castle_outer_wall(
    blocks: dict[Position, str],
    state_overrides: dict[Position, dict[str, str | bool]],
    wall_x1: int,
    wall_x2: int,
    wall_z1: int,
    wall_z2: int,
    wall_height: int,
    gate_x1: int,
    gate_x2: int,
    materials: dict[str, str],
) -> None:
    _add_castle_box_shell(blocks, wall_x1, wall_x2, wall_z1, wall_z2, 0, wall_height, materials)
    for x in range(gate_x1, gate_x2 + 1):
        for y in range(1, wall_height + 3):
            _remove_block(blocks, x, y, wall_z1)
            _remove_block(blocks, x, y, wall_z1 + 1)
    _add_castle_battlements(blocks, state_overrides, wall_x1, wall_x2, wall_z1, wall_z2, wall_height, materials)

    for z in range(wall_z1 + 2, wall_z2 - 1):
        _add_block(blocks, wall_x1 + 1, 1, z, materials["courtyard_path"])
        _add_block(blocks, wall_x2 - 1, 1, z, materials["courtyard_path"])
    for x in range(wall_x1 + 2, wall_x2 - 1):
        _add_block(blocks, x, 1, wall_z1 + 1, materials["courtyard_path"])
        _add_block(blocks, x, 1, wall_z2 - 1, materials["courtyard_path"])

    for x in (gate_x1 - 1, gate_x2 + 1):
        _add_vertical_line(blocks, x, wall_z1, 1, wall_height + 1, materials["trim"])
        _add_block(blocks, x, 2, wall_z1 - 1, materials["light"])

    for x in range(gate_x1 - 1, gate_x2 + 2):
        _add_block(blocks, x, wall_height + 1, wall_z1 + 1, materials["stairs"])
        state_overrides[(x, wall_height + 1, wall_z1 + 1)] = {
            "facing": "south",
            "half": "bottom",
            "shape": "straight",
        }


def _add_castle_extra_towers(
    blocks: dict[Position, str],
    state_overrides: dict[Position, dict[str, str | bool]],
    tower_positions: list[tuple[int, int, int, int, int]],
    materials: dict[str, str],
) -> None:
    for x1, x2, z1, z2, height in tower_positions:
        _add_castle_tower(blocks, state_overrides, x1, x2, z1, z2, height, materials)


def _add_castle_courtyard(
    blocks: dict[Position, str],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    materials: dict[str, str],
) -> None:
    _fill_rect(blocks, x1, x2, z1, z2, 0, materials["ground"])
    mid_x = (x1 + x2) // 2
    mid_z = (z1 + z2) // 2
    _fill_rect(blocks, mid_x - 1, mid_x + 1, z1, z2, 0, materials["courtyard_path"])
    _fill_rect(blocks, x1, x2, mid_z - 1, mid_z + 1, 0, materials["courtyard_path"])
    for x in (x1 + 1, x2 - 1):
        _add_block(blocks, x, 1, z1 + 1, materials["light"])
        _add_block(blocks, x, 1, z2 - 1, materials["light"])
    for x in range(mid_x - 1, mid_x + 2):
        for z in range(mid_z - 1, mid_z + 2):
            _add_block(blocks, x, 1, z, materials["trim"])
    _add_block(blocks, mid_x, 2, mid_z, materials["bars"])
    _add_block(blocks, mid_x, 3, mid_z, materials["light"])

    for px, pz in ((x1 + 2, z1 + 2), (x2 - 2, z1 + 2), (x1 + 2, z2 - 2), (x2 - 2, z2 - 2)):
        _add_block(blocks, px, 1, pz, materials["leaf"])
        _add_block(blocks, px, 2, pz, materials["leaf"])


def _add_castle_moat(
    blocks: dict[Position, str],
    moat_x1: int,
    moat_x2: int,
    moat_z1: int,
    moat_z2: int,
    front_gate_x1: int,
    front_gate_x2: int,
    front_z: int,
    materials: dict[str, str],
    *,
    leave_causeway: bool,
) -> None:
    wall_material = materials["trim"]
    for x in range(moat_x1, moat_x2 + 1):
        for z in range(moat_z1, moat_z2 + 1):
            on_ring = (
                x in (moat_x1, moat_x1 + 1, moat_x2 - 1, moat_x2)
                or z in (moat_z1, moat_z1 + 1, moat_z2 - 1, moat_z2)
            )
            if not on_ring:
                continue
            _add_block(blocks, x, -2, z, wall_material)
            _add_block(blocks, x, -1, z, materials["water"])
            _add_block(blocks, x, 0, z, materials["water"])

    for x in range(moat_x1, moat_x2 + 1):
        for z in (moat_z1, moat_z2):
            _add_block(blocks, x, 1, z, wall_material)
    for z in range(moat_z1, moat_z2 + 1):
        for x in (moat_x1, moat_x2):
            _add_block(blocks, x, 1, z, wall_material)

    if leave_causeway:
        for x in range(front_gate_x1 - 1, front_gate_x2 + 2):
            for z in range(moat_z1, front_z):
                _add_block(blocks, x, -2, z, wall_material)
                _remove_block(blocks, x, -1, z)
                _add_block(blocks, x, 0, z, materials["courtyard_path"])
    else:
        for x in range(front_gate_x1 - 1, front_gate_x2 + 2):
            _add_block(blocks, x, -2, front_z - 1, wall_material)
            _add_block(blocks, x, -1, front_z - 1, materials["water"])
            _add_block(blocks, x, 0, front_z - 1, materials["water"])


def _add_castle_extra_decor(
    blocks: dict[Position, str],
    state_overrides: dict[Position, dict[str, str | bool]],
    front_x1: int,
    front_x2: int,
    front_z: int,
    wall_height: int,
    materials: dict[str, str],
) -> None:
    for x in (front_x1 + 1, front_x2 - 1):
        _add_block(blocks, x, 2, front_z - 1, materials["light"])
        _add_block(blocks, x, 1, front_z - 1, materials["trim"])
    for x in range(front_x1 + 2, front_x2 - 1, 3):
        _add_block(blocks, x, 1, front_z + 1, materials["stairs"])
        state_overrides[(x, 1, front_z + 1)] = {"facing": "south", "half": "bottom", "shape": "straight"}
    for x in (front_x1 + 2, front_x2 - 2):
        for y in range(1, min(4, wall_height)):
            _add_block(blocks, x, y, front_z + 1, materials["trim"])
        _add_block(blocks, x, min(4, wall_height), front_z + 1, materials["stairs"])
        state_overrides[(x, min(4, wall_height), front_z + 1)] = {"facing": "south", "half": "bottom", "shape": "straight"}
    for x in range(front_x1 + 3, front_x2 - 2, 2):
        _add_block(blocks, x, wall_height, front_z + 1, materials["bars"])


def _generate_castle(
    width: int,
    depth: int,
    height: int,
    materials: dict[str, str],
    size: str,
    selected_extensions: list[str],
) -> tuple[dict[Position, str], dict[Position, dict[str, str | bool]]]:
    blocks: dict[Position, str] = {}
    state_overrides: dict[Position, dict[str, str | bool]] = {}
    extension_set = set(selected_extensions)

    if size == "small":
        front_height = 5
        keep_height = max(height, 8)
        rear_tower_height = keep_height + 3
        front_tower_height = front_height + 2
        tower_size = 3
        gate_width = 3
    elif size == "large":
        front_height = 8
        keep_height = max(height + 1, 14)
        rear_tower_height = keep_height + 4
        front_tower_height = front_height + 3
        tower_size = 4
        gate_width = 4
    else:
        front_height = 6
        keep_height = max(height, 11)
        rear_tower_height = keep_height + 4
        front_tower_height = front_height + 3
        tower_size = 4
        gate_width = 3

    x1, z1 = 0, 0
    x2, z2 = width - 1, depth - 1
    front_depth = max(4, depth // 3)
    keep_z1 = front_depth - 1

    gatehouse_x1 = tower_size - 1
    gatehouse_x2 = width - tower_size
    gate_x1 = (width - gate_width) // 2
    gate_x2 = gate_x1 + gate_width - 1

    _add_castle_box_shell(blocks, gatehouse_x1, gatehouse_x2, z1, front_depth, 0, front_height, materials)
    _add_castle_box_shell(blocks, tower_size, width - tower_size - 1, keep_z1, z2, 0, keep_height, materials)

    _add_castle_tower(blocks, state_overrides, 0, tower_size - 1, 0, tower_size, front_tower_height, materials)
    _add_castle_tower(blocks, state_overrides, width - tower_size, width - 1, 0, tower_size, front_tower_height, materials)
    _add_castle_tower(blocks, state_overrides, 0, tower_size - 1, depth - tower_size - 1, depth - 1, rear_tower_height, materials)
    _add_castle_tower(blocks, state_overrides, width - tower_size, width - 1, depth - tower_size - 1, depth - 1, rear_tower_height, materials)

    _add_castle_battlements(blocks, state_overrides, gatehouse_x1, gatehouse_x2, z1, front_depth, front_height, materials)
    _add_castle_battlements(blocks, state_overrides, tower_size, width - tower_size - 1, keep_z1, z2, keep_height, materials)

    _add_castle_gate(blocks, state_overrides, gate_x1, gate_x2, z1, 2, max(3, front_height - 1), materials)

    _add_castle_slit_window(blocks, gate_x1 - 2, z1, 3, max(3, front_height - 2), materials)
    _add_castle_slit_window(blocks, gate_x2 + 2, z1, 3, max(3, front_height - 2), materials)
    _add_castle_slit_window(blocks, (width // 2) - 1, keep_z1, front_height + 1, min(keep_height - 1, front_height + 3), materials)
    _add_castle_slit_window(blocks, (width // 2) + 1, keep_z1, front_height + 1, min(keep_height - 1, front_height + 3), materials)

    bridge_length = 5 if size == "small" else 7 if size == "medium" else 9
    if "puente_entrada" in extension_set:
        _add_castle_bridge(blocks, state_overrides, gate_x1, gate_x2, z1, bridge_length, materials)
    else:
        for z in range(-2, 0):
            for x in range(gate_x1, gate_x2 + 1):
                _add_block(blocks, x, 0, z, materials["courtyard_path"])

    outer_bounds = None
    if "muralla_exterior" in extension_set:
        wall_x1 = -5
        wall_x2 = width + 4
        wall_z1 = -6
        wall_z2 = depth + 4
        outer_wall_height = front_height + 1
        outer_gate_x1 = gate_x1
        outer_gate_x2 = gate_x2
        _add_castle_outer_wall(
            blocks,
            state_overrides,
            wall_x1,
            wall_x2,
            wall_z1,
            wall_z2,
            outer_wall_height,
            outer_gate_x1,
            outer_gate_x2,
            materials,
        )
        outer_bounds = (wall_x1, wall_x2, wall_z1, wall_z2, outer_wall_height)

    if "torres_adicionales" in extension_set:
        if outer_bounds:
            wall_x1, wall_x2, wall_z1, wall_z2, wall_height = outer_bounds
            mid_x = (wall_x1 + wall_x2) // 2
            mid_z = (wall_z1 + wall_z2) // 2
            extra_towers = [
                (wall_x1 - 1, wall_x1 + 1, wall_z1 - 1, wall_z1 + 1, wall_height + 3),
                (wall_x2 - 1, wall_x2 + 1, wall_z1 - 1, wall_z1 + 1, wall_height + 3),
                (wall_x1 - 1, wall_x1 + 1, wall_z2 - 1, wall_z2 + 1, wall_height + 3),
                (wall_x2 - 1, wall_x2 + 1, wall_z2 - 1, wall_z2 + 1, wall_height + 3),
                (mid_x - 1, mid_x + 1, wall_z2 - 1, wall_z2 + 1, wall_height + 2),
                (wall_x1 - 1, wall_x1 + 1, mid_z - 1, mid_z + 1, wall_height + 2),
                (wall_x2 - 1, wall_x2 + 1, mid_z - 1, mid_z + 1, wall_height + 2),
            ]
        else:
            mid_z = depth // 2
            extra_towers = [
                (-1, 1, mid_z - 1, mid_z + 1, keep_height + 2),
                (width - 2, width, mid_z - 1, mid_z + 1, keep_height + 2),
            ]
        _add_castle_extra_towers(blocks, state_overrides, extra_towers, materials)

    if "patio_interior" in extension_set:
        _add_castle_courtyard(blocks, tower_size + 2, width - tower_size - 3, keep_z1 + 2, min(z2 - 2, keep_z1 + 5), materials)

    if "decoracion_extra" in extension_set:
        _add_castle_extra_decor(blocks, state_overrides, gatehouse_x1, gatehouse_x2, z1, front_height, materials)

    if "foso" in extension_set:
        if outer_bounds:
            wall_x1, wall_x2, wall_z1, wall_z2, _ = outer_bounds
            moat_x1 = wall_x1 - 3
            moat_x2 = wall_x2 + 3
            moat_z1 = wall_z1 - 3
            moat_z2 = wall_z2 + 3
            front_for_moat = wall_z1
        else:
            moat_x1 = -3
            moat_x2 = width + 2
            moat_z1 = -4
            moat_z2 = depth + 2
            front_for_moat = z1
        _add_castle_moat(
            blocks,
            moat_x1,
            moat_x2,
            moat_z1,
            moat_z2,
            gate_x1,
            gate_x2,
            front_for_moat,
            materials,
            leave_causeway="puente_entrada" not in extension_set,
        )
        if "puente_entrada" in extension_set:
            _add_castle_bridge(blocks, state_overrides, gate_x1, gate_x2, z1, bridge_length + 4, materials)

    return blocks, state_overrides


def _add_farm_box_shell(
    blocks: dict[Position, str],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    floor_y: int,
    wall_top_y: int,
    materials: dict[str, str],
    *,
    wall_block: str | None = None,
) -> None:
    wall_material = wall_block or materials["walls"]
    _fill_rect(blocks, x1, x2, z1, z2, floor_y, materials["foundation"])
    for y in range(floor_y + 1, wall_top_y + 1):
        for x in range(x1, x2 + 1):
            _add_block(blocks, x, y, z1, wall_material)
            _add_block(blocks, x, y, z2, wall_material)
        for z in range(z1, z2 + 1):
            _add_block(blocks, x1, y, z, wall_material)
            _add_block(blocks, x2, y, z, wall_material)

    for cx, cz in ((x1, z1), (x1, z2), (x2, z1), (x2, z2)):
        _add_vertical_line(blocks, cx, cz, floor_y + 1, wall_top_y + 1, materials["log"])


def _add_farm_gabled_roof(
    blocks: dict[Position, str],
    state_overrides: dict[Position, dict[str, str | bool]],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    wall_top_y: int,
    materials: dict[str, str],
    *,
    gable_block: str | None = None,
) -> None:
    gable_material = gable_block or materials["gable"]
    span = max(1, (x2 - x1) // 2 + 1)
    for layer in range(span + 1):
        left_x = x1 + layer
        right_x = x2 - layer
        if left_x > right_x:
            break
        roof_y = wall_top_y + 1 + layer
        if left_x == right_x:
            for z in range(z1 - 1, z2 + 2):
                _add_block(blocks, left_x, roof_y, z, materials["roof_slab"])
                state_overrides[(left_x, roof_y, z)] = {"type": "bottom"}
        else:
            for z in range(z1 - 1, z2 + 2):
                _add_block(blocks, left_x, roof_y, z, materials["roof"])
                state_overrides[(left_x, roof_y, z)] = {"facing": "east", "half": "bottom", "shape": "straight"}
                _add_block(blocks, right_x, roof_y, z, materials["roof"])
                state_overrides[(right_x, roof_y, z)] = {"facing": "west", "half": "bottom", "shape": "straight"}
        for x in range(left_x, right_x + 1):
            _add_block(blocks, x, roof_y - 1, z1, gable_material)
            _add_block(blocks, x, roof_y - 1, z2, gable_material)


def _add_farm_crop_plot(
    blocks: dict[Position, str],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    materials: dict[str, str],
) -> None:
    _outline_rect(blocks, x1, x2, z1, z2, 0, materials["field_border"])
    for x in range(x1 + 1, x2):
        for z in range(z1 + 1, z2):
            if (x - x1) % 3 == 1:
                _add_block(blocks, x, 0, z, materials["water"])
            else:
                _add_block(blocks, x, 0, z, materials["soil"])
                _add_block(blocks, x, 1, z, materials["crop"])


def _add_farm_lantern_post(
    blocks: dict[Position, str],
    x: int,
    z: int,
    materials: dict[str, str],
) -> None:
    _add_block(blocks, x, 0, z, materials["trim"])
    _add_block(blocks, x, 1, z, materials["log"])
    _add_block(blocks, x, 2, z, materials["light"])


def _add_farm_window(
    blocks: dict[Position, str],
    x1: int,
    x2: int,
    y1: int,
    y2: int,
    z: int,
    materials: dict[str, str],
) -> None:
    for x in range(x1, x2 + 1):
        for y in range(y1, y2 + 1):
            _add_block(blocks, x, y, z, materials["glass"])


def _add_farm_side_window(
    blocks: dict[Position, str],
    x: int,
    z1: int,
    z2: int,
    y1: int,
    y2: int,
    materials: dict[str, str],
) -> None:
    for z in range(z1, z2 + 1):
        for y in range(y1, y2 + 1):
            _add_block(blocks, x, y, z, materials["glass"])


def _add_farm_pen(
    blocks: dict[Position, str],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    materials: dict[str, str],
) -> None:
    _fill_rect(blocks, x1, x2, z1, z2, 0, materials["grass"])
    _outline_rect(blocks, x1, x2, z1, z2, 1, materials["fence"])
    gate_x = (x1 + x2) // 2
    _remove_block(blocks, gate_x, 1, z1)
    _remove_block(blocks, gate_x + 1, 1, z1)
    _add_block(blocks, x1 + 2, 1, z2 - 2, materials["hay"])
    _add_block(blocks, x1 + 3, 1, z2 - 2, materials["hay"])
    _add_block(blocks, x1 + 2, 2, z2 - 2, materials["hay"])
    _add_block(blocks, x2 - 2, 0, z1 + 2, materials["water"])
    _add_block(blocks, x2 - 2, 0, z1 + 3, materials["water"])
    _add_block(blocks, gate_x - 1, 2, z1 + 1, materials["light"])
    _add_block(blocks, gate_x + 2, 2, z1 + 1, materials["light"])


def _add_farm_storage_shed(
    blocks: dict[Position, str],
    state_overrides: dict[Position, dict[str, str | bool]],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    materials: dict[str, str],
) -> None:
    wall_top = 4
    _add_farm_box_shell(blocks, x1, x2, z1, z2, 0, wall_top, materials, wall_block=materials["annex_walls"])
    _add_farm_gabled_roof(blocks, state_overrides, x1, x2, z1, z2, wall_top, materials, gable_block=materials["annex_walls"])
    for x in range(x1 + 1, min(x2, x1 + 3)):
        _add_block(blocks, x, 1, z1 + 1, materials["barrel"])
    _add_block(blocks, x2 - 1, 1, z1, materials["door"])
    _add_farm_window(blocks, x1 + 1, x1 + 2, 2, 3, z1, materials)
    _add_farm_side_window(blocks, x1, z1 + 2, z2 - 1, 2, 3, materials)
    for x in range(x1 + 1, x2 - 1):
        _add_block(blocks, x, 1, z2 + 1, materials["hay"])
    _add_farm_lantern_post(blocks, x1, z1 - 1, materials)
    _add_farm_lantern_post(blocks, x2, z1 - 1, materials)


def _add_farm_outer_fence(
    blocks: dict[Position, str],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    gate_x1: int,
    gate_x2: int,
    materials: dict[str, str],
) -> None:
    _outline_rect(blocks, x1, x2, z1, z2, 1, materials["fence"])
    for x in range(gate_x1, gate_x2 + 1):
        _remove_block(blocks, x, 1, z1)
    for x, z in ((x1, z1), (x2, z1), (x1, z2), (x2, z2)):
        _add_block(blocks, x, 0, z, materials["trim"])
        _add_block(blocks, x, 1, z, materials["log"])
        _add_block(blocks, x, 2, z, materials["light"])
    for z in range(z1 + 1, z2, 5):
        _add_block(blocks, x1, 0, z, materials["trim"])
        _add_block(blocks, x2, 0, z, materials["trim"])
    for x in range(x1 + 1, x2, 6):
        _add_block(blocks, x, 0, z2, materials["trim"])
    for x in range(gate_x1 - 1, gate_x2 + 2):
        _add_block(blocks, x, 0, z1, materials["path"])


def _generate_farm(
    width: int,
    depth: int,
    height: int,
    materials: dict[str, str],
    size: str,
    selected_extensions: list[str],
) -> tuple[dict[Position, str], dict[Position, dict[str, str | bool]]]:
    blocks: dict[Position, str] = {}
    state_overrides: dict[Position, dict[str, str | bool]] = {}
    extension_set = set(selected_extensions)

    if size == "small":
        barn_wall = 5
        shed_wall = 4
        annex_wall = 3
        barn_width = max(9, width - 6)
        barn_depth = depth
        front_window_y2 = 3
        loft_window_y1 = 4
        loft_window_y2 = 4
        front_window_half_width = 0
        loft_window_half_width = 0
        side_window_span = 1
        annex_window_half_width = 1
    elif size == "large":
        barn_wall = 8
        shed_wall = 5
        annex_wall = 4
        barn_width = max(13, width - 8)
        barn_depth = depth + 1
        front_window_y2 = 5
        loft_window_y1 = 4
        loft_window_y2 = 6
        front_window_half_width = 1
        loft_window_half_width = 1
        side_window_span = 3
        annex_window_half_width = 2
    else:
        barn_wall = 6
        shed_wall = 4
        annex_wall = 3
        barn_width = max(11, width - 7)
        barn_depth = depth
        front_window_y2 = 4
        loft_window_y1 = 4
        loft_window_y2 = 5
        front_window_half_width = 1
        loft_window_half_width = 1
        side_window_span = 2
        annex_window_half_width = 1

    barn_x1 = 6
    barn_x2 = barn_x1 + barn_width - 1
    barn_z1 = 0
    barn_z2 = barn_z1 + barn_depth - 1

    shed_x1 = 0
    shed_x2 = barn_x1
    shed_z1 = 3
    shed_z2 = min(barn_z2 - 1, 8 if size != "large" else 10)

    annex_x1 = barn_x2 - 2
    annex_x2 = barn_x2 + 4
    annex_z1 = 2
    annex_z2 = min(barn_z2 - 2, 7)

    _add_farm_box_shell(blocks, barn_x1, barn_x2, barn_z1, barn_z2, 0, barn_wall, materials)
    _add_farm_gabled_roof(blocks, state_overrides, barn_x1, barn_x2, barn_z1, barn_z2, barn_wall, materials)

    _add_farm_box_shell(blocks, shed_x1, shed_x2, shed_z1, shed_z2, 0, shed_wall, materials)
    _add_farm_gabled_roof(blocks, state_overrides, shed_x1, shed_x2, shed_z1, shed_z2, shed_wall, materials)

    _add_farm_box_shell(
        blocks,
        annex_x1,
        annex_x2,
        annex_z1,
        annex_z2,
        0,
        annex_wall,
        materials,
        wall_block=materials["annex_walls"],
    )
    _add_farm_gabled_roof(
        blocks,
        state_overrides,
        annex_x1,
        annex_x2,
        annex_z1,
        annex_z2,
        annex_wall,
        materials,
        gable_block=materials["annex_walls"],
    )

    door_x1 = (barn_x1 + barn_x2) // 2 - 1
    door_x2 = door_x1 + 1
    for x, hinge in ((door_x1, "left"), (door_x2, "right")):
        _add_block(blocks, x, 1, barn_z1, materials["door"])
        _add_block(blocks, x, 2, barn_z1, materials["door"])
        state_overrides[(x, 1, barn_z1)] = {"facing": "south", "half": "lower", "hinge": hinge, "open": False}
        state_overrides[(x, 2, barn_z1)] = {"facing": "south", "half": "upper", "hinge": hinge, "open": False}

    left_front_window_center = door_x1 - 4
    right_front_window_center = door_x2 + 4
    _add_farm_window(
        blocks,
        left_front_window_center - front_window_half_width,
        left_front_window_center + front_window_half_width,
        2,
        front_window_y2,
        barn_z1,
        materials,
    )
    _add_farm_window(
        blocks,
        right_front_window_center - front_window_half_width,
        right_front_window_center + front_window_half_width,
        2,
        front_window_y2,
        barn_z1,
        materials,
    )
    _add_farm_window(
        blocks,
        max(barn_x1 + 2, door_x1 - loft_window_half_width),
        min(barn_x2 - 2, door_x2 + loft_window_half_width),
        loft_window_y1,
        loft_window_y2,
        barn_z1,
        materials,
    )
    _add_farm_side_window(blocks, barn_x1, barn_z1 + 3, barn_z1 + 3 + side_window_span, 2, 3, materials)
    _add_farm_side_window(blocks, barn_x2, barn_z1 + 3, barn_z1 + 3 + side_window_span, 2, 3, materials)
    _add_farm_side_window(blocks, barn_x1, barn_z2 - 3 - side_window_span, barn_z2 - 3, 2, 3, materials)
    _add_farm_side_window(blocks, barn_x2, barn_z2 - 3 - side_window_span, barn_z2 - 3, 2, 3, materials)

    for z in range(shed_z1 + 1, shed_z2, 2):
        _add_block(blocks, shed_x2, 2, z, materials["glass"])
    _add_farm_window(blocks, shed_x1 + 2, min(shed_x2 - 1, shed_x1 + 3 + front_window_half_width), 2, front_window_y2, shed_z1, materials)
    for z in range(annex_z1 + 1, annex_z2):
        _add_block(blocks, annex_x1, 2, z, materials["glass"])
    _add_farm_window(
        blocks,
        annex_x1 + 1,
        min(annex_x2 - 1, annex_x1 + 1 + annex_window_half_width * 2),
        2,
        2 + (1 if size != "small" else 0),
        annex_z1,
        materials,
    )

    path_center = (door_x1 + door_x2) // 2
    for z in range(-8, 0):
        for x in range(path_center - 1, path_center + 2):
            _add_block(blocks, x, 0, z, materials["path"])

    _add_farm_crop_plot(blocks, shed_x1 - 1, shed_x2 - 1, barn_z2 - 4, barn_z2 + 2, materials)
    _add_farm_lantern_post(blocks, path_center - 3, -1, materials)
    _add_farm_lantern_post(blocks, path_center + 3, -1, materials)

    if "huerto_ampliado" in extension_set:
        _add_farm_crop_plot(blocks, shed_x1 - 6, shed_x2 - 2, barn_z2 - 4, barn_z2 + 2, materials)
        _add_farm_crop_plot(blocks, barn_x2 - 3, barn_x2 + 5, barn_z2 - 5, barn_z2 + 2, materials)
        _add_farm_crop_plot(blocks, barn_x1 + 2, barn_x1 + 8, barn_z2 + 3, barn_z2 + 8, materials)
        for x in range(barn_x1 + 4, barn_x1 + 7):
            _add_block(blocks, x, 0, barn_z2 + 2, materials["path"])

    if "valla_exterior" in extension_set:
        _add_farm_outer_fence(blocks, -7, barn_x2 + 8, -9, barn_z2 + 4, path_center - 1, path_center + 1, materials)
        for z in range(-8, barn_z2 + 3):
            if z % 4 == 0:
                _add_farm_lantern_post(blocks, -5, z, materials)
                _add_farm_lantern_post(blocks, barn_x2 + 6, z, materials)

    if "establo_animales" in extension_set:
        _add_farm_pen(blocks, -8, 4, -7, 3, materials)
        _add_farm_box_shell(blocks, -8, -2, -7, -2, 0, 3, materials, wall_block=materials["annex_walls"])
        _add_farm_gabled_roof(blocks, state_overrides, -8, -2, -7, -2, 3, materials, gable_block=materials["annex_walls"])
        _add_farm_pen(blocks, -8, -1, 5, 11, materials)
        _add_block(blocks, -6, 1, 4, materials["hay"])
        _add_block(blocks, -5, 1, 4, materials["hay"])

    if "almacen" in extension_set:
        _add_farm_storage_shed(blocks, state_overrides, barn_x2 + 5, barn_x2 + 12, 2, 9, materials)
        _add_farm_storage_shed(blocks, state_overrides, barn_x2 + 7, barn_x2 + 11, 10, 14, materials)

    if "decoracion_extra" in extension_set:
        _add_block(blocks, barn_x1 - 2, 1, 1, materials["hay"])
        _add_block(blocks, barn_x1 - 2, 2, 1, materials["hay"])
        _add_block(blocks, barn_x1 - 3, 1, 2, materials["barrel"])
        _add_block(blocks, barn_x2 + 1, 1, barn_z2 - 1, materials["barrel"])
        _add_block(blocks, barn_x2 + 2, 1, barn_z2 - 1, materials["hay"])
        _add_block(blocks, shed_x1 + 1, 1, shed_z1 - 1, materials["leaf"])
        _add_block(blocks, shed_x1 + 1, 2, shed_z1 - 1, materials["leaf"])
        _add_farm_lantern_post(blocks, barn_x2 + 2, -2, materials)
        _add_farm_lantern_post(blocks, barn_x1 - 4, 0, materials)
        _add_block(blocks, barn_x1 - 4, 1, 1, materials["barrel"])
        _add_block(blocks, barn_x1 - 5, 1, 1, materials["hay"])
        _add_block(blocks, barn_x1 - 5, 2, 1, materials["hay"])
        _add_block(blocks, annex_x2 + 1, 1, annex_z2 + 1, materials["barrel"])
        _add_block(blocks, annex_x2 + 2, 1, annex_z2 + 1, materials["leaf"])
        _add_block(blocks, annex_x2 + 2, 2, annex_z2 + 1, materials["leaf"])

    return blocks, state_overrides


def _add_mine_hillside(
    blocks: dict[Position, str],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    max_height: int,
    materials: dict[str, str],
) -> None:
    center_x = (x1 + x2) // 2
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            distance = abs(x - center_x) + max(0, z - z1)
            height = max(2, max_height - distance // 2)
            for y in range(0, height):
                block = materials["dirt"] if y < height - 1 else materials["ground"]
                _add_block(blocks, x, y, z, block)


def _add_mine_support_frame(
    blocks: dict[Position, str],
    state_overrides: dict[Position, dict[str, str | bool]],
    x1: int,
    x2: int,
    z: int,
    height: int,
    materials: dict[str, str],
) -> None:
    _add_vertical_line(blocks, x1, z, 1, height, materials["log"])
    _add_vertical_line(blocks, x2, z, 1, height, materials["log"])
    for x in range(x1, x2 + 1):
        _add_block(blocks, x, height + 1, z, materials["wood_stairs"])
        state_overrides[(x, height + 1, z)] = {"facing": "south", "half": "bottom", "shape": "straight"}
    _add_block(blocks, x1 - 1, height, z, materials["wood_slab"])
    _add_block(blocks, x2 + 1, height, z, materials["wood_slab"])
    state_overrides[(x1 - 1, height, z)] = {"type": "bottom"}
    state_overrides[(x2 + 1, height, z)] = {"type": "bottom"}


def _add_mine_rail_run(
    blocks: dict[Position, str],
    x: int,
    z1: int,
    z2: int,
    materials: dict[str, str],
) -> None:
    for z in range(z1, z2 + 1):
        _add_block(blocks, x, 0, z, materials["tunnel_floor"])
        _add_block(blocks, x, 1, z, materials["rail"])


def _add_mine_storage_area(
    blocks: dict[Position, str],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    materials: dict[str, str],
) -> None:
    _fill_rect(blocks, x1, x2, z1, z2, 0, materials["path"])
    _add_block(blocks, x1 + 1, 1, z1 + 1, materials["barrel"])
    _add_block(blocks, x1 + 2, 1, z1 + 1, materials["barrel"])
    _add_block(blocks, x2 - 1, 1, z2 - 1, materials["barrel"])
    _add_block(blocks, x2 - 2, 1, z2 - 1, materials["barrel"])


def _add_mine_small_shed(
    blocks: dict[Position, str],
    state_overrides: dict[Position, dict[str, str | bool]],
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    materials: dict[str, str],
) -> None:
    wall_top = 3
    _fill_rect(blocks, x1, x2, z1, z2, 0, materials["path"])
    for y in range(1, wall_top + 1):
        _add_block(blocks, x1, y, z1, materials["log"])
        _add_block(blocks, x2, y, z1, materials["log"])
        _add_block(blocks, x1, y, z2, materials["log"])
        _add_block(blocks, x2, y, z2, materials["log"])
    for x in range(x1, x2 + 1):
        _add_block(blocks, x, wall_top + 1, z1, materials["wood_stairs"])
        state_overrides[(x, wall_top + 1, z1)] = {"facing": "south", "half": "bottom", "shape": "straight"}
        _add_block(blocks, x, wall_top + 1, z2, materials["wood_stairs"])
        state_overrides[(x, wall_top + 1, z2)] = {"facing": "north", "half": "bottom", "shape": "straight"}
    for z in range(z1 + 1, z2):
        for x in range(x1, x2 + 1):
            _add_block(blocks, x, wall_top + 1, z, materials["wood_slab"])
            state_overrides[(x, wall_top + 1, z)] = {"type": "bottom"}
    _add_block(blocks, x1 + 1, 1, z1 + 1, materials["barrel"])
    _add_block(blocks, x2 - 1, 1, z1 + 1, materials["barrel"])
    _add_block(blocks, x1 + 1, 1, z2 - 1, materials["barrel"])
    _add_block(blocks, x2 - 1, 1, z2 - 1, materials["barrel"])


def _add_mine_railing(
    blocks: dict[Position, str],
    x1: int,
    x2: int,
    z: int,
    materials: dict[str, str],
) -> None:
    for x in range(x1, x2 + 1):
        _add_block(blocks, x, 1, z, materials["fence"])


def _generate_mine_entrance(
    width: int,
    depth: int,
    height: int,
    materials: dict[str, str],
    size: str,
    selected_extensions: list[str],
) -> tuple[dict[Position, str], dict[Position, dict[str, str | bool]]]:
    blocks: dict[Position, str] = {}
    state_overrides: dict[Position, dict[str, str | bool]] = {}
    extension_set = set(selected_extensions)

    if size == "small":
        entrance_width = 5
        entrance_height = 4
        tunnel_length = 6
        porch_depth = 2
        hillside_height = 6
    elif size == "large":
        entrance_width = 9
        entrance_height = 6
        tunnel_length = 10
        porch_depth = 4
        hillside_height = 10
    else:
        entrance_width = 7
        entrance_height = 5
        tunnel_length = 8
        porch_depth = 3
        hillside_height = 8

    entrance_x1 = 4
    entrance_x2 = entrance_x1 + entrance_width - 1
    center_x = (entrance_x1 + entrance_x2) // 2
    tunnel_z1 = 0
    tunnel_z2 = tunnel_length

    _add_mine_hillside(blocks, 0, width - 1, tunnel_z1, depth + 5, hillside_height, materials)

    for z in range(tunnel_z1, tunnel_z2 + 1):
        for x in range(entrance_x1, entrance_x2 + 1):
            for y in range(1, entrance_height + 1):
                _remove_block(blocks, x, y, z)
                if y == 1:
                    _add_block(blocks, x, y, z, materials["tunnel_floor"])
        for y in range(1, entrance_height + 2):
            _add_block(blocks, entrance_x1 - 1, y, z, materials["rock"])
            _add_block(blocks, entrance_x2 + 1, y, z, materials["rock"])
        for x in range(entrance_x1 - 1, entrance_x2 + 2):
            _add_block(blocks, x, entrance_height + 1, z, materials["rock"])

    for y in range(1, entrance_height + 2):
        _add_block(blocks, entrance_x1 - 1, y, tunnel_z1, materials["trim"])
        _add_block(blocks, entrance_x2 + 1, y, tunnel_z1, materials["trim"])
    for x in range(entrance_x1 - 1, entrance_x2 + 2):
        _add_block(blocks, x, entrance_height + 2, tunnel_z1, materials["slab"])
        state_overrides[(x, entrance_height + 2, tunnel_z1)] = {"type": "bottom"}

    for z in range(tunnel_z1 + 1, tunnel_z2 + 1, 3):
        _add_mine_support_frame(blocks, state_overrides, entrance_x1, entrance_x2, z, entrance_height, materials)

    _add_mine_support_frame(blocks, state_overrides, entrance_x1, entrance_x2, -1, entrance_height, materials)

    for z in range(-porch_depth, 0):
        for x in range(center_x - 1, center_x + 2):
            _add_block(blocks, x, 0, z, materials["path"])
    _add_mine_rail_run(blocks, center_x, -porch_depth, tunnel_z2, materials)

    _add_block(blocks, entrance_x1 - 2, 1, -1, materials["light"])
    _add_block(blocks, entrance_x2 + 2, 1, -1, materials["light"])

    _add_block(blocks, entrance_x1 - 1, 2, 1, materials["bars"])
    _add_block(blocks, entrance_x2 + 1, 2, 1, materials["bars"])

    _add_block(blocks, entrance_x1 + 1, 2, tunnel_z1, materials["glass"])
    _add_block(blocks, entrance_x2 - 1, 2, tunnel_z1, materials["glass"])

    for z in range(-6, 1):
        _add_block(blocks, center_x, 0, z, materials["path"])
    for x in range(center_x - 2, center_x + 3):
        _add_block(blocks, x, 0, -6, materials["path"])

    if "decoracion_railes" in extension_set:
        _add_mine_rail_run(blocks, center_x - 2, -8, -2, materials)
        _add_mine_rail_run(blocks, center_x + 2, -7, -3, materials)
        _add_block(blocks, center_x - 3, 1, -8, materials["barrel"])
        _add_block(blocks, center_x + 3, 1, -7, materials["barrel"])
        _add_block(blocks, center_x - 2, 0, -9, materials["path"])
        _add_block(blocks, center_x + 2, 0, -8, materials["path"])
        _add_mine_railing(blocks, center_x - 4, center_x - 1, -9, materials)
        _add_mine_railing(blocks, center_x + 1, center_x + 4, -8, materials)
        _add_block(blocks, center_x - 4, 2, -9, materials["light"])
        _add_block(blocks, center_x + 4, 2, -8, materials["light"])

    if "almacen_exterior" in extension_set:
        _add_mine_storage_area(blocks, entrance_x2 + 3, entrance_x2 + 8, -4, 2, materials)
        _add_block(blocks, entrance_x2 + 6, 1, -5, materials["light"])
        _add_mine_small_shed(blocks, state_overrides, entrance_x2 + 4, entrance_x2 + 9, -6, -1, materials)
        _add_mine_railing(blocks, entrance_x2 + 3, entrance_x2 + 8, 3, materials)

    if "estructuras_madera" in extension_set:
        _add_mine_support_frame(blocks, state_overrides, entrance_x1 - 2, entrance_x1 + 1, -2, entrance_height - 1, materials)
        _add_mine_support_frame(blocks, state_overrides, entrance_x2 - 1, entrance_x2 + 2, -2, entrance_height - 1, materials)
        _add_mine_support_frame(blocks, state_overrides, entrance_x1 + 1, entrance_x2 - 1, tunnel_z2 + 1, entrance_height - 1, materials)
        _add_mine_support_frame(blocks, state_overrides, entrance_x1 - 3, entrance_x1 - 1, 2, entrance_height - 2, materials)
        _add_mine_support_frame(blocks, state_overrides, entrance_x2 + 1, entrance_x2 + 3, 2, entrance_height - 2, materials)
        for z in range(-1, 4):
            _add_block(blocks, entrance_x1 - 4, 1, z, materials["wood"])
            _add_block(blocks, entrance_x2 + 4, 1, z, materials["wood"])

    if "entrada_ampliada" in extension_set:
        for z in range(-2, tunnel_z2 + 2):
            for x in range(entrance_x1 - 1, entrance_x2 + 2):
                for y in range(1, entrance_height + 2):
                    _remove_block(blocks, x, y, z)
                    if y == 1:
                        _add_block(blocks, x, y, z, materials["tunnel_floor"])
            for y in range(1, entrance_height + 3):
                _add_block(blocks, entrance_x1 - 2, y, z, materials["rock"])
                _add_block(blocks, entrance_x2 + 2, y, z, materials["rock"])
            for x in range(entrance_x1 - 2, entrance_x2 + 3):
                _add_block(blocks, x, entrance_height + 2, z, materials["rock"])
        _add_mine_support_frame(blocks, state_overrides, entrance_x1 - 1, entrance_x2 + 1, -3, entrance_height + 1, materials)
        _add_vertical_line(blocks, entrance_x1 - 2, 0, 1, entrance_height + 1, materials["trim"])
        _add_vertical_line(blocks, entrance_x2 + 2, 0, 1, entrance_height + 1, materials["trim"])
        _add_block(blocks, entrance_x1 - 2, 2, 1, materials["bars"])
        _add_block(blocks, entrance_x2 + 2, 2, 1, materials["bars"])
        _add_block(blocks, entrance_x1 - 3, 2, -1, materials["glass"])
        _add_block(blocks, entrance_x2 + 3, 2, -1, materials["glass"])
        for x in range(entrance_x1 - 2, entrance_x2 + 3):
            _add_block(blocks, x, entrance_height + 2, -1, materials["slab"])
            state_overrides[(x, entrance_height + 2, -1)] = {"type": "bottom"}
        _add_mine_rail_run(blocks, center_x + 1, -3, tunnel_z2 + 1, materials)
        _add_mine_railing(blocks, entrance_x1 - 2, entrance_x1 + 1, -4, materials)
        _add_mine_railing(blocks, entrance_x2 - 1, entrance_x2 + 2, -4, materials)
        _add_block(blocks, entrance_x1 - 2, 2, -4, materials["light"])
        _add_block(blocks, entrance_x2 + 2, 2, -4, materials["light"])
        for x in range(entrance_x1 - 1, entrance_x2 + 2):
            _add_block(blocks, x, 0, -4, materials["path"])

    if "decoracion_extra" in extension_set:
        _add_block(blocks, entrance_x1 - 3, 1, 0, materials["barrel"])
        _add_block(blocks, entrance_x2 + 3, 1, 0, materials["barrel"])
        _add_block(blocks, entrance_x1 - 3, 1, -2, materials["leaf"])
        _add_block(blocks, entrance_x1 - 3, 2, -2, materials["leaf"])
        _add_block(blocks, entrance_x2 + 3, 1, -2, materials["leaf"])
        _add_block(blocks, entrance_x2 + 3, 2, -2, materials["leaf"])
        _add_block(blocks, center_x - 4, 1, -5, materials["light"])
        _add_block(blocks, center_x + 4, 1, -5, materials["light"])
        _add_block(blocks, center_x - 5, 1, -3, materials["barrel"])
        _add_block(blocks, center_x + 5, 1, -3, materials["barrel"])
        _add_mine_railing(blocks, center_x - 5, center_x - 3, -6, materials)
        _add_mine_railing(blocks, center_x + 3, center_x + 5, -6, materials)

    return blocks, state_overrides


def _generate_modern_house(
    width: int,
    depth: int,
    height: int,
    materials: dict[str, str],
    size: str,
    selected_extensions: list[str],
) -> tuple[dict[tuple[int, int, int], str], dict[Position, dict[str, str | bool]]]:
    blocks: dict[tuple[int, int, int], str] = {}
    state_overrides: dict[Position, dict[str, str | bool]] = {}
    extension_set = set(selected_extensions)
    has_pool = "piscina" in extension_set
    has_terrace = "terraza" in extension_set
    has_garage = "garaje" in extension_set
    has_garden = "jardin" in extension_set
    has_decor = "decoracion_extra" in extension_set

    if size == "small":
        ground_height = 4
        upper_height = 3
        pool_width = 3
        pool_depth = 2
        upper_offset_x = 4
        upper_offset_z = 1
        upper_width = width - 5
        upper_depth = depth - 3
    elif size == "large":
        ground_height = 6
        upper_height = 5
        pool_width = 5
        pool_depth = 3
        upper_offset_x = 5
        upper_offset_z = 1
        upper_width = width - 6
        upper_depth = depth - 4
    else:
        ground_height = 5
        upper_height = 4
        pool_width = 4
        pool_depth = 2
        upper_offset_x = 4
        upper_offset_z = 1
        upper_width = width - 5
        upper_depth = depth - 3

    x1, z1 = 0, 0
    x2, z2 = width - 1, depth - 1

    _add_modern_box_shell(blocks, x1, x2, z1, z2, 0, ground_height, materials)

    upper_x1 = upper_offset_x
    upper_x2 = min(x2, upper_x1 + upper_width - 1)
    upper_z1 = upper_offset_z
    upper_z2 = min(z2 - 1, upper_z1 + upper_depth - 1)
    upper_floor_y = ground_height + 1
    upper_top_y = upper_floor_y + upper_height
    _add_modern_box_shell(blocks, upper_x1, upper_x2, upper_z1, upper_z2, upper_floor_y, upper_top_y, materials)

    balcony_x1 = x1 + 1
    balcony_x2 = upper_x1 + 1
    balcony_z1 = z1 - 1
    balcony_z2 = z1 + 2
    _fill_rect(blocks, balcony_x1, balcony_x2, balcony_z1, balcony_z2, upper_floor_y, materials["terrace"])

    side_cube_x1 = x2 - max(3, width // 4)
    side_cube_z1 = z1 + 2
    side_cube_z2 = z1 + min(5, depth - 3)
    side_cube_floor_y = upper_floor_y
    side_cube_top_y = upper_top_y - 1
    _add_modern_box_shell(blocks, side_cube_x1, x2, side_cube_z1, side_cube_z2, side_cube_floor_y, side_cube_top_y, materials)

    _add_modern_flat_roof(blocks, state_overrides, x1, x2, z1, z2, ground_height + 1, materials)
    _add_modern_flat_roof(blocks, state_overrides, upper_x1, upper_x2, upper_z1, upper_z2, upper_top_y + 1, materials)
    _add_modern_flat_roof(blocks, state_overrides, side_cube_x1, x2, side_cube_z1, side_cube_z2, side_cube_top_y + 1, materials)

    door_x = x2 - 2
    for y in (1, 2):
        _add_block(blocks, door_x, y, z1, materials["door"])
    state_overrides[(door_x, 1, z1)] = {"facing": "south", "half": "lower", "hinge": "left", "open": False}
    state_overrides[(door_x, 2, z1)] = {"facing": "south", "half": "upper", "hinge": "left", "open": False}

    _add_modern_glass_panel(blocks, x1 + 1, x1 + max(3, width // 3), 1, ground_height - 1, z1, materials)
    _add_modern_glass_panel(blocks, upper_x1 + 1, upper_x2 - 1, upper_floor_y + 1, upper_top_y - 1, z1, materials)
    _add_modern_side_glass_panel(blocks, x2, z1 + 2, z1 + max(4, depth // 2), 2, ground_height - 1, materials)
    _add_modern_side_glass_panel(blocks, upper_x2, upper_z1 + 1, upper_z2 - 1, upper_floor_y + 1, upper_top_y - 1, materials)

    wood_band_y = ground_height
    for x in range(x1 + 1, x2 - 1):
        _add_block(blocks, x, wood_band_y, z1 + 1, materials["accent_wood"])
    for x in range(upper_x1 + 1, upper_x2):
        _add_block(blocks, x, upper_floor_y + 1, z1, materials["accent_wood"])
    for z in range(z1 + 1, z2 - 1):
        _add_block(blocks, upper_x1 - 1, upper_floor_y + 1, z, materials["trim"])
    for z in range(side_cube_z1 + 1, side_cube_z2):
        _add_block(blocks, side_cube_x1, upper_floor_y + 1, z, materials["accent_wood"])

    stair_base_z = z1 + 1
    stair_x = upper_x1 - 1
    for step in range(ground_height):
        z = stair_base_z + step
        y = 1 + step
        _add_block(blocks, stair_x, y, z, materials["stairs"])
        state_overrides[(stair_x, y, z)] = {
            "facing": "south",
            "half": "bottom",
            "shape": "straight",
        }
        _add_block(blocks, stair_x + 1, y, z, materials["stairs"])
        state_overrides[(stair_x + 1, y, z)] = {
            "facing": "south",
            "half": "bottom",
            "shape": "straight",
        }

    pool_x1 = x1 + 1
    pool_x2 = min(x2 - 3, pool_x1 + pool_width)
    pool_z1 = -pool_depth - 1
    pool_z2 = -1
    _fill_rect(blocks, pool_x1 - 1, pool_x2 + 1, pool_z1 - 1, pool_z2 + 1, 0, materials["pool_border"])
    _fill_rect(blocks, pool_x1, pool_x2, pool_z1, pool_z2, 0, materials["pool_water"])

    for x in range(pool_x1 - 1, pool_x2 + 2):
        _add_block(blocks, x, 1, pool_z1 - 1, materials["trim"])
        _add_block(blocks, x, 1, pool_z2 + 1, materials["trim"])
    for z in range(pool_z1, pool_z2 + 1):
        _add_block(blocks, pool_x1 - 1, 1, z, materials["trim"])
        _add_block(blocks, pool_x2 + 1, 1, z, materials["trim"])

    if has_terrace:
        _add_modern_terrace_extension(blocks, upper_x1, upper_x2, upper_z1, upper_z2, upper_top_y, materials)
    if has_pool:
        _add_modern_pool_extension(blocks, pool_x1, pool_x2, pool_z1, pool_z2, materials)
    if has_garage:
        _add_modern_garage_extension(blocks, x1, z1, z2, ground_height, materials)
    if has_garden:
        _add_modern_garden_extension(blocks, x1, x2, z1, z2, pool_z1, materials)
    if has_decor:
        _add_modern_extra_decor(blocks, upper_x1, upper_x2, z1, z2, ground_height, materials)

    return blocks, state_overrides


def _generate_house(
    width: int,
    depth: int,
    height: int,
    materials: dict[str, str],
    features: list[str],
    size: str,
    selected_extensions: list[str],
) -> tuple[dict[tuple[int, int, int], str], dict[Position, dict[str, str | bool]]]:
    blocks: dict[tuple[int, int, int], str] = {}
    state_overrides: dict[Position, dict[str, str | bool]] = {}
    x1, z1 = 0, 0
    x2, z2 = width - 1, depth - 1
    size_profile = _build_size_profile(size, features)
    wall_height = int(size_profile["wall_height"])
    overhang = 1
    extension_set = set(selected_extensions)
    has_garden = "jardin" in extension_set or "con_jardin" in features
    has_decor = "decoracion_extra" in extension_set or "decorada" in features
    has_porche = "porche" in extension_set
    has_stable = "establo" in extension_set

    upper_x1, upper_x2, upper_z1, upper_z2 = _add_house_shell(
        blocks,
        x1,
        x2,
        z1,
        z2,
        0,
        wall_height,
        materials,
        overhang,
    )

    _fill_rect(blocks, upper_x1 + 1, upper_x2 - 1, upper_z1 + 1, upper_z2 - 1, 3, materials["porch_planks"])
    porch_x1, porch_x2, porch_front_z = _add_reference_front_porch(
        blocks,
        state_overrides,
        upper_x1,
        upper_x2,
        upper_z1,
        materials,
        size_profile,
        add_decor=has_decor,
    )
    if has_porche:
        _add_porch_extension(blocks, state_overrides, porch_x1, porch_x2, porch_front_z, materials)
    _add_reference_front_facade(blocks, state_overrides, upper_x1, upper_x2, upper_z1, materials)
    _add_reference_side_windows(blocks, upper_x1, upper_x2, upper_z1, upper_z2, materials, size_profile)
    _add_reference_side_annex(
        blocks,
        state_overrides,
        upper_x2,
        upper_z1,
        upper_z2,
        materials,
        size_profile,
        add_decor=has_decor,
    )
    _add_gabled_roof(blocks, state_overrides, upper_x1, upper_x2, upper_z1, upper_z2, wall_height + 4, materials)
    _fill_gable_faces(blocks, state_overrides, upper_x1, upper_x2, upper_z1, upper_z2, wall_height, materials)
    _add_reference_roof_details(
        blocks,
        state_overrides,
        upper_x1,
        upper_x2,
        upper_z1,
        upper_z2,
        wall_height + 4,
        materials,
        size_profile,
    )
    _add_chimney(
        blocks,
        upper_x2 - 1,
        upper_z1 + 2,
        wall_height + 5,
        int(size_profile["chimney_height"]),
        materials,
    )
    if has_stable:
        _add_stable_extension(blocks, state_overrides, upper_x1, upper_z1, upper_z2, materials, size_profile)
    if has_decor:
        _add_reference_ground_details(blocks, upper_x1, upper_x2, upper_z1, upper_z2, materials)

    garden_min_x = upper_x1 - 5
    garden_max_x = upper_x2 + 7
    garden_min_z = upper_z1 - 8
    garden_max_z = upper_z2 + 3
    if has_garden:
        _add_small_garden(blocks, garden_min_x, garden_max_x, garden_min_z, garden_max_z, materials)
        _add_path_and_lanterns(blocks, (upper_x1 + upper_x2) // 2, upper_z1 - 3, garden_min_z, materials)
        _add_greenery(blocks, upper_x1, upper_x2, upper_z1, upper_z2, materials)
        _add_small_tree(blocks, garden_min_x + 3, upper_z1 - 3, materials)
        _add_small_tree(blocks, garden_max_x - 2, upper_z2 + 1, materials)
    if has_decor:
        _add_block(blocks, upper_x1 + 1, 5, upper_z2 - 1, materials["accent"])
        _add_block(blocks, upper_x2 - 1, 5, upper_z2 - 1, materials["accent"])
    return blocks, state_overrides


def _infer_stair_facing(position: Position, block_map: dict[Position, str]) -> str:
    x, y, z = position
    block = block_map[position]
    same_west = block_map.get((x - 1, y, z)) == block
    same_east = block_map.get((x + 1, y, z)) == block
    same_north = block_map.get((x, y, z - 1)) == block
    same_south = block_map.get((x, y, z + 1)) == block

    east_higher = block_map.get((x + 1, y + 1, z)) == block
    west_higher = block_map.get((x - 1, y + 1, z)) == block
    east_lower = block_map.get((x + 1, y - 1, z)) == block
    west_lower = block_map.get((x - 1, y - 1, z)) == block
    south_higher = block_map.get((x, y + 1, z + 1)) == block
    north_higher = block_map.get((x, y + 1, z - 1)) == block
    south_lower = block_map.get((x, y - 1, z + 1)) == block
    north_lower = block_map.get((x, y - 1, z - 1)) == block

    if east_higher or west_lower:
        return "west"
    if west_higher or east_lower:
        return "east"
    if south_higher or north_lower:
        return "north"
    if north_higher or south_lower:
        return "south"

    if same_east and not same_west:
        return "west"
    if same_west and not same_east:
        return "east"
    if same_south and not same_north:
        return "north"
    if same_north and not same_south:
        return "south"

    if _is_connectable(block_map.get((x, y, z + 1))) and not _is_connectable(block_map.get((x, y, z - 1))):
        return "north"
    if _is_connectable(block_map.get((x, y, z - 1))) and not _is_connectable(block_map.get((x, y, z + 1))):
        return "south"
    if _is_connectable(block_map.get((x + 1, y, z))) and not _is_connectable(block_map.get((x - 1, y, z))):
        return "west"
    if _is_connectable(block_map.get((x - 1, y, z))) and not _is_connectable(block_map.get((x + 1, y, z))):
        return "east"
    return "north"


def _infer_stair_shape(position: Position, facing: str, block_map: dict[Position, str]) -> str:
    left_by_facing = {"north": "west", "east": "north", "south": "east", "west": "south"}
    right_by_facing = {"north": "east", "east": "south", "south": "west", "west": "north"}
    block = block_map[position]
    left_neighbor = _neighbor(position, left_by_facing[facing])
    right_neighbor = _neighbor(position, right_by_facing[facing])

    if block_map.get(left_neighbor) == block:
        return "outer_left"
    if block_map.get(right_neighbor) == block:
        return "outer_right"
    return "straight"


def _infer_slab_type(position: Position, block_map: dict[Position, str]) -> str:
    x, y, z = position
    if block_map.get((x, y + 1, z)) == block_map[position] or block_map.get((x, y - 1, z)) == block_map[position]:
        return "double"

    below = block_map.get((x, y - 1, z))
    above = block_map.get((x, y + 1, z))
    if _is_connectable(below) and not _is_connectable(above):
        return "bottom"
    if _is_connectable(above) and not _is_connectable(below):
        return "top"
    return "bottom"


def _infer_connections(position: Position, block_map: dict[Position, str]) -> dict[str, bool]:
    return {
        direction: _is_connectable(block_map.get(_neighbor(position, direction)))
        for direction in HORIZONTAL_DIRECTIONS
    }


def _infer_door_state(position: Position, block_map: dict[Position, str]) -> dict[str, str | bool]:
    x, y, z = position
    upper = block_map.get((x, y + 1, z)) == block_map[position]
    lower = block_map.get((x, y - 1, z)) == block_map[position]

    if lower and not upper:
        return {"facing": "south", "half": "upper", "hinge": "left", "open": False}
    return {"facing": "south", "half": "lower", "hinge": "left", "open": False}


def _infer_trapdoor_state(position: Position, block_map: dict[Position, str]) -> dict[str, str | bool]:
    x, y, z = position
    if block_map.get((x + 1, y, z)) == "glass_pane":
        facing = "west"
    elif block_map.get((x - 1, y, z)) == "glass_pane":
        facing = "east"
    elif block_map.get((x, y, z + 1)) == "glass_pane":
        facing = "north"
    else:
        facing = "south"
    return {"facing": facing, "half": "top", "open": True}


def _infer_log_axis(position: Position, block_map: dict[Position, str]) -> str:
    x, y, z = position
    block = block_map[position]
    if block_map.get((x + 1, y, z)) == block or block_map.get((x - 1, y, z)) == block:
        return "x"
    if block_map.get((x, y, z + 1)) == block or block_map.get((x, y, z - 1)) == block:
        return "z"
    return "y"


def _infer_rail_shape(position: Position, block_map: dict[Position, str]) -> str:
    x, y, z = position
    rail_blocks = {"rail", "powered_rail", "detector_rail", "activator_rail"}
    east = block_map.get((x + 1, y, z)) in rail_blocks
    west = block_map.get((x - 1, y, z)) in rail_blocks
    north = block_map.get((x, y, z - 1)) in rail_blocks
    south = block_map.get((x, y, z + 1)) in rail_blocks
    if east or west:
        return "east_west"
    if north or south:
        return "north_south"
    return "north_south"


def _build_block_states(block_map: dict[Position, str]) -> dict[Position, dict[str, str | bool]]:
    states: dict[Position, dict[str, str | bool]] = {}

    for position, block in block_map.items():
        if block.endswith("_stairs"):
            facing = _infer_stair_facing(position, block_map)
            states[position] = {
                "facing": facing,
                "half": "bottom",
                "shape": _infer_stair_shape(position, facing, block_map),
            }
        elif block.endswith("_slab"):
            states[position] = {"type": _infer_slab_type(position, block_map)}
        elif block.endswith("_fence"):
            states[position] = _infer_connections(position, block_map)
        elif block.endswith("_wall"):
            wall_state = _infer_connections(position, block_map)
            wall_state["up"] = not any(wall_state.values())
            states[position] = wall_state
        elif block.endswith("_pane") or block == "iron_bars":
            states[position] = _infer_connections(position, block_map)
        elif block.endswith("_door"):
            states[position] = _infer_door_state(position, block_map)
        elif block.endswith("_trapdoor"):
            states[position] = _infer_trapdoor_state(position, block_map)
        elif block.endswith("_log"):
            states[position] = {"axis": _infer_log_axis(position, block_map)}
        elif block in {"rail", "powered_rail", "detector_rail", "activator_rail"}:
            states[position] = {"shape": _infer_rail_shape(position, block_map)}
        elif block == "campfire":
            states[position] = {"lit": True, "signal_fire": True}

    return states


def generate_build(
    template_id: str,
    prompt: str,
    size: str,
    main_material: str | None = None,
    secondary_materials: list[str] | None = None,
    extensions: list[str] | None = None,
) -> BuildGenerateResponse:
    template = _find_template(template_id)
    prompt_used = _resolve_prompt_for_size(template, size, prompt)
    features = _parse_features(prompt_used)
    selected_extensions = _normalize_extension_selection(template, extensions)
    selected_main_material, selected_secondary_materials = _normalize_material_selection(
        template,
        main_material,
        secondary_materials,
    )
    width, depth, height = _resolve_dimensions(template, size, features)
    if template["id"] == "casa_moderna":
        materials = _resolve_modern_materials(template, selected_main_material, selected_secondary_materials)
        block_map, state_overrides = _generate_modern_house(
            width,
            depth,
            height,
            materials,
            size,
            selected_extensions,
        )
    elif template["id"] == "entrada_mina":
        materials = _resolve_mine_materials(template, selected_main_material, selected_secondary_materials)
        block_map, state_overrides = _generate_mine_entrance(
            width,
            depth,
            height,
            materials,
            size,
            selected_extensions,
        )
    elif template["id"] == "granja":
        materials = _resolve_farm_materials(template, selected_main_material, selected_secondary_materials)
        block_map, state_overrides = _generate_farm(
            width,
            depth,
            height,
            materials,
            size,
            selected_extensions,
        )
    elif template["id"] == "castillo":
        materials = _resolve_castle_materials(template, selected_main_material, selected_secondary_materials)
        block_map, state_overrides = _generate_castle(
            width,
            depth,
            height,
            materials,
            size,
            selected_extensions,
        )
    else:
        materials = _resolve_materials(template, features, selected_main_material, selected_secondary_materials)
        block_map, state_overrides = _generate_house(
            width,
            depth,
            height,
            materials,
            features,
            size,
            selected_extensions,
        )
    block_states = _build_block_states(block_map)
    for position, override_state in state_overrides.items():
        if position not in block_map:
            continue
        block_name = block_map[position]
        if "facing" in override_state and not (block_name.endswith("_stairs") or block_name.endswith("_door")):
            continue
        if "type" in override_state and not block_name.endswith("_slab"):
            continue
        if position in block_map:
            block_states[position] = override_state

    blocks = [
        BlockPlacement(x=x, y=y, z=z, block=block, state=block_states.get((x, y, z), {}))
        for (x, y, z), block in sorted(
            block_map.items(),
            key=lambda item: (item[0][1], item[0][0], item[0][2]),
        )
    ]

    metadata = BuildMetadata(
        template_id=template["id"],
        template_label=template["label"],
        category=template["category"],
        size=size,
        selected_main_material=selected_main_material,
        selected_secondary_materials=selected_secondary_materials,
        selected_extensions=selected_extensions,
        prompt_used=prompt_used,
        width=width,
        depth=depth,
        height=height,
        applied_features=features,
        materials=materials,
        block_count=len(blocks),
    )
    return BuildGenerateResponse(metadata=metadata, blocks=blocks)
