from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..database import get_db
from ..models import Enrollment,Course,Student
from ..auth import current_user,admin_only,require_student
router=APIRouter(prefix='/enrollments',tags=['選課'])
@router.get('/mine')
def mine(db:Session=Depends(get_db),user=Depends(current_user)):
    sid=require_student(user)
    rows=db.scalars(select(Enrollment).where(Enrollment.student_id==sid,Enrollment.status=='enrolled')).all()
    return [{'id':e.id,'course_id':e.course_id,'grade':e.grade} for e in rows]
@router.get('/list')
def all_enrollments(db:Session=Depends(get_db),_admin=Depends(admin_only)):
    return [{'id':e.id,'student_id':e.student_id,'course_id':e.course_id,'status':e.status,'grade':e.grade} for e in db.scalars(select(Enrollment)).all()]
@router.post('/{course_id}',status_code=201)
def enroll(course_id:int,db:Session=Depends(get_db),user=Depends(current_user)):
    sid=require_student(user)
    c=db.get(Course,course_id)
    if not c or not c.active:raise HTTPException(404,'找不到該課程')
    existing=db.scalar(select(Enrollment).where(Enrollment.student_id==sid,Enrollment.course_id==course_id))
    if existing and existing.status=='enrolled':raise HTTPException(409,'不可重複選課')
    count=db.query(Enrollment).filter(Enrollment.course_id==course_id,Enrollment.status=='enrolled').count()
    if count>=c.capacity:raise HTTPException(409,'名額已滿')
    selected=db.scalars(select(Course).join(Enrollment,Enrollment.course_id==Course.id).where(Enrollment.student_id==sid,Enrollment.status=='enrolled')).all()
    if any(other.semester==c.semester and other.day==c.day and other.start<c.start+c.length and c.start<other.start+other.length for other in selected):
        raise HTTPException(409,'課程時間衝堂')
    if existing:existing.status='enrolled';existing.grade=None
    else:db.add(Enrollment(student_id=sid,course_id=course_id))
    try:db.commit()
    except IntegrityError:db.rollback();raise HTTPException(409,'選課衝突，請重試')
    return {'message':'選課成功','course_id':course_id}
@router.delete('/{course_id}')
def drop(course_id:int,db:Session=Depends(get_db),user=Depends(current_user)):
    sid=require_student(user)
    e=db.scalar(select(Enrollment).where(Enrollment.student_id==sid,Enrollment.course_id==course_id,Enrollment.status=='enrolled'))
    if not e:raise HTTPException(404,'尚未選修該課程')
    e.status='dropped';db.commit();return {'message':'退選成功'}
