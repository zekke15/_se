"""Playwright Chromium E2E, requires a running Docker Compose stack."""
import uuid
from datetime import date, timedelta
import httpx
from playwright.sync_api import Page, expect


def test_web_add_complete_delete_task(page: Page, base_url):
    tag = 'E2E-TASK-' + uuid.uuid4().hex[:10]
    task_id = None
    with httpx.Client(base_url=base_url, timeout=15) as client:
        try:
            page.goto(base_url + '/', wait_until='domcontentloaded')
            expect(page.locator('#connection')).to_contain_text('服務已連線', timeout=15000)
            page.locator('#task-form [name="title"]').fill(tag)
            page.locator('#task-form [name="course"]').fill('系統測試')
            page.locator('#task-form [name="due_date"]').fill((date.today()+timedelta(days=3)).isoformat())
            page.locator('#task-form button[type="submit"]').click()
            row = page.locator('#task-list .entry').filter(has_text=tag)
            expect(row).to_be_visible(timeout=15000)
            matches = [t for t in client.get('/api/tasks').json() if t['title'] == tag]
            assert len(matches) == 1
            task_id = matches[0]['id']
            row.locator('input[type="checkbox"]').check()
            expect(page.locator('#task-list .entry').filter(has_text=tag).locator('input')).to_be_checked(timeout=15000)
            assert next(t for t in client.get('/api/tasks').json() if t['id'] == task_id)['completed'] is True
            page.locator('#task-list .entry').filter(has_text=tag).locator('button.delete').click()
            expect(page.locator('#task-list .entry').filter(has_text=tag)).to_have_count(0, timeout=15000)
            assert all(t['id'] != task_id for t in client.get('/api/tasks').json())
        finally:
            if task_id is not None and any(t['id'] == task_id for t in client.get('/api/tasks').json()):
                client.delete(f'/api/tasks/{task_id}')


def test_web_add_delete_expense(page: Page, base_url):
    tag = 'E2E-EXPENSE-' + uuid.uuid4().hex[:10]
    expense_id = None
    with httpx.Client(base_url=base_url, timeout=15) as client:
        try:
            page.goto(base_url + '/', wait_until='domcontentloaded')
            expect(page.locator('#connection')).to_contain_text('服務已連線', timeout=15000)
            page.locator('#expense-form [name="description"]').fill(tag)
            page.locator('#expense-form [name="amount"]').fill('35')
            page.locator('#expense-form [name="spent_on"]').fill(date.today().isoformat())
            page.locator('#expense-form button[type="submit"]').click()
            expect(page.locator('#expense-list .entry').filter(has_text=tag)).to_be_visible(timeout=15000)
            matches = [e for e in client.get('/api/expenses').json() if e['description'] == tag]
            assert len(matches) == 1
            expense_id = matches[0]['id']
            page.locator('#expense-list .entry').filter(has_text=tag).locator('button.delete').click()
            expect(page.locator('#expense-list .entry').filter(has_text=tag)).to_have_count(0, timeout=15000)
            assert all(e['id'] != expense_id for e in client.get('/api/expenses').json())
        finally:
            if expense_id is not None and any(e['id'] == expense_id for e in client.get('/api/expenses').json()):
                client.delete(f'/api/expenses/{expense_id}')
