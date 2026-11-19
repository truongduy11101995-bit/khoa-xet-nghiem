// Module 1: Bảng Phân Công Vị Trí Làm Việc & Lịch Trực
let currentWeekStartDate = null;
let scheduleStaffList = [];
let schedulePositions = [];
let scheduleData = null;
let currentScheduleView = 'week'; // 'week' or 'day'

window.loadScheduleModule = async function() {
  if (!currentWeekStartDate) {
    const today = new Date();
    // Monday of current week
    const day = today.getDay();
    const diff = today.getDate() - day + (day === 0 ? -6 : 1);
    const monday = new Date(today.setDate(diff));
    currentWeekStartDate = formatDateToISO(monday);
  }

  await loadStaffAndPositions();
  await fetchWeeklySchedule();
};

function formatDateToISO(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

async function loadStaffAndPositions() {
  try {
    const [resUsers, resPos] = await Promise.all([
      fetch('/api/schedule/users'),
      fetch('/api/schedule/positions')
    ]);
    const dataUsers = await resUsers.json();
    const dataPos = await resPos.json();

    scheduleStaffList = dataUsers.users || [];
    schedulePositions = dataPos.positions || [];
  } catch (err) {
    console.error('Error loading positions or staff', err);
  }
}

async function fetchWeeklySchedule() {
  const container = document.getElementById('schedule-table-container');
  if (!container) return;

  container.innerHTML = '<div class="p-12 text-center text-slate-500"><div class="animate-spin inline-block w-8 h-8 border-4 border-sky-600 border-t-transparent rounded-full mb-3"></div><div>Đang tải lịch phân công vị trí...</div></div>';

  try {
    const res = await fetch(`/api/schedule/weekly?start_date=${currentWeekStartDate}`);
    const data = await res.json();
    if (!res.ok || !data.success) {
      container.innerHTML = '<div class="p-8 text-center text-red-500 font-semibold">Không thể tải dữ liệu lịch phân công.</div>';
      return;
    }

    scheduleData = data;
    renderWeeklyScheduleGrid(data);
  } catch (err) {
    container.innerHTML = '<div class="p-8 text-center text-red-500 font-semibold">Lỗi kết nối máy chủ khi tải lịch.</div>';
  }
}

function renderWeeklyScheduleGrid(data) {
  const container = document.getElementById('schedule-table-container');
  const isAdmin = currentUser && ['truong_khoa', 'ktv_truong'].includes(currentUser.role);
  const myId = currentUser ? currentUser.id : null;

  // Format header dates
  const weekDates = data.week_dates; // Array of 7 'YYYY-MM-DD'
  const dayLabels = ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ Nhật'];

  // Update date range banner
  const rangeBanner = document.getElementById('schedule-date-range-text');
  if (rangeBanner) {
    const dStart = new Date(weekDates[0]);
    const dEnd = new Date(weekDates[6]);
    rangeBanner.textContent = `Tuần từ ${dStart.toLocaleDateString('vi-VN')} đến ${dEnd.toLocaleDateString('vi-VN')}`;
  }

  // Categories mapping
  const catNames = {
    'blood': { name: '1. VỊ TRÍ LẤY MÁU NGOẠI TRÚ & NỘI TRÚ (4 BÀN LẤY MÁU)', color: 'bg-rose-50 text-rose-900 border-rose-200' },
    'machine': { name: '2. VẬN HÀNH PHÒNG MÁY XÉT NGHIỆM (HUYẾT HỌC, SINH HÓA, ĐÔNG MÁU...)', color: 'bg-blue-50 text-blue-900 border-blue-200' },
    'warehouse': { name: '3. QUẢN LÝ KHO HÓA CHẤT & VẬT TƯ TIÊU HAO', color: 'bg-amber-50 text-amber-900 border-amber-200' },
    'quality_2429': { name: '4. QUẢN LÝ SỔ SÁCH & HỒ SƠ CHẤT LƯỢNG (QĐ 2429)', color: 'bg-teal-50 text-teal-900 border-teal-200' },
    'direct': { name: '5. THƯỜNG TRỰC CẤP CỨU & TRỰC ĐÊM 24/24', color: 'bg-purple-50 text-purple-900 border-purple-200' }
  };

  let html = `
    <div class="overflow-x-auto rounded-xl border border-slate-200 shadow-sm bg-white">
      <table class="w-full text-xs text-left border-collapse">
        <thead>
          <tr class="bg-sky-800 text-white font-bold text-center">
            <th class="p-3 border border-sky-700 min-w-[200px] text-left">VỊ TRÍ CÔNG TÁC</th>
            <th class="p-3 border border-sky-700 w-16">CA</th>
  `;

  weekDates.forEach((dStr, idx) => {
    const parts = dStr.split('-');
    const shortDate = `${parts[2]}/${parts[1]}`;
    // Check if this date is today
    const isToday = dStr === formatDateToISO(new Date());
    const todayBadge = isToday ? '<span class="ml-1 px-1.5 py-0.5 bg-amber-400 text-amber-950 rounded text-[10px] font-extrabold uppercase">Hôm nay</span>' : '';

    html += `
      <th class="p-2.5 border border-sky-700 min-w-[140px] ${isToday ? 'bg-sky-900 ring-2 ring-amber-400' : ''}">
        <div class="text-xs uppercase font-extrabold">${dayLabels[idx]} ${todayBadge}</div>
        <div class="text-[11px] font-normal text-sky-200">${shortDate}</div>
      </th>
    `;
  });

  html += `
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-200">
  `;

  let currentCategory = null;

  schedulePositions.forEach(pos => {
    // If new category, render section banner
    if (pos.category !== currentCategory) {
      currentCategory = pos.category;
      const catInfo = catNames[currentCategory] || { name: currentCategory.toUpperCase(), color: 'bg-slate-100 text-slate-800 border-slate-200' };
      html += `
        <tr class="${catInfo.color} font-bold text-xs">
          <td colspan="9" class="py-2 px-3 border border-slate-300">
            <div class="flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-full bg-current opacity-70"></span>
              <span>${catInfo.name}</span>
            </div>
          </td>
        </tr>
      `;
    }

    // Determine shifts to show for this position
    const shifts = (pos.category === 'direct') ? ['truc'] : ['sang', 'chieu'];

    shifts.forEach((shift, sIdx) => {
      const shiftName = shift === 'sang' ? 'Sáng' : (shift === 'chieu' ? 'Chiều' : 'Trực 24h');
      const shiftColor = shift === 'sang' ? 'text-sky-700 font-semibold' : (shift === 'chieu' ? 'text-amber-700 font-semibold' : 'text-purple-700 font-bold');

      html += `<tr class="hover:bg-slate-50/70 transition">`;

      if (sIdx === 0) {
        html += `
          <td rowspan="${shifts.length}" class="p-3 border border-slate-200 align-top bg-white font-medium text-slate-800">
            <div class="font-bold text-slate-900">${pos.name}</div>
            <div class="text-[11px] text-slate-500 mt-0.5 leading-snug">${pos.description || ''}</div>
          </td>
        `;
      }

      html += `
        <td class="p-2 border border-slate-200 text-center font-bold bg-slate-50/50 ${shiftColor}">
          ${shiftName}
        </td>
      `;

      // 7 days cells
      weekDates.forEach(dStr => {
        const key = `${pos.id}_${dStr}_${shift}`;
        const assignment = data.schedule_map[key];
        const isMyCell = assignment && assignment.user_id === myId;
        const cellClass = isMyCell ? 'user-highlight-shift' : '';

        html += `
          <td class="p-1.5 border border-slate-200 text-center align-middle ${cellClass}">
        `;

        if (isAdmin) {
          // Admin can change selection directly
          html += `
            <select onchange="handleScheduleChange('${dStr}', '${shift}', ${pos.id}, this.value)"
                    class="w-full text-xs font-semibold py-1 px-1.5 rounded border border-slate-300 focus:ring-1 focus:ring-sky-500 bg-white cursor-pointer ${isMyCell ? 'font-bold text-sky-800 bg-sky-50 border-sky-400' : 'text-slate-700'}">
              <option value="0">-- Trống --</option>
          `;
          scheduleStaffList.forEach(u => {
            const selected = (assignment && assignment.user_id === u.id) ? 'selected' : '';
            html += `<option value="${u.id}" ${selected}>${u.full_name}</option>`;
          });
          html += `</select>`;
        } else {
          // Regular view
          if (assignment) {
            if (isMyCell) {
              html += `
                <div class="py-1 px-1.5 bg-sky-600 text-white rounded font-bold text-xs shadow-sm flex items-center justify-center gap-1">
                  <span>★</span>
                  <span>${assignment.full_name}</span>
                </div>
              `;
            } else {
              html += `
                <div class="py-1 px-1.5 bg-slate-100 text-slate-800 rounded font-medium text-xs truncate" title="${assignment.full_name}">
                  ${assignment.full_name}
                </div>
              `;
            }
          } else {
            html += `<span class="text-slate-300 text-[11px] italic">--</span>`;
          }
        }

        html += `</td>`;
      });

      html += `</tr>`;
    });
  });

  html += `
        </tbody>
      </table>
    </div>
  `;

  container.innerHTML = html;
}

async function handleScheduleChange(work_date, shift, position_id, user_id) {
  try {
    const res = await fetch('/api/schedule/assign', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        work_date,
        shift,
        position_id,
        user_id: parseInt(user_id) || 0
      })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast('Cập nhật phân công thành công!', 'success');
      loadKPIStats();
    } else {
      showToast(data.detail || 'Không thể lưu phân công.', 'error');
    }
  } catch (err) {
    showToast('Lỗi kết nối khi cập nhật lịch.', 'error');
  }
}

