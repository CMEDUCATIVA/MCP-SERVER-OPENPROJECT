#!/bin/bash
# Script para construir y probar el contenedor Docker

set -e  # Salir si hay error

echo "🐳 OpenProject MCP Server - Build & Test"
echo "=========================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}➜${NC} $1"
}

# 1. Verificar archivos necesarios
print_info "Verificando archivos necesarios..."
if [[ ! -f "Dockerfile" ]]; then
    print_error "Dockerfile no encontrado"
    exit 1
fi

if [[ ! -f "docker-compose.yml" ]]; then
    print_error "docker-compose.yml no encontrado"
    exit 1
fi

if [[ ! -f "requirements.txt" ]]; then
    print_error "requirements.txt no encontrado"
    exit 1
fi

if [[ ! -f "openproject_mcp.py" ]]; then
    print_error "openproject_mcp.py no encontrado"
    exit 1
fi

if [[ ! -f "server_http.py" ]]; then
    print_error "server_http.py no encontrado"
    exit 1
fi

print_success "Todos los archivos necesarios están presentes"

# 2. Verificar variables de entorno
print_info "Verificando variables de entorno..."
if [[ ! -f ".env" ]]; then
    print_error "Archivo .env no encontrado"
    echo ""
    echo "Por favor crea un archivo .env con:"
    echo "  OPENPROJECT_URL=https://tu-instancia.com"
    echo "  OPENPROJECT_API_KEY=tu-api-key"
    echo ""
    echo "Puedes copiar .env.production como base:"
    echo "  cp .env.production .env"
    exit 1
fi

# Verificar que las variables requeridas estén configuradas
source .env
if [[ -z "$OPENPROJECT_URL" ]]; then
    print_error "OPENPROJECT_URL no está configurado en .env"
    exit 1
fi

if [[ -z "$OPENPROJECT_API_KEY" ]]; then
    print_error "OPENPROJECT_API_KEY no está configurado en .env"
    exit 1
fi

print_success "Variables de entorno configuradas"

# 3. Construir imagen Docker
print_info "Construyendo imagen Docker..."
docker build -t openproject-mcp-server:latest . || {
    print_error "Error al construir la imagen Docker"
    exit 1
}
print_success "Imagen Docker construida exitosamente"

# 4. Verificar el tamaño de la imagen
IMAGE_SIZE=$(docker images openproject-mcp-server:latest --format "{{.Size}}")
print_info "Tamaño de la imagen: $IMAGE_SIZE"

# 5. Iniciar contenedor con docker-compose
print_info "Iniciando contenedor con docker-compose..."
docker-compose down 2>/dev/null || true
docker-compose up -d || {
    print_error "Error al iniciar el contenedor"
    exit 1
}
print_success "Contenedor iniciado"

# 6. Esperar a que el contenedor esté listo
print_info "Esperando a que el servidor esté listo..."
sleep 5

# Verificar que el contenedor esté corriendo
if ! docker-compose ps | grep -q "Up"; then
    print_error "El contenedor no está corriendo"
    echo ""
    echo "Logs del contenedor:"
    docker-compose logs
    exit 1
fi

# 7. Probar health check
print_info "Probando health check..."
MAX_RETRIES=10
RETRY=0

while [[ $RETRY -lt $MAX_RETRIES ]]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Health check exitoso"
        break
    fi
    RETRY=$((RETRY+1))
    if [[ $RETRY -eq $MAX_RETRIES ]]; then
        print_error "Health check falló después de $MAX_RETRIES intentos"
        echo ""
        echo "Logs del contenedor:"
        docker-compose logs
        exit 1
    fi
    echo "  Reintentando... ($RETRY/$MAX_RETRIES)"
    sleep 2
done

# 8. Probar endpoint raíz
print_info "Probando endpoint raíz..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
if [[ "$HTTP_CODE" == "200" ]]; then
    print_success "Endpoint raíz respondió correctamente (HTTP $HTTP_CODE)"
else
    print_error "Endpoint raíz falló (HTTP $HTTP_CODE)"
fi

# 9. Probar conexión a OpenProject
print_info "Probando conexión a OpenProject..."
RESPONSE=$(curl -s -X POST http://localhost:8000/tools/test_connection \
    -H "Content-Type: application/json" \
    -d '{}')

if echo "$RESPONSE" | grep -q "successful"; then
    print_success "Conexión a OpenProject exitosa"
else
    print_error "Conexión a OpenProject falló"
    echo "Respuesta: $RESPONSE"
fi

# 10. Mostrar información del contenedor
echo ""
echo "=========================================="
print_success "¡Build y tests completados exitosamente!"
echo "=========================================="
echo ""
echo "📊 Información del Deployment:"
echo "  • Contenedor: $(docker-compose ps --format '{{.Name}}' | head -n 1)"
echo "  • Estado: $(docker-compose ps --format '{{.Status}}' | head -n 1)"
echo "  • Puerto: 8000"
echo "  • Image Size: $IMAGE_SIZE"
echo ""
echo "🌐 Endpoints disponibles:"
echo "  • API Root:        http://localhost:8000/"
echo "  • Health Check:    http://localhost:8000/health"
echo "  • Swagger Docs:    http://localhost:8000/docs"
echo "  • ReDoc:           http://localhost:8000/redoc"
echo "  • OpenAPI Schema:  http://localhost:8000/openapi.json"
echo ""
echo "📝 Comandos útiles:"
echo "  • Ver logs:        docker-compose logs -f"
echo "  • Reiniciar:       docker-compose restart"
echo "  • Detener:         docker-compose down"
echo "  • Estado:          docker-compose ps"
echo ""
print_info "Para ver los logs en tiempo real:"
echo "  docker-compose logs -f"
