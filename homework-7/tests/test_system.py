"""Real HTTP API system tests: Nginx reverse proxy -> FastAPI -> PostgreSQL."""
import uuid
from datetime import date, timedelta
import httpx


def test_real_http_api_crud(base_url):
    tag = 'SYSTEM-' + uuid.uuid4().hex[:10]
    with httpx.Client(base_url=base_url, timeout=15, follow_redirects=True) as client:
        health = client.get('/api/health')
        assert health.status_code == 200, health.text
        assert health.json()['database'] == 'connected'
        task_id, expense_id = None, None
        try:
            task = client.post('/api/tasks', json={
                'title': tag, 'course': '測試專用',
                'due_date': (date.today()+timedelta(days=5)).isoformat(), 'priority': 'high'
            })
            assert task.status_code == 201, task.text
            task_id = task.json()['id']
            assert any(t['id'] == task_id and t['title'] == tag for t in client.get('/api/tasks').json())
            patch = client.patch(f'/api/tasks/{task_id}', json={'completed': True})
            assert patch.status_code == 200 and patch.json()['completed'] is True
            expense = client.post('/api/expenses', json={
                'description': tag, 'category': '學習', 'amount': 17,
                'spent_on': date.today().isoformat()
            })
            assert expense.status_code == 201, expense.text
            expense_id = expense.json()['id']
            assert any(x['id'] == expense_id for x in client.get('/api/expenses').json())
            stats = client.get('/api/stats')
            assert stats.status_code == 200
            assert 'tasks_pending' in stats.json() and 'month_expenses' in stats.json()
            assert client.post('/api/expenses', json={
                'description': tag, 'amount': -100, 'spent_on': date.today().isoformat()
            }).status_code == 422
        finally:
            if task_id is not None:
                assert client.delete(f'/api/tasks/{task_id}').status_code == 204
            if expense_id is not None:
                assert client.delete(f'/api/expenses/{expense_id}').status_code == 204
