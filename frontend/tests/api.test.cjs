const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

function dashboard(role = 'staff', configured = true, firstLogin = false) {
  const elements = new Map();
  const requests = [];
  const responses = new Map();
  const classes = new Set();
  function element(tagName = 'DIV', id = '') {
    const listeners = {};
    const childElements = [];
    return {
      tagName,
      id,
      textContent: '',
      innerHTML: '',
      children: childElements,
      disabled: false,
      style: {},
      value: '',
      dataset: {},
      className: '',
      listeners,
      setAttribute() {},
      classList: {
        add(...names) { names.forEach(name => classes.add(`${id}:${name}`)); },
        remove(...names) { names.forEach(name => classes.delete(`${id}:${name}`)); },
        contains(name) { return classes.has(`${id}:${name}`); },
        toggle(name) {
          if (classes.has(`${id}:${name}`)) classes.delete(`${id}:${name}`);
          else classes.add(`${id}:${name}`);
        }
      },
      append(...nodes) { childElements.push(...nodes); },
      appendChild(child) {
        childElements.push(child);
        if (tagName === 'SELECT' && !this.value) this.value = child.value;
      },
      replaceChildren(...nodes) {
        childElements.splice(0, childElements.length, ...nodes);
        if (tagName === 'SELECT') this.value = nodes[0]?.value || '';
      },
      addEventListener(name, callback) { listeners[name] = callback; },
      reset() { this.value = ''; }
    };
  }

  const navButtons = ['my-account', 'accounts', 'analytics', 'products', 'categories', 'settings', 'employees', 'queries', 'orders', 'distribution'].map(tab => {
    const button = element('BUTTON', `nav-${tab}`);
    button.dataset.tab = tab;
    button.classList.add('nav-btn');
    return button;
  });
  const orderSubmit = element('BUTTON', 'order-submit');
  let loginCalls = 0;
  const window = {
    FASHION_MANAGER_API_URL: configured ? 'https://api.example.com/' : '',
    innerWidth: 1200,
    location: { pathname: '/', reload() {} }
  };
  const document = {
    referrer: '',
    getElementById(id) {
      if (!elements.has(id)) {
        const tag = ['productTableBody', 'orderLogBody', 'employeeTableBody', 'distributionTableBody', 'orderHistoryBody', 'movementTableBody', 'reportTableBody'].includes(id)
          ? 'TBODY'
          : ['orderCustomer', 'orderProduct', 'orderStore', 'orderWarehouse', 'employeeStore', 'querySelect', 'reportGroup', 'adjustWarehouse', 'adjustProduct', 'transferSource', 'transferTarget', 'transferProduct'].includes(id)
            ? 'SELECT' : 'DIV';
        elements.set(id, element(tag, id));
      }
      return elements.get(id);
    },
    createElement(tag) { return element(tag.toUpperCase()); },
    querySelectorAll(selector) { return selector === '.nav-btn' ? navButtons : []; },
    querySelector(selector) { return selector === '#orderForm button' ? orderSubmit : null; }
  };
  function respond(url, options) {
    requests.push({ url, options });
    const override = responses.get(new URL(url).pathname);
    if (override) return override(url, options);
    if (url.endsWith('/api/auth/login')) {
      loginCalls++;
      return ok({
        access_token: `test-token-${loginCalls}`,
        user: {
          employee_id: role === 'staff' ? 'NV200' : 'NV000',
          name: 'Test user',
          phone: '0900000000',
          role,
          permissions: role === 'unassigned' ? [] : role === 'staff'
            ? ['catalog.read','stores.read', 'sales.create', 'inventory.read', 'customers.read']
            : ['catalog.read','stores.read', 'reports.read', 'employees.read', 'employees.write', ...(role === 'admin' ? ['queries.execute','auth.grant'] : [])],
          assignments: role === 'unassigned' ? [] : [{ ma_vai_tro: role, pham_vi: role === 'admin' ? 'system' : 'store', ma_cua_hang: 'CH01', permissions: role === 'admin' ? ['queries.execute','auth.grant'] : [] }],
          region_id: role === 'regional_manager' ? 1 : null,
          store_id: role === 'staff' || role === 'store_manager' ? 'CH01' : null,
          must_change_password: firstLogin && loginCalls === 1
        }
      });
    }
    if (url.endsWith('/api/auth/password')) return ok({ status: 'password_changed' });
    if (url.endsWith('/api/analytics/sales')) return ok({
      total_orders: 0, total_revenue: 0, categories: [], orders: [],
      daily: Array.from({ length: 30 }, (_, index) => ({ date: `2026-10-${String(index + 1).padStart(2, '0')}`, count: 0, revenue: 0 })),
      hourly: Array.from({ length: 24 }, (_, hour) => ({ hour, count: 0 }))
    });
    if (url.includes('/api/analytics/summary')) return ok({ total_products: 40, total_categories: 20, total_stores: 1, total_orders: 0 });
    if (url.endsWith('/api/health/db')) return ok({ status: 'ok' });
    if (url.endsWith('/api/products?limit=100&offset=0')) return ok({
      items: [{ ma_san_pham: 'SP01', ten_san_pham: 'Áo', mau_sac: 'Đen', kich_co: 'M', gia_ban: 100000 }]
    });
    if (url.endsWith('/api/customers')) return ok({
      items: [{ ma_khach_hang: 'KH01', ho_ten: 'Khách', so_dien_thoai: '0900000001' }]
    });
    if (url.includes('/api/stores?permission=sales.create')) return ok({items: [{ma_cua_hang: 'CH01', ten_cua_hang: 'Shop'}]});
    if (url.endsWith('/api/warehouses')) return ok({items: [{ma_kho: 'K01', ma_cua_hang: 'CH01', ten_kho: 'Stock'}]});
    if (url.endsWith('/api/orders')) return ok({ order_id: 'DH01', status: 'created' }, 201);
    if (url.endsWith('/api/employee/distribution')) return ok({ items: [{ ma_kho: 'K01', ma_san_pham: 'SP01', ten_san_pham: 'Áo', so_luong: 4 }] });
    if (url.endsWith('/api/employees')) return ok({ items: [] });
    if (url.endsWith('/api/employees/stores')) return ok({ items: [] });
    if (url.endsWith('/api/query-explorer')) return ok({
      items: [{ query_id: 'M02_Q01', title: 'Nhan vien va cua hang 1' }]
    });
    if (url.endsWith('/api/query-explorer/M02_Q01')) return ok({
      query_id: 'M02_Q01',
      columns: ['ma_nhan_vien', 'ho_ten'],
      items: [{ ma_nhan_vien: 'NV001', ho_ten: 'Nguyễn An' }]
    });
    if (url.endsWith('/api/stores')) return ok({ items: [] });
    if (url.endsWith('/api/categories')) return ok({ items: [] });
    if (url.includes('/api/products?')) return ok({ items: [] });
    return ok({ items: [] });
  }

  const context = vm.createContext({
    window,
    document,
    fetch: async (url, options) => respond(url, options),
    AbortSignal,
    Intl,
    Date,
    crypto: require('node:crypto').webcrypto,
    setTimeout() {},
    clearTimeout() {}
  });
  // Match inputs present in index.html before onload; the fake DOM is lazy.
  ['loginPhone', 'loginPassword', 'loginSubmit'].forEach(id => document.getElementById(id));
  document.getElementById('orderQuantity').value = '1';
  for (const filename of ['api.js', 'charts.js', 'app.js']) {
    vm.runInContext(fs.readFileSync(path.join(__dirname, '../js', filename), 'utf8'), context);
  }
  return { context, elements, navButtons, requests, responses, window };
}

