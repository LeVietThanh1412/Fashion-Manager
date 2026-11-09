const REGION_NAMES = {};
const ROLE_NAMES = {
  system_admin: 'Quản trị hệ thống',
  operations_manager: 'Quản lý toàn chuỗi',
  sales_staff: 'Nhân viên bán hàng',
  warehouse_staff: 'Nhân viên kho',
  unassigned: 'Chưa được phân quyền',
  regional_manager: 'Quản lý khu vực',
  store_manager: 'Quản lý cửa hàng',
  staff: 'Nhân viên'
};
let employeeStores = [];
let availableGrantScopes = {regions:[],stores:[],warehouses:[]};
let academicQueries = [];

function setVisible(element, visible) {
  if (!element) return;
  if (visible) element.classList.remove('hidden');
  else element.classList.add('hidden');
}

function switchTab(tabId, loadData = true) {
  const tabs = ['my-account','accounts','analytics', 'products', 'categories', 'settings', 'employees', 'queries', 'orders', 'distribution'];
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
  if (tabId === 'analytics') {
    loadSalesAnalytics();
    loadBusinessReport();
  }
  if (tabId === 'employees') loadEmployees();
  if (tabId === 'my-account') loadMyAccount();
  if (tabId === 'accounts') loadAccounts();
  if (tabId === 'queries') loadAcademicQueries();
  if (tabId === 'orders') {
    if (can('sales.create')) loadOrderFormData();
    if (can('sales.read')) loadOrders();
  }
  if (tabId === 'distribution') loadDistribution();
}

function scopeLabel(grant) {
  return grant.pham_vi === 'system' ? 'Toàn hệ thống' :
    `${{region:'Khu vực',store:'Cửa hàng',warehouse:'Kho'}[grant.pham_vi]}: ${grant.ma_khu_vuc ?? grant.ma_cua_hang ?? grant.ma_kho}`;
}

function addText(parent, tag, value, className='') {
  const node=document.createElement(tag);
  node.textContent=value;
  node.className=className;
  parent.appendChild(node);
  return node;
}

async function loadMyAccount() {
  const profile=document.getElementById('myAccountProfile');
  const grants=document.getElementById('myAccountGrants');
  profile.replaceChildren(); grants.replaceChildren();
  try {
    const {user}=await apiRequest('/api/auth/me');
    currentUser=user;
    addText(profile,'p',`${user.name} · ${user.employee_id} · ${user.phone}`);
    if (user.email) addText(profile,'p',`Email: ${user.email}`);
    if (user.manager_id) addText(profile,'p',`Quản lý trực tiếp: ${user.manager_id}`);
    if (user.salary != null) addText(profile,'p',`Lương: ${formatVND(user.salary)}`);
    addText(profile,'p',`Tài khoản: ${user.account_id}`);
    (user.workplaces || []).forEach(work => addText(profile,'p',`${work.ten_chuc_vu} · ${work.ten_noi_lam_viec} (${work.ma_cua_hang || work.ma_kho})`));
    if (!user.assignments.length) addText(grants,'p','Tài khoản chưa được gán quyền nghiệp vụ.');
    user.assignments.forEach(grant => {
      const card=addText(grants,'div','', 'border rounded p-3');
      addText(card,'p',`${ROLE_NAMES[grant.ma_vai_tro] || grant.ma_vai_tro} · ${scopeLabel(grant)}`,'font-semibold');
      addText(card,'p',`Hiệu lực: ${grant.tu_ngay} → ${grant.den_ngay || 'không thời hạn'}`);
      addText(card,'p',`Quyền trong phạm vi này: ${grant.permissions.join(', ')}`);
    });
  } catch (error) { addText(profile,'p',error.message,'text-red-600'); }
}

function systemGrantAdmin() {
  return (currentUser?.assignments || []).some(g => g.pham_vi==='system' && g.permissions.includes('auth.grant'));
}

function renderGrantScopeOptions() {
  const scope=document.getElementById('grantScope').value;
  const input=document.getElementById('grantScopeId');
  const list=document.getElementById('grantScopeOptions');
  input.value='';
  input.disabled=scope==='system';
  list.replaceChildren();
  const rows=scope==='region'?availableGrantScopes.regions:scope==='store'?availableGrantScopes.stores:scope==='warehouse'?availableGrantScopes.warehouses:[];
  rows.forEach(item=>{
    const option=document.createElement('option');
    option.value=String(item.ma_khu_vuc ?? item.ma_cua_hang ?? item.ma_kho);
    option.label=item.ten_khu_vuc ?? item.ten_cua_hang ?? item.ten_kho;
    list.appendChild(option);
  });
}

