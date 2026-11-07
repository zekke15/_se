def course_id(client,headers,code):return next(x['id'] for x in client.get('/courses/',headers=headers).json() if x['code']==code)
def test_enroll_duplicate_conflict_and_drop(client,student_auth):
    a=course_id(client,student_auth,'C1');b=course_id(client,student_auth,'C2')
    assert client.post(f'/enrollments/{a}',headers=student_auth).status_code==201
    assert client.post(f'/enrollments/{a}',headers=student_auth).status_code==409
    assert client.post(f'/enrollments/{b}',headers=student_auth).status_code==409
    assert client.delete(f'/enrollments/{a}',headers=student_auth).status_code==200
    assert client.post(f'/enrollments/{b}',headers=student_auth).status_code==201
def test_course_not_found(client,student_auth):assert client.post('/enrollments/999',headers=student_auth).status_code==404
def test_student_cannot_list_all(client,student_auth):assert client.get('/enrollments/list',headers=student_auth).status_code==403
def test_admin_cannot_enroll_as_student(client,admin_auth):assert client.post('/enrollments/1',headers=admin_auth).status_code==403
def test_course_capacity(client,student_auth,admin_auth):
    c=course_id(client,student_auth,'C1')
    assert client.post(f'/enrollments/{c}',headers=student_auth).status_code==201
    new=client.post('/students/',headers=admin_auth,json={'student_id':'STUDENT02','name':'另一個學生','email':'s2@example.com','enrollment_year':2024})
    assert new.status_code==201
    from app.database import get_db
    from app.main import app
    from app.models import User
    from app.auth import hash_password
    db=next(app.dependency_overrides[get_db]())
    try:
        db.add(User(username='another',password_hash=hash_password('pass456'),role='student',student_id=new.json()['id']))
        db.commit()
    finally:
        db.close()
    login=client.post('/login',json={'username':'another','password':'pass456'}).json()
    second={'Authorization':'Bearer '+login['access_token']}
    assert client.post(f'/enrollments/{c}',headers=second).status_code==409
