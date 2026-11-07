"""External tests target a running Compose stack (Nginx -> FastAPI -> Postgres)."""
import os
from urllib.parse import urlsplit
import pytest

@pytest.fixture(scope='session')
def base_url():
    url = os.getenv('TEST_BASE_URL', 'http://127.0.0.1:8080').rstrip('/')
    parsed = urlsplit(url)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname:
        pytest.fail('TEST_BASE_URL must be a valid http(s) URL')
    if parsed.hostname not in ('localhost', '127.0.0.1', '::1') and os.getenv('TEST_ALLOW_REMOTE') != '1':
        pytest.skip('Remote CRUD tests disabled. Set TEST_ALLOW_REMOTE=1 explicitly for your own disposable test deployment.')
    return url
