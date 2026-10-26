const REGION_NAMES = { 1: 'Miền Bắc', 2: 'Miền Trung', 3: 'Miền Nam' };
const ROLE_NAMES = {
  admin: 'Admin',
  regional_manager: 'Quản lý khu vực',
  store_manager: 'Quản lý cửa hàng',
  staff: 'Nhân viên'
};
let employeeStores = [];
let academicQueries = [];

function setVisible(element, visible) {
  if (!element) return;
  if (visible) element.classList.remove('hidden');
  else element.classList.add('hidden');
}

function switchTab(tabId, loadData = true) {
  const tabs = ['analytics', 'products', 'categories', 'settings', 'employees', 'queries', 'orders', 'distribution'];
  if (!tabs.includes(tabId)) return;
  tabs.forEach(tab => {
    const element = document.getElementById(`tab-${tab}`);
    if (element) element.classList.add('hidden');
  });
  const activeTab = document.getElementById(`tab-${tabId}`);
  if (activeTab) activeTab.classList.remove('hidden');

  document.querySelectorAll('.nav-btn').forEach(button => {
    const hidden = button.classList.contains('hidden');
    button.className = button.dataset.tab === tabId
      ? `nav-btn ${hidden ? 'hidden' : ''} w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13.5px] font-medium bg-zinc-200/80 text-zinc-900 transition-colors`
      : `nav-btn ${hidden ? 'hidden' : ''} w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13.5px] font-medium text-zinc-600 hover:bg-zinc-200/50 hover:text-zinc-900 transition-colors`;
  });

  const sidebar = document.getElementById('sidebar');
  if (sidebar && !sidebar.classList.contains('-translate-x-full') && window.innerWidth < 768) toggleMobileMenu();
  if (!loadData) return;
  if (tabId === 'products') loadProducts();
  if (tabId === 'categories') loadCategories();
  if (tabId === 'settings') {
    loadStores();
    loadAnalyticsSummary();
  }
  if (tabId === 'analytics') loadSalesAnalytics();
  if (tabId === 'employees') loadEmployees();
  if (tabId === 'queries') loadAcademicQueries();
  if (tabId === 'orders') loadOrderFormData();
  if (tabId === 'distribution') loadDistribution();
}

function toggleMobileMenu() {
  const sidebar = document.getElementById('sidebar');
  const backdrop = document.getElementById('mobileBackdrop');
  if (!sidebar || !backdrop) return;
  sidebar.classList.toggle('-translate-x-full');
  backdrop.classList.toggle('hidden');
}

let toastTimeout;
function showToast(message) {
  const toast = document.getElementById('toast');
  const toastText = document.getElementById('toastText');
  if (!toast || !toastText) return;
  toastText.textContent = message;
  toast.classList.remove('opacity-0', 'translate-y-2', 'pointer-events-none');
  clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-2', 'pointer-events-none');
  }, 2600);
}

function setStatus(id, text, isError = false) {
  const element = document.getElementById(id);
  if (!element) return;
  element.textContent = text;
  element.className = `text-sm mt-2 ${isError ? 'text-red-600' : 'text-zinc-500'}`;
}

