/**
 * Phân hệ 4: Quản Lý Kho Hóa Chất, Sinh Phẩm & Vật Tư Tiêu Hao
 * Khoa Xét Nghiệm - Bệnh Viện Đa Khoa Thiên Ân - Viễn Đông
 * Tiêu chuẩn: Quyết định 2429/QĐ-BYT (Chương VI: Quản lý hóa chất, vật tư)
 * Chia thành 2 mục chính:
 * 1. Số Lượng Kho Hiện Đang Có Trong Kho (Tồn Kho Thực Tế)
 * 2. Dự Trù Hóa Chất & Vật Tư Tiêu Hao (Kế Hoạch Mua Sắm & Dự Trù)
 */

let inventoryState = {
  activeSubTab: 'stock', // 'stock' or 'forecast'
  category: 'all',       // 'all', 'hoa_chat', 'sinh_pham', 'vat_tu'
  statusFilter: 'all',   // 'all', 'low_stock', 'near_expiry', 'safe'
  searchQuery: '',
  items: [],
  selectedItemForEdit: null,
  forecastItems: []
};

// Main loader for Module 4 (Inventory)
window.loadInventoryModule = async function() {
  await fetchInventoryItems();
  if (inventoryState.activeSubTab === 'forecast') {
    initForecastDraft();
  } else if (inventoryState.activeSubTab === 'openvials') {
    fetchOpenVials();
  }
};

// Switch between 3 main sections: Tồn Kho Thực Tế & Dự Trù & Hạn Mở Nắp
window.switchInventorySubTab = function(subTab) {
  inventoryState.activeSubTab = subTab;

  const btnStock = document.getElementById('inv-subtab-btn-stock');
  const btnForecast = document.getElementById('inv-subtab-btn-forecast');
  const btnOpenVials = document.getElementById('inv-subtab-btn-openvials');

  const contentStock = document.getElementById('inv-content-stock');
  const contentForecast = document.getElementById('inv-content-forecast');
  const contentOpenVials = document.getElementById('inv-content-openvials');

  const activeCls = "flex items-center gap-2 px-3.5 py-2.5 rounded-xl font-bold text-xs sm:text-sm bg-sky-700 text-white shadow-sm transition";
  const inactiveCls = "flex items-center gap-2 px-3.5 py-2.5 rounded-xl font-semibold text-xs sm:text-sm text-slate-600 hover:text-sky-700 hover:bg-sky-50 transition";

  if (btnStock) btnStock.className = (subTab === 'stock') ? activeCls : inactiveCls;
  if (btnForecast) btnForecast.className = (subTab === 'forecast') ? activeCls : inactiveCls;
  if (btnOpenVials) btnOpenVials.className = (subTab === 'openvials') ? activeCls : inactiveCls;

  if (contentStock) contentStock.classList.toggle('hidden', subTab !== 'stock');
  if (contentForecast) contentForecast.classList.toggle('hidden', subTab !== 'forecast');
  if (contentOpenVials) contentOpenVials.classList.toggle('hidden', subTab !== 'openvials');

  if (subTab === 'stock') {
    fetchInventoryItems();
  } else if (subTab === 'forecast') {
    initForecastDraft();
  } else if (subTab === 'openvials') {
    fetchOpenVials();
  }
};

/* ==========================================================================
   MỤC 1: SỐ LƯỢNG KHO HIỆN ĐANG CÓ TRONG KHO (TỒN KHO THỰC TẾ)
   ========================================================================== */

async function fetchInventoryItems() {
  const container = document.getElementById('inventory-items-tbody');
  if (!container) return;

  container.innerHTML = `
    <tr>
      <td colspan="10" class="p-8 text-center text-slate-500">
        <div class="animate-spin inline-block w-6 h-6 border-3 border-sky-600 border-t-transparent rounded-full mb-2"></div>
        <div>Đang tải danh mục tồn kho thực tế...</div>
      </td>
    </tr>
  `;

  try {
    let url = `/api/inventory/items?category=${inventoryState.category}&status_filter=${inventoryState.statusFilter}`;
    if (inventoryState.searchQuery) {
      url += `&q=${encodeURIComponent(inventoryState.searchQuery)}`;
    }

    const res = await fetch(url);
    const data = await res.json();
    if (!res.ok || !data.success) {
      container.innerHTML = '<tr><td colspan="10" class="p-8 text-center text-red-500">Không thể tải dữ liệu kho.</td></tr>';
      return;
    }

    inventoryState.items = data.items || [];
    renderInventoryKPI(data);
    renderInventoryTable(inventoryState.items);
  } catch (err) {
    container.innerHTML = '<tr><td colspan="10" class="p-8 text-center text-red-500">Lỗi kết nối máy chủ khi tải kho.</td></tr>';
  }
}

function renderInventoryKPI(data) {
  const setT = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  setT('inv-kpi-total', `${data.total_unfiltered || data.total} Mặt Hàng`);
  setT('inv-kpi-low-stock', `${data.low_stock_count || 0} Cảnh Báo`);
  setT('inv-kpi-near-expiry', `${data.near_expiry_count || 0} Mặt Hàng`);
  setT('inv-results-count', `Hiển thị ${data.total} / ${data.total_unfiltered || data.total} mặt hàng`);
}

