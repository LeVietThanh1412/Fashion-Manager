const DEVICE_LABELS = { mobile: 'Điện thoại', tablet: 'Máy tính bảng', desktop: 'Máy tính' };

function renderVisitBars(id, items, label) {
  const chart = document.getElementById(id);
  chart.innerHTML = '';
  const max = Math.max(1, ...items.map(item => item.count));
  items.forEach(item => {
    const column = document.createElement('div');
    column.className = 'flex-1 h-full flex items-end min-w-0';
    const bar = document.createElement('div');
    bar.className = `w-full rounded-t-sm transition-all duration-300 ${item.count ? 'bg-zinc-900 hover:bg-zinc-700' : 'bg-zinc-200'}`;
    bar.style.height = item.count ? `${Math.max(3, item.count / max * 100)}%` : '2px';
    bar.title = `${label(item)}: ${item.count} lượt xem`;
    bar.setAttribute('aria-label', bar.title);
    column.appendChild(bar);
    chart.appendChild(column);
  });
}

function visitDateLabel(value) {
  const [, month, day] = value.split('-');
  return `${day}/${month}`;
}

function clearVisitAnalytics(message) {
  document.getElementById('visitsTotal').textContent = message;
  document.getElementById('visitsStatus').textContent = message;
  ['chart30Days', 'chartHourly'].forEach(id => renderMessage(document.getElementById(id), message));
  ['Mobile', 'Tablet', 'Desktop'].forEach(device => {
    document.getElementById(`count${device}`).textContent = '—';
    document.getElementById(`bar${device}`).style.width = '0%';
  });
  ['chartFirstDate', 'chartMiddleDate'].forEach(id => { document.getElementById(id).textContent = '—'; });
  renderMessage(document.getElementById('visitLogBody'), message);
}

function renderVisitAnalytics(data) {
  document.getElementById('visitsTotal').textContent = `Tổng cộng ${new Intl.NumberFormat('vi-VN').format(data.total)} lượt xem trang cửa hàng thời trang`;
  renderVisitBars('chart30Days', data.daily, item => visitDateLabel(item.date));
  renderVisitBars('chartHourly', data.hourly, item => `${item.hour}h`);
  document.getElementById('chartFirstDate').textContent = visitDateLabel(data.daily[0].date);
  document.getElementById('chartMiddleDate').textContent = visitDateLabel(data.daily[15].date);
  Object.entries({ mobile: 'Mobile', tablet: 'Tablet', desktop: 'Desktop' }).forEach(([key, suffix]) => {
    const count = data.devices[key];
    document.getElementById(`count${suffix}`).textContent = count;
    document.getElementById(`bar${suffix}`).style.width = `${data.total ? count / data.total * 100 : 0}%`;
  });
  const tbody = document.getElementById('visitLogBody');
  tbody.innerHTML = '';
  if (!data.visits.length) renderMessage(tbody, 'Chưa có lượt truy cập trong 30 ngày gần nhất.');
  data.visits.forEach(visit => {
    const row = document.createElement('tr');
    const timestamp = new Intl.DateTimeFormat('vi-VN', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23', timeZone: 'Asia/Ho_Chi_Minh' }).format(new Date(visit.timestamp));
    [timestamp, visit.path, visit.ip, visit.location || 'Chưa xác định', DEVICE_LABELS[visit.device], visit.referrer || 'Trực tiếp']
      .forEach(value => {
        const cell = document.createElement('td');
        cell.className = 'py-3.5 pr-4 text-zinc-600 break-words';
        cell.textContent = value;
        row.appendChild(cell);
      });
    tbody.appendChild(row);
  });
  const now = new Date().toLocaleTimeString('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh' });
  document.getElementById('visitsStatus').textContent = `${data.visits.length} lượt gần nhất · Cập nhật ${now}`;
}

async function loadVisitAnalytics() {
  clearVisitAnalytics('Đang tải dữ liệu...');
  try {
    renderVisitAnalytics(await apiRequest('/api/analytics/visits'));
    return true;
  } catch (error) {
    clearVisitAnalytics(`Không thể tải lượt xem: ${error.message}`);
    return false;
  }
}

async function recordPageVisit() {
  try {
    await apiRequest('/api/analytics/visits', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: window.location.pathname.slice(0, 500), referrer: document.referrer.slice(0, 2000) })
    });
    return true;
  } catch (_) {
    // Reading the dashboard still works for a read-only account; do not invent a visit.
    return false;
  }
}
