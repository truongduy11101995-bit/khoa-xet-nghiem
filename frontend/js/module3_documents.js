// Module 3: Kho Hồ Sơ, Biểu Mẫu & Mục Lục 10 Cuốn (2429 & ATSH Cấp II)
// Khoa Xét Nghiệm - Bệnh Viện Đa Khoa Thiên Ân - Viễn Đông

let currentDocSubTab = 'catalog'; // 'catalog', 'fulltree', 'forms', 'downloads'

// Sub-Tab Switcher
window.switchDocSubTab = function(subTabName) {
  currentDocSubTab = subTabName;

  const btnCatalog = document.getElementById('doc-subtab-btn-catalog');
  const btnFulltree = document.getElementById('doc-subtab-btn-fulltree');
  const btnForms = document.getElementById('doc-subtab-btn-forms');
  const btnDownloads = document.getElementById('doc-subtab-btn-downloads');

  const contentCatalog = document.getElementById('doc-subtab-content-catalog');
  const contentFulltree = document.getElementById('doc-subtab-content-fulltree');
  const contentForms = document.getElementById('doc-subtab-content-forms');
  const contentDownloads = document.getElementById('doc-subtab-content-downloads');

  const activeBtnCls = "flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs sm:text-sm bg-sky-700 text-white shadow-sm transition";
  const inactiveBtnCls = "flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold text-xs sm:text-sm text-slate-600 hover:text-sky-700 hover:bg-sky-50 transition";

  if (btnCatalog) btnCatalog.className = (subTabName === 'catalog') ? activeBtnCls : inactiveBtnCls;
  if (btnFulltree) btnFulltree.className = (subTabName === 'fulltree') ? activeBtnCls : inactiveBtnCls;
  if (btnForms) btnForms.className = (subTabName === 'forms') ? activeBtnCls : inactiveBtnCls;
  if (btnDownloads) btnDownloads.className = (subTabName === 'downloads') ? activeBtnCls : inactiveBtnCls;

  if (contentCatalog) contentCatalog.classList.toggle('hidden', subTabName !== 'catalog');
  if (contentFulltree) contentFulltree.classList.toggle('hidden', subTabName !== 'fulltree');
  if (contentForms) contentForms.classList.toggle('hidden', subTabName !== 'forms');
  if (contentDownloads) contentDownloads.classList.toggle('hidden', subTabName !== 'downloads');

  // Trigger relevant initializers
  if (subTabName === 'catalog') {
    if (window.initCatalogModule) window.initCatalogModule();
  } else if (subTabName === 'fulltree') {
    loadFullTree();
  } else if (subTabName === 'forms') {
    fetchDocuments();
  }
};

window.loadDocumentsModule = async function() {
  window.switchDocSubTab(currentDocSubTab || 'catalog');
};

/* ==========================================================================
   PART A: FULL-TREE (523 FILES TỪ Ổ D:\ THEO 12 CHUYÊN ĐỀ)
   ========================================================================== */
let fullTreeCategories = [];
let fullTreeSearchQuery = '';
let fullTreeExtFilter = 'all';
let fullTreeExpanded = {};

