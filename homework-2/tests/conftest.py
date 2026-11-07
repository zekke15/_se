import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from app.database import Base,get_db
from app.main import app
from app.models import Student,User,Course,Enrollment
from app.auth import hash_password
@pytest.fixture
def client():
    engine=create_engine('sqlite://',connect_args={'check_same_thread':False},poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Testing=sessionmaker(bind=engine,expire_on_commit=False)
    with Testing() as db:
        s=Student(student_id='TEST01',name='測試學生',email='test@example.com',department='資工',enrollment_year=2024)
        db.add(s);db.flush()
        db.add_all([User(username='student',password_hash=hash_password('pass123'),role='student',student_id=s.id),User(username='admin',password_hash=hash_password('adminpass'),role='admin')])
        db.add_all([Course(code='C1',name='演算法',credits=3,capacity=1,day=1,start=2,length=3),Course(code='C2',name='衝堂課',credits=2,capacity=10,day=1,start=3,length=2),Course(code='C3',name='不同時段',credits=2,capacity=10,day=2,start=3,length=2)])
        db.commit()
    def override():
        with Testing() as db:yield db
    app.dependency_overrides[get_db]=override
    with TestClient(app) as c:yield c
    app.dependency_overrides.clear()
    engine.dispose()
@pytest.fixture
def student_auth(client):
    r=client.post('/login',json={'username':'student','password':'pass123'})
    return {'Authorization':'Bearer '+r.json()['access_token']}
@pytest.fixture
def admin_auth(client):
    r=client.post('/login',json={'username':'admin','password':'adminpass'})
    return {'Authorization':'Bearer '+r.json()['access_token']}
