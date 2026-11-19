/**
 * Phân hệ 5: Mục Lục 10 Cuốn Hồ Sơ & Tra Cứu Toàn Văn 147 Tài Liệu Chuẩn Hóa
 * Khoa Xét Nghiệm - Bệnh Viện Đa Khoa Thiên Ân - Viễn Đông
 * Tự động đồng bộ với CATALOG_BINDERS, CATALOG_GROUPS, CATALOG_DOCUMENTS từ catalog_data.js
 */

let catalogState = {
    selectedBinder: 'all',
    selectedGroup: 'all',
    searchQuery: '',
    viewMode: 'catalog', // 'catalog' or 'binders'
    activeDocCode: null
};

// Initialize Catalog Module
function initCatalogModule() {
    console.log("Initializing Catalog Module (DM.TONG.00)...");
    if (typeof CATALOG_DOCUMENTS === 'undefined' || typeof CATALOG_BINDERS === 'undefined') {
        console.error("CATALOG_DOCUMENTS or CATALOG_BINDERS not loaded!");
        return;
    }

    renderCatalogStats();
    renderGroupPills();
    populateBinderDropdown();
    renderBinderCards();
    applyCatalogFilters();

    // Setup Search Input Event
    const searchInput = document.getElementById('catalog-search-input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            catalogState.searchQuery = e.target.value.trim().toLowerCase();
            applyCatalogFilters();
        });
    }

    // Setup Binder Filter Dropdown
    const binderSelect = document.getElementById('catalog-binder-select');
    if (binderSelect) {
        binderSelect.addEventListener('change', (e) => {
            catalogState.selectedBinder = e.target.value;
            applyCatalogFilters();
        });
    }

    // Setup View Mode Toggle Buttons
    const btnViewCatalog = document.getElementById('btn-view-catalog-table');
    const btnViewBinders = document.getElementById('btn-view-binders-grid');
    if (btnViewCatalog && btnViewBinders) {
        btnViewCatalog.addEventListener('click', () => switchCatalogView('catalog'));
        btnViewBinders.addEventListener('click', () => switchCatalogView('binders'));
    }
}

// Switch between Table and Binder Grid views
function switchCatalogView(mode) {
    catalogState.viewMode = mode;
    const viewCatalog = document.getElementById('catalog-table-container');
    const viewBinders = document.getElementById('catalog-binders-container');
    const btnViewCatalog = document.getElementById('btn-view-catalog-table');
    const btnViewBinders = document.getElementById('btn-view-binders-grid');

    if (mode === 'catalog') {
        if (viewCatalog) viewCatalog.classList.remove('hidden');
        if (viewBinders) viewBinders.classList.add('hidden');
        if (btnViewCatalog) {
            btnViewCatalog.classList.add('bg-blue-600', 'text-white', 'shadow-sm');
            btnViewCatalog.classList.remove('bg-white', 'text-slate-700', 'hover:bg-slate-50');
        }
        if (btnViewBinders) {
            btnViewBinders.classList.remove('bg-blue-600', 'text-white', 'shadow-sm');
            btnViewBinders.classList.add('bg-white', 'text-slate-700', 'hover:bg-slate-50');
        }
    } else {
        if (viewCatalog) viewCatalog.classList.add('hidden');
        if (viewBinders) viewBinders.classList.remove('hidden');
        if (btnViewBinders) {
            btnViewBinders.classList.add('bg-blue-600', 'text-white', 'shadow-sm');
            btnViewBinders.classList.remove('bg-white', 'text-slate-700', 'hover:bg-slate-50');
        }
        if (btnViewCatalog) {
            btnViewCatalog.classList.remove('bg-blue-600', 'text-white', 'shadow-sm');
            btnViewCatalog.classList.add('bg-white', 'text-slate-700', 'hover:bg-slate-50');
        }
    }
}

// Render Top Statistics
function renderCatalogStats() {
    const totalDocsEl = document.getElementById('stat-total-docs');
    const totalBindersEl = document.getElementById('stat-total-binders');
    const totalGroupsEl = document.getElementById('stat-total-groups');

    if (totalDocsEl) totalDocsEl.textContent = CATALOG_DOCUMENTS.length;
    if (totalBindersEl) totalBindersEl.textContent = "10 Cuốn (11 Tập)";
    if (totalGroupsEl) totalGroupsEl.textContent = "07 Nhóm Chuẩn";
}

