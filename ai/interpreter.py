"""
Intérprete de comandos usando GPT-4
Convierte lenguaje natural a comandos estructurados JSON
"""
import json
from openai import OpenAI
import os
from datetime import datetime

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


SYSTEM_PROMPT = """Eres Arebot, un asistente amigable de gestión de horas laborales.

Tu trabajo es:
1. Conversar de forma natural cuando NO hay comandos
2. Convertir comandos a JSON estructurado cuando HAY acciones

TIPOS DE COMANDOS:

1. CONSULTA SEMANAL:
{
  "tipo": "consulta_semana",
  "fecha": "2026-02-03"
}

2. LISTAR PROYECTOS:
{
  "tipo": "listar_proyectos"
}

3. IMPUTACIÓN (uno o varios proyectos):
{
  "tipo": "imputar",
  "imputaciones": [
    {
      "proyecto": "Desarrollo",
      "horas": 8,
      "dias": ["lunes", "martes", "miercoles", "jueves", "viernes"]
    }
  ]
}

4. CONVERSACIÓN (cuando NO hay comando):
{
  "tipo": "conversacion",
  "respuesta": "¡Hola! ¿En qué puedo ayudarte hoy?"
}

REGLAS:
- Para SALUDOS, AGRADECIMIENTOS o CONVERSACIÓN GENERAL: usa tipo "conversacion"
- Para COMANDOS DE ACCIÓN: usa tipo "consulta_semana" o "imputar"
- Si dice "hoy", usa el día actual
- Si dice "toda la semana", usa: lunes, martes, miercoles, jueves, viernes
- Para consultas, devuelve el lunes de la semana en formato ISO
- NO INVENTES EL PROYECTO. Por ejemplo: si dice "Pon 8 horas en reunion" no interpretes "reuniones". Siempre haz lo que diga el usuario

FECHA ACTUAL DEL SISTEMA:
- Hoy es: """ + datetime.now().strftime("%d de %B de %Y") + """
- Día de la semana: """ + datetime.now().strftime("%A").replace('Monday', 'LUNES').replace('Tuesday', 'MARTES').replace('Wednesday', 'MIERCOLES').replace('Thursday', 'JUEVES').replace('Friday', 'VIERNES').replace('Saturday', 'SABADO').replace('Sunday', 'DOMINGO') + """
- Fecha en formato ISO: """ + datetime.now().strftime("%Y-%m-%d") + """
- IMPORTANTE: Si el usuario dice "hoy", "esta semana" o "ahora", usa esta fecha como referencia.

EJEMPLOS:

"hola"
{"tipo": "conversacion", "respuesta": "¡Hola! 👋 Soy tu asistente de gestión de horas. ¿En qué puedo ayudarte?"}

"gracias"
{"tipo": "conversacion", "respuesta": "¡De nada! 😊 Aquí estoy para lo que necesites."}

"¿qué proyectos tengo?"
{"tipo": "listar_proyectos"}

"lista mis proyectos"
{"tipo": "listar_proyectos"}

"muéstrame los proyectos"
{"tipo": "listar_proyectos"}

"¿Qué horas tengo esta semana?"
{"tipo": "consulta_semana", "fecha": "2026-02-03"}

"Pon 8 horas en Desarrollo toda la semana"
{"tipo": "imputar", "imputaciones": [{"proyecto": "Desarrollo", "horas": 8, "dias": ["lunes", "martes", "miercoles", "jueves", "viernes"]}]}

"3 horas en Desarrollo y 5 en Reuniones el lunes"
{"tipo": "imputar", "imputaciones": [{"proyecto": "Desarrollo", "horas": 3, "dias": ["lunes"]}, {"proyecto": "Reuniones", "horas": 5, "dias": ["lunes"]}]}

IMPORTANTE: RESPONDE SOLO CON EL JSON, sin explicaciones adicionales."""


def interpretar_mensaje(mensaje):
    """
    Interpreta un mensaje del usuario usando GPT-4
    
    Args:
        mensaje: Texto del usuario
        
    Returns:
        dict: Comando estructurado o None si hay error
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # SUPER BARATO: $0.00015/1K input + $0.0006/1K output
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": mensaje}
            ],
            temperature=0.3,  # Un poco más de creatividad para conversación
            max_tokens=500
        )
        
        contenido = response.choices[0].message.content.strip()
        
        # Limpiar markdown si GPT lo añade
        if contenido.startswith("```json"):
            contenido = contenido.replace("```json", "").replace("```", "").strip()
        elif contenido.startswith("```"):
            contenido = contenido.replace("```", "").strip()
        
        comando = json.loads(contenido)
        print(f"📝 Comando interpretado: {comando}")
        
        return comando
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parseando JSON de GPT: {e}")
        print(f"Contenido recibido: {contenido}")
        # Devolver respuesta de error amigable
        return {
            "tipo": "conversacion",
            "respuesta": "Lo siento, no entendí bien tu mensaje. ¿Podrías reformularlo?"
        }
    except Exception as e:
        print(f"❌ Error en GPT: {e}")
        return {
            "tipo": "conversacion",
            "respuesta": "Ups, tuve un problema técnico. Intenta de nuevo por favor."
        }
