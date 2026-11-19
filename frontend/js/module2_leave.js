// Module 2: Lịch Tháng & Đăng Ký Nghỉ Phép (Leave Calendar)
let currentCalendarYear = null;
let currentCalendarMonth = null;
let calendarData = null;
let currentAdminLeaveFilter = 'pending';
let cachedAdminRequests = [];

window.loadLeaveModule = async function() {
  if (!currentCalendarYear || !currentCalendarMonth) {
    const today = new Date();
    currentCalendarYear = today.getFullYear();
    currentCalendarMonth = today.getMonth() + 1;
  }

  await fetchCalendarData();
  await loadMyLeaveHistory();
  if (currentUser && ['truong_khoa', 'ktv_truong'].includes(currentUser.role)) {
    await loadAdminLeaveRequests();
  }
};

async function fetchCalendarData() {
  const gridContainer = document.getElementById('leave-calendar-grid');
  const alertContainer = document.getElementById('calendar-month-warnings');
  if (!gridContainer) return;

  gridContainer.innerHTML = '<div class="col-span-7 p-12 text-center text-slate-500"><div class="animate-spin inline-block w-8 h-8 border-4 border-sky-600 border-t-transparent rounded-full mb-3"></div><div>Đang tải lịch tháng...</div></div>';

  try {
    const res = await fetch(`/api/leave/calendar?year=${currentCalendarYear}&month=${currentCalendarMonth}`);
    const data = await res.json();
    if (!res.ok || !data.success) {
      gridContainer.innerHTML = '<div class="col-span-7 p-8 text-center text-red-500">Không thể tải dữ liệu lịch tháng.</div>';
      return;
    }

    calendarData = data;
    renderCalendarGrid(data);
    renderMonthWarnings(data);
    renderLeaveBalances(data.balances, data.my_balance);
  } catch (err) {
    gridContainer.innerHTML = '<div class="col-span-7 p-8 text-center text-red-500">Lỗi kết nối khi tải lịch tháng.</div>';
  }
}

