from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Student
from ..schemas import StudentCreate,ProfileUpdate
from ..auth import current_user,admin_only,require_student
router=APIRouter(tags=['學生'])
@router.post('/students/',status_code=201)
def add_student(data:StudentCreate,db:Session=Depends(get_db),_admin=Depends(admin_only)):
    if db.scalar(select(Student).where(Student.student_id==data.student_id)):raise HTTPException(409,'學號重複')
    if db.scalar(select(Student).where(Student.email==data.email)):raise HTTPException(409,'Email 重複')
    s=Student(**data.model_dump());db.add(s);db.commit();db.refresh(s)
    return {'id':s.id,'student_id':s.student_id,'name':s.name,'email':s.email}
@router.get('/me')
def me(db:Session=Depends(get_db),user=Depends(current_user)):
    if user.role=='admin':return {'username':user.username,'role':'admin'}
    s=db.get(Student,require_student(user))
    if not s:raise HTTPException(404,'學生不存在')
    return {'username':user.username,'role':'student','student_id':s.student_id,'name':s.name,'email':s.email,'department':s.department,'enrollment_year':s.enrollment_year,'phone':s.phone}
@router.put('/me')
def update_me(data:ProfileUpdate,db:Session=Depends(get_db),user=Depends(current_user)):
    s=db.get(Student,require_student(user))
    duplicate=db.scalar(select(Student).where(Student.email==data.email,Student.id!=s.id))
    if duplicate:raise HTTPException(409,'Email 已被使用')
    s.name=data.name;s.email=data.email;s.phone=data.phone;db.commit()
    return {'message':'個人資料已更新'}
