const $ = (q) => document.querySelector(q);
const today = () => new Date().toLocaleDateString('en-CA');
const money = (n) => new Intl.NumberFormat('zh-TW').format(n);
const short = (s) => String(s || '').slice(0, 10);
const escapeHtml = (v) => String(v).replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let tasks = [], expenses = [];
let toastTimer;
function toast(msg){const el=$('#toast');el.textContent=msg;el.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.classList.remove('show'),3000)}
async function request(path, options = {}){
  const response=await fetch('/api'+path,{...options,headers:{'Content-Type':'application/json',...(options.headers||{})}});
  if (!response.ok){const data=await response.json().catch(()=>({}));throw new Error(typeof data.detail==='string'?data.detail:`HTTP ${response.status}`)}
  return response.status===204?null:response.json();
}
function setConnection(ok){const el=$('#connection');el.className='connection '+(ok?'ok':'fail');el.textContent=ok?'●　服務已連線':'●　API 連線失敗';$('#status').textContent=ok?'正常':'離線'}
function renderTasks(){const el=$('#task-list');el.innerHTML=tasks.length?tasks.map(t=>`<li class="entry ${t.completed?'completed':''}"><input aria-label="標記完成" type="checkbox" data-complete="${t.id}" ${t.completed?'checked':''}><div class="desc"><strong>${escapeHtml(t.title)}</strong><small>${escapeHtml(t.course)} · ${short(t.due_date)} · ${({'low':'低','medium':'中','high':'高'})[t.priority]||'中'}優先</small></div><button class="delete" data-remove-task="${t.id}" aria-label="刪除任務">✕</button></li>`).join(''):'<li class="empty">還沒有任務，新增第一件作業吧 ✨</li>'}
function renderExpenses(){const el=$('#expense-list');el.innerHTML=expenses.length?expenses.map(e=>`<li class="entry"><div class="desc"><strong>${escapeHtml(e.description)}</strong><small>${escapeHtml(e.category)} · ${short(e.spent_on)}</small></div><strong>NT$ ${money(e.amount)}</strong><button class="delete" data-remove-expense="${e.id}" aria-label="刪除支出">✕</button></li>`).join(''):'<li class="empty">還沒有支出紀錄</li>'}
async function reload(){try{const [health,t,e,s]=await Promise.all([request('/health'),request('/tasks'),request('/expenses'),request('/stats')]);tasks=t;expenses=e;renderTasks();renderExpenses();$('#pending').textContent=s.tasks_pending;$('#overdue').textContent=s.tasks_overdue;$('#total').textContent='NT$ '+money(s.month_expenses);setConnection(health.status==='ok')}catch(e){setConnection(false);toast('讀取失敗：'+e.message)}}
$('#task-form').elements.due_date.value=today();$('#expense-form').elements.spent_on.value=today();
$('#task-form').addEventListener('submit',async(e)=>{e.preventDefault();const form=e.currentTarget;const data=Object.fromEntries(new FormData(form));data.course=data.course.trim()||'其他';try{await request('/tasks',{method:'POST',body:JSON.stringify(data)});form.reset();form.elements.due_date.value=today();toast('任務新增成功');await reload()}catch(err){toast(err.message)}});
$('#expense-form').addEventListener('submit',async(e)=>{e.preventDefault();const form=e.currentTarget;const data=Object.fromEntries(new FormData(form));data.amount=Number(data.amount);try{await request('/expenses',{method:'POST',body:JSON.stringify(data)});form.reset();form.elements.spent_on.value=today();toast('支出已記錄');await reload()}catch(err){toast(err.message)}});
$('#task-list').addEventListener('change',async(e)=>{const id=e.target.dataset.complete;if(!id)return;try{await request('/tasks/'+id,{method:'PATCH',body:JSON.stringify({completed:e.target.checked})});await reload()}catch(err){toast(err.message);await reload()}});
document.addEventListener('click',async(e)=>{const taskId=e.target.dataset.removeTask,expenseId=e.target.dataset.removeExpense;if(!taskId&&!expenseId)return;try{await request(taskId?'/tasks/'+taskId:'/expenses/'+expenseId,{method:'DELETE'});toast('已刪除');await reload()}catch(err){toast(err.message)}});
reload();
