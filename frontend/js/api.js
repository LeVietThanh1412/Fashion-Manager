const API_BASE = 'http://127.0.0.1:8000';

// ── Fallback demo data ────────────────────────────────────────────
const _DEMO_PRODUCTS = [
  { ma_san_pham: 'SP001', ten_san_pham: 'Áo khoác Denim', mau_sac: 'Xanh', kich_co: 'M', gia_ban: 490000, ma_danh_muc: 'DM01' },
  { ma_san_pham: 'SP002', ten_san_pham: 'Áo khoác Denim', mau_sac: 'Đen', kich_co: 'L', gia_ban: 490000, ma_danh_muc: 'DM01' },
  { ma_san_pham: 'SP003', ten_san_pham: 'Quần jeans Slim', mau_sac: 'Xanh', kich_co: 'S', gia_ban: 390000, ma_danh_muc: 'DM02' },
  { ma_san_pham: 'SP004', ten_san_pham: 'Quần jeans Slim', mau_sac: 'Đen', kich_co: 'M', gia_ban: 390000, ma_danh_muc: 'DM02' },
  { ma_san_pham: 'SP005', ten_san_pham: 'Váy midi hoa', mau_sac: 'Hồng', kich_co: 'M', gia_ban: 420000, ma_danh_muc: 'DM03' },
  { ma_san_pham: 'SP006', ten_san_pham: 'Áo thun cotton', mau_sac: 'Trắng', kich_co: 'L', gia_ban: 220000, ma_danh_muc: 'DM04' },
  { ma_san_pham: 'SP007', ten_san_pham: 'Áo thun cotton', mau_sac: 'Đen', kich_co: 'XL', gia_ban: 220000, ma_danh_muc: 'DM04' },
];

const _DEMO_CATEGORIES = [
  { ma_danh_muc: 'DM01', ten_danh_muc: 'Áo khoác thu đông', slug: 'ao-khoac-thu-dong', so_san_pham: 12 },
  { ma_danh_muc: 'DM02', ten_danh_muc: 'Bộ sưu tập mới', slug: 'bo-suu-tap-moi', so_san_pham: 8 },
  { ma_danh_muc: 'DM03', ten_danh_muc: 'Áo sơ mi & kiểu', slug: 'ao-so-mi', so_san_pham: 15 },
  { ma_danh_muc: 'DM04', ten_danh_muc: 'Quần dài', slug: 'quan-dai', so_san_pham: 10 },
];

// ── Helpers ───────────────────────────────────────────────────────
function formatVND(amount) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
}

// ── Products ──────────────────────────────────────────────────────
async function loadProducts() {
  let items = _DEMO_PRODUCTS;
  try {
    const res = await fetch(`${API_BASE}/api/products`);
    if (res.ok) {
      const data = await res.json();
      if (data.items && data.items.length > 0) items = data.items;
    }
  } catch (_) { /* backend offline – use demo data */ }

  const tbody = document.getElementById('productTableBody');
  if (!tbody) return;
  tbody.innerHTML = '';
  items.forEach(p => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-zinc-200/30 transition-colors';
    tr.innerHTML = `
      <td class="py-3.5 pr-4 font-medium text-zinc-900">${p.ten_san_pham}</td>
      <td class="py-3.5 px-4 text-zinc-600">${p.mau_sac} · ${p.kich_co}</td>
      <td class="py-3.5 px-4 text-zinc-900">${formatVND(p.gia_ban)}</td>
      <td class="py-3.5 pl-4 text-zinc-500 text-xs">${p.ma_danh_muc}</td>
    `;
    tbody.appendChild(tr);
  });
}

// ── Categories ────────────────────────────────────────────────────
async function loadCategories() {
  let items = _DEMO_CATEGORIES;
  try {
    const res = await fetch(`${API_BASE}/api/categories`);
    if (res.ok) {
      const data = await res.json();
      if (data.items && data.items.length > 0) items = data.items;
    }
  } catch (_) { /* backend offline – use demo data */ }

  const grid = document.getElementById('categoriesGrid');
  if (!grid) return;
  grid.innerHTML = '';
  items.forEach(cat => {
    const slug = cat.slug || cat.ma_danh_muc;
    const count = cat.so_san_pham != null ? cat.so_san_pham : '?';
    const div = document.createElement('div');
    div.className = 'p-4 rounded-xl bg-white border border-zinc-200/80 flex items-center justify-between';
    div.innerHTML = `
      <div>
        <div class="font-medium text-sm text-zinc-900">${cat.ten_danh_muc}</div>
        <div class="text-xs text-zinc-500 mt-0.5">/san-pham?danh-muc=${slug}</div>
      </div>
      <span class="text-xs font-medium bg-zinc-100 px-2.5 py-1 rounded-md text-zinc-700">${count} SP</span>
    `;
    grid.appendChild(div);
  });
}

// ── Backend Health / Sync ─────────────────────────────────────────
async function checkBackendHealth() {
  const syncDot = document.getElementById('syncDot');
  const syncTitle = document.getElementById('syncTitle');
  const syncDesc = document.getElementById('syncDesc');
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (res.ok) {
      if (syncDot) syncDot.className = 'w-2 h-2 rounded-full bg-emerald-600 inline-block';
      if (syncTitle) syncTitle.textContent = 'Backend đang kết nối';
      if (syncDesc) syncDesc.textContent = 'API đang hoạt động. Dữ liệu được lấy từ server.';
    } else {
      throw new Error('not ok');
    }
  } catch (_) {
    if (syncDot) syncDot.className = 'w-2 h-2 rounded-full bg-zinc-400 inline-block';
    if (syncTitle) syncTitle.textContent = 'Chế độ Demo';
    if (syncDesc) syncDesc.textContent = 'Backend offline. Hiển thị dữ liệu mẫu.';
  }
}

async function triggerSync() {
  const btn = document.getElementById('syncBtn');
  const btnText = document.getElementById('syncBtnText');
  const syncDot = document.getElementById('syncDot');
  const syncTitle = document.getElementById('syncTitle');

  btn.disabled = true;
  btn.classList.add('opacity-80');
  btnText.textContent = 'Đang đồng bộ...';
  syncDot.className = 'w-2 h-2 rounded-full bg-amber-500 animate-ping inline-block';

  await checkBackendHealth();
  await loadProducts();
  await loadCategories();

  setTimeout(() => {
    btn.disabled = false;
    btn.classList.remove('opacity-80');
    btnText.textContent = 'Đồng bộ dữ liệu';
    showToast('Đồng bộ dữ liệu cửa hàng thời trang thành công!');
  }, 800);
}

