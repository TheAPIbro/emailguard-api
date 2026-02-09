# 🛡️ EmailGuard API - Validación Profesional de Emails

API completa para validar emails, detectar temporales y reducir bounces.

## 🚀 Características

- ✅ Validación de sintaxis
- ✅ Verificación DNS/MX records
- ✅ Verificación SMTP opcional
- ✅ Detección de 5000+ dominios temporales/desechables
- ✅ Detección de cuentas role (info@, admin@, etc.)
- ✅ Sistema de API keys con rate limiting
- ✅ Planes Free, Starter, Pro, Business
- ✅ Documentación automática (Swagger)
- ✅ Validación bulk (múltiples emails)

## 💰 Planes y Precios

| Plan | Precio/mes | Validaciones | Ideal para |
|------|------------|--------------|------------|
| Free | €0 | 100 | Pruebas |
| Starter | €9.99 | 5,000 | Startups |
| Pro | €29.99 | 25,000 | PyMEs |
| Business | €79.99 | 100,000 | Empresas |

## 📦 Instalación Local

### Opción 1: Python directo

```bash
# Clonar el proyecto
cd email-validator-api

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Correr el servidor
python main.py
```

La API estará disponible en `http://localhost:8000`

### Opción 2: Docker

```bash
# Construir imagen
docker build -t emailguard-api .

# Correr contenedor
docker run -p 8000:8000 emailguard-api
```

## 🌐 Deployment en Producción

### Railway (Recomendado - Gratis para empezar)