const ok = (payload, status = 200) => ({ ok: status >= 200 && status < 300, status, json: async () => payload });

async function loginAs(app) {
  await app.context.window.onload();
  app.elements.get('loginPhone').value = '0900000000';
  app.elements.get('loginPassword').value = 'NV200';
  await app.elements.get('loginForm').listeners.submit({ preventDefault() {} });
}

test('unauthenticated startup stays at login and makes no protected requests', async () => {
  const app = dashboard();
  assert.equal(await app.context.window.onload(), false);
  assert.equal(app.requests.length, 0);
  assert.equal(app.elements.get('authPanel').classList.contains('hidden'), false);
  assert.ok(app.navButtons.every(button => button.classList.contains('hidden')));
});

test('staff sees order and distribution tabs while managers do not see order creation', async () => {
  const staff = dashboard('staff');
  await loginAs(staff);
  assert.equal(staff.navButtons.find(button => button.dataset.tab === 'orders').classList.contains('hidden'), false);
  assert.equal(staff.navButtons.find(button => button.dataset.tab === 'distribution').classList.contains('hidden'), false);
  assert.equal(staff.navButtons.find(button => button.dataset.tab === 'employees').classList.contains('hidden'), true);
  assert.ok(staff.requests.filter(request => request.options.headers?.Authorization).length > 0);
  assert.ok(staff.requests.some(request => request.url.endsWith('/api/customers')));

  const manager = dashboard('store_manager');
  await loginAs(manager);
  assert.equal(manager.navButtons.find(button => button.dataset.tab === 'orders').classList.contains('hidden'), true);
  assert.equal(manager.navButtons.find(button => button.dataset.tab === 'employees').classList.contains('hidden'), false);
  assert.equal(manager.navButtons.find(button => button.dataset.tab === 'accounts').classList.contains('hidden'), false);
  assert.equal(manager.navButtons.find(button => button.dataset.tab === 'queries').classList.contains('hidden'), true);
  assert.ok(manager.requests.some(request => request.url.endsWith('/api/analytics/sales')));
  await manager.context.loadAccounts();
  assert.ok(manager.requests.some(request => request.url.endsWith('/api/access/accounts')));
  assert.equal(manager.requests.some(request => request.url.endsWith('/api/access/roles')), false);
});

