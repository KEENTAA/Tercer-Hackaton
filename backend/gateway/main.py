from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
import httpx
import os

app = FastAPI(title="API Gateway - Hackaton")

# Configuración de servicios internos
EXECUTION_SERVICE_URL = os.getenv("EXECUTION_SERVICE_URL", "http://execution-service:8000")
PLAGIARISM_SERVICE_URL = os.getenv("PLAGIARISM_SERVICE_URL", "http://plagiarism-service:8000")

client = httpx.AsyncClient()

async def proxy_request(service_url: str, path: str, request: Request):
    url = f"{service_url}/{path}"
    
    # Reenviar headers, exceptuando el host
    headers = dict(request.headers)
    headers.pop("host", None)
    
    # Obtener el cuerpo de la petición
    body = await request.body()
    
    # Realizar la petición al servicio interno
    try:
        response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            params=request.query_params,
            content=body,
            timeout=60.0
        )
        
        return StreamingResponse(
            response.aiter_raw(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con el servicio: {str(e)}")

@app.api_route("/plagio/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def plagiarism_proxy(path: str, request: Request):
    return await proxy_request(PLAGIARISM_SERVICE_URL, path, request)

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def main_proxy(path: str, request: Request):
    return await proxy_request(EXECUTION_SERVICE_URL, path, request)

@app.on_event("shutdown")
async def shutdown_event():
    await client.aclose()
