// App Core, Authentication, Routing & Common UI Utilities
const BACKEND_API = (window.location.hostname.includes('pages.dev')) 
  ? 'https://khoa-xet-nghiem.onrender.com' 
  : '';

// Global fetch interceptor: Attach Authorization header and route to backend if on pages.dev
const _nativeFetch = window.fetch;
window.fetch = function(url, options = {}) {
  options.headers = options.headers || {};
  const token = localStorage.getItem('token');
  let targetUrl = url;
  if (typeof url === 'string' && url.startsWith('/api')) {
    if (BACKEND_API) {
      targetUrl = BACKEND_API + url;
    }
    if (token) {
      if (options.headers instanceof Headers) {
        if (!options.headers.has('Authorization')) options.headers.set('Authorization', 'Bearer ' + token);
      } else if (Array.isArray(options.headers)) {
        options.headers.push(['Authorization', 'Bearer ' + token]);
      } else {
        if (!options.headers['Authorization']) options.headers['Authorization'] = 'Bearer ' + token;
      }
    }
  }
  return _nativeFetch(targetUrl, options);
};

let currentUser = null;
let currentModule = 'schedule';

async function initApp() {
  // Check auth
  try {
    const res = await fetch('/api/auth/me');
    if (!res.ok) {
      window.location.href = '/login';
      return;
    }
    const data = await res.json();
    currentUser = data.user;
    localStorage.setItem('currentUser', JSON.stringify(currentUser));
  } catch (err) {
    window.location.href = '/login';
    return;
  }

  // Render User Header
  renderUserHeader();

  // Load KPI Stats
  loadKPIStats();

  // Init Modules
  initModuleRouting();

  // Default module
  switchModule('schedule');

  // Clock
  updateClock();
  setInterval(updateClock, 1000);

  // Client-side Keep-Alive ping every 4 minutes to prevent Cloud sleep
  setInterval(() => {
    fetch('/api/health').catch(() => {});
  }, 240000);

  // Global Escape key listener to close any active modal
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (typeof closeDocumentViewer === 'function') closeDocumentViewer();
      if (typeof closeDocPreviewModal === 'function') closeDocPreviewModal();
      document.querySelectorAll('.modal-backdrop:not(.hidden)').forEach(m => {
        m.classList.add('hidden');
      });
      document.body.classList.remove('overflow-hidden');
    }
  });
}

function renderUserHeader() {
  if (!currentUser) return;

  const nameEl = document.getElementById('user-fullname');
  const roleEl = document.getElementById('user-role-badge');
  const titleEl = document.getElementById('user-title');

  if (nameEl) nameEl.textContent = currentUser.full_name;
  if (titleEl) titleEl.textContent = currentUser.title;

  if (roleEl) {
    if (currentUser.role === 'truong_khoa') {
      roleEl.textContent = 'Trưởng Khoa (Admin)';
      roleEl.className = 'px-2.5 py-0.5 text-xs font-bold rounded-full bg-red-100 text-red-800 border border-red-200';
    } else if (currentUser.role === 'ktv_truong') {
      roleEl.textContent = 'KTV Trưởng (Quản lý)';
      roleEl.className = 'px-2.5 py-0.5 text-xs font-bold rounded-full bg-teal-100 text-teal-800 border border-teal-200';
    } else {
      roleEl.textContent = 'Kỹ Thuật Viên';
      roleEl.className = 'px-2.5 py-0.5 text-xs font-semibold rounded-full bg-sky-100 text-sky-800 border border-sky-200';
    }
  }

  // Show or hide admin-specific elements
  const isAdmin = ['truong_khoa', 'ktv_truong'].includes(currentUser.role);
  document.querySelectorAll('.admin-only').forEach(el => {
    if (isAdmin) el.classList.remove('hidden');
    else el.classList.add('hidden');
  });

  const btnIpAdmin = document.getElementById('btn-ip-admin');
  if (btnIpAdmin) {
    if (isAdmin) btnIpAdmin.classList.remove('hidden');
    else btnIpAdmin.classList.add('hidden');
  }
}

