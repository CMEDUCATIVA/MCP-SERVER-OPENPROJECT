#!/bin/bash
# Script de instalación automática para OpenProject MCP Server
# Ubuntu/Debian 20.04+

set -e  # Salir si hay error

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}➜${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""
}

# Banner
clear
echo ""
echo "  ╔═══════════════════════════════════════════╗"
echo "  ║   OpenProject MCP Server - Installer     ║"
echo "  ║   Instalación Automática v1.0            ║"
echo "  ╚═══════════════════════════════════════════╝"
echo ""

# Verificar que se ejecuta en Ubuntu/Debian
if [[ ! -f /etc/debian_version ]]; then
    print_error "Este script solo funciona en Ubuntu/Debian"
    exit 1
fi

# Verificar que NO se ejecuta como root
if [[ $EUID -eq 0 ]]; then
   print_error "No ejecutes este script como root"
   echo "Usa: ./install.sh (sin sudo)"
   exit 1
fi

# Variables de configuración
INSTALL_DIR="/opt/openproject-mcp-server"
SERVICE_NAME="openproject-mcp"
CURRENT_USER=$(whoami)

print_header "Paso 1: Verificación de requisitos"

# Verificar Python 3.10+
print_info "Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [[ $(echo "$PYTHON_VERSION >= 3.10" | bc -l) -eq 1 ]] 2>/dev/null || [[ "$PYTHON_VERSION" == "3.10" ]] || [[ "$PYTHON_VERSION" > "3.10" ]]; then
        print_success "Python $PYTHON_VERSION encontrado"
    else
        print_warning "Python $PYTHON_VERSION es menor a 3.10"
        print_info "Se instalará Python 3.10..."
        sudo apt update
        sudo apt install -y python3.10 python3.10-venv
    fi
else
    print_warning "Python no encontrado, instalando..."
    sudo apt update
    sudo apt install -y python3.10 python3.10-venv
fi

print_header "Paso 2: Instalación de dependencias del sistema"

print_info "Instalando dependencias..."
sudo apt update
sudo apt install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    git \
    curl \
    nano \
    ufw

print_success "Dependencias instaladas"

print_header "Paso 3: Configuración del proyecto"

# Verificar si ya existe instalación
if [[ -d "$INSTALL_DIR" ]]; then
    print_warning "El directorio $INSTALL_DIR ya existe"
    read -p "¿Deseas sobrescribir? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        print_info "Haciendo backup de configuración anterior..."
        if [[ -f "$INSTALL_DIR/.env" ]]; then
            sudo cp "$INSTALL_DIR/.env" "$INSTALL_DIR/.env.backup.$(date +%Y%m%d-%H%M%S)"
            print_success "Backup creado"
        fi
        sudo rm -rf "$INSTALL_DIR"
    else
        print_error "Instalación cancelada"
        exit 1
    fi
fi

# Crear directorio
print_info "Creando directorio de instalación..."
sudo mkdir -p "$INSTALL_DIR"
sudo chown -R $CURRENT_USER:$CURRENT_USER "$INSTALL_DIR"

# Copiar archivos al directorio de instalación
print_info "Copiando archivos..."
if [[ -f "openproject_mcp.py" ]]; then
    # Ejecutando desde el directorio del proyecto
    cp openproject_mcp.py "$INSTALL_DIR/"
    cp server_http.py "$INSTALL_DIR/"
    cp requirements.txt "$INSTALL_DIR/"
    [[ -f ".env.production" ]] && cp .env.production "$INSTALL_DIR/"
    [[ -f "pyproject.toml" ]] && cp pyproject.toml "$INSTALL_DIR/"
    print_success "Archivos copiados desde directorio actual"
else
    print_error "No se encontraron los archivos del proyecto"
    print_info "Por favor ejecuta este script desde el directorio del proyecto"
    exit 1
fi

cd "$INSTALL_DIR"

print_header "Paso 4: Creación de entorno virtual"

print_info "Creando entorno virtual..."
python3 -m venv .venv
print_success "Entorno virtual creado"

print_info "Activando entorno virtual..."
source .venv/bin/activate
print_success "Entorno virtual activado"

print_header "Paso 5: Instalación de dependencias Python"

