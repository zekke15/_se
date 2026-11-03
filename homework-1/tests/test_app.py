import unittest
from unittest.mock import patch, MagicMock
from app import app, validate_url, RequestError

class CurlLabTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home(self):
        self.assertEqual(self.client.get('/').status_code, 200)

    def test_invalid_json(self):
        self.assertEqual(self.client.post('/api/request', data='invalid', content_type='application/json').status_code, 400)

    def test_invalid_url_scheme(self):
        with self.assertRaises(RequestError):
            validate_url('file:///etc/passwd')

    def test_localhost_blocked(self):
        with self.assertRaises(RequestError):
            validate_url('http://localhost:5000')

    def test_private_ip_blocked(self):
        with self.assertRaises(RequestError):
            validate_url('http://127.0.0.1')

    def test_public_allowlist(self):
        with self.assertRaises(RequestError):
            validate_url('https://example.com')

    def test_non_https_blocked(self):
        with self.assertRaises(RequestError):
            validate_url('http://jsonplaceholder.typicode.com')

    def test_invalid_method(self):
        with patch('app.validate_url', return_value='https://example.com'):
            r = self.client.post('/api/request', json={'url':'https://example.com','method':'TRACE'})
            self.assertEqual(r.status_code, 400)

    def test_invalid_headers(self):
        with patch('app.validate_url', return_value='https://example.com'):
            r = self.client.post('/api/request', json={'url':'https://example.com','headers':[]})
            self.assertEqual(r.status_code, 400)

    def test_invalid_json_body(self):
        with patch('app.validate_url', return_value='https://example.com'):
            r = self.client.post('/api/request', json={'url':'https://example.com','method':'POST','body':'{oops','jsonMode':True})
            self.assertEqual(r.status_code, 400)

    def test_get_request_success(self):
        mocked = MagicMock()
        mocked.status_code = 200
        mocked.reason = 'OK'
        mocked.headers = {'Content-Type': 'application/json'}
        mocked.encoding = 'utf-8'
        mocked.url = 'https://example.com/api'
        mocked.iter_content.return_value = [b'{"ok":true}']
        mocked.__enter__.return_value = mocked
        with patch('app.validate_url', return_value='https://example.com/api'), patch('app.requests.request', return_value=mocked) as call:
            r = self.client.post('/api/request', json={'url':'https://example.com/api'})
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json['body'], '{"ok":true}')
            self.assertEqual(r.json['status'], 200)
            self.assertFalse(call.call_args.kwargs['allow_redirects'])

    def test_network_timeout(self):
        import requests
        with patch('app.validate_url', return_value='https://example.com'), patch('app.requests.request', side_effect=requests.Timeout):
            r = self.client.post('/api/request', json={'url':'https://example.com'})
            self.assertEqual(r.status_code, 504)

if __name__ == '__main__':
    unittest.main()
