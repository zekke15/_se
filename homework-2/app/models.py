from datetime import datetime, timezone
from sqlalchemy import String, Integer, ForeignKey, DateTime, UniqueConstraint, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

def now(): return datetime.now(timezone.utc)
class Student(Base):
    __tablename__='students'
    id: Mapped[int]=mapped_column(primary_key=True)
    student_id: Mapped[str]=mapped_column(String(25),unique=True,index=True)
    name: Mapped[str]=mapped_column(String(60))
    email: Mapped[str]=mapped_column(String(120),unique=True)
    department: Mapped[str]=mapped_column(String(80),default='資訊工程學系')
    enrollment_year: Mapped[int]=mapped_column(Integer,default=2024)
    phone: Mapped[str]=mapped_column(String(40),default='')
    active: Mapped[bool]=mapped_column(Boolean,default=True)
class User(Base):
    __tablename__='users'
    id: Mapped[int]=mapped_column(primary_key=True)
    username: Mapped[str]=mapped_column(String(60),unique=True)
    password_hash: Mapped[str]=mapped_column(String(300))
    role: Mapped[str]=mapped_column(String(12),default='student')
    student_id: Mapped[int|None]=mapped_column(ForeignKey('students.id'),nullable=True)
    active: Mapped[bool]=mapped_column(Boolean,default=True)
class Course(Base):
    __tablename__='courses'
    id: Mapped[int]=mapped_column(primary_key=True)
    code: Mapped[str]=mapped_column(String(30),unique=True)
    name: Mapped[str]=mapped_column(String(120))
    credits: Mapped[int]=mapped_column(Integer)
    capacity: Mapped[int]=mapped_column(Integer,default=40)
    teacher: Mapped[str]=mapped_column(String(80),default='')
    semester: Mapped[str]=mapped_column(String(25),default='115-1')
    day: Mapped[int]=mapped_column(Integer)
    start: Mapped[int]=mapped_column(Integer)
    length: Mapped[int]=mapped_column(Integer)
    room: Mapped[str]=mapped_column(String(80),default='')
    category: Mapped[str]=mapped_column(String(50),default='專業選修')
    active: Mapped[bool]=mapped_column(Boolean,default=True)
class Enrollment(Base):
    __tablename__='enrollments'
    __table_args__=(UniqueConstraint('student_id','course_id',name='uq_student_course'),)
    id: Mapped[int]=mapped_column(primary_key=True)
    student_id: Mapped[int]=mapped_column(ForeignKey('students.id'))
    course_id: Mapped[int]=mapped_column(ForeignKey('courses.id'))
    status: Mapped[str]=mapped_column(String(20),default='enrolled')
    grade: Mapped[int|None]=mapped_column(Integer,nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Leave(Base):
    __tablename__='leaves'
    id: Mapped[int]=mapped_column(primary_key=True)
    student_id: Mapped[int]=mapped_column(ForeignKey('students.id'))
    date: Mapped[str]=mapped_column(String(10))
    kind: Mapped[str]=mapped_column(String(20))
    period: Mapped[str]=mapped_column(String(30))
    reason: Mapped[str]=mapped_column(Text)
    status: Mapped[str]=mapped_column(String(20),default='待審核')
class Announcement(Base):
    __tablename__='announcements'
    id: Mapped[int]=mapped_column(primary_key=True)
    title: Mapped[str]=mapped_column(String(200))
    date: Mapped[str]=mapped_column(String(10))
    department: Mapped[str]=mapped_column(String(70),default='教務處')
