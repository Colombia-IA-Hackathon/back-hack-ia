# back-hack-ia

Insure AI Proyecto desarrollado para el hackathon de Colombia IA 2025.

## Estructura del proyecto

```
DockerFile
requirements.txt
app/
    __init__.py
    main.py
    requirements.txt
    __pycache__/
        __init__.cpython-313.pyc
        main.cpython-313.pyc
```

## Descripción
Este proyecto es una aplicación Python que puede ejecutarse localmente o en un contenedor Docker. El código principal se encuentra en la carpeta `app`.

## Instalación

### Requisitos
- Python 3.13 o superior
- Docker (opcional)

### Instalación de dependencias

Ejecuta en la raíz del proyecto:
```powershell
pip install -r requirements.txt
pip install -r app/requirements.txt
```

### Ejecución

Para ejecutar la aplicación principal:
```powershell
python app/main.py
```

### Ejecución con FastAPI

Si tu proyecto utiliza FastAPI, puedes ejecutarlo con:
```powershell
uvicorn app.main:app --reload
```
Esto levantará el servidor en modo desarrollo en `http://127.0.0.1:8000`.

### Ejecución con FastMCP

Si tienes FastMCP instalado y configurado, puedes ejecutarlo con:
```powershell
fastmcp run app.main:app
```
Esto iniciará el servidor usando FastMCP.

### Uso con Docker

Para construir y ejecutar el contenedor:
```powershell
docker build -t back-hack-ia .
docker run -it back-hack-ia
```

## Autor
Brayan Medina
Leonardo Ramirez
Santiago Viana
Luis Miguel

## Licencia
Este proyecto es solo para fines educativos y de hackathon.
