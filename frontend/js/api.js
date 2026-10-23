const API_BASE = (window.FASHION_MANAGER_API_URL || '').replace(/\/+$/, '');
let productPage = 0;
const PRODUCT_PAGE_SIZE = 20;

async function apiRequest(path, options = {}) {
  if (!API_BASE) throw new Error('Chưa cấu hình URL backend trong config.js.');
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, { ...options, signal: AbortSignal.timeout(60000) });
  } catch (error) {
    throw new Error(error.name === 'TimeoutError'
      ? 'Backend phản hồi quá chậm. Hãy thử tải lại.'
      : 'Không gọi được backend. Kiểm tra URL API, dịch vụ backend và cấu hình CORS.');
  }
  let payload;
  try {
    payload = await response.json();
  } catch (_) {
    throw new Error(`Backend trả về dữ liệu không hợp lệ (HTTP ${response.status}).`);
  }
  if (!response.ok) {
    throw new Error(typeof payload.detail === 'string' ? payload.detail : `API trả về lỗi HTTP ${response.status}`);
  }
  return payload;
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
    content.colSpan = container.id === 'visitLogBody' ? 6 : 4;
    element.appendChild(content);
  }
  content.className = `py-6 text-sm ${className}`;
  content.textContent = message;
  container.appendChild(element);
}

async function loadProducts() {
  const tbody = document.getElementById('productTableBody');
  if (!tbody) return true;
  const previous = document.getElementById('productsPrevious');
  const next = document.getElementById('productsNext');
  previous.disabled = next.disabled = true;
  renderMessage(tbody, 'Đang tải sản phẩm...');
  try {
    // Fetch one extra row to know whether another page exists.
    const data = await apiRequest(`/api/products?limit=${PRODUCT_PAGE_SIZE + 1}&offset=${productPage * PRODUCT_PAGE_SIZE}`);
    tbody.innerHTML = '';
    if (!data.items.length) renderMessage(tbody, 'Không có sản phẩm trong trang này.');
    data.items.slice(0, PRODUCT_PAGE_SIZE).forEach(product => {
      const row = document.createElement('tr');
      row.className = 'hover:bg-zinc-200/30 transition-colors';
      [product.ten_san_pham, `${product.mau_sac} · ${product.kich_co}`, formatVND(product.gia_ban), product.ma_danh_muc]
        .forEach(value => {
          const cell = document.createElement('td');
          cell.className = 'py-3.5 px-4 text-zinc-700';
          cell.textContent = value;
          row.appendChild(cell);
        });
      tbody.appendChild(row);
    });
    document.getElementById('productsPage').textContent = `Trang ${productPage + 1}`;
    previous.disabled = productPage === 0;
    next.disabled = data.items.length <= PRODUCT_PAGE_SIZE;
    return true;
  } catch (error) {
    renderMessage(tbody, `Không thể tải sản phẩm: ${error.message}`, 'text-red-600');
    previous.disabled = productPage === 0;
    return false;
  }
}

function changeProductPage(direction) {
  productPage = Math.max(0, productPage + direction);
  return loadProducts();
}

async function loadCategories() {
  const grid = document.getElementById('categoriesGrid');
  if (!grid) return true;
  renderMessage(grid, 'Đang tải danh mục...');
  try {
    const data = await apiRequest('/api/categories');
    grid.innerHTML = '';
    if (!data.items.length) renderMessage(grid, 'Database chưa có danh mục.');
    data.items.forEach(category => {
      const card = document.createElement('div');
      card.className = 'p-4 rounded-xl bg-white border border-zinc-200/80';
      const name = document.createElement('div');
      name.className = 'font-medium text-sm text-zinc-900';
      name.textContent = category.ten_danh_muc;
      const details = document.createElement('div');
      details.className = 'text-xs text-zinc-500 mt-2';
      details.textContent = `${category.ma_danh_muc} · ${category.so_san_pham} sản phẩm`;
      card.append(name, details);
      grid.appendChild(card);
    });
    return true;
  } catch (error) {
    renderMessage(grid, `Không thể tải danh mục: ${error.message}`, 'text-red-600');
    return false;
  }
}

async function loadStores() {
  const container = document.getElementById('storesGrid');
  if (!container) return true;
  renderMessage(container, 'Đang tải cửa hàng...');
  try {
    const data = await apiRequest('/api/stores');
    container.innerHTML = '';
    if (!data.items.length) renderMessage(container, 'Database chưa có cửa hàng.');
    data.items.forEach(store => {
      const card = document.createElement('article');
      card.className = 'rounded-xl bg-white border border-zinc-200/80 p-4';
      const name = document.createElement('h3');
      name.className = 'font-medium text-sm text-zinc-900';
      name.textContent = store.ten_cua_hang;
      const details = document.createElement('p');
      details.className = 'text-xs text-zinc-500 mt-2 leading-relaxed';
      details.textContent = `${store.ma_cua_hang} · ${store.dia_chi} · ${store.so_dien_thoai}`;
      card.append(name, details);
      container.appendChild(card);
    });
    return true;
  } catch (error) {
    renderMessage(container, `Không thể tải cửa hàng: ${error.message}`, 'text-red-600');
    return false;
  }
}

async function loadAnalyticsSummary() {
  const fields = { summaryProducts: 'total_products', summaryCategories: 'total_categories', summaryStores: 'total_stores', summaryOrders: 'total_orders' };
  const status = document.getElementById('summaryStatus');
  Object.keys(fields).forEach(id => { document.getElementById(id).textContent = '—'; });
  status.textContent = 'Đang tải số liệu...';
  try {
    const summary = await apiRequest('/api/analytics/summary');
    Object.entries(fields).forEach(([id, key]) => {
      document.getElementById(id).textContent = new Intl.NumberFormat('vi-VN').format(summary[key]);
    });
    status.textContent = `Cập nhật lúc ${new Date().toLocaleTimeString('vi-VN')}`;
    return true;
  } catch (error) {
    status.textContent = `Không thể tải thống kê: ${error.message}`;
    return false;
  }
}

async function checkBackendHealth() {
  const dot = document.getElementById('syncDot');
  const title = document.getElementById('syncTitle');
  const description = document.getElementById('syncDesc');
  title.textContent = 'Đang kiểm tra kết nối';
  dot.className = 'w-2 h-2 rounded-full bg-zinc-400 inline-block';
  try {
    await apiRequest('/api/health/db');
    dot.className = 'w-2 h-2 rounded-full bg-emerald-600 inline-block';
    title.textContent = 'Database đang kết nối';
    description.textContent = 'Đã kết nối MySQL qua backend.';
    return true;
  } catch (error) {
    dot.className = 'w-2 h-2 rounded-full bg-red-600 inline-block';
    title.textContent = 'Database chưa kết nối';
    description.textContent = error.message;
    return false;
  }
}

async function triggerSync(notify = true) {
  const button = document.getElementById('syncBtn');
  const text = document.getElementById('syncBtnText');
  button.disabled = true;
  text.textContent = 'Đang tải dữ liệu...';
  try {
    const results = await Promise.allSettled([checkBackendHealth(), loadProducts(), loadCategories(), loadStores(), loadAnalyticsSummary(), loadVisitAnalytics()]);
    const success = results.every(result => result.status === 'fulfilled' && result.value === true);
    if (notify) showToast(success ? 'Đã tải lại dữ liệu từ database.' : 'Tải dữ liệu chưa hoàn tất. Xem lỗi tại từng mục.');
    return success;
  } finally {
    button.disabled = false;
    text.textContent = 'Tải lại dữ liệu';
  }
}