async function accountAction(path,method,body) {
  try {
    await apiRequest(path,{method,headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    await loadAccounts();
    showToast('Đã cập nhật tài khoản.');
  } catch (error) { setStatus('accountsStatus',error.message,true); }
}

async function loadAccounts() {
  const container=document.getElementById('accountRows');
  container.replaceChildren();
  setStatus('accountsStatus','Đang tải tài khoản...');
  try {
    const data=await apiRequest('/api/access/accounts');
    const canGrant=can('auth.grant');
    if (canGrant) {
      const [catalog,scopes]=await Promise.all([apiRequest('/api/access/roles'),apiRequest('/api/access/scopes')]);
      availableGrantScopes=scopes;
      renderGrantScopeOptions();
      const roleSelect=document.getElementById('grantRole');
      roleSelect.replaceChildren();
      catalog.roles.forEach(role=>{
        const node=document.createElement('option');
        node.value=role.ma_vai_tro;
        node.textContent=role.ten_vai_tro;
        roleSelect.appendChild(node);
      });
    }
    const employeeSelect=document.getElementById('accountEmployee');
    const accountSelect=document.getElementById('grantAccount');
    [employeeSelect,accountSelect].forEach(select=>select.replaceChildren());
    const option=(select,value,label)=>{const node=document.createElement('option');node.value=value;node.textContent=label;select.appendChild(node);};
    data.items.forEach(person=>{
      if (!person.ma_tai_khoan && person.employee_status==='active') option(employeeSelect,person.ma_nhan_vien,`${person.ho_ten} · ${person.ma_nhan_vien}`);
      else option(accountSelect,person.ma_tai_khoan,`${person.ho_ten} · ${person.ma_tai_khoan}`);
      const card=addText(container,'div','', 'border rounded p-4 text-sm');
      addText(card,'h3',`${person.ho_ten} · ${person.ma_nhan_vien} · ${person.so_dien_thoai}`,'font-semibold');
      addText(card,'p',`Chức vụ / nơi làm việc: ${person.workplaces.map(w=>`${w.ten_chuc_vu} @ ${w.ten_noi_lam_viec}`).join('; ') || 'Chưa phân công'}`);
      addText(card,'p',`Tài khoản: ${person.ma_tai_khoan || 'chưa có'} · ${person.account_status || '—'}`);
      person.assignments.forEach(grant=>{
        const detail=addText(card,'div','', 'mt-2 pl-3 border-l');
        addText(detail,'p',`${grant.ma_vai_tro} · ${scopeLabel(grant)} · ${grant.effective ? 'đang hiệu lực' : grant.thu_hoi_luc ? 'đã thu hồi' : 'chưa hiệu lực / hết hạn'}`);
        addText(detail,'p',`Từ ${grant.tu_ngay} đến ${grant.den_ngay || 'không thời hạn'} · ${grant.trang_thai}`);
        addText(detail,'p',`Quyền: ${grant.permissions.join(', ')}`);
        if (systemGrantAdmin() && grant.effective) {
          const button=addText(detail,'button','Thu hồi','border rounded px-2 py-1 mt-1');
          button.addEventListener('click',()=>accountAction(`/api/access/assignments/${grant.ma_phan_cong}/revoke`,'POST',{}));
        }
      });
      if (person.ma_tai_khoan && systemGrantAdmin()) {
        const controls=addText(card,'div','', 'flex flex-wrap gap-2 mt-3');
        if (person.ma_tai_khoan !== currentUser.account_id) {
          const next=person.account_status==='active'?'locked':'active';
          const button=addText(controls,'button',next==='active'?'Kích hoạt':'Khóa','border rounded px-2 py-1');
          button.addEventListener('click',()=>accountAction(`/api/access/accounts/${encodeURIComponent(person.ma_tai_khoan)}/status`,'PUT',{status:next}));
        }
        const password=document.createElement('input');
        password.type='password';password.minLength=12;password.autocomplete='new-password';password.placeholder='Mật khẩu mới (12+ ký tự)';password.className='border rounded px-2 py-1';
        controls.appendChild(password);
        const reset=addText(controls,'button','Đặt lại mật khẩu','border rounded px-2 py-1');
        reset.addEventListener('click',async()=>{if(password.value.length<12)return setStatus('accountsStatus','Mật khẩu cần ít nhất 12 ký tự.',true);const value=password.value;password.value='';await accountAction(`/api/access/accounts/${encodeURIComponent(person.ma_tai_khoan)}/password`,'PUT',{password:value});});
      }
    });
    setVisible(document.getElementById('accountCreateSection'),can('employees.write') || can('auth.grant'));
    setVisible(document.getElementById('roleGrantSection'),canGrant);
    setStatus('accountsStatus',`${data.items.length} hồ sơ trong phạm vi quản trị.`);
  } catch (error) {setStatus('accountsStatus',error.message,true);}
}

async function handleCreateAccount(event) {
  event.preventDefault();
  const password=document.getElementById('accountPassword');
  const payload={employee_id:document.getElementById('accountEmployee').value,account_id:document.getElementById('accountId').value.trim(),password:password.value};
  password.value='';
  await accountAction('/api/access/accounts','POST',payload);
  event.target.reset();
}

async function handleGrant(event) {
  event.preventDefault();
  const scope=document.getElementById('grantScope').value;
  const key={region:'ma_khu_vuc',store:'ma_cua_hang',warehouse:'ma_kho'}[scope];
  const id=document.getElementById('grantScopeId').value.trim();
  if (key && !id) return setStatus('accountsStatus','Cần nhập mã phạm vi.',true);
  const data={ma_tai_khoan:document.getElementById('grantAccount').value,ma_vai_tro:document.getElementById('grantRole').value,
    pham_vi:scope,tu_ngay:new Date(document.getElementById('grantStart').value).toISOString(),
    den_ngay:document.getElementById('grantEnd').value?new Date(document.getElementById('grantEnd').value).toISOString():null,
    duoc_uy_quyen:document.getElementById('grantDelegable').checked};
  if (key) data[key]=scope==='region'?Number(id):id;
  await accountAction('/api/access/assignments','POST',data);
}

async function handlePasswordChange(event) {
  event.preventDefault();
  const form=event.currentTarget;
  const currentPassword=document.getElementById('currentPassword');
  const newPassword=document.getElementById('newPassword');
  const confirmPassword=document.getElementById('confirmPassword');
  if (newPassword.value !== confirmPassword.value) {
    setStatus('passwordStatus','Mật khẩu mới nhập lại không khớp.',true);
    return;
  }
  const current=currentPassword.value;
  const next=newPassword.value;
  currentPassword.value='';
  newPassword.value='';
  confirmPassword.value='';
  try {
    await changePassword(current,next);
    setStatus('passwordStatus','Đã đổi mật khẩu. Phiên đăng nhập hiện tại vẫn được duy trì.',false);
    showToast('Đã đổi mật khẩu.');
  } catch (error) {
    setStatus('passwordStatus',error.message,true);
  } finally {
    form.reset();
  }
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

function can(permission) {
  return Boolean(currentUser?.permissions?.includes(permission));
}

function updateRoleNavigation(user) {
  const tabs = { analytics: 'reports.read', settings: 'stores.read', employees: 'employees.read',
    queries: 'queries.execute', distribution: 'inventory.read',
    products: 'catalog.read', categories: 'catalog.read' };
  document.querySelectorAll('.nav-btn').forEach(button => {
    const visible = button.dataset.tab === 'my-account'
      || (button.dataset.tab === 'accounts' ? can('employees.write') || can('auth.grant')
        : button.dataset.tab === 'orders' ? can('sales.create') || can('sales.read')
          : can(tabs[button.dataset.tab]));
    setVisible(button, visible);
    if (visible) button.classList.add('flex');
  });
  setVisible(document.getElementById('employeeCreatePanel'), can('employees.write'));
  setVisible(document.getElementById('orderCreateSection'),can('sales.create'));
  setVisible(document.getElementById('orderHistorySection'),can('sales.read'));
  setVisible(document.getElementById('orderExportButton'),can('reports.read'));
  const scope = document.getElementById('employeeScope');
  if (scope) scope.textContent = (user.assignments || []).map(g =>
    `${ROLE_NAMES[g.ma_vai_tro] || g.ma_vai_tro}: ${g.pham_vi === 'system' ? 'toàn hệ thống' : g.ma_cua_hang || g.ma_kho || REGION_NAMES[g.ma_khu_vuc] || g.ma_khu_vuc}`).join(' · ');
}

async function showAuthenticated(user) {
  currentUser = user;
  productPage = 0;
  setVisible(document.getElementById('syncBtn'), true);
  setVisible(document.getElementById('authPanel'), false);
  setVisible(document.getElementById('dashboardContent'), true);
  setVisible(document.getElementById('accountActions'), true);
  document.getElementById('accountLabel').textContent = `${user.name} · ${ROLE_NAMES[user.role] || user.role}`;
  updateRoleNavigation(user);
  switchTab(can('reports.read') ? 'analytics' : can('sales.create') ? 'orders' : 'my-account', false);
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
      details.textContent = `${store.ma_cua_hang} · ${store.ten_khu_vuc || store.khu_vuc} · ${store.dia_chi} · ${store.so_dien_thoai}`;
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
    if (method === 'DELETE' && path.startsWith('/api/employees/')) {
      setStatus('employeeStatus', `Không thể đuổi việc: ${error.message}`, true);
      showToast('Không thể đuổi việc. Xem chi tiết trong thông báo nhân sự.');
    } else {
      showToast(`Thao tác thất bại: ${error.message}`);
    }
  }
}

async function loadEmployees() {
  const body = document.getElementById('employeeTableBody');
  if (!body || !currentUser) return false;
  setStatus('employeeStatus', 'Đang tải nhân sự...');
  body.replaceChildren();
  try {
    const [employees, stores, positions] = await Promise.all([
      apiRequest('/api/employees'),
      can('employees.write') ? apiRequest('/api/employees/stores') : Promise.resolve({items: []}),
      can('employees.write') ? apiRequest('/api/positions') : Promise.resolve({items: []})
    ]);
    employeeStores = stores.items;
    const positionSelect = document.getElementById('employeePosition');
    positionSelect.replaceChildren();
    positions.items.forEach(position => {
      const option=document.createElement('option');
      option.value=position.ma_chuc_vu; option.textContent=position.ten_chuc_vu;
      positionSelect.appendChild(option);
    });
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
      row.cells[2].textContent = employee.positions_workplaces || 'Chưa phân công';

      const actions = document.createElement('td');
      actions.className = 'pl-3 py-2';
      const isSelf = employee.ma_nhan_vien === currentUser.employee_id;
      if (!isSelf && can('employees.salary')) {
        const salary = document.createElement('input');
        salary.type = 'number'; salary.min = '0.01'; salary.step = '0.01';
        salary.value = employee.luong;
        salary.className = 'w-28 rounded border px-2 py-1 text-xs mr-1';
        actions.appendChild(salary);
        actions.appendChild(makeAction('Lưu lương', () => {
          const value = Number(salary.value);
          if (!Number.isFinite(value) || value <= 0) return showToast('Lương phải lớn hơn 0.');
          performEmployeeAction(employee.ma_nhan_vien, `/api/employees/${encodeURIComponent(employee.ma_nhan_vien)}/salary`, 'PUT', {salary: salary.value}, 'Đã cập nhật lương.');
        }));
      }
      if (!isSelf && can('employees.write')) {
        const status=employee.trang_thai==='active'?'inactive':'active';
        actions.appendChild(makeAction(status==='inactive'?'Ngừng làm việc':'Kích hoạt nhân viên', () => {
          performEmployeeAction(employee.ma_nhan_vien, `/api/employees/${encodeURIComponent(employee.ma_nhan_vien)}/status`, 'PUT', {status},
            status==='inactive'?'Đã ngừng làm việc và khóa đăng nhập.':'Đã kích hoạt nhân sự; tài khoản đăng nhập vẫn cần được kích hoạt riêng.');
        }));
        if (employeeStores.length) {
          const storeSelect=document.createElement('select');
          storeSelect.className='rounded border px-2 py-1 text-xs mr-1';
          employeeStores.forEach(store=>{
            const option=document.createElement('option');
            option.value=store.ma_cua_hang;
            option.textContent=`${store.ma_cua_hang} · ${store.ten_cua_hang}`;
            option.selected=store.ma_cua_hang===employee.ma_cua_hang;
            storeSelect.appendChild(option);
          });
          actions.appendChild(storeSelect);
          actions.appendChild(makeAction('Chuyển cửa hàng',()=>{
            if (storeSelect.value===employee.ma_cua_hang) return showToast('Nhân viên đã làm việc tại cửa hàng này.');
            performEmployeeAction(employee.ma_nhan_vien,`/api/employees/${encodeURIComponent(employee.ma_nhan_vien)}/work`,'POST',
              {store_id:storeSelect.value},'Đã cập nhật nơi làm việc.');
          }));
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


async function handleCreateEmployee(event) {
  event.preventDefault();
  const salary = Number(document.getElementById('employeeSalary').value);
  if (!Number.isFinite(salary) || salary <= 0) {
    setStatus('employeeFormStatus', 'Lương phải là số nguyên dương theo ràng buộc database.', true);
    return;
  }
  const payload = {
    employee_id: document.getElementById('employeeId').value.trim(),
    name: document.getElementById('employeeName').value.trim(),
    phone: document.getElementById('employeePhone').value.trim(),
    email: document.getElementById('employeeEmail').value.trim(),
    store_id: document.getElementById('employeeStore').value,
    position_id: document.getElementById('employeePosition').value,
    salary
  };
  try {
    const result = await apiRequest('/api/employees', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    document.getElementById('employeeForm').reset();
    setStatus('employeeFormStatus', `Đã tạo ${result.employee_id}; hồ sơ nhân sự chưa có tài khoản đăng nhập hoặc quyền.`);
    showToast('Đã tạo nhân sự.');
    await loadEmployees();
  } catch (error) {
    setStatus('employeeFormStatus', `Không thể tạo nhân sự: ${error.message}`, true);
  }
}

async function loadOrderFormData() {
  if (!currentUser || !can('sales.create')) return false;
  const customerSelect = document.getElementById('orderCustomer');
  const productSelect = document.getElementById('orderProduct');
  setStatus('orderStatus', 'Đang tải khách hàng và sản phẩm...');
  try {
    const [customers, products, stores, warehouses] = await Promise.all([
      apiRequest('/api/customers'),
      apiRequest('/api/products?limit=100&offset=0'),
      apiRequest('/api/stores?permission=sales.create'),
      can('inventory.read') ? apiRequest('/api/warehouses') : Promise.resolve({items: []})
    ]);
    const storeSelect = document.getElementById('orderStore');
    storeSelect.replaceChildren();
    stores.items.forEach(store => {
      const option = document.createElement('option');
      option.value = store.ma_cua_hang; option.textContent = `${store.ma_cua_hang} · ${store.ten_cua_hang}`;
      storeSelect.appendChild(option);
    });
    function fillWarehouses() {
      const select = document.getElementById('orderWarehouse'); select.replaceChildren();
      warehouses.items.filter(w => w.ma_cua_hang === storeSelect.value).forEach(w => {
        const option = document.createElement('option'); option.value = w.ma_kho; option.textContent = w.ten_kho; select.appendChild(option);
      });
    }
    storeSelect.onchange = fillWarehouses; fillWarehouses();
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
      option.textContent = `${product.ten_san_pham} · ${product.ma_san_pham} · ${product.mau_sac} · ${product.kich_co} · ${formatVND(product.gia_ban)}`;
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
    let customerId = document.getElementById('orderCustomer').value;
    const newName = document.getElementById('newCustomerName').value.trim();
    const newPhone = document.getElementById('newCustomerPhone').value.trim();
    if (newName || newPhone) {
      if (!newName || !newPhone) throw new Error('Nhập đủ tên và số điện thoại khách mới.');
      const created = await apiRequest('/api/customers', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({customer_id: `KH${crypto.randomUUID().replaceAll('-', '').slice(0,18)}`, name: newName, phone: newPhone})
      });
      customerId = created.customer_id;
      const option = document.createElement('option'); option.value = customerId; option.textContent = `${newName} · ${customerId}`;
      document.getElementById('orderCustomer').appendChild(option);
      document.getElementById('orderCustomer').value = customerId;
      document.getElementById('newCustomerName').value = '';
      document.getElementById('newCustomerPhone').value = '';
    }
    if (!customerId) throw new Error('Chọn khách hàng hoặc nhập thông tin khách mới.');
    const result = await apiRequest('/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        customer_id: customerId,
        store_id: document.getElementById('orderStore').value,
        warehouse_id: document.getElementById('orderWarehouse').value || null,
        details: [{
          product_id: document.getElementById('orderProduct').value,
          quantity: Number(document.getElementById('orderQuantity').value)
        }]
      })
    });
    setStatus('orderStatus', `Tạo đơn thành công: ${result.order_id}.`);
    showToast(`Đã tạo đơn ${result.order_id}.`);
    if (can('sales.read')) await loadOrders();
    if (can('inventory.read')) await loadDistribution();
  } catch (error) {
    setStatus('orderStatus', `Không thể tạo đơn: ${error.message}`, true);
    showToast(`Tạo đơn thất bại: ${error.message}`);
  } finally {
    button.disabled = false;
  }
}

async function loadOrders() {
  const body=document.getElementById('orderHistoryBody');
  if (!body||!can('sales.read')) return false;
  body.replaceChildren();
  setStatus('orderHistoryStatus','Đang tải đơn hàng...');
  try {
    const {items}=await apiRequest('/api/orders?limit=100&offset=0');
    if (!items.length) renderMessage(body,'Chưa có đơn hàng trong phạm vi được phép.');
    items.forEach(order=>{
      const row=document.createElement('tr');
      appendCell(row,`${order.ma_don_hang} · ${order.ngay_tao_don}`);
      appendCell(row,`${order.ma_cua_hang} · ${order.ten_cua_hang||''}`,'px-3');
      appendCell(row,order.trang_thai==='cancelled'?'Đã hủy':'Hoàn tất','px-3');
      appendCell(row,order.quantity,'px-3');
      appendCell(row,formatVND(order.total),'px-3');
      const actions=document.createElement('td');
      actions.className='pl-3 py-2';
      const details=addText(actions,'button','Chi tiết','border rounded px-2 py-1 mr-1');
      details.addEventListener('click',()=>showOrderDetails(order.ma_don_hang,row));
      if (can('sales.cancel')&&order.trang_thai==='completed') {
        const cancel=addText(actions,'button','Hủy đơn','border rounded px-2 py-1 text-red-700');
        cancel.addEventListener('click',()=>cancelOrder(order.ma_don_hang));
      }
      row.appendChild(actions);
      body.appendChild(row);
    });
    setStatus('orderHistoryStatus',`${items.length} đơn hàng gần nhất trong phạm vi được phép.`);
    return true;
  } catch (error) {
    renderMessage(body,`Không thể tải đơn hàng: ${error.message}`,'text-red-600');
    setStatus('orderHistoryStatus',error.message,true);
    return false;
  }
}

async function showOrderDetails(orderId,row) {
  const existing=row.nextElementSibling;
  if (existing&&existing.dataset.orderDetails===orderId) {
    existing.remove();
    return;
  }
  try {
    const order=await apiRequest(`/api/orders/${encodeURIComponent(orderId)}`);
    const detailRow=document.createElement('tr');
    detailRow.dataset.orderDetails=orderId;
    const cell=addText(detailRow,'td','', 'px-4 py-3 bg-white text-sm');
    cell.colSpan=6;
    order.details.forEach(line=>addText(cell,'p',`${line.ma_san_pham} · ${line.so_luong} sản phẩm · ${formatVND(line.don_gia_ban)} · Giảm ${formatVND(line.giam_gia)}`));
    row.parentElement.insertBefore(detailRow,row.nextSibling);
  } catch (error) {
    setStatus('orderHistoryStatus',`Không thể tải chi tiết ${orderId}: ${error.message}`,true);
  }
}

async function cancelOrder(orderId) {
  try {
    await apiRequest(`/api/orders/${encodeURIComponent(orderId)}/cancel`,{method:'POST'});
    showToast(`Đã hủy đơn ${orderId} và hoàn kho.`);
    await Promise.all([loadOrders(),can('inventory.read')?loadDistribution():Promise.resolve(true)]);
  } catch (error) {
    setStatus('orderHistoryStatus',`Không thể hủy đơn ${orderId}: ${error.message}`,true);
  }
}

async function downloadOrders() {
  try {
    await apiDownload('/api/orders/export','orders.csv');
  } catch (error) {
    setStatus('orderHistoryStatus',`Không thể tải CSV: ${error.message}`,true);
  }
}

async function loadBusinessReport() {
  const body=document.getElementById('reportTableBody');
  if (!body||!can('reports.read')) return false;
  const start=document.getElementById('reportStart').value;
  const end=document.getElementById('reportEnd').value;
  if (!start||!end) {
    setStatus('reportStatus','Chọn khoảng ngày để xem báo cáo.');
    return false;
  }
  body.replaceChildren();
  setStatus('reportStatus','Đang tổng hợp báo cáo...');
  try {
    const group=document.getElementById('reportGroup').value;
    const {sales}=await apiRequest(`/api/reports?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}&group=${encodeURIComponent(group)}`);
    if (!sales.length) renderMessage(body,'Không có doanh thu trong khoảng ngày này.');
    sales.forEach(item=>{
      const row=document.createElement('tr');
      appendCell(row,item.ma??'—');
      appendCell(row,item.so_don,'px-3');
      appendCell(row,item.so_luong??0,'px-3');
      appendCell(row,formatVND(item.doanh_thu),'pl-3');
      body.appendChild(row);
    });
    setStatus('reportStatus',`${sales.length} nhóm doanh thu · ${start} đến ${end}.`);
    return true;
  } catch (error) {
    renderMessage(body,`Không thể tải báo cáo: ${error.message}`,'text-red-600');
    setStatus('reportStatus',error.message,true);
    return false;
  }
}

async function handleBusinessReport(event) {
  event.preventDefault();
  await loadBusinessReport();
}

async function loadDistribution() {
  const body = document.getElementById('distributionTableBody');
  if (!body) return false;
  body.replaceChildren();
  setStatus('distributionStatus', 'Đang tải tồn kho theo SKU...');
  try {
    const [inventory,movementData]=await Promise.all([
      apiRequest('/api/inventory'),
      apiRequest('/api/inventory/movements')
    ]);
    const {items}=inventory;
    if (!items.length) renderMessage(body, 'Chưa có dữ liệu tồn kho cho cửa hàng.');
    items.forEach(item => {
      const row = document.createElement('tr');
      appendCell(row, `${item.ten_san_pham} · ${item.mau_sac} · ${item.kich_co}`);
      appendCell(row, `${item.ma_san_pham} · ${item.ma_kho}`,  'px-3 text-zinc-700');
      appendCell(row, item.so_luong, 'pl-3 text-zinc-700');
      body.appendChild(row);
    });
    setStatus('distributionStatus', `${items.length} sản phẩm có dữ liệu tồn kho. Số lượng đã ghi nhận theo từng kho.`);
    await loadInventoryActions();
    renderMovements(movementData.items);
    return true;
  } catch (error) {
    renderMessage(body, `Không thể tải phân phối: ${error.message}`, 'text-red-600');
    setStatus('distributionStatus', `Không thể tải dữ liệu: ${error.message}`, true);
    return false;
  }
}

async function loadInventoryActions() {
  const canAdjust=can('inventory.adjust');
  const canTransfer=can('inventory.transfer');
  setVisible(document.getElementById('inventoryActions'),canAdjust||canTransfer);
  setVisible(document.getElementById('adjustmentForm'),canAdjust);
  setVisible(document.getElementById('transferForm'),canTransfer);
  if (!canAdjust&&!canTransfer) return;
  const [warehouses,products]=await Promise.all([
    apiRequest('/api/warehouses'),
    apiRequest('/api/products?limit=100&offset=0')
  ]);
  const addOptions=(select,items,value,label)=>{
    select.replaceChildren();
    items.forEach(item=>{
      const option=document.createElement('option');
      option.value=item[value];
      option.textContent=label(item);
      select.appendChild(option);
    });
  };
  if (canAdjust) {
    addOptions(document.getElementById('adjustWarehouse'),warehouses.items,'ma_kho',item=>`${item.ma_kho} · ${item.ten_kho}`);
    addOptions(document.getElementById('adjustProduct'),products.items,'ma_san_pham',item=>`${item.ma_san_pham} · ${item.ten_san_pham} · ${item.mau_sac} · ${item.kich_co}`);
  }
  if (canTransfer) {
    addOptions(document.getElementById('transferSource'),warehouses.items,'ma_kho',item=>`${item.ma_kho} · ${item.ten_kho}`);
    addOptions(document.getElementById('transferTarget'),warehouses.items,'ma_kho',item=>`${item.ma_kho} · ${item.ten_kho}`);
    addOptions(document.getElementById('transferProduct'),products.items,'ma_san_pham',item=>`${item.ma_san_pham} · ${item.ten_san_pham} · ${item.mau_sac} · ${item.kich_co}`);
  }
}

function renderMovements(movements) {
  const body=document.getElementById('movementTableBody');
  body.replaceChildren();
  if (!movements.length) renderMessage(body,'Chưa có biến động kho.');
  const reversed=new Set(movements.filter(item=>item.loai==='cancel_transfer').map(item=>item.ma_phan_phoi));
  const shownTransfers=new Set();
  movements.forEach(item=>{
    const row=document.createElement('tr');
    appendCell(row,item.tao_luc);
    appendCell(row,`${item.ma_kho} · ${item.ma_san_pham}`,'px-3');
    appendCell(row,item.loai,'px-3');
    appendCell(row,item.so_luong,'px-3');
    appendCell(row,`${item.ly_do}${item.ma_don_hang?` · ${item.ma_don_hang}`:''}${item.ma_phan_phoi?` · ${item.ma_phan_phoi}`:''}`,'px-3');
    const actions=document.createElement('td');
    actions.className='pl-3 py-2';
    if (can('inventory.transfer')&&item.ma_phan_phoi&&item.loai==='transfer'
        &&!reversed.has(item.ma_phan_phoi)&&!shownTransfers.has(item.ma_phan_phoi)) {
      shownTransfers.add(item.ma_phan_phoi);
      const button=addText(actions,'button','Hủy phiếu','border rounded px-2 py-1 text-red-700');
      button.addEventListener('click',()=>cancelTransfer(item.ma_phan_phoi));
    }
    row.appendChild(actions);
    body.appendChild(row);
  });
  setStatus('movementStatus',`${movements.length} biến động gần nhất.`);
}

async function handleAdjustment(event) {
  event.preventDefault();
  try {
    await apiRequest('/api/inventory/adjustments',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        warehouse_id:document.getElementById('adjustWarehouse').value,
        product_id:document.getElementById('adjustProduct').value,
        quantity:Number(document.getElementById('adjustQuantity').value),
        reason:document.getElementById('adjustReason').value.trim()
      })
    });
    event.currentTarget.reset();
    setStatus('adjustmentStatus','Đã ghi nhận điều chỉnh tồn kho.');
    await loadDistribution();
  } catch (error) {
    setStatus('adjustmentStatus',error.message,true);
  }
}

