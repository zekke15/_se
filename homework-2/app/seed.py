"""Idempotent fictional demo data. Run once after `alembic upgrade head`."""
from sqlalchemy import select
from .database import SessionLocal
from .models import User,Student,Course,Enrollment,Announcement
from .auth import hash_password
COURSES=[
('CS301','演算法',3,45,'王教授',1,2,3,'A302','專業必修'),
('CS302','作業系統',3,45,'陳教授',2,3,3,'B201','專業必修'),
('CS303','資料庫系統',3,40,'李教授',3,2,3,'A305','專業必修'),
('CS304','計算機網路',3,40,'張教授',4,4,3,'B301','專業選修'),
('CS305','人工智慧導論',3,40,'林教授',5,2,3,'智慧教室','專業選修'),
('CS306','網頁程式設計',3,40,'吳教授',1,6,3,'電腦教室','專業選修'),
('CS307','資訊安全',3,35,'劉教授',2,3,3,'A401','專業選修'),
('GE101','科技與生活',2,55,'許教授',4,1,2,'綜合大樓','通識課程'),
('GE102','海洋文化概論',2,50,'蔡教授',3,6,2,'綜合大樓','通識課程'),
('PE101','體育與健康',1,45,'鄭老師',5,7,2,'體育館','共同必修')]
def seed():
    with SessionLocal() as db:
        student=db.scalar(select(Student).where(Student.student_id=='DEMO2026001'))
        if not student:
            student=Student(student_id='DEMO2026001',name='林同學',email='demo@example.com',department='資訊工程學系',enrollment_year=2024)
            db.add(student);db.flush()
        for username,password,role,sid in [('demo','demo123','student',student.id),('admin','admin123','admin',None)]:
            if not db.scalar(select(User).where(User.username==username)):
                db.add(User(username=username,password_hash=hash_password(password),role=role,student_id=sid))
        for code,name,credits,capacity,teacher,day,start,length,room,category in COURSES:
            if not db.scalar(select(Course).where(Course.code==code)):
                db.add(Course(code=code,name=name,credits=credits,capacity=capacity,teacher=teacher,day=day,start=start,length=length,room=room,category=category))
        if not db.scalar(select(Announcement)):
            for d,title,dept in [('2026-11-05','選課結果確認通知（展示）','教務處'),('2026-11-02','圖書館開放時間公告（展示）','圖書館')]:db.add(Announcement(date=d,title=title,department=dept))
        db.commit()
        if not db.scalar(select(Enrollment).where(Enrollment.student_id==student.id)):
            for code in ['CS301','CS302','CS303','CS305','GE101']:
                course=db.scalar(select(Course).where(Course.code==code))
                db.add(Enrollment(student_id=student.id,course_id=course.id))
            db.commit()
        print('示範資料建立完成：demo/demo123 (學生)、admin/admin123 (教務)')
if __name__=='__main__':seed()
