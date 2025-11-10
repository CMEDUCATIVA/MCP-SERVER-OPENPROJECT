# 🚀 Guía de Deployment - OpenProject MCP Server

Esta guía te ayudará a desplegar el OpenProject MCP Server en diferentes plataformas, con énfasis en **Easypanel**.

---

## 📋 Tabla de Contenidos

1. [Deployment en Easypanel (Recomendado)](#deployment-en-easypanel)
2. [Deployment con Docker Compose](#deployment-con-docker-compose)
3. [Deployment con Dockerfile](#deployment-con-dockerfile)
4. [Variables de Entorno](#variables-de-entorno)
5. [Verificación y Pruebas](#verificación-y-pruebas)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Deployment en Easypanel (Recomendado)

Easypanel soporta múltiples formas de deployment. Aquí están las **3 opciones** ordenadas de más fácil a más personalizable:

### **Opción 1: Docker Compose (Más Fácil) ⭐**

Esta es la forma más sencilla y recomendada.

#### Pasos:

1. **Accede a tu servidor Easypanel**
   - URL: `https://your-easypanel-domain.com`

2. **Crea una nueva aplicación**
   - Click en "Create Application"
   - Nombre: `openproject-mcp-server`

3. **Selecciona "Docker Compose"**
   - En el tipo de aplicación, selecciona "Docker Compose"

4. **Copia el contenido de `docker-compose.yml`**
   ```yaml
   # Pega el contenido completo del archivo docker-compose.yml aquí
   ```

5. **Configura las variables de entorno**

   En la sección "Environment Variables" de Easypanel, agrega:

   ```bash
   # REQUERIDO
   OPENPROJECT_URL=https://tu-instancia-openproject.com
   OPENPROJECT_API_KEY=tu-api-key-aquí

   # SEGURIDAD (Cambiar contraseñas)
   HTTP_AUTH_ENABLED=true
   HTTP_AUTH_USERNAME=admin
   HTTP_AUTH_PASSWORD=tu-password-seguro

   # OPCIONAL
   LOG_LEVEL=INFO
   CORS_ENABLED=true
   CORS_ORIGINS=*
   RATE_LIMIT=100/minute
   ```

6. **Configura el puerto**
   - Port Mapping: `8000:8000`
   - Marca como "Expose to Internet" si necesitas acceso público

7. **Deploy**
   - Click en "Deploy"
   - Espera a que el contenedor esté "Running"

8. **Verifica**
   - Accede a: `http://your-server:8000/`
   - Deberías ver la página de bienvenida
   - Accede a: `http://your-server:8000/docs` para la documentación Swagger

---

### **Opción 2: GitHub Repository (Automático)**

Si tu proyecto está en GitHub, Easypanel puede hacer auto-deploy.

#### Pasos:

1. **Sube tu código a GitHub**
   ```bash
   cd openproject-mcp-server
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/tu-usuario/openproject-mcp-server.git
   git push -u origin main
   ```

2. **En Easypanel:**
   - Create Application → "From GitHub"
   - Conecta tu repositorio
   - Easypanel detectará automáticamente el `Dockerfile`

3. **Configura Build Settings**
   - Build Context: `/` (raíz del proyecto)
   - Dockerfile Path: `./Dockerfile`

4. **Agrega las variables de entorno** (como en Opción 1)

5. **Deploy y listo!**

---

### **Opción 3: Docker Image (Manual)**

Si prefieres construir la imagen localmente y subirla.

#### Pasos:

1. **Construye la imagen localmente**
   ```bash
   docker build -t your-dockerhub-username/openproject-mcp-server:latest .
   ```

2. **Sube a Docker Hub**
   ```bash
   docker push your-dockerhub-username/openproject-mcp-server:latest
   ```

3. **En Easypanel:**
   - Create Application → "Docker Image"
   - Image: `your-dockerhub-username/openproject-mcp-server:latest`
   - Port: `8000`

4. **Agrega las variables de entorno** (como en Opción 1)

5. **Deploy**

---

## 🐳 Deployment con Docker Compose (Local o VPS)

Si tienes un servidor sin Easypanel:

### Pasos:

1. **Clona o copia el proyecto**
   ```bash
   cd /opt
   git clone https://github.com/tu-usuario/openproject-mcp-server.git
   cd openproject-mcp-server
   ```

2. **Copia el archivo de configuración**
   ```bash
   cp .env.production .env
   ```

3. **Edita las variables de entorno**
   ```bash
   nano .env
   ```

   Configura al menos:
   ```bash
   OPENPROJECT_URL=https://tu-instancia.com
   OPENPROJECT_API_KEY=tu-api-key
   HTTP_AUTH_PASSWORD=password-seguro
   ```

4. **Levanta el servicio**
   ```bash
   docker-compose up -d
   ```

5. **Verifica los logs**
   ```bash
   docker-compose logs -f
   ```

6. **Accede**
   - `http://tu-servidor:8000/`
   - `http://tu-servidor:8000/docs`

### Comandos útiles:

```bash
# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Detener
docker-compose down

# Actualizar (después de cambios)
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Ver estado
docker-compose ps
```

---

## 🐋 Deployment con Dockerfile (Solo Docker)

Si solo tienes Docker instalado:

```bash
# 1. Construir imagen
docker build -t openproject-mcp-server .

# 2. Ejecutar contenedor
docker run -d \
  --name openproject-mcp \
  -p 8000:8000 \
  -e OPENPROJECT_URL="https://tu-instancia.com" \
  -e OPENPROJECT_API_KEY="tu-api-key" \
  -e HTTP_AUTH_ENABLED="true" \
  -e HTTP_AUTH_USERNAME="admin" \
  -e HTTP_AUTH_PASSWORD="password-seguro" \
  --restart unless-stopped \
  openproject-mcp-server

# 3. Ver logs
docker logs -f openproject-mcp

# 4. Detener
docker stop openproject-mcp

# 5. Iniciar
docker start openproject-mcp
```

---

## 🔐 Variables de Entorno

### **Requeridas:**

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `OPENPROJECT_URL` | URL de tu instancia OpenProject | `https://openproject.example.com` |
| `OPENPROJECT_API_KEY` | API Key de OpenProject | `a1b2c3d4e5f6...` |

### **Seguridad (Recomendadas):**

| Variable | Descripción | Default | Ejemplo |
|----------|-------------|---------|---------|
| `HTTP_AUTH_ENABLED` | Habilitar autenticación HTTP Basic | `false` | `true` |
| `HTTP_AUTH_USERNAME` | Usuario para HTTP Basic Auth | `admin` | `myuser` |
| `HTTP_AUTH_PASSWORD` | Contraseña para HTTP Basic Auth | `changeme` | `SecurePass123!` |

### **Configuración HTTP:**

| Variable | Descripción | Default | Ejemplo |
|----------|-------------|---------|---------|
| `HTTP_HOST` | IP de binding | `0.0.0.0` | `0.0.0.0` |
| `HTTP_PORT` | Puerto del servidor | `8000` | `8080` |

### **CORS:**

| Variable | Descripción | Default | Ejemplo |
|----------|-------------|---------|---------|
| `CORS_ENABLED` | Habilitar CORS | `true` | `true` |
| `CORS_ORIGINS` | Dominios permitidos | `*` | `https://app1.com,https://app2.com` |

### **Rate Limiting:**

| Variable | Descripción | Default | Ejemplo |
|----------|-------------|---------|---------|
| `RATE_LIMIT` | Límite de peticiones | `100/minute` | `200/minute` |

### **Logging:**

| Variable | Descripción | Default | Ejemplo |
|----------|-------------|---------|---------|
| `LOG_LEVEL` | Nivel de logs | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_FORMAT` | Formato de logs | `json` | `standard`, `json` |

### **Opcionales:**

| Variable | Descripción | Default | Ejemplo |
|----------|-------------|---------|---------|
| `OPENPROJECT_PROXY` | Proxy HTTP | `` | `http://proxy.corp.com:8080` |
| `GZIP_ENABLED` | Habilitar compresión GZIP | `true` | `true` |
| `GZIP_MIN_SIZE` | Tamaño mínimo para comprimir (bytes) | `1000` | `500` |

---

## ✅ Verificación y Pruebas

### 1. **Health Check**
```bash
curl http://localhost:8000/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "openproject_connected": true
}
```

### 2. **Documentación API**

Accede a Swagger UI:
```
http://localhost:8000/docs
```

O ReDoc:
```
http://localhost:8000/redoc
```

### 3. **Test de Conexión a OpenProject**

```bash
curl -X POST http://localhost:8000/tools/test_connection \
  -H "Content-Type: application/json" \
  -d '{}'
```

Con autenticación (si está habilitada):
```bash
curl -X POST http://localhost:8000/tools/test_connection \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 4. **Listar Proyectos**

```bash
curl -X POST http://localhost:8000/tools/list_projects \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "active_only": true,
    "page_size": 10
  }'
```

### 5. **Buscar Proyectos**

```bash
curl -X POST http://localhost:8000/tools/list_projects \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "name_contains": "web",
    "offset": 1,
    "page_size": 20
  }'
```

---

## 🔧 Troubleshooting

### **Problema: Contenedor no inicia**

**Solución:**
```bash
# Ver logs detallados
docker-compose logs openproject-mcp

# O con docker
docker logs openproject-mcp
```

### **Problema: Error "Connection refused" a OpenProject**

**Causa:** La URL o API Key son incorrectas.

**Solución:**
1. Verifica las variables de entorno:
   ```bash
   docker-compose exec openproject-mcp env | grep OPENPROJECT
   ```

2. Prueba la conexión manualmente:
   ```bash
   curl -H "Authorization: Basic $(echo -n 'apikey:TU_API_KEY' | base64)" \
     https://tu-openproject.com/api/v3
   ```

### **Problema: 401 Unauthorized en API**

**Causa:** HTTP Basic Auth está habilitado pero no envías credenciales.

**Solución:**
```bash
# Agregar -u usuario:password
curl -u admin:password http://localhost:8000/health
```

O deshabilitar auth:
```bash
HTTP_AUTH_ENABLED=false
```

### **Problema: CORS Error**

**Causa:** Tu dominio no está en la lista de CORS_ORIGINS.

**Solución:**
```bash
# Permitir todos (desarrollo)
CORS_ORIGINS=*

# Permitir específicos (producción)
CORS_ORIGINS=https://app1.com,https://app2.com
```

### **Problema: Rate Limit Exceeded**

**Solución:**
```bash
# Aumentar límite
RATE_LIMIT=200/minute

# O deshabilitar temporalmente editando server_http.py
```

### **Problema: Contenedor consume mucha memoria**

**Solución:** Ajustar límites en `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 256M  # Reducir si es necesario
```

---

## 📊 Monitoreo

### **Logs en tiempo real**
```bash
docker-compose logs -f openproject-mcp
```

### **Estadísticas de recursos**
```bash
docker stats openproject-mcp
```

### **Health check manual**
```bash
watch -n 5 'curl -s http://localhost:8000/health | jq'
```

---

## 🔄 Actualización

### **Con Docker Compose:**
```bash
# 1. Hacer pull de cambios
git pull

# 2. Reconstruir imagen
docker-compose build --no-cache

# 3. Reiniciar servicio
docker-compose up -d

# 4. Verificar
docker-compose logs -f
```

### **Con Easypanel:**
- Si usaste GitHub: Push los cambios y Easypanel auto-deploya
- Si usaste Compose: Edita y "Redeploy"
- Si usaste Image: Rebuild y push nueva imagen

---

## 🎉 ¡Listo!

Tu OpenProject MCP Server ahora está desplegado y funcionando.

**Endpoints importantes:**
- API Root: `http://tu-servidor:8000/`
- Swagger Docs: `http://tu-servidor:8000/docs`
- ReDoc: `http://tu-servidor:8000/redoc`
- Health Check: `http://tu-servidor:8000/health`

**Próximos pasos:**
1. Configurar un dominio personalizado
2. Agregar SSL/TLS (Let's Encrypt)
3. Configurar backup automático
4. Integrar con tu aplicación

---

## 📚 Recursos Adicionales

- [Documentación de Easypanel](https://easypanel.io/docs)
- [Documentación de Docker Compose](https://docs.docker.com/compose/)
- [OpenProject API Docs](https://www.openproject.org/docs/api/)

---

**Creado con ❤️ para facilitar el deployment**
