# Assumes the FastAPI app from above is already defined
from fastmcp import FastMCP
from fastapi import FastAPI
from supabase import create_client, Client
from fastapi import HTTPException
import uvicorn

# 1. Crea la instancia de FastMCP primero


# 2. Define tu FastAPI app, pasando el lifespan de FastMCP
app = FastAPI(title="Insurence API", lifespan=mcp.lifespan)
mcp = FastMCP.from_fastapi(app=app)
# 3. Define tus endpoints de la API de Supabase
# Se asume que las credenciales de Supabase son correctas
SUPABASE_URL = "https://supabase.kaiser-soft.com"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlzcyI6InN1cGFiYXNlIiwiaWF0IjoxNzU1ODM4ODAwLCJleHAiOjE5MTM2MDUyMDB9.QHME589F1zHAZRX23WX6sBaQZ_pKVT-M-1MEXWlRDQc"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/supabase-data")
async def get_supabase_data():
    try:
        # Cambia 'test' por el nombre de tu tabla si es necesario
        response = supabase.table("test").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/insert-text")
async def insert_text(text: str):
    try:
        response = supabase.table("test").insert({"text": text}).execute()
        return {"inserted": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4. Monta el servidor FastMCP en la aplicación FastAPI
# El parámetro path del mount es la ruta base para todos los endpoints de FastMCP
mcp.mount(app, "/llm")

# Punto de entrada para ejecutar el servidor
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

# Ahora tienes:
# - Regular API: http://localhost:8000/
# - LLM-friendly MCP: http://localhost:8000/llm/mcp/
# Ambos servidos desde la misma aplicación FastAPI.