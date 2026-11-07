from datetime import date
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Leave,Announcement,Enrollment,Course
from ..schemas import LeaveCreate,GradeUpdate
from ..auth import current_user,admin_only,require_student
router=APIRouter(tags=['校務服務'])
@router.get('/announcements')
def announcements(db:Session=Depends(get_db),_user=Depends(current_user)):
    return [{'date':a.date,'title':a.title,'department':a.department} for a in db.scalars(select(Announcement).order_by(Announcement.date.desc())).all()]
@router.get('/leaves')
def leaves(db:Session=Depends(get_db),user=Depends(current_user)):
    sid=require_student(user)
    return [{'id':l.id,'date':l.date,'kind':l.kind,'period':l.period,'reason':l.reason,'status':l.status} for l in db.scalars(select(Leave).where(Leave.student_id==sid).order_by(Leave.id.desc())).all()]
@router.post('/leaves',status_code=201)
def create_leave(payload:LeaveCreate,db:Session=Depends(get_db),user=Depends(current_user)):
    sid=require_student(user)
    try:date.fromisoformat(payload.date)
    except ValueError:raise HTTPException(422,'日期不正確')
    l=Leave(student_id=sid,**payload.model_dump());db.add(l);db.commit();db.refresh(l)
    return {'id':l.id,'status':l.status}
@router.get('/grades')
def grades(db:Session=Depends(get_db),user=Depends(current_user)):
    sid=require_student(user)
    rows=db.execute(select(Enrollment,Course).join(Course,Enrollment.course_id==Course.id).where(Enrollment.student_id==sid,Enrollment.grade.is_not(None))).all()
    return [{'course':c.name,'credits':c.credits,'grade':e.grade,'semester':c.semester} for e,c in rows]
@router.put('/enrollments/{enrollment_id}/grade')
def set_grade(enrollment_id:int,payload:GradeUpdate,db:Session=Depends(get_db),_admin=Depends(admin_only)):
    e=db.get(Enrollment,enrollment_id)
    if not e:raise HTTPException(404,'選課紀錄不存在')
    e.grade=payload.grade;e.status='completed';db.commit();return {'message':'成績已更新'}
