from openai import OpenAI
from config import OPENAI_API_KEY, MAX_CONTEXT_MESSAGES
from database import obtener_memoria, actualizar_memoria

# Inicializar cliente OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# =========================
# PROMPT BASE DEL ASESOR
# =========================

SYSTEM_PROMPT = """
Eres un ASESOR PROFESIONAL DE TRADING EN FUTUROS PERPETUOS.

ROL:
- Asistente educativo personal 24/7 para alumnos de una academia.
- Actúas como un mentor experto, claro, humano y paciente.

CAPACIDADES:
- Análisis avanzado: market structure, liquidez, order blocks, FVG,
  contexto multi-timeframe, sesiones.
- Explicas escenarios de trading de forma REALISTA y PROFESIONAL.

REGLAS ESTRICTAS:
- NO das señales directas.
- NO dices “compra”, “vende”, “entra ahora”.
- NO prometes ganancias.
- SIEMPRE aclaras que es contenido educativo, no asesoría financiera.

ESTILO:
- Lenguaje claro y didáctico.
- Te adaptas automáticamente al nivel del alumno.
- Si el alumno repite dudas, ajustas la explicación.
"""

# =========================
# FUNCIÓN PRINCIPAL
# =========================

def responder(user_id: int, mensaje_usuario: str) -> str:
    """
    Genera una respuesta usando:
    - Perfil permanente del alumno
    - Historial reciente
    - Nuevo mensaje
    """

    memoria = obtener_memoria(user_id)

    perfil = memoria.get("perfil", "")
    historial = memoria.get("historial", [])

    # Construir mensajes para la IA
    mensajes = [{"role": "system", "content": SYSTEM_PROMPT}]

    if perfil:
        mensajes.append({
            "role": "system",
            "content": f"Perfil del alumno: {perfil}"
        })

    # Agregar historial limitado por MAX_CONTEXT_MESSAGES
    for h in historial[-MAX_CONTEXT_MESSAGES:]:
        mensajes.append(h)

    # Agregar nuevo mensaje del usuario
    mensajes.append({
        "role": "user",
        "content": mensaje_usuario
    })

    # =========================
    # GENERAR RESPUESTA IA
    # =========================

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Cambiado a modelo gratuito
        messages=mensajes
    )

    respuesta = response.choices[0].message.content

    # =========================
    # ACTUALIZAR MEMORIA
    # =========================

    historial.append({"role": "user", "content": mensaje_usuario})
    historial.append({"role": "assistant", "content": respuesta})

    # Limitar historial
    historial = historial[-MAX_CONTEXT_MESSAGES * 2:]

    # Perfil adaptativo base
    if not perfil:
        perfil = "Alumno en proceso de aprendizaje de trading en futuros perpetuos."

    actualizar_memoria(user_id, perfil, historial)

    return respuesta
