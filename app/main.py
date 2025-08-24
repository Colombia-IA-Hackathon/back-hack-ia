import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from supabase import create_client, Client
from fastapi import Body
import datetime
from typing import Optional
from math import radians, cos, sin, sqrt, atan2

# =========================================================================
# 1. CONFIGURACIÓN E INICIALIZACIÓN
# =========================================================================

# Inicializa el cliente de Supabase con tus credenciales.
# Es una buena práctica usar variables de entorno para las claves.
SUPABASE_URL = "https://supabase.kaiser-soft.com"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlzcyI6InN1cGFiYXNlIiwiaWF0IjoxNzU1ODM4ODAwLCJleHAiOjE5MTM2MDUyMDB9.QHME589F1zHAZRX23WX6sBaQZ_pKVT-M-1MEXWlRDQc"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Crea la instancia de FastMCP.
mcp = FastMCP(name="Insure AI MCP")

# Crea la aplicación ASGI de FastMCP. Esta aplicación gestiona el ciclo de vida
# y los endpoints de MCP.
mcp_app = mcp.http_app(path='/mcp')

# Crea la aplicación principal de FastAPI.
# Es CRUCIAL pasar el 'lifespan' del objeto mcp_app.
app = FastAPI(
    title="Insure AI API",
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

class ClientCreateRequest(BaseModel):
	nombre: str
	tipo_documento: str
	numero_documento: str
	direccion: str
	telefono: str
	email: str
	fecha_registro: str
	estado: str

@app.post("/add-client")
async def add_client(client: ClientCreateRequest = Body(...)):
	"""
	Agrega un nuevo cliente a la tabla 'clientes' en Supabase.
	"""
	# Convierte fecha_registro a tipo date (YYYY-MM-DD)
	try:
		client_data = client.model_dump()
		fecha_registro_date = datetime.date.fromisoformat(client_data["fecha_registro"])
		client_data["fecha_registro"] = fecha_registro_date.isoformat()
		response = supabase.table("Cliente").insert(client_data).execute()
		return {"inserted": response.data}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error al agregar cliente: {str(e)}")

@app.get("/get-client-by-document/{numero_documento}")
async def get_client_by_document(numero_documento: str):
	"""
	Obtiene la información de un cliente por su numero_documento.
	"""
	try:
		response = supabase.table("Cliente").select("*").eq("numero_documento", numero_documento).execute()
		if response.data:
			return response.data[0]
		else:
			raise HTTPException(status_code=404, detail="Cliente no encontrado")
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error al obtener cliente: {str(e)}")
class CultivoCreateRequest(BaseModel):
	cliente_id: int
	nombre: str
	hectareas: float
	departamento: str
	municipio: str
	latitud: float
	longitud: float
	altitud: float
	zona_altitudinal: str
	fecha_siembra: str
	estado: str

@app.post("/add-cultivo")
async def add_cultivo(cultivo: CultivoCreateRequest = Body(...)):
	"""
	Agrega un nuevo cultivo a la tabla 'Cultivo' en Supabase.
	"""
	try:
		cultivo_data = cultivo.model_dump()
		# Convierte fecha_siembra a tipo date (YYYY-MM-DD)
		fecha_siembra_date = datetime.date.fromisoformat(cultivo_data["fecha_siembra"])
		cultivo_data["fecha_siembra"] = fecha_siembra_date.isoformat()
		response = supabase.table("Cultivo").insert(cultivo_data).execute()
		return {"inserted": response.data}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error al agregar cultivo: {str(e)}")
      
class CultivoUpdateRequest(BaseModel):
	nombre: str | None = None
	hectareas: float | None = None
	departamento: str | None = None
	municipio: str | None = None
	latitud: float | None = None
	longitud: float | None = None
	altitud: float | None = None
	zona_altitudinal: str | None = None
	fecha_siembra: str | None = None
	estado: str | None = None

@app.put("/update-cultivo/{cultivo_id}")
async def update_cultivo(cultivo_id: int, cultivo: CultivoUpdateRequest = Body(...)):
	"""
	Edita la información de un cultivo existente en la tabla 'Cultivo' de Supabase.
	"""
	try:
		cultivo_data = {k: v for k, v in cultivo.model_dump().items() if v is not None}
		if "fecha_siembra" in cultivo_data and cultivo_data["fecha_siembra"]:
			fecha_siembra_date = datetime.date.fromisoformat(cultivo_data["fecha_siembra"])
			cultivo_data["fecha_siembra"] = fecha_siembra_date.isoformat()
		response = supabase.table("Cultivo").update(cultivo_data).eq("id", cultivo_id).execute()
		return {"updated": response.data}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error al actualizar cultivo: {str(e)}")
@app.get("/get-cultivos-by-cliente/{cliente_id}")
async def get_cultivos_by_cliente(cliente_id: int):
	"""
	Obtiene todos los cultivos asociados a un cliente dado su id.
	"""
	try:
		response = supabase.table("Cultivo").select("*").eq("cliente_id", cliente_id).execute()
		return response.data
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error al obtener cultivos: {str(e)}")

class PuntoEspacialRequest(BaseModel):
	latitud: float
	longitud: float

def haversine(lat1, lon1, lat2, lon2):
	R = 6371  # Radio de la Tierra en km
	dlat = radians(lat2 - lat1)
	dlon = radians(lon2 - lon1)
	a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
	c = 2 * atan2(sqrt(a), sqrt(1-a))
	return R * c

@app.post("/nearest-punto-espacial")
async def nearest_punto_espacial(request: PuntoEspacialRequest = Body(...)):
	"""
	Busca el punto espacial más cercano a la latitud y longitud proporcionadas.
	"""
	try:
		response = supabase.table("Puntos_espaciales").select("*").execute()
		puntos = response.data
		print(puntos)
		if not puntos:
			raise HTTPException(status_code=404, detail="No hay puntos espaciales en la base de datos")
		min_dist = float("inf")
		nearest = None
		for punto in puntos:
			print(punto)
			dist = haversine(
				float(request.latitud),
				float(request.longitud),
				float(punto["latitude"]),
				float(punto["longitude"])
			)
			if dist < min_dist:
				min_dist = dist
				nearest = punto
		return {"nearest": nearest, "distance_km": min_dist}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error al buscar punto espacial: {str(e)}")
@app.post("/historicos-clima")
async def get_historicos_clima(request: PuntoEspacialRequest = Body(...)):
	"""
	Consulta los 5 registros más recientes de la tabla 'Historicos_Clima' para los años 2025-2021
	en la ubicación dada (latitud, longitud).
	"""
	try:
		years = [2025, 2024, 2023, 2022, 2021]
		historicos = {}
		for year in years:
			response = supabase.table("Historicos_Clima") \
				.select("*") \
				.eq("latitude", request.latitud) \
				.eq("longitude", request.longitud) \
				.order("time", desc=True) \
				.execute()
			# Filtra por año en Python
			filtered = [row for row in response.data if "time" in row and datetime.datetime.fromisoformat(row["time"]).year == year]
			historicos[str(year)] = filtered[:5]
		return {"historicos": historicos}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error al consultar historicos: {str(e)}")
@app.get("/get-all-cultivos")
async def get_all_cultivos():
	"""
	Obtiene todos los cultivos registrados en la tabla 'Cultivo' de Supabase.
	"""
	try:
		response = supabase.table("Cultivo").select("*").execute()
		return response.data
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error al obtener cultivos: {str(e)}")


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
