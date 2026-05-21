import re
import unicodedata


SPANISH_STOPWORDS = {
    "como", "que", "para", "con", "sin", "puedo", "puede", "hacer",
    "funciona", "mejor", "donde", "cual", "los", "las", "una", "un",
    "del", "por", "necesito", "sirve", "aparece", "como", "se", "consigue",
    "encantamiento", "granja", "mobs", "minecraft",
}

CATALAN_STOPWORDS = {
    "com", "que", "per", "amb", "sense", "puc", "pot", "fer",
    "funciona", "millor", "on", "quina", "quin", "els", "les", "una", "un",
    "del", "pel", "necessito", "serveix", "apareix", "apareixen", "es",
}

ENGLISH_STOPWORDS = {
    "how", "what", "where", "which", "can", "the", "with", "without",
    "for", "need", "best", "does", "work", "make", "build", "find",
    "get", "is", "are", "appear",
}


def _normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return " ".join(text.split())


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-ZÀ-ÿ0-9'-]+", text.lower())


def detect_input_language(text: str) -> str:
    normalized = _normalize_text(text)
    tokens = _tokenize(normalized)
    if not tokens:
        return "es"

    spanish_score = sum(token in SPANISH_STOPWORDS for token in tokens)
    catalan_score = sum(token in CATALAN_STOPWORDS for token in tokens)
    english_score = sum(token in ENGLISH_STOPWORDS for token in tokens)

    if normalized.startswith(("com ", "que ", "quina ", "quin ", "on ", "per a que ")):
        catalan_score += 2
    if normalized.startswith(("how ", "what ", "where ", "which ")):
        english_score += 2
    if normalized.startswith(("como ", "que ", "donde ", "cual ", "para que ")):
        spanish_score += 2

    if catalan_score > spanish_score and catalan_score >= english_score:
        return "ca"
    if english_score > spanish_score:
        return "en"
    return "es"
