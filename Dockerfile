# Dockerfile para OpenProject MCP Server
# Optimizado para producción con multi-stage build

# Stage 1: Builder
FROM python:3.11-slim as builder

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Crear virtual environment e instalar dependencias
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Metadata
LABEL maintainer="your.email@example.com"
LABEL description="OpenProject MCP Server - HTTP REST API"
LABEL version="1.0.0"

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 -s /bin/bash appuser

# Establecer directorio de trabajo
WORKDIR /app

# Copiar virtual environment del builder
COPY --from=builder /opt/venv /opt/venv

# Copiar archivos de la aplicación
COPY --chown=appuser:appuser openproject_mcp.py .
COPY --chown=appuser:appuser server_http.py .
COPY --chown=appuser:appuser requirements.txt .

# Configurar PATH para usar el venv
ENV PATH="/opt/venv/bin:$PATH"

# Variables de entorno por defecto
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV LOG_LEVEL=INFO
ENV LOG_FORMAT=json
ENV HTTP_HOST=0.0.0.0
ENV HTTP_PORT=8000

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Comando por defecto: ejecutar servidor HTTP
CMD ["python", "server_http.py"]
