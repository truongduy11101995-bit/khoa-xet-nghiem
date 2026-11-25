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
  await loadShiftHandovers();
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

  const approvedLeaves = data.approved_leaves || [];

  weekDates.forEach((dStr, idx) => {
    const parts = dStr.split('-');
    const shortDate = `${parts[2]}/${parts[1]}`;
    // Check if this date is today
    const isToday = dStr === formatDateToISO(new Date());
    const todayBadge = isToday ? '<span class="ml-1 px-1.5 py-0.5 bg-amber-400 text-amber-950 rounded text-[10px] font-extrabold uppercase">Hôm nay</span>' : '';
    const dayLeaves = approvedLeaves.filter(l => l.leave_date === dStr);
    const leaveNames = Array.from(new Set(dayLeaves.map(l => l.full_name.replace('CN. ', ''))));
    const leaveHeaderHtml = leaveNames.length > 0
      ? `<div class="mt-1 px-1.5 py-0.5 rounded bg-rose-500/90 text-white text-[10px] font-bold truncate" title="Nhân sự nghỉ phép: ${leaveNames.join(', ')}">🏖️ Nghỉ: ${leaveNames.join(', ')}</div>`
      : '';

    html += `
      <th class="p-2.5 border border-sky-700 min-w-[140px] ${isToday ? 'bg-sky-900 ring-2 ring-amber-400' : ''}">
        <div class="text-xs uppercase font-extrabold">${dayLabels[idx]} ${todayBadge}</div>
        <div class="text-[11px] font-normal text-sky-200">${shortDate}</div>
        ${leaveHeaderHtml}
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
          // Check if assigned user is on approved leave on this date & shift
          const isAssignedOnLeave = assignment && approvedLeaves.some(l =>
            l.user_id === assignment.user_id &&
            l.leave_date === dStr &&
            (l.shift === 'all' || l.shift === shift || shift === 'truc')
          );

          // Admin can change selection directly
          html += `
            <select onchange="handleScheduleChange('${dStr}', '${shift}', ${pos.id}, this.value)"
                    class="w-full text-xs font-semibold py-1 px-1.5 rounded border ${isAssignedOnLeave ? 'border-red-500 bg-red-50 text-red-900' : 'border-slate-300 bg-white'} focus:ring-1 focus:ring-sky-500 cursor-pointer ${isMyCell ? 'font-bold text-sky-800 bg-sky-50 border-sky-400' : 'text-slate-700'}">
              <option value="0">-- Trống --</option>
          `;
          scheduleStaffList.forEach(u => {
            const selected = (assignment && assignment.user_id === u.id) ? 'selected' : '';
            const userOnLeave = approvedLeaves.some(l =>
              l.user_id === u.id &&
              l.leave_date === dStr &&
              (l.shift === 'all' || l.shift === shift || shift === 'truc')
            );
            const leaveSuffix = userOnLeave ? ' ⚠️ (Đang nghỉ)' : '';
            html += `<option value="${u.id}" ${selected}>${u.full_name}${leaveSuffix}</option>`;
          });
          html += `</select>`;
          if (isAssignedOnLeave) {
            html += `<div class="mt-0.5 text-[10px] font-bold text-red-600 leading-tight">⚠️ Trùng lịch nghỉ!</div>`;
          }
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

// ================= SHIFT HANDOVERS (AI TRỰC RA - AI TRỰC VÀO) =================
window.loadShiftHandovers = async function() {
  const dateInput = document.getElementById('ho-date');
  if (dateInput && !dateInput.value) {
    dateInput.value = formatDateToISO(new Date());
  }

  const outSelect = document.getElementById('ho-outgoing-user');
  const inSelect = document.getElementById('ho-incoming-user');
  if (outSelect && inSelect && scheduleStaffList.length > 0) {
    const optsHtml = scheduleStaffList.map(u => `<option value="${u.id}">${u.full_name}</option>`).join('');
    outSelect.innerHTML = `<option value="">-- Chọn KTV ra trực --</option>` + optsHtml;
    inSelect.innerHTML = `<option value="">-- Chọn KTV vào trực --</option>` + optsHtml;
  }

  try {
    const res = await fetch('/api/schedule/handovers');
    const data = await res.json();
    if (!res.ok || !data.success) return;

    const handovers = data.handovers || [];
    const summaryEl = document.getElementById('handover-today-summary');

    // Auto pre-select suggested outgoing / incoming
    if (outSelect && !outSelect.value && data.suggested_outgoing) {
      outSelect.value = String(data.suggested_outgoing.user_id);
    }
    if (inSelect && !inSelect.value && data.suggested_incoming) {
      inSelect.value = String(data.suggested_incoming.user_id);
    }

    if (summaryEl) {
      const latest = handovers[0];
      if (latest) {
        summaryEl.innerHTML = `Gần nhất (${latest.handover_date}): <span class="text-rose-200 font-bold">Ra: ${latest.outgoing_name}</span> ➔ <span class="text-emerald-200 font-bold">Vào: ${latest.incoming_name}</span>`;
      } else if (data.suggested_outgoing || data.suggested_incoming) {
        const outN = data.suggested_outgoing ? data.suggested_outgoing.full_name : 'Chưa xếp';
        const inN = data.suggested_incoming ? data.suggested_incoming.full_name : 'Chưa xếp';
        summaryEl.innerHTML = `Theo lịch trực: <span class="text-rose-200 font-bold">Ra: ${outN}</span> ➔ <span class="text-emerald-200 font-bold">Vào: ${inN}</span>`;
      } else {
        summaryEl.textContent = 'Chưa có lượt bàn giao trực nào';
      }
    }

    const tbody = document.getElementById('shift-handovers-tbody');
    if (!tbody) return;

    if (handovers.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7" class="p-6 text-center text-slate-400">
            Chưa có dữ liệu bàn giao ca trực. Chọn KTV Ra Trực &amp; KTV Vào Trực ở trên rồi bấm <b>"✓ Lưu Giao Ca"</b>.
          </td>
        </tr>
      `;
      return;
    }

    const isAdmin = currentUser && ['truong_khoa', 'ktv_truong'].includes(currentUser.role);
    const myId = currentUser ? currentUser.id : null;

    tbody.innerHTML = handovers.map((h, idx) => {
      const parts = (h.handover_date || '').split('-');
      const dVN = parts.length === 3 ? `${parts[2]}/${parts[1]}/${parts[0]}` : h.handover_date;
      const canDel = isAdmin || (myId && h.created_by === myId);
      return `
        <tr class="hover:bg-purple-50/30 transition border-b border-slate-100">
          <td class="p-2.5 text-center font-bold text-slate-400">${idx + 1}</td>
          <td class="p-2.5 text-center font-mono font-bold text-slate-800 whitespace-nowrap">${dVN}</td>
          <td class="p-2.5 font-semibold text-purple-900">${h.shift_time}</td>
          <td class="p-2.5">
            <span class="px-2 py-0.5 rounded-lg bg-rose-50 text-rose-800 border border-rose-200 font-bold whitespace-nowrap">⬅️ ${h.outgoing_name}</span>
          </td>
          <td class="p-2.5">
            <span class="px-2 py-0.5 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 font-bold whitespace-nowrap">➡️ ${h.incoming_name}</span>
          </td>
          <td class="p-2.5 text-slate-700">
            <div><b class="text-slate-800">Máy:</b> ${h.equipment_status || 'Bình thường'}</div>
            <div class="text-[11px] text-slate-500"><b>Mẫu tồn:</b> ${h.pending_samples || 'Không'}${h.notes ? ` • <b>Ghi chú:</b> ${h.notes}` : ''}</div>
          </td>
          <td class="p-2.5 text-center">
            ${canDel ? `<button onclick="deleteShiftHandover(${h.id})" class="px-2 py-1 text-red-600 hover:bg-red-50 rounded border border-red-200 text-[11px] font-bold">Xóa</button>` : '--'}
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error('Error loading shift handovers', err);
  }
};

window.submitShiftHandover = async function() {
  const handover_date = document.getElementById('ho-date')?.value;
  const shift_time = document.getElementById('ho-shift-time')?.value;
  const outEl = document.getElementById('ho-outgoing-user');
  const inEl = document.getElementById('ho-incoming-user');
  const equipment_status = document.getElementById('ho-equipment')?.value?.trim();
  const pending_samples = document.getElementById('ho-samples')?.value?.trim();
  const notes = document.getElementById('ho-notes')?.value?.trim();

  const outgoing_user_id = outEl && outEl.value ? parseInt(outEl.value) : null;
  const incoming_user_id = inEl && inEl.value ? parseInt(inEl.value) : null;
  const outgoing_name = outEl && outEl.selectedIndex > 0 ? outEl.options[outEl.selectedIndex].text : '';
  const incoming_name = inEl && inEl.selectedIndex > 0 ? inEl.options[inEl.selectedIndex].text : '';

  if (!outgoing_name || !incoming_name) {
    showToast('Vui lòng chọn đầy đủ KTV Ra Trực và KTV Vào Trực!', 'warning');
    return;
  }

  try {
    const res = await fetch('/api/schedule/handovers', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        handover_date,
        shift_time,
        outgoing_user_id,
        outgoing_name,
        incoming_user_id,
        incoming_name,
        equipment_status,
        pending_samples,
        notes
      })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(data.message, 'success');
      if (document.getElementById('ho-notes')) document.getElementById('ho-notes').value = '';
      await loadShiftHandovers();
    } else {
      showToast(data.detail || 'Không thể lưu bàn giao trực.', 'error');
    }
  } catch (err) {
    showToast('Lỗi kết nối khi lưu bàn giao trực.', 'error');
  }
};

window.deleteShiftHandover = async function(id) {
  if (!confirm('Xóa bản ghi bàn giao ca trực này?')) return;
  try {
    const res = await fetch(`/api/schedule/handovers/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast('Đã xóa bản ghi bàn giao trực.', 'info');
      await loadShiftHandovers();
    } else {
      showToast(data.detail || 'Không thể xóa.', 'error');
    }
  } catch (err) {
    showToast('Lỗi kết nối.', 'error');
  }
};
