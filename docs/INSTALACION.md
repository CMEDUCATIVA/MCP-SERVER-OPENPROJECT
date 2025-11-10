# 📥 Guía de Instalación Completa

Guía detallada paso a paso para instalar OpenProject MCP Server v1.1.0

---

## 📋 Tabla de Contenidos

- [Requisitos Previos](#requisitos-previos)
- [Instalación en Ubuntu/Debian](#instalación-en-ubuntudebian)
- [Instalación en CentOS/RHEL](#instalación-en-centosrhel)
- [Configuración Inicial](#configuración-inicial)
- [Verificación](#verificación)
- [Configuración como Servicio](#configuración-como-servicio)
- [Actualización](#actualización)

---

## Requisitos Previos

### Sistema Operativo

**Sistemas soportados:**
- Ubuntu 20.04 LTS o superior
- Debian 10 (Buster) o superior
- CentOS 8 o superior
- RHEL 8 o superior

### Recursos del Sistema

**Mínimos:**
- CPU: 1 core
- RAM: 512 MB
- Disco: 500 MB libres

**Recomendados:**
- CPU: 2 cores
- RAM: 1 GB
- Disco: 2 GB libres

### Software Base

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- venv (módulo de entornos virtuales)
- git (opcional, para clonar repositorio)

---

## Instalación en Ubuntu/Debian

### Paso 1: Actualizar el sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### Paso 2: Instalar Python 3.10+

```bash
# Verificar versión de Python
python3 --version

# Si es menor a 3.10, instalar desde deadsnakes PPA
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev -y
```

### Paso 3: Instalar dependencias del sistema

```bash
sudo apt install python3-pip build-essential curl wget -y
```

### Paso 4: Crear directorio del proyecto

```bash
# Opción 1: Descargar ZIP
cd /home/$USER
wget https://tu-servidor.com/openproject-mcp-server.zip
unzip openproject-mcp-server.zip
cd openproject-mcp-server

# Opción 2: Clonar repositorio (si aplica)
cd /home/$USER
git clone https://github.com/tu-usuario/openproject-mcp-server.git
cd openproject-mcp-server

# Opción 3: Si ya tienes los archivos
cd /home/$USER/openproject-mcp-server
```

### Paso 5: Crear entorno virtual

```bash
# Crear entorno virtual
python3.10 -m venv .venv

# Activar entorno virtual
source .venv/bin/activate

# Verificar que estás en el venv
which python
# Debe mostrar: /home/usuario/openproject-mcp-server/.venv/bin/python
```

### Paso 6: Instalar dependencias de Python

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar dependencias desde requirements.txt
pip install -r requirements.txt

# O instalar manualmente
pip install \
  mcp>=1.0.0 \
  aiohttp>=3.8.0 \
  python-dotenv>=1.0.0 \
  certifi>=2022.0.0 \
  fastapi>=0.104.0 \
  uvicorn>=0.24.0 \
  slowapi>=0.1.9 \
  python-json-logger>=2.0.7 \
  httpx>=0.24.0
```

### Paso 7: Configurar variables de entorno

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
HTTP_HOST=0.0.0.0
HTTP_PORT=8000
```

**Guardar:** `Ctrl+O`, `Enter`, `Ctrl+X`

### Paso 8: Verificar instalación

```bash
# Probar servidor manualmente
python server_http.py
```

**Resultado esperado:**
```
2025-11-08 12:00:00 - openproject_mcp_http - INFO - ✅ OpenProject MCP HTTP Adapter iniciado
2025-11-08 12:00:00 - openproject_mcp_http - INFO - 📍 Conectado a: https://tu-openproject.com
2025-11-08 12:00:00 - openproject_mcp_http - INFO - 🚀 Iniciando servidor en http://0.0.0.0:8000
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Probar desde otro terminal:**

```bash
curl http://localhost:8000/health
```

**Resultado esperado:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-08T12:00:00",
  "openproject": "connected"
}
```

---

## Instalación en CentOS/RHEL

### Paso 1: Actualizar el sistema

```bash
sudo dnf update -y
# O para versiones antiguas: sudo yum update -y
```

### Paso 2: Instalar Python 3.10+

```bash
# Instalar repositorios EPEL
sudo dnf install epel-release -y

# Instalar Python 3.10
sudo dnf install python3.10 python3.10-devel -y
```

### Paso 3: Instalar dependencias

```bash
sudo dnf install python3-pip gcc make wget curl -y
```

### Paso 4-8: Seguir los mismos pasos que Ubuntu

Los pasos 4 al 8 son idénticos a la instalación en Ubuntu/Debian.

---

## Configuración Inicial

### 1. Obtener API Key de OpenProject

1. Inicia sesión en tu instalación de OpenProject
2. Ve a tu perfil (esquina superior derecha)
3. Click en "My account"
4. Ve a la pestaña "Access tokens"
5. Crear nuevo token:
   - **Name:** `MCP Server`
   - **Expires:** Sin expiración (o fecha lejana)
   - **Scopes:** Seleccionar todos
6. Click en "Generate"
7. **Copiar el token generado** (solo se muestra una vez)

### 2. Configurar .env

```bash
nano .env
```

**Configuración completa:**

```ini
# ============================================================================
# OPENPROJECT CONNECTION
# ============================================================================
OPENPROJECT_URL=https://tu-openproject.com
OPENPROJECT_API_KEY=colocar_aqui_el_token_copiado
OPENPROJECT_PROXY=  # Solo si usas proxy corporativo

# ============================================================================
# HTTP SERVER
# ============================================================================
HTTP_HOST=0.0.0.0          # Escuchar en todas las interfaces
HTTP_PORT=8000              # Puerto del servidor

# ============================================================================
# SEGURIDAD (Producción)
# ============================================================================
HTTP_AUTH_ENABLED=true      # Habilitar en producción
HTTP_AUTH_USERNAME=admin
HTTP_AUTH_PASSWORD=tu_password_segura_aqui

# ============================================================================
# CORS
# ============================================================================
CORS_ENABLED=true
CORS_ORIGINS=*             # En producción: https://tu-app.com

# ============================================================================
# RATE LIMITING
# ============================================================================
RATE_LIMIT=100/minute

# ============================================================================
# COMPRESIÓN
# ============================================================================
GZIP_ENABLED=true
GZIP_MIN_SIZE=1000

# ============================================================================
# LOGGING
# ============================================================================
LOG_LEVEL=INFO
LOG_FORMAT=standard
```

### 3. Ajustar permisos

```bash
# Hacer ejecutable (opcional)
chmod +x server_http.py

# Asegurar que .env no sea accesible públicamente
chmod 600 .env

# Verificar permisos
ls -la .env
# Debe mostrar: -rw------- 1 usuario usuario ...
```

---

## Verificación

### Test de Conexión

```bash
# Activar entorno virtual
source .venv/bin/activate

# Ejecutar servidor
python server_http.py
```

### Test desde navegador

Abre tu navegador y ve a:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### Test desde terminal

```bash
# En otro terminal

# Health check
curl http://localhost:8000/health

# Test de conexión a OpenProject
curl -X POST http://localhost:8000/tools/test_connection

# Listar proyectos
curl -X POST http://localhost:8000/tools/list_projects

# Ver info del servidor
curl http://localhost:8000/ | python3 -m json.tool
```

**Resultados esperados:**

```json
{
  "service": "OpenProject MCP HTTP Adapter",
  "version": "1.1.0",
  "status": "running",
  "openproject_url": "https://tu-openproject.com",
  "features": {
    "authentication": true,
    "cors": true,
    "rate_limiting": true,
    "gzip_compression": true
  },
  "documentation": "/docs"
}
```

---

## Configuración como Servicio

### 1. Crear archivo de servicio systemd

```bash
sudo nano /etc/systemd/system/openproject-mcp.service
```

### 2. Contenido del servicio

```ini
[Unit]
Description=OpenProject MCP HTTP Server
After=network.target

[Service]
Type=simple
User=TU_USUARIO_AQUI
WorkingDirectory=/home/TU_USUARIO_AQUI/openproject-mcp-server
Environment="PATH=/home/TU_USUARIO_AQUI/openproject-mcp-server/.venv/bin"
ExecStart=/home/TU_USUARIO_AQUI/openproject-mcp-server/.venv/bin/python server_http.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**⚠️ IMPORTANTE:** Reemplaza `TU_USUARIO_AQUI` con tu usuario real:

```bash
# Para obtener tu usuario actual
echo $USER

# Ejemplo: si tu usuario es "vinfrancis", el servicio quedaría:
# User=vinfrancis
# WorkingDirectory=/home/vinfrancis/openproject-mcp-server
# etc.
```

### 3. Activar servicio

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

**Estado esperado:**
```
● openproject-mcp.service - OpenProject MCP HTTP Server
     Loaded: loaded (/etc/systemd/system/openproject-mcp.service; enabled)
     Active: active (running) since Sat 2025-11-08 12:00:00 UTC
   Main PID: 12345 (python)
      Tasks: 1
     Memory: 48.7M
     CGroup: /system.slice/openproject-mcp.service
             └─12345 /home/usuario/.../python server_http.py
```

### 4. Comandos útiles del servicio

```bash
# Ver estado
sudo systemctl status openproject-mcp

# Reiniciar
sudo systemctl restart openproject-mcp

# Detener
sudo systemctl stop openproject-mcp

# Ver logs en tiempo real
sudo journalctl -u openproject-mcp -f

# Ver últimos logs
sudo journalctl -u openproject-mcp -n 100
```

---

## Actualización

### Actualizar dependencias

```bash
# Ir al directorio
cd /home/$USER/openproject-mcp-server

# Activar entorno virtual
source .venv/bin/activate

# Actualizar pip
pip install --upgrade pip

# Actualizar dependencias
pip install --upgrade -r requirements.txt

# Reiniciar servicio
sudo systemctl restart openproject-mcp

# Verificar
curl http://localhost:8000/health
```

### Actualizar código

```bash
# Backup del código actual
cp server_http.py server_http.py.backup

# Descargar nueva versión
# (método depende de cómo obtengas las actualizaciones)

# Reiniciar servicio
sudo systemctl restart openproject-mcp

# Ver logs para confirmar
sudo journalctl -u openproject-mcp -n 20
```

### Migrar a nueva versión mayor

```bash
# 1. Detener servicio
sudo systemctl stop openproject-mcp

# 2. Backup completo
tar -czf backup-$(date +%Y%m%d).tar.gz \
  --exclude='.venv' \
  --exclude='__pycache__' \
  .

# 3. Actualizar código y dependencias
# ... (según instrucciones de la nueva versión)

# 4. Probar manualmente primero
source .venv/bin/activate
python server_http.py

# 5. Si funciona, iniciar servicio
sudo systemctl start openproject-mcp
```

---

## Firewall y Networking

### Abrir puerto en firewall (Ubuntu/Debian)

```bash
# UFW
sudo ufw allow 8000/tcp
sudo ufw reload
sudo ufw status
```

### Abrir puerto en firewall (CentOS/RHEL)

```bash
# Firewalld
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
sudo firewall-cmd --list-ports
```

### Acceso desde red externa

Si quieres acceder desde otras máquinas:

1. Asegúrate que `HTTP_HOST=0.0.0.0` en `.env`
2. Abre el puerto 8000 en el firewall
3. Accede usando la IP del servidor: `http://IP-SERVIDOR:8000`

---

## Solución de Problemas Comunes

### Python 3.10 no disponible

```bash
# Ubuntu/Debian
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.10 python3.10-venv

# CentOS/RHEL
sudo dnf install python3.10
```

### Entorno virtual sin pip

```bash
# Instalar python3-venv
sudo apt install python3.10-venv python3-pip

# Recrear venv
rm -rf .venv
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Permiso denegado al crear servicio

```bash
# Verificar que eres sudo
sudo -v

# Crear archivo con sudo
sudo nano /etc/systemd/system/openproject-mcp.service
```

---

## Próximos Pasos

✅ Instalación completada

**Ahora puedes:**

1. 📖 Leer la [Guía de Configuración](CONFIGURACION.md)
2. 🎮 Ver [Ejemplos de Uso](EJEMPLOS.md)
3. 📚 Consultar la [Referencia de API](API_REFERENCE.md)
4. 🔐 Revisar [Mejores Prácticas de Seguridad](SEGURIDAD.md)

---

**¿Problemas durante la instalación?** Consulta [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

