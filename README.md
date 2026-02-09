# 🤖 Bot Demo Horas

Bot simple para imputar horas en demo-gestion-horas.

**IMPORTANTE**: El bot actúa sobre el usuario que está logueado en el frontend (usa su token JWT).

## Instalación

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## Configuración

Copia `.env.example` a `.env` y añade tu API key de OpenAI:

```env
OPENAI_API_KEY=tu_key_aqui
DEMO_API_URL=http://localhost:8000
BOT_PORT=8001
```

## Uso

```bash
# Activar entorno
.venv\Scripts\activate

# Iniciar servidor
python server.py
```

El bot estará en `http://localhost:8001`

## API

**POST /chat**

El frontend envía el token JWT del usuario logueado:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "message": "Pon 8 horas en Desarrollo toda la semana"
}
```

**Response:**
```json
{
  "response": "✅ Desarrollo: 8h × 5 días (lunes, martes, miercoles, jueves, viernes)",
  "success": true
}
```

## Ejemplos de comandos

### Consultas
- "¿Qué horas tengo esta semana?"
- "Resumen de la semana"

### Imputación simple
- "Pon 8 horas en Desarrollo toda la semana"
- "Imputa 4 horas el lunes en Dirección"

### Imputación múltiple
- "3h en Desarrollo y 5h en Reuniones el lunes"
- "4h en Desarrollo y 2h en Dirección toda la semana"

## Integración con Frontend

El chatbot del frontend debe:
1. Obtener el token del `localStorage.getItem('token')`
2. Enviarlo en cada petición al bot
3. El bot actúa sobre la sesión del usuario logueado

```javascript
const token = localStorage.getItem('token');

const response = await fetch('http://localhost:8001/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    token: token,
    message: userInput
  })
});

const data = await response.json();
console.log(data.response); // Mostrar al usuario
```

## Ventajas

✅ El bot actúa sobre el **usuario ya logueado**
✅ No necesita credenciales adicionales
✅ Usa el mismo token JWT que el frontend
✅ Los cambios se reflejan automáticamente vía WebSocket
