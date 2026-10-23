// ── Tab Switching ─────────────────────────────────────────────────
function switchTab(tabId) {
  const tabs = ['analytics', 'products', 'categories', 'settings'];
  tabs.forEach(t => {
    const el = document.getElementById('tab-' + t);
    if (el) el.classList.add('hidden');
  });
  document.getElementById('tab-' + tabId).classList.remove('hidden');

  // Update active button state in sidebar
  document.querySelectorAll('.nav-btn').forEach(btn => {
    if (btn.dataset.tab === tabId) {
      btn.className = 'nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13.5px] font-medium bg-zinc-200/80 text-zinc-900 transition-colors';
    } else {
      btn.className = 'nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13.5px] font-medium text-zinc-600 hover:bg-zinc-200/50 hover:text-zinc-900 transition-colors';
    }
  });

  // Close mobile menu if open
  const sidebar = document.getElementById('sidebar');
  if (!sidebar.classList.contains('-translate-x-full') && window.innerWidth < 768) {
    toggleMobileMenu();
  }

  // Reload data when switching to relevant tabs
  if (tabId === 'products') loadProducts();
  if (tabId === 'categories') loadCategories();
  if (tabId === 'settings') loadStores();
  if (tabId === 'analytics') loadAnalyticsSummary();
}

// ── Mobile Menu ───────────────────────────────────────────────────
function toggleMobileMenu() {
  const sidebar = document.getElementById('sidebar');
  const backdrop = document.getElementById('mobileBackdrop');
  sidebar.classList.toggle('-translate-x-full');
  backdrop.classList.toggle('hidden');
}

// ── Toast ─────────────────────────────────────────────────────────
let toastTimeout;
function showToast(message) {
  const toast = document.getElementById('toast');
  const toastText = document.getElementById('toastText');
  toastText.textContent = message;
  toast.classList.remove('opacity-0', 'translate-y-2', 'pointer-events-none');
  clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-2', 'pointer-events-none');
  }, 2600);
}

// ── Init ──────────────────────────────────────────────────────────
window.onload = function () {
  if (window.lucide) lucide.createIcons();

  document.getElementById('mobileMenuBtn').addEventListener('click', toggleMobileMenu);

  return triggerSync(false);
};
