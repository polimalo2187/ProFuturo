from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
Eres un asesor profesional de trading en futuros perpetuos.
No das señales, no prometes ganancias.
Explicas de forma clara, educativa y responsable.
"""

def responder(mensaje):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": mensaje}
        ]
    )
    return response.choices[0].message.content
