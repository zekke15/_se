from pathlib import Path
from fastapi import FastAPI,Depends,HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .schemas import LoginIn
from .auth import verify_password,create_token
from .routers import courses,students,enrollment,services

app=FastAPI(title='Smart Campus API',description='獨立的智慧校務系統示範專案，不連接真實學校資料',version='2.0.0')
app.include_router(courses.router)
app.include_router(students.router)
app.include_router(enrollment.router)
app.include_router(services.router)
STATIC=Path(__file__).parent/'static'
app.mount('/static',StaticFiles(directory=STATIC),name='static')
@app.get('/',include_in_schema=False)
def home():return FileResponse(STATIC/'index.html')
@app.get('/health')
def health():return {'status':'ok'}
@app.post('/login')
def login(payload:LoginIn,db:Session=Depends(get_db)):
    u=db.scalar(select(User).where(User.username==payload.username))
    if not u or not u.active or not verify_password(payload.password,u.password_hash):raise HTTPException(401,'帳號或密碼錯誤')
    return {'access_token':create_token(u),'token_type':'bearer','role':u.role}
