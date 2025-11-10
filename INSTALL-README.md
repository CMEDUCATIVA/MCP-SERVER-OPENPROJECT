# 🚀 Instalación Rápida - OpenProject MCP Server

Tres métodos de instalación disponibles. Elige el que prefieras:

---

## ⚡ Método 1: Script Automático (Más Fácil) ⭐

**Instalación en 1 comando:**

```bash
chmod +x install.sh
./install.sh
```

**¿Qué hace?**
- ✅ Instala todas las dependencias
- ✅ Crea entorno virtual
- ✅ Configura el servicio systemd
- ✅ Configura firewall
- ✅ Ejecuta tests automáticos
- ✅ ¡Todo listo en 5 minutos!

**Requisitos:**
- Ubuntu 20.04+ o Debian 11+
- Acceso sudo
- Conexión a internet

---

## 🐳 Método 2: Docker/Easypanel (Recomendado para producción)

### **Para Easypanel:**
Ver guía completa: **[EASYPANEL-SETUP.md](EASYPANEL-SETUP.md)**

**Quick start:**
1. Create Application → Docker Compose
2. Pega contenido de `docker-compose.yml`
3. Configura variables de entorno
4. Deploy!

### **Para Docker Compose:**
Ver guía: **[DOCKER-QUICKSTART.md](DOCKER-QUICKSTART.md)**

```bash
cp .env.production .env
nano .env  # Configurar
docker-compose up -d
```

---

## 📦 Método 3: Manual (Control total)

Ver guía detallada: **[MANUAL-INSTALL.md](MANUAL-INSTALL.md)**

**Pasos básicos:**
```bash
# 1. Instalar dependencias
sudo apt install python3.10-venv

# 2. Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar paquetes
pip install -r requirements.txt

# 4. Configurar
cp .env.production .env
nano .env

# 5. Ejecutar
python server_http.py
```

---

## 📋 Comparación de Métodos

| Característica | Script Auto | Docker/Easypanel | Manual |
|----------------|-------------|------------------|--------|
| Dificultad | ⭐ Fácil | ⭐⭐ Media | ⭐⭐⭐ Avanzada |
| Tiempo | 5 min | 5 min | 15 min |
| Servicio systemd | ✅ Sí | ❌ No | Manual |
| Portabilidad | ❌ No | ✅ Sí | ❌ No |
| Actualizaciones | Manual | Fácil | Manual |
| Control | Medio | Bajo | Alto |

---

## 🎯 Recomendaciones

### **Usa Script Automático si:**
- ✅ Tienes un servidor Ubuntu/Debian dedicado
- ✅ Quieres instalación rápida y sencilla
- ✅ Necesitas servicio systemd automático
- ✅ Prefieres instalación nativa (sin Docker)

### **Usa Docker/Easypanel si:**
- ✅ Usas Easypanel
- ✅ Quieres portabilidad
- ✅ Prefieres contenedores
- ✅ Necesitas deployment rápido
- ✅ Quieres aislamiento del sistema

### **Usa Instalación Manual si:**
- ✅ Quieres control total
- ✅ Necesitas personalización avanzada
- ✅ Estás debuggeando problemas
- ✅ Quieres entender cada paso

---

## ✅ Post-Instalación

### **Verificar que funciona:**

```bash
# Health check
curl http://localhost:8000/health

# Esperado:
# {"status":"healthy","openproject_connected":true}

# Ver documentación
http://localhost:8000/docs
```

### **Comandos útiles (Script Auto/Manual):**

```bash
# Ver logs
sudo journalctl -u openproject-mcp -f

# Reiniciar
sudo systemctl restart openproject-mcp

# Estado
sudo systemctl status openproject-mcp
```

### **Comandos útiles (Docker):**

```bash
# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Estado
docker-compose ps
```

---

## 🔧 Troubleshooting Rápido

### **No funciona el health check**

```bash
# Ver logs
sudo journalctl -u openproject-mcp -n 50
# o
docker-compose logs

# Verificar variables de entorno
cat .env
```

### **Error de conexión a OpenProject**

```bash
# Probar API Key manualmente
curl -H "Authorization: Basic $(echo -n 'apikey:TU_API_KEY' | base64)" \
  https://tu-openproject.com/api/v3
```

### **Puerto ocupado**

```bash
# Cambiar puerto en .env
HTTP_PORT=8080

# Reiniciar
sudo systemctl restart openproject-mcp
```

---

## 📚 Documentación Completa

| Guía | Descripción |
|------|-------------|
| [MANUAL-INSTALL.md](MANUAL-INSTALL.md) | Instalación manual paso a paso |
| [DOCKER-QUICKSTART.md](DOCKER-QUICKSTART.md) | Quick start con Docker |
| [EASYPANEL-SETUP.md](EASYPANEL-SETUP.md) | Deployment en Easypanel |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Guía completa de deployment |
| [README.md](README.md) | Documentación del proyecto |

---

## 🆘 ¿Necesitas Ayuda?

1. Revisa la documentación apropiada arriba
2. Busca en los logs: `sudo journalctl -u openproject-mcp -n 100`
3. Verifica las variables de entorno
4. Abre un issue en GitHub con los logs

---

## 🎉 ¡Listo!

Elige tu método preferido y comienza a usar OpenProject MCP Server.

**¡Happy Coding!** 🚀