test('admin can run a predefined query and view dynamically shaped results', async () => {
  const app = dashboard('admin');
  await loginAs(app);
  const queryNav = app.navButtons.find(button => button.dataset.tab === 'queries');
  assert.equal(queryNav.classList.contains('hidden'), false);

  app.context.switchTab('queries');
  await app.context.loadAcademicQueries();
  app.elements.get('querySelect').value = 'M02_Q01';
  assert.equal(await app.context.runAcademicQuery(), true);

  assert.ok(app.requests.some(request => request.url.endsWith('/api/query-explorer/M02_Q01')
    && request.options.method === 'POST'));
  assert.deepEqual(app.elements.get('queryResultHead').children[0].children.map(cell => cell.textContent), [
    'ma_nhan_vien', 'ho_ten'
  ]);
  assert.deepEqual(app.elements.get('queryResultBody').children[0].children.map(cell => cell.textContent), [
    'NV001', 'Nguyễn An'
  ]);
});

test('sales chart ends on the last day in the 30-day order period', () => {
  const app = dashboard('admin');
  app.context.renderSalesAnalytics({
    period: { start: '2026-07-24', end: '2026-08-22', mode: 'latest_order' },
    total_orders: 2,
    total_revenue: 350000,
    daily: Array.from({ length: 30 }, (_, index) => {
      const date = new Date(Date.UTC(2026, 6, 24 + index)).toISOString().slice(0, 10);
      return { date, count: 0, revenue: 0 };
    }),
    hourly: Array.from({ length: 24 }, (_, hour) => ({ hour, count: 0 })),
    categories: [],
    orders: []
  });

  assert.equal(app.elements.get('chartFirstDate').textContent, '24/07');
  assert.equal(app.elements.get('chartMiddleDate').textContent, '08/08');
  assert.equal(app.elements.get('chartLastDate').textContent, '22/08');
});

test('staff order submission uses authenticated API and reports success', async () => {
  const app = dashboard('staff');
  await loginAs(app);
  const form = app.elements.get('orderForm');
  await form.listeners.submit({ preventDefault() {} });
  const orderRequest = app.requests.find(request => request.url.endsWith('/api/orders'));
  assert.ok(orderRequest);
  assert.equal(orderRequest.options.headers.Authorization, 'Bearer test-token-1');
  assert.deepEqual(JSON.parse(orderRequest.options.body), {
    customer_id: 'KH01',
    store_id: 'CH01',
    warehouse_id: 'K01',
    details: [{ product_id: 'SP01', quantity: 1 }]
  });
  assert.match(app.elements.get('orderStatus').textContent, /DH01/);
});

