# 📦 Instalación Manual - OpenProject MCP Server

Guía paso a paso para instalar el servidor **sin Docker**, directamente en Ubuntu/Debian.

> **Basado en experiencia real de deployment en producción**

---

## 📋 Requisitos Previos

- Ubuntu 20.04+ / Debian 11+
- Python 3.10 o superior
- Acceso sudo
- Conexión a internet

---

## 🚀 Instalación Paso a Paso

### **Paso 1: Instalar Dependencias del Sistema**

```bash
# Actualizar paquetes
sudo apt update && sudo apt upgrade -y

# Instalar Python 3.10 y herramientas
sudo apt install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    git \
    curl \
    nano
```

**Verificar instalación:**
```bash
python3 --version
# Debe mostrar: Python 3.10.x o superior
```

---

### **Paso 2: Clonar o Descargar el Proyecto**

#### Opción A: Desde GitHub
```bash
cd /opt
sudo git clone https://github.com/tu-usuario/openproject-mcp-server.git
cd openproject-mcp-server
```

#### Opción B: Subir archivos manualmente
```bash
# Crear directorio
sudo mkdir -p /opt/openproject-mcp-server
cd /opt/openproject-mcp-server

# Subir archivos via SCP/SFTP
# Luego cambiar permisos
sudo chown -R $USER:$USER /opt/openproject-mcp-server
```

---

### **Paso 3: Crear Entorno Virtual**

```bash
# Crear virtual environment
python3 -m venv .venv

# Activar entorno virtual
source .venv/bin/activate

# Tu prompt debería cambiar a: (.venv) usuario@host:~$
```

**✅ Verificación:**
```bash
which python
# Debe mostrar: /opt/openproject-mcp-server/.venv/bin/python
```

---

### **Paso 4: Actualizar pip e Instalar Dependencias**

```bash
# Actualizar pip a la última versión
pip install --upgrade pip

# Instalar todas las dependencias
pip install -r requirements.txt
```

**Esto instalará:**
- mcp >= 1.0.0
- aiohttp >= 3.8.0
- python-dotenv >= 1.0.0
- certifi >= 2022.0.0
- fastapi >= 0.104.0
- uvicorn >= 0.24.0
- slowapi >= 0.1.9
- python-json-logger >= 2.0.7
- httpx >= 0.24.0

**Tiempo estimado:** 2-3 minutos

---

### **Paso 5: Configurar Variables de Entorno**

```bash
# Copiar template
cp .env.production .env

# Editar configuración
nano .env
```

**Configuración mínima requerida:**
```bash
# OpenProject Connection (REQUERIDO)
OPENPROJECT_URL=https://cmproyectos.cmeducativa.es
OPENPROJECT_API_KEY=tu-api-key-aqui

# HTTP Server
HTTP_HOST=0.0.0.0
HTTP_PORT=8000

# Security (IMPORTANTE en producción)
HTTP_AUTH_ENABLED=true
HTTP_AUTH_USERNAME=admin
HTTP_AUTH_PASSWORD=UnPasswordSeguro123!

# CORS
CORS_ENABLED=true
CORS_ORIGINS=*

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
TEST_CONNECTION_ON_STARTUP=true

# GZIP
GZIP_ENABLED=true
GZIP_MIN_SIZE=1000

# Rate Limiting
RATE_LIMIT=100/minute
```

**Guardar:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

### **Paso 6: Verificar y Corregir Imports (Fix Común)**

⚠️ **Fix conocido:** En versiones antiguas puede haber un error de importación.

```bash
# Verificar si existe el error
grep "from fastapi.middleware.gzip import GZIPMiddleware" server_http.py

# Si aparece, corregirlo:
sed -i 's/from fastapi.middleware.gzip import GZIPMiddleware/from starlette.middleware.gzip import GZipMiddleware/g' server_http.py

# Verificar que se corrigió
grep "GZip" server_http.py | head -3
```

**Debe mostrar:**
```python
from starlette.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=GZIP_MIN_SIZE)
```

> **Nota:** Las versiones nuevas ya tienen este fix aplicado.

---

### **Paso 7: Probar la Instalación**

```bash
# Asegurarse de que el entorno virtual esté activado
source .venv/bin/activate

# Ejecutar servidor HTTP
python server_http.py
```

**Deberías ver:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Testing OpenProject API connection...
INFO:     ✓ OpenProject API connection successful
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