function renderLeaveBalances(balances, myBalance) {
  const container = document.getElementById('leave-balances-container');
  const myRemainText = document.getElementById('my-leave-remaining-text');

  if (myBalance && myRemainText) {
    myRemainText.textContent = `${myBalance.remaining_days} / ${myBalance.total_entitled} ngày`;
  }

  if (!container || !balances || balances.length === 0) return;

  let html = '';
  balances.forEach(b => {
    const isMe = currentUser && currentUser.id === b.user_id;
    const ratio = Math.round((b.used_approved / b.total_entitled) * 100);
    const barColor = b.remaining_days <= 2 ? 'bg-red-500' : (b.remaining_days <= 5 ? 'bg-amber-500' : 'bg-emerald-500');

    html += `
      <div class="p-3.5 rounded-2xl border ${isMe ? 'border-sky-400 bg-sky-50/50 ring-2 ring-sky-200' : 'border-slate-200 bg-slate-50/70'} shadow-xs flex flex-col justify-between transition hover:shadow">
        <div>
          <div class="flex items-center justify-between">
            <span class="text-xs font-extrabold text-slate-900 truncate" title="${b.full_name}">${b.full_name}</span>
            ${isMe ? '<span class="px-1.5 py-0.2 bg-sky-700 text-white rounded text-[9px] font-bold">Bạn</span>' : ''}
          </div>
          <div class="text-[10px] text-slate-500 truncate mt-0.5">${b.title}</div>
        </div>

        <div class="mt-3">
          <div class="flex items-baseline justify-between text-xs">
            <span class="text-slate-500 text-[11px]">Phép năm còn lại:</span>
            <span class="font-black text-sm ${b.remaining_days <= 2 ? 'text-red-600' : 'text-emerald-700'}">
              ${b.remaining_days} <span class="text-[10px] font-normal text-slate-400">/ 12 ngày</span>
            </span>
          </div>

          <!-- Progress Bar -->
          <div class="w-full bg-slate-200 rounded-full h-1.5 mt-1.5 overflow-hidden">
            <div class="${barColor} h-1.5 rounded-full transition-all duration-500" style="width: ${Math.max(0, 100 - ratio)}%"></div>
          </div>

          <div class="flex items-center justify-between text-[10px] text-slate-500 mt-2 pt-1.5 border-t border-slate-200/60">
            <span>Đã nghỉ: <b class="text-slate-700">${b.used_approved} ngày</b></span>
            <span>Chờ duyệt: <b class="text-amber-700">${b.used_pending} ngày</b></span>
          </div>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

function renderCalendarGrid(data) {
  const container = document.getElementById('leave-calendar-grid');
  const monthTitle = document.getElementById('calendar-month-title');
  if (monthTitle) {
    monthTitle.textContent = `Tháng ${data.month} Năm ${data.year}`;
  }

  const firstWeekday = data.first_weekday; // 0 = Mon, 6 = Sun
  const numDays = data.num_days;
  const daysMap = data.days; // Object keyed by 'YYYY-MM-DD'
  const todayStr = formatDateToISO(new Date());

  let html = '';

  // Blank padding cells for days before first day of month
  for (let i = 0; i < firstWeekday; i++) {
    html += `
      <div class="calendar-day-cell bg-slate-50/50 border border-slate-200/60 rounded-xl p-2 opacity-40"></div>
    `;
  }

  // Render day cells
  for (let d = 1; d <= numDays; d++) {
    const dStr = `${data.year}-${String(data.month).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
    const dayInfo = daysMap[dStr] || { date: dStr, day: d, leaves: [], leave_count: 0, has_warning: false };
    const isToday = dStr === todayStr;
    const hasWarning = dayInfo.has_warning;

    let cellBorderClass = 'border-slate-200 hover:border-sky-300';
    let cellBgClass = 'bg-white';

    if (hasWarning) {
      cellBorderClass = 'calendar-day-warning shadow-md';
      cellBgClass = 'bg-red-50/40';
    } else if (isToday) {
      cellBorderClass = 'border-sky-500 ring-2 ring-sky-400';
      cellBgClass = 'bg-sky-50/30';
    }

    html += `
      <div onclick="openLeaveRequestModal('${dStr}')"
           class="calendar-day-cell flex flex-col justify-between p-2 rounded-xl border ${cellBorderClass} ${cellBgClass} cursor-pointer group shadow-sm hover:shadow">
        <!-- Day Number Header -->
        <div class="flex items-center justify-between">
          <span class="text-sm font-bold ${isToday ? 'px-2 py-0.5 bg-sky-700 text-white rounded-full' : 'text-slate-800'}">
            ${d}
          </span>
          ${hasWarning ? `
            <span class="flex items-center gap-1 text-[10px] font-extrabold text-red-700 bg-red-100 border border-red-300 px-1.5 py-0.5 rounded-full animate-pulse" title="${dayInfo.warning_message}">
              <svg class="w-3 h-3 text-red-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>
              <span>${dayInfo.leave_count} nghỉ</span>
            </span>
          ` : ''}
        </div>

        <!-- Leaves List in Day -->
        <div class="mt-1 space-y-1 overflow-y-auto max-h-[85px]">
    `;

    if (dayInfo.leaves && dayInfo.leaves.length > 0) {
      dayInfo.leaves.forEach(l => {
        const isApproved = l.status === 'approved';
        const isPending = l.status === 'pending';
        const isRejected = l.status === 'rejected';

        const statusBadgeColor = isApproved ? 'bg-emerald-100 text-emerald-800 border-emerald-300' : (isPending ? 'bg-amber-100 text-amber-800 border-amber-300' : 'bg-slate-200 text-slate-600 line-through');
        const typeLabels = {
          'phep_nam': 'Phép năm',
          'phep_cuoi': 'Phép cưới (3 ngày)',
          'nghi_bu': 'Nghỉ bù',
          'di_hoc': 'Đi học',
          'viec_rieng': 'Việc riêng',
          'khac': 'Lý do khác'
        };

        html += `
          <div class="p-1 rounded border text-[11px] leading-tight flex items-center justify-between ${statusBadgeColor}" title="${l.full_name}: ${typeLabels[l.leave_type]} - ${l.reason}">
            <div class="truncate font-semibold">
              <span class="inline-block w-1.5 h-1.5 rounded-full ${isApproved ? 'bg-emerald-500' : 'bg-amber-500'} mr-1"></span>
              ${l.full_name}
            </div>
            <span class="text-[9px] font-normal px-1">${typeLabels[l.leave_type] || ''}</span>
          </div>
        `;
      });
    } else {
      html += `
        <div class="text-[11px] text-slate-300 italic group-hover:text-sky-500 transition py-1 text-center">
          + Xin nghỉ
        </div>
      `;
    }

    html += `
        </div>
      </div>
    `;
  }

  container.innerHTML = html;
}

function renderMonthWarnings(data) {
  const alertContainer = document.getElementById('calendar-month-warnings');
  if (!alertContainer) return;

  const warningDays = Object.values(data.days).filter(d => d.has_warning);

  if (warningDays.length === 0) {
    alertContainer.innerHTML = '';
    alertContainer.classList.add('hidden');
    return;
  }

  let html = `
    <div class="staffing-warning-card p-4 rounded-xl border border-red-200 shadow-sm mb-4">
      <div class="flex items-start gap-3">
        <div class="p-2 bg-red-100 text-red-600 rounded-lg mt-0.5">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
        </div>
        <div class="flex-grow">
          <h4 class="text-sm font-extrabold text-red-900 uppercase">CẢNH BÁO NGUY CƠ THIẾU HỤT NHÂN SỰ TRONG THÁNG (${warningDays.length} ngày có từ 2 nhân sự trở lên xin nghỉ)</h4>
          <p class="text-xs text-red-700 mt-1 leading-relaxed">
            Quy định vận hành Khoa Xét nghiệm yêu cầu duy trì tối thiểu 4 nhân sự lấy máu ngoại trú và kíp trực phòng máy. Vui lòng kiểm tra và cân đối các ngày sau:
          </p>
          <div class="mt-2.5 flex flex-wrap gap-2">
  `;

  warningDays.forEach(wd => {
    const names = wd.leaves.map(l => l.full_name).join(', ');
    const parts = wd.date.split('-');
    const formatted = `${parts[2]}/${parts[1]}/${parts[0]}`;
    html += `
      <div class="px-2.5 py-1 bg-white border border-red-300 rounded-lg text-xs shadow-sm flex items-center gap-1.5">
        <span class="font-bold text-red-800">${formatted}</span>:
        <span class="text-slate-700 font-medium">${names}</span>
        <span class="px-1.5 py-0.2 bg-red-100 text-red-700 rounded text-[10px] font-bold">(${wd.leave_count} người)</span>
      </div>
    `;
  });

  html += `
          </div>
        </div>
      </div>
    </div>
  `;

  alertContainer.innerHTML = html;
  alertContainer.classList.remove('hidden');
}

function prevMonth() {
  currentCalendarMonth--;
  if (currentCalendarMonth < 1) {
    currentCalendarMonth = 12;
    currentCalendarYear--;
  }
  fetchCalendarData();
}

function nextMonth() {
  currentCalendarMonth++;
  if (currentCalendarMonth > 12) {
    currentCalendarMonth = 1;
    currentCalendarYear++;
  }
  fetchCalendarData();
}

window.onLeaveTargetUserChange = function() {
  updateModalLeaveQuotaInfo();
};

window.onLeaveTypeChange = function() {
  updateModalLeaveQuotaInfo();
};

window.onLeaveShiftChange = function() {
  updateModalLeaveQuotaInfo();
};

function updateModalLeaveQuotaInfo() {
  if (!calendarData || !calendarData.balances) return;

  const targetSelect = document.getElementById('lr-target-user');
  let selectedUserId = currentUser ? currentUser.id : null;
  if (targetSelect && !targetSelect.closest('.hidden') && targetSelect.value) {
    selectedUserId = parseInt(targetSelect.value);
  }

  const userBal = calendarData.balances.find(b => b.user_id === selectedUserId) || {
    total_entitled: 12.0,
    used_approved: 0.0,
    used_pending: 0.0,
    remaining_days: 12.0
  };

  const usedEl = document.getElementById('lr-used-phep-text');
  const pendingEl = document.getElementById('lr-pending-phep-text');
  const remainBadge = document.getElementById('lr-remaining-phep-badge');
  const warningEl = document.getElementById('lr-quota-warning');
  const typeSelect = document.getElementById('lr-type');
  const shiftSelect = document.getElementById('lr-shift');

  if (usedEl) usedEl.textContent = userBal.used_approved;
  if (pendingEl) pendingEl.textContent = userBal.used_pending;
  if (remainBadge) {
    remainBadge.textContent = `${userBal.remaining_days} / 12 ngày`;
    remainBadge.className = userBal.remaining_days <= 2 ?
      'text-xs font-black px-2.5 py-1 rounded-lg bg-red-600 text-white shadow-xs' :
      'text-xs font-black px-2.5 py-1 rounded-lg bg-emerald-600 text-white shadow-xs';
  }

  // Check if requesting phep_nam with not enough quota
  const isPhepNam = typeSelect && typeSelect.value === 'phep_nam';
  const reqDays = (shiftSelect && shiftSelect.value === 'all') ? 1.0 : 0.5;

  if (warningEl) {
    if (isPhepNam && userBal.remaining_days < reqDays) {
      warningEl.textContent = `⚠️ Cán bộ này chỉ còn ${userBal.remaining_days} ngày phép năm (không đủ cho yêu cầu ${reqDays} ngày). Vui lòng chọn "Nghỉ bù" hoặc "Việc riêng / Không lương".`;
      warningEl.classList.remove('hidden');
    } else {
      warningEl.classList.add('hidden');
    }
  }
}

function openLeaveRequestModal(dateStr) {
  const modal = document.getElementById('modal-leave-request');
  const dateInput = document.getElementById('lr-date');
  const userSelect = document.getElementById('lr-target-user');
  const userSelectGroup = document.getElementById('lr-user-select-group');

  if (dateInput) {
    dateInput.value = dateStr || formatDateToISO(new Date());
  }

  // If Admin, show dropdown to submit on behalf of someone
  const isAdmin = currentUser && ['truong_khoa', 'ktv_truong'].includes(currentUser.role);
  if (userSelectGroup && userSelect) {
    const staffList = (calendarData && calendarData.balances && calendarData.balances.length > 0)
      ? calendarData.balances
      : ((typeof scheduleStaffList !== 'undefined' && scheduleStaffList.length > 0) ? scheduleStaffList : []);

    if (isAdmin && staffList.length > 0) {
      userSelectGroup.classList.remove('hidden');
      userSelect.innerHTML = staffList.map(u => `
        <option value="${u.id || u.user_id}" ${(u.id || u.user_id) === currentUser.id ? 'selected' : ''}>${u.full_name} (${u.title})</option>
      `).join('');
    } else {
      userSelectGroup.classList.add('hidden');
    }
  }

  document.getElementById('lr-reason').value = '';
  document.getElementById('lr-error').classList.add('hidden');

  updateModalLeaveQuotaInfo();
  openModal('modal-leave-request');
}

async function submitLeaveRequest() {
  const date = document.getElementById('lr-date').value;
  const leave_type = document.getElementById('lr-type').value;
  const shift = document.getElementById('lr-shift').value;
  const reason = document.getElementById('lr-reason').value.trim();
  const targetUserEl = document.getElementById('lr-target-user');
  const target_user_id = targetUserEl ? targetUserEl.value : null;

  const errEl = document.getElementById('lr-error');

  if (!reason) {
    errEl.textContent = 'Vui lòng nhập lý do xin nghỉ phép.';
    errEl.classList.remove('hidden');
    return;
  }

  try {
    let url = '/api/leave/request';
    if (target_user_id) {
      url += `?target_user_id=${target_user_id}`;
    }

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        leave_date: date,
        leave_type: leave_type,
        shift: shift,
        reason: reason
      })
    });

    const data = await res.json();
    if (res.ok && data.success) {
      closeModal('modal-leave-request');
      showToast(data.message, data.has_staff_warning ? 'warning' : 'success');
      fetchCalendarData();
      loadMyLeaveHistory();
      if (currentUser && ['truong_khoa', 'ktv_truong'].includes(currentUser.role)) {
        loadAdminLeaveRequests();
      }
      loadKPIStats();
    } else {
      errEl.textContent = data.detail || 'Không thể tạo đơn nghỉ phép.';
      errEl.classList.remove('hidden');
    }
  } catch (err) {
    errEl.textContent = 'Lỗi kết nối khi gửi đơn.';
    errEl.classList.remove('hidden');
  }
}