print_info "Actualizando pip..."
pip install --upgrade pip --quiet

print_info "Instalando dependencias (esto puede tomar 2-3 minutos)..."
pip install -r requirements.txt --quiet
print_success "Dependencias instaladas"

print_header "Paso 6: Verificación y corrección de código"

print_info "Verificando imports en server_http.py..."

# Fix conocido: GZIPMiddleware vs GZipMiddleware
if grep -q "from fastapi.middleware.gzip import GZIPMiddleware" server_http.py; then
    print_warning "Detectado import incorrecto de GZIPMiddleware"
    print_info "Aplicando fix..."
    sed -i 's/from fastapi.middleware.gzip import GZIPMiddleware/from starlette.middleware.gzip import GZipMiddleware/g' server_http.py
    sed -i 's/GZIPMiddleware/GZipMiddleware/g' server_http.py
    print_success "Fix aplicado"
else
    print_success "Imports correctos"
fi

print_header "Paso 7: Configuración de variables de entorno"

if [[ ! -f ".env" ]]; then
    print_info "Creando archivo de configuración..."

    # Solicitar datos al usuario
    echo ""
    read -p "Ingresa la URL de OpenProject (ej: https://openproject.example.com): " OPENPROJECT_URL
    read -p "Ingresa tu API Key de OpenProject: " OPENPROJECT_API_KEY
    echo ""
    read -p "¿Habilitar autenticación HTTP? (s/n) [s]: " ENABLE_AUTH
    ENABLE_AUTH=${ENABLE_AUTH:-s}

    if [[ $ENABLE_AUTH =~ ^[Ss]$ ]]; then
        read -p "Usuario para HTTP Auth [admin]: " HTTP_USER
        HTTP_USER=${HTTP_USER:-admin}
        read -sp "Contraseña para HTTP Auth: " HTTP_PASS
        echo ""
        HTTP_AUTH_ENABLED="true"
    else
        HTTP_AUTH_ENABLED="false"
        HTTP_USER="admin"
        HTTP_PASS="changeme"
    fi

    read -p "Puerto del servidor [8000]: " HTTP_PORT
    HTTP_PORT=${HTTP_PORT:-8000}

    # Crear archivo .env
    cat > .env << EOF
# OpenProject Connection
OPENPROJECT_URL=$OPENPROJECT_URL
OPENPROJECT_API_KEY=$OPENPROJECT_API_KEY

# HTTP Server
HTTP_HOST=0.0.0.0
HTTP_PORT=$HTTP_PORT

# Security
HTTP_AUTH_ENABLED=$HTTP_AUTH_ENABLED
HTTP_AUTH_USERNAME=$HTTP_USER
HTTP_AUTH_PASSWORD=$HTTP_PASS

# CORS
CORS_ENABLED=true
CORS_ORIGINS=*

# Rate Limiting
RATE_LIMIT=100/minute

# Compression
GZIP_ENABLED=true
GZIP_MIN_SIZE=1000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
TEST_CONNECTION_ON_STARTUP=true
EOF

    chmod 600 .env
    print_success "Configuración creada"
else
    print_success "Archivo .env ya existe"
fi

print_header "Paso 8: Prueba de funcionamiento"

print_info "Probando servidor (5 segundos)..."

# Ejecutar servidor en background
python server_http.py > /tmp/openproject-mcp-test.log 2>&1 &
SERVER_PID=$!

# Esperar a que inicie
sleep 5

# Verificar que esté corriendo
if kill -0 $SERVER_PID 2>/dev/null; then
    # Probar health check
    if curl -s http://localhost:${HTTP_PORT:-8000}/health > /dev/null 2>&1; then
        print_success "Servidor funcionando correctamente"
    else
        print_warning "Servidor corriendo pero health check falló"
        cat /tmp/openproject-mcp-test.log
    fi

    # Detener servidor de prueba
    kill $SERVER_PID 2>/dev/null || true
else
    print_error "Error al iniciar servidor"
    cat /tmp/openproject-mcp-test.log
    exit 1
fi

print_header "Paso 9: Configuración como servicio systemd"

print_info "Creando servicio systemd..."

sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null << EOF
[Unit]
Description=OpenProject MCP Server
After=network.target
Documentation=https://github.com/tu-usuario/openproject-mcp-server

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/.venv/bin"
EnvironmentFile=$INSTALL_DIR/.env
ExecStart=$INSTALL_DIR/.venv/bin/python $INSTALL_DIR/server_http.py

# Restart policy
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

[Install]
WantedBy=multi-user.target
EOF

print_success "Servicio creado"

print_info "Habilitando servicio..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
print_success "Servicio habilitado para inicio automático"

print_info "Iniciando servicio..."
sudo systemctl start $SERVICE_NAME
sleep 3

if sudo systemctl is-active --quiet $SERVICE_NAME; then
    print_success "Servicio iniciado correctamente"
else
    print_error "Error al iniciar servicio"
    sudo systemctl status $SERVICE_NAME
    exit 1
fi

print_header "Paso 10: Configuración de firewall"

print_info "Configurando firewall UFW..."
sudo ufw allow ${HTTP_PORT:-8000}/tcp > /dev/null 2>&1 || true
print_success "Puerto ${HTTP_PORT:-8000} permitido en firewall"

print_header "✅ Instalación Completada"

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                           ║${NC}"
echo -e "${GREEN}║  ✨ OpenProject MCP Server instalado exitosamente! ✨    ║${NC}"
echo -e "${GREEN}║                                                           ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Información de deployment
print_info "📊 Información de la instalación:"
echo ""
echo "  📁 Directorio:    $INSTALL_DIR"
echo "  🐍 Python:        $(python3 --version)"
echo "  🔧 Servicio:      $SERVICE_NAME"
echo "  🌐 Puerto:        ${HTTP_PORT:-8000}"
echo "  👤 Usuario:       $CURRENT_USER"
echo ""

print_info "🌐 Endpoints disponibles:"
echo ""
echo "  • API Root:       http://localhost:${HTTP_PORT:-8000}/"
echo "  • Health Check:   http://localhost:${HTTP_PORT:-8000}/health"
echo "  • Swagger Docs:   http://localhost:${HTTP_PORT:-8000}/docs"
echo "  • ReDoc:          http://localhost:${HTTP_PORT:-8000}/redoc"
echo ""

print_info "📝 Comandos útiles:"
echo ""
echo "  # Ver estado del servicio"
echo "  sudo systemctl status $SERVICE_NAME"
echo ""
echo "  # Ver logs en tiempo real"
echo "  sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "  # Reiniciar servicio"
echo "  sudo systemctl restart $SERVICE_NAME"
echo ""
echo "  # Detener servicio"
echo "  sudo systemctl stop $SERVICE_NAME"
echo ""
echo "  # Editar configuración"
echo "  nano $INSTALL_DIR/.env"
echo "  sudo systemctl restart $SERVICE_NAME"
echo ""

print_info "🧪 Verificar instalación:"
echo ""
echo "  curl http://localhost:${HTTP_PORT:-8000}/health"
echo ""

# Test final
print_info "🔍 Ejecutando test final..."
if curl -s http://localhost:${HTTP_PORT:-8000}/health | grep -q "healthy"; then
    print_success "Health check OK!"
    echo ""
    curl -s http://localhost:${HTTP_PORT:-8000}/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:${HTTP_PORT:-8000}/health
    echo ""
else
    print_warning "Health check no respondió. Verifica los logs:"
    echo "  sudo journalctl -u $SERVICE_NAME -n 50"
fi

print_info "📚 Documentación:"
echo ""
echo "  • Manual de instalación: $INSTALL_DIR/MANUAL-INSTALL.md"
echo "  • Guía de deployment:    $INSTALL_DIR/DEPLOYMENT.md"
echo "  • README:                $INSTALL_DIR/README.md"
echo ""

print_success "¡Instalación completada! 🎉"
echo ""

# Preguntar si quiere instalar Nginx
read -p "¿Deseas instalar Nginx como reverse proxy? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    print_info "Para configurar Nginx, sigue las instrucciones en:"
    echo "  $INSTALL_DIR/MANUAL-INSTALL.md (sección Nginx)"
fi

echo ""
print_info "Para más ayuda, consulta la documentación o abre un issue en GitHub"
echo ""