### **Paso 8: Verificar Funcionamiento**

Abre otra terminal y ejecuta:

```bash
# Health check
curl http://localhost:8000/health

# Esperado:
# {"status":"healthy","openproject_connected":true}

# Test de conexión
curl -X POST http://localhost:8000/tools/test_connection \
  -u admin:tu-password \
  -H "Content-Type: application/json" \
  -d '{}'

# Listar proyectos
curl -X POST http://localhost:8000/tools/list_projects \
  -u admin:tu-password \
  -H "Content-Type: application/json" \
  -d '{"page_size": 5}'
```

**Si todo funciona:** ✅ ¡Instalación exitosa!

---

## 🔧 Configurar como Servicio Systemd (Recomendado)

Para que el servidor se ejecute automáticamente al iniciar el sistema:

### **Paso 1: Crear archivo de servicio**

```bash
sudo nano /etc/systemd/system/openproject-mcp.service
```

**Contenido:**
```ini
[Unit]
Description=OpenProject MCP Server
After=network.target
Documentation=https://github.com/tu-usuario/openproject-mcp-server

[Service]
Type=simple
User=tu-usuario
Group=tu-usuario
WorkingDirectory=/opt/openproject-mcp-server
Environment="PATH=/opt/openproject-mcp-server/.venv/bin"
EnvironmentFile=/opt/openproject-mcp-server/.env
ExecStart=/opt/openproject-mcp-server/.venv/bin/python server_http.py

# Restart policy
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=openproject-mcp

[Install]
WantedBy=multi-user.target
```

**Cambiar:**
- `tu-usuario` por tu usuario real
- Ajustar rutas si instalaste en otro directorio

**Guardar:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

### **Paso 2: Habilitar y arrancar el servicio**

```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar para inicio automático
sudo systemctl enable openproject-mcp

# Iniciar servicio
sudo systemctl start openproject-mcp

# Verificar estado
sudo systemctl status openproject-mcp
```

**Estado esperado:**
```
● openproject-mcp.service - OpenProject MCP Server
   Loaded: loaded (/etc/systemd/system/openproject-mcp.service; enabled)
   Active: active (running) since ...
```

---

### **Paso 3: Comandos útiles del servicio**

```bash
# Ver estado
sudo systemctl status openproject-mcp

# Ver logs en tiempo real
sudo journalctl -u openproject-mcp -f

# Ver últimas 100 líneas
sudo journalctl -u openproject-mcp -n 100

# Reiniciar servicio
sudo systemctl restart openproject-mcp

# Detener servicio
sudo systemctl stop openproject-mcp

# Deshabilitar inicio automático
sudo systemctl disable openproject-mcp
```

---

## 🔥 Configurar Firewall (UFW)

```bash
# Permitir puerto 8000
sudo ufw allow 8000/tcp

# Verificar reglas
sudo ufw status
```

---

## 🌐 Configurar Nginx como Reverse Proxy (Opcional)

Para acceder con un dominio y SSL:

### **Paso 1: Instalar Nginx**

```bash
sudo apt install nginx
```

### **Paso 2: Crear configuración**

```bash
sudo nano /etc/nginx/sites-available/openproject-mcp
```

**Contenido:**
```nginx
server {
    listen 80;
    server_name openproject-mcp.tudominio.com;

    # Logs
    access_log /var/log/nginx/openproject-mcp.access.log;
    error_log /var/log/nginx/openproject-mcp.error.log;

    # Proxy
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### **Paso 3: Activar sitio**

```bash
# Crear symlink
sudo ln -s /etc/nginx/sites-available/openproject-mcp /etc/nginx/sites-enabled/

# Verificar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

### **Paso 4: Configurar SSL con Let's Encrypt**

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d openproject-mcp.tudominio.com

# Certificado se renovará automáticamente
```

---

## 🔄 Actualización del Servidor

```bash
# 1. Detener servicio
sudo systemctl stop openproject-mcp

# 2. Activar entorno virtual
cd /opt/openproject-mcp-server
source .venv/bin/activate

# 3. Hacer pull de cambios (si usas git)
git pull

# 4. Actualizar dependencias
pip install --upgrade -r requirements.txt

# 5. Reiniciar servicio
sudo systemctl start openproject-mcp