test('a first-time customer can be registered before creating an order', async () => {
  const app = dashboard('staff');
  await loginAs(app);
  app.responses.set('/api/customers', (url, options) => ok({customer_id: JSON.parse(options.body).customer_id}, 201));
  app.context.document.getElementById('newCustomerName').value = 'New customer';
  app.context.document.getElementById('newCustomerPhone').value = '0900000777';
  await app.elements.get('orderForm').listeners.submit({preventDefault() {}});
  const created = app.requests.find(request => request.url.endsWith('/api/customers') && request.options.method === 'POST');
  const sale = app.requests.find(request => request.url.endsWith('/api/orders'));
  assert.equal(JSON.parse(sale.options.body).customer_id, JSON.parse(created.options.body).customer_id);
});

test('an absent amount is not displayed as zero currency', () => {
  const app = dashboard();
  assert.equal(app.context.formatVND(null), 'Chưa đủ dữ liệu');
  assert.notEqual(app.context.formatVND(0), app.context.formatVND(null));
});

test('login does not call an unavailable password-rotation endpoint', async () => {
  const app = dashboard('staff', true, true);
  await loginAs(app);
  assert.equal(app.elements.get('dashboardContent').classList.contains('hidden'), false);
  assert.equal(app.requests.some(request => request.url.endsWith('/api/auth/password')), false);
});

test('a signed-in user can change their password without losing the current session', async () => {
  const app = dashboard('staff');
  await loginAs(app);
  app.responses.set('/api/auth/password', (url, options) => {
    assert.equal(options.headers.Authorization, 'Bearer test-token-1');
    assert.deepEqual(JSON.parse(options.body), {
      current_password: 'old-password-is-long-enough',
      new_password: 'new-password-is-long-enough'
    });
    return ok({ access_token: 'rotated-token' });
  });
  app.context.document.getElementById('currentPassword').value = 'old-password-is-long-enough';
  app.context.document.getElementById('newPassword').value = 'new-password-is-long-enough';
  app.context.document.getElementById('confirmPassword').value = 'new-password-is-long-enough';
  const form=app.context.document.getElementById('passwordForm');
  await form.listeners.submit({
    preventDefault() {},
    currentTarget: form
  });
  assert.match(app.elements.get('passwordStatus').textContent, /Đã đổi mật khẩu/);
  await app.context.apiRequest('/api/auth/me');
  assert.equal(app.requests.at(-1).options.headers.Authorization, 'Bearer rotated-token');
});

test('sales history loads scoped orders and submits cancellation only when permitted', async () => {
  const app = dashboard('staff');
  await loginAs(app);
  vm.runInContext("currentUser.permissions.push('sales.read','sales.cancel')", app.context);
  app.responses.set('/api/orders', url => new URL(url).search
    ? ok({items:[{ma_don_hang:'DH01',ngay_tao_don:'2026-11-09',ma_cua_hang:'S1',ten_cua_hang:'Shop',trang_thai:'completed',quantity:2,total:300000}]})
    : ok({order_id:'DH01'}));
  assert.equal(await app.context.loadOrders(), true);
  const row=app.elements.get('orderHistoryBody').children[0];
  assert.equal(row.children[0].textContent,'DH01 · 2026-11-09');
  await row.children[5].children[1].listeners.click();
  const cancel=app.requests.find(request=>request.url.endsWith('/api/orders/DH01/cancel'));
  assert.equal(cancel.options.method,'POST');
});

