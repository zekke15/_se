from app.auth import hash_password,verify_password
def test_hash():
    s=hash_password('secret');assert 'secret' not in s;assert verify_password('secret',s)
def test_wrong_password():assert not verify_password('no','invalid')
def test_login(client):assert client.post('/login',json={'username':'student','password':'pass123'}).status_code==200
def test_login_fail(client):assert client.post('/login',json={'username':'student','password':'wrong'}).status_code==401
def test_missing_auth(client):assert client.get('/me').status_code==401
