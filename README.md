# OpenProject MCP Server v1.1.0

**Servidor HTTP REST para integración con OpenProject mediante Model Context Protocol**

[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/yourusername/openproject-mcp-server)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal.svg)](https://fastapi.tiangolo.com/)

---

## 📋 Índice

- [Descripción](#-descripción)
- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación Rápida](#-instalación-rápida)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [API Endpoints](#-api-endpoints)
- [Mantenimiento](#-mantenimiento)
- [Troubleshooting](#-troubleshooting)
- [Documentación Detallada](#-documentación-detallada)

---

## 🎯 Descripción

OpenProject MCP Server es un adaptador HTTP REST que proporciona acceso completo a la API de OpenProject v3 mediante el protocolo MCP (Model Context Protocol). Permite la integración sencilla con OpenProject desde cualquier cliente HTTP.

**Servidor de producción:** `https://cmproyectos.cmeducativa.es`

---

## ✨ Características

### 🔧 Funcionalidades Core
- ✅ **52+ endpoints** para gestión completa de OpenProject
- ✅ **REST Aliases** - Endpoints simplificados estilo RESTful
- ✅ **Documentación interactiva** - Swagger UI y ReDoc
- ✅ **OpenAPI 3.1** - Especificación estándar

### 🔐 Seguridad
- ✅ **HTTP Basic Auth** - Autenticación opcional configurable
- ✅ **CORS** - Control de orígenes cruzados
- ✅ **Rate Limiting** - Protección contra abuso (100 req/min)

### ⚡ Performance
- ✅ **Compresión GZIP** - Respuestas optimizadas (>1KB)
- ✅ **Async/Await** - Operaciones asíncronas
- ✅ **Connection pooling** - Reutilización de conexiones

### 📊 Observabilidad
- ✅ **Logs estructurados** - JSON logging opcional
- ✅ **Health checks** - Endpoint de monitoreo
- ✅ **Métricas** - Estadísticas de uso

---

## 📋 Requisitos

### Sistema Operativo
- **Linux:** Ubuntu 20.04+, Debian 10+, CentOS 8+
- **Python:** 3.10 o superior
- **Memoria:** Mínimo 512MB RAM
- **Disco:** 500MB libres

### Dependencias del Sistema
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip -y
```

---

## 🚀 Instalación Rápida

### 1. Preparar el entorno

```bash
# Ir al directorio del proyecto
cd /home/tuusuario/openproject-mcp-server

# Crear entorno virtual
python3 -m venv .venv

# Activar entorno virtual
source .venv/bin/activate
```

### 2. Instalar dependencias

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar desde requirements.txt
pip install -r requirements.txt
```

**Dependencias principales:**
- `mcp>=1.0.0` - Model Context Protocol
- `fastapi>=0.104.0` - Framework web
- `uvicorn>=0.24.0` - Servidor ASGI
- `aiohttp>=3.8.0` - Cliente HTTP asíncrono
- `slowapi>=0.1.9` - Rate limiting
- `python-json-logger>=2.0.7` - Logging estructurado

### 3. Configurar variables de entorno

```bash
# Copiar ejemplo de configuración
cp env_example.txt .env

# Editar configuración
nano .env
```

**Configuración mínima requerida:**
```ini
OPENPROJECT_URL=https://tu-openproject.com
OPENPROJECT_API_KEY=tu_api_key_aqui
```

### 4. Probar el servidor

```bash
# Ejecutar servidor manualmente
python server_http.py
```

**Acceder a:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health Check: `http://localhost:8000/health`

---

## ⚙️ Configuración

### Variables de Entorno (.env)

```ini
# ============================================================================
# OPENPROJECT CONNECTION
# ============================================================================
OPENPROJECT_URL=https://cmproyectos.cmeducativa.es
OPENPROJECT_API_KEY=tu_api_key_secreta_aqui
OPENPROJECT_PROXY=  # Opcional, ej: http://proxy.company.com:8080

# ============================================================================
# HTTP SERVER
# ============================================================================
HTTP_HOST=0.0.0.0        # 0.0.0.0 para todas las interfaces
HTTP_PORT=8000            # Puerto del servidor

# ============================================================================
# SEGURIDAD (Opcional)
# ============================================================================
HTTP_AUTH_ENABLED=false   # true para habilitar autenticación
HTTP_AUTH_USERNAME=admin
HTTP_AUTH_PASSWORD=changeme_secure_password

# ============================================================================
# CORS (Cross-Origin Resource Sharing)
# ============================================================================
CORS_ENABLED=true
CORS_ORIGINS=*           # O dominios específicos separados por comas
                         # Ejemplo: https://app1.com,https://app2.com

# ============================================================================
# RATE LIMITING
# ============================================================================
RATE_LIMIT=100/minute    # Formato: número/periodo (second, minute, hour, day)

# ============================================================================
# COMPRESIÓN
# ============================================================================
GZIP_ENABLED=true
GZIP_MIN_SIZE=1000       # Tamaño mínimo en bytes para comprimir

# ============================================================================
# LOGGING
# ============================================================================
LOG_LEVEL=INFO           # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=standard      # 'standard' o 'json'
```

### Configuración de Producción

Para entornos de producción, se recomienda:

```ini
# Seguridad
HTTP_AUTH_ENABLED=true
HTTP_AUTH_USERNAME=admin_produccion
HTTP_AUTH_PASSWORD=contraseña_muy_segura_aqui

# CORS restrictivo
CORS_ORIGINS=https://tu-app.com,https://tu-dashboard.com

# Rate limiting más estricto
RATE_LIMIT=50/minute

# Logging JSON para herramientas de monitoreo
LOG_FORMAT=json
LOG_LEVEL=WARNING
```

---

## 🎮 Uso

### Documentación Interactiva

**Swagger UI (Recomendado para pruebas):**
```
http://tu-servidor:8000/docs
```
- Interfaz gráfica completa
- Prueba endpoints en tiempo real
- Documentación de parámetros
- Ejemplos de respuestas

**ReDoc (Recomendado para consulta):**
```
http://tu-servidor:8000/redoc
```
- Documentación limpia y organizada
- Búsqueda de endpoints
- Exportar especificación

**OpenAPI JSON:**
```
http://tu-servidor:8000/openapi.json
```
- Especificación OpenAPI 3.1
- Para generación de clientes
- Importar en Postman/Insomnia

### Ejemplos de Uso

#### Con curl

```bash
# Test de conexión
curl -X POST http://localhost:8000/tools/test_connection

# Listar proyectos activos
curl -X POST http://localhost:8000/tools/list_projects

# Obtener proyecto específico
curl -X POST "http://localhost:8000/tools/get_project?project_id=1"

# Crear work package
curl -X POST "http://localhost:8000/tools/create_work_package" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "subject": "Nueva tarea",
    "type_id": 1,
    "description": "Descripción de la tarea"
  }'

# REST Alias - Listar proyectos (GET)
curl http://localhost:8000/api/v1/projects

# Con autenticación HTTP Basic
curl -u admin:password http://localhost:8000/api/v1/projects
```

#### Con Python

```python
import requests

# Configuración
BASE_URL = "http://localhost:8000"
AUTH = ("admin", "password")  # Si HTTP_AUTH_ENABLED=true

# Test de conexión
response = requests.post(f"{BASE_URL}/tools/test_connection")
print(response.json())

# Listar proyectos
response = requests.post(
    f"{BASE_URL}/tools/list_projects",
    auth=AUTH  # Solo si está habilitada la autenticación
)
projects = response.json()

print(f"✅ Proyectos encontrados: {len(projects)}")
for project in projects:
    print(f"  - [{project['id']}] {project['name']}")

# Crear work package
data = {
    "project_id": 1,
    "subject": "Tarea desde Python",
    "type_id": 1,
    "description": "Creada mediante API"
}

response = requests.post(
    f"{BASE_URL}/tools/create_work_package",
    params=data,
    auth=AUTH
)

if response.status_code == 200:
    wp = response.json()
    print(f"✅ Work package creado: #{wp['id']}")
else:
    print(f"❌ Error: {response.status_code}")
```

#### Con JavaScript/Node.js

```javascript
const axios = require('axios');

const baseURL = 'http://localhost:8000';
const auth = {
  username: 'admin',
  password: 'password'
};

// Listar proyectos
async function listProjects() {
  try {
    const response = await axios.post(
      `${baseURL}/tools/list_projects`,
      {},
      { auth }
    );
    
    console.log(`✅ Proyectos: ${response.data.length}`);
    response.data.forEach(project => {
      console.log(`  - [${project.id}] ${project.name}`);
    });
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

// Crear work package
async function createWorkPackage() {
  try {
    const response = await axios.post(
      `${baseURL}/tools/create_work_package`,
      {},
      {
        params: {
          project_id: 1,
          subject: 'Tarea desde Node.js',
          type_id: 1,
          description: 'Creada mediante API'
        },
        auth
      }
    );
    
    console.log(`✅ Work package creado: #${response.data.id}`);
  } catch (error) {
    console.error('❌ Error:', error.response?.data || error.message);
  }
}

listProjects();
createWorkPackage();
```

---

## 📚 API Endpoints

### 🏠 Info (Información del servidor)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Información del servidor |
| GET | `/health` | Health check |

### 🔧 Core (Funcionalidades principales)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/tools/test_connection` | Probar conexión con OpenProject |

### 🏢 Projects (Gestión de proyectos)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/tools/list_projects` | Listar proyectos |
| POST | `/tools/get_project` | Obtener proyecto específico |
| POST | `/tools/create_project` | Crear nuevo proyecto |
| POST | `/tools/update_project` | Actualizar proyecto |
| POST | `/tools/delete_project` | Eliminar proyecto |

### 📦 Work Packages (Gestión de tareas)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/tools/list_work_packages` | Listar work packages |
| POST | `/tools/get_work_package` | Obtener work package específico |
| POST | `/tools/create_work_package` | Crear work package |
| POST | `/tools/update_work_package` | Actualizar work package |
| POST | `/tools/delete_work_package` | Eliminar work package |
| POST | `/tools/list_types` | Listar tipos de work packages |
| POST | `/tools/list_statuses` | Listar estados |
| POST | `/tools/list_priorities` | Listar prioridades |

### 🔗 Work Package Relations (Relaciones)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/tools/set_work_package_parent` | Establecer relación padre-hijo |
| POST | `/tools/remove_work_package_parent` | Eliminar relación padre |
| POST | `/tools/list_work_package_children` | Listar hijos de un WP |
| POST | `/tools/create_work_package_relation` | Crear relación |
| POST | `/tools/list_work_package_relations` | Listar relaciones |
| POST | `/tools/get_work_package_relation` | Obtener relación específica |
| POST | `/tools/update_work_package_relation` | Actualizar relación |
| POST | `/tools/delete_work_package_relation` | Eliminar relación |

### 👥 Users (Gestión de usuarios)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/tools/list_users` | Listar usuarios |
| POST | `/tools/get_user` | Obtener usuario específico |

### 🎫 Memberships (Membresías de proyectos)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/tools/list_memberships` | Listar membresías |
| POST | `/tools/get_membership` | Obtener membresía específica |
| POST | `/tools/create_membership` | Crear membresía |
| POST | `/tools/update_membership` | Actualizar membresía |
| POST | `/tools/delete_membership` | Eliminar membresía |
| POST | `/tools/list_project_members` | Listar miembros de un proyecto |
| POST | `/tools/list_user_projects` | Listar proyectos de un usuario |

### 🎭 Roles (Gestión de roles)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/tools/list_roles` | Listar roles |
| POST | `/tools/get_role` | Obtener rol específico |

### ⏱️ Time Tracking (Seguimiento de tiempo)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/tools/list_time_entries` | Listar entradas de tiempo |
| POST | `/tools/create_time_entry` | Crear entrada de tiempo |
| POST | `/tools/update_time_entry` | Actualizar entrada |
| POST | `/tools/delete_time_entry` | Eliminar entrada |
| POST | `/tools/list_time_entry_activities` | Listar actividades |

### 📌 Versions (Versiones/Hitos)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/tools/list_versions` | Listar versiones |
| POST | `/tools/create_version` | Crear versión |

### 🚀 REST Aliases (Endpoints simplificados)

Endpoints estilo REST para operaciones comunes:

**Projects:**
```
GET    /api/v1/projects              # Listar proyectos
POST   /api/v1/projects              # Crear proyecto
GET    /api/v1/projects/{id}         # Obtener proyecto
PUT    /api/v1/projects/{id}         # Actualizar proyecto
DELETE /api/v1/projects/{id}         # Eliminar proyecto
```

**Users:**
```
GET    /api/v1/users                 # Listar usuarios
GET    /api/v1/users/{id}            # Obtener usuario
```

**Work Packages:**
```
GET    /api/v1/workpackages          # Listar work packages
POST   /api/v1/workpackages          # Crear work package
GET    /api/v1/workpackages/{id}     # Obtener work package
PUT    /api/v1/workpackages/{id}     # Actualizar work package
DELETE /api/v1/workpackages/{id}     # Eliminar work package
```

**Otros:**
```
GET    /api/v1/roles                 # Listar roles
GET    /api/v1/memberships           # Listar membresías
GET    /api/v1/time-entries          # Listar entradas de tiempo
```

---

## 🔧 Mantenimiento

### Configurar como Servicio Systemd

#### 1. Crear archivo de servicio

```bash
sudo nano /etc/systemd/system/openproject-mcp.service
```

#### 2. Contenido del servicio

```ini
[Unit]
Description=OpenProject MCP HTTP Server
After=network.target

[Service]
Type=simple
User=tuusuario
WorkingDirectory=/home/tuusuario/openproject-mcp-server
Environment="PATH=/home/tuusuario/openproject-mcp-server/.venv/bin"
ExecStart=/home/tuusuario/openproject-mcp-server/.venv/bin/python server_http.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**⚠️ Importante:** Reemplaza `tuusuario` con tu usuario real

#### 3. Activar y arrancar servicio

```bash
# Recargar configuración de systemd
sudo systemctl daemon-reload

# Habilitar inicio automático
sudo systemctl enable openproject-mcp

# Iniciar servicio
sudo systemctl start openproject-mcp

# Ver estado
sudo systemctl status openproject-mcp
```

### Comandos Útiles

```bash
# Ver estado del servicio
sudo systemctl status openproject-mcp

# Reiniciar servicio
sudo systemctl restart openproject-mcp

# Detener servicio
sudo systemctl stop openproject-mcp

# Ver logs en tiempo real
sudo journalctl -u openproject-mcp -f

# Ver últimas 100 líneas de logs
sudo journalctl -u openproject-mcp -n 100

# Ver logs de hoy
sudo journalctl -u openproject-mcp --since today

# Ver logs con errores
sudo journalctl -u openproject-mcp -p err
```

### Actualización de Dependencias

```bash
# Ir al directorio del proyecto
cd /home/tuusuario/openproject-mcp-server

# Activar entorno virtual
source .venv/bin/activate

# Actualizar pip
pip install --upgrade pip

# Actualizar dependencias
pip install --upgrade -r requirements.txt

# Reiniciar servicio
sudo systemctl restart openproject-mcp

# Verificar que funciona
curl http://localhost:8000/health
```

### Backup y Restauración

```bash
# Backup de configuración
cp .env .env.backup.$(date +%Y%m%d)

# Backup completo del proyecto
tar -czf openproject-mcp-backup-$(date +%Y%m%d).tar.gz \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  /home/tuusuario/openproject-mcp-server

# Restaurar desde backup
tar -xzf openproject-mcp-backup-YYYYMMDD.tar.gz -C /
```

---

## 🆘 Troubleshooting

### El servicio no arranca

**Síntoma:** `systemctl status` muestra `failed`

**Solución:**
```bash
# 1. Ver logs de error
sudo journalctl -u openproject-mcp -n 50 --no-pager

# 2. Probar manualmente para ver errores
cd /home/tuusuario/openproject-mcp-server
source .venv/bin/activate
python server_http.py

# 3. Verificar permisos
ls -la server_http.py
# Debe ser legible por el usuario del servicio
```

### Error: ModuleNotFoundError

**Síntoma:** `ModuleNotFoundError: No module named 'slowapi'` (o similar)

**Solución:**
```bash
# Reinstalar dependencias EN el venv correcto
cd /home/tuusuario/openproject-mcp-server
source .venv/bin/activate
pip install mcp aiohttp python-dotenv certifi fastapi uvicorn slowapi python-json-logger httpx

# Verificar instalación
pip list | grep -E "fastapi|uvicorn|slowapi"

# Reiniciar servicio
sudo systemctl restart openproject-mcp
```

### Puerto 8000 ya está en uso

**Síntoma:** `Error: [Errno 98] Address already in use`

**Solución:**
```bash
# Ver qué proceso usa el puerto
sudo lsof -i :8000
sudo ss -tlnp | grep 8000

# Opción 1: Matar el proceso
sudo fuser -k 8000/tcp

# Opción 2: Cambiar puerto en .env
nano .env
# Cambiar: HTTP_PORT=8001

# Reiniciar
sudo systemctl restart openproject-mcp
```

### Entorno virtual corrupto o sin pip

**Síntoma:** `.venv/bin/pip` no existe

**Solución:**
```bash
cd /home/tuusuario/openproject-mcp-server

# Borrar venv corrupto
rm -rf .venv

# Instalar python3-venv si es necesario
sudo apt install python3.10-venv python3-pip -y

# Recrear venv
python3 -m venv .venv

# Activar y verificar pip
source .venv/bin/activate
which pip
pip --version

# Reinstalar dependencias
pip install -r requirements.txt
```

### Swagger UI muestra endpoints viejos (caché)

**Síntoma:** Swagger UI no muestra todos los endpoints o muestra versión vieja

**Solución:**
```bash
# En el navegador:
# 1. Presionar Ctrl + F5 (hard refresh)
# 2. O Ctrl + Shift + R
# 3. O abrir en modo incógnito

# Si persiste, borrar caché de Python en el servidor:
cd /home/tuusuario/openproject-mcp-server
rm -rf __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
sudo systemctl restart openproject-mcp
```

### Error de conexión a OpenProject

**Síntoma:** `Connection refused` o `timeout` al probar endpoints

**Solución:**
```bash
# 1. Verificar conectividad
curl -I https://cmproyectos.cmeducativa.es

# 2. Verificar API key en .env
nano .env
# Confirmar OPENPROJECT_URL y OPENPROJECT_API_KEY

# 3. Probar endpoint de test
curl -X POST http://localhost:8000/tools/test_connection

# 4. Ver logs para más detalles
sudo journalctl -u openproject-mcp -n 50
```

### Logs no aparecen

**Síntoma:** `journalctl` no muestra logs del servicio

**Solución:**
```bash
# Verificar que el servicio esté registrado
systemctl list-units | grep openproject

# Ver logs directamente del proceso
ps aux | grep server_http
# Anotar el PID
sudo tail -f /proc/PID/fd/1  # stdout
sudo tail -f /proc/PID/fd/2  # stderr

# O ejecutar manualmente para ver output
cd /home/tuusuario/openproject-mcp-server
source .venv/bin/activate
python server_http.py
```

### Rendimiento lento

**Síntoma:** Respuestas lentas de la API

**Diagnóstico y solución:**
```bash
# 1. Verificar recursos del sistema
htop
df -h
free -h

# 2. Ver logs para errores
sudo journalctl -u openproject-mcp -p warning -n 100

# 3. Revisar rate limiting
nano .env
# Ajustar RATE_LIMIT si es muy restrictivo

# 4. Verificar compresión GZIP está activa
curl -I -H "Accept-Encoding: gzip" http://localhost:8000/

# 5. Monitorear conexiones
sudo netstat -ant | grep 8000 | wc -l
```

---

## 📖 Documentación Detallada

Ver archivos adicionales en el directorio `docs/`:

- **[INSTALACION.md](docs/INSTALACION.md)** - Guía paso a paso de instalación
- **[CONFIGURACION.md](docs/CONFIGURACION.md)** - Configuración avanzada y tunning
- **[API_REFERENCE.md](docs/API_REFERENCE.md)** - Referencia completa de endpoints
- **[EJEMPLOS.md](docs/EJEMPLOS.md)** - Casos de uso y ejemplos prácticos
- **[DESPLIEGUE.md](docs/DESPLIEGUE.md)** - Despliegue en producción
- **[SEGURIDAD.md](docs/SEGURIDAD.md)** - Mejores prácticas de seguridad
- **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Guía completa de solución de problemas

---

## 📝 Notas de Versión

### v1.1.0 (2025-11-08) - ACTUAL ✨

**Nuevas características:**
- ✅ 52+ endpoints completos para todas las operaciones de OpenProject
- ✅ REST Aliases implementados para uso simplificado
- ✅ Sistema de autenticación HTTP Basic Auth opcional
- ✅ CORS configurable para aplicaciones web
- ✅ Rate limiting para protección contra abuso
- ✅ Compresión GZIP automática
- ✅ JSON structured logging para herramientas de monitoreo
- ✅ Health check endpoint
- ✅ Documentación interactiva completa (Swagger UI + ReDoc)

**Mejoras:**
- ⚡ Performance optimizado con async/await
- 📚 Documentación completa y detallada
- 🔧 Sistema de configuración robusto via .env
- 🛡️ Mejor manejo de errores y validaciones

**Módulos disponibles:**
- Projects, Work Packages, Work Package Relations
- Users, Memberships, Roles
- Time Tracking, Versions

---

## 🔐 Seguridad

### Mejores Prácticas

1. **Siempre usa HTTPS en producción**
2. **Habilita autenticación HTTP Basic Auth**
3. **Restringe CORS a dominios específicos**
4. **Mantén el API key de OpenProject seguro**
5. **Actualiza dependencias regularmente**
6. **Monitorea logs para actividad sospechosa**
7. **Usa firewall para restringir acceso al puerto 8000**

### Configuración Segura para Producción

```ini
# .env para producción
HTTP_AUTH_ENABLED=true
HTTP_AUTH_USERNAME=admin_prod
HTTP_AUTH_PASSWORD=contraseña_muy_segura_y_larga_123!

CORS_ENABLED=true
CORS_ORIGINS=https://tu-app-produccion.com

RATE_LIMIT=50/minute

LOG_LEVEL=WARNING
LOG_FORMAT=json
```

---

## 👨‍💻 Soporte y Contacto

**Servidor de producción:** https://cmproyectos.cmeducativa.es  
**Desarrollado para:** CM Educativa  
**Version actual:** 1.1.0  
**Última actualización:** 2025-11-08

### Recursos Adicionales

- **OpenProject API Docs:** https://docs.openproject.org/api/
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **MCP Protocol:** https://modelcontextprotocol.io/

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT.

---

**✅ ¿Todo listo?** Consulta la [documentación detallada](docs/) para más información o los [ejemplos](docs/EJEMPLOS.md) para casos de uso específicos.

**🆘 ¿Problemas?** Revisa la sección de [Troubleshooting](#-troubleshooting) o consulta [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) para soluciones detalladas.
