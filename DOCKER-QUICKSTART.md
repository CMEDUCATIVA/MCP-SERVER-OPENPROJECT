# 🚀 Docker Quick Start - OpenProject MCP Server

Guía ultra-rápida para desplegar en menos de 5 minutos.

---

## ⚡ Quick Start (3 pasos)

### 1️⃣ Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.production .env

# Editar con tus credenciales
nano .env
```

**Mínimo requerido en `.env`:**
```bash
OPENPROJECT_URL=https://tu-openproject.com
OPENPROJECT_API_KEY=tu-api-key-aqui
```

### 2️⃣ Levantar el servicio

```bash
docker-compose up -d
```

### 3️⃣ Verificar

```bash
# Ver que esté corriendo
docker-compose ps

# Ver logs
docker-compose logs -f

# Probar health check
curl http://localhost:8000/health
```

**¡Listo!** Accede a:
- 📖 Swagger Docs: http://localhost:8000/docs
- 🔍 Health Check: http://localhost:8000/health

---

## 🎯 Para Easypanel

### Método 1: Docker Compose (Más Fácil)

1. En Easypanel: **"Create Application"** → **"Docker Compose"**
2. Pega el contenido de `docker-compose.yml`
3. En "Environment Variables" agrega:
   ```
   OPENPROJECT_URL=https://tu-instancia.com
   OPENPROJECT_API_KEY=tu-api-key
   ```
4. **Deploy!**

### Método 2: Desde GitHub

1. Sube tu código a GitHub
2. En Easypanel: **"Create Application"** → **"From GitHub"**
3. Selecciona tu repo
4. Easypanel detectará el Dockerfile automáticamente
5. Agrega las variables de entorno
6. **Deploy!**

---

## 📋 Variables de Entorno Importantes

### Requeridas:
```bash
OPENPROJECT_URL=https://tu-openproject.com
OPENPROJECT_API_KEY=tu-api-key
```

### Seguridad (Recomendadas):
```bash
HTTP_AUTH_ENABLED=true
HTTP_AUTH_USERNAME=admin
HTTP_AUTH_PASSWORD=tu-password-seguro
```

### Opcionales:
```bash
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
CORS_ENABLED=true
CORS_ORIGINS=*              # O dominios específicos
RATE_LIMIT=100/minute
```

Ver todas las variables en: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🧪 Probar la Instalación

### Health Check
```bash
curl http://localhost:8000/health
```

**Respuesta esperada:**
```json
{"status": "healthy", "openproject_connected": true}
```

### Test de Conexión
```bash
curl -X POST http://localhost:8000/tools/test_connection \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Listar Proyectos
```bash
curl -X POST http://localhost:8000/tools/list_projects \
  -H "Content-Type: application/json" \
  -d '{"page_size": 10}'
```

### Buscar Proyectos
```bash
curl -X POST http://localhost:8000/tools/list_projects \
  -H "Content-Type: application/json" \
  -d '{
    "name_contains": "web",
    "offset": 1,
    "page_size": 20
  }'
```

---

## 🛠️ Comandos Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Reiniciar servicio
docker-compose restart

# Detener servicio
docker-compose down

# Actualizar después de cambios
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Ver estado
docker-compose ps

# Ver estadísticas de recursos
docker stats openproject-mcp-server

# Entrar al contenedor
docker-compose exec openproject-mcp bash
```

---

## 🔧 Troubleshooting Rápido

### El contenedor no inicia
```bash
# Ver logs detallados
docker-compose logs
```

### Error de conexión a OpenProject
```bash
# Verificar variables
docker-compose exec openproject-mcp env | grep OPENPROJECT

# Probar conexión manual
curl -H "Authorization: Basic $(echo -n 'apikey:TU_API_KEY' | base64)" \
  https://tu-openproject.com/api/v3
```

### Puerto 8000 ocupado
```bash
# Cambiar puerto en .env
HTTP_PORT=8080

# O en docker-compose.yml
ports:
  - "8080:8000"
```

---

## 📊 Arquitectura del Contenedor

```
┌─────────────────────────────────────┐
│   Docker Container                  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Python 3.11 (slim)          │  │
│  │                              │  │
│  │  ┌────────────────────────┐  │  │
│  │  │  server_http.py        │  │  │
│  │  │  (FastAPI + Uvicorn)   │  │  │
│  │  └──────────┬─────────────┘  │  │
│  │             │                │  │
│  │  ┌──────────▼─────────────┐  │  │
│  │  │  openproject_mcp.py    │  │  │
│  │  │  (OpenProject Client)  │  │  │
│  │  └──────────┬─────────────┘  │  │
│  │             │                │  │
│  └─────────────┼────────────────┘  │
│                │                   │
└────────────────┼───────────────────┘
                 │
                 ▼
         OpenProject API
```

---

## 📈 Recursos del Contenedor

**Uso de memoria:** ~100-150 MB
**Uso de CPU:** ~5-10% (idle)
**Tamaño de imagen:** ~200-300 MB

**Límites configurados:**
- CPU: 1 core máximo
- RAM: 512 MB máximo

Puedes ajustar en `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '1'
      memory: 512M
```

---

## 🔐 Seguridad

### Buenas prácticas:

1. **Siempre usar HTTP Auth en producción:**
   ```bash
   HTTP_AUTH_ENABLED=true
   HTTP_AUTH_PASSWORD=UnPasswordMuySeguro123!
   ```

2. **Restringir CORS:**
   ```bash
   CORS_ORIGINS=https://tu-app.com,https://otro-dominio.com
   ```

3. **Usar HTTPS con reverse proxy:**
   - Nginx
   - Traefik
   - Caddy

4. **No commitear `.env`:**
   Ya está en `.gitignore`, pero verifica.

5. **Rotar API Keys regularmente**

---

## 🚀 Siguientes Pasos

1. ✅ Configura un dominio personalizado
2. ✅ Agrega SSL/TLS (Let's Encrypt)
3. ✅ Configura monitoreo (Prometheus/Grafana)
4. ✅ Implementa backups automáticos
5. ✅ Integra con tu aplicación

---

## �� Más Información

- [DEPLOYMENT.md](DEPLOYMENT.md) - Guía completa de deployment
- [README.md](README.md) - Documentación completa del proyecto
- [OpenProject API](https://www.openproject.org/docs/api/) - Docs de la API

---

**¿Necesitas ayuda?** Abre un issue en GitHub o consulta la documentación completa.

**¡Happy Coding!** 🎉
