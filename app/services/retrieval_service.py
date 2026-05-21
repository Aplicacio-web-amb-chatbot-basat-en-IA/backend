import re
import unicodedata
from math import sqrt

from sqlalchemy.orm import Session

from app.database.models import DocumentChunk
from app.services.embedding_service import deserialize_embedding, generate_embedding


SIMILARITY_THRESHOLD = 0.25
INITIAL_RETRIEVAL_LIMIT = 15
INITIAL_KEYWORD_LIMIT = 15
MAX_RESPONSE_SENTENCES = 3
MAX_RESPONSE_CHARS = 420
LLM_CONTEXT_LIMIT = 5
QUESTION_HEADING_PREFIXES = (
    "como ",
    "que ",
    "por que ",
    "cuando ",
    "cual ",
    "para que ",
)


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return " ".join(text.split())


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    norm_a = sqrt(sum(a * a for a in vector_a))
    norm_b = sqrt(sum(b * b for b in vector_b))

    if not norm_a or not norm_b:
        return 0.0

    return dot_product / (norm_a * norm_b)


def detect_question_type(message: str) -> str:
    text = normalize_text(message)

    if text.startswith(("que es ", "quien es ", "que son ", "quienes son ")):
        return "definition"
    if text.startswith(
        (
            "que encantamientos puede tener ",
            "que encantamientos puede llevar ",
            "que encantamientos admite ",
            "que encantamientos tiene ",
            "que encantamientos lleva ",
            "que encantamiento puede tener ",
            "que encantamiento puede llevar ",
            "que encantamientos se le pueden poner a ",
            "que encantamientos se le pueden poner al ",
            "cuales son los encantamientos de ",
        )
    ):
        return "item_enchantments"
    if text.startswith(("que mobs aparecen en ", "que criaturas aparecen en ", "que enemigos aparecen en ")):
        return "location"
    if text.startswith(
        (
            "que materiales necesito para hacer ",
            "que materiales hacen falta para hacer ",
            "que necesito para ",
            "que hace falta para ",
            "que necesito ",
        )
    ):
        return "requirements"
    if text.startswith("como se hace una puerta "):
        if any(term in text for term in ("redstone", "2x2", "automatica", "automatica", "pistones")):
            return "build"
        return "recipe"
    if text.startswith(
        (
            "como se construye ",
            "como se hace un portal ",
            "como hacer una granja ",
            "como se hace una granja ",
            "como se crea una granja ",
            "como puedo hacer una granja ",
            "como puedo hacer una trampa ",
            "como hacer una trampa ",
            "como se hace una trampa ",
            "como puedo organizar automaticamente ",
            "como puedo construir ",
            "como disenar ",
        )
    ):
        return "build"
    if text.startswith(
        (
            "como se hace ",
            "como se fabrica ",
            "como se craftea ",
            "como se crea una pocion ",
        )
    ):
        return "recipe"
    if text.startswith(
        (
            "como se domestica ",
            "como domesticar ",
            "como puedo domesticar ",
            "que animales se pueden domesticar",
        )
    ):
        return "tame"
    if text.startswith(
        (
            "como matar ",
            "como derrotar ",
            "como vencer ",
            "como puedo matar ",
            "como puedo derrotar ",
            "como puedo vencer ",
        )
    ):
        return "combat"
    if text.startswith(
        (
            "cual es la mejor estrategia para ",
            "que estrategia usar para ",
            "como explorar ",
            "como puedo sobrevivir mejor en ",
            "como sobrevivir mejor en ",
            "como me preparo para ",
            "como prepararme para ",
            "como evito ",
        )
    ):
        return "strategy"
    if "diferencia entre" in text or "que diferencia hay entre" in text:
        return "comparison"
    if text.startswith(
        (
            "como funciona ",
            "como funcionan ",
            "como puedo mover ",
            "como se usa ",
            "como usar ",
            "como se puede dormir ",
            "como dormir ",
            "como se duerme ",
        )
    ):
        return "mechanic"
    if text.startswith(
        (
            "que utilidad tiene ",
            "que utilidad tienen ",
            "para que sirve ",
            "para que sirven ",
            "que aporta ",
            "que hace un ",
            "que hace una ",
            "que hace ",
        )
    ):
        return "purpose"
    if text.startswith(
        (
            "donde esta ",
            "donde aparece ",
            "donde encontrar ",
            "donde consigo ",
            "donde se encuentra ",
        )
    ):
        return "location"
    if text.startswith(("cuando aparece ", "cuando se puede ", "cuando conviene ")):
        return "timing"
    if text.startswith(
        (
            "cual es el mejor ",
            "cual es la mejor ",
            "que es mejor ",
            "que encantamiento es mejor para ",
            "que encantamientos son mejores para ",
            "cuales son los mejores encantamientos para ",
            "cual es el mejor encantamiento para ",
        )
    ):
        return "best_choice"
    if text.startswith(("como reparo ", "como reparar ", "como se reparan ")):
        return "repair"
    if text.startswith(
        (
            "como consigo ",
            "como se consigue ",
            "como obtener ",
            "como se obtiene ",
            "como puedo llegar al ",
            "como encuentro ",
            "como encontrar ",
            "como puedo encontrar ",
            "donde encuentro ",
            "donde puedo encontrar ",
            "como puedo conseguir ",
            "como conseguir ",
        )
    ):
        return "obtain"
    if text.startswith(("se puede ", "puedo ", "es posible ")):
        return "possibility"
    return "general"


