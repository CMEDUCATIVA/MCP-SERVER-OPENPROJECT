from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import secrets
import asyncio
import os
import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv
from pythonjsonlogger import jsonlogger

# Importar el cliente OpenProject
from openproject_mcp import OpenProjectClient

# Cargar variables de entorno
load_dotenv()

# Configurar logging (JSON o estándar según configuración)
LOG_FORMAT = os.getenv("LOG_FORMAT", "standard")  # 'json' o 'standard'
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

if LOG_FORMAT.lower() == "json":
    # Logging JSON estructurado
    log_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        rename_fields={"levelname": "level", "asctime": "timestamp"}
    )
    log_handler.setFormatter(formatter)
    logger = logging.getLogger("openproject_mcp_http")
    logger.addHandler(log_handler)
    logger.setLevel(LOG_LEVEL)
else:
    # Logging estándar
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("openproject_mcp_http")

# Cargar configuración desde .env
OPENPROJECT_URL = os.getenv("OPENPROJECT_URL")
OPENPROJECT_API_KEY = os.getenv("OPENPROJECT_API_KEY")
OPENPROJECT_PROXY = os.getenv("OPENPROJECT_PROXY")

# Configuración HTTP Server
HTTP_HOST = os.getenv("HTTP_HOST", "0.0.0.0")
HTTP_PORT = int(os.getenv("HTTP_PORT", "8000"))

# Autenticación HTTP (opcional)
HTTP_AUTH_ENABLED = os.getenv("HTTP_AUTH_ENABLED", "false").lower() == "true"
HTTP_AUTH_USERNAME = os.getenv("HTTP_AUTH_USERNAME", "admin")
HTTP_AUTH_PASSWORD = os.getenv("HTTP_AUTH_PASSWORD", "changeme")

# CORS
CORS_ENABLED = os.getenv("CORS_ENABLED", "true").lower() == "true"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Rate Limiting
RATE_LIMIT = os.getenv("RATE_LIMIT", "100/minute")

# GZIP
GZIP_ENABLED = os.getenv("GZIP_ENABLED", "true").lower() == "true"
GZIP_MIN_SIZE = int(os.getenv("GZIP_MIN_SIZE", "1000"))

# Crear cliente global
client = OpenProjectClient(
    base_url=OPENPROJECT_URL,
    api_key=OPENPROJECT_API_KEY,
    proxy=OPENPROJECT_PROXY
)

logger.info(f"OpenProject Client initialized for: {OPENPROJECT_URL}")

OPENAPI_BASE_URL = os.getenv("OPENAPI_BASE_URL", f"http://{HTTP_HOST}:{HTTP_PORT}")

# Configurar FastAPI
app = FastAPI(
    title="OpenProject MCP HTTP Adapter",
    description="API REST para acceder a todas las funcionalidades de OpenProject MCP",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Info", "description": "Información del servidor"},
        {"name": "Core", "description": "Funcionalidades principales"},
        {"name": "Projects", "description": "Gestión de proyectos"},
        {"name": "Work Packages", "description": "Gestión de work packages"},
        {"name": "Work Package Relations", "description": "Relaciones entre work packages"},
        {"name": "Users", "description": "Gestión de usuarios"},
        {"name": "Memberships", "description": "Gestión de membresías"},
        {"name": "Roles", "description": "Gestión de roles"},
        {"name": "Time Tracking", "description": "Seguimiento de tiempo"},
        {"name": "Versions", "description": "Gestión de versiones"},
        {"name": "REST Aliases", "description": "Endpoints REST simplificados"},
    ]
    ,
    servers=[{"url": OPENAPI_BASE_URL}]
)

# Configurar Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configurar CORS
if CORS_ENABLED:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Configurar GZIP
if GZIP_ENABLED:
    app.add_middleware(GZipMiddleware, minimum_size=GZIP_MIN_SIZE)