// Render Group Filter Pills
function renderGroupPills() {
    const container = document.getElementById('catalog-group-pills');
    if (!container) return;

    let html = `
        <button onclick="setGroupFilter('all')" 
            class="group-pill px-3 py-1.5 rounded-full text-xs font-semibold transition-all duration-200 border ${catalogState.selectedGroup === 'all' ? 'bg-blue-600 text-white border-blue-600 shadow-sm' : 'bg-white text-slate-700 border-slate-200 hover:border-blue-400 hover:bg-blue-50'}">
            Tất cả (${CATALOG_DOCUMENTS.length})
        </button>
    `;

    CATALOG_GROUPS.forEach(g => {
        const isSelected = catalogState.selectedGroup === g.id;
        const shortName = g.name.split(':')[0].trim();
        html += `
            <button onclick="setGroupFilter('${g.id}')" 
                class="group-pill px-3 py-1.5 rounded-full text-xs font-semibold transition-all duration-200 border ${isSelected ? 'bg-blue-600 text-white border-blue-600 shadow-sm' : 'bg-white text-slate-700 border-slate-200 hover:border-blue-400 hover:bg-blue-50'}"
                title="${g.name}">
                ${shortName} (${g.count})
            </button>
        `;
    });

    container.innerHTML = html;
}

// Set Group Filter
function setGroupFilter(groupId) {
    catalogState.selectedGroup = groupId;
    renderGroupPills();
    applyCatalogFilters();
}

// Populate Binder Dropdown
function populateBinderDropdown() {
    const select = document.getElementById('catalog-binder-select');
    if (!select) return;

    let html = '<option value="all">Tất cả Cuốn Hồ sơ (Cuốn 01 → Cuốn 10)</option>';
    CATALOG_BINDERS.forEach(b => {
        html += `<option value="${b.id}">${b.title}</option>`;
    });

    select.innerHTML = html;
}

