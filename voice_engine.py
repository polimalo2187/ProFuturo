from gtts import gTTS
import uuid
import os

# =========================
# CONVERSIÓN TEXTO → AUDIO
# =========================

def generar_audio(texto: str) -> str:
    """
    Convierte texto en audio (español) y devuelve
    la ruta del archivo generado.
    """
    nombre_archivo = f"audio_{uuid.uuid4()}.mp3"
    tts = gTTS(text=texto, lang="es", slow=False)
    tts.save(nombre_archivo)
    return nombre_archivo

def eliminar_audio(ruta: str):
    """
    Elimina el archivo de audio temporal.
    """
    if os.path.exists(ruta):
        os.remove(ruta)
