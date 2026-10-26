const API_BASE = (window.FASHION_MANAGER_API_URL || '').replace(/\/+$/, '');
let productPage = 0;
let accessToken = null;
let currentUser = null;
const PRODUCT_PAGE_SIZE = 20;

async function apiRequest(path, options = {}, authenticate = true) {
  if (!API_BASE) throw new Error('Chưa cấu hình URL backend trong config.js.');
  let response;
  const headers = { ...(options.headers || {}) };
  if (authenticate && accessToken) headers.Authorization = `Bearer ${accessToken}`;
  try {
    response = await fetch(`${API_BASE}${path}`, { ...options, headers, signal: AbortSignal.timeout(60000) });
  } catch (error) {
    throw new Error(error.name === 'TimeoutError'
      ? 'Backend phản hồi quá chậm. Hãy thử tải lại.'
      : window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'Không gọi được API từ Live Server. Backend cần cho phép CORS origin hiện tại và phải đang hoạt động.'
        : 'Không gọi được backend. Kiểm tra URL API, dịch vụ backend và cấu hình CORS.');
  }
  let payload;
  try {
    payload = await response.json();
  } catch (_) {
    throw new Error(`Backend trả về dữ liệu không hợp lệ (HTTP ${response.status}).`);
  }
  if (!response.ok) {
    if (response.status === 404 && path === '/api/auth/login') {
      throw new Error('Backend đang chạy chưa có API đăng nhập. Hãy cập nhật và triển khai lại backend Render.');
    }
    if (response.status === 401 && authenticate) {
      accessToken = null;
      currentUser = null;
      if (typeof showLogin === 'function') showLogin();
    }
    const detail = Array.isArray(payload.detail)
      ? payload.detail.map(item => `${(item.loc || []).filter(part => part !== 'body').join('.')}: ${item.msg}`).join('; ')
      : payload.detail;
    throw new Error(typeof detail === 'string' ? detail : `API trả về lỗi HTTP ${response.status}`);
  }
  return payload;
}

async function login(phone, password) {
  accessToken = null;
  currentUser = null;
  const result = await apiRequest('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone, password })
  }, false);
  accessToken = result.access_token;
  currentUser = result.user;
  return result.user;
}

function logout() {
  accessToken = null;
  currentUser = null;
  window.location.reload();
}

function formatVND(amount) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
}

function renderMessage(container, message, className = 'text-zinc-500') {
  container.innerHTML = '';
  const isTable = container.tagName === 'TBODY';
  const element = document.createElement(isTable ? 'tr' : 'p');
  const content = isTable ? document.createElement('td') : element;
  if (isTable) {
    content.colSpan = {
      orderLogBody: 6,
      employeeTableBody: 5,
      distributionTableBody: 3
    }[container.id] || 4;
    element.appendChild(content);
  }
  content.className = `py-6 text-sm ${className}`;
  content.textContent = message;
  container.appendChild(element);
}
