# 🎯 Instalación en Easypanel - Paso a Paso

Guía visual para desplegar OpenProject MCP Server en Easypanel en **menos de 5 minutos**.

---

## 🚀 Método Recomendado: Docker Compose

### ✅ Paso 1: Acceder a Easypanel

1. Abre tu navegador y accede a tu instancia de Easypanel:
   ```
   https://tu-easypanel.tudominio.com
   ```

2. Inicia sesión con tus credenciales

---

### ✅ Paso 2: Crear Nueva Aplicación

1. Click en **"Projects"** en el menú lateral
2. Selecciona tu proyecto o crea uno nuevo
3. Click en **"Create Application"** o **"+ New Service"**
4. Selecciona **"Docker Compose"**

---

### ✅ Paso 3: Configurar Docker Compose

Copia y pega el siguiente contenido en el editor de Easypanel:

```yaml
version: '3.8'

services:
  app:
    build:
      context: https://github.com/TU-USUARIO/openproject-mcp-server.git
    image: openproject-mcp-server:latest
    container_name: openproject-mcp
    restart: unless-stopped

    ports:
      - "8000:8000"

    environment:
      # OpenProject (Configurar abajo)
      OPENPROJECT_URL: ${OPENPROJECT_URL}
      OPENPROJECT_API_KEY: ${OPENPROJECT_API_KEY}

      # Server
      HTTP_HOST: 0.0.0.0
      HTTP_PORT: 8000

      # Security
      HTTP_AUTH_ENABLED: ${HTTP_AUTH_ENABLED:-true}
      HTTP_AUTH_USERNAME: ${HTTP_AUTH_USERNAME:-admin}
      HTTP_AUTH_PASSWORD: ${HTTP_AUTH_PASSWORD:-changeme}

      # CORS
      CORS_ENABLED: true
      CORS_ORIGINS: "*"

      # Logging
      LOG_LEVEL: INFO
      LOG_FORMAT: json

      # Python
      PYTHONUNBUFFERED: 1

    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

**O si prefieres usar la imagen directamente sin build:**

```yaml
version: '3.8'

services:
  app:
    image: python:3.11-slim
    working_dir: /app

    command: >
      sh -c "
      apt-get update && apt-get install -y git curl &&
      git clone https://github.com/TU-USUARIO/openproject-mcp-server.git . &&
      pip install --no-cache-dir -r requirements.txt &&
      python server_http.py
      "

    ports:
      - "8000:8000"

    environment:
      OPENPROJECT_URL: ${OPENPROJECT_URL}
      OPENPROJECT_API_KEY: ${OPENPROJECT_API_KEY}
      HTTP_HOST: 0.0.0.0
      HTTP_PORT: 8000
      HTTP_AUTH_ENABLED: ${HTTP_AUTH_ENABLED:-true}
      HTTP_AUTH_USERNAME: ${HTTP_AUTH_USERNAME:-admin}
      HTTP_AUTH_PASSWORD: ${HTTP_AUTH_PASSWORD:-changeme}
      CORS_ENABLED: true
      CORS_ORIGINS: "*"
      LOG_LEVEL: INFO
      PYTHONUNBUFFERED: 1

    restart: unless-stopped
```

---

### ✅ Paso 4: Configurar Variables de Entorno

En la sección **"Environment Variables"** de Easypanel, agrega:

#### **Variables REQUERIDAS:**

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `OPENPROJECT_URL` | `https://tu-openproject.com` | URL de tu instancia OpenProject |
| `OPENPROJECT_API_KEY` | `tu-api-key-aqui` | API Key de OpenProject |

#### **Variables de Seguridad (RECOMENDADAS):**

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `HTTP_AUTH_ENABLED` | `true` | Habilitar autenticación |
| `HTTP_AUTH_USERNAME` | `admin` | Usuario para HTTP Basic Auth |
| `HTTP_AUTH_PASSWORD` | `TuPasswordSeguro123!` | Contraseña (¡CAMBIAR!) |

#### **Variables Opcionales:**

