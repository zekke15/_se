const $ = (id) => document.getElementById(id);
const form = $('request-form');
let currentResponse = '';
let responseHeaders = '';
let responseTab = 'response';
const pretty = (body) => { try { return JSON.stringify(JSON.parse(body), null, 2); } catch { return body; } };

function showResponse() {
  $('output').textContent = responseTab === 'response' ? currentResponse : responseHeaders;
}
function setTab(name) {
  document.querySelectorAll('[data-tab]').forEach(button => button.setAttribute('aria-selected', button.dataset.tab === name));
  $('headers-panel').hidden = name !== 'headers';
  $('body-panel').hidden = name !== 'body';
}
document.querySelectorAll('[data-tab]').forEach(button => button.addEventListener('click', () => setTab(button.dataset.tab)));
document.querySelectorAll('[data-resp]').forEach(button => button.addEventListener('click', () => {
  responseTab = button.dataset.resp;
  document.querySelectorAll('[data-resp]').forEach(b => b.setAttribute('aria-selected', b.dataset.resp === responseTab));
  showResponse();
}));
function resetResponse() {
  currentResponse = '{\n  "message": "Ready to send your first request"\n}';
  responseHeaders = '';
  $('status').textContent = '—'; $('status').className = '';
  $('time').textContent = '—'; $('size').textContent = '—';
  $('result-label').textContent = '等待發送請求…';
  $('notice').textContent = '輸入網址並點擊「送出請求」開始。';
  showResponse();
}
$('reset').addEventListener('click', resetResponse);
$('copy').addEventListener('click', async () => {
  try { await navigator.clipboard.writeText($('output').textContent); $('notice').textContent = '已複製內容到剪貼簿。'; }
  catch { $('notice').textContent = '複製失敗，請手動選取內容。'; }
});
document.querySelectorAll('[data-example]').forEach(button => button.addEventListener('click', () => {
  if (button.dataset.example === 'get') {
    $('method').value = 'GET'; $('url').value = 'https://jsonplaceholder.typicode.com/todos/1'; $('body').value = ''; setTab('headers');
  } else {
    $('method').value = 'POST'; $('url').value = 'https://jsonplaceholder.typicode.com/posts';
    $('body').value = JSON.stringify({title:'CurlLab 測試',body:'Hello from Python!',userId:1},null,2);
    $('json-mode').checked = true; setTab('body');
  }
}));
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  let headers;
  try {
    headers = JSON.parse($('headers').value || '{}');
    if (headers === null || Array.isArray(headers) || typeof headers !== 'object') throw new Error();
  } catch { $('notice').textContent = 'Headers 必須是正確的 JSON 物件，例如 {"Accept":"application/json"}。'; return; }
  const button = $('send'); button.disabled = true; button.textContent = '請求傳送中…';
  $('notice').textContent = '正在等待伺服器回應…';
  try {
    const result = await fetch('/api/request', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({method:$('method').value,url:$('url').value.trim(),headers,body:$('body').value,jsonMode:$('json-mode').checked})});
    const data = await result.json();
    if (!result.ok) throw new Error(data.error || `HTTP ${result.status}`);
    $('status').textContent = `${data.status} ${data.reason || ''}`;
    $('status').className = data.status >= 200 && data.status < 400 ? 'good' : 'bad';
    $('time').textContent = `${data.elapsed_ms} ms`;
    $('size').textContent = `${data.size_bytes.toLocaleString()} B`;
    $('result-label').textContent = data.encoding === 'base64' ? 'Body (Base64)' : 'Response Body';
    currentResponse = data.encoding === 'base64' ? data.body : pretty(data.body);
    responseHeaders = JSON.stringify(data.headers, null, 2);
    $('notice').textContent = data.truncated ? '回應過大，只顯示前 1 MB。' : (data.status >= 300 && data.status < 400 ? '收到重新導向回應（安全起見不自動跟隨）。' : `完成：${data.final_url}`);
    showResponse();
  } catch (error) {
    $('status').textContent = 'Error'; $('status').className = 'bad';
    $('time').textContent = '—'; $('size').textContent = '—';
    currentResponse = JSON.stringify({error:error.message},null,2); responseHeaders = '';
    $('result-label').textContent = '請求失敗'; $('notice').textContent = error.message;
    showResponse();
  } finally { button.disabled = false; button.innerHTML = '送出請求 <span>↗</span>'; }
});