# 6. Verificar
sudo systemctl status openproject-mcp
```

---

## 🐛 Troubleshooting

### **Error: ModuleNotFoundError**

**Causa:** Dependencias no instaladas o entorno virtual no activado.

**Solución:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### **Error: ImportError: GZIPMiddleware**

**Causa:** Import incorrecto en server_http.py

**Solución:**
```bash
sed -i 's/GZIPMiddleware/GZipMiddleware/g' server_http.py
```

### **Error: Connection refused a OpenProject**

**Causa:** URL o API Key incorrectos

**Solución:**
```bash
# Verificar variables
cat .env | grep OPENPROJECT

# Probar conexión manual
curl -H "Authorization: Basic $(echo -n 'apikey:TU_API_KEY' | base64)" \
  https://tu-openproject.com/api/v3
```

### **Puerto 8000 ocupado**

**Solución:**
```bash
# Ver qué usa el puerto
sudo lsof -i :8000

# Cambiar puerto en .env
nano .env
# Cambiar HTTP_PORT=8080

# Reiniciar
sudo systemctl restart openproject-mcp
```

### **Servicio no inicia**

**Solución:**
```bash
# Ver logs detallados
sudo journalctl -u openproject-mcp -n 100 --no-pager

# Verificar permisos
sudo chown -R tu-usuario:tu-usuario /opt/openproject-mcp-server

# Probar manualmente
cd /opt/openproject-mcp-server
source .venv/bin/activate
python server_http.py
```

---

## 📊 Monitoreo

### **Ver logs en tiempo real**
```bash
sudo journalctl -u openproject-mcp -f
```

### **Ver logs con filtro**
```bash
# Solo errores
sudo journalctl -u openproject-mcp -p err

# Últimas 24 horas
sudo journalctl -u openproject-mcp --since "24 hours ago"

# Por fecha
sudo journalctl -u openproject-mcp --since "2024-11-09" --until "2024-11-10"
```

### **Estadísticas del proceso**
```bash
# Ver proceso
ps aux | grep server_http

# Uso de recursos
top -p $(pgrep -f server_http.py)
```

---

## 🔐 Seguridad

### **Recomendaciones:**

1. **Usar HTTPS:** Configura Nginx + Let's Encrypt
2. **Firewall:** Solo permite puertos necesarios
3. **HTTP Auth:** Siempre activa HTTP_AUTH_ENABLED=true
4. **Restringir CORS:** No uses `*` en producción
5. **Actualizar regularmente:** Mantén Python y dependencias actualizadas
6. **Logs:** Revisa logs regularmente
7. **Backups:** Haz backup de `.env` y configuraciones

---

## ✅ Checklist de Instalación

- [ ] Python 3.10+ instalado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas
- [ ] Archivo `.env` configurado
- [ ] Fix de imports aplicado (si necesario)
- [ ] Servidor prueba OK manualmente
- [ ] Servicio systemd configurado
- [ ] Servicio habilitado e iniciado
- [ ] Firewall configurado
- [ ] Nginx reverse proxy (opcional)
- [ ] SSL/TLS configurado (opcional)
- [ ] Health check respondiendo
- [ ] Tests de API funcionando
- [ ] Logs monitoreados

---

## 📚 Archivos Importantes

```
/opt/openproject-mcp-server/
├── .env                          # Tu configuración
├── .venv/                        # Entorno virtual
├── openproject_mcp.py            # Cliente MCP
├── server_http.py                # Servidor HTTP
├── requirements.txt              # Dependencias
└── logs/ (si configuras)

/etc/systemd/system/
└── openproject-mcp.service       # Servicio systemd

/etc/nginx/sites-available/
└── openproject-mcp               # Config Nginx

/var/log/nginx/
├── openproject-mcp.access.log    # Logs de acceso
└── openproject-mcp.error.log     # Logs de error
```

---

## 🎉 ¡Listo!

Tu OpenProject MCP Server está instalado y corriendo como servicio del sistema.

**Endpoints disponibles:**
- API: `http://tu-servidor:8000/`
- Docs: `http://tu-servidor:8000/docs`
- Health: `http://tu-servidor:8000/health`

**Con Nginx + SSL:**
- API: `https://openproject-mcp.tudominio.com/`
- Docs: `https://openproject-mcp.tudominio.com/docs`
- Health: `https://openproject-mcp.tudominio.com/health`

---

**Creado basado en deployment real en producción** ✨