// Render Binder Cards Grid
function renderBinderCards() {
    const container = document.getElementById('catalog-binders-grid');
    if (!container) return;

    let html = '';
    CATALOG_BINDERS.forEach(b => {
        // Count docs in this binder
        const docsInBinder = CATALOG_DOCUMENTS.filter(d => d.binder_id === b.id || d.location.includes(b.label));
        const docCount = docsInBinder.length;

        // Visual color theme by binder
        let borderAccent = "border-l-blue-600";
        let badgeColor = "bg-blue-100 text-blue-800";
        if (b.id.includes('01')) { borderAccent = "border-l-emerald-600"; badgeColor = "bg-emerald-100 text-emerald-800"; }
        else if (b.id.includes('03')) { borderAccent = "border-l-indigo-600"; badgeColor = "bg-indigo-100 text-indigo-800"; }
        else if (b.id.includes('04')) { borderAccent = "border-l-teal-600"; badgeColor = "bg-teal-100 text-teal-800"; }
        else if (b.id.includes('06')) { borderAccent = "border-l-purple-600"; badgeColor = "bg-purple-100 text-purple-800"; }
        else if (b.id.includes('07')) { borderAccent = "border-l-amber-600"; badgeColor = "bg-amber-100 text-amber-800"; }
        else if (b.id.includes('08')) { borderAccent = "border-l-rose-600"; badgeColor = "bg-rose-100 text-rose-800"; }
        else if (b.id.includes('10')) { borderAccent = "border-l-red-600"; badgeColor = "bg-red-100 text-red-800"; }

        html += `
            <div class="bg-white rounded-xl border border-slate-200 border-l-4 ${borderAccent} shadow-sm hover:shadow-md transition-all duration-200 p-5 flex flex-col justify-between">
                <div>
                    <div class="flex items-center justify-between gap-2 mb-2">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-bold ${badgeColor}">
                            ${b.label}
                        </span>
                        <span class="text-xs text-slate-500 font-medium">${b.scale}</span>
                    </div>
                    <h3 class="font-bold text-slate-800 text-sm md:text-base leading-snug mb-2">${b.title}</h3>
                    <p class="text-xs text-slate-600 leading-relaxed mb-3 line-clamp-3">${b.docs_inside}</p>
                    <div class="text-[11px] text-slate-500 bg-slate-50 p-2 rounded border border-slate-100 mb-4">
                        <span class="font-semibold text-slate-700">Căn cứ:</span> ${b.legal}
                    </div>
                </div>
                
                <div class="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                    <span class="text-xs font-bold text-slate-700">${docCount > 0 ? docCount + ' tài liệu' : b.scale}</span>
                    <div class="flex items-center gap-1.5">
                        <a href="${b.download_url || '#'}" download 
                            class="inline-flex items-center gap-1 px-2.5 py-1.5 bg-slate-100 hover:bg-emerald-50 hover:text-emerald-700 text-slate-700 rounded-lg text-xs font-semibold transition-all border border-slate-200"
                            title="Tải file Word (.docx) của cuốn này (${b.file_size || ''})">
                            <svg class="w-3.5 h-3.5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
                            <span>Tải Word</span>
                        </a>
                        <button onclick="filterBySpecificBinder('${b.id}')" 
                            class="inline-flex items-center gap-1 px-2.5 py-1.5 bg-blue-50 text-blue-700 hover:bg-blue-600 hover:text-white rounded-lg text-xs font-semibold transition-all">
                            <span>Mở Cuốn</span>
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

// Quick filter by specific binder from card click
function filterBySpecificBinder(binderId) {
    catalogState.selectedBinder = binderId;
    const select = document.getElementById('catalog-binder-select');
    if (select) select.value = binderId;
    switchCatalogView('catalog');
    applyCatalogFilters();
}

// Apply Filters and Re-render Document Table
function applyCatalogFilters() {
    let filtered = CATALOG_DOCUMENTS.filter(doc => {
        // Group Filter
        if (catalogState.selectedGroup !== 'all' && doc.group_id !== catalogState.selectedGroup) {
            return false;
        }

        // Binder Filter
        if (catalogState.selectedBinder !== 'all') {
            const targetBinder = CATALOG_BINDERS.find(b => b.id === catalogState.selectedBinder);
            if (targetBinder) {
                const matchId = doc.binder_id === catalogState.selectedBinder;
                const matchLabel = doc.location.toLowerCase().includes(targetBinder.label.toLowerCase());
                if (!matchId && !matchLabel) return false;
            }
        }

        // Search Query
        if (catalogState.searchQuery) {
            const q = catalogState.searchQuery;
            const matchCode = doc.code.toLowerCase().includes(q);
            const matchName = doc.name.toLowerCase().includes(q);
            const matchLoc = doc.location.toLowerCase().includes(q);
            const matchGroup = doc.group_name.toLowerCase().includes(q);
            if (!matchCode && !matchName && !matchLoc && !matchGroup) return false;
        }

        return true;
    });

    renderDocumentTable(filtered);
}

// Render Document Table
function renderDocumentTable(docs) {
    const tbody = document.getElementById('catalog-docs-tbody');
    const countEl = document.getElementById('catalog-results-count');
    if (!tbody) return;

    if (countEl) {
        countEl.textContent = `Hiển thị ${docs.length} / ${CATALOG_DOCUMENTS.length} tài liệu chuẩn hóa`;
    }

    if (docs.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="px-6 py-12 text-center text-slate-500">
                    <svg class="mx-auto h-12 w-12 text-slate-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                    <p class="text-sm font-semibold text-slate-700">Không tìm thấy tài liệu phù hợp</p>
                    <p class="text-xs text-slate-500 mt-1">Vui lòng thử lại với từ khóa hoặc bộ lọc khác.</p>
                </td>
            </tr>
        `;
        return;
    }

    let html = '';
    docs.forEach(doc => {
        // Badge color based on code type
        let badgeColor = "bg-blue-50 text-blue-700 border-blue-200";
        if (doc.code.startsWith('ST.')) badgeColor = "bg-purple-50 text-purple-700 border-purple-200";
        else if (doc.code.startsWith('QT.')) badgeColor = "bg-indigo-50 text-indigo-700 border-indigo-200";
        else if (doc.code.startsWith('BM.TD')) badgeColor = "bg-amber-50 text-amber-700 border-amber-200";
        else if (doc.code.startsWith('BM.')) badgeColor = "bg-emerald-50 text-emerald-700 border-emerald-200";
        else if (doc.code.startsWith('QĐ.') || doc.code.startsWith('CV.')) badgeColor = "bg-rose-50 text-rose-700 border-rose-200";
        else if (doc.code.startsWith('PT.')) badgeColor = "bg-teal-50 text-teal-700 border-teal-200";

        html += `
            <tr class="hover:bg-blue-50/40 transition-colors duration-150 border-b border-slate-200/80">
                <td class="px-3 py-3 text-center text-xs font-semibold text-slate-500">${doc.stt}</td>
                <td class="px-3 py-3 whitespace-nowrap">
                    <button onclick="openDocumentViewer('${doc.code}')" 
                        class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-mono font-bold border ${badgeColor} hover:shadow-xs transition-all text-left">
                        ${doc.code}
                    </button>
                </td>
                <td class="px-4 py-3">
                    <a href="javascript:void(0)" onclick="openDocumentViewer('${doc.code}')" 
                        class="text-xs md:text-sm font-bold text-slate-800 hover:text-blue-600 transition-colors leading-snug line-clamp-2 block">
                        ${doc.name}
                    </a>
                    <span class="text-[11px] text-slate-600 mt-0.5 block">${doc.group_name.split(':')[0]}</span>
                </td>
                <td class="px-3 py-3 whitespace-nowrap">
                    <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
                        ${doc.location}
                    </span>
                </td>
                <td class="px-3 py-3 whitespace-nowrap text-center">
                    <span class="text-xs font-medium text-slate-600">Phiên bản 01</span>
                </td>
                <td class="px-3 py-3 whitespace-nowrap text-right text-xs">
                    <div class="inline-flex items-center gap-1.5">
                        <button onclick="openDocumentViewer('${doc.code}')" 
                            class="inline-flex items-center gap-1 px-2.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium shadow-xs transition-all">
                            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                            <span>Xem Toàn Văn</span>
                        </button>
                        <button onclick="printDirectDocument('${doc.code}')" 
                            class="inline-flex items-center p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-md transition-all"
                            title="In tài liệu này">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/></svg>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

// Open Full Document Viewer Modal
function openDocumentViewer(code) {
    const doc = CATALOG_DOCUMENTS.find(d => d.code === code);
    if (!doc) {
        alert("Không tìm thấy nội dung tài liệu mã hiệu: " + code);
        return;
    }

    catalogState.activeDocCode = code;

    const modal = document.getElementById('catalog-doc-modal');
    const modalTitle = document.getElementById('catalog-modal-title');
    const modalSubtitle = document.getElementById('catalog-modal-subtitle');
    const modalContent = document.getElementById('catalog-modal-content');
    const dlBtn = document.getElementById('catalog-modal-download-btn');

    if (modalTitle) modalTitle.textContent = `${doc.code} — ${doc.name}`;
    if (modalSubtitle) modalSubtitle.textContent = `Lưu trữ: ${doc.location} | Hệ thống Quản lý Chất lượng BVĐK Thiên Ân - Viễn Đông`;
    if (modalContent) modalContent.innerHTML = doc.html_content;
    if (dlBtn && doc.download_url) {
        dlBtn.href = doc.download_url;
        dlBtn.title = `Tải file Word (.docx) của cuốn chứa tài liệu này (${doc.file_name || ''})`;
    }

    if (modal) {
        modal.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');
    }
}

// Close Document Viewer Modal
function closeDocumentViewer() {
    const modal = document.getElementById('catalog-doc-modal');
    if (modal) {
        modal.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
    }
    catalogState.activeDocCode = null;
}

// Print currently open document or direct print
function printDocument() {
    if (!catalogState.activeDocCode) return;
    window.print();
}

function printDirectDocument(code) {
    openDocumentViewer(code);
    setTimeout(() => {
        window.print();
    }, 300);
}

// Copy Document Content
function copyDocumentContent() {
    const modalContent = document.getElementById('catalog-modal-content');
    if (!modalContent) return;

    const textToCopy = modalContent.innerText;
    navigator.clipboard.writeText(textToCopy).then(() => {
        alert("Đã sao chép nội dung tài liệu vào clipboard thành công!");
    }).catch(err => {
        console.error("Copy failed:", err);
    });
}

// Export for global usage
window.initCatalogModule = initCatalogModule;
window.setGroupFilter = setGroupFilter;
window.filterBySpecificBinder = filterBySpecificBinder;
window.switchCatalogView = switchCatalogView;
window.openDocumentViewer = openDocumentViewer;
window.closeDocumentViewer = closeDocumentViewer;
window.printDocument = printDocument;
window.printDirectDocument = printDirectDocument;
window.copyDocumentContent = copyDocumentContent;

// Pre-init on load if data is ready
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        if (typeof CATALOG_DOCUMENTS !== 'undefined') {
            renderCatalogStats();
            renderGroupPills();
            populateBinderDropdown();
            renderBinderCards();
        }
    }, 100);
});