function prevWeek() {
  const d = new Date(currentWeekStartDate);
  d.setDate(d.getDate() - 7);
  currentWeekStartDate = formatDateToISO(d);
  fetchWeeklySchedule();
}

function nextWeek() {
  const d = new Date(currentWeekStartDate);
  d.setDate(d.getDate() + 7);
  currentWeekStartDate = formatDateToISO(d);
  fetchWeeklySchedule();
}

function currentWeek() {
  const today = new Date();
  const day = today.getDay();
  const diff = today.getDate() - day + (day === 0 ? -6 : 1);
  const monday = new Date(today.setDate(diff));
  currentWeekStartDate = formatDateToISO(monday);
  fetchWeeklySchedule();
}

function exportScheduleToExcel() {
  window.open(`/api/schedule/export-excel?start_date=${currentWeekStartDate}`, '_blank');
}

function printWeeklySchedule() {
  window.print();
}

async function copyWeekToNext() {
  const curMonday = new Date(currentWeekStartDate);
  const nextMonday = new Date(curMonday);
  nextMonday.setDate(nextMonday.getDate() + 7);
  const nextMondayStr = formatDateToISO(nextMonday);

  if (!confirm(`Bạn có chắc chắn muốn sao chép toàn bộ lịch phân công của tuần này sang tuần sau (bắt đầu từ ${nextMondayStr})?`)) return;

  try {
    const res = await fetch(`/api/schedule/copy-week?from_start_date=${currentWeekStartDate}&to_start_date=${nextMondayStr}`, {
      method: 'POST'
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(data.message, 'success');
      // Jump to next week
      currentWeekStartDate = nextMondayStr;
      fetchWeeklySchedule();
    } else {
      showToast(data.detail || 'Không thể sao chép lịch.', 'error');
    }
  } catch (err) {
    showToast('Lỗi kết nối khi sao chép lịch.', 'error');
  }
}
