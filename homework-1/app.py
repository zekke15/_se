"""CurlLab: a small web UI for making HTTP requests (local development only)."""
import base64
import ipaddress
import json
import os
import socket
import time
from collections import defaultdict, deque
from threading import Lock
from urllib.parse import urlsplit

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
app.json.ensure_ascii = False
MAX_RESPONSE_BYTES = 1_000_000
MAX_REQUEST_BYTES = 100_000
TIMEOUT = 12
# 公開展示版只允許連線到指定的教學 API，避免成為任意網址代理。
ALLOWED_HOSTS = frozenset(h.strip().lower() for h in os.environ.get(
    'ALLOWED_HOSTS', 'jsonplaceholder.typicode.com,httpbin.org'
).split(',') if h.strip())
RATE_LIMIT = 20  # 單一來源每 60 秒最多 20 筆 API 請求（單一程序示範限流）
_rate_window = defaultdict(deque)
_rate_lock = Lock()

@app.before_request
def public_rate_limit():
    if request.path != '/api/request':
        return None
    ip = request.remote_addr or 'unknown'
    now = time.monotonic()
    with _rate_lock:
        times = _rate_window[ip]
        while times and now - times[0] >= 60:
            times.popleft()
        if len(times) >= RATE_LIMIT:
            return jsonify(error='請求過於頻繁，請稍後再試。'), 429
        times.append(now)
    return None

class RequestError(ValueError):
    pass


def validate_url(url: str) -> str:
    if not isinstance(url, str) or not url.strip():
        raise RequestError('請輸入網址。')
    url = url.strip()
    parsed = urlsplit(url)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname:
        raise RequestError('只支援完整 http:// 或 https:// 網址。')
    if parsed.username or parsed.password:
        raise RequestError('網址不可包含帳號或密碼。')
    hostname = parsed.hostname.lower()
    # 這個公開範例只對指定 API 主機發送 HTTPS 請求。
    if parsed.scheme != 'https' or parsed.port not in (None, 443):
        raise RequestError('公開展示版僅支援 HTTPS（443 埠）。')
    if hostname not in ALLOWED_HOSTS:
        raise RequestError('公開展示版僅允許指定教學 API：' + ', '.join(sorted(ALLOWED_HOSTS)))
    if hostname.lower() == 'localhost' or hostname.lower().endswith('.localhost'):
        raise RequestError('基於安全考量，不能請求本機位址。')
    try:
        addresses = socket.getaddrinfo(hostname, parsed.port or (443 if parsed.scheme == 'https' else 80), type=socket.SOCK_STREAM)
    except (socket.gaierror, OverflowError, ValueError) as exc:
        raise RequestError('無法解析該網站的網域名稱。') from exc
    if not addresses:
        raise RequestError('找不到網域的 IP 位址。')
    for info in addresses:
        ip = ipaddress.ip_address(info[4][0].split('%')[0])
        if not ip.is_global:
            raise RequestError('基於安全考量，不允許連線到內網、保留或本機 IP。')
    return url


@app.get('/')
def index():
    return render_template('index.html')


@app.post('/api/request')
def make_request():
    if request.content_length and request.content_length > MAX_REQUEST_BYTES:
        return jsonify(error='請求資料過大。'), 413
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error='請提供正確的 JSON 請求資料。'), 400
    try:
        url = validate_url(data.get('url', ''))
        method = str(data.get('method', 'GET')).upper()
        if method not in ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD'):
            raise RequestError('不支援的 HTTP 方法。')
        headers = data.get('headers', {})
        if headers is None:
            headers = {}
        if not isinstance(headers, dict) or len(headers) > 30:
            raise RequestError('Headers 必須是物件，且最多 30 筆。')
        for key, value in headers.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise RequestError('Header 名稱和值必須是文字。')
            if key.lower() in ('host', 'content-length', 'transfer-encoding', 'connection', 'proxy-authorization', 'authorization', 'cookie', 'proxy-connection', 'forwarded', 'x-forwarded-for'):
                raise RequestError(f'不允許設定 Header：{key}')
        body = data.get('body', '')
        if not isinstance(body, str):
            raise RequestError('Body 必須是文字。')
        if len(body.encode('utf-8')) > MAX_REQUEST_BYTES:
            raise RequestError('Body 不可超過 100 KB。')
        if method in ('GET', 'HEAD') and body:
            raise RequestError('GET / HEAD 請求不支援 Body。')
        if data.get('jsonMode') and body:
            try:
                json.loads(body)
            except json.JSONDecodeError as exc:
                raise RequestError(f'JSON 格式不正確：{exc.msg}') from exc
            headers.setdefault('Content-Type', 'application/json')

        started = time.perf_counter()
        # Redirects are disabled to prevent a public URL redirecting to a private address.
        with requests.request(method, url, headers=headers, data=body.encode('utf-8') if body else None,
                              timeout=TIMEOUT, allow_redirects=False, stream=True,
                              proxies={'http': None, 'https': None}) as response:
            content = bytearray()
            too_large = False
            for chunk in response.iter_content(chunk_size=16_384):
                if len(content) + len(chunk) > MAX_RESPONSE_BYTES:
                    content.extend(chunk[:MAX_RESPONSE_BYTES-len(content)])
                    too_large = True
                    break
                content.extend(chunk)
            elapsed_ms = round((time.perf_counter() - started) * 1000)
            raw = bytes(content)
            ctype = response.headers.get('Content-Type', '')
            binary = not any(t in ctype.lower() for t in ('text/', 'json', 'xml', 'javascript', 'x-www-form-urlencoded')) and b'\x00' in raw
            if binary:
                output = base64.b64encode(raw).decode('ascii')
                format_name = 'base64'
            else:
                encoding = response.encoding or 'utf-8'
                output = raw.decode(encoding, errors='replace')
                format_name = 'text'
            return jsonify(status=response.status_code, reason=response.reason,
                           elapsed_ms=elapsed_ms, size_bytes=len(raw), truncated=too_large,
                           headers=dict(response.headers), body=output, encoding=format_name,
                           final_url=response.url)
    except RequestError as exc:
        return jsonify(error=str(exc)), 400
    except requests.Timeout:
        return jsonify(error='連線逾時，請稍後重試。'), 504
    except requests.RequestException as exc:
        return jsonify(error=f'網路請求失敗：{type(exc).__name__}'), 502
    except (UnicodeError, ValueError) as exc:
        return jsonify(error=f'請求格式錯誤：{exc}'), 400


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(os.environ.get('PORT', '5000')), debug=False)
