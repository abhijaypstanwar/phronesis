const API = 'http://localhost:8000';

function saveAuth(token, user) { localStorage.setItem('token', token); localStorage.setItem('user', JSON.stringify(user)); }
function getToken() { return localStorage.getItem('token'); }
function getUser()  { const u = localStorage.getItem('user'); return u ? JSON.parse(u) : null; }
function clearAuth(){ localStorage.removeItem('token'); localStorage.removeItem('user'); }
function isLoggedIn(){ return !!getToken(); }
function initials(name){ return name.split(' ').map(w=>w[0]).join('').toUpperCase().slice(0,2); }

async function apiPost(endpoint, body) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res  = await fetch(`${API}${endpoint}`, { method:'POST', headers, body: JSON.stringify(body) });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Something went wrong');
  return data;
}
async function apiGet(endpoint) {
  const res  = await fetch(`${API}${endpoint}`, { headers:{ 'Authorization':`Bearer ${getToken()}` } });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Something went wrong');
  return data;
}
async function apiPatch(endpoint) {
  const res  = await fetch(`${API}${endpoint}`, { method:'PATCH', headers:{ 'Authorization':`Bearer ${getToken()}` } });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Something went wrong');
  return data;
}
async function apiPatchBody(endpoint, body) {
  const res  = await fetch(`${API}${endpoint}`, { method:'PATCH', headers:{ 'Content-Type':'application/json','Authorization':`Bearer ${getToken()}` }, body: JSON.stringify(body) });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Something went wrong');
  return data;
}
async function apiDelete(endpoint) {
  const res = await fetch(`${API}${endpoint}`, { method:'DELETE', headers:{ 'Authorization':`Bearer ${getToken()}` } });
  if (res.status === 204) return;
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Something went wrong');
  return data;
}
async function login(email, password) {
  const data = await apiPost('/api/auth/login', { email, password });
  saveAuth(data.access_token, data.user);
  return data.user;
}
async function register(name, email, password) {
  const data = await apiPost('/api/auth/register', { name, email, password });
  saveAuth(data.access_token, data.user);
  return data.user;
}
function logout() { clearAuth(); window.location.href = '/welcome'; }
function redirectByRole(user) {
  if (user.role === 'admin') window.location.href = '/admin';
  else if (!user.is_verified) window.location.href = '/verify';
  else window.location.href = '/dashboard';
}
function requireAuth()  { if (!isLoggedIn()) window.location.href = '/login'; }
function requireAdmin() { const u = getUser(); if (!u || u.role !== 'admin') window.location.href = '/login'; }
function toast(msg, type='default') {
  let el = document.getElementById('toast');
  if (!el) { el = document.createElement('div'); el.id='toast'; document.body.appendChild(el); }
  el.textContent = msg;
  el.className = 'show' + (type==='error' ? ' error' : '');
  clearTimeout(el._t);
  el._t = setTimeout(()=>{ el.className=''; }, 3000);
}
function setLoading(btn, loading) {
  if (loading) { btn.dataset.original = btn.innerHTML; btn.innerHTML='<span class="spinner"></span>'; btn.disabled=true; }
  else { btn.innerHTML = btn.dataset.original; btn.disabled=false; }
}