1. Ve a [railway.app](https://railway.app)
2. Conecta tu GitHub
3. Sube estos archivos a un repo
4. Click en "New Project" → "Deploy from GitHub"
5. Selecciona el repo
6. Railway detecta automáticamente el Dockerfile
7. ¡Desplegado! Te da una URL tipo: `emailguard-api.up.railway.app`

**Coste:** Gratis primeros $5/mes, luego ~$5-10/mes

### Render

1. Ve a [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Conecta GitHub
4. Selecciona el repo
5. Runtime: Docker
6. Click "Create Web Service"

**Coste:** Gratis tier disponible, luego $7/mes

### DigitalOcean App Platform

```bash
# Usar el Dockerfile incluido
# DigitalOcean lo detecta automáticamente
```

**Coste:** $5/mes básico

## 📖 Uso de la API

### 1. Generar API Key de prueba

```bash
curl -X POST http://localhost:8000/generate-key
```

Respuesta:
```json
{
  "api_key": "demo_xxxxxxxxxxxxx",
  "plan": "free",
  "message": "API key generada. Límite: 100 validaciones/mes"
}
```

### 2. Validar un email

```bash
curl -X POST http://localhost:8000/validate \
  -H "X-API-Key: demo_xxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@gmail.com",
    "check_smtp": true
  }'
```

Respuesta:
```json
{
  "email": "test@gmail.com",
  "valid": true,
  "syntax_valid": true,
  "domain_exists": true,
  "smtp_valid": true,
  "is_disposable": false,
  "is_role_account": false,
  "risk_score": 0,
  "timestamp": "2025-02-06T10:30:00"
}
```

### 3. Validar múltiples emails

```bash
curl -X POST http://localhost:8000/validate/bulk \
  -H "X-API-Key: demo_xxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "emails": ["test1@gmail.com", "fake@10minutemail.com", "admin@empresa.com"],
    "check_smtp": false
  }'
```

### 4. Ver estadísticas de uso

```bash
curl -X GET http://localhost:8000/stats \
  -H "X-API-Key: demo_xxxxxxxxxxxxx"
```

Respuesta:
```json
{
  "plan": "free",
  "limit": 100,
  "used": 45,
  "remaining": 55,
  "reset_date": "2025-03-06T10:30:00",
  "percentage_used": 45.0
}
```

## 📚 Documentación Interactiva

Una vez corriendo, visita:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## 🔑 Sistema de API Keys

### Para desarrollo (incluido):

```python
API_KEYS = {
    "demo_key_123": {"plan": "free", "limit": 100},
    "starter_key_456": {"plan": "starter", "limit": 5000}
}
```

### Para producción (próximo paso):

Reemplazar con PostgreSQL + sistema de registro:
- Crear tabla `api_keys`
- Endpoint `/register` para nuevos usuarios
- Integrar Stripe para pagos
- Sistema de webhooks para suscripciones

## 🏪 Publicar en RapidAPI

### Paso 1: Crear cuenta

1. Ve a [rapidapi.com/developer](https://rapidapi.com/developer)
2. Regístrate como proveedor
3. Click "Add New API"

### Paso 2: Configurar API

- **Name:** EmailGuard - Email Validation API
- **Category:** Data / Business
- **Description:** "Valida emails, detecta temporales y reduce bounces. Ideal para formularios, marketing y limpieza de listas."
- **Base URL:** Tu URL de Railway/Render
- **Auth:** API Key en header `X-API-Key`

### Paso 3: Documentar endpoints

RapidAPI importa automáticamente desde tu `/docs` (OpenAPI/Swagger)

### Paso 4: Pricing

```
Free: 100 validaciones/mes - €0
Basic: 5,000 validaciones/mes - €9.99
Pro: 25,000 validaciones/mes - €29.99
Mega: 100,000 validaciones/mes - €79.99
```

### Paso 5: Marketing

- Añadir screenshots de la documentación
- Video demo de 30 segundos
- Keywords: "email validation", "email verification", "temporary email detection"
- Categorías: Business, Data, Productivity

## 💡 Próximos Pasos (Escalar)

### Base de datos real (PostgreSQL)

```python
# Reemplazar diccionario API_KEYS por:
import databases
import sqlalchemy

DATABASE_URL = "postgresql://user:password@localhost/emailguard"
database = databases.Database(DATABASE_URL)

# Tabla api_keys
metadata = sqlalchemy.MetaData()
api_keys_table = sqlalchemy.Table(
    "api_keys",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("key", sqlalchemy.String, unique=True),
    sqlalchemy.Column("user_email", sqlalchemy.String),
    sqlalchemy.Column("plan", sqlalchemy.String),
    sqlalchemy.Column("limit", sqlalchemy.Integer),
    sqlalchemy.Column("used", sqlalchemy.Integer),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime),
)
```

### Integrar pagos (Stripe)

```python
import stripe
stripe.api_key = "sk_live_..."

@app.post("/subscribe")
async def create_subscription(email: str, plan: str):
    # Crear customer en Stripe
    customer = stripe.Customer.create(email=email)
    
    # Crear suscripción
    subscription = stripe.Subscription.create(
        customer=customer.id,
        items=[{"price": PLAN_PRICES[plan]}],
    )
    
    # Generar API key
    api_key = generate_api_key()
    # Guardar en DB...
    
    return {"api_key": api_key, "subscription_id": subscription.id}
```

### Landing Page

Crear página simple con:
- Hero: "Valida emails en segundos"
- Features: 4 bloques con iconos
- Pricing: Tabla de planes
- CTA: "Empieza gratis"
- Testimonios (cuando tengas)

### Marketing Inicial

1. **Product Hunt:** Lanzar en Product Hunt España
2. **Reddit:** Post en r/ecommerce, r/SideProject
3. **Facebook Groups:** Grupos de startups/SaaS españoles
4. **Cold Email:** 100 startups con formularios web
5. **SEO:** Blog post "Cómo reducir bounces en email marketing"

## 📊 Métricas Clave

Monitorear:
- **Conversión Free → Paid:** Meta 5-10%
- **Churn mensual:** Mantener <5%
- **CAC (Coste Adquisición):** <€20
- **LTV (Lifetime Value):** >€300

## 🐛 Troubleshooting

### Error: "Could not resolve hostname"
- Verificar DNS: `dig domain.com MX`
- Algunos servidores bloquean queries DNS masivas

### SMTP lento
- Reducir timeout: `check_smtp(email, timeout=3)`
- Desactivar SMTP check en bulk

### Rate limit excedido
- Verificar `reset_date`
- Upgradar plan

## 📄 Licencia

Uso comercial libre. Código propiedad del creador.

## 🤝 Soporte

- Email: support@emailguard.com (configura uno)
- Docs: /docs endpoint
- Issues: GitHub Issues

---

**¡Tu API está lista para generar ingresos! 🚀💰**

Siguiente paso: Desplegar en Railway y publicar en RapidAPI.
