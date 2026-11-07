"""End-to-end API workflow. Optional browser E2E instructions are in README."""
def test_student_course_workflow(client,student_auth):
    courses=client.get('/courses/',headers=student_auth).json()
    c=next(x for x in courses if x['code']=='C3')
    assert client.post(f"/enrollments/{c['id']}",headers=student_auth).status_code==201
    assert any(e['course_id']==c['id'] for e in client.get('/enrollments/mine',headers=student_auth).json())
    assert client.delete(f"/enrollments/{c['id']}",headers=student_auth).status_code==200
    assert not client.get('/enrollments/mine',headers=student_auth).json()