function renderInventoryTable(items) {
  const tbody = document.getElementById('inventory-items-tbody');
  if (!tbody) return;

  const isAdmin = currentUser && (currentUser.role === 'truong_khoa' || currentUser.role === 'ktv_truong');
  const btnAdd = document.getElementById('btn-add-inventory-item');
  if (btnAdd) btnAdd.classList.toggle('hidden', !isAdmin);

  if (items.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="10" class="p-10 text-center text-slate-500">
          <svg class="w-10 h-10 mx-auto text-slate-300 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>
          <div class="font-semibold text-slate-700 text-sm">Không tìm thấy mặt hàng nào phù hợp</div>
          <div class="text-xs text-slate-400 mt-0.5">Thử đổi bộ lọc hoặc từ khóa tìm kiếm (Glucose, EDTA, Tip, Cồn...)</div>
        </td>
      </tr>
    `;
    return;
  }

  const catBadges = {
    'hoa_chat': '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-sky-100 text-sky-800 border border-sky-200">Hóa chất</span>',
    'sinh_pham': '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-200">Sinh phẩm</span>',
    'vat_tu': '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">Vật tư</span>',
    'qc_chuan': '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200">QC/Chuẩn</span>'
  };

  const tempBadges = {
    '2-8°C': '<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">❄️ 2-8°C</span>',
    '-20°C': '<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">🧊 -20°C</span>',
    '15-25°C': '<span class="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-slate-100 text-slate-700">15-25°C</span>',
    'Phòng': '<span class="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-slate-100 text-slate-700">Phòng</span>'
  };

  let html = '';
  items.forEach((item, idx) => {
    const qty = parseFloat(item.quantity || 0);
    const minS = parseFloat(item.min_stock || 0);
    const isLow = item.is_low_stock;
    const daysLeft = item.days_left;

    // Expiry badge
    let expBadge = '<span class="text-slate-600 font-mono text-xs">' + (item.expiry_date || '--') + '</span>';
    if (item.expiry_status === 'expired') {
      expBadge = `<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-800 border border-red-300">ĐÃ HẾT HẠN (${item.expiry_date})</span>`;
    } else if (item.expiry_status === 'warning_30') {
      expBadge = `<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-300">⚠️ Cận date (${daysLeft} ngày)</span>`;
    }

    // Progress bar for stock level
    const ratio = minS > 0 ? Math.min(100, Math.round((qty / (minS * 2)) * 100)) : 100;
    const barColor = isLow ? 'bg-red-500' : (ratio < 60 ? 'bg-amber-500' : 'bg-emerald-500');

    html += `
      <tr class="hover:bg-slate-50/80 transition text-xs border-b border-slate-100">
        <!-- STT & Mã -->
        <td class="p-3 text-center text-slate-400 font-mono">${idx + 1}</td>
        <td class="p-3">
          <span class="font-mono font-bold text-slate-900 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">
            ${item.code}
          </span>
          <div class="mt-1">${catBadges[item.category] || item.category}</div>
        </td>

        <!-- Tên mặt hàng & Quy cách -->
        <td class="p-3">
          <div class="font-bold text-slate-900 text-xs sm:text-sm hover:text-sky-700 transition leading-snug">
            ${item.name}
          </div>
          <div class="text-[11px] text-slate-500 mt-0.5 flex items-center gap-2">
            <span>QC: <b>${item.spec || '--'}</b></span>
            <span>• Hãng: <b>${item.manufacturer || '--'}</b></span>
          </div>
        </td>

        <!-- ĐVT & Vị trí -->
        <td class="p-3 text-center">
          <span class="font-bold text-slate-800 text-xs">${item.unit}</span>
          <div class="text-[10px] text-slate-400 truncate max-w-[120px] mt-0.5" title="${item.location || ''}">
            ${item.location || 'Kho'}
          </div>
        </td>

        <!-- Lô & Hạn sử dụng -->
        <td class="p-3 text-center">
          <div class="font-mono font-bold text-slate-700">${item.lot_number || '--'}</div>
          <div class="mt-0.5">${expBadge}</div>
        </td>

        <!-- Nhiệt độ bảo quản -->
        <td class="p-3 text-center">
          ${tempBadges[item.storage_temp] || `<span class="text-xs">${item.storage_temp}</span>`}
          ${item.open_date ? `
            <div class="text-[10px] text-teal-700 font-medium mt-1" title="Ngày mở nắp: ${item.open_date}">
              Mở: ${item.open_date.slice(5)}
            </div>
          ` : ''}
        </td>

        <!-- Số lượng tồn kho hiện tại -->
        <td class="p-3 text-right">
          <div class="flex items-center justify-end gap-1.5">
            <span class="text-sm font-extrabold ${isLow ? 'text-red-600' : 'text-slate-900'} font-mono">
              ${qty}
            </span>
            <span class="text-xs text-slate-500">${item.unit}</span>
          </div>
          <!-- Mini progress bar -->
          <div class="w-full bg-slate-200 rounded-full h-1.5 mt-1 overflow-hidden">
            <div class="${barColor} h-1.5 rounded-full" style="width: ${ratio}%"></div>
          </div>
          <div class="text-[10px] text-slate-400 mt-0.5">Tối thiểu: ${minS}</div>
        </td>

        <!-- Tình trạng -->
        <td class="p-3 text-center">
          ${isLow ? `
            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-red-800 border border-red-200">
              Cần nhập thêm
            </span>
          ` : `
            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
              Đủ tồn kho
            </span>
          `}
        </td>

        <!-- Thao tác nhập / xuất / sửa -->
        <td class="p-3 text-right shrink-0">
          ${isAdmin ? `
            <div class="flex items-center justify-end gap-1">
              <button onclick="openAdjustStockModal(${item.id}, 'nhap')" title="Nhập thêm vào kho (+)"
                      class="px-2 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-bold text-[11px] rounded-lg transition border border-emerald-200">
                + Nhập
              </button>
              <button onclick="openAdjustStockModal(${item.id}, 'xuat')" title="Xuất kho sử dụng (-)"
                      class="px-2 py-1 bg-sky-50 hover:bg-sky-100 text-sky-700 font-bold text-[11px] rounded-lg transition border border-sky-200">
                - Xuất
              </button>
              <button onclick="openEditItemModal(${item.id})" title="Chỉnh sửa thông tin mặt hàng"
                      class="p-1 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
              </button>
            </div>
          ` : `
            <span class="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-slate-100 text-slate-500 border border-slate-200 inline-block" title="Nhân viên chỉ có quyền theo dõi hóa chất thực tế">
              👁️ Theo dõi
            </span>
          `}
        </td>
      </tr>
    `;
  });

  tbody.innerHTML = html;
}

window.handleInventorySearch = function(q) {
  inventoryState.searchQuery = q.trim();
  fetchInventoryItems();
};

window.setInventoryCategory = function(cat) {
  inventoryState.category = cat;
  const cats = ['all', 'hoa_chat', 'sinh_pham', 'vat_tu'];
  cats.forEach(c => {
    const el = document.getElementById(`inv-cat-tab-${c}`);
    if (!el) return;
    if (c === cat) {
      el.className = "px-3 py-1.5 rounded-xl font-bold text-xs bg-sky-700 text-white shadow-xs transition";
    } else {
      el.className = "px-3 py-1.5 rounded-xl font-semibold text-xs text-slate-600 hover:text-sky-700 hover:bg-sky-50 border border-slate-200 transition";
    }
  });
  fetchInventoryItems();
};

window.setInventoryStatusFilter = function(status) {
  inventoryState.statusFilter = status;
  fetchInventoryItems();
};

window.exportInventoryExcel = function() {
  window.location.href = `/api/inventory/export-excel?category=${inventoryState.category}`;
};

// Quick Stock Adjustment Modal (+ Nhập / - Xuất)
let currentAdjustItemId = null;
let currentAdjustType = 'xuat';

window.openAdjustStockModal = function(itemId, type) {
  currentAdjustItemId = itemId;
  currentAdjustType = type;

  const item = inventoryState.items.find(i => i.id === itemId);
  if (!item) return;

  const titleEl = document.getElementById('adjust-stock-title');
  const itemNameEl = document.getElementById('adjust-stock-item-name');
  const currentQtyEl = document.getElementById('adjust-stock-current-qty');
  const qtyInput = document.getElementById('adjust-stock-qty');
  const reasonInput = document.getElementById('adjust-stock-reason');
  const btnSubmit = document.getElementById('adjust-stock-submit-btn');

  if (titleEl) titleEl.textContent = (type === 'nhap') ? 'Nhập Thêm Hàng Vào Kho' : 'Xuất Hàng Sử Dụng / Phòng Máy';
  if (itemNameEl) itemNameEl.textContent = `Mặt hàng: ${item.code} - ${item.name} (${item.unit})`;
  if (currentQtyEl) currentQtyEl.textContent = `${item.quantity} ${item.unit}`;
  if (qtyInput) {
    qtyInput.value = '1';
    qtyInput.focus();
  }
  if (reasonInput) reasonInput.value = (type === 'nhap') ? 'Nhập hàng theo dự trù định kỳ' : 'Xuất phòng máy vận hành ca sáng';
  if (btnSubmit) {
    btnSubmit.textContent = (type === 'nhap') ? 'Xác Nhận Nhập Kho' : 'Xác Nhận Xuất Kho';
    btnSubmit.className = (type === 'nhap') ?
      'px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-xs shadow-sm transition' :
      'px-4 py-2 bg-sky-700 hover:bg-sky-800 text-white rounded-xl font-bold text-xs shadow-sm transition';
  }

  document.getElementById('adjust-stock-error').classList.add('hidden');
  openModal('modal-adjust-stock');
};

window.submitAdjustStock = async function() {
  const qtyInput = document.getElementById('adjust-stock-qty');
  const reasonInput = document.getElementById('adjust-stock-reason');
  const errEl = document.getElementById('adjust-stock-error');

  const qty = parseFloat(qtyInput.value || 0);
  const reason = reasonInput.value.trim();

  if (qty <= 0) {
    errEl.textContent = 'Số lượng phải lớn hơn 0.';
    errEl.classList.remove('hidden');
    return;
  }

  try {
    const res = await fetch('/api/inventory/adjust-stock', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        item_id: currentAdjustItemId,
        type: currentAdjustType,
        quantity: qty,
        reason: reason
      })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      closeModal('modal-adjust-stock');
      showToast(data.message, 'success');
      fetchInventoryItems();
      loadKPIStats();
    } else {
      errEl.textContent = data.detail || 'Không thể cập nhật số lượng tồn kho.';
      errEl.classList.remove('hidden');
    }
  } catch (err) {
    errEl.textContent = 'Lỗi kết nối máy chủ.';
    errEl.classList.remove('hidden');
  }
};

