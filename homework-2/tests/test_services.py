def test_leave(client,student_auth):
    payload={'date':'2026-11-09','kind':'事假','period':'第1節','reason':'家庭事項'}
    assert client.post('/leaves',json=payload,headers=student_auth).status_code==201
    assert len(client.get('/leaves',headers=student_auth).json())==1
def test_bad_leave_date(client,student_auth):
    assert client.post('/leaves',json={'date':'2026-02-31','kind':'事假','period':'上午','reason':'家庭事項'},headers=student_auth).status_code==422
def test_profile(client,student_auth):
    assert client.put('/me',json={'name':'改名','email':'new@example.com','phone':'0900000000'},headers=student_auth).status_code==200
    assert client.get('/me',headers=student_auth).json()['name']=='改名'
def test_grade_permissions(client,student_auth):
    assert client.put('/enrollments/1/grade',json={'grade':90},headers=student_auth).status_code==403
def test_announcements(client,student_auth):assert client.get('/announcements',headers=student_auth).status_code==200