async function loadMyLeaveHistory() {
  const container = document.getElementById('my-leave-history-table');
  if (!container) return;

  try {
    const res = await fetch('/api/leave/my-history');
    const data = await res.json();
    if (!res.ok || !data.success) return;

    const leaves = data.leaves || [];
    if (leaves.length === 0) {
      container.innerHTML = '<div class="p-6 text-center text-slate-400 text-xs italic">Bạn chưa có đơn đăng ký nghỉ nào.</div>';
      return;
    }

    const typeLabels = {
      'phep_nam': 'Nghỉ phép năm',
      'nghi_bu': 'Nghỉ bù',
      'di_hoc': 'Đi học / Tập huấn',
      'viec_rieng': 'Việc riêng'
    };

    let html = `
      <div class="overflow-x-auto">
        <table class="w-full text-xs text-left">
          <thead class="bg-slate-100 text-slate-700 font-bold">
            <tr>
              <th class="p-2.5">Ngày Nghỉ</th>
              <th class="p-2.5">Loại Nghỉ</th>
              <th class="p-2.5">Buổi</th>
              <th class="p-2.5">Lý Do</th>
              <th class="p-2.5">Trạng Thái</th>
              <th class="p-2.5 text-right">Thao Tác</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
    `;

    leaves.forEach(l => {
      const parts = l.leave_date.split('-');
      const dVN = `${parts[2]}/${parts[1]}/${parts[0]}`;
      const shiftStr = l.shift === 'all' ? 'Cả ngày (07h-11h & 13h-17h)' : (l.shift === 'sang' ? 'Sáng (07h-11h)' : 'Chiều (13h-17h)');

      let statusBadge = '';
      if (l.status === 'approved') {
        statusBadge = '<span class="px-2 py-0.5 rounded-full font-bold text-[10px] bg-emerald-100 text-emerald-800">Đã duyệt</span>';
      } else if (l.status === 'rejected') {
        statusBadge = '<span class="px-2 py-0.5 rounded-full font-bold text-[10px] bg-red-100 text-red-800">Từ chối</span>';
      } else {
        statusBadge = '<span class="px-2 py-0.5 rounded-full font-bold text-[10px] bg-amber-100 text-amber-800">Chờ duyệt</span>';
      }

      html += `
        <tr class="hover:bg-slate-50 transition">
          <td class="p-2.5 font-bold text-slate-900">${dVN}</td>
          <td class="p-2.5">${typeLabels[l.leave_type] || l.leave_type}</td>
          <td class="p-2.5">${shiftStr}</td>
          <td class="p-2.5 text-slate-600 max-w-[200px] truncate" title="${l.reason}">${l.reason}</td>
          <td class="p-2.5">${statusBadge}</td>
          <td class="p-2.5 text-right flex items-center justify-end gap-1.5">
            <button onclick="printOfficialLeaveApplication(${l.id})"
                    class="px-2 py-1 text-[11px] font-bold text-sky-700 bg-sky-50 hover:bg-sky-100 border border-sky-200 rounded transition flex items-center gap-1 shadow-sm" title="In đơn xin nghỉ phép chuẩn mẫu bệnh viện">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/></svg>
              <span>In Đơn</span>
            </button>
      `;

      if (l.status === 'pending') {
        html += `
          <button onclick="cancelMyLeave(${l.id})" class="px-2 py-1 text-[11px] font-semibold text-red-600 hover:text-red-800 hover:bg-red-50 rounded transition">
            Hủy đơn
          </button>
        `;
      }

      html += `</td></tr>`;
    });

    html += `
          </tbody>
        </table>
      </div>
    `;

    container.innerHTML = html;
  } catch (err) {
    console.error('Error loading leave history', err);
  }
}