| Variable | Valor por Defecto | Descripción |
|----------|-------------------|-------------|
| `LOG_LEVEL` | `INFO` | Nivel de logs (DEBUG, INFO, WARNING, ERROR) |
| `CORS_ORIGINS` | `*` | Dominios permitidos (separados por coma) |
| `RATE_LIMIT` | `100/minute` | Límite de peticiones |

---

### ✅ Paso 5: Configurar Dominio (Opcional)

1. En Easypanel, ve a la sección **"Domains"**
2. Click en **"Add Domain"**
3. Ingresa tu dominio: `openproject-mcp.tudominio.com`
4. Easypanel automáticamente configurará SSL con Let's Encrypt

---

### ✅ Paso 6: Deploy

1. Verifica que todas las variables estén configuradas
2. Click en **"Deploy"** o **"Save & Deploy"**
3. Espera a que el contenedor esté en estado **"Running"** (1-2 minutos)

---

### ✅ Paso 7: Verificar Instalación

#### Desde Easypanel:

1. Ve a la pestaña **"Logs"** para ver el output
2. Deberías ver:
   ```
   INFO:     Started server process
   INFO:     Uvicorn running on http://0.0.0.0:8000
   INFO:     Application startup complete.
   ```

#### Desde tu navegador:

Accede a las siguientes URLs:

1. **Health Check:**
   ```
   https://openproject-mcp.tudominio.com/health
   ```

   Deberías ver:
   ```json
   {
     "status": "healthy",
     "openproject_connected": true
   }
   ```

2. **Swagger UI (Documentación):**
   ```
   https://openproject-mcp.tudominio.com/docs
   ```

3. **API Root:**
   ```
   https://openproject-mcp.tudominio.com/
   ```

---

## 🎨 Alternativa: Desde GitHub

Si tu código está en GitHub, es aún más fácil:

### Paso 1: Preparar GitHub

```bash
cd openproject-mcp-server
git init
git add .
git commit -m "Initial deployment"
git remote add origin https://github.com/tu-usuario/openproject-mcp-server.git
git push -u origin main
```

### Paso 2: En Easypanel

1. **Create Application** → **"From GitHub"**
2. Conecta tu cuenta de GitHub (si es primera vez)
3. Selecciona el repositorio: `openproject-mcp-server`
4. Easypanel detectará el `Dockerfile` automáticamente

### Paso 3: Configurar

1. **Build Settings:**
   - Build Context: `/`
   - Dockerfile Path: `./Dockerfile`

2. **Environment Variables:** (como arriba)
   - `OPENPROJECT_URL`
   - `OPENPROJECT_API_KEY`
   - etc.

3. **Port:** `8000`

### Paso 4: Deploy

Click en **"Deploy"** y listo!

**Ventaja:** Cada vez que hagas `git push`, Easypanel auto-desplegará los cambios.

---

## 🔧 Configuración Post-Deployment

### 1. Configurar Reverse Proxy (Opcional)

Si usas Nginx o Traefik:

```nginx
server {
    listen 80;
    server_name openproject-mcp.tudominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Configurar SSL/TLS

Easypanel lo hace automáticamente, pero si lo haces manual:

```bash
certbot --nginx -d openproject-mcp.tudominio.com
```

### 3. Configurar Backup

Exporta las variables de entorno regularmente:

```bash
# En Easypanel, exporta la configuración
# Settings → Export Configuration
```

---

## 📊 Monitoreo en Easypanel

### Ver Logs en Tiempo Real

1. Ve a tu aplicación en Easypanel
2. Click en **"Logs"**
3. Los logs se actualizan en tiempo real

### Ver Métricas

1. Click en **"Metrics"**
2. Verás:
   - Uso de CPU
   - Uso de Memoria
   - Requests por minuto
   - Uptime

### Alerts (Opcional)

Configura alertas en Easypanel:
- CPU > 80%
- Memoria > 400MB
- Servicio down

---

## 🧪 Pruebas Post-Instalación

### Test 1: Health Check

```bash
curl https://openproject-mcp.tudominio.com/health
```

**Esperado:**
```json
{"status": "healthy", "openproject_connected": true}
```

### Test 2: Autenticación

```bash
curl -u admin:TuPassword \
  https://openproject-mcp.tudominio.com/health
