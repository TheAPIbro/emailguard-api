# 🚂 GUÍA DE DEPLOYMENT EN RAILWAY - PASO A PASO

Esta guía te llevará de 0 a API en producción en **10 minutos**.

## ✅ REQUISITOS PREVIOS

- [ ] Cuenta de GitHub (gratis)
- [ ] Cuenta de Railway (gratis - https://railway.app)
- [ ] Git instalado en tu computadora

---

## 📦 PASO 1: SUBIR CÓDIGO A GITHUB

### Opción A: Desde terminal (si sabes usar Git)

```bash
# Navegar a la carpeta del proyecto
cd email-validator-api

# Inicializar repositorio
git init

# Añadir archivos
git add .

# Crear commit
git commit -m "Initial commit - EmailGuard API"

# Crear repo en GitHub y subir
# Ve a github.com/new y crea repo "emailguard-api"
git remote add origin https://github.com/TU_USUARIO/emailguard-api.git
git branch -M main
git push -u origin main
```

### Opción B: Subir manualmente (más fácil)

1. Ve a https://github.com/new
2. Nombre del repo: `emailguard-api`
3. Descripción: "Email validation API"
4. Público o Privado (tú decides)
5. Click "Create repository"
6. Click "uploading an existing file"
7. Arrastra todos los archivos del proyecto
8. Click "Commit changes"

✅ **Checkpoint:** Tu código está en GitHub

---

## 🚂 PASO 2: DEPLOYMENT EN RAILWAY

### 2.1 Crear cuenta

1. Ve a https://railway.app
2. Click "Login"
3. Conecta con GitHub
4. Autoriza Railway

### 2.2 Crear nuevo proyecto

1. Click "New Project"
2. Selecciona "Deploy from GitHub repo"
3. Busca `emailguard-api`
4. Click en tu repositorio

### 2.3 Configuración automática

Railway detecta automáticamente:
- ✅ Dockerfile
- ✅ Puerto 8000
- ✅ Dependencias en requirements.txt

**No necesitas configurar nada.** Railway lo hace todo.

### 2.4 Deployment

1. Railway empieza a construir automáticamente
2. Verás logs en tiempo real
3. Espera 2-3 minutos

**Logs que verás:**
```
Building...
Installing dependencies...
Starting server...
✓ Deployed successfully
```

### 2.5 Obtener URL pública

1. En Railway, click en tu servicio
2. Click en "Settings"
3. Scroll hasta "Domains"
4. Click "Generate Domain"
5. Te da URL tipo: `emailguard-api-production-xxxx.up.railway.app`

✅ **Checkpoint:** Tu API está VIVA en internet

---

## 🧪 PASO 3: PROBAR TU API

### Método 1: Navegador

Abre en tu navegador:
```
https://tu-url-de-railway.up.railway.app/docs
```

Deberías ver la documentación Swagger interactiva.

### Método 2: Curl (Terminal)

```bash
# Generar API key
curl -X POST https://tu-url-de-railway.up.railway.app/generate-key

# Te devolverá algo como:
# {"api_key": "demo_abc123...", "plan": "free", ...}

# Validar un email
curl -X POST https://tu-url-de-railway.up.railway.app/validate \
  -H "X-API-Key: demo_abc123..." \
  -H "Content-Type: application/json" \
  -d '{"email": "test@gmail.com", "check_smtp": false}'
```

### Método 3: Python

```python
import requests

# Generar key
response = requests.post("https://tu-url-de-railway.up.railway.app/generate-key")
api_key = response.json()["api_key"]

# Validar email
response = requests.post(
    "https://tu-url-de-railway.up.railway.app/validate",
    headers={"X-API-Key": api_key},
    json={"email": "test@gmail.com", "check_smtp": False}
)

print(response.json())
```

✅ **Si todo funciona, continúa al siguiente paso**

---

## 💳 PASO 4: COSTES DE RAILWAY

Railway tiene un modelo freemium:

**Plan Gratuito (Hobby):**
- $5 USD gratis/mes
- Suficiente para ~500,000 requests/mes
- Tu API estará activa 24/7

**Cuando necesites más:**
- $5/mes por 500,000 requests adicionales
- Pagas solo lo que usas

**Cómo monitorear:**
1. Click en tu proyecto en Railway
2. Click "Usage"
3. Ves cuánto llevas gastado

**💡 Tip:** Con el plan gratis puedes operar tranquilamente los primeros 2-3 meses mientras consigues clientes.

---

## 🔄 PASO 5: ACTUALIZAR TU API (después de cambios)

Cada vez que hagas cambios en el código:

```bash
# Hacer cambios en main.py u otro archivo
# ...

# Commit y push a GitHub
git add .
git commit -m "Descripción del cambio"
git push

# Railway detecta el cambio automáticamente y redeploy
# Tarda ~2 minutos
```

**No tienes que hacer nada en Railway.** El deploy es automático.

---

## 🐛 TROUBLESHOOTING

### Problema: "Application failed to start"

**Solución:**
1. Ve a Railway → tu proyecto → "Deployments"
2. Click en el deployment fallido
3. Lee los logs (te dirán el error)
4. Común: dependencia faltante en requirements.txt

### Problema: "Connection refused"

**Solución:**
- Verifica que el Dockerfile usa `PORT` variable de entorno
- Railway asigna puerto automáticamente
- Nuestro Dockerfile ya está configurado correctamente

### Problema: "API muy lenta"

**Solución:**
- Railway free tier tiene CPU limitada
- Desactiva `check_smtp` en validaciones (es lo más lento)
- O reduce `SMTP_TIMEOUT` a 3 segundos

### Problema: "Excedí el límite gratis"

**Solución:**
- Railway te cobra automáticamente vía tarjeta
- O pausa el proyecto hasta siguiente mes
- $5 adicionales te dan 500k requests más

---

## 📊 PASO 6: MONITOREO BÁSICO

Railway incluye métricas gratis:

1. Ve a tu proyecto
2. Click "Metrics"
3. Verás:
   - CPU usage
   - Memory usage
   - Network (requests/segundo)
   - Uptime

**Alerta si:**
- CPU >80% constantemente → Necesitas upgrade
- Memory >400MB → Posible memory leak
- Requests >1000/segundo → ¡Éxito! Hora de escalar

---

## 🎯 SIGUIENTE PASO: PUBLICAR EN RAPIDAPI

Una vez tu API está en Railway, es hora de monetizar.

**Guía rápida:**

1. Ve a https://rapidapi.com/developer
2. Regístrate como Provider
3. Click "Add New API"
4. Nombre: "EmailGuard - Email Validation"
5. Base URL: `https://tu-url-de-railway.up.railway.app`
6. Import OpenAPI: pega `/openapi.json` de tu API
7. Configura pricing:
   - Free: 100/mes - $0
   - Basic: 5000/mes - $9.99
   - Pro: 25000/mes - $29.99
8. Publica

**RapidAPI maneja:**
- ✅ Pagos (Stripe integrado)
- ✅ Facturación automática
- ✅ API keys (adicionales a las tuyas)
- ✅ Analytics
- ✅ Marketplace con 4M usuarios

**Tú recibes:**
- 80% de cada suscripción
- Pagos mensuales vía PayPal/transferencia

---

## ✅ CHECKLIST FINAL

- [ ] Código en GitHub
- [ ] API deployed en Railway
- [ ] URL pública funcionando
- [ ] Documentación accesible en /docs
- [ ] API key de prueba generada
- [ ] Validación funcionando
- [ ] Métricas monitoreadas

**🎉 ¡FELICIDADES!** Tu API está lista para vender.

---

## 💰 RECORDATORIO: PROYECCIÓN DE INGRESOS

**Mes 1:** €60 (€9.99 × 3 clientes + €29.99 × 1)
**Mes 2:** €200 (más conversiones)
**Mes 3:** €500+ (crecimiento orgánico)

**Costes Railway:** €5-10/mes

**Ganancia neta mes 3:** €490/mes (~€5,880/año)

---

## 🆘 NECESITAS AYUDA?

- **Docs Railway:** https://docs.railway.app
- **Docs FastAPI:** https://fastapi.tiangolo.com
- **RapidAPI Support:** support@rapidapi.com

**¡Mucha suerte! 🚀**
