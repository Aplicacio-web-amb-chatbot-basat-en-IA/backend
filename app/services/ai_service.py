import os

from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

SYSTEM_INSTRUCTION = """
Eres un asistente experto en Minecraft Vanilla.

Objetivo:
Responder preguntas de Minecraft Vanilla con precisión, claridad y utilidad.

Reglas obligatorias:
- Responde siempre en español.
- Habla solo de Minecraft Vanilla.
- No menciones mods, plugins ni contenido no oficial salvo que el usuario lo pida explícitamente.
- No inventes datos, mecánicas, recetas, versiones ni probabilidades.
- Si no estás seguro, di claramente "No estoy seguro" o "No lo sé con certeza".
- Si la pregunta es ambigua, indica la ambigüedad y da la interpretación más probable.
- Prioriza exactitud por encima de velocidad o creatividad.
- Da una respuesta breve pero suficiente: entre 2 y 5 frases.
- Si ayuda, añade un último consejo práctico en una frase.
- No uses relleno ni introducciones largas.
"""

def build_user_prompt(user_message: str) -> str:
    return f"""
Sigue estos ejemplos de estilo:

Pregunta: ¿Cómo consigo obsidiana?
Respuesta: La obsidiana se obtiene cuando el agua entra en contacto con un bloque fuente de lava. No se fabrica en la mesa de crafteo. Para recogerla necesitas un pico de diamante o de netherita.

Pregunta: ¿Los aldeanos pueden abrir cofres?
Respuesta: No, en Minecraft Vanilla los aldeanos no abren cofres ni gestionan inventarios como un jugador. Solo interactúan con ciertos bloques de trabajo y con sus mecánicas propias.

Pregunta: ¿Cuál es la mejor granja del juego?
Respuesta: Depende del recurso que quieras conseguir, porque no hay una única mejor granja para todo. Si me dices si buscas comida, experiencia, hierro o esmeraldas, te recomiendo una opción concreta.

Ahora responde a esta pregunta del usuario:
{user_message}
"""

def generate_response(user_message: str) -> str:
    try:
        if not GEMINI_API_KEY:
            return "Error con Gemini: falta GEMINI_API_KEY en el archivo .env"

        client = genai.Client(api_key=GEMINI_API_KEY)

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=build_user_prompt(user_message),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION
            )
        )

        return response.text if response.text else "No response"

    except Exception as e:
        return f"Error con Gemini: {str(e)}"