async function loadAcademicQueries() {
  const select = document.getElementById('querySelect');
  const runButton = document.getElementById('runQueryBtn');
  const head = document.getElementById('queryResultHead');
  const body = document.getElementById('queryResultBody');
  if (!select || !runButton || !head || !body) return false;

  runButton.disabled = true;
  setStatus('queryStatus', 'Đang tải danh sách truy vấn...');
  try {
    const result = await apiRequest('/api/query-explorer');
    academicQueries = result.items;
    select.replaceChildren();
    head.replaceChildren();
    body.replaceChildren();
    const groups = new Map();
    academicQueries.forEach(query => {
      const groupId = query.query_id.slice(0, 3);
      let group = groups.get(groupId);
      if (!group) {
        group = document.createElement('optgroup');
        group.label = `Thành viên ${groupId.slice(1)}`;
        groups.set(groupId, group);
        select.appendChild(group);
      }
      const option = document.createElement('option');
      option.value = query.query_id;
      option.textContent = `${query.query_id} · ${query.title}`;
      group.appendChild(option);
    });
    runButton.disabled = academicQueries.length === 0;
    setStatus('queryStatus', academicQueries.length
      ? `${academicQueries.length} truy vấn đã định nghĩa sẵn sàng. Các truy vấn không chỉnh sửa dữ liệu.`
      : 'Không tìm thấy truy vấn nào trong bộ truy vấn hiện tại.', academicQueries.length === 0);
    return academicQueries.length > 0;
  } catch (error) {
    academicQueries = [];
    select.replaceChildren();
    const option = document.createElement('option');
    option.value = '';
    option.textContent = 'Không thể tải danh sách truy vấn';
    select.appendChild(option);
    setStatus('queryStatus', `Không thể tải danh sách truy vấn: ${error.message}`, true);
    return false;
  }
}

