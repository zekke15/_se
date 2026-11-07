"""Backend unit tests (FastAPI TestClient with isolated in-memory SQLite)."""
from datetime import date, timedelta
import pytest

TASK = {'title': '單元測試任務', 'course': '軟體工程', 'due_date': '2026-12-01', 'priority': 'high'}
EXPENSE = {'description': '測試午餐', 'category': '餐飲', 'amount': 120, 'spent_on': '2026-11-07'}


def test_health(client):
    r = client.get('/api/health')
    assert r.status_code == 200
    assert r.json() == {'status': 'ok', 'service': 'api', 'database': 'connected'}


def test_task_create_list_complete_uncomplete_delete(client):
    assert client.get('/api/tasks').json() == []
    created = client.post('/api/tasks', json=TASK)
    assert created.status_code == 201
    task = created.json()
    assert task['title'] == TASK['title'] and task['completed'] is False
    task_id = task['id']
    assert len(client.get('/api/tasks').json()) == 1
    assert client.get('/api/stats').json()['tasks_pending'] == 1
    assert client.patch(f'/api/tasks/{task_id}', json={'completed': True}).json()['completed'] is True
    assert client.get('/api/stats').json()['tasks_pending'] == 0
    assert client.patch(f'/api/tasks/{task_id}', json={'completed': False}).json()['completed'] is False
    assert client.delete(f'/api/tasks/{task_id}').status_code == 204
    assert client.get('/api/tasks').json() == []


@pytest.mark.parametrize('payload', [
    {**TASK, 'title': ''},
    {**TASK, 'title': 'x' * 161},
    {**TASK, 'priority': 'urgent'},
    {**TASK, 'due_date': 'tomorrow'},
])
def test_invalid_tasks_rejected(client, payload):
    assert client.post('/api/tasks', json=payload).status_code == 422
    assert client.get('/api/tasks').json() == []


def test_task_not_found(client):
    assert client.patch('/api/tasks/9999', json={'completed': True}).status_code == 404
    assert client.delete('/api/tasks/9999').status_code == 404


def test_expense_create_list_delete(client):
    result = client.post('/api/expenses', json=EXPENSE)
    assert result.status_code == 201
    expense_id = result.json()['id']
    assert result.json()['amount'] == 120
    assert len(client.get('/api/expenses').json()) == 1
    assert client.delete(f'/api/expenses/{expense_id}').status_code == 204
    assert client.get('/api/expenses').json() == []


@pytest.mark.parametrize('amount', [-1, 0, 1_000_001, 'not-a-number'])
def test_invalid_expense_rejected(client, amount):
    assert client.post('/api/expenses', json={**EXPENSE, 'amount': amount}).status_code == 422


def test_expense_not_found(client):
    assert client.delete('/api/expenses/9999').status_code == 404


def test_overdue_stats(client):
    past = (date.today() - timedelta(days=2)).isoformat()
    result = client.post('/api/tasks', json={**TASK, 'due_date': past})
    assert result.status_code == 201
    assert client.get('/api/stats').json()['tasks_overdue'] == 1
    assert client.patch(f"/api/tasks/{result.json()['id']}", json={'completed': True}).status_code == 200
    assert client.get('/api/stats').json()['tasks_overdue'] == 0
