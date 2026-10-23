const API_BASE = window.FASHION_MANAGER_API_URL || 'http://127.0.0.1:8000';

async function apiRequest(path) {
  const response = await fetch(`${API_BASE}${path}`);
  let payload = null;
  try {
    payload = await response.json();
  } catch (_) {
    // The error below still contains the HTTP status when the server returned non-JSON.
  }
  if (!response.ok) {
    throw new Error(payload?.detail || `API trả về lỗi HTTP ${response.status}`);
  }
  return payload;
}

function formatVND(amount) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
}

function renderMessage(container, message, className = 'text-zinc-500') {
  container.innerHTML = '';
  const messageElement = document.createElement('p');
  messageElement.className = `py-6 text-sm ${className}`;
  messageElement.textContent = message;
  container.appendChild(messageElement);
}

async function loadProducts() {
  const tbody = document.getElementById('productTableBody');
  if (!tbody) return;
  renderMessage(tbody, 'Đang tải sản phẩm từ database...');
  try {
    const data = await apiRequest('/api/products');
    tbody.innerHTML = '';
    if (!data.items.length) {
      renderMessage(tbody, 'Database chưa có sản phẩm.');
      return;
    }
    data.items.forEach((product) => {
      const row = document.createElement('tr');
      row.className = 'hover:bg-zinc-200/30 transition-colors';
      [
        product.ten_san_pham,
        `${product.mau_sac} · ${product.kich_co}`,
        formatVND(product.gia_ban),
        product.ma_danh_muc
      ].forEach((value, index) => {
        const cell = document.createElement('td');
        cell.className = ['py-3.5 pr-4 font-medium text-zinc-900', 'py-3.5 px-4 text-zinc-600', 'py-3.5 px-4 text-zinc-900', 'py-3.5 pl-4 text-zinc-500 text-xs'][index];
        cell.textContent = value;
        row.appendChild(cell);
      });
      tbody.appendChild(row);
    });
  } catch (error) {
    renderMessage(tbody, `Không thể tải sản phẩm: ${error.message}`, 'text-red-600');
  }
}

async function loadCategories() {
  const grid = document.getElementById('categoriesGrid');
  if (!grid) return;
  renderMessage(grid, 'Đang tải danh mục từ database...');
  try {
    const data = await apiRequest('/api/categories');
    grid.innerHTML = '';
    if (!data.items.length) {
      renderMessage(grid, 'Database chưa có danh mục.');
      return;
    }
    data.items.forEach((category) => {
      const card = document.createElement('div');
      card.className = 'p-4 rounded-xl bg-white border border-zinc-200/80 flex items-center justify-between';
      const details = document.createElement('div');
      const name = document.createElement('div');
      name.className = 'font-medium text-sm text-zinc-900';
      name.textContent = category.ten_danh_muc;
      const code = document.createElement('div');
      code.className = 'text-xs text-zinc-500 mt-0.5';
      code.textContent = category.ma_danh_muc;
      details.append(name, code);
      const count = document.createElement('span');
      count.className = 'text-xs font-medium bg-zinc-100 px-2.5 py-1 rounded-md text-zinc-700';
      count.textContent = `${category.so_san_pham} SP`;
      card.append(details, count);
      grid.appendChild(card);
    });
  } catch (error) {
    renderMessage(grid, `Không thể tải danh mục: ${error.message}`, 'text-red-600');
  }
}

async function loadAnalyticsSummary() {
  try {
    const summary = await apiRequest('/api/analytics/summary');
    const products = document.getElementById('summaryProducts');
    const categories = document.getElementById('summaryCategories');
    const stores = document.getElementById('summaryStores');
    const orders = document.getElementById('summaryOrders');
    if (products) products.textContent = `${summary.total_products} sản phẩm trong database`;
    if (categories) categories.textContent = `${summary.total_categories} danh mục trong database`;
    if (stores) stores.textContent = `${summary.total_stores} cửa hàng trong database`;
    if (orders) orders.textContent = `${summary.total_orders} đơn hàng trong database`;
  } catch (error) {
    showToast(`Không thể tải thống kê database: ${error.message}`);
  }

  async function loadStores() {
    const container = document.getElementById('storesGrid');
    if (!container) return;
    renderMessage(container, 'Đang tải cửa hàng từ database...');
    try {
      const data = await apiRequest('/api/stores');
      container.innerHTML = '';
      if (!data.items.length) {
        renderMessage(container, 'Database chưa có cửa hàng.');
        return;
      }
      data.items.forEach((store) => {
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
    } catch (error) {
      renderMessage(container, `Không thể tải cửa hàng: ${error.message}`, 'text-red-600');
    }
  }
}

async function checkBackendHealth() {
  const syncDot = document.getElementById('syncDot');
  const syncTitle = document.getElementById('syncTitle');
  const syncDesc = document.getElementById('syncDesc');
  try {
    await apiRequest('/api/health/db');
    syncDot.className = 'w-2 h-2 rounded-full bg-emerald-600 inline-block';
    syncTitle.textContent = 'Database đang kết nối';
    syncDesc.textContent = 'Dữ liệu trên trang được đọc trực tiếp từ MySQL.';
  } catch (error) {
    syncDot.className = 'w-2 h-2 rounded-full bg-red-600 inline-block';
    syncTitle.textContent = 'Database chưa kết nối';
    syncDesc.textContent = error.message;
  }
}

async function triggerSync() {
  const btn = document.getElementById('syncBtn');
  const btnText = document.getElementById('syncBtnText');
  btn.disabled = true;
  btn.classList.add('opacity-80');
  btnText.textContent = 'Đang tải dữ liệu...';
  await Promise.all([checkBackendHealth(), loadProducts(), loadCategories(), loadStores(), loadAnalyticsSummary()]);
  btn.disabled = false;
  btn.classList.remove('opacity-80');
  btnText.textContent = 'Tải lại dữ liệu';
  showToast('Đã tải lại dữ liệu từ database.');
}