// Add New Item Modal
window.openAddInventoryModal = function() {
  document.getElementById('add-inv-code').value = '';
  document.getElementById('add-inv-name').value = '';
  document.getElementById('add-inv-spec').value = '';
  document.getElementById('add-inv-unit').value = 'Hộp';
  document.getElementById('add-inv-mfg').value = '';
  document.getElementById('add-inv-lot').value = '';
  document.getElementById('add-inv-exp').value = '';
  document.getElementById('add-inv-qty').value = '0';
  document.getElementById('add-inv-min').value = '5';
  document.getElementById('add-inv-usage').value = '10';
  document.getElementById('add-inv-price').value = '0';
  document.getElementById('add-inv-location').value = 'Tủ lạnh 2-8°C';
  document.getElementById('add-inv-error').classList.add('hidden');
  openModal('modal-add-inventory-item');
};

window.submitAddInventoryItem = async function() {
  const code = document.getElementById('add-inv-code').value.trim();
  const name = document.getElementById('add-inv-name').value.trim();
  const category = document.getElementById('add-inv-cat').value;
  const spec = document.getElementById('add-inv-spec').value.trim();
  const unit = document.getElementById('add-inv-unit').value.trim();
  const manufacturer = document.getElementById('add-inv-mfg').value.trim();
  const lot_number = document.getElementById('add-inv-lot').value.trim();
  const expiry_date = document.getElementById('add-inv-exp').value;
  const storage_temp = document.getElementById('add-inv-temp').value;
  const quantity = parseFloat(document.getElementById('add-inv-qty').value || 0);
  const min_stock = parseFloat(document.getElementById('add-inv-min').value || 0);
  const monthly_usage = parseFloat(document.getElementById('add-inv-usage').value || 0);
  const unit_price = parseFloat(document.getElementById('add-inv-price').value || 0);
  const location = document.getElementById('add-inv-location').value.trim();
  const notes = document.getElementById('add-inv-notes').value.trim();
  const errEl = document.getElementById('add-inv-error');

  if (!code || !name) {
    errEl.textContent = 'Vui lòng nhập đầy đủ Mã hàng và Tên mặt hàng.';
    errEl.classList.remove('hidden');
    return;
  }

  try {
    const res = await fetch('/api/inventory/items', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code, name, category, spec, unit, manufacturer, lot_number,
        expiry_date, storage_temp, quantity, min_stock, monthly_usage,
        unit_price, location, notes
      })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      closeModal('modal-add-inventory-item');
      showToast(data.message, 'success');
      fetchInventoryItems();
      loadKPIStats();
    } else {
      errEl.textContent = data.detail || 'Không thể thêm mặt hàng.';
      errEl.classList.remove('hidden');
    }
  } catch (err) {
    errEl.textContent = 'Lỗi kết nối máy chủ.';
    errEl.classList.remove('hidden');
  }
};

// Edit Existing Item Modal
window.openEditItemModal = function(itemId) {
  const item = inventoryState.items.find(i => i.id === itemId);
  if (!item) return;

  inventoryState.selectedItemForEdit = item;
  document.getElementById('edit-inv-id').value = item.id;
  document.getElementById('edit-inv-name').value = item.name || '';
  document.getElementById('edit-inv-code-display').textContent = item.code || '';
  document.getElementById('edit-inv-cat').value = item.category || 'hoa_chat';
  document.getElementById('edit-inv-spec').value = item.spec || '';
  document.getElementById('edit-inv-unit').value = item.unit || 'Hộp';
  document.getElementById('edit-inv-mfg').value = item.manufacturer || '';
  document.getElementById('edit-inv-lot').value = item.lot_number || '';
  document.getElementById('edit-inv-exp').value = item.expiry_date || '';
  document.getElementById('edit-inv-temp').value = item.storage_temp || '2-8°C';
  document.getElementById('edit-inv-qty').value = item.quantity ?? 0;
  document.getElementById('edit-inv-min').value = item.min_stock ?? 0;
  document.getElementById('edit-inv-usage').value = item.monthly_usage ?? 0;
  document.getElementById('edit-inv-price').value = item.unit_price ?? 0;
  document.getElementById('edit-inv-open-date').value = item.open_date || '';
  document.getElementById('edit-inv-location').value = item.location || '';
  document.getElementById('edit-inv-notes').value = item.notes || '';
  document.getElementById('edit-inv-error').classList.add('hidden');

  openModal('modal-edit-inventory-item');
};