```

### Test 3: Listar Proyectos

```bash
curl -X POST https://openproject-mcp.tudominio.com/tools/list_projects \
  -u admin:TuPassword \
  -H "Content-Type: application/json" \
  -d '{"page_size": 5}'
```

### Test 4: Buscar Proyectos

```bash
curl -X POST https://openproject-mcp.tudominio.com/tools/list_projects \
  -u admin:TuPassword \
  -H "Content-Type: application/json" \
  -d '{
    "name_contains": "web",
    "page_size": 10
  }'
```

---

## 🔄 Actualización

### Desde Easypanel UI:

1. Ve a tu aplicación
2. Click en **"Redeploy"**
3. Easypanel reconstruirá la imagen

### Desde Git (si usas GitHub):

```bash
git add .
git commit -m "Update features"
git push
```

Easypanel detectará el push y auto-desplegará.

---

## ❓ Troubleshooting

### Problema: Contenedor no inicia

**Solución:**
1. Ve a **"Logs"** en Easypanel
2. Busca errores
3. Verifica que las variables de entorno estén configuradas

### Problema: Error 502 Bad Gateway

**Causa:** El servicio no está corriendo.

**Solución:**
1. Verifica el estado en Easypanel
2. Ve a **"Logs"** para ver el error
3. Reinicia el servicio: Click en **"Restart"**

### Problema: Error de conexión a OpenProject

**Solución:**
1. Verifica `OPENPROJECT_URL` y `OPENPROJECT_API_KEY`
2. Prueba la conexión manualmente:
   ```bash
   curl -H "Authorization: Basic $(echo -n 'apikey:TU_API_KEY' | base64)" \
     https://tu-openproject.com/api/v3
   ```

### Problema: Logs vacíos

**Causa:** El contenedor no está iniciando.

**Solución:**
1. Verifica las variables de entorno
2. Verifica el `docker-compose.yml`
3. Reinicia desde Easypanel

---

## 📈 Optimización

### Reducir Tamaño de Imagen

El Dockerfile ya está optimizado con multi-stage build:
- Imagen final: ~200-300 MB
- Sin archivos de desarrollo
- Solo dependencias de producción

### Limitar Recursos

En Easypanel, configura límites:
- **CPU:** 0.5-1 core
- **Memory:** 256-512 MB

### Cache de Dependencias

El Dockerfile usa cache de Docker para acelerar builds:
```dockerfile
COPY requirements.txt .
RUN pip install -r requirements.txt
# Los archivos del código se copian después
```

---

## ✅ Checklist Post-Deployment

- [ ] Health check responde OK
- [ ] Swagger UI accesible en `/docs`
- [ ] Test de conexión a OpenProject exitoso
- [ ] Autenticación HTTP funciona
- [ ] SSL/TLS configurado
- [ ] Dominio personalizado configurado
- [ ] Logs funcionando correctamente
- [ ] Métricas visibles en Easypanel
- [ ] Backup de configuración exportado
- [ ] Variables de entorno documentadas

---

## 🎉 ¡Listo!

Tu OpenProject MCP Server está desplegado y funcionando en Easypanel.

**Endpoints:**
- 🏠 Home: `https://tu-dominio.com/`
- 📖 Docs: `https://tu-dominio.com/docs`
- ❤️ Health: `https://tu-dominio.com/health`

**Próximos pasos:**
1. Integrar con tu aplicación
2. Configurar webhooks (si necesitas)
3. Agregar monitoreo avanzado
4. Configurar CI/CD

---

**¿Preguntas?** Consulta:
- [DEPLOYMENT.md](DEPLOYMENT.md) - Guía completa
- [DOCKER-QUICKSTART.md](DOCKER-QUICKSTART.md) - Quick start
- [README.md](README.md) - Documentación del proyecto

**¡Happy Deploying!** 🚀
