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

  const navButtons = ['analytics', 'products', 'categories', 'settings', 'employees', 'queries', 'orders', 'distribution'].map(tab => {
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
        const tag = ['productTableBody', 'orderLogBody', 'employeeTableBody', 'distributionTableBody'].includes(id)
          ? 'TBODY'
          : ['orderCustomer', 'orderProduct', 'employeeRole', 'employeeStore', 'employeeRegion', 'querySelect'].includes(id)
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
    if (url.endsWith('/api/orders')) return ok({ order_id: 'DH01', status: 'created' }, 201);
    if (url.endsWith('/api/employee/distribution')) return ok({ items: [{ ma_san_pham: 'SP01', ten_san_pham: 'Áo', so_luong_phan_phoi: 4 }] });
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
  assert.equal(manager.navButtons.find(button => button.dataset.tab === 'queries').classList.contains('hidden'), true);
  assert.ok(manager.requests.some(request => request.url.endsWith('/api/analytics/sales')));
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
    details: [{ product_id: 'SP01', quantity: 1 }]
  });
  assert.match(app.elements.get('orderStatus').textContent, /DH01/);
});

test('obsolete password-rotation flags do not block the current employee-ID login flow', async () => {
  const app = dashboard('staff', true, true);
  await loginAs(app);
  assert.equal(app.elements.get('dashboardContent').classList.contains('hidden'), false);
  assert.equal(app.requests.some(request => request.url.endsWith('/api/auth/password')), false);
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
    /details\.0\.quantity: Input should be greater than 0/);
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