def extract_focus_term(message: str, question_type: str) -> str:
    text = normalize_text(message).strip(" ?¿!")
    prefixes = {
        "definition": [
            "que es un ",
            "que es una ",
            "que es ",
            "quien es un ",
            "quien es una ",
            "quien es ",
            "que son ",
            "quienes son ",
        ],
        "item_enchantments": [
            "que encantamientos puede tener un ",
            "que encantamientos puede tener una ",
            "que encantamientos puede tener ",
            "que encantamientos puede llevar un ",
            "que encantamientos puede llevar una ",
            "que encantamientos puede llevar ",
            "que encantamientos admite un ",
            "que encantamientos admite una ",
            "que encantamientos admite ",
            "que encantamientos tiene un ",
            "que encantamientos tiene una ",
            "que encantamientos tiene ",
            "que encantamientos lleva un ",
            "que encantamientos lleva una ",
            "que encantamientos lleva ",
            "que encantamiento puede tener un ",
            "que encantamiento puede tener una ",
            "que encantamiento puede tener ",
            "que encantamiento puede llevar un ",
            "que encantamiento puede llevar una ",
            "que encantamiento puede llevar ",
            "que encantamientos se le pueden poner a un ",
            "que encantamientos se le pueden poner a una ",
            "que encantamientos se le pueden poner a ",
            "que encantamientos se le pueden poner al ",
            "cuales son los encantamientos de un ",
            "cuales son los encantamientos de una ",
            "cuales son los encantamientos de ",
        ],
        "requirements": [
            "que materiales necesito para hacer ",
            "que materiales hacen falta para hacer ",
            "que necesito para ",
            "que hace falta para ",
            "que necesito ",
        ],
        "build": [
            "como se construye un ",
            "como se construye una ",
            "como se construye ",
            "como se hace un portal ",
            "como se hace una puerta ",
            "como hacer una granja de ",
            "como hacer una granja ",
            "como se hace una granja de ",
            "como se hace una granja ",
            "como se crea una granja de ",
            "como se crea una granja ",
            "como puedo hacer una granja de ",
            "como puedo hacer una granja ",
            "como puedo hacer una trampa de ",
            "como puedo hacer una trampa ",
            "como hacer una trampa de ",
            "como hacer una trampa ",
            "como se hace una trampa de ",
            "como se hace una trampa ",
            "como puedo organizar automaticamente ",
            "como puedo construir un ",
            "como puedo construir una ",
            "como puedo construir ",
            "como disenar un ",
            "como disenar una ",
            "como disenar ",
        ],
        "recipe": [
            "como se hace un ",
            "como se hace una ",
            "como se hace ",
            "como se fabrica un ",
            "como se fabrica una ",
            "como se fabrica ",
            "como se craftea un ",
            "como se craftea una ",
            "como se craftea ",
            "como se crea una pocion de ",
            "como se crea una pocion ",
            "como creo ",
            "como se crea",
        ],
        "purpose": [
            "que utilidad tiene ",
            "que utilidad tienen ",
            "para que sirve un ",
            "para que sirve una ",
            "para que sirve ",
            "para que sirven ",
            "que aporta ",
            "que hace un ",
            "que hace una ",
            "que hace ",
        ],
        "mechanic": [
            "como puedo mover ",
            "como funciona un ",
            "como funciona una ",
            "como funciona ",
            "como funcionan los ",
            "como funcionan las ",
            "como funcionan ",
            "como se usa un ",
            "como se usa una ",
            "como se usa ",
            "como usar un ",
            "como usar una ",
            "como usar ",
            "como se puede dormir en ",
            "como se puede dormir ",
            "como dormir en ",
            "como dormir ",
            "como se duerme en ",
            "como se duerme ",
        ],
        "tame": [
            "que animales se pueden domesticar",
            "como se domestica un ",
            "como se domestica una ",
            "como se domestica ",
            "como domesticar un ",
            "como domesticar una ",
            "como domesticar ",
            "como puedo domesticar un ",
            "como puedo domesticar una ",
            "como puedo domesticar ",
        ],
        "combat": [
            "como matar a ",
            "como matar ",
            "como derrotar a ",
            "como derrotar ",
            "como vencer a ",
            "como vencer ",
            "como puedo matar a ",
            "como puedo matar ",
            "como puedo derrotar a ",
            "como puedo derrotar ",
            "como puedo vencer a ",
            "como puedo vencer ",
        ],
        "strategy": [
            "cual es la mejor estrategia para ",
            "que estrategia usar para ",
            "como explorar ",
            "como puedo sobrevivir mejor en ",
            "como sobrevivir mejor en ",
            "como me preparo para ",
            "como prepararme para ",
            "como evito ",
        ],
        "repair": [
            "como reparo ",
            "como reparar ",
            "como se reparan ",
        ],
        "obtain": [
            "como consigo ",
            "como se consigue ",
            "como obtener ",
            "como se obtiene ",
            "como puedo llegar al ",
            "como encuentro ",
            "como encontrar ",
            "como puedo conseguir ",
            "como puedo encontrar ",
            "como conseguir ",
            "donde encuentro ",
            "donde puedo encontrar ",
        ],
        "location": [
            "donde esta ",
            "donde aparece ",
            "donde encontrar ",
            "donde consigo ",
            "donde se encuentra ",
        ],
        "timing": [
            "cuando aparece ",
            "cuando se puede ",
            "cuando conviene ",
        ],
        "best_choice": [
            "cual es el mejor ",
            "cual es la mejor ",
            "que es mejor ",
            "que encantamiento es mejor para ",
            "que encantamientos son mejores para ",
            "cuales son los mejores encantamientos para ",
            "cual es el mejor encantamiento para ",
        ],
        "possibility": [
            "se puede ",
            "puedo ",
            "es posible ",
        ],
    }

    for prefix in prefixes.get(question_type, []):
        if text.startswith(prefix):
            return text[len(prefix):].strip(" ?¿!")

    if question_type == "comparison":
        normalized_text = text.replace("que diferencia hay entre ", "")
        normalized_text = normalized_text.replace("diferencia entre ", "")
        return normalized_text.strip(" ?¿!")

    return text


