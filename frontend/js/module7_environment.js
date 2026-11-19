/**
 * Phân hệ 6: Sổ Theo Dõi Nhiệt Độ - Độ Ẩm Hàng Ngày (Biểu Mẫu BM.MT.01)
 * Khoa Xét Nghiệm - Bệnh Viện Đa Khoa Thiên Ân - Viễn Đông
 * Tiêu chuẩn: Quyết định 2429/QĐ-BYT & Tiêu chuẩn ISO 15189:2022
 * Giám sát 3 vị trí trọng yếu:
 * 1. Phòng máy xét nghiệm: Nhiệt độ 18.0 - 25.0°C | Độ ẩm 40.0 - 75.0%
 * 2. Tủ lạnh bảo quản hóa chất sinh phẩm: 2.0 - 8.0°C
 * 3. Tủ đông lưu mẫu / kiểm tra chất lượng: ≤ -15.0°C (chuẩn -18 đến -25°C)
 */

let environmentState = {
  year: new Date().getFullYear(),
  month: new Date().getMonth() + 1,
  logs: [],
  stats: {},
  limits: {
    room_temp_min: 18.0,
    room_temp_max: 25.0,
    room_hum_min: 40.0,
    room_hum_max: 75.0,
    fridge_temp_min: 2.0,
    fridge_temp_max: 8.0,
    freezer_temp_max: -15.0
  }
};

// Main loader called when switching to 'environment' tab
window.loadEnvironmentModule = async function() {
  const monthSelect = document.getElementById('env-select-month');
  const yearSelect = document.getElementById('env-select-year');

  const now = new Date();
  if (monthSelect && !monthSelect.value) {
    monthSelect.value = now.getMonth() + 1;
  }
  if (yearSelect && !yearSelect.value) {
    yearSelect.value = now.getFullYear();
  }

  await loadEnvironmentLogs();
};

window.loadEnvironmentLogs = async function() {
  const monthSelect = document.getElementById('env-select-month');
  const yearSelect = document.getElementById('env-select-year');
  const tbody = document.getElementById('env-logs-tbody');

  if (monthSelect) environmentState.month = parseInt(monthSelect.value) || (new Date().getMonth() + 1);
  if (yearSelect) environmentState.year = parseInt(yearSelect.value) || new Date().getFullYear();

  if (tbody) {
    tbody.innerHTML = `
      <tr>
        <td colspan="11" class="p-8 text-center text-slate-500">
          <div class="animate-spin inline-block w-6 h-6 border-3 border-teal-600 border-t-transparent rounded-full mb-2"></div>
          <div>Đang tải sổ nhiệt độ - độ ẩm Tháng ${environmentState.month}/${environmentState.year}...</div>
        </td>
      </tr>
    `;
  }

  try {
    const res = await fetch(`/api/environment/logs?year=${environmentState.year}&month=${environmentState.month}`);
    if (!res.ok) throw new Error('Không thể tải dữ liệu nhiệt độ môi trường');
    const data = await res.json();

    environmentState.logs = data.logs || [];
    environmentState.stats = data.stats || {};
    if (data.stats && data.stats.limits) {
      environmentState.limits = data.stats.limits;
    }

    renderEnvironmentKPIs(environmentState.stats);
    renderEnvironmentTable(environmentState.logs);
  } catch (err) {
    console.error('loadEnvironmentLogs error:', err);
    if (tbody) {
      tbody.innerHTML = '<tr><td colspan="11" class="p-8 text-center text-red-500 font-bold">Lỗi kết nối tải dữ liệu nhiệt độ.</td></tr>';
    }
  }
};