function displayQueryValue(value) {
  if (value === null || value === undefined) return '—';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

async function runAcademicQuery() {
  const queryId = document.getElementById('querySelect').value;
  const button = document.getElementById('runQueryBtn');
  const head = document.getElementById('queryResultHead');
  const body = document.getElementById('queryResultBody');
  if (!queryId || !academicQueries.some(query => query.query_id === queryId)) {
    setStatus('queryStatus', 'Hãy chọn một truy vấn hợp lệ.', true);
    return false;
  }

  button.disabled = true;
  setStatus('queryStatus', `Đang chạy ${queryId}...`);
  head.replaceChildren();
  renderMessage(body, 'Đang tải kết quả...');
  try {
    const result = await apiRequest(`/api/query-explorer/${encodeURIComponent(queryId)}`, { method: 'POST' });
    const columns = result.columns?.length ? result.columns : Object.keys(result.items[0] || {});
    head.replaceChildren();
    body.replaceChildren();
    if (columns.length) {
      const row = document.createElement('tr');
      columns.forEach(column => {
        const cell = document.createElement('th');
        cell.className = 'whitespace-nowrap px-4 py-3 font-medium';
        cell.textContent = column;
        row.appendChild(cell);
      });
      head.appendChild(row);
    }
    if (!result.items.length) {
      const row = document.createElement('tr');
      const cell = document.createElement('td');
      cell.colSpan = Math.max(columns.length, 1);
      cell.className = 'px-4 py-6 text-sm text-zinc-500';
      cell.textContent = 'Truy vấn không có kết quả.';
      row.appendChild(cell);
      body.appendChild(row);
    } else {
      result.items.forEach(item => {
        const row = document.createElement('tr');
        columns.forEach(column => {
          const cell = document.createElement('td');
          cell.className = 'whitespace-nowrap px-4 py-3 text-zinc-700';
          cell.textContent = displayQueryValue(item[column]);
          row.appendChild(cell);
        });
        body.appendChild(row);
      });
    }
    const limitNote = result.items.length === 500 ? ' · Hiển thị tối đa 500 dòng' : '';
    const compatibilityNote = result.notice ? ` · ${result.notice}` : '';
    setStatus('queryStatus', `${queryId}: ${result.items.length} dòng${limitNote}.${compatibilityNote}`);
    return true;
  } catch (error) {
    head.replaceChildren();
    renderMessage(body, `Không thể chạy truy vấn: ${error.message}`, 'text-red-600');
    setStatus('queryStatus', `Truy vấn thất bại: ${error.message}`, true);
    return false;
  } finally {
    button.disabled = false;
  }
}

function showLogin() {
  document.querySelectorAll('.nav-btn').forEach(button => button.classList.add('hidden'));
  setVisible(document.getElementById('syncBtn'), false);
  document.getElementById('syncTitle').textContent = 'Cần đăng nhập';
  document.getElementById('syncDesc').textContent = 'Đăng nhập để tải dữ liệu theo đúng quyền của bạn.';
  setVisible(document.getElementById('authPanel'), true);
  setVisible(document.getElementById('dashboardContent'), false);
  setVisible(document.getElementById('accountActions'), false);
  setVisible(document.getElementById('loginForm'), true);
}

function updateRoleNavigation(user) {
  const manager = ['admin', 'regional_manager', 'store_manager'].includes(user.role);
  const allowedTabs = manager
    ? ['analytics', 'products', 'categories', 'settings', 'employees', ...(user.role === 'admin' ? ['queries'] : [])]
    : ['products', 'categories', 'orders', 'distribution'];
  document.querySelectorAll('.nav-btn').forEach(button => {
    const visible = allowedTabs.includes(button.dataset.tab);
    setVisible(button, visible);
    if (visible) button.classList.add('flex');
  });
  setVisible(document.getElementById('employeeCreatePanel'), user.role !== 'staff');
  const roleSelect = document.getElementById('employeeRole');
  if (roleSelect) {
    roleSelect.replaceChildren();
    const options = user.role === 'admin'
      ? ['regional_manager', 'store_manager', 'staff']
      : user.role === 'regional_manager'
        ? ['store_manager', 'staff']
        : ['staff'];
    options.forEach(role => {
      const option = document.createElement('option');
      option.value = role;
      option.textContent = ROLE_NAMES[role];
      roleSelect.appendChild(option);
    });
  }
  const scope = document.getElementById('employeeScope');
  if (scope) {
    scope.textContent = user.role === 'admin'
      ? 'Phạm vi: toàn hệ thống.'
      : user.role === 'regional_manager'
        ? `Phạm vi: ${REGION_NAMES[user.region_id] || 'khu vực được phân công'}.`
        : `Phạm vi: cửa hàng ${user.store_id || 'được phân công'}.`;
  }
  updateEmployeeFormScope();
}

async function showAuthenticated(user) {
  currentUser = user;
  productPage = 0;
  setVisible(document.getElementById('syncBtn'), true);
  setVisible(document.getElementById('authPanel'), false);
  setVisible(document.getElementById('dashboardContent'), true);
  setVisible(document.getElementById('accountActions'), true);
  document.getElementById('accountLabel').textContent = `${user.name} · ${ROLE_NAMES[user.role]}`;
  updateRoleNavigation(user);
  switchTab(user.role === 'staff' ? 'orders' : 'analytics', false);
  await triggerSync(false);
}

async function handleLogin(event) {
  event.preventDefault();
  const button = document.getElementById('loginSubmit');
  if (button.disabled) return;
  button.disabled = true;
  setStatus('loginStatus', 'Đang đăng nhập...');
  try {
    const user = await login(
      document.getElementById('loginPhone').value.trim(),
      document.getElementById('loginPassword').value
    );
    document.getElementById('loginPassword').value = '';
    setStatus('loginStatus', '');
    await showAuthenticated(user);
  } catch (error) {
    setStatus('loginStatus', error.message, true);
  } finally {
    button.disabled = false;
  }
}

async function loadProducts() {
  const tbody = document.getElementById('productTableBody');
  if (!tbody) return true;
  const previous = document.getElementById('productsPrevious');
  const next = document.getElementById('productsNext');
  previous.disabled = next.disabled = true;
  renderMessage(tbody, 'Đang tải sản phẩm...');
  try {
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
    if (!data.items.length) renderMessage(container, 'Không có cửa hàng trong phạm vi được phép.');
    data.items.forEach(store => {
      const card = document.createElement('article');
      card.className = 'rounded-xl bg-white border border-zinc-200/80 p-4';
      const name = document.createElement('h3');
      name.className = 'font-medium text-sm text-zinc-900';
      name.textContent = store.ten_cua_hang;
      const details = document.createElement('p');
      details.className = 'text-xs text-zinc-500 mt-2 leading-relaxed';
      details.textContent = `${store.ma_cua_hang} · ${REGION_NAMES[store.khu_vuc] || ''} · ${store.dia_chi} · ${store.so_dien_thoai}`;
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

function appendCell(row, value, className = 'py-3 pr-3 text-zinc-700') {
  const cell = document.createElement('td');
  cell.className = className;
  cell.textContent = value ?? '—';
  row.appendChild(cell);
  return cell;
}

function makeAction(label, action, disabled = false) {
  const button = document.createElement('button');
  button.type = 'button';
  button.textContent = label;
  button.disabled = disabled;
  button.className = 'mr-2 mb-1 rounded border px-2 py-1 text-xs disabled:opacity-40';
  button.addEventListener('click', action);
  return button;
}

async function performEmployeeAction(employeeId, path, method, body, successMessage) {
  try {
    await apiRequest(path, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: body === null ? undefined : JSON.stringify(body)
    });
    showToast(successMessage);
    await loadEmployees();
  } catch (error) {
    showToast(`Thao tác thất bại: ${error.message}`);
  }
}

async function loadEmployees() {
  const body = document.getElementById('employeeTableBody');
  if (!body || !currentUser) return false;
  setStatus('employeeStatus', 'Đang tải nhân sự...');
  body.replaceChildren();
  try {
    const [employees, stores] = await Promise.all([
      apiRequest('/api/employees'),
      apiRequest('/api/employees/stores')
    ]);
    employeeStores = stores.items;
    const storeSelect = document.getElementById('employeeStore');
    if (storeSelect) {
      storeSelect.replaceChildren();
      stores.items.forEach(store => {
        const option = document.createElement('option');
        option.value = store.ma_cua_hang;
        option.textContent = `${store.ma_cua_hang} · ${store.ten_cua_hang} (${REGION_NAMES[store.khu_vuc] || 'Khu vực'})`;
        storeSelect.appendChild(option);
      });
    }
    if (!employees.items.length) {
      renderMessage(body, 'Không có nhân sự trong phạm vi được phép.');
      setStatus('employeeStatus', 'Không có dữ liệu.');
      return true;
    }
    employees.items.forEach(employee => {
      const row = document.createElement('tr');
      appendCell(row, `${employee.ho_ten} · ${employee.ma_nhan_vien}`);
      appendCell(row, ROLE_NAMES[employee.quyen_han] || employee.quyen_han, 'px-3 text-zinc-700');
      appendCell(row, employee.quyen_han === 'regional_manager'
        ? (REGION_NAMES[employee.khu_vuc_quan_ly] || 'Chưa gán')
        : `${employee.ma_cua_hang || '—'}${employee.ten_cua_hang ? ` · ${employee.ten_cua_hang}` : ''}`, 'px-3 text-zinc-700');
      appendCell(row, formatVND(employee.luong), 'px-3 text-zinc-700');

      const actions = document.createElement('td');
      actions.className = 'pl-3 py-2';
      const isSelf = employee.ma_nhan_vien === currentUser.employee_id;
      if (!isSelf && employee.quyen_han !== 'admin') {
        const salary = document.createElement('input');
        salary.type = 'number';
        salary.min = '1';
        salary.step = '1';
        salary.value = employee.luong ?? '';
        salary.placeholder = 'Lương';
        salary.className = 'w-28 rounded border px-2 py-1 text-xs mr-1';
        actions.appendChild(salary);
        actions.appendChild(makeAction('Lưu lương', () => {
          const value = Number(salary.value);
          if (!Number.isInteger(value) || value <= 0) return showToast('Lương phải là số nguyên dương.');
          performEmployeeAction(employee.ma_nhan_vien, `/api/employees/${encodeURIComponent(employee.ma_nhan_vien)}/salary`, 'PUT', { salary: value }, 'Đã cập nhật lương.');
        }));
        if (employee.quyen_han === 'store_manager' && ['admin', 'regional_manager'].includes(currentUser.role)) {
          actions.appendChild(makeAction('Hạ chức', () => {
            performEmployeeAction(employee.ma_nhan_vien, `/api/employees/${encodeURIComponent(employee.ma_nhan_vien)}/demote`, 'POST', {}, 'Đã hạ chức xuống nhân viên.');
          }));
        } else if (employee.quyen_han === 'regional_manager' && currentUser.role === 'admin') {
          const regionStores = employeeStores.filter(store => store.khu_vuc === employee.khu_vuc_quan_ly);
          const storeSelect = document.createElement('select');
          storeSelect.className = 'rounded border px-2 py-1 text-xs mr-1';
          regionStores.forEach(store => {
            const option = document.createElement('option');
            option.value = store.ma_cua_hang;
            option.textContent = store.ma_cua_hang;
            storeSelect.appendChild(option);
          });
          actions.appendChild(storeSelect);
          actions.appendChild(makeAction('Hạ chức', () => {
            if (!storeSelect.value) return showToast('Không có cửa hàng trong khu vực để phân công.');
            performEmployeeAction(employee.ma_nhan_vien, `/api/employees/${encodeURIComponent(employee.ma_nhan_vien)}/demote`, 'POST', { store_id: storeSelect.value }, 'Đã hạ chức xuống nhân viên.');
          }, regionStores.length === 0));
        }
      }
      row.appendChild(actions);
      body.appendChild(row);
    });
    setStatus('employeeStatus', `${employees.items.length} nhân sự trong phạm vi được phép.`);
    return true;
  } catch (error) {
    renderMessage(body, `Không thể tải nhân sự: ${error.message}`, 'text-red-600');
    setStatus('employeeStatus', `Không thể tải danh sách: ${error.message}`, true);
    return false;
  }
}

function updateEmployeeFormScope() {
  const role = document.getElementById('employeeRole').value;
  setVisible(document.getElementById('employeeRegion'), role === 'regional_manager');
  setVisible(document.getElementById('employeeStore'), role !== 'regional_manager');
}

async function handleCreateEmployee(event) {
  event.preventDefault();
  const role = document.getElementById('employeeRole').value;
  const salary = Number(document.getElementById('employeeSalary').value);
  if (!Number.isInteger(salary) || salary <= 0) {
    setStatus('employeeFormStatus', 'Lương phải là số nguyên dương theo ràng buộc database.', true);
    return;
  }
  const payload = {
    employee_id: document.getElementById('employeeId').value.trim(),
    name: document.getElementById('employeeName').value.trim(),
    phone: document.getElementById('employeePhone').value.trim(),
    email: document.getElementById('employeeEmail').value.trim(),
    role,
    store_id: role === 'regional_manager' ? null : document.getElementById('employeeStore').value,
    region_id: role === 'regional_manager' ? Number(document.getElementById('employeeRegion').value) : null,
    salary
  };
  try {
    const result = await apiRequest('/api/employees', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    document.getElementById('employeeForm').reset();
    setStatus('employeeFormStatus', `Đã tạo ${result.employee_id}; mật khẩu ban đầu là mã nhân viên.`);
    showToast('Đã tạo nhân sự.');
    await loadEmployees();
  } catch (error) {
    setStatus('employeeFormStatus', `Không thể tạo nhân sự: ${error.message}`, true);
  }
}

async function loadOrderFormData() {
  if (!currentUser || currentUser.role !== 'staff') return false;
  const customerSelect = document.getElementById('orderCustomer');
  const productSelect = document.getElementById('orderProduct');
  setStatus('orderStatus', 'Đang tải khách hàng và sản phẩm...');
  try {
    const [customers, products] = await Promise.all([
      apiRequest('/api/customers'),
      apiRequest('/api/products?limit=100&offset=0')
    ]);
    customerSelect.replaceChildren();
    productSelect.replaceChildren();
    customers.items.forEach(customer => {
      const option = document.createElement('option');
      option.value = customer.ma_khach_hang;
      option.textContent = `${customer.ho_ten} · ${customer.ma_khach_hang} · ${customer.so_dien_thoai}`;
      customerSelect.appendChild(option);
    });
    products.items.forEach(product => {
      const option = document.createElement('option');
      option.value = product.ma_san_pham;
      option.textContent = `${product.ten_san_pham} · ${product.ma_san_pham} · ${formatVND(product.gia_ban)}`;
      productSelect.appendChild(option);
    });
    if (!customers.items.length) setStatus('orderStatus', 'Chưa có khách hàng trong database.');
    else setStatus('orderStatus', 'Sẵn sàng tạo đơn.');
    return customers.items.length > 0 && products.items.length > 0;
  } catch (error) {
    setStatus('orderStatus', `Không thể tải dữ liệu đơn hàng: ${error.message}`, true);
    return false;
  }
}

async function handleCreateOrder(event) {
  event.preventDefault();
  const button = document.querySelector('#orderForm button');
  button.disabled = true;
  setStatus('orderStatus', 'Đang tạo đơn...');
  try {
    const result = await apiRequest('/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        customer_id: document.getElementById('orderCustomer').value,
        details: [{
          product_id: document.getElementById('orderProduct').value,
          quantity: Number(document.getElementById('orderQuantity').value)
        }]
      })
    });
    setStatus('orderStatus', `Tạo đơn thành công: ${result.order_id}.`);
    showToast(`Đã tạo đơn ${result.order_id}.`);
  } catch (error) {
    setStatus('orderStatus', `Không thể tạo đơn: ${error.message}`, true);
    showToast(`Tạo đơn thất bại: ${error.message}`);
  } finally {
    button.disabled = false;
  }
}

async function loadDistribution() {
  const body = document.getElementById('distributionTableBody');
  if (!body) return false;
  body.replaceChildren();
  setStatus('distributionStatus', 'Đang tải số lượng phân phối...');
  try {
    const { items } = await apiRequest('/api/employee/distribution');
    if (!items.length) renderMessage(body, 'Chưa có dữ liệu phân phối cho cửa hàng.');
    items.forEach(item => {
      const row = document.createElement('tr');
      appendCell(row, `${item.ten_san_pham} · ${item.mau_sac} · ${item.kich_co}`);
      appendCell(row, item.ma_san_pham, 'px-3 text-zinc-700');
      appendCell(row, item.so_luong_phan_phoi, 'pl-3 text-zinc-700');
      body.appendChild(row);
    });
    setStatus('distributionStatus', `${items.length} sản phẩm có dữ liệu phân phối. Đây không phải tồn kho hiện tại.`);
    return true;
  } catch (error) {
    renderMessage(body, `Không thể tải phân phối: ${error.message}`, 'text-red-600');
    setStatus('distributionStatus', `Không thể tải dữ liệu: ${error.message}`, true);
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
    await apiRequest('/api/health/db', {}, false);
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
  if (!currentUser) return false;
  const button = document.getElementById('syncBtn');
  const text = document.getElementById('syncBtnText');
  button.disabled = true;
  text.textContent = 'Đang tải dữ liệu...';
  try {
    const tasks = currentUser.role === 'staff'
      ? [checkBackendHealth(), loadProducts(), loadCategories(), loadOrderFormData(), loadDistribution()]
      : [checkBackendHealth(), loadProducts(), loadCategories(), loadStores(), loadAnalyticsSummary(), loadSalesAnalytics()];
    const results = await Promise.allSettled(tasks);
    const success = results.every(result => result.status === 'fulfilled' && result.value === true);
    if (notify) showToast(success ? 'Đã tải lại dữ liệu từ database.' : 'Tải dữ liệu chưa hoàn tất. Xem lỗi tại từng mục.');
    return success;
  } finally {
    button.disabled = false;
    text.textContent = 'Tải lại dữ liệu';
  }
}

window.onload = function () {
  if (window.lucide) lucide.createIcons();
  document.getElementById('mobileMenuBtn').addEventListener('click', toggleMobileMenu);
  document.getElementById('loginForm').addEventListener('submit', handleLogin);
  document.getElementById('employeeForm').addEventListener('submit', handleCreateEmployee);
  document.getElementById('employeeRole').addEventListener('change', updateEmployeeFormScope);
  document.getElementById('orderForm').addEventListener('submit', handleCreateOrder);
  showLogin();
  return false;
};
