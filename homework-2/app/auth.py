"""PBKDF2-SHA256 password storage and signed JWT authentication."""
import os, hmac, hashlib, secrets
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .models import User

SECRET=os.getenv('JWT_SECRET','')
if not SECRET:
    # ephemeral secret for a local demo; configure JWT_SECRET for persistent deployments
    SECRET=secrets.token_urlsafe(48)
ALGORITHM='HS256'
bearer=HTTPBearer(auto_error=False)
def hash_password(password):
    salt=os.urandom(16)
    encoded=hashlib.pbkdf2_hmac('sha256',password.encode(),salt,300_000)
    return f'pbkdf2_sha256$300000${salt.hex()}${encoded.hex()}'
def verify_password(password, encoded):
    try:
        algorithm, iterations, salt, expected=encoded.split('$')
        if algorithm!='pbkdf2_sha256': return False
        calc=hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),int(iterations))
        return hmac.compare_digest(calc, bytes.fromhex(expected))
    except (TypeError,ValueError,AttributeError): return False

def create_token(user):
    return jwt.encode({'sub':str(user.id),'role':user.role,'exp':datetime.now(timezone.utc)+timedelta(hours=8)},SECRET,algorithm=ALGORITHM)
def current_user(credentials:HTTPAuthorizationCredentials|None=Depends(bearer),db:Session=Depends(get_db)):
    if not credentials: raise HTTPException(401,'未提供認證 Token')
    try:
        payload=jwt.decode(credentials.credentials,SECRET,algorithms=[ALGORITHM])
        user=db.get(User,int(payload['sub']))
    except (jwt.PyJWTError,ValueError,TypeError,KeyError): raise HTTPException(401,'Token 無效或已過期')
    if not user or not user.active: raise HTTPException(401,'帳號不存在或已停用')
    return user

def admin_only(user:User=Depends(current_user)):
    if user.role!='admin':raise HTTPException(403,'此功能限教務管理者使用')
    return user

def require_student(user):
    if user.role!='student' or user.student_id is None:raise HTTPException(403,'此功能限學生帳號使用')
    return user.student_id
