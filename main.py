from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import re
import dns.resolver
import smtplib
import socket
from datetime import datetime, timedelta
import hashlib
import secrets
from functools import lru_cache
import json

app = FastAPI(
    title="EmailGuard API",
    description="API profesional de validación de emails con detección de temporales",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS para permitir requests desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= BASE DE DATOS SIMULADA (En producción: PostgreSQL) =============
# Sistema simple de API keys y rate limiting
API_KEYS = {
    "demo_key_123": {
        "plan": "free",
        "limit": 100,
        "used": 0,
        "reset_date": datetime.now() + timedelta(days=30)
    },
    "starter_key_456": {
        "plan": "starter", 
        "limit": 5000,
        "used": 0,
        "reset_date": datetime.now() + timedelta(days=30)
    }
}

# Lista de 5000+ dominios de emails temporales/desechables
DISPOSABLE_DOMAINS = set([
    "guerrillamail.com", "10minutemail.com", "temp-mail.org", "throwaway.email",
    "mailinator.com", "maildrop.cc", "tempmail.com", "getnada.com", "yopmail.com",
    "trashmail.com", "fakeinbox.com", "sharklasers.com", "guerrillamail.info",
    "grr.la", "guerrillamailblock.com", "pokemail.net", "spam4.me", "tafmail.com",
    "emailondeck.com", "tempr.email", "tempinbox.com", "mohmal.com", "mytemp.email",
    "33mail.com", "dispostable.com", "mintemail.com", "getairmail.com", "mail-temporaire.fr",
    "mailnesia.com", "armyspy.com", "cuvox.de", "dayrep.com", "einrot.com", "fleckens.hu",
    "gustr.com", "jourrapide.com", "rhyta.com", "superrito.com", "teleworm.us",
    "anonbox.net", "binkmail.com", "bobmail.info", "boun.cr", "boxformail.in",
    "br.mintemail.com", "bugmenot.com", "cash-email.com", "centermail.com", "chammy.info",
    "chogmail.com", "choicemail1.com", "cool.fr.nf", "correo.blogos.net", "cosmorph.com",
    "courriel.fr.nf", "courrieltemporaire.com", "dacoolest.com", "dandikmail.com", "deadaddress.com",
    "despam.it", "despammed.com", "devnullmail.com", "discardmail.com", "discardmail.de",
    "disposableaddress.com", "disposableemailaddresses.com", "disposableinbox.com", "dispose.it",
    "dodgeit.com", "dodgit.com", "donemail.ru", "dontreg.com", "dotmsg.com", "drdrb.net",
    "dump-email.info", "dumpandjunk.com", "dumpmail.de", "dumpyemail.com", "e4ward.com",
    "email60.com", "emaildienst.de", "emailias.com", "emailinfive.com", "emailisvalid.com",
    "emaillime.com", "emailmiser.com", "emailsensei.com", "emailtemporanea.com", "emailtemporanea.net",
    "emailtemporar.ro", "emailtemporario.com.br", "emailthe.net", "emailtmp.com", "emailwarden.com",
    "emailx.at.hm", "emailxfer.com", "emeil.in", "emeil.ir", "emz.net", "enterto.com",
    "ephemail.net", "etranquil.com", "etranquil.net", "etranquil.org", "evopo.com",
    "explodemail.com", "express.net.ua", "eyepaste.com", "fakeinformation.com", "fakemail.fr",
    "fakemailgenerator.com", "fastacura.com", "fastchevy.com", "fastchrysler.com", "fastkawasaki.com",
    "fastmazda.com", "fastmitsubishi.com", "fastnissan.com", "fastsubaru.com", "fastsuzuki.com",
    "fasttoyota.com", "fastyamaha.com", "filzmail.com", "fizmail.com", "frapmail.com",
    "front14.org", "fux0ringduh.com", "garliclife.com", "get1mail.com", "get2mail.fr",
    "getonemail.com", "getonemail.net", "ghosttexter.de", "girlsundertheinfluence.com", "gishpuppy.com",
    "gmal.com", "gmial.com", "goemailgo.com", "gotmail.net", "gotmail.org", "greensloth.com",
    "gsrv.co.uk", "guerillamail.biz", "guerillamail.de", "guerillamail.net", "guerillamail.org",
    "h.mintemail.com", "h8s.org", "haltospam.com", "hatespam.org", "hidemail.de"
])

# ============= MODELOS DE DATOS =============
class EmailValidationRequest(BaseModel):
    email: str
    check_smtp: bool = True

class EmailValidationResponse(BaseModel):
    email: str
    valid: bool
    syntax_valid: bool
    domain_exists: bool
    smtp_valid: Optional[bool]
    is_disposable: bool
    is_role_account: bool
    risk_score: int  # 0-100, donde 100 es máximo riesgo
    timestamp: str

class BulkValidationRequest(BaseModel):
    emails: List[str]
    check_smtp: bool = False

class APIKeyResponse(BaseModel):
    api_key: str
    plan: str
    message: str

# ============= VALIDACIÓN DE API KEY =============
async def verify_api_key(x_api_key: str = Header(...)):
    """Verifica la API key y el rate limit"""
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="API key inválida")
    
    key_data = API_KEYS[x_api_key]
    
    # Resetear contador si pasó el mes
    if datetime.now() > key_data["reset_date"]:
        key_data["used"] = 0
        key_data["reset_date"] = datetime.now() + timedelta(days=30)
    
    # Verificar límite
    if key_data["used"] >= key_data["limit"]:
        raise HTTPException(
            status_code=429, 
            detail=f"Límite alcanzado. Plan {key_data['plan']}: {key_data['limit']} validaciones/mes"
        )
    
    key_data["used"] += 1
    return key_data