window.submitEditInventoryItem = async function() {
  const id = document.getElementById('edit-inv-id').value;
  const name = document.getElementById('edit-inv-name').value.trim();
  const category = document.getElementById('edit-inv-cat').value;
  const spec = document.getElementById('edit-inv-spec').value.trim();
  const unit = document.getElementById('edit-inv-unit').value.trim();
  const manufacturer = document.getElementById('edit-inv-mfg').value.trim();
  const lot_number = document.getElementById('edit-inv-lot').value.trim();
  const expiry_date = document.getElementById('edit-inv-exp').value;
  const storage_temp = document.getElementById('edit-inv-temp').value;
  const quantity = parseFloat(document.getElementById('edit-inv-qty').value || 0);
  const min_stock = parseFloat(document.getElementById('edit-inv-min').value || 0);
  const monthly_usage = parseFloat(document.getElementById('edit-inv-usage').value || 0);
  const unit_price = parseFloat(document.getElementById('edit-inv-price').value || 0);
  const open_date = document.getElementById('edit-inv-open-date').value;
  const location = document.getElementById('edit-inv-location').value.trim();
  const notes = document.getElementById('edit-inv-notes').value.trim();
  const errEl = document.getElementById('edit-inv-error');

  try {
    const res = await fetch(`/api/inventory/items/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name, category, spec, unit, manufacturer, lot_number,
        expiry_date, storage_temp, quantity, min_stock, monthly_usage,
        unit_price, open_date, location, notes
      })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      closeModal('modal-edit-inventory-item');
      showToast(data.message, 'success');
      fetchInventoryItems();
    } else {
      errEl.textContent = data.detail || 'Không thể cập nhật mặt hàng.';
      errEl.classList.remove('hidden');
    }
  } catch (err) {
    errEl.textContent = 'Lỗi kết nối máy chủ.';
    errEl.classList.remove('hidden');
  }
};

window.deleteCurrentInventoryItem = async function() {
  if (!inventoryState.selectedItemForEdit) return;
  const id = inventoryState.selectedItemForEdit.id;
  const name = inventoryState.selectedItemForEdit.name;

  if (!confirm(`Bạn có chắc chắn muốn xóa mặt hàng "${name}" khỏi kho?`)) return;

  try {
    const res = await fetch(`/api/inventory/items/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (res.ok && data.success) {
      closeModal('modal-edit-inventory-item');
      showToast(data.message, 'info');
      fetchInventoryItems();
      loadKPIStats();
    } else {
      alert(data.detail || 'Lỗi khi xóa mặt hàng.');
    }
  } catch (err) {
    alert('Lỗi kết nối máy chủ.');
  }
};

/* ==========================================================================
   MỤC 2: DỰ TRÙ HÓA CHẤT & VẬT TƯ TIÊU HAO (KẾ HOẠCH DỰ TRÙ & THEO DÕI NỢ DƯỢC)
   ========================================================================== */

function initForecastDraft() {
  // Build forecast list automatically from items in stock
  const items = inventoryState.items;
  if (!items || items.length === 0) return;

  inventoryState.forecastItems = items.map(item => {
    const qty = parseFloat(item.quantity || 0);
    const usage = parseFloat(item.monthly_usage || 0);
    const suggested = parseFloat(item.suggested_order || 0);
    const orderQty = suggested > 0 ? suggested : (item.is_low_stock ? Math.max(1, item.min_stock - qty) : 0);
    const price = parseFloat(item.unit_price || 0);
    const receivedQty = item.received_qty !== undefined ? parseFloat(item.received_qty) : (orderQty > 0 ? 0 : 0);
    const debtQty = Math.max(0, orderQty - receivedQty);

    return {
      id: item.id,
      code: item.code,
      name: item.name,
      category: item.category,
      unit: item.unit,
      current_stock: qty,
      monthly_usage: usage,
      suggested_qty: suggested,
      order_qty: orderQty,
      received_qty: receivedQty,
      debt_qty: debtQty,
      debt_notes: item.debt_notes || '',
      unit_price: price,
      total_cost: orderQty * price,
      notes: item.is_low_stock ? 'Kho sắp hết hàng' : (suggested > 0 ? 'Bổ sung định kỳ' : 'Dự phòng')
    };
  });

  renderForecastTable();
}

function renderForecastTable() {
  const tbody = document.getElementById('forecast-items-tbody');
  const totalCostEl = document.getElementById('forecast-total-cost-text');
  if (!tbody) return;

  const isAdmin = currentUser && (currentUser.role === 'truong_khoa' || currentUser.role === 'ktv_truong');

  // Toggle admin buttons in forecast toolbar
  const btnAuto = document.getElementById('btn-forecast-autocalc');
  const btnSave = document.getElementById('btn-forecast-save');
  if (btnAuto) btnAuto.classList.toggle('hidden', !isAdmin);
  if (btnSave) btnSave.classList.toggle('hidden', !isAdmin);

  let totalCost = 0;
  let totalWithOrder = 0;
  let fullySupplied = 0;
  let debtItems = 0;
  let html = '';

  inventoryState.forecastItems.forEach((fItem, idx) => {
    const lineTotal = fItem.order_qty * fItem.unit_price;
    fItem.total_cost = lineTotal;
    totalCost += lineTotal;

    const isOrdering = fItem.order_qty > 0;
    if (isOrdering) {
      totalWithOrder++;
      if (fItem.debt_qty > 0) debtItems++;
      else fullySupplied++;
    }

    const isDebt = fItem.debt_qty > 0;
    const isFull = isOrdering && fItem.debt_qty === 0;

    let debtBadge = '<span class="text-slate-400 font-mono">--</span>';
    if (isDebt) {
      debtBadge = `<span class="px-2 py-0.5 rounded text-[11px] font-black bg-red-100 text-red-700 border border-red-300 animate-pulse whitespace-nowrap">⚠️ Nợ ${fItem.debt_qty} ${fItem.unit}</span>`;
    } else if (isFull) {
      debtBadge = `<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300 whitespace-nowrap">✅ Đủ hàng</span>`;
    }

    let actionBtn = '<span class="text-slate-300 font-mono text-center block">--</span>';
    if (isDebt && isAdmin) {
      actionBtn = `
        <button onclick="openResolveDebtModal('${fItem.code}')" class="px-2 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-[11px] font-bold shadow-xs transition flex items-center justify-center gap-1 w-full" title="Kho Dược phát bù hàng nợ đợt tiếp theo">
          <span>⚡ Nhận bù</span>
        </button>
      `;
    }

    html += `
      <tr class="${isDebt ? 'bg-red-50/30' : (isOrdering ? 'bg-amber-50/30 font-medium' : 'text-slate-600')} hover:bg-slate-50 transition border-b border-slate-100 text-xs">
        <td class="p-2.5 text-center font-mono text-slate-400">${idx + 1}</td>
        <td class="p-2.5 font-mono font-bold text-slate-800">${fItem.code}</td>
        <td class="p-2.5 font-bold text-slate-900">${fItem.name}</td>
        <td class="p-2.5 text-center font-semibold text-slate-700">${fItem.unit}</td>
        <td class="p-2.5 text-right font-mono text-slate-700">${fItem.current_stock}</td>
        <td class="p-2.5 text-right font-mono text-slate-700">${fItem.monthly_usage}</td>
        <td class="p-2.5 text-right font-mono font-bold text-sky-800">${fItem.suggested_qty}</td>
        
        <!-- Editable Order Quantity (Khoa Dự Trù) -->
        <td class="p-1.5 text-center bg-amber-50/50">
          <input type="number" min="0" step="1" value="${fItem.order_qty}" 
                 ${isAdmin ? '' : 'disabled title="Chỉ Trưởng khoa / KTV trưởng mới có quyền sửa số lượng dự trù"'}
                 onchange="updateForecastItemQty(${idx}, this.value)"
                 class="w-20 text-center p-1.5 bg-white border ${isOrdering ? 'border-amber-400 font-bold text-amber-900 ring-2 ring-amber-100' : 'border-slate-300 text-slate-700'} rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-sky-600 ${isAdmin ? '' : 'opacity-70 cursor-not-allowed'}">
        </td>

        <!-- Editable Received Quantity (Dược Thực Cấp) -->
        <td class="p-1.5 text-center bg-blue-50/50">
          <input type="number" min="0" step="1" value="${fItem.received_qty}" 
                 ${isAdmin ? '' : 'disabled'}
                 onchange="updateForecastItemReceived(${idx}, this.value)"
                 class="w-20 text-center p-1.5 bg-white border border-blue-300 font-bold text-blue-900 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-blue-600 ${isAdmin ? '' : 'opacity-70 cursor-not-allowed'}"
                 title="Số lượng Dược đã thực tế cấp phát">
        </td>

        <!-- Dược Còn Nợ -->
        <td class="p-2 text-center bg-red-50/30">
          ${debtBadge}
        </td>

        <!-- Editable Unit Price -->
        <td class="p-1.5 text-right">
          <input type="number" min="0" step="1000" value="${fItem.unit_price}" 
                 ${isAdmin ? '' : 'disabled'}
                 onchange="updateForecastItemPrice(${idx}, this.value)"
                 class="w-24 text-right p-1.5 bg-white border border-slate-300 rounded-lg text-xs font-mono focus:outline-none focus:ring-2 focus:ring-sky-600 ${isAdmin ? '' : 'opacity-70 cursor-not-allowed'}">
        </td>

        <!-- Thành tiền -->
        <td class="p-2.5 text-right font-mono font-bold ${isOrdering ? 'text-red-700' : 'text-slate-400'}">
          ${lineTotal.toLocaleString('vi-VN')} đ
        </td>

        <!-- Ghi chú nợ / Hẹn phát sau -->
        <td class="p-1.5">
          <input type="text" value="${fItem.debt_notes || fItem.notes || ''}" 
                 ${isAdmin ? '' : 'disabled'}
                 onchange="updateForecastItemNotes(${idx}, this.value)"
                 placeholder="Lý do nợ / Ngày hẹn phát sau..."
                 class="w-full p-1.5 bg-white border border-slate-200 rounded-lg text-[11px] text-slate-700 focus:outline-none focus:ring-2 focus:ring-sky-600 ${isAdmin ? '' : 'opacity-70 cursor-not-allowed'}">
        </td>

        <!-- Thao tác nhận bù -->
        <td class="p-1.5 text-center">
          ${actionBtn}
        </td>
      </tr>
    `;
  });

  tbody.innerHTML = html;
  if (totalCostEl) {
    totalCostEl.textContent = `${totalCost.toLocaleString('vi-VN')} VNĐ`;
  }

  // Update Debt KPI summary
  const kpiTotalEl = document.getElementById('forecast-kpi-total-items');
  const kpiFullEl = document.getElementById('forecast-kpi-fully-supplied');
  const kpiDebtEl = document.getElementById('forecast-kpi-debt-items');
  if (kpiTotalEl) kpiTotalEl.textContent = `${totalWithOrder} Mặt Hàng`;
  if (kpiFullEl) kpiFullEl.textContent = `${fullySupplied} Mặt Hàng`;
  if (kpiDebtEl) kpiDebtEl.textContent = `${debtItems} Mặt Hàng`;
}

window.updateForecastItemQty = function(idx, val) {
  const qty = parseFloat(val || 0);
  if (inventoryState.forecastItems[idx]) {
    inventoryState.forecastItems[idx].order_qty = Math.max(0, qty);
    const rec = inventoryState.forecastItems[idx].received_qty || 0;
    inventoryState.forecastItems[idx].debt_qty = Math.max(0, inventoryState.forecastItems[idx].order_qty - rec);
    renderForecastTable();
  }
};

window.updateForecastItemReceived = function(idx, val) {
  const rec = parseFloat(val || 0);
  if (inventoryState.forecastItems[idx]) {
    inventoryState.forecastItems[idx].received_qty = Math.max(0, rec);
    inventoryState.forecastItems[idx].debt_qty = Math.max(0, inventoryState.forecastItems[idx].order_qty - inventoryState.forecastItems[idx].received_qty);
    renderForecastTable();
  }
};

window.updateForecastItemPrice = function(idx, val) {
  const price = parseFloat(val || 0);
  if (inventoryState.forecastItems[idx]) {
    inventoryState.forecastItems[idx].unit_price = Math.max(0, price);
    renderForecastTable();
  }
};

window.updateForecastItemNotes = function(idx, val) {
  if (inventoryState.forecastItems[idx]) {
    inventoryState.forecastItems[idx].debt_notes = val.trim();
    inventoryState.forecastItems[idx].notes = val.trim();
  }
};

window.openResolveDebtModal = function(itemCode) {
  const item = inventoryState.forecastItems.find(i => i.code === itemCode);
  if (!item) return;

  window.currentResolveDebtItem = item;
  document.getElementById('resolve-debt-item-name').textContent = `${item.code} - ${item.name} (${item.unit})`;
  document.getElementById('resolve-debt-current-debt').textContent = `${item.debt_qty} ${item.unit}`;
  document.getElementById('resolve-debt-stock-qty').textContent = `${item.current_stock} ${item.unit}`;
  document.getElementById('resolve-debt-qty').value = item.debt_qty;
  document.getElementById('resolve-debt-qty').max = item.debt_qty;
  document.getElementById('resolve-debt-notes').value = '';
  document.getElementById('resolve-debt-error').classList.add('hidden');

  openModal('modal-resolve-debt');
};

window.submitResolveDebt = async function() {
  if (!window.currentResolveDebtItem) return;
  const item = window.currentResolveDebtItem;
  const returnQty = parseFloat(document.getElementById('resolve-debt-qty').value || 0);
  const notes = document.getElementById('resolve-debt-notes').value.trim();
  const errEl = document.getElementById('resolve-debt-error');

  if (returnQty <= 0) {
    errEl.textContent = 'Số lượng nhận bù phải lớn hơn 0.';
    errEl.classList.remove('hidden');
    return;
  }

  try {
    const res = await fetch('/api/inventory/forecasts/resolve-debt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        forecast_id: 1,
        item_code: item.code,
        return_qty: returnQty,
        notes: notes
      })
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      errEl.textContent = data.detail || 'Không thể ghi nhận hàng bù.';
      errEl.classList.remove('hidden');
      return;
    }

    closeModal('modal-resolve-debt');
    showToast(data.message, 'success');

    // Cập nhật số liệu local
    item.received_qty = (item.received_qty || 0) + returnQty;
    item.debt_qty = Math.max(0, item.order_qty - item.received_qty);
    item.current_stock += returnQty;
    renderForecastTable();

    // Tải lại tồn kho thực tế
    fetchInventoryItems();
  } catch (err) {
    errEl.textContent = 'Lỗi kết nối máy chủ.';
    errEl.classList.remove('hidden');
  }
};