test('business report sends the selected dates and grouping and renders returned totals', async () => {
  const app=dashboard('staff');
  await loginAs(app);
  vm.runInContext("currentUser.permissions.push('reports.read')",app.context);
  app.context.document.getElementById('reportStart').value='2026-11-01';
  app.context.document.getElementById('reportEnd').value='2026-11-09';
  app.context.document.getElementById('reportGroup').value='store';
  app.responses.set('/api/reports',()=>ok({sales:[{ma:'S1',so_don:3,so_luong:5,doanh_thu:250000}]}));
  assert.equal(await app.context.loadBusinessReport(),true);
  assert.ok(app.requests.some(request=>request.url.endsWith('/api/reports?start=2026-11-01&end=2026-11-09&group=store')));
  assert.deepEqual(app.elements.get('reportTableBody').children[0].children.map(cell=>String(cell.textContent)),[
    'S1','3','5',app.context.formatVND(250000)
  ]);
});

test('inventory forms submit scoped adjustment and transfer payloads', async () => {
  const app=dashboard('staff');
  await loginAs(app);
  vm.runInContext("currentUser.permissions.push('inventory.adjust','inventory.transfer')",app.context);
  app.responses.set('/api/warehouses',()=>ok({items:[
    {ma_kho:'K1',ten_kho:'Kho 1'},{ma_kho:'K2',ten_kho:'Kho 2'}
  ]}));
  assert.equal(await app.context.loadDistribution(),true);
  app.context.document.getElementById('adjustQuantity').value='2';
  app.context.document.getElementById('adjustReason').value='Kiểm kê';
  const adjustmentForm=app.context.document.getElementById('adjustmentForm');
  await adjustmentForm.listeners.submit({preventDefault(){},currentTarget:adjustmentForm});
  const adjustment=app.requests.find(request=>request.url.endsWith('/api/inventory/adjustments'));
  assert.deepEqual(JSON.parse(adjustment.options.body),{
    warehouse_id:'K1',product_id:'SP01',quantity:2,reason:'Kiểm kê'
  });
  app.context.document.getElementById('transferSource').value='K1';
  app.context.document.getElementById('transferTarget').value='K2';
  app.context.document.getElementById('transferQuantity').value='3';
  const transferForm=app.context.document.getElementById('transferForm');
  await transferForm.listeners.submit({preventDefault(){},currentTarget:transferForm});
  const transfer=app.requests.find(request=>request.url.endsWith('/api/inventory/transfers'));
  assert.deepEqual(JSON.parse(transfer.options.body),{
    source_id:'K1',target_id:'K2',details:[{product_id:'SP01',quantity:3}]
  });
});

test('missing deployment configuration never calls the API', async () => {
  const app = dashboard('staff', false);
  await app.context.window.onload();
  await assert.rejects(() => app.context.apiRequest('/api/products'), /Chưa cấu hình URL backend/);
  assert.equal(app.requests.length, 0);
});

test('login loads each dashboard endpoint once and clears the password input', async () => {
  const app = dashboard('admin');
  await loginAs(app);
  for (const endpoint of ['/api/analytics/sales', '/api/products?limit=21&offset=0', '/api/categories']) {
    assert.equal(app.requests.filter(request => request.url.endsWith(endpoint)).length, 1);
  }
  assert.equal(app.elements.get('loginPassword').value, '');
  assert.equal(app.elements.get('loginSubmit').disabled, false);
});

test('account without grants sees only its own account and loads no business endpoint', async () => {
  const app = dashboard('unassigned');
  await loginAs(app);
  assert.equal(app.navButtons.find(button => button.dataset.tab === 'my-account').classList.contains('hidden'), false);
  assert.equal(app.navButtons.find(button => button.dataset.tab === 'products').classList.contains('hidden'), true);
  assert.equal(app.navButtons.find(button => button.dataset.tab === 'accounts').classList.contains('hidden'), true);
  assert.equal(app.requests.some(request => request.url.includes('/api/products?')), false);
  assert.equal(app.requests.some(request => request.url.endsWith('/api/analytics/sales')), false);
  app.responses.set('/api/auth/me', () => ok({user:{employee_id:'E1',name:'No grants',phone:'+84900000000',account_id:'A1',workplaces:[{ten_chuc_vu:'Sales',ten_noi_lam_viec:'Shop 1',ma_cua_hang:'S1'}],assignments:[]}}));
  await app.context.loadMyAccount();
  assert.equal(app.elements.get('myAccountGrants').children[0].textContent, 'Tài khoản chưa được gán quyền nghiệp vụ.');
});