async function cancelMyLeave(id) {
  if (!confirm('Bạn có chắc chắn muốn hủy đơn xin nghỉ này?')) return;
  try {
    const res = await fetch(`/api/leave/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast('Đã hủy đơn nghỉ phép.', 'info');
      fetchCalendarData();
      loadMyLeaveHistory();
      loadKPIStats();
    } else {
      showToast(data.detail || 'Không thể hủy đơn.', 'error');
    }
  } catch (e) {
    showToast('Lỗi kết nối khi hủy đơn.', 'error');
  }
}

// ================= ADMIN LEAVE APPROVAL MANAGEMENT =================
window.setAdminLeaveFilter = function(filter) {
  currentAdminLeaveFilter = filter;
  ['pending', 'all', 'approved', 'rejected'].forEach(f => {
    const btn = document.getElementById(`admin-filter-${f}`);
    if (btn) {
      if (f === filter) {
        btn.className = 'px-3 py-1.5 rounded-lg bg-white text-slate-900 shadow-xs transition';
      } else {
        btn.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition';
      }
    }
  });
  renderAdminLeaveRequests(cachedAdminRequests);
};

window.loadAdminLeaveRequests = async function() {
  const container = document.getElementById('admin-leave-requests-table');
  const badge = document.getElementById('admin-pending-count-badge');
  if (!container) return;

  try {
    const res = await fetch('/api/leave/all-requests');
    const data = await res.json();
    if (!res.ok || !data.success) {
      container.innerHTML = '<div class="p-6 text-center text-red-500 text-xs">Không thể tải danh sách đơn duyệt.</div>';
      return;
    }

    cachedAdminRequests = data.requests || [];
    const pendingCount = cachedAdminRequests.filter(r => r.status === 'pending').length;
    if (badge) {
      badge.textContent = `${pendingCount} đơn chờ`;
      badge.className = pendingCount > 0
        ? 'px-2 py-0.5 rounded-full text-xs font-black bg-amber-500 text-white animate-pulse'
        : 'px-2 py-0.5 rounded-full text-xs font-bold bg-slate-100 text-slate-600 border border-slate-200';
    }

    renderAdminLeaveRequests(cachedAdminRequests);
  } catch (e) {
    console.error('Error fetching admin leave requests', e);
  }
};

function renderAdminLeaveRequests(requests) {
  const container = document.getElementById('admin-leave-requests-table');
  if (!container) return;

  let filtered = requests;
  if (currentAdminLeaveFilter !== 'all') {
    filtered = requests.filter(r => r.status === currentAdminLeaveFilter);
  }

  if (filtered.length === 0) {
    const filterName = currentAdminLeaveFilter === 'pending' ? 'Chờ duyệt' : (currentAdminLeaveFilter === 'approved' ? 'Đã duyệt' : (currentAdminLeaveFilter === 'rejected' ? 'Từ chối' : 'Tất cả'));
    container.innerHTML = `
      <div class="p-8 text-center bg-slate-50 rounded-xl border border-dashed border-slate-200 text-slate-400 text-xs">
        <svg class="w-8 h-8 mx-auto mb-2 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
        Không có đơn xin nghỉ nào trong danh mục <b>"${filterName}"</b>.
      </div>
    `;
    return;
  }

  const typeLabels = {
    'phep_nam': 'Nghỉ phép năm',
    'nghi_bu': 'Nghỉ bù',
    'di_hoc': 'Đi học / Tập huấn',
    'viec_rieng': 'Việc riêng (không lương)',
    'phep_cuoi': 'Phép cưới'
  };

  let html = `
    <div class="overflow-x-auto">
      <table class="w-full text-xs text-left">
        <thead class="bg-amber-50/70 text-slate-800 font-extrabold border-b border-amber-200/60 uppercase text-[11px]">
          <tr>
            <th class="p-3">Mã & Cán Bộ</th>
            <th class="p-3">Ngày Nghỉ & Ca</th>
            <th class="p-3">Loại Nghỉ</th>
            <th class="p-3">Số Phép Năm Còn Lại</th>
            <th class="p-3">Lý Do Xin Nghỉ</th>
            <th class="p-3">Trạng Thái</th>
            <th class="p-3 text-right">Phê Duyệt / Thao Tác</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
  `;

  filtered.forEach(r => {
    const parts = r.leave_date.split('-');
    const dVN = `${parts[2]}/${parts[1]}/${parts[0]}`;
    const shiftStr = r.shift === 'all' ? 'Cả ngày (07h-11h & 13h-17h)' : (r.shift === 'sang' ? 'Sáng (07h-11h)' : 'Chiều (13h-17h)');
    const isPhepNam = r.leave_type === 'phep_nam';
    const dayDed = r.day_deduction || (r.shift === 'all' ? 1.0 : 0.5);

    let statusBadge = '';
    if (r.status === 'approved') {
      statusBadge = `<span class="px-2.5 py-1 rounded-full font-extrabold text-[10px] bg-emerald-100 text-emerald-800 border border-emerald-200">✅ ĐÃ DUYỆT</span>`;
    } else if (r.status === 'rejected') {
      statusBadge = `<span class="px-2.5 py-1 rounded-full font-extrabold text-[10px] bg-red-100 text-red-800 border border-red-200">❌ TỪ CHỐI</span>`;
    } else {
      statusBadge = `<span class="px-2.5 py-1 rounded-full font-black text-[10px] bg-amber-400 text-amber-950 border border-amber-500 animate-pulse">⏳ CHỜ DUYỆT</span>`;
    }

    let quotaHtml = '';
    if (isPhepNam) {
      const rem = r.remaining_days;
      const afterApprove = Math.max(0, Math.round((rem - dayDed) * 10) / 10);
      const remColor = rem <= 2 ? 'text-red-600 font-black' : (rem <= 5 ? 'text-amber-600 font-bold' : 'text-emerald-700 font-black');

      quotaHtml = `
        <div class="space-y-0.5">
          <div class="text-[11px]"><span class="text-slate-500">Hiện còn:</span> <span class="${remColor}">${rem} / 12 ngày</span></div>
          ${r.status === 'pending' ? `<div class="text-[10px] text-sky-700 font-medium bg-sky-50 px-1.5 py-0.5 rounded border border-sky-100">Duyệt sẽ trừ: <b>-${dayDed} ngày</b> (còn ${afterApprove} ngày)</div>` : ''}
          ${r.status === 'approved' ? `<div class="text-[10px] text-emerald-700">Đã trừ -${dayDed} ngày vào quỹ phép</div>` : ''}
        </div>
      `;
    } else {
      quotaHtml = `
        <div class="text-slate-500 text-[11px]">
          <span>Không trừ phép năm</span>
          <div class="text-[10px] text-slate-400">(${typeLabels[r.leave_type] || r.leave_type})</div>
        </div>
      `;
    }

    html += `
      <tr class="hover:bg-amber-50/30 transition">
        <td class="p-3">
          <div class="font-extrabold text-slate-900 text-xs">${r.full_name}</div>
          <div class="text-[10px] text-slate-500">${r.user_title || ''} • #${r.id}</div>
        </td>
        <td class="p-3">
          <div class="font-black text-slate-800 text-xs">${dVN}</div>
          <div class="text-[10px] text-sky-800 font-medium">${shiftStr}</div>
        </td>
        <td class="p-3">
          <span class="px-2 py-0.5 rounded font-bold text-[10px] ${isPhepNam ? 'bg-sky-100 text-sky-800 border border-sky-200' : 'bg-slate-100 text-slate-700'}">
            ${typeLabels[r.leave_type] || r.leave_type}
          </span>
        </td>
        <td class="p-3">${quotaHtml}</td>
        <td class="p-3">
          <div class="text-slate-700 max-w-[220px] truncate" title="${r.reason}">${r.reason}</div>
          ${r.review_note ? `<div class="text-[10px] text-slate-500 italic mt-0.5">Ghi chú: ${r.review_note}</div>` : ''}
          ${r.reviewer_name ? `<div class="text-[10px] text-emerald-700 font-semibold mt-0.5">Người duyệt: ${r.reviewer_name}</div>` : ''}
        </td>
        <td class="p-3">${statusBadge}</td>
        <td class="p-3 text-right">
          <div class="flex items-center justify-end gap-1.5">
            ${r.status === 'pending' ? `
              <button onclick="reviewLeave(${r.id}, 'approved')"
                      class="px-2.5 py-1.5 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg shadow-sm transition flex items-center gap-1"
                      title="Phê duyệt đơn và tự động trừ phép năm nếu là phép năm">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                <span>Duyệt Trừ Phép</span>
              </button>
              <button onclick="reviewLeave(${r.id}, 'rejected')"
                      class="px-2 py-1.5 text-xs font-bold text-red-700 bg-red-50 hover:bg-red-100 border border-red-200 rounded-lg transition"
                      title="Từ chối đơn xin nghỉ">
                <span>Từ Chối</span>
              </button>
            ` : `
              <button onclick="reviewLeave(${r.id}, '${r.status === 'approved' ? 'rejected' : 'approved'}')"
                      class="px-2 py-1 text-[11px] font-medium text-slate-600 hover:bg-slate-100 border border-slate-200 rounded transition"
                      title="Đổi lại trạng thái duyệt">
                ${r.status === 'approved' ? 'Thu hồi duyệt' : 'Duyệt lại'}
              </button>
            `}
            <button onclick="printOfficialLeaveApplication(${r.id})"
                    class="p-1.5 text-sky-700 bg-sky-50 hover:bg-sky-100 border border-sky-200 rounded-lg transition"
                    title="In đơn A4">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/></svg>
            </button>
          </div>
        </td>
      </tr>
    `;
  });

  html += `
        </tbody>
      </table>
    </div>
  `;

  container.innerHTML = html;
}

// For Admin: inline approve / reject
async function reviewLeave(leaveId, status) {
  const isApprove = status === 'approved';
  const confirmMsg = isApprove ?
    'Bạn có chắc chắn muốn PHÊ DUYỆT đơn xin nghỉ này?\n(Nếu là phép năm, hệ thống sẽ tự động trừ vào định mức 12 ngày phép của nhân viên)' :
    'Bạn có chắc chắn muốn TỪ CHỐI đơn xin nghỉ này?';

  if (!confirm(confirmMsg)) return;

  const note = prompt(isApprove ? 'Ghi chú duyệt (không bắt buộc):' : 'Lý do từ chối (không bắt buộc):') || '';
  try {
    const res = await fetch(`/api/leave/${leaveId}/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, review_note: note })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(data.message, isApprove ? 'success' : 'info');
      await fetchCalendarData();
      await loadAdminLeaveRequests();
      await loadMyLeaveHistory();
      if (typeof loadKPIStats === 'function') loadKPIStats();
    } else {
      showToast(data.detail || 'Lỗi khi cập nhật trạng thái.', 'error');
    }
  } catch (err) {
    showToast('Lỗi kết nối máy chủ.', 'error');
  }
}