async function loadFullTree(forceRefresh = false) {
  const container = document.getElementById('fulltree-accordion-container');
  const statsText = document.getElementById('fulltree-stats-text');
  if (!container) return;

  if (fullTreeCategories.length === 0 || forceRefresh) {
    container.innerHTML = `
      <div class="p-12 text-center bg-white rounded-2xl border border-slate-200">
        <div class="animate-spin inline-block w-8 h-8 border-4 border-sky-600 border-t-transparent rounded-full mb-3"></div>
        <div class="text-sm font-semibold text-slate-700">Đang quét toàn diện 523 tệp tin từ ổ D:...</div>
        <div class="text-xs text-slate-400 mt-1">D:\\01_TRON_BO_HO_SO_KHOA_XET_NGHIEM_TOAN_DIEN_2026</div>
      </div>
    `;
    if (statsText) statsText.textContent = "Đang đồng bộ dữ liệu ổ D:...";

    try {
      const res = await fetch('/api/documents/full-tree');
      const data = await res.json();
      if (!res.ok || !data.success) {
        container.innerHTML = '<div class="p-8 text-center text-red-500 bg-white rounded-2xl border border-red-200">Không thể quét cây thư mục từ ổ D. Vui lòng kiểm tra quyền truy cập.</div>';
        return;
      }

      fullTreeCategories = data.categories || [];

      // Calculate ext counts
      let totalAll = 0, countDocx = 0, countXlsx = 0, countPdf = 0;
      fullTreeCategories.forEach(cat => {
        (cat.files || []).forEach(f => {
          totalAll++;
          const e = (f.ext || '').toLowerCase();
          if (e === 'docx' || e === 'doc') countDocx++;
          else if (e === 'xlsx' || e === 'xls') countXlsx++;
          else if (e === 'pdf') countPdf++;
        });
      });

      const setT = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
      setT('ft-cnt-all', totalAll);
      setT('ft-cnt-docx', countDocx);
      setT('ft-cnt-xlsx', countXlsx);
      setT('ft-cnt-pdf', countPdf);
      setT('badge-fulltree-total', totalAll);
      setT('stat-total-disk-files', `${totalAll} Files`);

      // Set default expanded for first 2 categories
      if (Object.keys(fullTreeExpanded).length === 0 && fullTreeCategories.length > 0) {
        fullTreeCategories.forEach((cat, idx) => {
          fullTreeExpanded[cat.key] = (idx < 2);
        });
      }

      if (statsText) {
        statsText.textContent = `Tổng: ${totalAll} tệp tin (${data.total_size_mb || 0} MB) trong ${fullTreeCategories.length} nhóm chuyên đề`;
      }
    } catch (err) {
      container.innerHTML = '<div class="p-8 text-center text-red-500 bg-white rounded-2xl border border-red-200">Lỗi kết nối khi quét ổ đĩa D.</div>';
      return;
    }
  }

  renderFullTree();
}