test('account administration shows position, scoped permissions and account controls', async () => {
  const app = dashboard('admin');
  await loginAs(app);
  app.elements.get('accountForm').parentElement = app.context.document.createElement('section');
  app.responses.set('/api/access/roles',()=>ok({roles:[{ma_vai_tro:'sales_staff',ten_vai_tro:'Sales Staff'}],permissions:[]}));
  app.responses.set('/api/access/accounts',()=>ok({items:[
    {ma_nhan_vien:'E1',ho_ten:'One',so_dien_thoai:'+84900000001',employee_status:'active',ma_tai_khoan:null,account_status:null,workplaces:[{ten_chuc_vu:'Sales',ten_noi_lam_viec:'Shop 1'}],assignments:[]},
    {ma_nhan_vien:'E2',ho_ten:'Two',so_dien_thoai:'+84900000002',employee_status:'active',ma_tai_khoan:'A2',account_status:'active',workplaces:[{ten_chuc_vu:'Manager',ten_noi_lam_viec:'Shop 2'}],assignments:[{ma_phan_cong:7,ma_vai_tro:'sales_staff',pham_vi:'store',ma_cua_hang:'S2',effective:true,tu_ngay:'2026-01-01',den_ngay:null,trang_thai:'active',permissions:['sales.read','sales.create']}]}
  ]}));
  await app.context.loadAccounts();
  const cards=app.elements.get('accountRows').children;
  assert.equal(cards.length,2);
  assert.ok(cards[1].children.some(child=>child.textContent.includes('Manager @ Shop 2')));
  assert.ok(cards[1].children.some(child=>child.children?.some(line=>line.textContent.includes('Cửa hàng: S2'))));
  assert.equal(JSON.stringify(cards).includes('mat_khau_hash'),false);
  assert.equal(app.elements.get('accountEmployee').children[0].value,'E1');
});

test('expired authentication returns to login and stops sending the old token', async () => {
  const app = dashboard('staff');
  await loginAs(app);
  app.responses.set('/api/customers', () => ok({ detail: 'Phiên đăng nhập đã hết hạn.' }, 401));
  await assert.rejects(() => app.context.apiRequest('/api/customers'), /hết hạn/);
  assert.equal(app.elements.get('dashboardContent').classList.contains('hidden'), true);
  assert.equal(app.elements.get('authPanel').classList.contains('hidden'), false);
  await app.context.apiRequest('/api/categories');
  assert.equal(app.requests.at(-1).options.headers.Authorization, undefined);
});

test('API validation errors include the invalid field and reason', async () => {
  const app = dashboard();
  app.responses.set('/api/orders', () => ok({ detail: [
    { loc: ['body', 'details', 0, 'quantity'], msg: 'Input should be greater than 0' }
  ] }, 422));
  await assert.rejects(() => app.context.apiRequest('/api/orders', { method: 'POST' }),
    /details\.0\.Số lượng: Input should be greater than 0/);
});

test('employee deletion explains when the backend does not expose the endpoint', async () => {
  const app = dashboard('admin');
  await loginAs(app);
  app.responses.set('/api/employees/NV100', () => ok({ detail: 'Not Found' }, 404));

  await assert.rejects(() => app.context.apiRequest('/api/employees/NV100', { method: 'DELETE' }),
    /Backend chưa có API đuổi việc nhân viên/);
});

test('database errors make synchronization fail without showing success', async () => {
  const app = dashboard('admin');
  await loginAs(app);
  app.responses.set('/api/analytics/summary', () => ok({ detail: 'Không thể đọc MySQL.' }, 503));
  assert.equal(await app.context.triggerSync(), false);
  assert.match(app.elements.get('summaryStatus').textContent, /Không thể đọc MySQL/);
  assert.match(app.elements.get('toastText').textContent, /chưa hoàn tất/);
  assert.equal(app.elements.get('summaryOrders').textContent, '—');
});