async function handleTransfer(event) {
  event.preventDefault();
  const source=document.getElementById('transferSource').value;
  const target=document.getElementById('transferTarget').value;
  if (!source||!target||source===target) {
    setStatus('transferStatus','Chọn hai kho khác nhau.',true);
    return;
  }
  try {
    const result=await apiRequest('/api/inventory/transfers',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        source_id:source,
        target_id:target,
        details:[{product_id:document.getElementById('transferProduct').value,quantity:Number(document.getElementById('transferQuantity').value)}]
      })
    });
    setStatus('transferStatus',`Đã tạo phiếu ${result.transfer_id}.`);
    await loadDistribution();
  } catch (error) {
    setStatus('transferStatus',error.message,true);
  }
}

async function cancelTransfer(transferId) {
  try {
    await apiRequest(`/api/inventory/transfers/${encodeURIComponent(transferId)}/cancel`,{method:'POST'});
    showToast(`Đã hủy phiếu ${transferId} và hoàn tồn kho.`);
    await loadDistribution();
  } catch (error) {
    setStatus('movementStatus',`Không thể hủy phiếu ${transferId}: ${error.message}`,true);
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
    title.textContent = 'Kiểm tra trạng thái gặp lỗi';
    description.textContent = 'Không đọc được /api/health/db. Xem log backend và tải lại; các số liệu khác có thể vẫn hoạt động.';
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
    const tasks = [checkBackendHealth()];
    if (can('catalog.read')) tasks.push(loadProducts(),loadCategories());
    if (can('stores.read')) tasks.push(loadStores());
    if (can('reports.read')) tasks.push(loadAnalyticsSummary(), loadSalesAnalytics());
    if (can('sales.create')) tasks.push(loadOrderFormData());
    if (can('sales.read')) tasks.push(loadOrders());
    if (can('inventory.read')) tasks.push(loadDistribution());
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
  document.getElementById('accountForm').addEventListener('submit', handleCreateAccount);
  document.getElementById('passwordForm').addEventListener('submit', handlePasswordChange);
  document.getElementById('grantForm').addEventListener('submit', handleGrant);
  document.getElementById('grantScope').addEventListener('change',renderGrantScopeOptions);
  document.getElementById('orderForm').addEventListener('submit', handleCreateOrder);
  document.getElementById('reportForm').addEventListener('submit', handleBusinessReport);
  document.getElementById('adjustmentForm').addEventListener('submit', handleAdjustment);
  document.getElementById('transferForm').addEventListener('submit', handleTransfer);
  showLogin();
  return false;
};
