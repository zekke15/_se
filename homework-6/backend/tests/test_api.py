import os
os.environ['DATABASE_URL'] = 'sqlite:///'

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from app.main import app, Base, get_db


def test_task_and_expense_lifecycle():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    def override_db():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as client:
            assert client.get('/api/health').json()['status'] == 'ok'
            task = client.post('/api/tasks', json={
                'title': '期末報告', 'course': '軟體工程', 'due_date': '2026-12-01', 'priority': 'high'
            })
            assert task.status_code == 201
            tid = task.json()['id']
            assert client.get('/api/stats').json()['tasks_pending'] == 1
            assert client.patch(f'/api/tasks/{tid}', json={'completed': True}).json()['completed'] is True
            assert client.get('/api/stats').json()['tasks_pending'] == 0
            assert client.delete(f'/api/tasks/{tid}').status_code == 204
            assert client.patch(f'/api/tasks/{tid}', json={'completed': False}).status_code == 404
            bad = client.post('/api/expenses', json={'description':'午餐','category':'餐飲','amount':-5,'spent_on':'2026-11-07'})
            assert bad.status_code == 422
            expense = client.post('/api/expenses', json={'description':'午餐','category':'餐飲','amount':120,'spent_on':'2026-11-07'})
            assert expense.status_code == 201
            eid = expense.json()['id']
            assert len(client.get('/api/expenses').json()) == 1
            assert client.delete(f'/api/expenses/{eid}').status_code == 204
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