window.autoCalculateForecast = function() {
  initForecastDraft();
  showToast('Đã tính toán xong số lượng đề xuất dự trù căn cứ trên tồn kho và lượng tiêu hao.', 'success');
};

window.saveForecastPlan = async function() {
  const period = document.getElementById('forecast-period-select').value;
  const filteredItems = inventoryState.forecastItems.filter(i => i.order_qty > 0);

  if (filteredItems.length === 0) {
    alert('Chưa có mặt hàng nào có số lượng dự trù > 0. Vui lòng nhập số lượng cần mua.');
    return;
  }

  try {
    const res = await fetch('/api/inventory/forecasts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        period: period,
        title: `Bảng Dự Trù Hóa Chất & Vật Tư - ${period}`,
        items: filteredItems,
        notes: `Lập ngày ${new Date().toLocaleDateString('vi-VN')} bởi Khoa Xét Nghiệm BVĐK Thiên Ân.`
      })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(data.message, 'success');
    } else {
      alert(data.detail || 'Không thể lưu bảng dự trù.');
    }
  } catch (err) {
    alert('Lỗi kết nối máy chủ.');
  }
};

// Official Printable Forecast Sheet (Chuẩn Thể Thức Y Tế A4 BVĐK Thiên Ân)
window.printOfficialForecastForm = function() {
  const period = document.getElementById('forecast-period-select').value;
  const filteredItems = inventoryState.forecastItems.filter(i => i.order_qty > 0);

  if (filteredItems.length === 0) {
    alert('Vui lòng nhập số lượng dự trù cho ít nhất 1 mặt hàng trước khi in phiếu.');
    return;
  }

  const container = document.getElementById('print-forecast-container');
  if (!container) return;

  let totalCost = 0;
  let rowsHtml = '';
  filteredItems.forEach((item, idx) => {
    const lineTotal = item.order_qty * item.unit_price;
    totalCost += lineTotal;
    const recQty = item.received_qty !== undefined ? item.received_qty : 0;
    const debtQty = item.debt_qty !== undefined ? item.debt_qty : Math.max(0, item.order_qty - recQty);

    rowsHtml += `
      <tr style="border-bottom: 1px solid #cbd5e1; font-size: 9.5pt;">
        <td style="padding: 5px; text-align: center; font-family: monospace;">${idx + 1}</td>
        <td style="padding: 5px; font-family: monospace; font-weight: bold;">${item.code}</td>
        <td style="padding: 5px; font-weight: bold; text-align: left;">${item.name}</td>
        <td style="padding: 5px; text-align: center;">${item.unit}</td>
        <td style="padding: 5px; text-align: right; font-family: monospace;">${item.current_stock}</td>
        <td style="padding: 5px; text-align: right; font-family: monospace; font-weight: bold; color: #1e3a8a;">${item.order_qty}</td>
        <td style="padding: 5px; text-align: right; font-family: monospace; color: #0f766e;">${recQty}</td>
        <td style="padding: 5px; text-align: right; font-family: monospace; font-weight: bold; color: ${debtQty > 0 ? '#b91c1c' : '#166534'};">
          ${debtQty > 0 ? `${debtQty} (Nợ)` : 'Đủ'}
        </td>
        <td style="padding: 5px; text-align: right; font-family: monospace;">${item.unit_price.toLocaleString('vi-VN')} đ</td>
        <td style="padding: 5px; text-align: right; font-family: monospace; font-weight: bold; color: #b91c1c;">${lineTotal.toLocaleString('vi-VN')} đ</td>
        <td style="padding: 5px; font-size: 8.5pt;">${item.debt_notes || item.notes || 'Dự trù định kỳ'}</td>
      </tr>
    `;
  });

  const now = new Date();
  const dateStr = `Vĩnh Long, ngày ${now.getDate()} tháng ${now.getMonth() + 1} năm ${now.getFullYear()}`;

  container.innerHTML = `
    <div style="font-family: 'Times New Roman', Times, serif; color: #000; line-height: 1.4; padding: 25px 35px;">
      <!-- Header -->
      <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
        <tr>
          <td style="width: 13%; text-align: center; vertical-align: middle;">
            <img src="/static/img/logo_thien_an.png" style="width: 70px; height: 70px; object-fit: contain;" alt="Logo BV Thiên Ân">
          </td>
          <td style="width: 45%; text-align: left; vertical-align: middle; padding-left: 8px;">
            <div style="font-size: 10pt; font-weight: bold; color: #334155;">SỞ Y TẾ TỈNH VĨNH LONG</div>
            <div style="font-size: 11pt; font-weight: bold; color: #0369a1; text-transform: uppercase;">BỆNH VIỆN ĐA KHOA THIÊN ÂN - VIỄN ĐÔNG</div>
            <div style="font-size: 10pt; font-weight: bold; color: #0f766e;">KHOA XÉT NGHIỆM</div>
            <div style="font-size: 9pt; font-style: italic; margin-top: 1px;">Mã biểu mẫu: BM.HC.01 / BVĐK Thiên Ân</div>
          </td>
          <td style="width: 42%; text-align: center; vertical-align: middle;">
            <div style="font-size: 10.5pt; font-weight: bold;">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
            <div style="font-size: 10.5pt; font-weight: bold;">Độc lập - Tự do - Hạnh phúc</div>
            <div style="margin: 3px auto; width: 120px; border-bottom: 1.5px solid #000;"></div>
            <div style="font-size: 10pt; font-style: italic; margin-top: 4px;">${dateStr}</div>
          </td>
        </tr>
      </table>

      <!-- Document Title -->
      <div style="text-align: center; margin: 25px 0 15px 0;">
        <h2 style="font-size: 14.5pt; font-weight: bold; margin: 0; text-transform: uppercase; color: #1e3a8a;">
          BẢNG DỰ TRÙ & THEO DÕI NỢ HÓA CHẤT, SINH PHẨM, VẬT TƯ
        </h2>
        <div style="font-size: 11pt; font-weight: bold; margin-top: 4px; color: #334155;">
          KỲ DỰ TRÙ: ${period.toUpperCase()}
        </div>
        <div style="font-size: 10pt; font-style: italic; margin-top: 3px; color: #475569;">
          (Kính gửi: Ban Giám Đốc • Kho Dược / Phòng Vật tư - TBYT • Phòng Tài chính Kế toán)
        </div>
      </div>

      <!-- Intro paragraph -->
      <p style="font-size: 10.5pt; text-indent: 25px; margin: 12px 0; text-align: justify;">
        Căn cứ vào cơ số bệnh nhân xét nghiệm thực tế và lượng tồn kho hiện có tính đến ngày ${now.getDate()}/${now.getMonth() + 1}/${now.getFullYear()}; Khoa Xét nghiệm kính đề nghị Ban Giám đốc, Kho Dược và các phòng chức năng xem xét phê duyệt cấp phát các mặt hàng hóa chất, sinh phẩm và vật tư tiêu hao. Các mặt hàng Kho Dược chưa có sẵn sẽ được <b>ghi nhận nợ lại và phát bù sau</b> theo đúng thỏa thuận:
      </p>

      <!-- Table -->
      <table style="width: 100%; border-collapse: collapse; margin: 15px 0; border: 1.5px solid #000;">
        <thead>
          <tr style="background-color: #f1f5f9; border-bottom: 1.5px solid #000; font-size: 9pt; font-weight: bold; text-transform: uppercase;">
            <th style="padding: 6px 3px; border: 1px solid #cbd5e1; width: 30px; text-align: center;">STT</th>
            <th style="padding: 6px 4px; border: 1px solid #cbd5e1; width: 65px; text-align: center;">Mã Hàng</th>
            <th style="padding: 6px 5px; border: 1px solid #cbd5e1; text-align: left;">Tên Hóa Chất / Sinh Phẩm / Vật Tư</th>
            <th style="padding: 6px 3px; border: 1px solid #cbd5e1; width: 45px; text-align: center;">ĐVT</th>
            <th style="padding: 6px 3px; border: 1px solid #cbd5e1; width: 45px; text-align: right;">Tồn Kho</th>
            <th style="padding: 6px 4px; border: 1px solid #cbd5e1; width: 50px; text-align: right; color: #1e3a8a;">SL Dự Trù</th>
            <th style="padding: 6px 4px; border: 1px solid #cbd5e1; width: 50px; text-align: right; color: #0f766e;">Thực Cấp</th>
            <th style="padding: 6px 4px; border: 1px solid #cbd5e1; width: 50px; text-align: right; color: #b91c1c;">Dược Nợ</th>
            <th style="padding: 6px 4px; border: 1px solid #cbd5e1; width: 85px; text-align: right;">Đơn Giá (đ)</th>
            <th style="padding: 6px 5px; border: 1px solid #cbd5e1; width: 95px; text-align: right; color: #b91c1c;">Thành Tiền</th>
            <th style="padding: 6px 4px; border: 1px solid #cbd5e1; width: 85px; text-align: left;">Ghi Chú Nợ</th>
          </tr>
        </thead>
        <tbody>
          ${rowsHtml}
          <!-- Sum row -->
          <tr style="background-color: #fef2f2; border-top: 1.5px solid #000; font-weight: bold; font-size: 9.5pt;">
            <td colspan="9" style="padding: 8px; text-align: right; text-transform: uppercase;">TỔNG CỘNG KINH PHÍ DỰ TRÙ:</td>
            <td style="padding: 8px; text-align: right; font-family: monospace; color: #b91c1c; font-size: 10pt;">${totalCost.toLocaleString('vi-VN')} VNĐ</td>
            <td></td>
          </tr>
        </tbody>
      </table>

      <!-- Signatures Block with Pharmacy Debt Acknowledgement -->
      <table style="width: 100%; border-collapse: collapse; margin-top: 25px; text-align: center; page-break-inside: avoid;">
        <tr style="font-size: 10pt; font-weight: bold;">
          <td style="width: 20%; vertical-align: top;">NGƯỜI LẬP DỰ TRÙ</td>
          <td style="width: 20%; vertical-align: top;">KỸ THUẬT VIÊN TRƯỞNG</td>
          <td style="width: 20%; vertical-align: top;">TRƯỞNG KHOA XÉT NGHIỆM</td>
          <td style="width: 20%; vertical-align: top; color: #b91c1c;">KHO DƯỢC XÁC NHẬN NỢ</td>
          <td style="width: 20%; vertical-align: top;">BAN GIÁM ĐỐC</td>
        </tr>
        <tr style="font-size: 8.5pt; font-style: italic; color: #475569;">
          <td>(Ký và ghi rõ họ tên)</td>
          <td>(Ký và ghi rõ họ tên)</td>
          <td>(Ký và ghi rõ họ tên)</td>
          <td>(Ký nhận các mục nợ)</td>
          <td>(Phê duyệt)</td>
        </tr>
        <tr style="height: 60px;">
          <td></td>
          <td></td>
          <td></td>
          <td></td>
          <td></td>
        </tr>
        <tr style="font-size: 10pt; font-weight: bold;">
          <td>CN. Tống Mọng Tiền</td>
          <td>CN. Nguyễn Trường Duy</td>
          <td>CN. Lê Đình Tú</td>
          <td>..................................</td>
          <td>BAN GIÁM ĐỐC</td>
        </tr>
      </table>
    </div>
  `;

  openModal('modal-print-forecast');
};