# Configurar autenticación HTTP Basic (opcional)
security = HTTPBasic(auto_error=False)

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Verificar credenciales HTTP Basic si está habilitado"""
    if not HTTP_AUTH_ENABLED:
        return True
    
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    correct_username = secrets.compare_digest(credentials.username, HTTP_AUTH_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, HTTP_AUTH_PASSWORD)
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True

# ============================================================================
# ENDPOINTS DE INFORMACIÓN
# ============================================================================

@app.get("/", tags=["Info"])
async def root():
    """Información sobre el servidor"""
    return {
        "service": "OpenProject MCP HTTP Adapter",
        "version": "1.1.0",
        "status": "running",
        "openproject_url": OPENPROJECT_URL,
        "features": {
            "authentication": HTTP_AUTH_ENABLED,
            "cors": CORS_ENABLED,
            "rate_limiting": True,
            "gzip_compression": GZIP_ENABLED
        },
        "documentation": "/docs"
    }

@app.get("/health", tags=["Info"])
@limiter.limit(RATE_LIMIT)
async def health_check(request: Request):
    """Verificar estado del servicio (no depende de OpenProject)"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "openproject-mcp-http",
    }


@app.get("/health/openproject", tags=["Info"])
@limiter.limit(RATE_LIMIT)
async def health_openproject(request: Request):
    """Verificar estado de la conexión con OpenProject"""
    try:
        await client.test_connection()
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "openproject": "connected",
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "openproject": "disconnected",
                "error": str(e),
            },
        )

# ============================================================================
# CORE - Test Connection
# ============================================================================