async function printOfficialLeaveApplication(leaveId) {
  try {
    const res = await fetch(`/api/leave/${leaveId}/print-data`);
    const data = await res.json();
    if (!res.ok || !data.success) {
      showToast(data.detail || 'Không thể lấy dữ liệu đơn.', 'error');
      return;
    }
    renderLeavePrintTemplate(data.print_data);
    openModal('modal-print-leave');
  } catch (err) {
    showToast('Lỗi khi tải thông tin đơn.', 'error');
  }
}

window.currentLeavePrintOriginalData = null;

window.revertOriginalLeavePrint = function() {
  if (window.currentLeavePrintOriginalData) {
    renderLeavePrintTemplate(window.currentLeavePrintOriginalData, false);
    showToast('Đã khôi phục nội dung đơn về nguyên bản.', 'info');
  }
};

function printBlankOfficialLeaveApplication() {
  const today = new Date();
  const blankData = {
    full_name: currentUser ? currentUser.full_name : '..........................................................',
    phone: '0911761707',
    department: 'Khoa Xét Nghiệm',
    leave_type: 'phep_nam',
    duration_text: '01 ngày, ngày ..... / ..... / 2026 (Từ 07h00 - 11h00 và 13h00 - 17h00)',
    reason: '..................................................................................................................',
    today_day: String(today.getDate()).padStart(2, '0'),
    today_month: String(today.getMonth() + 1).padStart(2, '0'),
    today_year: String(today.getFullYear()),
    manager_name: 'CN. Lê Đình Tú'
  };
  renderLeavePrintTemplate(blankData);
  openModal('modal-print-leave');
}

