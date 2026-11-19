// Module 4: Hồ Sơ Lý Lịch Cá Nhân Nhân Viên (Employee Profiles)
let staffProfilesList = [];
let selectedProfileDetail = null;

window.loadProfilesModule = async function() {
  await fetchProfilesList();
};

async function fetchProfilesList() {
  const container = document.getElementById('profiles-list-container');
  if (!container) return;

  container.innerHTML = '<div class="p-12 text-center text-slate-500"><div class="animate-spin inline-block w-8 h-8 border-4 border-sky-600 border-t-transparent rounded-full mb-3"></div><div>Đang tải danh sách hồ sơ nhân sự...</div></div>';

  try {
    const res = await fetch('/api/profiles/list');
    const data = await res.json();
    if (!res.ok || !data.success) {
      container.innerHTML = '<div class="p-8 text-center text-red-500">Không thể tải danh sách hồ sơ.</div>';
      return;
    }

    staffProfilesList = data.profiles || [];
    renderProfilesGrid(staffProfilesList, data.is_admin, data.current_user_id);
  } catch (err) {
    container.innerHTML = '<div class="p-8 text-center text-red-500">Lỗi kết nối khi tải danh sách nhân sự.</div>';
  }
}

function renderProfilesGrid(profiles, isAdmin, currentUserId) {
  const container = document.getElementById('profiles-list-container');
  let html = '';

  // 1. HR Overview Summary Table for Admins (Lê Đình Tú & Nguyễn Trường Duy)
  if (isAdmin) {
    html += `
      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-4 sm:p-5 mb-5">
        <div class="flex items-center justify-between mb-3 border-b border-slate-100 pb-2.5">
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></span>
            <h4 class="text-sm font-extrabold text-slate-900 uppercase">Bảng Tổng Hợp Trạng Thái Bổ Sung Thông Tin Cán Bộ</h4>
          </div>
          <span class="text-xs font-semibold px-2.5 py-1 bg-emerald-50 text-emerald-800 rounded-lg border border-emerald-200">
            4/4 Cán bộ đã khai báo đầy đủ thông tin hành chính
          </span>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-xs text-left">
            <thead class="bg-slate-50 text-slate-700 font-bold uppercase text-[11px]">
              <tr>
                <th class="p-2.5">Cán bộ</th>
                <th class="p-2.5">Ngày sinh</th>
                <th class="p-2.5">SĐT / Email</th>
                <th class="p-2.5">Số CCHN / Ngày cấp</th>
                <th class="p-2.5">Phạm vi hoạt động</th>
                <th class="p-2.5 text-center">Hồ sơ scan (ổ D)</th>
                <th class="p-2.5 text-center">Tiến độ</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 font-medium">
    `;

    profiles.forEach(p => {
      const hasPhone = Boolean(p.phone && !p.phone.includes('**'));
      const hasCCHN = Boolean(p.cchn && !p.cchn.includes('**'));
      const hasDOB = Boolean(p.dob);
      const fileCount = p.file_count || 0;

      // Status
      const isCompleteInfo = hasPhone && hasCCHN && hasDOB;

      html += `
        <tr class="hover:bg-slate-50 transition">
          <td class="p-2.5">
            <div class="font-bold text-slate-900">${p.full_name}</div>
            <div class="text-[10px] text-slate-500 font-normal">${p.title}</div>
          </td>
          <td class="p-2.5 font-mono">${p.dob || '<span class=\"text-red-500\">Chưa có</span>'}</td>
          <td class="p-2.5">
            <div class="font-mono text-slate-800 font-semibold">${p.phone || '--'}</div>
            <div class="text-[10px] text-slate-400 truncate max-w-[150px]">${p.email || '--'}</div>
          </td>
          <td class="p-2.5 font-mono">
            <div class="font-bold text-sky-800">${p.cchn || '--'}</div>
            <div class="text-[10px] text-slate-500">${p.cchn_date || ''}</div>
          </td>
          <td class="p-2.5 text-slate-700 max-w-[180px] leading-snug">${p.cchn_scope || '--'}</td>
          <td class="p-2.5 text-center">
            <span class="px-2 py-0.5 rounded font-bold ${fileCount > 0 ? 'bg-sky-100 text-sky-800' : 'bg-amber-100 text-amber-800'}">
              ${fileCount} tệp
            </span>
          </td>
          <td class="p-2.5 text-center">
            ${fileCount > 0 ? `
              <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">100% Đầy đủ</span>
            ` : `
              <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800" title="Đã có thông tin hành chính, chờ tải scan Bằng cấp & CCHN">Chờ tải Scan</span>
            `}
          </td>
        </tr>
      `;
    });

    html += `
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  // 2. Profile Cards Grid
  html += `<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">`;

  profiles.forEach(p => {
    const isMe = p.id === currentUserId;
    const canAccess = isAdmin || isMe;

    const roleBadges = {
      'truong_khoa': 'bg-red-100 text-red-800 border-red-200',
      'ktv_truong': 'bg-teal-100 text-teal-800 border-teal-200',
      'ktv': 'bg-sky-100 text-sky-800 border-sky-200'
    };
    const roleLabels = {
      'truong_khoa': 'Trưởng Khoa',
      'ktv_truong': 'KTV Trưởng',
      'ktv': 'Kỹ Thuật Viên'
    };

    html += `
      <div class="bg-white rounded-2xl border ${isMe ? 'border-sky-500 ring-2 ring-sky-300' : 'border-slate-200'} shadow-sm hover:shadow-md transition p-5 flex flex-col justify-between">
        <div>
          <!-- Header: Avatar & Badge -->
          <div class="flex items-start justify-between mb-3">
            <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-sky-600 to-teal-500 text-white font-extrabold text-base flex items-center justify-center shadow-md">
              ${p.full_name.split(' ').slice(-1)[0].substring(0, 2).toUpperCase()}
            </div>
            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold border ${roleBadges[p.role] || ''}">
              ${roleLabels[p.role] || p.role}
            </span>
          </div>

          <!-- Name & Title -->
          <h4 class="text-sm font-bold text-slate-900 leading-snug">
            ${p.full_name} ${isMe ? '<span class="text-xs text-sky-600 font-extrabold">(Bạn)</span>' : ''}
          </h4>
          <p class="text-xs text-slate-500 mt-0.5">${p.title}</p>

          <!-- Info Details -->
          <div class="mt-4 pt-3 border-t border-slate-100 space-y-1.5 text-xs text-slate-600">
            <div class="flex items-center justify-between">
              <span class="text-slate-400">Số CCHN/GPHN:</span>
              <span class="font-mono font-semibold text-slate-800">${p.cchn || 'Chưa cập nhật'}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-slate-400">Trình độ:</span>
              <span class="font-medium text-slate-800 truncate max-w-[140px]" title="${p.education || ''}">${p.education || 'Chưa cập nhật'}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-slate-400">Hồ sơ scan (ổ D:):</span>
              <span class="px-2 py-0.2 bg-slate-100 rounded text-slate-800 font-bold">${p.file_count || 0} tệp</span>
            </div>
          </div>
        </div>

        <!-- Button Action -->
        <div class="mt-5 pt-3 border-t border-slate-100">
          ${canAccess ? `
            <button onclick="openProfileDrawer(${p.id})"
                    class="w-full py-2 px-3 rounded-xl font-bold text-xs bg-sky-50 text-sky-800 hover:bg-sky-700 hover:text-white border border-sky-200 transition flex items-center justify-center gap-1.5 shadow-sm">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2"/></svg>
              <span>Xem & Quản lý hồ sơ</span>
            </button>
          ` : `
            <div class="text-center py-2 px-3 bg-slate-50 text-slate-400 rounded-xl text-xs flex items-center justify-center gap-1">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
              <span>Bảo mật cá nhân</span>
            </div>
          `}
        </div>
      </div>
    `;
  });

  html += `</div>`;
  container.innerHTML = html;
}

async function openProfileDrawer(userId) {
  try {
    const res = await fetch(`/api/profiles/${userId}`);
    const data = await res.json();
    if (!res.ok || !data.success) {
      showToast(data.detail || 'Không có quyền truy cập hồ sơ này.', 'error');
      return;
    }

    selectedProfileDetail = data;
    renderProfileDetailModal(data);
    openModal('modal-profile-detail');
  } catch (err) {
    showToast('Lỗi khi tải chi tiết hồ sơ.', 'error');
  }
}

function renderProfileDetailModal(data) {
  const p = data.profile;
  const files = data.files || [];
  const canEdit = data.can_edit;

  document.getElementById('pd-fullname').textContent = p.full_name;
  document.getElementById('pd-title').textContent = p.title;
  document.getElementById('pd-folder').textContent = `D:\\KHOA_XET_NGHIEM_DATA\\HO_SO_NHAN_SU\\${p.folder_name}\\`;

  document.getElementById('pd-dob').textContent = p.dob || 'Chưa cập nhật';
  document.getElementById('pd-cchn').textContent = p.cchn || 'Chưa cập nhật';
  document.getElementById('pd-cchn-date').textContent = p.cchn_date || 'Chưa cập nhật';
  document.getElementById('pd-cchn-scope').textContent = p.cchn_scope || 'Chưa cập nhật';
  document.getElementById('pd-education').textContent = p.education || 'Chưa cập nhật';
  document.getElementById('pd-specialty').textContent = p.specialty || 'Chưa cập nhật';
  document.getElementById('pd-phone').textContent = p.phone || 'Chưa cập nhật';
  document.getElementById('pd-email').textContent = p.email || 'Chưa cập nhật';

  // Files List
  const filesContainer = document.getElementById('pd-files-container');
  const typeMap = {
    'bang_cap': 'Bằng cấp / Chứng chỉ',
    'cchn': 'Giấy phép hành nghề (CCHN)',
    'atsh': 'Chứng chỉ An toàn sinh học',
    'gksk': 'Giấy khám sức khỏe',
    'syll': 'Sơ yếu lý lịch / Hợp đồng',
    'mo_ta_cv': 'Mô tả công việc (QĐ 2429)',
    'khac': 'Tài liệu khác'
  };

  if (files.length === 0) {
    filesContainer.innerHTML = '<div class="p-6 text-center text-slate-400 text-xs italic">Chưa có tệp tin scan nào trong hồ sơ.</div>';
  } else {
    let fHtml = `<div class="space-y-2">`;
    files.forEach(f => {
      const ext = f.file_name.split('.').pop().toLowerCase();
      const isPdfOrImg = ['pdf', 'png', 'jpg', 'jpeg'].includes(ext);

      fHtml += `
        <div class="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between text-xs hover:bg-slate-100 transition">
          <div class="flex items-center gap-2.5 min-w-0">
            <span class="p-2 bg-white rounded-lg border border-slate-200 text-sky-700 font-extrabold uppercase text-[10px]">
              ${ext}
            </span>
            <div class="min-w-0">
              <div class="font-bold text-slate-800 truncate" title="${f.title}">${f.title}</div>
              <div class="text-[11px] text-slate-500 flex items-center gap-2">
                <span>${typeMap[f.doc_type] || f.doc_type}</span>
                <span>•</span>
                <span class="font-mono text-slate-400">${f.file_name}</span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-1.5 flex-shrink-0">
            ${isPdfOrImg ? `
              <a href="/api/profiles/${p.id}/file/${f.id}/preview" target="_blank"
                 class="px-2 py-1 bg-white hover:bg-sky-50 text-sky-700 font-semibold rounded border border-slate-200 text-[11px] transition">
                Xem
              </a>
            ` : ''}

            <a href="/api/profiles/${p.id}/file/${f.id}/download" download
               class="px-2.5 py-1 bg-sky-700 hover:bg-sky-800 text-white font-semibold rounded text-[11px] shadow-sm transition">
              Tải về
            </a>

            ${canEdit ? `
              <button onclick="deleteProfileFile(${p.id}, ${f.id})"
                      class="p-1 text-slate-400 hover:text-red-600 transition" title="Xóa tệp">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
              </button>
            ` : ''}
          </div>
        </div>
      `;
    });
    fHtml += `</div>`;
    filesContainer.innerHTML = fHtml;
  }
}

function openEditProfileModal() {
  if (!selectedProfileDetail) return;
  const p = selectedProfileDetail.profile;

  document.getElementById('ep-dob').value = p.dob || '';
  document.getElementById('ep-phone').value = p.phone || '';
  document.getElementById('ep-email').value = p.email || '';
  document.getElementById('ep-cchn').value = p.cchn || '';
  document.getElementById('ep-cchn-date').value = p.cchn_date || '';
  document.getElementById('ep-cchn-scope').value = p.cchn_scope || '';
  document.getElementById('ep-education').value = p.education || '';
  document.getElementById('ep-specialty').value = p.specialty || '';
  document.getElementById('ep-error').classList.add('hidden');

  openModal('modal-edit-profile');
}

async function submitEditProfile() {
  if (!selectedProfileDetail) return;
  const userId = selectedProfileDetail.profile.id;

  const payload = {
    dob: document.getElementById('ep-dob').value,
    phone: document.getElementById('ep-phone').value.trim(),
    email: document.getElementById('ep-email').value.trim(),
    cchn: document.getElementById('ep-cchn').value.trim(),
    cchn_date: document.getElementById('ep-cchn-date').value,
    cchn_scope: document.getElementById('ep-cchn-scope').value.trim(),
    education: document.getElementById('ep-education').value.trim(),
    specialty: document.getElementById('ep-specialty').value.trim(),
  };

  try {
    const res = await fetch(`/api/profiles/${userId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (res.ok && data.success) {
      closeModal('modal-edit-profile');
      showToast(data.message, 'success');
      // Refresh modal
      openProfileDrawer(userId);
      fetchProfilesList();
    } else {
      const errEl = document.getElementById('ep-error');
      errEl.textContent = data.detail || 'Không thể cập nhật hồ sơ.';
      errEl.classList.remove('hidden');
    }
  } catch (err) {
    showToast('Lỗi kết nối khi cập nhật hồ sơ.', 'error');
  }
}

function openUploadScanModal() {
  if (!selectedProfileDetail) return;
  document.getElementById('up-file-title').value = '';
  document.getElementById('up-file-input').value = '';
  document.getElementById('up-file-error').classList.add('hidden');
  openModal('modal-upload-profile-file');
}

async function submitUploadProfileFile() {
  if (!selectedProfileDetail) return;
  const userId = selectedProfileDetail.profile.id;

  const fileInput = document.getElementById('up-file-input');
  const docType = document.getElementById('up-doc-type').value;
  const title = document.getElementById('up-file-title').value.trim();
  const errEl = document.getElementById('up-file-error');

  if (!fileInput.files || fileInput.files.length === 0) {
    errEl.textContent = 'Vui lòng chọn tệp tin scan/ảnh cần tải lên.';
    errEl.classList.remove('hidden');
    return;
  }
  if (!title) {
    errEl.textContent = 'Vui lòng nhập tên tài liệu / chứng chỉ.';
    errEl.classList.remove('hidden');
    return;
  }

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  formData.append('doc_type', docType);
  formData.append('title', title);

  try {
    const res = await fetch(`/api/profiles/${userId}/upload-file`, {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    if (res.ok && data.success) {
      closeModal('modal-upload-profile-file');
      showToast(data.message, 'success');
      // Refresh drawer
      openProfileDrawer(userId);
      fetchProfilesList();
    } else {
      errEl.textContent = data.detail || 'Không thể tải lên tệp tin.';
      errEl.classList.remove('hidden');
    }
  } catch (err) {
    errEl.textContent = 'Lỗi kết nối khi tải lên hồ sơ.';
    errEl.classList.remove('hidden');
  }
}

async function deleteProfileFile(userId, fileId) {
  if (!confirm('Bạn có chắc chắn muốn xóa tệp hồ sơ này?')) return;
  try {
    const res = await fetch(`/api/profiles/${userId}/file/${fileId}`, { method: 'DELETE' });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(data.message, 'info');
      openProfileDrawer(userId);
      fetchProfilesList();
    } else {
      showToast(data.detail || 'Không thể xóa tệp hồ sơ.', 'error');
    }
  } catch (err) {
    showToast('Lỗi kết nối khi xóa tệp.', 'error');
  }
}