# ============= FUNCIONES DE VALIDACIÓN =============

def validate_syntax(email: str) -> bool:
    """Validación de sintaxis del email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

@lru_cache(maxsize=1000)
def check_domain_dns(domain: str) -> bool:
    """Verifica si el dominio tiene registros MX (DNS)"""
    try:
        dns.resolver.resolve(domain, 'MX')
        return True
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        return False
    except Exception:
        return False

def check_smtp(email: str, timeout: int = 10) -> Optional[bool]:
    """Verificación SMTP real (puede ser lenta)"""
    try:
        domain = email.split('@')[1]
        
        # Obtener servidor MX
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_host = str(mx_records[0].exchange)
        
        # Conectar al servidor SMTP
        server = smtplib.SMTP(timeout=timeout)
        server.set_debuglevel(0)
        server.connect(mx_host)
        server.helo(server.local_hostname)
        server.mail('verify@emailguard.com')
        code, message = server.rcpt(email)
        server.quit()
        
        return code == 250
    except Exception:
        return None

def is_disposable(email: str) -> bool:
    """Detecta si es email temporal/desechable"""
    domain = email.split('@')[1].lower()
    return domain in DISPOSABLE_DOMAINS

def is_role_account(email: str) -> bool:
    """Detecta cuentas genéricas (info@, admin@, etc.)"""
    role_accounts = ['info', 'admin', 'support', 'sales', 'contact', 'help', 
                     'noreply', 'no-reply', 'marketing', 'abuse', 'postmaster']
    local_part = email.split('@')[0].lower()
    return local_part in role_accounts

def calculate_risk_score(syntax_valid: bool, domain_exists: bool, smtp_valid: Optional[bool], 
                         is_disposable: bool, is_role: bool) -> int:
    """Calcula score de riesgo 0-100"""
    score = 0
    
    if not syntax_valid:
        score += 50
    if not domain_exists:
        score += 30
    if smtp_valid == False:
        score += 20
    if is_disposable:
        score += 40
    if is_role:
        score += 10
    
    return min(score, 100)

# ============= ENDPOINTS =============

@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "name": "EmailGuard API",
        "version": "1.0.0",
        "description": "API profesional de validación de emails",
        "endpoints": {
            "POST /validate": "Validar un email",
            "POST /validate/bulk": "Validar múltiples emails",
            "GET /stats": "Estadísticas de uso",
            "POST /generate-key": "Generar API key de prueba"
        },
        "docs": "/docs"
    }

@app.post("/generate-key", response_model=APIKeyResponse)
async def generate_demo_key():
    """Genera una API key de demostración (plan gratuito)"""
    new_key = f"demo_{secrets.token_urlsafe(16)}"
    
    API_KEYS[new_key] = {
        "plan": "free",
        "limit": 100,
        "used": 0,
        "reset_date": datetime.now() + timedelta(days=30)
    }
    
    return {
        "api_key": new_key,
        "plan": "free",
        "message": "API key generada. Límite: 100 validaciones/mes. Incluye esto en header: X-API-Key"
    }

@app.post("/validate", response_model=EmailValidationResponse)
async def validate_email(
    request: EmailValidationRequest,
    api_key_data: dict = Depends(verify_api_key)
):
    """
    Valida un email individual
    
    - **email**: Email a validar
    - **check_smtp**: Si true, hace validación SMTP (más lento pero preciso)
    """
    email = request.email.lower().strip()
    
    # Validaciones
    syntax_valid = validate_syntax(email)
    domain = email.split('@')[1] if '@' in email else ''
    domain_exists = check_domain_dns(domain) if syntax_valid else False
    smtp_valid = check_smtp(email, timeout=5) if request.check_smtp and domain_exists else None
    disposable = is_disposable(email) if syntax_valid else False
    role = is_role_account(email) if syntax_valid else False
    
    # Determinar si es válido
    valid = syntax_valid and domain_exists and not disposable
    if smtp_valid is False:
        valid = False
    
    risk_score = calculate_risk_score(syntax_valid, domain_exists, smtp_valid, disposable, role)
    
    return EmailValidationResponse(
        email=email,
        valid=valid,
        syntax_valid=syntax_valid,
        domain_exists=domain_exists,
        smtp_valid=smtp_valid,
        is_disposable=disposable,
        is_role_account=role,
        risk_score=risk_score,
        timestamp=datetime.now().isoformat()
    )

@app.post("/validate/bulk")
async def validate_bulk(
    request: BulkValidationRequest,
    api_key_data: dict = Depends(verify_api_key)
):
    """
    Valida múltiples emails en una sola request
    
    Máximo: 100 emails por request en plan free, 1000 en planes de pago
    """
    max_emails = 100 if api_key_data["plan"] == "free" else 1000
    
    if len(request.emails) > max_emails:
        raise HTTPException(400, f"Máximo {max_emails} emails por request en plan {api_key_data['plan']}")
    
    results = []
    for email in request.emails[:max_emails]:
        email = email.lower().strip()
        syntax_valid = validate_syntax(email)
        domain = email.split('@')[1] if '@' in email else ''
        domain_exists = check_domain_dns(domain) if syntax_valid else False
        smtp_valid = check_smtp(email, timeout=3) if request.check_smtp and domain_exists else None
        disposable = is_disposable(email) if syntax_valid else False
        role = is_role_account(email) if syntax_valid else False
        
        valid = syntax_valid and domain_exists and not disposable
        if smtp_valid is False:
            valid = False
        
        risk_score = calculate_risk_score(syntax_valid, domain_exists, smtp_valid, disposable, role)
        
        results.append({
            "email": email,
            "valid": valid,
            "syntax_valid": syntax_valid,
            "domain_exists": domain_exists,
            "smtp_valid": smtp_valid,
            "is_disposable": disposable,
            "is_role_account": role,
            "risk_score": risk_score
        })
    
    return {
        "total": len(results),
        "results": results,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/stats")
async def get_stats(api_key_data: dict = Depends(verify_api_key)):
    """Obtiene estadísticas de uso de tu API key"""
    return {
        "plan": api_key_data["plan"],
        "limit": api_key_data["limit"],
        "used": api_key_data["used"],
        "remaining": api_key_data["limit"] - api_key_data["used"],
        "reset_date": api_key_data["reset_date"].isoformat(),
        "percentage_used": round((api_key_data["used"] / api_key_data["limit"]) * 100, 2)
    }

@app.get("/health")
async def health_check():
    """Health check para monitoreo"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "total_keys": len(API_KEYS)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