function renderEnvironmentKPIs(stats) {
  const summary = stats.summary || {};
  const latest = stats.latest || {};

  // Card 1: Phòng xét nghiệm Temp (18 - 25°C)
  const roomTempEl = document.getElementById('env-kpi-room-temp');
  const roomTempStatus = document.getElementById('env-kpi-room-temp-status');
  const roomTempAvg = document.getElementById('env-kpi-room-temp-avg');
  const roomTempRange = document.getElementById('env-kpi-room-temp-range');

  if (latest && latest.room_temp !== undefined) {
    const val = parseFloat(latest.room_temp);
    if (roomTempEl) roomTempEl.textContent = `${val.toFixed(1)}°C`;
    const isSafe = (val >= 18.0 && val <= 25.0);
    if (roomTempStatus) {
      roomTempStatus.textContent = isSafe ? 'Đạt chuẩn' : 'Ngoài ngưỡng!';
      roomTempStatus.className = isSafe ? 'text-[11px] font-bold text-emerald-600' : 'text-[11px] font-black text-red-600 animate-pulse';
    }
  } else if (roomTempEl) {
    roomTempEl.textContent = '--°C';
  }
  if (summary.room_temp) {
    if (roomTempAvg) roomTempAvg.textContent = summary.room_temp.avg !== null ? `${summary.room_temp.avg}°C` : '--';
    if (roomTempRange) roomTempRange.textContent = (summary.room_temp.min !== null) ? `${summary.room_temp.min} ~ ${summary.room_temp.max}°C` : '--';
  }

  // Card 2: Độ ẩm (40 - 75%)
  const roomHumEl = document.getElementById('env-kpi-room-hum');
  const roomHumStatus = document.getElementById('env-kpi-room-hum-status');
  const roomHumAvg = document.getElementById('env-kpi-room-hum-avg');
  const roomHumRange = document.getElementById('env-kpi-room-hum-range');

  if (latest && latest.room_humidity !== undefined) {
    const val = parseFloat(latest.room_humidity);
    if (roomHumEl) roomHumEl.textContent = `${val.toFixed(1)}%`;
    const isSafe = (val >= 40.0 && val <= 75.0);
    if (roomHumStatus) {
      roomHumStatus.textContent = isSafe ? 'Ổn định' : 'Vượt ẩm!';
      roomHumStatus.className = isSafe ? 'text-[11px] font-bold text-blue-600' : 'text-[11px] font-black text-red-600 animate-pulse';
    }
  } else if (roomHumEl) {
    roomHumEl.textContent = '--%';
  }
  if (summary.humidity) {
    if (roomHumAvg) roomHumAvg.textContent = summary.humidity.avg !== null ? `${summary.humidity.avg}%` : '--';
    if (roomHumRange) roomHumRange.textContent = (summary.humidity.min !== null) ? `${summary.humidity.min} ~ ${summary.humidity.max}%` : '--';
  }

  // Card 3: Tủ lạnh 2-8°C
  const fridgeEl = document.getElementById('env-kpi-fridge-temp');
  const fridgeStatus = document.getElementById('env-kpi-fridge-temp-status');
  const fridgeAvg = document.getElementById('env-kpi-fridge-temp-avg');
  const fridgeRange = document.getElementById('env-kpi-fridge-temp-range');

  if (latest && latest.fridge_temp !== undefined) {
    const val = parseFloat(latest.fridge_temp);
    if (fridgeEl) fridgeEl.textContent = `${val.toFixed(1)}°C`;
    const isSafe = (val >= 2.0 && val <= 8.0);
    if (fridgeStatus) {
      fridgeStatus.textContent = isSafe ? 'Bảo quản tốt' : 'Lệch nhiệt!';
      fridgeStatus.className = isSafe ? 'text-[11px] font-bold text-teal-600' : 'text-[11px] font-black text-red-600 animate-pulse';
    }
  } else if (fridgeEl) {
    fridgeEl.textContent = '--°C';
  }
  if (summary.fridge_temp) {
    if (fridgeAvg) fridgeAvg.textContent = summary.fridge_temp.avg !== null ? `${summary.fridge_temp.avg}°C` : '--';
    if (fridgeRange) fridgeRange.textContent = (summary.fridge_temp.min !== null) ? `${summary.fridge_temp.min} ~ ${summary.fridge_temp.max}°C` : '--';
  }

  // Card 4: Tủ đông <= -15°C
  const freezerEl = document.getElementById('env-kpi-freezer-temp');
  const freezerStatus = document.getElementById('env-kpi-freezer-temp-status');
  const freezerAvg = document.getElementById('env-kpi-freezer-temp-avg');
  const freezerRange = document.getElementById('env-kpi-freezer-temp-range');

  if (latest && latest.freezer_temp !== undefined) {
    const val = parseFloat(latest.freezer_temp);
    if (freezerEl) freezerEl.textContent = `${val.toFixed(1)}°C`;
    const isSafe = (val <= -15.0);
    if (freezerStatus) {
      freezerStatus.textContent = isSafe ? 'Đạt âm sâu' : 'Không đủ lạnh!';
      freezerStatus.className = isSafe ? 'text-[11px] font-bold text-cyan-700' : 'text-[11px] font-black text-red-600 animate-pulse';
    }
  } else if (freezerEl) {
    freezerEl.textContent = '--°C';
  }
  if (summary.freezer_temp) {
    if (freezerAvg) freezerAvg.textContent = summary.freezer_temp.avg !== null ? `${summary.freezer_temp.avg}°C` : '--';
    if (freezerRange) freezerRange.textContent = (summary.freezer_temp.min !== null) ? `${summary.freezer_temp.min} ~ ${summary.freezer_temp.max}°C` : '--';
  }

  // Month stats badge
  const statTotal = document.getElementById('env-stat-total');
  const statSafe = document.getElementById('env-stat-safe');
  const statWarning = document.getElementById('env-stat-warning');

  if (statTotal) statTotal.textContent = stats.total_logs || 0;
  if (statSafe) statSafe.textContent = stats.safe_count || 0;
  if (statWarning) statWarning.textContent = stats.warning_count || 0;
}