window.executePrintForecast = function() {
  window.print();
};

/* ==========================================================================
   MỤC 3: QUẢN LÝ HẠN MỞ NẮP LỌ (IN-USE STABILITY / OPEN-VIALS)
   ========================================================================== */

let openVialsState = {
  statusFilter: 'active',
  searchQuery: '',
  vials: []
};

let vialSearchTimer = null;
window.debounceVialsSearch = function() {
  clearTimeout(vialSearchTimer);
  vialSearchTimer = setTimeout(() => {
    const input = document.getElementById('vials-search-input');
    openVialsState.searchQuery = input ? input.value.trim() : '';
    fetchOpenVials();
  }, 300);
};

window.setVialsFilter = function(filter) {
  openVialsState.statusFilter = filter;
  const filterBtns = ['active', 'warning', 'expired', 'finished', 'all'];
  filterBtns.forEach(f => {
    const btn = document.getElementById(`vials-filter-${f}`);
    if (!btn) return;
    if (f === filter) {
      btn.className = "px-3 py-1.5 rounded-xl font-bold text-xs bg-sky-700 text-white shadow-xs transition";
    } else {
      btn.className = "px-3 py-1.5 rounded-xl font-semibold text-xs text-slate-600 hover:text-sky-700 hover:bg-sky-50 border border-slate-200 transition";
    }
  });
  fetchOpenVials();
};

