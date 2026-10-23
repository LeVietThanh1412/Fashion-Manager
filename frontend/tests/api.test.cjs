const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

function dashboard(respond, configured = true) {
  const elements = new Map();
  function element(tagName = 'DIV') {
    return {
      tagName, textContent: '', innerHTML: '', children: [], disabled: false,
      classList: { add() {}, remove() {}, contains() { return false; } },
      append(...children) { this.children.push(...children); },
      appendChild(child) { this.children.push(child); },
      addEventListener() {}
    };
  }
  const calls = [];
  const context = vm.createContext({
    window: { FASHION_MANAGER_API_URL: configured ? 'https://api.example.com/' : '' },
    document: {
      getElementById(id) {
        if (!elements.has(id)) elements.set(id, element(id === 'productTableBody' ? 'TBODY' : 'DIV'));
        return elements.get(id);
      },
      createElement(tag) { return element(tag.toUpperCase()); }
    },
    fetch: async url => { calls.push(url); return respond(url); },
    AbortSignal, Intl, Date, setTimeout() {}, clearTimeout() {}
  });
  for (const filename of ['api.js', 'app.js']) {
    vm.runInContext(fs.readFileSync(path.join(__dirname, '../js', filename), 'utf8'), context);
  }
  return { context, elements, calls };
}

const ok = payload => ({ ok: true, status: 200, json: async () => payload });
function realResponse(url) {
  if (url.includes('/summary')) return ok({ total_products: 40, total_categories: 20, total_stores: 20, total_orders: 50 });
  if (url.includes('/health/db')) return ok({ status: 'ok' });
  return ok({ items: [] });
}

test('startup calls every data endpoint, including stores and DB health', async () => {
  const { context, calls, elements } = dashboard(realResponse);
  assert.equal(await context.window.onload(), true);
  assert.equal(calls.length, 5);
  assert.ok(calls.some(url => url.endsWith('/api/stores')));
  assert.ok(calls.some(url => url.endsWith('/api/health/db')));
  assert.equal(elements.get('summaryProducts').textContent, '40');
  assert.equal(elements.get('syncBtn').disabled, false);
});

test('API failure clears old statistics and does not claim successful sync', async () => {
  let failed = false;
  const { context, elements } = dashboard(url => failed
    ? { ok: false, status: 503, json: async () => ({ detail: 'Database unavailable' }) }
    : realResponse(url));
  await context.window.onload();
  failed = true;
  assert.equal(await context.triggerSync(), false);
  assert.equal(elements.get('summaryProducts').textContent, '—');
  assert.match(elements.get('summaryStatus').textContent, /Database unavailable/);
  assert.match(elements.get('toastText').textContent, /chưa hoàn tất/);
  assert.equal(elements.get('syncBtn').disabled, false);
});

test('missing deployment configuration never calls localhost', async () => {
  const { context, calls } = dashboard(realResponse, false);
  assert.equal(await context.window.onload(), false);
  assert.equal(calls.length, 0);
});

test('pagination reads the next products from the API', async () => {
  const items = Array.from({ length: 21 }, (_, i) => ({ ten_san_pham: `Product ${i}`, mau_sac: 'Blue', kich_co: 'M', gia_ban: 1000, ma_danh_muc: 'DM' }));
  const { context, elements, calls } = dashboard(() => ok({ items }));
  await context.loadProducts();
  assert.equal(elements.get('productsNext').disabled, false);
  assert.equal(elements.get('productTableBody').children.at(-1).tagName, 'TR');
  await context.changeProductPage(1);
  assert.ok(calls.at(-1).endsWith('limit=21&offset=20'));
});