function renderFullTree() {
  const container = document.getElementById('fulltree-accordion-container');
  if (!container) return;

  const q = fullTreeSearchQuery.trim().toLowerCase();
  const ext = fullTreeExtFilter;

  const colorThemes = {
    blue: { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-800', badge: 'bg-blue-600 text-white', hover: 'hover:bg-blue-50/60' },
    indigo: { bg: 'bg-indigo-50', border: 'border-indigo-200', text: 'text-indigo-800', badge: 'bg-indigo-600 text-white', hover: 'hover:bg-indigo-50/60' },
    emerald: { bg: 'bg-emerald-50', border: 'border-emerald-200', text: 'text-emerald-800', badge: 'bg-emerald-600 text-white', hover: 'hover:bg-emerald-50/60' },
    purple: { bg: 'bg-purple-50', border: 'border-purple-200', text: 'text-purple-800', badge: 'bg-purple-600 text-white', hover: 'hover:bg-purple-50/60' },
    teal: { bg: 'bg-teal-50', border: 'border-teal-200', text: 'text-teal-800', badge: 'bg-teal-600 text-white', hover: 'hover:bg-teal-50/60' },
    cyan: { bg: 'bg-cyan-50', border: 'border-cyan-200', text: 'text-cyan-800', badge: 'bg-cyan-600 text-white', hover: 'hover:bg-cyan-50/60' },
    amber: { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-800', badge: 'bg-amber-600 text-white', hover: 'hover:bg-amber-50/60' },
    violet: { bg: 'bg-violet-50', border: 'border-violet-200', text: 'text-violet-800', badge: 'bg-violet-600 text-white', hover: 'hover:bg-violet-50/60' },
    orange: { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-800', badge: 'bg-orange-600 text-white', hover: 'hover:bg-orange-50/60' },
    rose: { bg: 'bg-rose-50', border: 'border-rose-200', text: 'text-rose-800', badge: 'bg-rose-600 text-white', hover: 'hover:bg-rose-50/60' },
    red: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-800', badge: 'bg-red-600 text-white', hover: 'hover:bg-red-50/60' },
    slate: { bg: 'bg-slate-100', border: 'border-slate-300', text: 'text-slate-800', badge: 'bg-slate-700 text-white', hover: 'hover:bg-slate-100/60' },
    sky: { bg: 'bg-sky-50', border: 'border-sky-200', text: 'text-sky-800', badge: 'bg-sky-600 text-white', hover: 'hover:bg-sky-50/60' }
  };

  let renderedCategoriesCount = 0;
  let totalMatchingFiles = 0;
  let html = '';

  fullTreeCategories.forEach(cat => {
    // Filter files
    let filteredFiles = (cat.files || []).filter(f => {
      // Ext filter
      const fileExt = (f.ext || '').toLowerCase();
      if (ext === 'docx' && fileExt !== 'docx' && fileExt !== 'doc') return false;
      if (ext === 'xlsx' && fileExt !== 'xlsx' && fileExt !== 'xls') return false;
      if (ext === 'pdf' && fileExt !== 'pdf') return false;

      // Query filter
      if (q) {
        const nameMatch = f.name.toLowerCase().includes(q);
        const subMatch = (f.sub_dir || '').toLowerCase().includes(q);
        const catMatch = (cat.title || '').toLowerCase().includes(q);
        return nameMatch || subMatch || catMatch;
      }
      return true;
    });

    if (filteredFiles.length === 0) return;

    renderedCategoriesCount++;
    totalMatchingFiles += filteredFiles.length;

    // When searching, auto-expand; otherwise follow fullTreeExpanded
    const isExpanded = q ? true : (fullTreeExpanded[cat.key] ?? false);
    const theme = colorThemes[cat.color] || colorThemes.blue;

    html += `
      <div class="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden transition">
        <!-- Accordion Header -->
        <button onclick="toggleFullTreeAccordion('${cat.key}')" 
                class="w-full p-4 flex items-center justify-between text-left ${theme.hover} transition">
          <div class="flex items-center gap-3 min-w-0 pr-3">
            <span class="px-2.5 py-1 rounded-lg text-xs font-black uppercase tracking-wider ${theme.badge} shrink-0 shadow-xs">
              ${cat.badge || cat.key.slice(0, 10)}
            </span>
            <div class="min-w-0">
              <h4 class="text-sm font-extrabold text-slate-900 truncate">
                ${cat.title}
              </h4>
              <p class="text-[11px] text-slate-400 font-mono truncate">
                ${cat.key}
              </p>
            </div>
          </div>
          <div class="flex items-center gap-3 shrink-0">
            <span class="px-2.5 py-0.5 rounded-full text-xs font-bold ${theme.bg} ${theme.text} border ${theme.border}">
              ${filteredFiles.length} tệp tin
            </span>
            <svg class="w-5 h-5 text-slate-400 transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </div>
        </button>

        <!-- Accordion Body: File list -->
        ${isExpanded ? `
          <div class="border-t border-slate-100 divide-y divide-slate-100 bg-slate-50/40">
            ${filteredFiles.map((file, fileIdx) => {
              const fileExt = (file.ext || '').toLowerCase();
              let iconSvg = '';
              let extBadge = '';

              if (fileExt === 'docx' || fileExt === 'doc') {
                extBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-sky-100 text-sky-800 border border-sky-200">DOCX</span>';
                iconSvg = '<svg class="w-4 h-4 text-sky-700" fill="currentColor" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm-1 2l5 5h-5V4zM8 17h8v-2H8v2zm0-4h8v-2H8v2zm0-4h4V7H8v2z"/></svg>';
              } else if (fileExt === 'xlsx' || fileExt === 'xls') {
                extBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">XLSX</span>';
                iconSvg = '<svg class="w-4 h-4 text-emerald-600" fill="currentColor" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm-1 2l5 5h-5V4zM8 17l2.5-4L8 9h2l1.5 2.5L13 9h2l-2.5 4L15 17h-2l-1.5-2.5L10 17H8z"/></svg>';
              } else if (fileExt === 'pdf') {
                extBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-800 border border-red-200">PDF</span>';
                iconSvg = '<svg class="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14.5v-9l6 4.5-6 4.5z"/></svg>';
              } else {
                extBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-800 border border-slate-200">${fileExt.toUpperCase()}</span>`;
                iconSvg = '<svg class="w-4 h-4 text-slate-600" fill="currentColor" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm-1 2l5 5h-5V4z"/></svg>';
              }

              const sizeText = file.size_kb > 1024 ? `${(file.size_kb / 1024).toFixed(1)} MB` : `${file.size_kb} KB`;

              return `
                <div class="p-3 sm:px-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 hover:bg-white transition group">
                  <div class="flex items-start gap-3 min-w-0">
                    <span class="text-xs font-mono text-slate-400 w-6 pt-0.5 shrink-0 text-right">${fileIdx + 1}.</span>
                    <div class="p-1.5 rounded-lg bg-white border border-slate-200 shrink-0 group-hover:border-sky-300 transition">
                      ${iconSvg}
                    </div>
                    <div class="min-w-0">
                      <div class="text-xs sm:text-sm font-semibold text-slate-900 group-hover:text-sky-700 transition leading-snug break-words">
                        ${file.name}
                      </div>
                      ${file.sub_dir ? `
                        <div class="text-[11px] text-slate-400 font-mono mt-0.5 flex items-center gap-1">
                          <svg class="w-3 h-3 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/></svg>
                          <span>${file.sub_dir}</span>
                        </div>
                      ` : ''}
                    </div>
                  </div>

                  <div class="flex items-center gap-2 self-end sm:self-auto shrink-0 pl-9 sm:pl-0">
                    ${extBadge}
                    <span class="text-[11px] font-mono text-slate-400 w-16 text-right">${sizeText}</span>

                    ${fileExt === 'pdf' ? `
                      <a href="/api/documents/preview-file?rel_path=${encodeURIComponent(file.rel_path)}" target="_blank"
                         class="px-2.5 py-1 rounded-lg text-xs font-semibold text-sky-700 bg-sky-50 hover:bg-sky-100 transition flex items-center gap-1"
                         title="Xem trước PDF trong tab mới">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                        <span>Xem</span>
                      </a>
                    ` : ''}

                    <a href="${file.download_url}" download
                       class="px-3 py-1 rounded-lg text-xs font-bold text-white bg-sky-700 hover:bg-sky-800 shadow-xs transition flex items-center gap-1.5"
                       title="Tải tệp tin về máy tính">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
                      <span>Tải Về</span>
                    </a>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        ` : ''}
      </div>
    `;
  });

  if (renderedCategoriesCount === 0) {
    container.innerHTML = `
      <div class="p-12 text-center bg-white rounded-2xl border border-slate-200">
        <svg class="w-12 h-12 mx-auto text-slate-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
        <div class="text-sm font-semibold text-slate-700">Không tìm thấy tệp tin phù hợp trong 523 files</div>
        <div class="text-xs text-slate-400 mt-1">Thử tìm với từ khóa khác (ví dụ: "SOP", "IQC", "hóa chất", "nồi hấp", "nhiệt độ"...)</div>
      </div>
    `;
    return;
  }

  container.innerHTML = html;
}

window.handleFullTreeSearch = function(query) {
  fullTreeSearchQuery = query;
  renderFullTree();
};

window.setFullTreeExtFilter = function(ext) {
  fullTreeExtFilter = ext;
  const ids = {
    'all': 'btn-tree-filter-all',
    'docx': 'btn-tree-filter-docx',
    'xlsx': 'btn-tree-filter-xlsx',
    'pdf': 'btn-tree-filter-pdf'
  };

  Object.keys(ids).forEach(k => {
    const el = document.getElementById(ids[k]);
    if (!el) return;
    if (k === ext) {
      el.className = "px-3 py-1 rounded-lg text-xs font-bold bg-sky-700 text-white transition";
    } else {
      el.className = "px-3 py-1 rounded-lg text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 border border-slate-200 transition";
    }
  });

  renderFullTree();
};

window.toggleFullTreeAccordion = function(catKey) {
  fullTreeExpanded[catKey] = !fullTreeExpanded[catKey];
  renderFullTree();
};

window.toggleAllFullTreeGroups = function(expand) {
  fullTreeCategories.forEach(cat => {
    fullTreeExpanded[cat.key] = expand;
  });
  renderFullTree();
};

/* ==========================================================================
   PART B: BIỂU MẪU THƯỜNG DÙNG, PHIẾU KẾT QUẢ & BÌA IN SẴN
   ========================================================================== */
let currentDocCategory = 'all';
let currentSearchQuery = '';
let documentsList = [];

async function fetchDocuments() {
  const container = document.getElementById('documents-list-container');
  if (!container) return;

  container.innerHTML = '<div class="p-12 text-center text-slate-500"><div class="animate-spin inline-block w-8 h-8 border-4 border-sky-600 border-t-transparent rounded-full mb-3"></div><div>Đang tải biểu mẫu từ ổ đĩa D:...</div></div>';

  try {
    let url = `/api/documents/list?category=${currentDocCategory}`;
    if (currentSearchQuery) {
      url += `&q=${encodeURIComponent(currentSearchQuery)}`;
    }

    const res = await fetch(url);
    const data = await res.json();
    if (!res.ok || !data.success) {
      container.innerHTML = '<div class="p-8 text-center text-red-500">Không thể tải danh sách tài liệu.</div>';
      return;
    }

    documentsList = data.documents || [];
    renderDocumentCategoryCounts(data.category_counts, data.total);
    renderDocumentsList(documentsList);
  } catch (err) {
    container.innerHTML = '<div class="p-8 text-center text-red-500">Lỗi kết nối khi tải kho tài liệu.</div>';
  }
}

function renderDocumentCategoryCounts(counts, total) {
  const setBadge = (id, count) => {
    const el = document.getElementById(id);
    if (el) el.textContent = count !== undefined ? count : 0;
  };

  setBadge('doc-count-all', total);
  setBadge('doc-count-phieu-kq', counts['phieu_kq_hen'] || 0);
  setBadge('doc-count-so-sach-2429', counts['so_sach_2429'] || 0);
  setBadge('doc-count-bia-hc', counts['bia_hanh_chinh'] || 0);
  setBadge('doc-count-ho-so-10-cuon', counts['ho_so_10_cuon'] || 0);
}

window.setDocumentCategory = function(cat) {
  currentDocCategory = cat;

  const tabIds = {
    'all': 'doc-tab-all',
    'phieu_kq_hen': 'doc-tab-phieu-kq',
    'so_sach_2429': 'doc-tab-so-sach-2429',
    'bia_hanh_chinh': 'doc-tab-bia-hc',
    'ho_so_10_cuon': 'doc-tab-ho-so-10-cuon'
  };

  Object.keys(tabIds).forEach(k => {
    const tabEl = document.getElementById(tabIds[k]);
    if (!tabEl) return;
    if (k === cat) {
      tabEl.className = "flex items-center gap-1.5 px-3 py-1.5 border-b-2 border-sky-700 text-sky-800 font-bold text-xs uppercase tracking-wider";
    } else {
      tabEl.className = "flex items-center gap-1.5 px-3 py-1.5 border-b-2 border-transparent text-slate-500 hover:text-slate-700 font-semibold text-xs uppercase tracking-wider";
    }
  });

  fetchDocuments();
};

window.handleDocumentSearch = function(query) {
  currentSearchQuery = query;
  fetchDocuments();
};

function renderDocumentsList(docs) {
  const container = document.getElementById('documents-list-container');
  const isAdmin = currentUser && ['truong_khoa', 'ktv_truong'].includes(currentUser.role);

  if (docs.length === 0) {
    container.innerHTML = `
      <div class="p-12 text-center bg-white rounded-2xl border border-slate-200">
        <svg class="w-12 h-12 mx-auto text-slate-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
        <div class="text-sm font-semibold text-slate-700">Không tìm thấy biểu mẫu phù hợp</div>
        <div class="text-xs text-slate-400 mt-1">Thử tìm với từ khóa khác như "2429", "nhiệt độ", "đông máu", "huyết trắng"...</div>
      </div>
    `;
    return;
  }

  const catLabels = {
    'phieu_kq_hen': 'Phiếu Kết Quả & Phiếu Hẹn',
    'so_sach_2429': 'Sổ Sách & Biểu Mẫu QLCL (2429)',
    'bia_hanh_chinh': 'Bìa Hồ Sơ & Hành Chính',
    'ho_so_10_cuon': 'Trọn Bộ 10 Cuốn Hồ Sơ (.docx & .zip)'
  };

  let html = `<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">`;

  docs.forEach(doc => {
    const ext = (doc.file_ext || '').toLowerCase();
    let badgeClass = 'badge-docx';
    let iconSvg = '';

    if (ext === 'pdf') {
      badgeClass = 'badge-pdf';
      iconSvg = '<svg class="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14.5v-9l6 4.5-6 4.5z"/></svg>';
    } else if (ext === 'xlsx' || ext === 'xls') {
      badgeClass = 'badge-xlsx';
      iconSvg = '<svg class="w-6 h-6 text-emerald-600" fill="currentColor" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm-1 2l5 5h-5V4zM8 17l2.5-4L8 9h2l1.5 2.5L13 9h2l-2.5 4L15 17h-2l-1.5-2.5L10 17H8z"/></svg>';
    } else {
      badgeClass = 'badge-docx';
      iconSvg = '<svg class="w-6 h-6 text-sky-700" fill="currentColor" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm-1 2l5 5h-5V4zM8 17h8v-2H8v2zm0-4h8v-2H8v2zm0-4h4V7H8v2z"/></svg>';
    }

    const sizeKB = Math.round(doc.file_size / 1024);
    const sizeDisplay = sizeKB > 1024 ? `${(sizeKB / 1024).toFixed(1)} MB` : `${sizeKB} KB`;

    html += `
      <div class="bg-white rounded-2xl border border-slate-200/90 shadow-sm hover:shadow-md transition p-4 flex flex-col justify-between group">
        <div>
          <!-- Top Row: Code & Category -->
          <div class="flex items-center justify-between gap-2 mb-2">
            <span class="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase tracking-wide bg-slate-100 text-slate-800 border border-slate-200">
              ${doc.code || 'BM-XN'}
            </span>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase ${badgeClass}">
              ${ext.toUpperCase()} • v${doc.version || '1.0'}
            </span>
          </div>

          <!-- Title -->
          <div class="flex items-start gap-2.5 mt-1">
            <div class="p-2 rounded-xl bg-slate-50 border border-slate-100 flex-shrink-0 group-hover:scale-105 transition">
              ${iconSvg}
            </div>
            <div>
              <h4 class="text-sm font-bold text-slate-900 group-hover:text-sky-700 transition leading-snug line-clamp-2" title="${doc.title}">
                ${doc.title}
              </h4>
              <p class="text-[11px] text-slate-400 mt-0.5 font-mono truncate" title="${doc.file_name}">${doc.file_name}</p>
            </div>
          </div>

          <!-- Description -->
          <p class="text-xs text-slate-500 mt-2.5 line-clamp-2 leading-relaxed">
            ${doc.description || catLabels[doc.category] || ''}
          </p>
        </div>

        <!-- Footer Actions -->
        <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
          <span class="text-[11px] text-slate-400 font-medium">${sizeDisplay}</span>

          <div class="flex items-center gap-1.5">
            ${ext === 'pdf' || ['png', 'jpg', 'jpeg'].includes(ext) ? `
              <button onclick="previewDocumentFile(${doc.id}, '${escapeHtml(doc.title)}')"
                      class="px-2.5 py-1.5 font-semibold text-sky-700 bg-sky-50 hover:bg-sky-100 rounded-lg transition flex items-center gap-1">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                <span>Xem</span>
              </button>
            ` : ''}

            <a href="/api/documents/${doc.id}/download" download
               class="px-2.5 py-1.5 font-bold text-white bg-sky-700 hover:bg-sky-800 rounded-lg shadow-sm transition flex items-center gap-1">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
              <span>Tải về / In</span>
            </a>

            ${isAdmin ? `
              <button onclick="deleteDocumentRecord(${doc.id})" title="Xóa biểu mẫu"
                      class="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
              </button>
            ` : ''}
          </div>
        </div>
      </div>
    `;
  });

  html += `</div>`;
  container.innerHTML = html;
}

function escapeHtml(text) {
  if (!text) return '';
  return text.replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

window.previewDocumentFile = function(docId, title) {
  const modal = document.getElementById('modal-doc-preview');
  const iframe = document.getElementById('preview-iframe');
  const titleEl = document.getElementById('preview-doc-title');
  const downloadLink = document.getElementById('preview-download-btn');

  if (titleEl) titleEl.textContent = title;
  if (downloadLink) downloadLink.href = `/api/documents/${docId}/download`;
  if (iframe) {
    iframe.src = `/api/documents/${docId}/preview`;
  }

  openModal('modal-doc-preview');
};

window.closeDocPreviewModal = function() {
  const iframe = document.getElementById('preview-iframe');
  if (iframe) iframe.src = 'about:blank';
  closeModal('modal-doc-preview');
};

window.openUploadDocModal = function() {
  document.getElementById('upload-doc-title').value = '';
  document.getElementById('upload-doc-code').value = '';
  document.getElementById('upload-doc-version').value = '1.0';
  document.getElementById('upload-doc-desc').value = '';
  document.getElementById('upload-doc-file').value = '';
  document.getElementById('upload-doc-error').classList.add('hidden');
  openModal('modal-upload-document');
};

window.submitUploadDocument = async function() {
  const fileInput = document.getElementById('upload-doc-file');
  const category = document.getElementById('upload-doc-cat').value;
  const title = document.getElementById('upload-doc-title').value.trim();
  const code = document.getElementById('upload-doc-code').value.trim();
  const version = document.getElementById('upload-doc-version').value.trim() || '1.0';
  const description = document.getElementById('upload-doc-desc').value.trim();
  const errEl = document.getElementById('upload-doc-error');

  if (!fileInput.files || fileInput.files.length === 0) {
    errEl.textContent = 'Vui lòng chọn tệp tin cần tải lên.';
    errEl.classList.remove('hidden');
    return;
  }
  if (!title) {
    errEl.textContent = 'Vui lòng nhập tên biểu mẫu.';
    errEl.classList.remove('hidden');
    return;
  }

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  formData.append('category', category);
  formData.append('title', title);
  formData.append('code', code);
  formData.append('version', version);
  formData.append('description', description);

  try {
    const res = await fetch('/api/documents/upload', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    if (res.ok && data.success) {
      closeModal('modal-upload-document');
      showToast(data.message, 'success');
      fetchDocuments();
      loadKPIStats();
    } else {
      errEl.textContent = data.detail || 'Không thể tải lên biểu mẫu.';
      errEl.classList.remove('hidden');
    }
  } catch (err) {
    errEl.textContent = 'Lỗi kết nối khi tải lên tệp tin.';
    errEl.classList.remove('hidden');
  }
};

window.syncDocumentsFromDisk = async function() {
  try {
    showToast('Đang quét thư mục D:\\KHOA_XET_NGHIEM_DATA\\BIEU_MAU...', 'info');
    const res = await fetch('/api/documents/sync-disk', { method: 'POST' });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(data.message, 'success');
      fetchDocuments();
      loadKPIStats();
    } else {
      showToast(data.detail || 'Không thể đồng bộ ổ đĩa D.', 'error');
    }
  } catch (e) {
    showToast('Lỗi kết nối khi đồng bộ ổ đĩa.', 'error');
  }
};

window.deleteDocumentRecord = async function(docId) {
  if (!confirm('Bạn có chắc chắn muốn xóa biểu mẫu này khỏi danh mục hệ thống?')) return;
  try {
    const res = await fetch(`/api/documents/${docId}`, { method: 'DELETE' });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast('Đã xóa biểu mẫu thành công.', 'info');
      fetchDocuments();
      loadKPIStats();
    } else {
      showToast(data.detail || 'Lỗi khi xóa tài liệu.', 'error');
    }
  } catch (err) {
    showToast('Lỗi kết nối máy chủ.', 'error');
  }
};