@app.post("/tools/test_connection", tags=["Core"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def test_connection(request: Request):
    """1. Probar conexión con OpenProject"""
    try:
        result = await client.test_connection()
        return result
    except Exception as e:
        logger.error(f"Error in test_connection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PROJECTS
# ============================================================================

@app.post("/tools/list_projects", tags=["Projects"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def list_projects(
    request: Request,
    active_only: bool = True
):
    """2. Listar TODOS los proyectos (SIEMPRE devuelve todos sin paginación)"""
    try:
        # SIEMPRE usar modo de recuperación completa
        # El cliente MCP ahora siempre usa auto-paginación internamente
        logger.info(f"Starting FULL retrieval of ALL projects (active_only={active_only})")
        
        result = await client.get_projects(
            active_only=active_only
        )
        
        projects = result.get("_embedded", {}).get("elements", [])
        total = result.get("total", 0)
        
        logger.info(f"FULL retrieval complete: {len(projects)} projects retrieved (total: {total})")
        
        # Construir respuesta con TODOS los proyectos
        response = {
            "_type": "Collection",
            "total": total,
            "count": len(projects),
            "pageSize": len(projects),  # <-- IMPORTANTE: pageSize = total de elementos
            "offset": 1,
            "_embedded": {
                "elements": projects
            },
            "_retrieval_info": {
                "mode": "full_retrieval",
                "total_retrieved": len(projects),
                "note": "All projects retrieved successfully"
            }
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error in list_projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/get_project", tags=["Projects"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def get_project(request: Request, project_id: int):
    """24. Obtener información detallada de un proyecto"""
    try:
        result = await client.get_project(project_id=project_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/create_project", tags=["Projects"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def create_project(
    request: Request,
    name: str,
    identifier: str,
    description: Optional[str] = None,
    public: Optional[bool] = None,
    status: Optional[str] = None,
    parent_id: Optional[int] = None
):
    """21. Crear un nuevo proyecto"""
    try:
        result = await client.create_project(
            name=name,
            identifier=identifier,
            description=description,
            public=public,
            status=status,
            parent_id=parent_id
        )
        return result
    except Exception as e:
        logger.error(f"Error in create_project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/update_project", tags=["Projects"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def update_project(
    request: Request,
    project_id: int,
    name: Optional[str] = None,
    identifier: Optional[str] = None,
    description: Optional[str] = None,
    public: Optional[bool] = None,
    status: Optional[str] = None,
    parent_id: Optional[int] = None
):
    """22. Actualizar un proyecto existente"""
    try:
        result = await client.update_project(
            project_id=project_id,
            name=name,
            identifier=identifier,
            description=description,
            public=public,
            status=status,
            parent_id=parent_id
        )
        return result
    except Exception as e:
        logger.error(f"Error in update_project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/delete_project", tags=["Projects"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def delete_project(request: Request, project_id: int):
    """23. Eliminar un proyecto"""
    try:
        result = await client.delete_project(project_id=project_id)
        return result
    except Exception as e:
        logger.error(f"Error in delete_project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# WORK PACKAGES
# ============================================================================

@app.post("/tools/list_work_packages", tags=["Work Packages"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def list_work_packages(
    request: Request,
    project_id: int,
    status: str = "open",
    offset: Optional[int] = None,
    page_size: Optional[int] = None,
    full_retrieval: bool = True
):
    """3. Listar TODOS los work packages (requiere project_id y recupera todo)"""
    try:
        # Construir filtros
        filters = []
        if project_id:
            filters.append({
                "project": {
                    "operator": "=",
                    "values": [str(project_id)]
                }
            })
        
        if status == "open":
            filters.append({
                "status": {
                    "operator": "o",
                    "values": []
                }
            })
        elif status == "closed":
            filters.append({
                "status": {
                    "operator": "c",
                    "values": []
                }
            })
        
        # SIEMPRE usar modo de recuperación completa, NO pasar parámetros de paginación al cliente MCP
        # Esto permite que el cliente MCP use auto-paginación
        logger.info(f"Starting FULL retrieval of ALL work packages (project_id={project_id}, status={status})")
        
        result = await client.get_work_packages(
            project_id=project_id,
            filters=filters if filters else None,
            # NO pasar offset ni page_size para activar auto-paginación en el cliente MCP
            offset=None,
            page_size=None
        )
        
        work_packages = result.get("_embedded", {}).get("elements", [])
        total = result.get("total", 0)
        
        logger.info(f"FULL retrieval complete: {len(work_packages)} work packages retrieved (total: {total})")
        
        # Construir respuesta con TODOS los work packages
        response = {
            "_type": "Collection",
            "total": total,
            "count": len(work_packages),
            "pageSize": len(work_packages),
            "offset": 1,
            "_embedded": {
                "elements": work_packages
            },
            "_retrieval_info": {
                "mode": "full_retrieval",
                "total_retrieved": len(work_packages),
                "note": "All work packages retrieved successfully"
            }
        }
        
        return response
    except Exception as e:
        logger.error(f"Error in list_work_packages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/get_work_package", tags=["Work Packages"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def get_work_package(request: Request, work_package_id: int):
    """11. Obtener información detallada de un work package"""
    try:
        result = await client.get_work_package(work_package_id=work_package_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_work_package: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/list_work_package_activities", tags=["Work Package Relations"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def list_work_package_activities(request: Request, work_package_id: int):
    """11b. Listar actividades de un work package"""
    try:
        result = await client.get_work_package_activities(work_package_id=work_package_id)
        return result
    except Exception as e:
        logger.error(f"Error in list_work_package_activities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/add_work_package_comment", tags=["Work Package Relations"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def add_work_package_comment(
    request: Request,
    work_package_id: int,
    comment: str,
    internal: bool = False,
    notify: Optional[bool] = None
):
    """11c. Agregar comentario (actividad) a un work package"""
    try:
        result = await client.add_work_package_comment(
            work_package_id=work_package_id,
            comment=comment,
            internal=internal,
            notify=notify
        )
        return result
    except Exception as e:
        logger.error(f"Error in add_work_package_comment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/create_work_package_reminder", tags=["Work Package Relations"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def create_work_package_reminder(
    request: Request,
    work_package_id: int,
    remind_at: str,
    note: Optional[str] = None
):
    """11d. Crear recordatorio de un work package"""
    try:
        result = await client.create_work_package_reminder(
            work_package_id=work_package_id,
            remind_at=remind_at,
            note=note
        )
        return result
    except Exception as e:
        logger.error(f"Error in create_work_package_reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/list_work_package_reminders", tags=["Work Package Relations"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def list_work_package_reminders(request: Request, work_package_id: int):
    """11g. Listar recordatorios de un work package"""
    try:
        result = await client.list_work_package_reminders(work_package_id=work_package_id)
        return result
    except Exception as e:
        logger.error(f"Error in list_work_package_reminders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/list_reminders", tags=["Work Package Relations"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def list_reminders(request: Request):
    """11h. Listar recordatorios activos del usuario"""
    try:
        result = await client.list_reminders()
        return result
    except Exception as e:
        logger.error(f"Error in list_reminders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/tools/delete_reminder", tags=["Work Package Relations"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def delete_reminder(request: Request, reminder_id: int):
    """11e. Eliminar recordatorio"""
    try:
        result = await client.delete_reminder(reminder_id=reminder_id)
        return {"deleted": result, "reminder_id": reminder_id}
    except Exception as e:
        logger.error(f"Error in delete_reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/tools/update_reminder", tags=["Work Package Relations"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def update_reminder(
    request: Request,
    reminder_id: int,
    remind_at: Optional[str] = None,
    note: Optional[str] = None
):
    """11f. Actualizar recordatorio"""
    try:
        if remind_at is None and note is None:
            raise HTTPException(status_code=400, detail="remind_at or note is required")
        result = await client.update_reminder(
            reminder_id=reminder_id,
            remind_at=remind_at,
            note=note
        )
        return result
    except Exception as e:
        logger.error(f"Error in update_reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/create_work_package", tags=["Work Packages"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def create_work_package(
    request: Request,
    project_id: int,
    subject: str,
    type_id: int,
    description: Optional[str] = None,
    priority_id: Optional[int] = None,
    assignee_id: Optional[int] = None
):
    """5. Crear un nuevo work package"""
    try:
        payload = {
            "project": project_id,
            "subject": subject,
            "type": type_id,
        }

        if description is not None:
            payload["description"] = description
        if priority_id is not None:
            payload["priority_id"] = priority_id
        if assignee_id is not None:
            payload["assignee_id"] = assignee_id

        logger.info(f"payload for create_work_package: {payload}")
        result = await client.create_work_package(payload)
        return result
    except Exception as e:
        logger.error(f"Error in create_work_package: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/update_work_package", tags=["Work Packages"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def update_work_package(
    request: Request,
    work_package_id: int,
    subject: Optional[str] = None,
    description: Optional[str] = None,
    type_id: Optional[int] = None,
    status_id: Optional[int] = None,
    priority_id: Optional[int] = None,
    assignee_id: Optional[int] = None,
    percentage_done: Optional[int] = None
):
    """12. Actualizar un work package existente"""
    try:
        result = await client.update_work_package(
            work_package_id=work_package_id,
            subject=subject,
            description=description,
            type_id=type_id,
            status_id=status_id,
            priority_id=priority_id,
            assignee_id=assignee_id,
            percentage_done=percentage_done
        )
        return result
    except Exception as e:
        logger.error(f"Error in update_work_package: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/delete_work_package", tags=["Work Packages"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def delete_work_package(request: Request, work_package_id: int):
    """13. Eliminar un work package"""
    try:
        result = await client.delete_work_package(work_package_id=work_package_id)
        return result
    except Exception as e:
        logger.error(f"Error in delete_work_package: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/list_types", tags=["Work Packages"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def list_types(request: Request, project_id: Optional[int] = None):
    """4. Listar tipos de work packages"""
    try:
        result = await client.get_types()
        return result
    except Exception as e:
        logger.error(f"Error in list_types: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/list_statuses", tags=["Work Packages"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def list_statuses(request: Request):
    """9. Listar estados de work packages"""
    try:
        result = await client.get_statuses()
        return result
    except Exception as e:
        logger.error(f"Error in list_statuses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/list_priorities", tags=["Work Packages"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def list_priorities(request: Request):
    """10. Listar prioridades de work packages"""
    try:
        result = await client.get_priorities()
        return result
    except Exception as e:
        logger.error(f"Error in list_priorities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# WORK PACKAGE RELATIONS
# ============================================================================

@app.post("/tools/set_work_package_parent", tags=["Work Package Relations"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def set_work_package_parent(request: Request, work_package_id: int, parent_id: int):
    """33. Establecer relación padre-hijo entre work packages"""
    try:
        result = await client.set_work_package_parent(
            work_package_id=work_package_id,
            parent_id=parent_id
        )
        return result
    except Exception as e:
        logger.error(f"Error in set_work_package_parent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/remove_work_package_parent", tags=["Work Package Relations"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def remove_work_package_parent(request: Request, work_package_id: int):
    """34. Eliminar relación padre de un work package"""
    try:
        result = await client.remove_work_package_parent(work_package_id=work_package_id)
        return result
    except Exception as e:
        logger.error(f"Error in remove_work_package_parent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/list_work_package_children", tags=["Work Package Relations"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def list_work_package_children(
    request: Request,
    parent_id: int,
    include_descendants: bool = False
):
    """35. Listar work packages hijos de un padre"""
    try:
        result = await client.get_work_package_children(
            parent_id=parent_id,
            include_descendants=include_descendants
        )
        return result
    except Exception as e:
        logger.error(f"Error in list_work_package_children: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/create_work_package_relation", tags=["Work Package Relations"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def create_work_package_relation(
    request: Request,
    from_id: int,
    to_id: int,
    relation_type: str,
    lag: Optional[int] = None,
    description: Optional[str] = None
):
    """36. Crear relación entre work packages"""
    try:
        result = await client.create_work_package_relation(
            from_id=from_id,
            to_id=to_id,
            relation_type=relation_type,
            lag=lag,
            description=description
        )
        return result
    except Exception as e:
        logger.error(f"Error in create_work_package_relation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/list_work_package_relations", tags=["Work Package Relations"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def list_work_package_relations(
    request: Request,
    work_package_id: Optional[int] = None,
    relation_type: Optional[str] = None
):
    """37. Listar relaciones de work packages"""
    try:
        result = await client.get_work_package_relations(
            work_package_id=work_package_id,
            relation_type=relation_type
        )
        return result
    except Exception as e:
        logger.error(f"Error in list_work_package_relations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/get_work_package_relation", tags=["Work Package Relations"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def get_work_package_relation(request: Request, relation_id: int):
    """40. Obtener información detallada de una relación"""
    try:
        result = await client.get_work_package_relation(relation_id=relation_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_work_package_relation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/update_work_package_relation", tags=["Work Package Relations"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def update_work_package_relation(
    request: Request,
    relation_id: int,
    relation_type: Optional[str] = None,
    lag: Optional[int] = None,
    description: Optional[str] = None
):
    """38. Actualizar una relación existente"""
    try:
        result = await client.update_work_package_relation(
            relation_id=relation_id,
            relation_type=relation_type,
            lag=lag,
            description=description
        )
        return result
    except Exception as e:
        logger.error(f"Error in update_work_package_relation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/delete_work_package_relation", tags=["Work Package Relations"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def delete_work_package_relation(request: Request, relation_id: int):
    """39. Eliminar una relación"""
    try:
        result = await client.delete_work_package_relation(relation_id=relation_id)
        return result
    except Exception as e:
        logger.error(f"Error in delete_work_package_relation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# USERS
# ============================================================================

@app.post("/tools/list_users", tags=["Users"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def list_users(request: Request, active_only: bool = True):
    """6. Listar usuarios"""
    try:
        result = await client.get_users(active_only=active_only)
        return result
    except Exception as e:
        logger.error(f"Error in list_users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/get_user", tags=["Users"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def get_user(request: Request, user_id: int):
    """7. Obtener información de un usuario"""
    try:
        result = await client.get_user(user_id=user_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MEMBERSHIPS
# ============================================================================

@app.post("/tools/list_memberships", tags=["Memberships"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def list_memberships(
    request: Request,
    project_id: Optional[int] = None,
    user_id: Optional[int] = None
):
    """8. Listar membresías de proyectos"""
    try:
        filters = []
        if project_id:
            filters.append({"project": {"operator": "=", "values": [str(project_id)]}})
        if user_id:
            filters.append({"principal": {"operator": "=", "values": [str(user_id)]}})
        
        result = await client.get_memberships(
            filters=filters if filters else None, full_retrieval=True
        )
        return result
    except Exception as e:
        logger.error(f"Error in list_memberships: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/get_membership", tags=["Memberships"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def get_membership(request: Request, membership_id: int):
    """28. Obtener información de una membresía"""
    try:
        result = await client.get_membership(membership_id=membership_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_membership: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/create_membership", tags=["Memberships"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def create_membership(
    request: Request,
    project_id: int,
    user_id: Optional[int] = None,
    group_id: Optional[int] = None,
    role_id: Optional[int] = None,
    role_ids: Optional[List[int]] = None,
    notification_message: Optional[str] = None
):
    """25. Crear una nueva membresía"""
    try:
        result = await client.create_membership(
            project_id=project_id,
            user_id=user_id,
            group_id=group_id,
            role_ids=role_ids or ([role_id] if role_id else None),
            notification_message=notification_message
        )
        return result
    except Exception as e:
        logger.error(f"Error in create_membership: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/update_membership", tags=["Memberships"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def update_membership(
    request: Request,
    membership_id: int,
    role_id: Optional[int] = None,
    role_ids: Optional[List[int]] = None,
    notification_message: Optional[str] = None
):
    """26. Actualizar una membresía"""
    try:
        result = await client.update_membership(
            membership_id=membership_id,
            role_ids=role_ids or ([role_id] if role_id else None),
            notification_message=notification_message
        )
        return result
    except Exception as e:
        logger.error(f"Error in update_membership: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/delete_membership", tags=["Memberships"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def delete_membership(request: Request, membership_id: int):
    """27. Eliminar una membresía"""
    try:
        result = await client.delete_membership(membership_id=membership_id)
        return result
    except Exception as e:
        logger.error(f"Error in delete_membership: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/list_project_members", tags=["Memberships"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def list_project_members(request: Request, project_id: int):
    """29. Listar miembros de un proyecto"""
    try:
        filters = [{"project": {"operator": "=", "values": [str(project_id)]}}]
        result = await client.get_memberships(filters=filters, full_retrieval=True)
        return result
    except Exception as e:
        logger.error(f"Error in list_project_members: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/list_user_projects", tags=["Memberships"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def list_user_projects(request: Request, user_id: int):
    """30. Listar proyectos de un usuario"""
    try:
        result = await client.get_memberships(user_id=user_id, full_retrieval=True)
        return result
    except Exception as e:
        logger.error(f"Error in list_user_projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ROLES
# ============================================================================

@app.post("/tools/list_roles", tags=["Roles"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def list_roles(request: Request):
    """31. Listar roles disponibles"""
    try:
        result = await client.get_roles()
        return result
    except Exception as e:
        logger.error(f"Error in list_roles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/get_role", tags=["Roles"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def get_role(request: Request, role_id: int):
    """32. Obtener información de un rol"""
    try:
        result = await client.get_role(role_id=role_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_role: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TIME TRACKING
# ============================================================================

@app.post("/tools/list_time_entries", tags=["Time Tracking"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def list_time_entries(
    request: Request,
    work_package_id: Optional[int] = None,
    user_id: Optional[int] = None
):
    """14. Listar entradas de tiempo"""
    try:
        filters = []
        if work_package_id:
            filters.append({"work_package": {"operator": "=", "values": [str(work_package_id)]}})
        if user_id:
            filters.append({"user": {"operator": "=", "values": [str(user_id)]}})
        
        result = await client.get_time_entries(filters=filters if filters else None)
        return result
    except Exception as e:
        logger.error(f"Error in list_time_entries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/create_time_entry", tags=["Time Tracking"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def create_time_entry(
    request: Request,
    work_package_id: int,
    hours: float,
    spent_on: str,
    comment: Optional[str] = None,
    activity_id: Optional[int] = None
):
    """15. Crear entrada de tiempo"""
    try:
        result = await client.create_time_entry(
            work_package_id=work_package_id,
            hours=hours,
            spent_on=spent_on,
            comment=comment,
            activity_id=activity_id
        )
        return result
    except Exception as e:
        logger.error(f"Error in create_time_entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/update_time_entry", tags=["Time Tracking"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def update_time_entry(
    request: Request,
    time_entry_id: int,
    hours: Optional[float] = None,
    spent_on: Optional[str] = None,
    comment: Optional[str] = None,
    activity_id: Optional[int] = None
):
    """16. Actualizar entrada de tiempo"""
    try:
        result = await client.update_time_entry(
            time_entry_id=time_entry_id,
            hours=hours,
            spent_on=spent_on,
            comment=comment,
            activity_id=activity_id
        )
        return result
    except Exception as e:
        logger.error(f"Error in update_time_entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/delete_time_entry", tags=["Time Tracking"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def delete_time_entry(request: Request, time_entry_id: int):
    """17. Eliminar entrada de tiempo"""
    try:
        result = await client.delete_time_entry(time_entry_id=time_entry_id)
        return result
    except Exception as e:
        logger.error(f"Error in delete_time_entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/list_time_entry_activities", tags=["Time Tracking"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def list_time_entry_activities(request: Request):
    """18. Listar actividades de time entries (con IDs predefinidos)"""
    try:
        result = await client.get_time_entry_activities()
        return result
    except Exception as e:
        logger.error(f"Error in list_time_entry_activities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# VERSIONS
# ============================================================================

@app.post("/tools/list_versions", tags=["Versions"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def list_versions(request: Request, project_id: Optional[int] = None):
    """19. Listar versiones/hitos"""
    try:
        filters = []
        if project_id:
            filters.append({"project": {"operator": "=", "values": [str(project_id)]}})
        
        result = await client.get_versions(filters=filters if filters else None)
        return result
    except Exception as e:
        logger.error(f"Error in list_versions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/create_version", tags=["Versions"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def create_version(
    request: Request,
    project_id: int,
    name: str,
    description: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None
):
    """20. Crear una versión/hito"""
    try:
        result = await client.create_version(
            project_id=project_id,
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            status=status
        )
        return result
    except Exception as e:
        logger.error(f"Error in create_version: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# REST ALIASES - Endpoints estilo REST más simples
# ============================================================================

@app.get("/api/v1/projects", tags=["REST Aliases"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def rest_list_projects(request: Request, active: bool = True):
    """Alias REST: Listar proyectos"""
    # Llamar directamente sin parámetros de paginación para forzar recuperación completa
    return await list_projects(request, active_only=active)

@app.post("/api/v1/projects", tags=["REST Aliases"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def rest_create_project(
    request: Request,
    name: str,
    identifier: str,
    description: Optional[str] = None,
    public: Optional[bool] = None
):
    """Alias REST: Crear proyecto"""
    return await create_project(request, name, identifier, description, public)

@app.get("/api/v1/projects/{project_id}", tags=["REST Aliases"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def rest_get_project(request: Request, project_id: int):
    """Alias REST: Obtener proyecto específico"""
    return await get_project(request, project_id)

@app.put("/api/v1/projects/{project_id}", tags=["REST Aliases"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def rest_update_project(
    request: Request,
    project_id: int,
    name: Optional[str] = None,
    identifier: Optional[str] = None,
    description: Optional[str] = None
):
    """Alias REST: Actualizar proyecto"""
    return await update_project(request, project_id, name, identifier, description)

@app.delete("/api/v1/projects/{project_id}", tags=["REST Aliases"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def rest_delete_project(request: Request, project_id: int):
    """Alias REST: Eliminar proyecto"""
    return await delete_project(request, project_id)

@app.get("/api/v1/users", tags=["REST Aliases"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def rest_list_users(request: Request, active: bool = True):
    """Alias REST: Listar usuarios"""
    return await list_users(request, active)

@app.get("/api/v1/users/{user_id}", tags=["REST Aliases"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def rest_get_user(request: Request, user_id: int):
    """Alias REST: Obtener usuario específico"""
    return await get_user(request, user_id)

@app.get("/api/v1/workpackages", tags=["REST Aliases"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def rest_list_workpackages(
    request: Request,
    project_id: int,
    status: str = "open"
):
    """Alias REST: Listar work packages"""
    return await list_work_packages(request, project_id, status)

@app.post("/api/v1/workpackages", tags=["REST Aliases"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def rest_create_workpackage(
    request: Request,
    project_id: int,
    subject: str,
    type_id: int,
    description: Optional[str] = None,
    priority_id: Optional[int] = None,
    assignee_id: Optional[int] = None
):
    """Alias REST: Crear work package"""
    return await create_work_package(request, project_id, subject, type_id, description, priority_id, assignee_id)

@app.get("/api/v1/workpackages/{work_package_id}", tags=["REST Aliases"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def rest_get_workpackage(request: Request, work_package_id: int):
    """Alias REST: Obtener work package específico"""
    return await get_work_package(request, work_package_id)

@app.get("/api/v1/workpackages/{work_package_id}/activities", tags=["Work Package Relations"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def rest_list_workpackage_activities(request: Request, work_package_id: int):
    """Alias REST: Listar actividades de un work package"""
    return await list_work_package_activities(request, work_package_id)

@app.post("/api/v1/workpackages/{work_package_id}/activities", tags=["Work Package Relations"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def rest_add_workpackage_comment(
    request: Request,
    work_package_id: int,
    comment: str,
    internal: bool = False,
    notify: Optional[bool] = None
):
    """Alias REST: Agregar comentario a un work package"""
    return await add_work_package_comment(
        request,
        work_package_id=work_package_id,
        comment=comment,
        internal=internal,
        notify=notify
    )

@app.post("/api/v1/workpackages/{work_package_id}/reminders", tags=["Work Package Relations"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def rest_create_workpackage_reminder(
    request: Request,
    work_package_id: int,
    remind_at: str,
    note: Optional[str] = None
):
    """Alias REST: Crear recordatorio de un work package"""
    return await create_work_package_reminder(
        request,
        work_package_id=work_package_id,
        remind_at=remind_at,
        note=note
    )

@app.get("/api/v1/workpackages/{work_package_id}/reminders", tags=["Work Package Relations"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def rest_list_workpackage_reminders(request: Request, work_package_id: int):
    """Alias REST: Listar recordatorios de un work package"""
    return await list_work_package_reminders(request, work_package_id)

@app.get("/api/v1/reminders", tags=["Work Package Relations"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def rest_list_reminders(request: Request):
    """Alias REST: Listar recordatorios activos del usuario"""
    return await list_reminders(request)

@app.delete("/api/v1/reminders/{reminder_id}", tags=["Work Package Relations"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def rest_delete_reminder(request: Request, reminder_id: int):
    """Alias REST: Eliminar recordatorio"""
    return await delete_reminder(request, reminder_id)

@app.patch("/api/v1/reminders/{reminder_id}", tags=["Work Package Relations"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def rest_update_reminder(
    request: Request,
    reminder_id: int,
    remind_at: Optional[str] = None,
    note: Optional[str] = None
):
    """Alias REST: Actualizar recordatorio"""
    return await update_reminder(request, reminder_id, remind_at, note)

@app.put("/api/v1/workpackages/{work_package_id}", tags=["REST Aliases"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def rest_update_workpackage(
    request: Request,
    work_package_id: int,
    subject: Optional[str] = None,
    description: Optional[str] = None,
    status_id: Optional[int] = None,
    priority_id: Optional[int] = None
):
    """Alias REST: Actualizar work package"""
    return await update_work_package(request, work_package_id, subject, description, None, status_id, priority_id)

@app.delete("/api/v1/workpackages/{work_package_id}", tags=["REST Aliases"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def rest_delete_workpackage(request: Request, work_package_id: int):
    """Alias REST: Eliminar work package"""
    return await delete_work_package(request, work_package_id)

@app.get("/api/v1/roles", tags=["REST Aliases"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def rest_list_roles(request: Request):
    """Alias REST: Listar roles"""
    return await list_roles(request)

@app.get("/api/v1/memberships", tags=["REST Aliases"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def rest_list_memberships(
    request: Request,
    project_id: Optional[int] = None,
    user_id: Optional[int] = None
):
    """Alias REST: Listar membresías"""
    return await list_memberships(request, project_id, user_id)

@app.get("/api/v1/time-entries", tags=["REST Aliases"], dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def rest_list_time_entries(
    request: Request,
    work_package_id: Optional[int] = None,
    user_id: Optional[int] = None
):
    """Alias REST: Listar entradas de tiempo"""
    return await list_time_entries(request, work_package_id, user_id)

# ============================================================================
# ENDPOINT GENÉRICO (Compatibilidad)
# ============================================================================

@app.post("/query", dependencies=[Depends(verify_credentials)])
@limiter.limit(RATE_LIMIT)
async def query(request: Request):
    """
    Endpoint genérico para compatibilidad con el formato original.
    Redirige a los endpoints específicos.
    """
    data = await request.json()
    tool = data.get("tool")
    params = data.get("params", {})
    
    # Mapeo de herramientas
    if tool == "test_connection":
        return await test_connection(request)
    elif tool == "list_projects":
        # Llamar directamente sin parámetros de paginación para forzar recuperación completa
        return await list_projects(
            request,
            active_only=params.get("active_only", True)
        )
    elif tool == "list_users":
        return await list_users(request, params.get("active_only", True))
    elif tool == "list_work_packages":
        project_id = params.get("project_id")
        if project_id is None:
            raise HTTPException(status_code=400, detail="project_id is required")
        return await list_work_packages(
            request,
            project_id=project_id,
            status=params.get("status", "open")
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unknown tool: {tool}")

# ============================================================================
# INICIALIZACIÓN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("✅ OpenProject MCP HTTP Adapter iniciado")
    logger.info(f"📍 Conectado a: {OPENPROJECT_URL}")
    logger.info(f"🔐 Autenticación HTTP: {'Habilitada' if HTTP_AUTH_ENABLED else 'Deshabilitada'}")
    logger.info(f"🌐 CORS: {'Habilitado' if CORS_ENABLED else 'Deshabilitado'}")
    logger.info(f"⚡ Rate limit: {RATE_LIMIT}")
    logger.info(f"🚀 Iniciando servidor en http://{HTTP_HOST}:{HTTP_PORT}")
    logger.info(f"📚 Documentación disponible en http://{HTTP_HOST}:{HTTP_PORT}/docs")
    
    if GZIP_ENABLED:
        logger.info(f"Compresión GZIP habilitada (mínimo {GZIP_MIN_SIZE}B)")
    
    uvicorn.run(
        app,
        host=HTTP_HOST,
        port=HTTP_PORT,
        log_level=LOG_LEVEL.lower()
    )
