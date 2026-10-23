// --- 1. DATA FOR 30-DAY BAR CHART ---
const days30Data = Array.from({ length: 30 }, (_, i) => {
  if (i === 28) return { label: '22/10', views: 22 }; // Tall bar right before today
  if (i === 29) return { label: 'Hôm nay (23/10)', views: 2 }; // Short bar on far right
  return { label: `Ngày ${i + 1}`, views: 0 };
});

function render30DaysChart() {
  const container = document.getElementById('chart30Days');
  container.innerHTML = '';
  const maxViews = Math.max(...days30Data.map(d => d.views), 1);

  days30Data.forEach((day) => {
    const heightPercent = day.views > 0 ? Math.max((day.views / maxViews) * 100, 8) : 0;
    const barCol = document.createElement('div');
    barCol.className = 'flex-1 h-full flex flex-col justify-end items-center relative bar-hover group';

    if (day.views > 0) {
      barCol.innerHTML = `
        <div class="bar-tooltip opacity-0 transform translate-y-1 transition-all pointer-events-none absolute -top-7 bg-zinc-900 text-white text-[10px] py-0.5 px-1.5 rounded whitespace-nowrap z-10">
          ${day.label}: ${day.views}
        </div>
        <div class="w-full max-w-[22px] bg-zinc-900 rounded-t-[3px] transition-all duration-300" style="height: ${heightPercent}%"></div>
      `;
    } else {
      barCol.innerHTML = `<div class="w-full max-w-[22px] h-0 bg-transparent"></div>`;
    }
    container.appendChild(barCol);
  });
}

// --- 2. DATA FOR 24-HOUR BAR CHART ---
const hourlyViews = [
  0, 0, 0, 0, 0, 0, 0, 3, // 0h - 7h (bar at 7h)
  0, 0, 0, 0, 0, 0, 0, 0, // 8h - 15h
  4, 0, 0, 0, 14, 3, 9, 1  // 16h - 23h (cluster at 20h-23h)
];

function renderHourlyChart() {
  const container = document.getElementById('chartHourly');
  container.innerHTML = '';
  const maxHourViews = Math.max(...hourlyViews, 1);

  hourlyViews.forEach((views, hour) => {
    const heightPercent = views > 0 ? Math.max((views / maxHourViews) * 92, 9) : 0;
    const col = document.createElement('div');
    col.className = 'flex-1 h-full flex flex-col justify-end items-center relative bar-hover';

    if (views > 0) {
      col.innerHTML = `
        <div class="bar-tooltip opacity-0 transform translate-y-1 transition-all pointer-events-none absolute -top-7 bg-zinc-900 text-white text-[10px] py-0.5 px-1.5 rounded whitespace-nowrap z-10">
          ${hour}h: ${views} lượt
        </div>
        <div class="w-full max-w-[16px] bg-zinc-900 rounded-t-[3px] transition-all duration-300" style="height: ${heightPercent}%"></div>
      `;
    } else {
      col.innerHTML = `<div class="w-full max-w-[16px] h-0"></div>`;
    }
    container.appendChild(col);
  });
}

// --- 3. VISIT LOGS DATA ---
const visitLogs = [
  {
    time: '07:26:40 23/10/2026',
    page: 'Trang chủ',
    ip: '123.31.18.242',
    location: 'Cầu Giấy, Hanoi, Việt Nam',
    isp: 'Vietnam Posts and Telecommunications Group',
    device: 'Edge · Windows · Máy tính',
    referrer: ''
  },
  {
    time: '07:09:41 23/10/2026',
    page: '/san-pham?danh-muc=ao-khoac-thu-dong&trang=2',
    ip: '2402:9d80:22b:b2cc:605c:4739:cdb5:5797',
    location: 'Hanoi, Việt Nam',
    isp: 'Mobifone',
    device: 'Safari · iOS · Điện thoại',
    referrer: ''
  },
  {
    time: '22:45:12 22/10/2026',
    page: '/san-pham/ao-blazer-oversize-han-quoc',
    ip: '113.190.232.104',
    location: 'Đống Đa, Hanoi, Việt Nam',
    isp: 'Viettel Group',
    device: 'Chrome · Windows · Máy tính',
    referrer: 'facebook.com'
  },
  {
    time: '21:18:05 22/10/2026',
    page: '/san-pham?danh-muc=bo-suu-tap-moi',
    ip: '2405:4802:1d92:a410:8912:31ff:fe4a:1109',
    location: 'Ho Chi Minh City, Việt Nam',
    isp: 'FPT Telecom',
    device: 'Safari · iOS · Điện thoại',
    referrer: 'instagram.com'
  }
];

function renderVisitLogs() {
  const tbody = document.getElementById('visitLogBody');
  tbody.innerHTML = '';

  visitLogs.forEach(item => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-zinc-200/30 transition-colors';
    tr.innerHTML = `
      <td class="py-4 pr-4 text-zinc-800 whitespace-nowrap">${item.time}</td>
      <td class="py-4 px-4 text-zinc-800 break-all leading-relaxed">${item.page}</td>
      <td class="py-4 px-4 text-zinc-800 font-mono text-[12.5px] break-all">${item.ip}</td>
      <td class="py-4 px-4">
        <div class="flex items-start gap-1.5">
          <i data-lucide="map-pin" class="w-3.5 h-3.5 text-zinc-500 mt-0.5 shrink-0"></i>
          <div>
            <div class="text-zinc-900 font-medium leading-snug">${item.location}</div>
            <div class="text-[12px] text-zinc-500 leading-snug mt-0.5">${item.isp}</div>
          </div>
        </div>
      </td>
      <td class="py-4 px-4 text-zinc-800 leading-snug">${item.device}</td>
      <td class="py-4 pl-4 text-zinc-500">${item.referrer}</td>
    `;
    tbody.appendChild(tr);
  });
  lucide.createIcons();
}

// --- 4. SIMULATE NEW VISIT ---
let mobileCount = 9;
let desktopCount = 15;

function simulateNewVisit() {
  days30Data[29].views += 1;
  hourlyViews[7] += 1;
  desktopCount += 1;

  const samplePages = [
    'Trang chủ',
    '/san-pham?danh-muc=ao-khoac-thu-dong&trang=1',
    '/san-pham/ao-so-mi-lua-toi-gian',
    '/san-pham/quan-tay-ong-suong'
  ];
  const randomPage = samplePages[Math.floor(Math.random() * samplePages.length)];

  const now = new Date();
  const timeStr = now.toTimeString().split(' ')[0] + ' 23/10/2026';

  visitLogs.unshift({
    time: timeStr,
    page: randomPage,
    ip: '123.31.18.' + Math.floor(100 + Math.random() * 150),
    location: 'Cầu Giấy, Hanoi, Việt Nam',
    isp: 'Vietnam Posts and Telecommunications Group',
    device: 'Edge · Windows · Máy tính',
    referrer: ''
  });

  render30DaysChart();
  renderHourlyChart();
  renderVisitLogs();

  const total = mobileCount + desktopCount;
  document.getElementById('countDesktop').textContent = desktopCount;
  document.getElementById('barDesktop').style.width = `${(desktopCount / total) * 100}%`;
  document.getElementById('barMobile').style.width = `${(mobileCount / total) * 100}%`;

  showToast('Đã ghi nhận +1 lượt xem mới vào Fashion - Manager');
}

