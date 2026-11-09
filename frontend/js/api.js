const API_BASE = (window.FASHION_MANAGER_API_URL || '').replace(/\/+$/, '');
let productPage = 0;
let accessToken = null;
let currentUser = null;
const PRODUCT_PAGE_SIZE = 20;
const API_FIELD_NAMES = {
  employee_id: 'Mã nhân viên',
  ma_nhan_vien: 'Mã nhân viên',
  phone: 'Số điện thoại',
  so_dien_thoai: 'Số điện thoại',
  email: 'Email',
  name: 'Họ tên',
  ho_ten: 'Họ tên',
  store_id: 'Mã cửa hàng',
  ma_cua_hang: 'Mã cửa hàng',
  manager_id: 'Mã quản lý trực tiếp',
  ma_quan_ly: 'Mã quản lý trực tiếp',
  region_id: 'Khu vực quản lý',
  khu_vuc_quan_ly: 'Khu vực quản lý',
  salary: 'Lương',
  luong: 'Lương',
  customer_id: 'Mã khách hàng',
  ma_khach_hang: 'Mã khách hàng',
  product_id: 'Mã sản phẩm',
  ma_san_pham: 'Mã sản phẩm',
  category_id: 'Mã danh mục',
  ma_danh_muc: 'Mã danh mục',
  order_id: 'Mã đơn hàng',
  ma_don_hang: 'Mã đơn hàng',
  distribution_id: 'Mã phiếu phân phối',
  ma_phan_phoi: 'Mã phiếu phân phối',
  quantity: 'Số lượng',
  so_luong: 'Số lượng',
  size: 'Kích cỡ',
  kich_co: 'Kích cỡ',
  color: 'Màu sắc',
  mau_sac: 'Màu sắc',
  price: 'Giá',
  gia_san_pham: 'Giá sản phẩm',
  role: 'Vai trò',
  quyen_han: 'Vai trò',
  status: 'Trạng thái',
  trang_thai: 'Trạng thái'
};

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
    if (response.status === 404 && options.method === 'DELETE'
      && /^\/api\/employees\/[^/]+$/.test(path) && payload.detail === 'Not Found') {
      throw new Error('Backend chưa có API đuổi việc nhân viên. Hãy cập nhật/redeploy backend rồi thử lại.');
    }
    if (response.status === 401 && authenticate) {
      accessToken = null;
      currentUser = null;
      if (typeof showLogin === 'function') showLogin();
    }
    const detail = Array.isArray(payload.detail)
      ? payload.detail.map(item => {
        const location = (item.loc || []).filter(part => part !== 'body');
        const field = location.map(part => API_FIELD_NAMES[part] || part).join('.');
        return `${field ? `${field}: ` : ''}${item.msg}`;
      }).join('; ')
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

async function changePassword(currentPassword, newPassword) {
  const result = await apiRequest('/api/auth/password', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ current_password: currentPassword, new_password: newPassword })
  });
  accessToken = result.access_token;
  return result;
}

async function apiDownload(path, filename) {
  if (!API_BASE) throw new Error('Chưa cấu hình URL backend trong config.js.');
  const headers = {};
  if (accessToken) headers.Authorization = `Bearer ${accessToken}`;
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, { headers, signal: AbortSignal.timeout(60000) });
  } catch (error) {
    throw new Error(error.name === 'TimeoutError' ? 'Backend phản hồi quá chậm. Hãy thử tải lại.' : 'Không gọi được backend.');
  }
  if (!response.ok) {
    let payload = {};
    try {
      payload = await response.json();
    } catch (error) {
      payload = { detail: `Backend trả về lỗi HTTP ${response.status}.` };
    }
    if (response.status === 401) {
      accessToken = null;
      currentUser = null;
      if (typeof showLogin === 'function') showLogin();
    }
    throw new Error(typeof payload.detail === 'string' ? payload.detail : `API trả về lỗi HTTP ${response.status}`);
  }
  const objectUrl = URL.createObjectURL(await response.blob());
  const link = document.createElement('a');
  link.href = objectUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(objectUrl);
}

function logout() {
  accessToken = null;
  currentUser = null;
  window.location.reload();
}

function formatVND(amount) {
  if (amount === null || amount === undefined) return 'Chưa đủ dữ liệu';
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
      distributionTableBody: 3,
      orderHistoryBody: 6,
      movementTableBody: 6,
      reportTableBody: 4
    }[container.id] || 4;
    element.appendChild(content);
  }
  content.className = `py-6 text-sm ${className}`;
  content.textContent = message;
  container.appendChild(element);
}