async function loadKPIStats() {
  try {
    const res = await fetch('/api/stats/summary');
    if (!res.ok) return;
    const data = await res.json();

    const statStaff = document.getElementById('stat-active-staff');
    const statSched = document.getElementById('stat-today-sched');
    const statLeaves = document.getElementById('stat-today-leaves');
    const statDocs = document.getElementById('stat-total-docs');
    const warningBanner = document.getElementById('global-staffing-alert');

    if (statStaff) statStaff.textContent = `${data.active_staff}/${data.max_staff} cán bộ`;
    if (statSched) statSched.textContent = `${data.today_scheduled} vị trí`;
    if (statLeaves) statLeaves.textContent = `${data.today_leaves} người nghỉ`;
    if (statDocs) statDocs.textContent = `${data.total_docs} biểu mẫu`;

    const statInv = document.getElementById('stat-total-inventory');
    if (statInv && data.total_inventory !== undefined) {
      statInv.textContent = `${data.total_inventory} mục`;
    }

    const storageText = document.getElementById('storage-status-text');
    if (storageText && data.db_type) {
      storageText.textContent = data.db_type;
    }

    // Global alert for today's staffing if >= 2
    if (warningBanner) {
      if (data.has_today_warning) {
        warningBanner.classList.remove('hidden');
      } else {
        warningBanner.classList.add('hidden');
      }
    }

    // Highlight user's today assignments in header notification
    const myPosContainer = document.getElementById('user-today-assignment');
    if (myPosContainer) {
      if (data.my_today_positions && data.my_today_positions.length > 0) {
        // Group by shift: sang, chieu, truc and remove duplicates
        const sang = Array.from(new Set(data.my_today_positions.filter(p => p.shift === 'sang').map(p => p.position_name)));
        const chieu = Array.from(new Set(data.my_today_positions.filter(p => p.shift === 'chieu').map(p => p.position_name)));
        const truc = Array.from(new Set(data.my_today_positions.filter(p => p.shift === 'truc').map(p => p.position_name)));

        let parts = [];
        if (sang.length > 0) {
          parts.push(`<span class="text-amber-200 font-bold">Sáng (07h-11h):</span> ${sang.join(', ')}`);
        }
        if (chieu.length > 0) {
          parts.push(`<span class="text-sky-200 font-bold">Chiều (13h-17h):</span> ${chieu.join(', ')}`);
        }
        if (truc.length > 0) {
          parts.push(`<span class="text-rose-300 font-bold">Trực 24h:</span> ${truc.join(', ')}`);
        }

        const userName = currentUser ? currentUser.full_name : '';
        myPosContainer.innerHTML = `
          <div class="flex items-center gap-2 flex-wrap">
            <span class="text-sky-200 text-xs">Vị trí hôm nay của bạn <b>(${userName})</b>:</span>
            <span class="bg-sky-800/90 text-white px-2.5 py-1 rounded-lg border border-sky-600/50 shadow-xs text-xs font-medium">
              ${parts.join(' <span class="text-white/40 mx-1.5">•</span> ')}
            </span>
          </div>
        `;
      } else {
        const userName = currentUser ? ` (${currentUser.full_name})` : '';
        myPosContainer.innerHTML = `
          <span class="text-sky-200 text-xs">Vị trí hôm nay của bạn${userName}:</span>
          <span class="bg-white/10 text-sky-100 px-2 py-0.5 rounded text-xs italic">Hôm nay không có ca phân công</span>
        `;
      }
    }
  } catch (err) {
    console.error('Failed to load KPI stats', err);
  }
}

function initModuleRouting() {
  const tabs = [
    { id: 'tab-schedule', mod: 'schedule' },
    { id: 'tab-leave', mod: 'leave' },
    { id: 'tab-documents', mod: 'documents' },
    { id: 'tab-inventory', mod: 'inventory' },
    { id: 'tab-profiles', mod: 'profiles' },
    { id: 'tab-environment', mod: 'environment' },
    { id: 'tab-qaqc', mod: 'qaqc' }
  ];

  tabs.forEach(t => {
    const btn = document.getElementById(t.id);
    if (btn) {
      btn.addEventListener('click', () => switchModule(t.mod));
    }
  });
}