function renderEnvironmentTable(logs) {
  const tbody = document.getElementById('env-logs-tbody');
  if (!tbody) return;

  if (!logs || logs.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="11" class="p-8 text-center text-slate-400">
          <div class="text-3xl mb-2">📋</div>
          <div class="font-bold text-slate-600">Chưa có bản ghi nhiệt độ nào trong Tháng ${environmentState.month}/${environmentState.year}</div>
          <div class="text-[11px] text-slate-400 mt-1">Nhấn "+ Ghi Nhận Ca Mới" để lưu nhiệt độ ca sáng hoặc chiều</div>
        </td>
      </tr>
    `;
    return;
  }

  const isAdmin = currentUser && ['truong_khoa', 'ktv_truong'].includes(currentUser.role);

  let html = '';
  logs.forEach((log, idx) => {
    const isSafe = Boolean(log.is_safe);
    const shiftLabel = (log.shift === 'sang') ? 'Ca Sáng' : 'Ca Chiều';
    const shiftBadge = (log.shift === 'sang') 
      ? '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800">Sáng (08h)</span>'
      : '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-100 text-indigo-800">Chiều (14h)</span>';

    // Cell coloring for out of range
    const rTemp = parseFloat(log.room_temp);
    const rHum = parseFloat(log.room_humidity);
    const frTemp = parseFloat(log.fridge_temp);
    const fzTemp = parseFloat(log.freezer_temp);

    const rTempWarn = (rTemp < 18.0 || rTemp > 25.0);
    const rHumWarn = (rHum < 40.0 || rHum > 75.0);
    const frWarn = (frTemp < 2.0 || frTemp > 8.0);
    const fzWarn = (fzTemp > -15.0);

    const devTag = log.target_device && log.target_device !== 'all' 
      ? `<span class="inline-block mt-0.5 px-1.5 py-0.5 rounded text-[9px] font-bold bg-teal-100 text-teal-800 border border-teal-200">${log.target_device.toUpperCase()}</span>` 
      : '<span class="inline-block mt-0.5 px-1.5 py-0.5 rounded text-[9px] font-medium bg-slate-100 text-slate-600">Toàn bộ</span>';

    const rowBg = !isSafe ? 'bg-red-50/60' : ((idx % 2 === 0) ? 'bg-white' : 'bg-slate-50/40');

    html += `
      <tr data-device="${log.target_device || 'all'}" class="${rowBg} hover:bg-teal-50/30 transition border-b border-slate-100 text-slate-800">
        <td class="p-2.5 text-center font-bold text-slate-400">${idx + 1}</td>
        <td class="p-2.5 text-center font-mono font-bold text-slate-900">${log.log_date}</td>
        <td class="p-2.5 text-center">
          ${shiftBadge}
          <div class="text-[10px] font-mono text-slate-400 mt-0.5">${log.log_time || '--:--'}</div>
          ${devTag}
        </td>
        <td class="p-2.5 text-right font-mono font-bold ${rTempWarn ? 'text-red-600 bg-red-100/70 rounded' : 'text-slate-800'}">
          ${rTemp.toFixed(1)}°C
        </td>
        <td class="p-2.5 text-right font-mono font-bold ${rHumWarn ? 'text-red-600 bg-red-100/70 rounded' : 'text-slate-800'}">
          ${rHum.toFixed(1)}%
        </td>
        <td class="p-2.5 text-right font-mono font-bold ${frWarn ? 'text-red-600 bg-red-100/70 rounded' : 'text-slate-800'}">
          ${frTemp.toFixed(1)}°C
        </td>
        <td class="p-2.5 text-right font-mono font-bold ${fzWarn ? 'text-red-600 bg-red-100/70 rounded' : 'text-slate-800'}">
          ${fzTemp.toFixed(1)}°C
        </td>
        <td class="p-2.5 text-center">
          ${isSafe 
            ? '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">🟢 An Toàn</span>' 
            : '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-800 border border-red-200 animate-pulse">🔴 Cảnh Báo</span>'}
        </td>
        <td class="p-2.5">
          ${log.warning_note ? `<div class="text-[11px] font-semibold text-red-700">${log.warning_note}</div>` : ''}
          ${log.action_taken ? `<div class="text-[11px] text-slate-600 italic mt-0.5">Xử lý: ${log.action_taken}</div>` : (isSafe ? '<span class="text-slate-400">Điều kiện bình thường</span>' : '<span class="text-red-500 italic">Chưa ghi nhận xử lý</span>')}
        </td>
        <td class="p-2.5">
          <div class="font-semibold text-slate-700">${log.logged_by_name || 'KTV'}</div>
        </td>
        <td class="p-2.5">
          ${log.reviewer_name 
            ? `<span class="inline-flex items-center gap-1 text-[11px] text-teal-800 font-bold"><svg class="w-3.5 h-3.5 text-teal-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>${log.reviewer_name}</span>`
            : (isAdmin ? `<button onclick="reviewEnvLog(${log.id})" class="px-2 py-1 bg-teal-50 hover:bg-teal-100 text-teal-700 font-bold rounded text-[11px] border border-teal-200">Ký Duyệt</button>` : '<span class="text-slate-400 text-[11px] italic">Chưa duyệt</span>')}
        </td>
      </tr>
    `;
  });

  tbody.innerHTML = html;
}

// Modal Log Entry with Device Selection
window.openEnvLogModal = function(targetDevice = 'all') {
  const errBox = document.getElementById('env-modal-error');
  if (errBox) errBox.classList.add('hidden');

  const now = new Date();
  const dateInput = document.getElementById('env-input-date');
  const shiftSelect = document.getElementById('env-input-shift');
  const timeInput = document.getElementById('env-input-time');

  if (dateInput) dateInput.value = now.toISOString().split('T')[0];
  const isMorning = now.getHours() < 12;
  if (shiftSelect) shiftSelect.value = isMorning ? 'sang' : 'chieu';
  if (timeInput) timeInput.value = now.toTimeString().slice(0, 5);

  // Set default reasonable values
  const rTemp = document.getElementById('env-input-room-temp');
  const rHum = document.getElementById('env-input-room-hum');
  const frTemp = document.getElementById('env-input-fridge-temp');
  const frSample = document.getElementById('env-input-fridge-sample-temp');
  const fzTemp = document.getElementById('env-input-freezer-temp');
  const incTemp = document.getElementById('env-input-incubator-temp');
  const actionInput = document.getElementById('env-input-action');

  if (rTemp) rTemp.value = isMorning ? "22.0" : "23.5";
  if (rHum) rHum.value = isMorning ? "58.0" : "62.0";
  if (frTemp) frTemp.value = "4.5";
  if (frSample) frSample.value = "4.2";
  if (fzTemp) fzTemp.value = "-20.0";
  if (incTemp) incTemp.value = "36.5";
  if (actionInput) actionInput.value = "";

  selectDevicePill(targetDevice || 'all');
  openModal('modal-env-log');
};

window.selectDevicePill = function(devId) {
  const select = document.getElementById('env-input-target-device');
  if (select) select.value = devId;

  // Update pills UI
  const pillIds = ['all', 'tl01', 'tl02', 'td01', 'ta01', 'room'];
  pillIds.forEach(id => {
    const btn = document.getElementById(`pill-dev-${id}`);
    if (!btn) return;
    if (id === devId) {
      btn.className = "px-2.5 py-1 rounded-lg text-xs font-bold bg-teal-700 text-white shadow-xs transition";
    } else {
      btn.className = "px-2.5 py-1 rounded-lg text-xs font-semibold bg-white text-slate-700 hover:bg-teal-100 border border-slate-200 transition";
    }
  });

  onTargetDeviceChange();
};

window.onTargetDeviceChange = function() {
  const select = document.getElementById('env-input-target-device');
  const devId = select ? select.value : 'all';

  const nameEl = document.getElementById('env-device-info-name');
  const limitEl = document.getElementById('env-device-info-limit');

  const allBoxes = [
    'box-env-room-temp', 'box-env-room-hum',
    'box-env-tl01', 'box-env-tl02',
    'box-env-td01', 'box-env-ta01'
  ];

  // Reset all boxes style
  allBoxes.forEach(bId => {
    const el = document.getElementById(bId);
    if (!el) return;
    el.className = "p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1 transition opacity-90";
  });

  const highlightClass = "p-3 bg-teal-50/70 border-2 border-teal-500 rounded-xl space-y-1 transition shadow-xs opacity-100 ring-2 ring-teal-300";

  if (devId === 'tl01') {
    if (nameEl) nameEl.textContent = "🧊 Đang chọn: Tủ Lạnh Hóa Chất & Sinh Phẩm (TL-01)";
    if (limitEl) limitEl.textContent = "Dải chuẩn: 2.0 - 8.0°C";
    const box = document.getElementById('box-env-tl01');
    if (box) box.className = highlightClass;
    setTimeout(() => document.getElementById('env-input-fridge-temp')?.focus(), 100);
  } else if (devId === 'tl02') {
    if (nameEl) nameEl.textContent = "🧪 Đang chọn: Tủ Lạnh Mẫu Bệnh Phẩm & Huyết Thanh (TL-02)";
    if (limitEl) limitEl.textContent = "Dải chuẩn: 2.0 - 8.0°C";
    const box = document.getElementById('box-env-tl02');
    if (box) box.className = highlightClass;
    setTimeout(() => document.getElementById('env-input-fridge-sample-temp')?.focus(), 100);
  } else if (devId === 'td01') {
    if (nameEl) nameEl.textContent = "❄️ Đang chọn: Tủ Đông Âm Sâu Lưu Mẫu & QC (TĐ-01)";
    if (limitEl) limitEl.textContent = "Dải chuẩn: ≤ -15.0°C";
    const box = document.getElementById('box-env-td01');
    if (box) box.className = "p-3 bg-cyan-50/70 border-2 border-cyan-500 rounded-xl space-y-1 transition shadow-xs opacity-100 ring-2 ring-cyan-300";
    setTimeout(() => document.getElementById('env-input-freezer-temp')?.focus(), 100);
  } else if (devId === 'ta01') {
    if (nameEl) nameEl.textContent = "🌡️ Đang chọn: Tủ Ấm Ủ Mẫu & Vi Sinh (TÂ-01)";
    if (limitEl) limitEl.textContent = "Dải chuẩn: 35.0 - 37.0°C";
    const box = document.getElementById('box-env-ta01');
    if (box) box.className = "p-3 bg-amber-50/70 border-2 border-amber-500 rounded-xl space-y-1 transition shadow-xs opacity-100 ring-2 ring-amber-300";
    setTimeout(() => document.getElementById('env-input-incubator-temp')?.focus(), 100);
  } else if (devId === 'room') {
    if (nameEl) nameEl.textContent = "🏢 Đang chọn: Không Gian Phòng Máy Xét Nghiệm (PM-01)";
    if (limitEl) limitEl.textContent = "Chuẩn: 18 - 25°C & 40 - 75%";
    const box1 = document.getElementById('box-env-room-temp');
    const box2 = document.getElementById('box-env-room-hum');
    if (box1) box1.className = "p-3 bg-emerald-50/70 border-2 border-emerald-500 rounded-xl space-y-1 transition shadow-xs opacity-100 ring-2 ring-emerald-300";
    if (box2) box2.className = "p-3 bg-blue-50/70 border-2 border-blue-500 rounded-xl space-y-1 transition shadow-xs opacity-100 ring-2 ring-blue-300";
    setTimeout(() => document.getElementById('env-input-room-temp')?.focus(), 100);
  } else {
    // 'all'
    if (nameEl) nameEl.textContent = "🏢 Đang chọn: Toàn bộ vị trí (Đo tổng hợp theo ca)";
    if (limitEl) limitEl.textContent = "Chuẩn BM.MT.01";
    allBoxes.forEach(bId => {
      const el = document.getElementById(bId);
      if (el) el.className = "p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1 transition opacity-100";
    });
  }

  checkEnvInputThresholds();
};

window.checkEnvInputThresholds = function() {
  const targetDevice = document.getElementById('env-input-target-device')?.value || 'all';

  const rTemp = parseFloat(document.getElementById('env-input-room-temp')?.value);
  const rHum = parseFloat(document.getElementById('env-input-room-hum')?.value);
  const frTemp = parseFloat(document.getElementById('env-input-fridge-temp')?.value);
  const frSample = parseFloat(document.getElementById('env-input-fridge-sample-temp')?.value);
  const fzTemp = parseFloat(document.getElementById('env-input-freezer-temp')?.value);
  const incTemp = parseFloat(document.getElementById('env-input-incubator-temp')?.value);

  const warnBox = document.getElementById('env-modal-warning-box');
  const warnText = document.getElementById('env-modal-warning-text');
  if (!warnBox || !warnText) return;

  const warnings = [];

  // Check based on active device
  if (targetDevice === 'all' || targetDevice === 'room') {
    if (!isNaN(rTemp) && (rTemp < 18.0 || rTemp > 25.0)) {
      warnings.push(`• Nhiệt độ phòng ${rTemp}°C ngoài dải chuẩn 18.0 - 25.0°C`);
    }
    if (!isNaN(rHum) && (rHum < 40.0 || rHum > 75.0)) {
      warnings.push(`• Độ ẩm phòng ${rHum}% ngoài dải chuẩn 40.0 - 75.0%`);
    }
  }

  if (targetDevice === 'all' || targetDevice === 'tl01') {
    if (!isNaN(frTemp) && (frTemp < 2.0 || frTemp > 8.0)) {
      warnings.push(`• Tủ lạnh sinh phẩm TL-01 (${frTemp}°C) ngoài dải chuẩn 2.0 - 8.0°C`);
    }
  }

  if (targetDevice === 'all' || targetDevice === 'tl02') {
    if (!isNaN(frSample) && (frSample < 2.0 || frSample > 8.0)) {
      warnings.push(`• Tủ lạnh mẫu lưu TL-02 (${frSample}°C) ngoài dải chuẩn 2.0 - 8.0°C`);
    }
  }

  if (targetDevice === 'all' || targetDevice === 'td01') {
    if (!isNaN(fzTemp) && fzTemp > -15.0) {
      warnings.push(`• Tủ đông lưu mẫu TĐ-01 (${fzTemp}°C) cao hơn ngưỡng chuẩn ≤ -15.0°C`);
    }
  }

  if (targetDevice === 'all' || targetDevice === 'ta01') {
    if (!isNaN(incTemp) && (incTemp < 35.0 || incTemp > 37.0)) {
      warnings.push(`• Tủ ấm TÂ-01 (${incTemp}°C) ngoài dải chuẩn 35.0 - 37.0°C`);
    }
  }

  if (warnings.length > 0) {
    warnBox.classList.remove('hidden');
    warnText.innerHTML = warnings.join('<br>') + '<div class="mt-1 font-bold text-slate-800">Vui lòng điền ô "Hành động khắc phục / Xử lý sự cố" bên dưới!</div>';
  } else {
    warnBox.classList.add('hidden');
    warnText.innerHTML = '';
  }
};

window.submitSaveEnvLog = async function() {
  const errBox = document.getElementById('env-modal-error');
  if (errBox) errBox.classList.add('hidden');

  const logDate = document.getElementById('env-input-date')?.value;
  const shift = document.getElementById('env-input-shift')?.value;
  const logTime = document.getElementById('env-input-time')?.value;
  const targetDevice = document.getElementById('env-input-target-device')?.value || 'all';

  const roomTemp = document.getElementById('env-input-room-temp')?.value;
  const roomHum = document.getElementById('env-input-room-hum')?.value;
  const fridgeTemp = document.getElementById('env-input-fridge-temp')?.value;
  const fridgeSample = document.getElementById('env-input-fridge-sample-temp')?.value;
  const freezerTemp = document.getElementById('env-input-freezer-temp')?.value;
  const incubatorTemp = document.getElementById('env-input-incubator-temp')?.value;
  const actionTaken = document.getElementById('env-input-action')?.value.trim();

  // Validate only the target device's input
  if (targetDevice === 'tl01' && (!fridgeTemp || isNaN(parseFloat(fridgeTemp)))) {
    if (errBox) {
      errBox.textContent = 'Vui lòng nhập nhiệt độ cho Tủ Lạnh Hóa Chất & Sinh Phẩm (TL-01)!';
      errBox.classList.remove('hidden');
    }
    return;
  }
  if (targetDevice === 'tl02' && (!fridgeSample || isNaN(parseFloat(fridgeSample)))) {
    if (errBox) {
      errBox.textContent = 'Vui lòng nhập nhiệt độ cho Tủ Lạnh Mẫu Bệnh Phẩm (TL-02)!';
      errBox.classList.remove('hidden');
    }
    return;
  }
  if (targetDevice === 'td01' && (!freezerTemp || isNaN(parseFloat(freezerTemp)))) {
    if (errBox) {
      errBox.textContent = 'Vui lòng nhập nhiệt độ cho Tủ Đông Âm Sâu (TĐ-01)!';
      errBox.classList.remove('hidden');
    }
    return;
  }
  if (targetDevice === 'ta01' && (!incubatorTemp || isNaN(parseFloat(incubatorTemp)))) {
    if (errBox) {
      errBox.textContent = 'Vui lòng nhập nhiệt độ cho Tủ Ấm (TÂ-01)!';
      errBox.classList.remove('hidden');
    }
    return;
  }
  if (targetDevice === 'room' && (!roomTemp || !roomHum)) {
    if (errBox) {
      errBox.textContent = 'Vui lòng nhập nhiệt độ và độ ẩm phòng máy xét nghiệm!';
      errBox.classList.remove('hidden');
    }
    return;
  }

  try {
    const res = await fetch('/api/environment/logs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        log_date: logDate,
        shift: shift,
        log_time: logTime,
        target_device: targetDevice,
        room_temp: roomTemp ? parseFloat(roomTemp) : null,
        room_humidity: roomHum ? parseFloat(roomHum) : null,
        fridge_temp: fridgeTemp ? parseFloat(fridgeTemp) : null,
        fridge_sample_temp: fridgeSample ? parseFloat(fridgeSample) : null,
        freezer_temp: freezerTemp ? parseFloat(freezerTemp) : null,
        incubator_temp: incubatorTemp ? parseFloat(incubatorTemp) : null,
        action_taken: actionTaken
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Lỗi lưu bản ghi');

    closeModal('modal-env-log');
    showToast(data.message || 'Đã ghi nhận nhiệt độ!', 'success');
    loadEnvironmentLogs();
  } catch (err) {
    if (errBox) {
      errBox.textContent = err.message;
      errBox.classList.remove('hidden');
    }
  }
};

window.filterEnvTableByDevice = function() {
  const filterSelect = document.getElementById('env-filter-device');
  const targetDev = filterSelect ? filterSelect.value : 'all';

  const rows = document.querySelectorAll('#env-logs-tbody tr');
  rows.forEach(tr => {
    // If targetDev is 'all', show all
    if (targetDev === 'all') {
      tr.classList.remove('hidden');
      return;
    }
    // Highlighting / filtering rows
    tr.classList.remove('hidden');
  });
};

window.reviewEnvLog = async function(logId) {
  try {
    const res = await fetch(`/api/environment/logs/${logId}/review`, { method: 'POST' });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Lỗi duyệt');
    showToast('Đã ký duyệt ghi nhận nhiệt độ.', 'success');
    loadEnvironmentLogs();
  } catch (err) {
    alert(err.message);
  }
};

// ==============================================================================
// XUẤT & IN SỔ NHIỆT ĐỘ - ĐỘ ẨM KHỔ A4 (BM.MT.01 / QUYẾT ĐỊNH 2429/QĐ-BYT)
// ==============================================================================

window.openPrintEnvModal = async function() {
  const container = document.getElementById('print-env-container');
  if (!container) return;

  container.innerHTML = '<div class="p-8 text-center text-slate-500">Đang chuẩn bị biểu mẫu A4 BM.MT.01...</div>';
  openModal('modal-print-env');

  try {
    const res = await fetch(`/api/environment/print-data?year=${environmentState.year}&month=${environmentState.month}`);
    if (!res.ok) throw new Error('Không thể tải biểu mẫu in');
    const data = await res.json();

    renderPrintEnvSheet(data);
  } catch (err) {
    container.innerHTML = `<div class="p-8 text-center text-red-500 font-bold">${err.message}</div>`;
  }
};

function renderPrintEnvSheet(data) {
  const container = document.getElementById('print-env-container');
  if (!container) return;

  let rowsHtml = '';
  data.days.forEach(d => {
    const m = d.morning || {};
    const a = d.afternoon || {};

    const mRTemp = m.room_temp !== undefined ? m.room_temp.toFixed(1) : '';
    const mRHum = m.room_humidity !== undefined ? m.room_humidity.toFixed(1) : '';
    const mFridge = m.fridge_temp !== undefined ? m.fridge_temp.toFixed(1) : '';
    const mFreezer = m.freezer_temp !== undefined ? m.freezer_temp.toFixed(1) : '';
    const mSign = m.logged_by_name ? m.logged_by_name.replace('CN. ', '') : '';

    const aRTemp = a.room_temp !== undefined ? a.room_temp.toFixed(1) : '';
    const aRHum = a.room_humidity !== undefined ? a.room_humidity.toFixed(1) : '';
    const aFridge = a.fridge_temp !== undefined ? a.fridge_temp.toFixed(1) : '';
    const aFreezer = a.freezer_temp !== undefined ? a.freezer_temp.toFixed(1) : '';
    const aSign = a.logged_by_name ? a.logged_by_name.replace('CN. ', '') : '';

    const warningAction = [m.warning_note, m.action_taken, a.warning_note, a.action_taken].filter(Boolean).join('; ');

    rowsHtml += `
      <tr style="height: 20px; font-size: 8.5pt;">
        <td style="text-align: center; font-weight: bold; border: 1px solid #333;">${d.day}</td>
        <!-- Morning -->
        <td style="text-align: center; border: 1px solid #333;">${mRTemp}</td>
        <td style="text-align: center; border: 1px solid #333;">${mRHum}</td>
        <td style="text-align: center; border: 1px solid #333;">${mFridge}</td>
        <td style="text-align: center; border: 1px solid #333;">${mFreezer}</td>
        <td style="text-align: center; border: 1px solid #333; font-size: 7.5pt;">${mSign}</td>
        <!-- Afternoon -->
        <td style="text-align: center; border: 1px solid #333;">${aRTemp}</td>
        <td style="text-align: center; border: 1px solid #333;">${aRHum}</td>
        <td style="text-align: center; border: 1px solid #333;">${aFridge}</td>
        <td style="text-align: center; border: 1px solid #333;">${aFreezer}</td>
        <td style="text-align: center; border: 1px solid #333; font-size: 7.5pt;">${aSign}</td>
        <!-- Note -->
        <td style="text-align: left; border: 1px solid #333; font-size: 7.5pt; padding: 1px 4px;">${warningAction}</td>
      </tr>
    `;
  });

  container.innerHTML = `
    <div id="print-env-sheet" style="font-family: 'Times New Roman', serif; color: #000; background: #fff; padding: 15px; font-size: 9.5pt; line-height: 1.25;">
      <!-- Header -->
      <table style="width: 100%; margin-bottom: 12px; border-collapse: collapse;">
        <tr>
          <td style="width: 45%; vertical-align: top;">
            <div style="font-weight: bold; font-size: 9.5pt;">${data.hospital}</div>
            <div style="font-weight: bold; font-size: 10.5pt; color: #0369a1;">${data.department}</div>
            <div style="font-size: 8.5pt; font-style: italic;">Mã biểu mẫu: <strong>${data.form_code}</strong></div>
          </td>
          <td style="width: 55%; text-align: center; vertical-align: top;">
            <div style="font-weight: bold; font-size: 9.5pt;">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
            <div style="font-size: 9pt; font-weight: bold;">Độc lập - Tự do - Hạnh phúc</div>
            <div style="font-size: 8pt; margin-top: 3px;">Tiêu chuẩn: Quyết định 2429/QĐ-BYT & ISO 15189:2022</div>
          </td>
        </tr>
      </table>

      <!-- Title -->
      <div style="text-align: center; margin-bottom: 12px;">
        <div style="font-size: 13pt; font-weight: bold; text-transform: uppercase;">
          BẢNG THEO DÕI NHIỆT ĐỘ VÀ ĐỘ ẨM HÀNG NGÀY
        </div>
        <div style="font-size: 10.5pt; font-weight: bold; margin-top: 2px;">
          THÁNG ${data.month < 10 ? '0' + data.month : data.month} NĂM ${data.year}
        </div>
        <div style="font-size: 8.5pt; font-style: italic; color: #334155; margin-top: 3px;">
          (Dải chuẩn: Phòng: 18-25°C, 40-75% • Tủ lạnh sinh phẩm: 2-8°C • Tủ đông: ≤ -15°C)
        </div>
      </div>

      <!-- Main Grid Table -->
      <table style="width: 100%; border-collapse: collapse; border: 1.5px solid #000; margin-bottom: 14px;">
        <thead>
          <tr style="background: #f1f5f9; font-weight: bold; font-size: 8pt; text-align: center;">
            <th rowspan="2" style="width: 4%; border: 1px solid #000; padding: 4px;">Ngày</th>
            <th colspan="5" style="border: 1px solid #000; padding: 4px; background: #e0f2fe;">CA SÁNG (08h00)</th>
            <th colspan="5" style="border: 1px solid #000; padding: 4px; background: #e0e7ff;">CA CHIỀU (14h00)</th>
            <th rowspan="2" style="width: 20%; border: 1px solid #000; padding: 4px;">Sự Cố & Hành Động Khắc Phục</th>
          </tr>
          <tr style="background: #f8fafc; font-weight: bold; font-size: 7.5pt; text-align: center;">
            <th style="width: 7%; border: 1px solid #000; padding: 3px;">Nhiệt độ phòng (°C)</th>
            <th style="width: 7%; border: 1px solid #000; padding: 3px;">Độ ẩm phòng (%)</th>
            <th style="width: 7%; border: 1px solid #000; padding: 3px;">Tủ lạnh (2-8°C)</th>
            <th style="width: 7%; border: 1px solid #000; padding: 3px;">Tủ đông (≤-15°C)</th>
            <th style="width: 7%; border: 1px solid #000; padding: 3px;">KTV Đo</th>
            <th style="width: 7%; border: 1px solid #000; padding: 3px;">Nhiệt độ phòng (°C)</th>
            <th style="width: 7%; border: 1px solid #000; padding: 3px;">Độ ẩm phòng (%)</th>
            <th style="width: 7%; border: 1px solid #000; padding: 3px;">Tủ lạnh (2-8°C)</th>
            <th style="width: 7%; border: 1px solid #000; padding: 3px;">Tủ đông (≤-15°C)</th>
            <th style="width: 7%; border: 1px solid #000; padding: 3px;">KTV Đo</th>
          </tr>
        </thead>
        <tbody>
          ${rowsHtml}
        </tbody>
      </table>

      <!-- Signatures -->
      <table style="width: 100%; border-collapse: collapse; margin-top: 10px; page-break-inside: avoid;">
        <tr style="text-align: center; font-weight: bold; font-size: 10pt;">
          <td style="width: 50%;">KỸ THUẬT VIÊN TRƯỞNG</td>
          <td style="width: 50%;">TRƯỞNG KHOA XÉT NGHIỆM</td>
        </tr>
        <tr style="text-align: center; font-style: italic; font-size: 8.5pt; color: #475569;">
          <td>(Ký và ghi rõ họ tên)</td>
          <td>(Ký và ghi rõ họ tên)</td>
        </tr>
        <tr style="height: 60px;">
          <td></td>
          <td></td>
        </tr>
        <tr style="text-align: center; font-weight: bold; font-size: 10pt;">
          <td>CN. Nguyễn Trường Duy</td>
          <td>CN. Lê Đình Tú</td>
        </tr>
      </table>
    </div>
  `;
}

window.executePrintEnvSheet = function() {
  const printContent = document.getElementById('print-env-sheet');
  if (!printContent) return;

  const win = window.open('', '', 'width=1100,height=850');
  win.document.write(`
    <html>
      <head>
        <title>Sổ Theo Dõi Nhiệt Độ - Độ Ẩm BM.MT.01 - BVĐK Thiên Ân</title>
        <style>
          @page { size: A4 landscape; margin: 8mm 6mm; }
          body { margin: 0; padding: 0; font-family: 'Times New Roman', serif; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
          table { border-collapse: collapse; }
        </style>
      </head>
      <body>
        ${printContent.outerHTML}
        <script>
          window.onload = function() { window.print(); window.close(); };
        </script>
      </body>
    </html>
  `);
  win.document.close();
};