function renderLeavePrintTemplate(p, saveOriginal = true) {
  if (saveOriginal) {
    window.currentLeavePrintOriginalData = JSON.parse(JSON.stringify(p));
  }
  const isKhongLuong = p.leave_type === 'viec_rieng';
  const isPhepNam = p.leave_type === 'phep_nam';
  const isPhepCuoi = p.leave_type === 'phep_cuoi';
  const isKhac = ['nghi_bu', 'di_hoc'].includes(p.leave_type) || (!isKhongLuong && !isPhepNam && !isPhepCuoi);

  let khacNote = '';
  if (p.leave_type === 'nghi_bu') khacNote = 'Nghỉ bù trực ca';
  else if (p.leave_type === 'di_hoc') khacNote = 'Đi học / Tập huấn nghiệp vụ';

  const container = document.getElementById('print-leave-container');
  if (!container) return;

  container.innerHTML = `
    <div class="official-leave-paper text-slate-900" style="font-family: 'Times New Roman', Times, serif; font-size: 13pt; line-height: 1.45;">
      <!-- Header Two Columns with Hospital Logo -->
      <table style="width: 100%; border: none; margin-bottom: 15px;">
        <tr style="border: none;">
          <td style="width: 14%; text-align: center; vertical-align: middle; border: none; padding: 0;">
            <img src="/static/img/logo_thien_an.png" style="width: 65px; height: 65px; object-fit: contain;" alt="Logo BV Thiên Ân">
          </td>
          <td style="width: 42%; text-align: left; vertical-align: middle; border: none; padding-left: 8px;">
            <div style="font-size: 10pt; font-weight: bold; text-transform: uppercase;">SỞ Y TẾ TỈNH VĨNH LONG</div>
            <div style="font-size: 11pt; font-weight: bold; text-transform: uppercase; color: #0369a1;">BỆNH VIỆN ĐA KHOA THIÊN ÂN</div>
            <div style="font-size: 10pt; font-weight: bold; text-transform: uppercase; color: #0f766e;">KHOA XÉT NGHIỆM</div>
            <div style="font-size: 8.5pt; font-style: italic; margin-top: 1px;">Mã biểu mẫu: BM.NS.02 / QĐ 2429</div>
          </td>
          <td style="width: 44%; text-align: center; vertical-align: middle; border: none; padding: 0;">
            <div style="font-size: 11pt; font-weight: bold;">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
            <div style="font-size: 11pt; font-weight: bold;">Độc lập – Tự do – Hạnh phúc</div>
            <div style="width: 120px; height: 1.5px; background: #000; margin: 3px auto 4px auto;"></div>
            <div style="font-size: 10pt; font-style: italic;">Vĩnh Long, ngày ${p.today_day} tháng ${p.today_month} năm ${p.today_year}</div>
          </td>
        </tr>
      </table>

      <!-- Document Title -->
      <div style="text-align: center; margin: 15px 0 15px 0;">
        <h2 style="font-size: 16pt; font-weight: bold; margin: 0; text-transform: uppercase; letter-spacing: 0.5px;">ĐƠN XIN NGHỈ PHÉP</h2>
      </div>

      <!-- Kính gửi -->
      <table style="width: 100%; border: none; margin-bottom: 12px;">
        <tr style="border: none;">
          <td style="width: 18%; vertical-align: top; font-weight: bold; border: none; padding: 0;">Kính gửi:</td>
          <td style="width: 82%; border: none; padding: 0; line-height: 1.5;">
            <div>- Ban Giám đốc Bệnh viện đa khoa Thiên Ân;</div>
            <div>- Phòng Tổ chức – Hành chính;</div>
            <div>- Trưởng Khoa/Phòng: Khoa Xét Nghiệm</div>
          </td>
        </tr>
      </table>

      <!-- Employee Info -->
      <div style="margin-bottom: 6px;">
        Tôi tên: <b>${p.full_name}</b>
      </div>
      <div style="margin-bottom: 6px;">
        Bộ phận: <b>Khoa Xét Nghiệm</b>
      </div>

      <div style="margin-bottom: 8px;">
        Nay tôi làm đơn này, kính xin Ban Giám đốc, Phòng Tổ chức – Hành chính, Trưởng Khoa Xét Nghiệm cho tôi được nghỉ:
      </div>

      <!-- Checkboxes -->
      <div style="padding-left: 20px; margin-bottom: 10px; line-height: 1.7;">
        <div>${isKhongLuong ? '☒' : '☐'} Không lương</div>
        <div>${isPhepNam ? '☒' : '☐'} Phép năm</div>
        <div>${isPhepCuoi ? '☒' : '☐'} Phép cưới (kết hôn - 3 ngày theo Luật Lao động)</div>
        <div>${isKhac ? '☒' : '☐'} Khác: <u class="editable-field" contenteditable="true" title="Bấm vào để gõ sửa lý do khác">${khacNote || '.........................................................'}</u> <span style="font-size: 11pt; font-style: italic;">(nghỉ bù, đi học, con ốm, thai sản...)</span></div>
      </div>

      <div style="margin-bottom: 6px;">
        Thời gian: <b>${p.duration_text}</b>
      </div>
      <div style="margin-bottom: 6px;">
        Lý do: <b>${p.reason}</b>
      </div>
      <div style="margin-bottom: 10px;">
        Số điện thoại liên hệ khi cần thiết: <b>0911761707</b>
      </div>

      <!-- Commitments -->
      <div style="text-align: justify; margin-bottom: 8px; text-indent: 20px;">
        Tôi cam kết đã sắp xếp các công việc được giao và đã bàn giao cho nhân viên còn lại để không ảnh hưởng đến hoạt động chung của Bệnh viện. Nếu có vấn đề xảy ra liên quan đến tôi làm ảnh hưởng đến hoạt động chung của Bệnh viện, tôi xin chịu trách nhiệm với Bệnh viện.
      </div>
      <div style="text-align: justify; margin-bottom: 8px; text-indent: 20px;">
        Kính mong Ban Giám đốc, Phòng Tổ chức – Hành chính và Trưởng Khoa/Phòng xem xét và chấp thuận.
      </div>
      <div style="margin-bottom: 25px; font-style: italic;">
        Tôi xin chân thành cảm ơn!
      </div>

      <!-- Signatures Row 1 -->
      <table style="width: 100%; border: none; margin-bottom: 40px;">
        <tr style="border: none;">
          <td style="width: 50%; text-align: center; vertical-align: top; border: none;">
            <div id="print-signer-title" style="font-weight: bold;" class="editable-field" contenteditable="true" title="Bấm vào để sửa chức danh">Trưởng bộ phận/Khoa, phòng</div>
            <div style="font-size: 10pt; font-style: italic; margin-bottom: 45px;">(Ký và ghi rõ họ tên)</div>
            <div id="print-signer-name" style="font-weight: bold;" class="editable-field" contenteditable="true" title="Bấm vào để sửa họ tên người ký duyệt">${p.manager_name || 'CN. Lê Đình Tú'}</div>
            <div id="print-signer-phone" style="font-size: 10pt; color: #475569; margin-top: 3px;" class="editable-field" contenteditable="true" title="Bấm vào để sửa SĐT">(ĐT: ${p.manager_phone || '0911761707'})</div>
          </td>
          <td style="width: 50%; text-align: center; vertical-align: top; border: none;">
            <div style="font-weight: bold;">Người làm đơn</div>
            <div style="font-size: 10pt; font-style: italic; margin-bottom: 45px;">(Ký và ghi rõ họ tên)</div>
            <div style="font-weight: bold;" class="editable-field" contenteditable="true" title="Bấm vào để sửa họ tên người làm đơn">${p.full_name}</div>
          </td>
        </tr>
      </table>
          </td>
        </tr>
      </table>

      <!-- Signatures Row 2 -->
      <table style="width: 100%; border: none;">
        <tr style="border: none;">
          <td style="width: 50%; text-align: center; vertical-align: top; border: none;">
            <div style="margin-bottom: 4px; color: #888;">............................................................</div>
            <div style="font-weight: bold;">Duyệt của Ban Giám đốc</div>
          </td>
          <td style="width: 50%; text-align: center; vertical-align: top; border: none;">
            <div style="margin-bottom: 4px; color: #888;">............................................................</div>
            <div style="font-weight: bold;">Trưởng phòng Tổ chức – Hành chính</div>
          </td>
        </tr>
      </table>
    </div>
  `;
}

function executePrintLeave() {
  window.print();
}
