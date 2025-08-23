import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from supabase import create_client, Client

# =========================================================================
# 1. CONFIGURACIÓN E INICIALIZACIÓN
# =========================================================================

# Inicializa el cliente de Supabase con tus credenciales.
# Es una buena práctica usar variables de entorno para las claves.
SUPABASE_URL = "https://supabase.kaiser-soft.com"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlzcyI6InN1cGFiYXNlIiwiaWF0IjoxNzU1ODM4ODAwLCJleHAiOjE5MTM2MDUyMDB9.QHME589F1zHAZRX23WX6sBaQZ_pKVT-M-1MEXWlRDQc"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Crea la instancia de FastMCP.
mcp = FastMCP(name="Insurence MCP")

# Crea la aplicación ASGI de FastMCP. Esta aplicación gestiona el ciclo de vida
# y los endpoints de MCP.
mcp_app = mcp.http_app(path='/mcp')

# Crea la aplicación principal de FastAPI.
# Es CRUCIAL pasar el 'lifespan' del objeto mcp_app.
app = FastAPI(
    title="Insurence API",
    lifespan=mcp_app.lifespan
)

# =========================================================================
# 2. ENDPOINTS DE FASTAPI
# =========================================================================

@app.get("/")
async def root():
    """Endpoint principal para verificar que la API está funcionando."""
    return {"message": "Hello from FastAPI!"}

@app.get("/supabase-data")
async def get_supabase_data():
    """
    Lee todos los registros de la tabla 'test' en Supabase.
    """
    try:
        response = supabase.table("test").select("*").execute()
        return response.data
    except Exception as e:
        # Manejo de errores para conexiones o consultas fallidas.
        raise HTTPException(status_code=500, detail=f"Error al obtener datos de Supabase: {str(e)}")

@app.post("/insert-text")
async def insert_text(text: str):
    """
    Inserta un nuevo registro en la tabla 'test' de Supabase con el texto proporcionado.
    """
    try:
        response = supabase.table("test").insert({"text": text}).execute()
        return {"inserted": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al insertar en Supabase: {str(e)}")

# =========================================================================
# 3. ENDPOINTS DE FASTMCP (PARA LLM)
# =========================================================================

# Define los modelos de datos para las funciones de MCP.
class GetUserRequest(BaseModel):
    user_id: str = Field(..., description="The ID of the user to retrieve.")

class GetUserResponse(BaseModel):
    user_id: str
    username: str
    email: str

# Decora la función con @mcp.tool para que sea una herramienta LLM.
@mcp.tool
async def get_user_by_id(user_request: GetUserRequest) -> GetUserResponse:
    """
    Retrieves a user's information by their user ID.
    This function simulates a database query.
    """
    users = {
        "user_1": {"username": "JohnDoe", "email": "john.doe@example.com"},
        "user_2": {"username": "JaneSmith", "email": "jane.smith@example.com"}
    }
    if user_request.user_id in users:
        user_info = users[user_request.user_id]
        return GetUserResponse(
            user_id=user_request.user_id,
            username=user_info["username"],
            email=user_info["email"]
        )
    else:
        raise HTTPException(status_code=404, detail="User not found")

# =========================================================================
# 4. MONTAJE Y EJECUCIÓN
# =========================================================================

# Monta la aplicación de FastMCP bajo la ruta '/llm'.
app.mount("/llm", mcp_app)

if __name__ == "__main__":
    # Punto de entrada para ejecutar el servidor con Uvicorn.
    # El host se ha cambiado a '127.0.0.1' para un acceso local.
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
