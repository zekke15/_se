def test_admin_only_create_course(client,student_auth,admin_auth):
    data={'code':'NEW','name':'測試','credits':3,'capacity':30,'day':3,'start':1,'length':2}
    assert client.post('/courses/',json=data,headers=student_auth).status_code==403
    assert client.post('/courses/',json=data,headers=admin_auth).status_code==201
    assert client.post('/courses/',json=data,headers=admin_auth).status_code==409
def test_admin_list(client,admin_auth):assert client.get('/enrollments/list',headers=admin_auth).status_code==200
def test_admin_role(client,admin_auth):assert client.get('/me',headers=admin_auth).json()['role']=='admin'