async function fetchOpenVials() {
  const tbody = document.getElementById('open-vials-tbody');
  if (!tbody) return;

  tbody.innerHTML = `
    <tr>
      <td colspan="11" class="p-8 text-center text-slate-500">
        <div class="animate-spin inline-block w-6 h-6 border-3 border-sky-600 border-t-transparent rounded-full mb-2"></div>
        <div>Đang tải danh sách lọ hóa chất mở nắp...</div>
      </td>
    </tr>
  `;

  try {
    let url = `/api/inventory/open-vials?status_filter=${openVialsState.statusFilter}`;
    if (openVialsState.searchQuery) {
      url += `&q=${encodeURIComponent(openVialsState.searchQuery)}`;
    }

    const res = await fetch(url);
    if (!res.ok) throw new Error('Không thể tải danh sách lọ mở nắp');
    const data = await res.json();

    const stats = data.stats || {};
    const statActive = document.getElementById('vials-stat-active');
    const statSafe = document.getElementById('vials-stat-safe');
    const statWarning = document.getElementById('vials-stat-warning');
    const statExpired = document.getElementById('vials-stat-expired');

    if (statActive) statActive.textContent = `${stats.total_active || 0} Lọ`;
    if (statSafe) statSafe.textContent = `${stats.safe_count || 0} Lọ`;
    if (statWarning) statWarning.textContent = `${stats.warning_count || 0} Lọ`;
    if (statExpired) statExpired.textContent = `${stats.expired_count || 0} Lọ`;

    openVialsState.vials = data.vials || [];
    renderOpenVialsTable(openVialsState.vials);
  } catch (err) {
    console.error('fetchOpenVials error:', err);
    tbody.innerHTML = '<tr><td colspan="11" class="p-8 text-center text-red-500 font-bold">Lỗi kết nối tải danh sách lọ mở nắp.</td></tr>';
  }
}

