function renderSalesBars(id, items, label) {
  const chart = document.getElementById(id);
  chart.innerHTML = '';
  const max = Math.max(1, ...items.map(item => item.count));
  items.forEach(item => {
    const column = document.createElement('div');
    column.className = 'flex-1 h-full flex items-end min-w-0';
    const bar = document.createElement('div');
    bar.className = `w-full rounded-t-sm transition-all duration-300 ${item.count ? 'bg-zinc-900 hover:bg-zinc-700' : 'bg-zinc-200'}`;
    bar.style.height = item.count ? `${Math.max(3, item.count / max * 100)}%` : '2px';
    bar.title = `${label(item)}: ${item.count} đơn hàng${item.revenue === undefined ? '' : ` · ${formatVND(item.revenue)}`}`;
    bar.setAttribute('aria-label', bar.title);
    column.appendChild(bar);
    chart.appendChild(column);
  });
}

function salesDateLabel(value) {
  const [, month, day] = value.split('-');
  return `${day}/${month}`;
}

function clearSalesAnalytics(message) {
  document.getElementById('salesTotal').textContent = message;
  document.getElementById('salesStatus').textContent = message;
  document.getElementById('salesRevenue').textContent = '—';
  ['chart30Days', 'chartHourly', 'categoryDistribution', 'orderLogBody'].forEach(id => renderMessage(document.getElementById(id), message));
  ['chartFirstDate', 'chartMiddleDate'].forEach(id => { document.getElementById(id).textContent = '—'; });
}

function renderSalesAnalytics(data) {
  document.getElementById('salesTotal').textContent = `${new Intl.NumberFormat('vi-VN').format(data.total_orders)} đơn hàng trong 30 ngày gần nhất`;
  document.getElementById('salesRevenue').textContent = `Doanh thu ước tính (giá hiện tại): ${formatVND(data.total_revenue)}`;
  renderSalesBars('chart30Days', data.daily, item => salesDateLabel(item.date));
  renderSalesBars('chartHourly', data.hourly, item => `${item.hour}h`);
  document.getElementById('chartFirstDate').textContent = salesDateLabel(data.daily[0].date);
  document.getElementById('chartMiddleDate').textContent = salesDateLabel(data.daily[15].date);
  const distribution = document.getElementById('categoryDistribution');
  distribution.innerHTML = '';
  const totalProducts = data.categories.reduce((sum, item) => sum + item.count, 0);
  if (!data.categories.length) renderMessage(distribution, 'Chưa có danh mục sản phẩm.');
  data.categories.forEach(category => {
    const row = document.createElement('div');
    row.className = 'grid grid-cols-12 items-center gap-3 text-sm';
    const name = document.createElement('span');
    name.className = 'col-span-5 text-zinc-700 truncate';
    name.textContent = category.name;
    name.title = category.name;
    const track = document.createElement('div');
    track.className = 'col-span-5 h-2 bg-zinc-200 rounded-full overflow-hidden';
    const bar = document.createElement('div');
    bar.className = 'h-full bg-zinc-900 rounded-full';
    bar.style.width = `${totalProducts ? category.count / totalProducts * 100 : 0}%`;
    track.appendChild(bar);
    const count = document.createElement('span');
    count.className = 'col-span-2 text-right text-zinc-900';
    count.textContent = `${category.count} SP`;
    row.append(name, track, count);
    distribution.appendChild(row);
  });
  const tbody = document.getElementById('orderLogBody');
  tbody.innerHTML = '';
  if (!data.orders.length) renderMessage(tbody, 'Database chưa có đơn hàng.');
  data.orders.forEach(order => {
    const row = document.createElement('tr');
    const timestamp = new Intl.DateTimeFormat('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', hourCycle: 'h23', timeZone: 'Asia/Ho_Chi_Minh' }).format(new Date(order.timestamp));
    [timestamp, order.id, order.customer_id, order.store, order.quantity, formatVND(order.total)].forEach(value => {
      const cell = document.createElement('td');
      cell.className = 'py-3.5 pr-4 text-zinc-600 break-words';
      cell.textContent = value;
      row.appendChild(cell);
    });
    tbody.appendChild(row);
  });
  const now = new Date().toLocaleTimeString('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh' });
  document.getElementById('salesStatus').textContent = `${data.orders.length} đơn gần nhất, toàn bộ thời gian · Cập nhật ${now}`;
}

async function loadSalesAnalytics() {
  clearSalesAnalytics('Đang tải dữ liệu bán hàng...');
  try {
    renderSalesAnalytics(await apiRequest('/api/analytics/sales'));
    return true;
  } catch (error) {
    clearSalesAnalytics(`Không thể tải thống kê bán hàng: ${error.message}`);
    return false;
  }
}