def extract_focus_tokens(focus: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+", focus)
    stopwords = {
        "un",
        "una",
        "unos",
        "unas",
        "el",
        "la",
        "los",
        "las",
        "de",
        "del",
        "y",
        "o",
        "en",
        "con",
        "para",
        "por",
        "al",
        "minecraft",
        "como",
        "funciona",
        "funcionan",
        "hace",
        "hacer",
        "fabrica",
        "craftea",
        "sirve",
        "sirven",
        "diferencia",
        "entre",
        "consigo",
        "obtener",
        "encuentro",
        "encontrar",
        "puedo",
        "domestica",
        "domesticar",
        "necesito",
        "falta",
        "mejor",
        "mejores",
        "estrategia",
        "donde",
        "cuando",
        "usar",
        "puede",
        "posible",
        "son",
        "reparo",
        "reparar",
        "sobrevivir",
        "preparo",
        "prepararme",
        "pelear",
        "contra",
    }
    return [token for token in tokens if token not in stopwords and len(token) > 1]


def extract_question_keywords(message: str) -> list[str]:
    keywords = extract_focus_tokens(normalize_text(message))
    aliases = {
        "encantamientos": ["encantamiento", "enchanting", "enchantments"],
        "crafteo": ["crafting"],
        "craftear": ["crafting"],
        "craftea": ["crafting"],
        "faro": ["baliza", "beacon"],
        "baliza": ["faro", "beacon"],
        "mesa": ["table"],
        "lobo": ["wolf", "wolves"],
        "lobos": ["wolf", "wolves"],
        "domestica": ["domesticar", "domesticado", "taming", "tamed"],
        "domesticar": ["domestica", "domesticado", "taming", "tamed"],
        "antorcha": ["torch"],
        "spawn": ["aparicion", "spawning"],
        "hierro": ["iron"],
        "diamante": ["diamond", "diamantes"],
        "diamantes": ["diamond", "diamante"],
        "granja": ["farm", "farming"],
        "experiencia": ["xp", "experience"],
        "aldeano": ["villager", "villagers"],
        "aldeanos": ["villager", "villagers"],
        "intercambio": ["trade", "trades", "intercambios"],
        "intercambios": ["trade", "trades", "intercambio"],
        "trade": ["intercambio", "intercambios", "trades"],
        "trades": ["intercambio", "intercambios", "trade"],
        "esmeralda": ["emerald", "emeralds"],
        "esmeraldas": ["emerald", "emeralds"],
        "fortress": ["fortaleza"],
        "fortaleza": ["fortress"],
        "comparador": ["comparator", "comparadores"],
        "comparadores": ["comparator", "comparador"],
        "polvora": ["gunpowder"],
        "cama": ["bed", "beds"],
        "armadura": ["armor", "armaduras"],
        "encuentra": ["ubicacion", "aparece"],
        "donde": ["ubicacion", "aparece"],
        "encantamiento": ["encantamientos", "enchanting", "enchantments"],
        "ocean": ["oceano", "oceanica", "oceanicas", "oceanic"],
        "ruin": ["ruina", "ruinas"],
        "trial": ["prueba", "pruebas", "trial chamber", "trial chambers"],
        "chamber": ["camara", "camaras", "chambers"],
        "chambers": ["camara", "camaras", "trial"],
    }

    expanded_keywords = []
    for keyword in keywords:
        expanded_keywords.append(keyword)
        expanded_keywords.extend(aliases.get(keyword, []))

    unique_keywords = []
    for keyword in expanded_keywords:
        if keyword not in unique_keywords:
            unique_keywords.append(keyword)

    return unique_keywords


def has_specific_focus_match(
    text: str,
    focus_tokens: list[str],
    ignored_tokens: set[str] | None = None,
) -> bool:
    ignored = ignored_tokens or set()
    specific_tokens = [token for token in focus_tokens if token not in ignored]
    if not specific_tokens:
        return True
    return any(token in text for token in specific_tokens)


def count_focus_matches(text: str, focus_tokens: list[str]) -> int:
    return sum(1 for token in focus_tokens if token in text)


def find_keyword_candidates(
    chunks: list[DocumentChunk],
    focus: str,
    focus_tokens: list[str],
    question_keywords: list[str],
    question_type: str = "general",
    limit: int = INITIAL_KEYWORD_LIMIT,
) -> list[tuple[DocumentChunk, float]]:
    scored_chunks = []

    for chunk in chunks:
        content = normalize_text(chunk.content)
        title = normalize_text(chunk.title or "")
        source = normalize_text(chunk.source or "")
        combined_text = " ".join((content, title, source))
        score = 0.0

        if focus and focus in content:
            score += 1.0
        if focus and focus in title:
            score += 0.7
        if focus and focus in source:
            score += 0.5

        score += count_focus_matches(content, focus_tokens) * 0.18
        score += count_focus_matches(title, focus_tokens) * 0.14
        score += count_focus_matches(source, focus_tokens) * 0.10
        score += count_focus_matches(content, question_keywords) * 0.06
        score += count_focus_matches(title, question_keywords) * 0.05

        if question_type == "recipe":
            is_potion_recipe = "pocion" in focus_tokens
            if any(phrase in title for phrase in ("receta", "recetas", "crafteo", "crafting")):
                score += 0.75
            if any(phrase in source for phrase in ("receta", "recetas", "crafteo", "crafting")):
                score += 0.55
            if any(phrase in content for phrase in ("se fabrica con", "se hace con")):
                score += 0.65
            if is_potion_recipe and any(
                phrase in content for phrase in ("pocion de ", "awkward potion", "fermented spider eye", "golden carrot")
            ):
                score += 0.70
            if is_potion_recipe and "soporte para pociones" in content:
                score -= 1.10
            if is_potion_recipe and not has_specific_focus_match(
                combined_text,
                focus_tokens,
                {"pocion", "pociones"},
            ):
                score -= 0.85
            if any(phrase in content for phrase in ("sirve para", "restaura", "protege", "permite", "encantamiento")):
                score -= 0.25
        elif question_type == "repair":
            if any(phrase in title for phrase in ("reparacion", "repair", "mending")):
                score += 0.75
            if any(
                phrase in content
                for phrase in (
                    "se reparan",
                    "se puede reparar",
                    "yunque",
                    "mending",
                    "combinar dos herramientas",
                    "material correspondiente",
                )
            ):
                score += 0.65
            if any(phrase in content for phrase in ("cobre", "redstone", "fortaleza", "slime")):
                score -= 0.25
        elif question_type == "item_enchantments":
            if any(phrase in title for phrase in ("encantamientos", "encantamiento")):
                score += 0.80
            if any(phrase in source for phrase in ("encantamientos", "encantamiento")):
                score += 0.65
            if any(
                phrase in content
                for phrase in (
                    "puede llevar",
                    "puede tener",
                    "se le pueden poner",
                    "lista principal",
                    "curse of vanishing",
                    "mending",
                    "unbreaking",
                )
            ):
                score += 0.75
            if any(
                phrase in content
                for phrase in (
                    "mesa de encantamientos",
                    "libros pueden encantarse",
                    "niveles de experiencia",
                    "lapislazuli",
                    "yunque permite combinar",
                )
            ):
                score -= 0.35

        if score > 0:
            scored_chunks.append((chunk, score))

    scored_chunks.sort(
        key=lambda item: (item[1], -len(item[0].content)),
        reverse=True,
    )
    return scored_chunks[:limit]


def score_candidate(
    chunk: DocumentChunk,
    similarity: float,
    question_type: str,
    focus: str,
    focus_tokens: list[str],
) -> float:
    content = normalize_text(chunk.content)
    title = normalize_text(chunk.title or "")
    source = normalize_text(chunk.source or "")
    score = similarity

    if focus and focus in content:
        score += 0.35
    if focus and focus in title:
        score += 0.20

    content_matches = count_focus_matches(content, focus_tokens)
    title_matches = count_focus_matches(title, focus_tokens)

    score += content_matches * 0.08
    score += title_matches * 0.06

    if question_type == "definition":
        if focus and focus in title:
            score += 0.28
        if focus and focus in source:
            score += 0.20
        if any(phrase in (content + " " + title + " " + source) for phrase in ("estructura", "estructuras")):
            score += 0.16
        if any(phrase in content for phrase in ("es un ", "es una ", "son ", "criatura", "mob hostil", "mob neutral", "mob pasivo")):
            score += 0.18
        if any(phrase in content for phrase in ("suelen encontrarse en", "pueden encontrarse en")):
            score -= 0.18
        if any(phrase in content for phrase in ("sueltan", "drop", "sirve para fabricar", "se fabrica con")):
            score -= 0.12
        if any(phrase in title for phrase in ("especific", "comportamiento", "definicion", "mob")):
            score += 0.18
        if any(phrase in source for phrase in ("especific", "comportamiento", "definicion", "mob")):
            score += 0.12
        if any(phrase in title for phrase in ("granja", "farm", "estrategia", "funcionamiento")):
            score -= 0.20
        if "definicion" in title:
            score += 0.24
        if "redstone" in title:
            score -= 0.18

    elif question_type == "recipe":
        is_potion_recipe = "pocion" in focus_tokens
        if focus and f"{focus} se fabrica con" in content:
            score += 0.45
        if "se fabrica con" in content:
            score += 0.22
        if is_potion_recipe and any(
            phrase in content for phrase in ("pocion de ", "awkward potion", "fermented spider eye", "golden carrot")
        ):
            score += 0.36
        if is_potion_recipe and "soporte para pociones" in content:
            score -= 0.95
        if is_potion_recipe and not has_specific_focus_match(
            " ".join((content, title, source)),
            focus_tokens,
            {"pocion", "pociones"},
        ):
            score -= 0.60
        if any(phrase in title for phrase in ("receta", "recetas", "crafteo", "crafting")):
            score += 0.32
        if any(phrase in source for phrase in ("receta", "recetas", "crafteo", "crafting")):
            score += 0.22
        if focus and f"{focus} de " in content:
            score -= 0.14
        if any(phrase in content for phrase in ("sirve para", "drop", "sueltan", "aparecen", "restaura", "protege", "encantamiento", "mejora", "efecto")):
            score -= 0.16
        if "recetas de crafteo" in title or "recetas de crafteo" in source:
            score += 0.22
        if "mapa" in focus_tokens and "localizador" not in focus_tokens and "localizador" in title:
            score -= 0.35
        if "mapa" in focus_tokens and "localizador" not in focus_tokens and "localizador" in content:
            score -= 0.25
        if "localizador" in focus_tokens and "localizador" in title:
            score += 0.25

    elif question_type == "comparison":
        if any(phrase in content for phrase in ("diferencia", "mas", "menos", "mejor", "peor", "durabilidad", "dano")):
            score += 0.16

    elif question_type == "item_enchantments":
        if any(phrase in title for phrase in ("encantamientos", "encantamiento")):
            score += 0.28
        if any(phrase in source for phrase in ("encantamientos", "encantamiento")):
            score += 0.18
        if any(
            phrase in content
            for phrase in (
                "puede llevar",
                "puede tener",
                "se le pueden poner",
                "lista principal",
                "curse of vanishing",
                "unbreaking",
                "mending",
            )
        ):
            score += 0.34
        if any(
            phrase in content
            for phrase in (
                "mesa de encantamientos",
                "libros encantados",
                "lapislazuli",
                "niveles de experiencia",
                "yunque permite combinar",
            )
        ):
            score -= 0.30

    elif question_type == "mechanic":
        if any(phrase in content for phrase in ("funciona", "depende de", "se basa en", "requiere", "usa")):
            score += 0.14
        if any(phrase in content for phrase in ("de noche", "durante una tormenta", "cama", "overworld")):
            score += 0.10
        if any(token in ("enderman",) for token in focus_tokens):
            if any(phrase in content for phrase in ("se construye lejos", "controlar mejor el spawn", "caida", "camara de daño", "experiencia")):
                score += 0.22

    elif question_type == "repair":
        if any(
            phrase in content
            for phrase in (
                "se reparan",
                "yunque",
                "mending",
                "combinar dos",
                "material correspondiente",
                "barra de experiencia",
            )
        ):
            score += 0.24
        if any(phrase in content for phrase in ("cobre", "rayos", "redstone")):
            score -= 0.20

    elif question_type == "requirements":
        if any(phrase in content for phrase in ("necesita", "requiere", "hace falta", "se fabrica con", "para ")):
            score += 0.18
        if focus and focus in title and any(phrase in content for phrase in ("se fabrica con", "obsidiana", "diamantes", "libro")):
            score += 0.24

    elif question_type == "build":
        if any(phrase in content for phrase in ("se basa en", "necesita", "usa", "requiere", "tolvas", "agua", "aldeanos", "golems")):
            score += 0.18
        if any(phrase in content for phrase in ("es un ", "sirve para", "sueltan")):
            score -= 0.08
        if any(token in ("trampa", "trampas") for token in focus_tokens):
            if "trampa" in title or "trampa" in content:
                score += 0.26
            if any(phrase in content for phrase in ("clasificador", "cofres", "tolvas")) and "trampa" not in content:
                score -= 0.60
        if any(token in ("intercambio", "intercambios", "trade", "trades") for token in focus_tokens):
            if any(phrase in content for phrase in ("descuentos", "curar aldeanos zombie", "bibliotecarios", "bloque de trabajo", "primer intercambio", "ofertas")):
                score += 0.26

    elif question_type == "combat":
        if any(phrase in content for phrase in ("para derrotar", "para matar", "vulnerable", "armadura", "arco", "espada", "cristales", "pociones")):
            score += 0.18

    elif question_type == "strategy":
        if any(phrase in content for phrase in ("estrategia", "conviene", "priorizar", "seguridad", "riesgo", "preparacion")):
            score += 0.18
        if any(token in ("nether",) for token in focus_tokens):
            if any(phrase in title for phrase in ("supervivencia", "nether supervivencia")):
                score += 0.34
            if any(
                phrase in content
                for phrase in (
                    "resistencia al fuego",
                    "armadura de oro",
                    "hoglins",
                    "ghasts",
                    "bloques de cobertura",
                    "comida",
                    "cobertura",
                )
            ):
                score += 0.26
            if any(phrase in title for phrase in ("fortaleza", "fortalezas")) and not any(
                phrase in content for phrase in ("resistencia al fuego", "armadura de oro", "hoglins", "ghasts", "piglins")
            ):
                score -= 0.22
        if any(token in ("wither",) for token in focus_tokens):
            if any(
                phrase in content
                for phrase in (
                    "leche",
                    "regeneracion",
                    "resistencia",
                    "manzanas doradas",
                    "invocarlo",
                    "espacio controlado",
                    "armadura fuerte",
                )
            ):
                score += 0.28
            if any(phrase in content for phrase in ("ender dragon", "cristales")):
                score -= 0.30

    elif question_type == "purpose":
        if any(phrase in content for phrase in ("sirve para", "permite", "se usa para", "su funcion principal es", "se pueden fabricar", "imprescindible para fabricar")):
            score += 0.20
        if any(phrase in content for phrase in ("corresponde al", "profesion", "se fabrica con")):
            score -= 0.08
        if any(phrase in content for phrase in ("bloquea", "compara", "mide", "activa", "usa una señal")):
            score += 0.12

    elif question_type == "obtain":
        if any(phrase in content for phrase in ("se obtiene", "se consiguen", "se encuentra", "aparece en", "se obtiene al")):
            score += 0.16
        if any(phrase in content for phrase in ("fortaleza del nether", "stronghold", "aldeanos", "comerciando", "minando", "derrotar")):
            score += 0.10
        if any(token in ("esmeralda", "esmeraldas", "emerald", "emeralds") for token in focus_tokens):
            if any(phrase in content for phrase in ("comerciar con aldeanos", "granjeros", "flecheros", "bibliotecarios", "biomas de montaña")):
                score += 0.24
            if "recetas de crafteo" in title or "se fabrica con" in content:
                score -= 0.26
        if any(token in ("lapislazuli",) for token in focus_tokens):
            if any(phrase in content for phrase in ("minando", "mineral de lapislazuli", "pico de piedra", "capas subterraneas")):
                score += 0.26
            if any(phrase in title for phrase in ("encantamientos", "suministro")):
                score -= 0.18

    elif question_type == "location":
        if any(phrase in content for phrase in ("aparece en", "se encuentra en", "bioma", "overworld", "nether", "end", "fortaleza", "stronghold", "y -58", "y -59", "deepslate", "piedra profunda")):
            score += 0.24
        if "recetas de crafteo" in title or "se fabrica con" in content:
            score -= 0.20

    elif question_type == "timing":
        if any(phrase in content for phrase in ("de noche", "durante una tormenta", "al principio", "juego temprano", "nivel de luz", "cuando")):
            score += 0.16

    elif question_type == "best_choice":
        if any(phrase in content for phrase in ("mejor", "depende", "conviene", "prioridad", "mas util")):
            score += 0.18
        if any(phrase in content for phrase in ("netherita", "diamante", "encantada", "proteccion")):
            score += 0.10
        if any(token in ("armadura", "armor", "armaduras") for token in focus_tokens):
            if any(phrase in content for phrase in ("netherita", "diamante", "durabilidad", "proteccion")):
                score += 0.18
        if any(token in ("comida", "food") for token in focus_tokens):
            if any(phrase in content for phrase in ("zanahorias doradas", "carne cocinada", "saturacion")):
                score += 0.14
        if any(token in ("espada", "sword") for token in focus_tokens):
            if any(phrase in title for phrase in ("armas", "espada")):
                score += 0.18
            if any(
                phrase in content
                for phrase in (
                    "sharpness",
                    "saqueo",
                    "looting",
                    "aspecto igneo",
                    "fire aspect",
                    "irrompibilidad",
                    "mending",
                    "reparacion",
                    "sweeping edge",
                )
            ):
                score += 0.34
            if any(phrase in content for phrase in ("mesa de encantamientos", "yunque", "lapislazuli")) and not any(
                phrase in content for phrase in ("sharpness", "saqueo", "looting", "aspecto igneo", "irrompibilidad", "mending", "reparacion")
            ):
                score -= 0.22
        if any(token in ("pico", "pickaxe") for token in focus_tokens):
            if any(phrase in title for phrase in ("herramientas", "pico")):
                score += 0.18
            if any(
                phrase in content
                for phrase in (
                    "efficiency",
                    "eficiencia",
                    "fortune",
                    "fortuna",
                    "silk touch",
                    "toque de seda",
                    "irrompibilidad",
                    "mending",
                    "reparacion",
                )
            ):
                score += 0.34
            if any(phrase in content for phrase in ("mesa de encantamientos", "yunque", "lapislazuli")) and not any(
                phrase in content for phrase in ("efficiency", "eficiencia", "fortune", "fortuna", "silk touch", "toque de seda", "irrompibilidad", "mending", "reparacion")
            ):
                score -= 0.22

    elif question_type == "possibility":
        if any(phrase in content for phrase in ("se puede", "puede", "no se puede", "es posible")):
            score += 0.16

    elif question_type == "tame":
        if any(phrase in content for phrase in ("para domesticar", "hay que darle huesos", "se domestica", "particulas de corazon", "se pueden domesticar usando huesos")):
            score += 0.30
        if any(phrase in content for phrase in ("reproducen", "curar a un lobo domesticado")):
            score -= 0.10

    if any(token in ("encantamientos", "encantamiento", "enchanting", "enchantments") for token in focus_tokens):
        if any(phrase in title for phrase in ("encantamientos", "enchanting", "enchantments")) or any(
            phrase in source for phrase in ("encantamientos", "enchanting", "enchantments")
        ):
            score += 0.40
        if any(phrase in content for phrase in ("mejoran herramientas", "mesa de encantamientos", "yunque", "libros encantados", "lapislazuli", "lapislazuli es necesario")):
            score += 0.38
        if "experiencia" in title or "xp" in title or "experience" in title:
            score -= 0.18
        if question_type == "mechanic" and any(
            phrase in content for phrase in ("mejoran herramientas", "dos formas principales", "mesa de encantamientos", "yunque", "libros encantados")
        ):
            score += 0.28
        if question_type == "mechanic" and any(phrase in title for phrase in ("lapislazuli", "suministro")):
            score -= 0.24
        if question_type == "mechanic" and "funcionamiento" in title:
            score += 0.24
        if question_type == "best_choice" and any(token in ("espada", "sword", "pico", "pickaxe") for token in focus_tokens):
            if any(phrase in content for phrase in ("mesa de encantamientos", "yunque", "lapislazuli")) and not any(
                phrase in content
                for phrase in (
                    "sharpness",
                    "saqueo",
                    "looting",
                    "aspecto igneo",
                    "fire aspect",
                    "efficiency",
                    "eficiencia",
                    "fortune",
                    "fortuna",
                    "silk touch",
                    "toque de seda",
                    "mending",
                    "reparacion",
                )
            ):
                score -= 0.32

    if "cueva" in focus or "cuevas" in focus:
        if any(phrase in content for phrase in ("luz", "antorchas", "retirada", "comida", "seguridad", "agua", "escudo")):
            score += 0.20

    if any(token in ("diamante", "diamantes") for token in focus_tokens) and question_type in {"location", "obtain"}:
        if "diamante mineria" in title or "diamantes" in content:
            score += 0.16
        if "recetas de crafteo" in title:
            score -= 0.18

    if "mesa de crafteo" in content and question_type == "purpose":
        score += 0.12
    content_length = len(chunk.content)

    if question_type in {"definition", "recipe", "purpose", "tame", "requirements", "location", "timing", "possibility"}:
        if content_length > 450:
            score -= 0.20
        elif content_length < 260:
            score += 0.04

    if question_type in {"mechanic", "repair", "build", "strategy", "comparison", "combat", "best_choice", "obtain"}:
        if content_length > 650:
            score -= 0.12

    if "referencia " in title and question_type in {"definition", "recipe", "purpose", "tame", "requirements"}:
        score -= 0.08

    if any(phrase in title for phrase in ("preguntas frecuentes", "detalles adicionales")):
        score -= 0.10

    score += min(content_length / 900, 0.04)
    return score


def rerank_candidates(
    message: str,
    candidates: list[tuple[DocumentChunk, float]],
    analysis_message: str | None = None,
) -> list[tuple[DocumentChunk, float]]:
    analysis_text = analysis_message or message
    question_type = detect_question_type(analysis_text)
    focus = extract_focus_term(analysis_text, question_type)
    focus_tokens = extract_focus_tokens(focus)
    question_keywords = extract_question_keywords(analysis_text)
    reranked = []

    for chunk, similarity in candidates:
        score = score_candidate(chunk, similarity, question_type, focus, focus_tokens)
        content = normalize_text(chunk.content)
        title = normalize_text(chunk.title or "")

        score += count_focus_matches(content, question_keywords) * 0.04
        score += count_focus_matches(title, question_keywords) * 0.03

        reranked.append((chunk, score))

    reranked.sort(
        key=lambda item: (item[1], -len(item[0].content)),
        reverse=True,
    )
    return reranked


def select_final_chunks(
    message: str,
    reranked_chunks: list[tuple[DocumentChunk, float]],
    analysis_message: str | None = None,
) -> list[tuple[DocumentChunk, float]]:
    analysis_text = analysis_message or message
    question_type = detect_question_type(analysis_text)

    if question_type == "definition":
        return reranked_chunks[:1]

    if question_type in {"recipe", "purpose", "tame", "location", "timing", "possibility", "best_choice"}:
        return reranked_chunks[:1]

    if question_type in {"requirements", "mechanic", "repair", "obtain"}:
        return reranked_chunks[:3]

    if question_type in {"build", "strategy", "combat", "general"}:
        return reranked_chunks[:3]

    if question_type in {"comparison", "combat", "requirements", "mechanic", "obtain", "build", "strategy", "general"}:
        return reranked_chunks[:2]

    return reranked_chunks[:1]


def find_top_document_chunks(
    db: Session,
    message: str,
    limit: int = 3,
    analysis_message: str | None = None,
) -> list[tuple[DocumentChunk, float]]:
    query_embedding = generate_embedding(message)
    chunks = db.query(DocumentChunk).filter(DocumentChunk.embedding.isnot(None)).all()
    scored_chunks = []
    analysis_text = analysis_message or message
    question_type = detect_question_type(analysis_text)
    focus = extract_focus_term(analysis_text, question_type)
    focus_tokens = extract_focus_tokens(focus)
    question_keywords = extract_question_keywords(analysis_text)

    for chunk in chunks:
        chunk_embedding = deserialize_embedding(chunk.embedding)
        similarity = cosine_similarity(query_embedding, chunk_embedding)
        if similarity > SIMILARITY_THRESHOLD:
            scored_chunks.append((chunk, similarity))

    scored_chunks.sort(
        key=lambda item: (item[1], -len(item[0].content)),
        reverse=True,
    )

    semantic_candidates = scored_chunks[:INITIAL_RETRIEVAL_LIMIT]
    keyword_candidates = find_keyword_candidates(
        chunks,
        focus,
        focus_tokens,
        question_keywords,
        question_type=question_type,
        limit=INITIAL_KEYWORD_LIMIT,
    )

    if question_type == "recipe":
        exact_recipe_candidates = []
        for chunk in chunks:
            content = normalize_text(chunk.content)
            title = normalize_text(chunk.title or "")
            source = normalize_text(chunk.source or "")
            combined_text = " ".join((content, title, source))
            is_potion_recipe = "pocion" in focus_tokens

            score = 0.0
            if focus and focus in content:
                score += 1.0
            if focus and focus in title:
                score += 0.8
            if any(phrase in title for phrase in ("receta", "recetas", "crafteo", "crafting")):
                score += 0.8
            if any(phrase in source for phrase in ("receta", "recetas", "crafteo", "crafting")):
                score += 0.6
            if any(phrase in content for phrase in ("se fabrica con", "se hace con")):
                score += 0.8
            if is_potion_recipe and any(
                phrase in content for phrase in ("pocion de ", "awkward potion", "fermented spider eye", "golden carrot")
            ):
                score += 0.9
            if is_potion_recipe and "soporte para pociones" in content:
                score -= 1.4
            if is_potion_recipe and not has_specific_focus_match(
                combined_text,
                focus_tokens,
                {"pocion", "pociones"},
            ):
                score -= 1.1
            if any(phrase in content for phrase in ("sirve para", "restaura", "protege", "encantamiento")):
                score -= 0.35

            if score > 1.0:
                exact_recipe_candidates.append((chunk, score))

        exact_recipe_candidates.sort(key=lambda item: (item[1], -len(item[0].content)), reverse=True)
        keyword_candidates = exact_recipe_candidates[:8] + [
            item for item in keyword_candidates if item[0].id not in {chunk.id for chunk, _ in exact_recipe_candidates[:8]}
        ][:7]

    merged_candidates_by_id: dict[int, tuple[DocumentChunk, float]] = {}
    for chunk, score in semantic_candidates:
        merged_candidates_by_id[chunk.id] = (chunk, score)

    for chunk, keyword_score in keyword_candidates:
        existing = merged_candidates_by_id.get(chunk.id)
        if existing is None:
            merged_candidates_by_id[chunk.id] = (chunk, keyword_score * 0.35)
        else:
            merged_candidates_by_id[chunk.id] = (chunk, existing[1] + keyword_score * 0.2)

    initial_candidates = list(merged_candidates_by_id.values())
    reranked_candidates = rerank_candidates(message, initial_candidates, analysis_text)
    final_chunks = select_final_chunks(message, reranked_candidates, analysis_text)
    return final_chunks[:limit]


def format_context_for_llm(
    chunks: list[tuple[DocumentChunk, float]],
    max_chunks: int = LLM_CONTEXT_LIMIT,
) -> str:
    if not chunks:
        return ""

    context_blocks: list[str] = []

    for index, (chunk, score) in enumerate(chunks[:max_chunks], start=1):
        source_label = chunk.title or chunk.source or f"Fragmento {index}"
        context_blocks.append(
            "\n".join(
                [
                    f"[Fragmento {index}]",
                    f"Titulo: {source_label}",
                    f"Similitud: {score:.3f}",
                    f"Contenido: {chunk.content.strip()}",
                ]
            )
        )

    return "\n\n".join(context_blocks)


def _split_sentences(text: str) -> list[str]:
    normalized = text.replace("\n", " ").strip()
    if not normalized:
        return []
    parts = re.split(r"(?<=[.!?])\s+", normalized)
    return [part.strip() for part in parts if part.strip()]


def _response_config(question_type: str) -> dict[str, int | bool]:
    if question_type == "definition":
        return {"min_sentences": 1, "max_sentences": 2, "max_chars": 320, "numbered": False}
    if question_type in {"purpose", "location", "timing", "possibility"}:
        return {"min_sentences": 1, "max_sentences": 3, "max_chars": 380, "numbered": False}
    if question_type == "item_enchantments":
        return {"min_sentences": 1, "max_sentences": 3, "max_chars": 420, "numbered": True}
    if question_type == "recipe":
        return {"min_sentences": 2, "max_sentences": 3, "max_chars": 420, "numbered": False}
    if question_type == "tame":
        return {"min_sentences": 1, "max_sentences": 3, "max_chars": 380, "numbered": False}
    if question_type in {"requirements", "mechanic", "repair", "obtain"}:
        return {"min_sentences": 1, "max_sentences": 4, "max_chars": 520, "numbered": False}
    if question_type in {"best_choice", "comparison"}:
        return {"min_sentences": 1, "max_sentences": 3, "max_chars": 440, "numbered": False}
    if question_type in {"build", "strategy", "combat", "general"}:
        return {"min_sentences": 1, "max_sentences": 4, "max_chars": 560, "numbered": True}
    return {"min_sentences": 1, "max_sentences": 3, "max_chars": 380, "numbered": False}


def _is_question_heading_sentence(sentence: str) -> bool:
    return False


def _remove_question_echo_sentences(sentences: list[str], analysis_text: str) -> list[str]:
    return sentences


def _score_sentence(sentence: str, question_type: str, focus_tokens: list[str]) -> float:
    normalized = normalize_text(sentence)
    score = 0.0

    focus_match_count = count_focus_matches(normalized, focus_tokens)
    score += focus_match_count * 0.25

    if question_type in {"definition", "recipe", "purpose", "obtain", "location", "build"} and focus_tokens and focus_match_count == 0:
        score -= 0.18
    if question_type == "definition":
        if any(phrase in normalized for phrase in ("es un", "es una", "es un mob", "criatura", "mob hostil", "mob neutral", "mob pasivo")):
            score += 0.45
        if any(phrase in normalized for phrase in ("estructura", "estructuras")):
            score += 0.22
        if any(phrase in normalized for phrase in ("aparece", "aparecen", "se acerca", "explota", "ataca", "sirve para", "suelta", "habita")):
            score += 0.18
        if any(phrase in normalized for phrase in ("suelen encontrarse en", "pueden encontrarse en")):
            score -= 0.20
        if any(phrase in normalized for phrase in ("granja", "sirve para fabricar", "se fabrica con", "sueltan")):
            score -= 0.20
    elif question_type == "recipe":
        is_potion_recipe = "pocion" in focus_tokens
        if "se fabrica con" in normalized:
            score += 0.45
        if is_potion_recipe and "pocion de " in normalized:
            score += 0.28
        if is_potion_recipe and "soporte para pociones" in normalized:
            score -= 0.95
        if any(phrase in normalized for phrase in ("mesa de crafteo", "fila", "coloca", "encima", "debajo", "columna", "forma de", "produce", "obtienes", "casilla central", "rodea", "rodeando", "vertical", "horizontal", "alrededor")):
            score += 0.12
    elif question_type == "item_enchantments":
        if any(
            phrase in normalized
            for phrase in (
                "puede llevar",
                "puede tener",
                "se le pueden poner",
                "lista principal",
            )
        ):
            score += 0.48
        if any(
            phrase in normalized
            for phrase in (
                "mesa de encantamientos",
                "libros encantados",
                "niveles de experiencia",
                "lapislazuli",
                "yunque",
            )
        ):
            score -= 0.22
    elif question_type == "purpose":
        if any(phrase in normalized for phrase in ("sirve para", "permite", "se usa para", "bloquea", "compara", "mide", "activa")):
            score += 0.40
    elif question_type == "requirements":
        if any(phrase in normalized for phrase in ("necesitas", "hace falta", "requiere", "para usar", "para hacer")):
            score += 0.38
    elif question_type == "tame":
        if any(phrase in normalized for phrase in ("usar huesos", "huesos", "corazon", "collar", "domesticar")):
            score += 0.40
    elif question_type == "mechanic":
        if any(phrase in normalized for phrase in ("funciona", "hay dos formas", "usa", "depende", "de noche", "tormenta", "no puedes dormir")):
            score += 0.34
        if any(phrase in normalized for phrase in ("para dormir", "necesitas una cama", "zona segura", "punto de respawn")):
            score += 0.18
    elif question_type == "repair":
        if any(
            phrase in normalized
            for phrase in (
                "se reparan",
                "yunque",
                "mending",
                "combinar dos herramientas",
                "material correspondiente",
                "puntos de durabilidad",
            )
        ):
            score += 0.40
    elif question_type == "obtain":
        if any(phrase in normalized for phrase in ("se obtiene", "se consiguen", "se obtienen", "al derrotar", "comerciar", "minando", "aparece")):
            score += 0.34
    elif question_type == "location":
        if any(phrase in normalized for phrase in ("aparecen", "aparece", "se encuentra", "pantanos", "nether", "end", "overworld", "y -58", "y -59", "entre los mobs", "comunes en", "se asocian")):
            score += 0.34
    elif question_type == "build":
        if any(phrase in normalized for phrase in ("se basa en", "necesita", "usa", "tolvas", "aldeanos", "golems", "plataformas", "spawn")):
            score += 0.30
        if any(token in ("intercambio", "intercambios", "trade", "trades") for token in focus_tokens):
            if any(phrase in normalized for phrase in ("descuentos", "curar aldeanos zombie", "bibliotecarios", "bloque de trabajo", "primer intercambio", "ofertas")):
                score += 0.40
            if any(phrase in normalized for phrase in ("experiencia", "cuarzo", "blaze", "enderman")):
                score -= 0.22
        if any(token in ("creeper", "creepers") for token in focus_tokens):
            if any(phrase in normalized for phrase in ("tijeras", "esquila")):
                score -= 0.28
    elif question_type == "combat":
        if any(phrase in normalized for phrase in ("derrotar", "matar", "cristales", "vulnerable", "arco", "espada", "pociones")):
            score += 0.34
    elif question_type == "strategy":
        if any(phrase in normalized for phrase in ("estrategia", "avanzar", "iluminar", "retirada", "comida", "escudo", "agua", "marcar el camino")):
            score += 0.34
        if any(token in ("nether",) for token in focus_tokens):
            if any(
                phrase in normalized
                for phrase in ("resistencia al fuego", "armadura de oro", "hoglins", "ghasts", "bloques de cobertura", "comida")
            ):
                score += 0.28
        if any(token in ("wither",) for token in focus_tokens):
            if any(
                phrase in normalized
                for phrase in ("leche", "regeneracion", "resistencia", "manzanas doradas", "espacio controlado", "invocarlo")
            ):
                score += 0.28
            if any(phrase in normalized for phrase in ("ender dragon", "cristales")):
                score -= 0.30
    elif question_type == "best_choice":
        if any(phrase in normalized for phrase in ("mejor", "mejores", "depende", "opcion", "suele ser")):
            score += 0.30
        if any(token in ("espada", "sword") for token in focus_tokens):
            if any(
                phrase in normalized
                for phrase in ("sharpness", "saqueo", "looting", "aspecto igneo", "fire aspect", "irrompibilidad", "mending", "reparacion")
            ):
                score += 0.34
        if any(token in ("pico", "pickaxe") for token in focus_tokens):
            if any(
                phrase in normalized
                for phrase in ("efficiency", "eficiencia", "fortune", "fortuna", "silk touch", "toque de seda", "irrompibilidad", "mending", "reparacion")
            ):
                score += 0.34

    score -= len(sentence) / 800
    return score


def _is_redundant_sentence(candidate_sentence: str, selected_sentences: list[str]) -> bool:
    candidate_tokens = set(re.findall(r"[a-z0-9]+", normalize_text(candidate_sentence)))
    if not candidate_tokens:
        return False

    for selected_sentence in selected_sentences:
        selected_tokens = set(re.findall(r"[a-z0-9]+", normalize_text(selected_sentence)))
        if not selected_tokens:
            continue
        overlap = len(candidate_tokens & selected_tokens) / max(1, min(len(candidate_tokens), len(selected_tokens)))
        if overlap >= 0.7:
            return True

    return False


def _select_response_sentences(
    chunks: list[tuple[DocumentChunk, float]],
    question_type: str,
    focus_tokens: list[str],
) -> list[str]:
    config = _response_config(question_type)
    min_sentences = int(config.get("min_sentences", 1))
    max_sentences = int(config["max_sentences"])
    max_chars = int(config["max_chars"])

    candidates: list[tuple[float, int, int, str, str]] = []
    seen_normalized: dict[str, tuple[float, int, int, str, str]] = {}

    for chunk_rank, (chunk, chunk_score) in enumerate(chunks):
        sentences = _split_sentences(chunk.content)
        for sentence_index, sentence in enumerate(sentences):
            normalized_sentence = normalize_text(sentence)
            if len(normalized_sentence) < 8:
                continue

            sentence_score = _score_sentence(sentence, question_type, focus_tokens)
            sentence_score += chunk_score * 0.12
            sentence_score += max(0.0, 0.22 - chunk_rank * 0.08)

            if sentence_index == 0 and not _is_question_heading_sentence(sentence):
                sentence_score += 0.12

            stored = seen_normalized.get(normalized_sentence)
            candidate = (sentence_score, chunk_rank, sentence_index, sentence, normalized_sentence)
            if stored is None or candidate[0] > stored[0]:
                seen_normalized[normalized_sentence] = candidate

    candidates = list(seen_normalized.values())
    candidates.sort(key=lambda item: item[0], reverse=True)
    best_score = candidates[0][0] if candidates else 0.0

    selected: list[tuple[int, int, str]] = []
    used_normalized: set[str] = set()
    total_chars = 0
    if question_type in {"strategy", "combat", "general"}:
        score_margin = 0.55
    elif question_type in {"build", "obtain", "mechanic", "repair", "requirements"}:
        score_margin = 0.35
    elif question_type in {"best_choice", "comparison"}:
        score_margin = 0.40
    else:
        score_margin = 0.32

    for sentence_score, chunk_rank, sentence_index, sentence, normalized_sentence in candidates:
        if len(selected) >= max_sentences:
            break
        if sentence_score < -0.05 and selected:
            continue
        if selected and sentence_score < best_score - score_margin:
            continue
        if normalized_sentence in used_normalized:
            continue
        if _is_redundant_sentence(sentence, [existing_sentence for _, _, existing_sentence in selected]):
            continue
        if total_chars + len(sentence) + 1 > max_chars and selected:
            continue

        selected.append((chunk_rank, sentence_index, sentence))
        used_normalized.add(normalized_sentence)
        total_chars += len(sentence) + 1

    if not selected and chunks:
        fallback_sentences = _split_sentences(chunks[0][0].content)
        if fallback_sentences:
            selected.append((0, 0, fallback_sentences[0]))

    if question_type == "recipe":
        selected_sentences = [existing_sentence for _, _, existing_sentence in selected]
        placement_markers = (
            "fila",
            "columna",
            "centro",
            "casilla",
            "encima",
            "debajo",
            "vertical",
            "horizontal",
            "rode",
            "alrededor",
            "forma de",
            "diagonal",
            "a los lados",
        )
        quantity_markers = (
            "la receta produce",
            "obtienes",
            "produce ",
        )

        def _contains_marker(sentence_text: str, markers: tuple[str, ...]) -> bool:
            lowered = normalize_text(sentence_text)
            return any(marker in lowered for marker in markers)

        needs_placement = not any(_contains_marker(sentence, placement_markers) for sentence in selected_sentences)
        needs_quantity = not any(_contains_marker(sentence, quantity_markers) for sentence in selected_sentences)

        for markers, needed in ((placement_markers, needs_placement), (quantity_markers, needs_quantity)):
            if not needed:
                continue
            for sentence_score, chunk_rank, sentence_index, sentence, normalized_sentence in candidates:
                if len(selected) >= max_sentences:
                    break
                if normalized_sentence in used_normalized:
                    continue
                if not _contains_marker(sentence, markers):
                    continue
                if _is_redundant_sentence(sentence, selected_sentences):
                    continue
                if total_chars + len(sentence) + 1 > max_chars and selected:
                    continue
                selected.append((chunk_rank, sentence_index, sentence))
                used_normalized.add(normalized_sentence)
                selected_sentences.append(sentence)
                total_chars += len(sentence) + 1
                break

    if len(selected) < min_sentences:
        selected_sentences = [existing_sentence for _, _, existing_sentence in selected]
        for sentence_score, chunk_rank, sentence_index, sentence, normalized_sentence in candidates:
            if len(selected) >= min_sentences:
                break
            if normalized_sentence in used_normalized:
                continue
            if _is_redundant_sentence(sentence, selected_sentences):
                continue
            if total_chars + len(sentence) + 1 > max_chars:
                continue
            selected.append((chunk_rank, sentence_index, sentence))
            used_normalized.add(normalized_sentence)
            selected_sentences.append(sentence)
            total_chars += len(sentence) + 1

    if question_type != "definition":
        selected.sort(key=lambda item: (item[0], item[1]))
    cleaned_sentences = [sentence for _, _, sentence in selected]
    return cleaned_sentences


def build_document_response(
    chunks: list[tuple[DocumentChunk, float]],
    message: str | None = None,
    analysis_message: str | None = None,
) -> str:
    if not chunks:
        return (
            "No he encontrado informacion relacionada en la base de datos. "
            "Prueba con otra pregunta o vuelve a cargar los documentos con embeddings."
        )

    analysis_text = analysis_message or message or ""
    question_type = detect_question_type(analysis_text)
    focus = extract_focus_term(analysis_text, question_type)
    focus_tokens = extract_focus_tokens(focus)
    best_chunk = chunks[0][0]
    response_sentences = _select_response_sentences(chunks, question_type, focus_tokens)
    config = _response_config(question_type)

    if not response_sentences:
        fallback_sentences: list[str] = []
        for chunk, _ in chunks:
            for sentence in _split_sentences(chunk.content):
                if _is_redundant_sentence(sentence, fallback_sentences):
                    continue
                fallback_sentences.append(sentence)
                if len(fallback_sentences) >= int(config.get("min_sentences", 1)):
                    break
            if fallback_sentences:
                break
        if fallback_sentences:
            response_sentences = fallback_sentences

    if not response_sentences:
        return best_chunk.content

    if config["numbered"] and len(response_sentences) > 1:
        return "\n".join(
            f"{index}. {sentence}" for index, sentence in enumerate(response_sentences, start=1)
        )

    return " ".join(response_sentences)