function switchModule(modName) {
  // Backward compatibility: if catalog requested, open documents tab on subtab catalog
  if (modName === 'catalog') {
    switchModule('documents');
    if (window.switchDocSubTab) {
      window.switchDocSubTab('catalog');
    }
    return;
  }

  currentModule = modName;

  // Update tabs visual (7 main modules)
  const navButtons = {
    'schedule': document.getElementById('tab-schedule'),
    'leave': document.getElementById('tab-leave'),
    'documents': document.getElementById('tab-documents'),
    'inventory': document.getElementById('tab-inventory'),
    'profiles': document.getElementById('tab-profiles'),
    'environment': document.getElementById('tab-environment'),
    'qaqc': document.getElementById('tab-qaqc')
  };

  const modViews = {
    'schedule': document.getElementById('view-schedule'),
    'leave': document.getElementById('view-leave'),
    'documents': document.getElementById('view-documents'),
    'inventory': document.getElementById('view-inventory'),
    'profiles': document.getElementById('view-profiles'),
    'environment': document.getElementById('view-environment'),
    'qaqc': document.getElementById('view-qaqc')
  };

  Object.keys(navButtons).forEach(key => {
    const btn = navButtons[key];
    const view = modViews[key];
    if (!btn || !view) return;

    if (key === modName) {
      btn.className = "flex items-center gap-2 px-3.5 py-2.5 rounded-xl font-bold text-xs sm:text-sm bg-sky-700 text-white shadow-md whitespace-nowrap";
      view.classList.remove('hidden');
    } else {
      btn.className = "flex items-center gap-2 px-3.5 py-2.5 rounded-xl font-semibold text-xs sm:text-sm text-slate-600 hover:text-sky-700 hover:bg-sky-50 whitespace-nowrap";
      view.classList.add('hidden');
    }
  });

  // Trigger module loaders
  if (modName === 'schedule' && window.loadScheduleModule) {
    window.loadScheduleModule();
  } else if (modName === 'leave' && window.loadLeaveModule) {
    window.loadLeaveModule();
  } else if (modName === 'documents' && window.loadDocumentsModule) {
    window.loadDocumentsModule();
  } else if (modName === 'inventory' && window.loadInventoryModule) {
    window.loadInventoryModule();
  } else if (modName === 'profiles' && window.loadProfilesModule) {
    window.loadProfilesModule();
  } else if (modName === 'environment' && window.loadEnvironmentModule) {
    window.loadEnvironmentModule();
  } else if (modName === 'qaqc') {
    const qaqcFrame = document.getElementById('qaqc-module-frame');
    if (qaqcFrame && qaqcFrame.getAttribute('src') === 'about:blank') {
      qaqcFrame.setAttribute('src', qaqcFrame.getAttribute('data-src') || '/static/qaqc.html');
    }
  }
}

function updateClock() {
  const clockEl = document.getElementById('live-clock');
  if (!clockEl) return;
  const now = new Date();
  const days = ['Chủ Nhật', 'Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy'];
  const dayName = days[now.getDay()];
  const dateStr = `${String(now.getDate()).padStart(2, '0')}/${String(now.getMonth() + 1).padStart(2, '0')}/${now.getFullYear()}`;
  const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
  clockEl.textContent = `${dayName}, ${dateStr} • ${timeStr}`;
}

async function handleLogout() {
  if (!confirm('Bạn có chắc chắn muốn đăng xuất khỏi hệ thống?')) return;
  try {
    await fetch('/api/auth/logout', { method: 'POST' });
  } catch (e) {}
  localStorage.removeItem('currentUser');
  localStorage.removeItem('token');
  window.location.href = '/login';
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  const bgColors = {
    'success': 'bg-emerald-600 text-white',
    'error': 'bg-red-600 text-white',
    'warning': 'bg-amber-500 text-white',
    'info': 'bg-sky-700 text-white'
  };

  toast.className = `flex items-center gap-2 px-4 py-3 rounded-xl shadow-lg text-sm font-medium transition-all transform duration-300 opacity-0 translate-y-2 ${bgColors[type] || bgColors.info}`;
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.remove('opacity-0', 'translate-y-2');
  }, 10);

  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-2');
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Global modal helpers
function openModal(modalId) {
  const m = document.getElementById(modalId);
  if (m) m.classList.remove('hidden');
}

function closeModal(modalId) {
  const m = document.getElementById(modalId);
  if (m) m.classList.add('hidden');
}

// Change Password Modal
function openChangePasswordModal() {
  document.getElementById('cp-old-password').value = '';
  document.getElementById('cp-new-password').value = '';
  document.getElementById('cp-confirm-password').value = '';
  document.getElementById('cp-error').classList.add('hidden');
  openModal('modal-change-password');
}

async function submitChangePassword() {
  const old_password = document.getElementById('cp-old-password').value;
  const new_password = document.getElementById('cp-new-password').value;
  const confirm_password = document.getElementById('cp-confirm-password').value;
  const errEl = document.getElementById('cp-error');

  if (new_password !== confirm_password) {
    errEl.textContent = 'Mật khẩu mới và xác nhận mật khẩu không khớp.';
    errEl.classList.remove('hidden');
    return;
  }

  try {
    const res = await fetch('/api/auth/change-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ old_password, new_password })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      closeModal('modal-change-password');
      showToast('Đổi mật khẩu thành công!', 'success');
    } else {
      errEl.textContent = data.detail || 'Không thể đổi mật khẩu.';
      errEl.classList.remove('hidden');
    }
  } catch (e) {
    errEl.textContent = 'Lỗi kết nối máy chủ.';
    errEl.classList.remove('hidden');
  }
}

document.addEventListener('DOMContentLoaded', initApp);
