# Usa una imagen base oficial de Python.
# python:3.10-slim es una opción ligera.
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor.
WORKDIR /app

# Copia el archivo de requisitos y los instala.
# Esto aprovecha el caché de Docker si requirements.txt no cambia.
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copia el resto de los archivos del proyecto al contenedor.
# La carpeta 'app' y el resto del contenido se copiarán en el WORKDIR '/app'.
COPY . /app

# Expone el puerto que usará FastAPI.
EXPOSE 8000

# Comando para ejecutar la aplicación.
# Se corrige la ruta del módulo para que Uvicorn encuentre 'main.py' dentro de la carpeta 'app'.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
