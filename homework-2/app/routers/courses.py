from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..database import get_db
from ..models import Course,Enrollment
from ..schemas import CourseCreate
from ..auth import current_user,admin_only
router=APIRouter(prefix='/courses',tags=['課程'])
def view(c,db):
    count=db.query(Enrollment).filter(Enrollment.course_id==c.id,Enrollment.status=='enrolled').count()
    return dict(id=c.id,code=c.code,name=c.name,credits=c.credits,capacity=c.capacity,enrolled=count,teacher=c.teacher,semester=c.semester,day=c.day,start=c.start,length=c.length,room=c.room,category=c.category)
@router.get('/')
def list_courses(db:Session=Depends(get_db),_user=Depends(current_user)):
    return [view(c,db) for c in db.scalars(select(Course).where(Course.active==True).order_by(Course.code)).all()]
@router.post('/',status_code=201)
def create_course(payload:CourseCreate,db:Session=Depends(get_db),_admin=Depends(admin_only)):
    if payload.start+payload.length>13:raise HTTPException(422,'上課節次不可超過第 12 節')
    if db.scalar(select(Course).where(Course.code==payload.code)):raise HTTPException(409,'課程代碼重複')
    c=Course(**payload.model_dump());db.add(c);db.commit();db.refresh(c)
    return view(c,db)
