"""
Servidor FastAPI para el bot de imputación de horas
Usa el token JWT del usuario que ya está logueado
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

from api_client import DemoApiClient
from ai.interpreter import interpretar_mensaje
from core.ejecutor import ejecutar_comando

app = FastAPI(title="Bot Demo Horas", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    token: str  # Token JWT del usuario logueado
    message: str


class ChatResponse(BaseModel):
    response: str
    success: bool


# Sesiones en memoria (por token)
api_clients = {}


def get_or_create_client(token):
    """Obtiene o crea un cliente API con el token JWT"""
    if token in api_clients:
        return api_clients[token]
    
    client = DemoApiClient()
    client.set_token(token)
    
    # Verificar que el token es válido intentando obtener proyectos
    proyectos = client.obtener_proyectos()
    if proyectos is None:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    api_clients[token] = client
    return client


@app.get("/")
def root():
    return {"status": "ok", "service": "Bot Demo Horas"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Endpoint principal del chatbot
    
    Recibe el token JWT del usuario ya logueado y ejecuta comandos
    """
    try:
        print(f"\n{'='*60}")
        print(f"📨 Mensaje: {request.message}")
        print(f"🔑 Token: {request.token[:20]}...")
        print(f"{'='*60}")
        
        # 1. Obtener cliente API con el token
        api_client = get_or_create_client(request.token)
        
        # 2. Interpretar con GPT-4
        comando = interpretar_mensaje(request.message)
        
        if not comando:
            return ChatResponse(
                response="❌ No entendí tu mensaje. Intenta reformularlo.",
                success=False
            )
        
        # 3. Ejecutar comando
        respuesta = ejecutar_comando(api_client, comando)
        
        print(f"\n✅ Respuesta: {respuesta}\n")
        
        return ChatResponse(
            response=respuesta,
            success=True
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        return ChatResponse(
            response=f"❌ Error: {str(e)}",
            success=False
        )


@app.delete("/session/{token}")
def delete_session(token: str):
    """Elimina sesión del token"""
    if token in api_clients:
        del api_clients[token]
        return {"message": "Sesión eliminada"}
    return {"message": "Sesión no encontrada"}


@app.get("/stats")
def stats():
    """Estadísticas del bot"""
    return {
        "active_sessions": len(api_clients)
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BOT_PORT", 8001))
    
    print(f"""
╔════════════════════════════════════════╗
║   🤖 BOT DEMO HORAS - INICIADO        ║
║   Puerto: {port}                         ║
║   Actúa sobre el usuario logueado     ║
╚════════════════════════════════════════╝
""")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