function renderOpenVialsTable(vials) {
  const tbody = document.getElementById('open-vials-tbody');
  if (!tbody) return;

  if (!vials || vials.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="11" class="p-8 text-center text-slate-400">
          <div class="text-3xl mb-2">🧪</div>
          <div class="font-bold text-slate-600">Không có lọ hóa chất nào phù hợp bộ lọc</div>
          <div class="text-[11px] text-slate-400 mt-1">Nhấn "+ Ghi Nhận Mở Lọ" để thêm lọ hóa chất đưa vào máy</div>
        </td>
      </tr>
    `;
    return;
  }

  let html = '';
  vials.forEach((v, idx) => {
    const isFinished = (v.status === 'finished');
    const isDiscarded = (v.status === 'discarded');
    const isActive = (v.status === 'active');

    // Status badge & progress color
    let statusBadge = '';
    let progressColor = 'bg-emerald-500';
    let countdownBadge = '';

    if (isFinished) {
      statusBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">Đã dùng hết</span>';
      countdownBadge = '<span class="text-slate-400 font-medium">Hoàn tất</span>';
    } else if (isDiscarded) {
      statusBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-gray-200 text-gray-800">Đã hủy bỏ</span>';
      countdownBadge = `<span class="text-red-500 font-medium text-[10px]">${v.discard_reason || 'Đã hủy'}</span>`;
    } else {
      // Active
      if (v.vial_status === 'expired') {
        statusBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-800 border border-red-200 animate-pulse">Quá hạn mở</span>';
        countdownBadge = `<span class="text-red-600 font-black">Quá hạn ${Math.abs(v.days_left)} ngày!</span>`;
        progressColor = 'bg-red-600';
      } else if (v.vial_status === 'warning') {
        statusBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200">Cận hạn mở</span>';
        countdownBadge = `<span class="text-amber-700 font-bold">Còn ${v.days_left} ngày</span>`;
        progressColor = 'bg-amber-500';
      } else {
        statusBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">Đang dùng tốt</span>';
        countdownBadge = `<span class="text-emerald-700 font-bold">Còn ${v.days_left} ngày</span>`;
        progressColor = 'bg-emerald-500';
      }
    }

    const rowBg = (idx % 2 === 0) ? 'bg-white' : 'bg-slate-50/50';

    html += `
      <tr class="${rowBg} hover:bg-sky-50/40 transition border-b border-slate-100 text-slate-800">
        <td class="p-2.5 text-center font-bold text-slate-400">${idx + 1}</td>
        <td class="p-2.5">
          <div class="font-bold text-slate-900">${v.item_name}</div>
          <div class="text-[11px] text-slate-400 font-mono">${v.item_code}</div>
        </td>
        <td class="p-2.5">
          <div class="font-mono font-bold text-sky-800">${v.lot_number || 'LOT--'}</div>
          <div class="text-[11px] text-slate-500">${v.vial_label || 'Lọ 01'}</div>
        </td>
        <td class="p-2.5">
          <span class="inline-block px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[11px] font-medium border border-slate-200">${v.location || 'Máy sinh hóa'}</span>
        </td>
        <td class="p-2.5 text-center">
          <div class="font-mono font-bold">${v.open_date}</div>
          <div class="text-[10px] text-slate-400">${v.open_time || '08:00'}</div>
        </td>
        <td class="p-2.5 text-center font-bold text-slate-600">
          ${v.stability_days} ngày
        </td>
        <td class="p-2.5 text-center">
          <div class="font-mono font-black ${v.vial_status === 'expired' && isActive ? 'text-red-600' : 'text-slate-800'}">${v.expiry_date}</div>
        </td>
        <td class="p-2.5">
          <div class="flex items-center justify-between text-[11px] mb-1">
            ${countdownBadge}
            <span class="text-slate-400 text-[10px]">${v.used_days || 0}/${v.stability_days}d</span>
          </div>
          <div class="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
            <div class="${progressColor} h-1.5 rounded-full" style="width: ${v.progress_pct || 0}%"></div>
          </div>
        </td>
        <td class="p-2.5">
          <div class="font-semibold text-slate-700">${v.opened_by_name || 'KTV'}</div>
        </td>
        <td class="p-2.5 text-center">
          ${statusBadge}
        </td>
        <td class="p-2.5 text-center">
          <div class="flex items-center justify-center gap-1.5">
            <button onclick="openPrintVialLabelModal(${v.id})" title="In tem nhãn dán lọ mini"
                    class="p-1.5 bg-sky-50 hover:bg-sky-100 text-sky-700 rounded-lg border border-sky-200 transition">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/></svg>
            </button>
            ${isActive ? `
            <button onclick="openFinishVialModal(${v.id}, '${v.item_name.replace(/'/g, "\\'")}', '${v.lot_number || ''}', '${v.open_date}')" 
                    title="Đánh dấu đã dùng hết hoặc hủy lọ"
                    class="px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-[11px] font-bold border border-slate-200 transition">
              Kết thúc
            </button>
            ` : ''}
          </div>
        </td>
      </tr>
    `;
  });

  tbody.innerHTML = html;
}

// Open modal for registering new vial
window.openAddVialModal = function() {
  const errBox = document.getElementById('aov-error');
  if (errBox) errBox.classList.add('hidden');

  const todayStr = new Date().toISOString().split('T')[0];
  const timeNow = new Date().toTimeString().slice(0, 5);

  const dateInput = document.getElementById('aov-date');
  const timeInput = document.getElementById('aov-time');
  const daysInput = document.getElementById('aov-days');

  if (dateInput) dateInput.value = todayStr;
  if (timeInput) timeInput.value = timeNow;
  if (daysInput) daysInput.value = 30;

  // Populate item dropdown from inventory items
  const select = document.getElementById('aov-item-select');
  if (select) {
    let opts = '<option value="">-- Chọn mặt hàng từ kho (hoặc nhập bên dưới) --</option>';
    if (inventoryState.items && inventoryState.items.length > 0) {
      inventoryState.items.forEach(it => {
        opts += `<option value="${it.id}" data-code="${it.code}" data-name="${it.name}" data-lot="${it.lot_number || ''}" data-spec="${it.spec || ''}">[${it.code}] ${it.name} (Lô: ${it.lot_number || 'N/A'})</option>`;
      });
    }
    select.innerHTML = opts;
  }

  calcVialExpiry();
  openModal('modal-add-open-vial');
};

window.onOpenVialItemSelected = function() {
  const select = document.getElementById('aov-item-select');
  if (!select || !select.value) return;

  const opt = select.options[select.selectedIndex];
  if (!opt) return;

  const code = opt.getAttribute('data-code') || '';
  const name = opt.getAttribute('data-name') || '';
  const lot = opt.getAttribute('data-lot') || '';
  const spec = opt.getAttribute('data-spec') || '';

  const codeInput = document.getElementById('aov-code');
  const nameInput = document.getElementById('aov-name');
  const lotInput = document.getElementById('aov-lot');
  const labelInput = document.getElementById('aov-label');

  if (codeInput) codeInput.value = code;
  if (nameInput) nameInput.value = name;
  if (lotInput && lot) lotInput.value = lot;
  if (labelInput && spec) labelInput.value = spec;

  calcVialExpiry();
};

window.calcVialExpiry = function() {
  const dateInput = document.getElementById('aov-date');
  const daysInput = document.getElementById('aov-days');
  const expiryInput = document.getElementById('aov-expiry');

  if (!dateInput || !daysInput || !expiryInput) return;

  const openDateVal = dateInput.value;
  const days = parseInt(daysInput.value) || 30;

  if (openDateVal) {
    try {
      const d = new Date(openDateVal);
      d.setDate(d.getDate() + days);
      expiryInput.value = d.toISOString().split('T')[0];
    } catch (e) {
      console.error(e);
    }
  }
};

window.submitAddOpenVial = async function() {
  const errBox = document.getElementById('aov-error');
  if (errBox) errBox.classList.add('hidden');

  const select = document.getElementById('aov-item-select');
  const itemId = select ? select.value : null;
  const code = document.getElementById('aov-code')?.value.trim() || '';
  const name = document.getElementById('aov-name')?.value.trim() || '';
  const lot = document.getElementById('aov-lot')?.value.trim() || '';
  const label = document.getElementById('aov-label')?.value.trim() || 'Lọ 01';
  const location = document.getElementById('aov-location')?.value || 'Máy sinh hóa tự động';
  const openDate = document.getElementById('aov-date')?.value;
  const openTime = document.getElementById('aov-time')?.value || '08:00';
  const stabilityDays = parseInt(document.getElementById('aov-days')?.value) || 30;
  const expiryDate = document.getElementById('aov-expiry')?.value;
  const notes = document.getElementById('aov-notes')?.value.trim() || '';

  if (!name) {
    if (errBox) {
      errBox.textContent = 'Vui lòng nhập tên hóa chất / sinh phẩm!';
      errBox.classList.remove('hidden');
    }
    return;
  }

  try {
    const res = await fetch('/api/inventory/open-vials', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        item_id: itemId ? parseInt(itemId) : null,
        item_code: code,
        item_name: name,
        lot_number: lot,
        vial_label: label,
        location: location,
        open_date: openDate,
        open_time: openTime,
        stability_days: stabilityDays,
        expiry_date: expiryDate,
        notes: notes
      })
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Không thể lưu lọ mở nắp');
    }

    closeModal('modal-add-open-vial');
    showToast(data.message || 'Đã ghi nhận mở lọ thành công!', 'success');
    fetchOpenVials();
  } catch (err) {
    if (errBox) {
      errBox.textContent = err.message;
      errBox.classList.remove('hidden');
    }
  }
};

// Finish/Discard Modal Handlers
window.openFinishVialModal = function(id, name, lot, openDate) {
  const idInput = document.getElementById('finish-vial-id');
  const nameEl = document.getElementById('finish-vial-name');
  const infoEl = document.getElementById('finish-vial-info');
  const reasonInput = document.getElementById('finish-vial-reason');

  if (idInput) idInput.value = id;
  if (nameEl) nameEl.textContent = name;
  if (infoEl) infoEl.textContent = `Số lô: ${lot || 'N/A'} • Ngày mở nắp: ${openDate}`;
  if (reasonInput) reasonInput.value = '';

  openModal('modal-finish-vial');
};

window.submitFinishOpenVial = async function() {
  const id = document.getElementById('finish-vial-id')?.value;
  const radios = document.getElementsByName('finish_vial_action');
  let action = 'finished';
  for (const r of radios) {
    if (r.checked) {
      action = r.value;
      break;
    }
  }
  const reason = document.getElementById('finish-vial-reason')?.value.trim() || '';

  if (!id) return;

  try {
    const res = await fetch(`/api/inventory/open-vials/${id}/finish`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        status: action,
        discard_reason: reason
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Lỗi xử lý');

    closeModal('modal-finish-vial');
    showToast(data.message || 'Đã cập nhật trạng thái lọ.', 'success');
    fetchOpenVials();
  } catch (err) {
    alert(err.message);
  }
};

// Mini Sticker Label Printing (QĐ 2429 Standard)
window.openPrintVialLabelModal = async function(vialId) {
  const container = document.getElementById('vial-sticker-printable');
  if (!container) return;

  container.innerHTML = '<div class="p-6 text-center text-slate-500">Đang tải tem nhãn...</div>';
  openModal('modal-print-vial-label');

  try {
    const res = await fetch(`/api/inventory/open-vials/${vialId}/label`);
    if (!res.ok) throw new Error('Không thể tải tem nhãn');
    const data = await res.json();
    const v = data.vial;

    container.innerHTML = `
      <div style="font-family: Arial, sans-serif; max-width: 320px; margin: 0 auto; padding: 12px; border: 2px solid #000; border-radius: 6px; background: #fff; color: #000;">
        <div style="text-align: center; border-bottom: 1.5px solid #000; padding-bottom: 4px; margin-bottom: 6px;">
          <div style="font-size: 8pt; font-weight: bold; text-transform: uppercase;">${data.hospital}</div>
          <div style="font-size: 9.5pt; font-weight: 900; color: #0369a1; text-transform: uppercase;">${data.department}</div>
          <div style="font-size: 7.5pt; font-style: italic;">TEM THEO DÕI HẠN MỞ NẮP (QĐ 2429/QĐ-BYT)</div>
        </div>
        
        <div style="font-size: 10pt; font-weight: bold; margin-bottom: 4px; line-height: 1.2;">
          ${v.item_name}
        </div>
        <div style="font-size: 8.5pt; display: flex; justify-content: space-between; margin-bottom: 4px;">
          <span>Mã: <strong>${v.item_code}</strong></span>
          <span>Lô: <strong>${v.lot_number || 'LOT--'}</strong></span>
        </div>
        <div style="font-size: 8.5pt; margin-bottom: 4px;">
          Quy cách/Nhãn: <strong>${v.vial_label || 'Lọ 01'}</strong>
        </div>
        <div style="font-size: 8.5pt; display: flex; justify-content: space-between; margin-bottom: 4px;">
          <span>Ngày mở: <strong>${v.open_date}</strong></span>
          <span>Giờ: <strong>${v.open_time || '08:00'}</strong></span>
        </div>
        
        <div style="background: #f1f5f9; border: 1.5px solid #dc2626; border-radius: 4px; padding: 5px; text-align: center; margin: 6px 0;">
          <div style="font-size: 7pt; font-weight: bold; text-transform: uppercase; color: #b91c1c;">HẠN DÙNG SAU MỞ NẮP (IN-USE EXP):</div>
          <div style="font-size: 12pt; font-weight: 900; color: #b91c1c; letter-spacing: 0.5px;">${v.expiry_date}</div>
          <div style="font-size: 7pt; color: #475569;">(Độ ổn định: ${v.stability_days} ngày)</div>
        </div>

        <div style="font-size: 8pt; display: flex; justify-content: space-between; border-top: 1px dotted #94a3b8; padding-top: 4px;">
          <span>Vị trí: <strong>${v.location || 'Máy sinh hóa'}</strong></span>
          <span>KTV: <strong>${v.opened_by_name || 'KTV'}</strong></span>
        </div>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="p-4 text-center text-red-500 font-bold">${err.message}</div>`;
  }
};

window.executePrintVialLabel = function() {
  const printContent = document.getElementById('vial-sticker-printable');
  if (!printContent) return;

  const win = window.open('', '', 'width=450,height=500');
  win.document.write(`
    <html>
      <head>
        <title>In Tem Dán Lọ Hóa Chất - BVĐK Thiên Ân</title>
        <style>
          @page { size: auto; margin: 2mm; }
          body { margin: 0; padding: 4px; font-family: Arial, sans-serif; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        </style>
      </head>
      <body>
        ${printContent.innerHTML}
        <script>
          window.onload = function() { window.print(); window.close(); };
        </script>
      </body>
    </html>
  `);
  win.document.close();
};
