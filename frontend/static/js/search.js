/**
 * search.js – Search & Filter client-side logic for F-LostFound
 *
 * Features:
 *   • Debounced autocomplete (300 ms)
 *   • AJAX search + filter (no page reload)
 *   • Dynamic card rendering with colour coding
 *   • Skeleton loading state
 *   • Empty-state illustration
 *   • Hierarchical location cascade
 *   • Pagination
 */

(function () {
    "use strict";

    // ─── Config ───────────────────────────────────────────
    const DEBOUNCE_MS = 300;
    const API_SEARCH = "/api/search";
    const API_COMPLETE = "/api/search/autocomplete";
    const API_LOCATIONS = "/api/search/locations";
    const API_CATEGORIES = "/api/search/categories";

    // ─── DOM refs ─────────────────────────────────────────
    const searchInput = document.getElementById("search-input");
    const clearBtn = document.getElementById("clear-search-btn");
    const searchBtn = document.getElementById("search-submit-btn");
    const acDropdown = document.getElementById("autocomplete-dropdown");
    const toggleFilterBtn = document.getElementById("toggle-filter-btn");
    const filterPanel = document.getElementById("filter-panel");
    const filterCountBadge = document.getElementById("active-filter-count");
    const resultCounter = document.getElementById("result-counter");
    const sortSelect = document.getElementById("sort-select");
    const locSelect = document.getElementById("filter-location");
    const subLocSelect = document.getElementById("filter-sub-location");
    const catSelect = document.getElementById("filter-category");
    const activeFiltersEl = document.getElementById("active-filters");
    const grid = document.getElementById("items-grid");
    const paginationEl = document.getElementById("pagination-bar");

    // ─── State ────────────────────────────────────────────
    let filters = { q: "", type: "", status: "", location: "", sub_location: "", category: "", sort: "newest", page: 1 };
    let locationsData = [];
    let debounceTimer = null;

    // ─── Init ─────────────────────────────────────────────
    document.addEventListener("DOMContentLoaded", () => {
        loadLocations();
        loadCategories();
        bindEvents();
        doSearch();            // initial load
    });

    // ─── Event binding ────────────────────────────────────
    function bindEvents() {
        let currentFocus = -1;
        
        searchInput.addEventListener("input", () => {
            currentFocus = -1;
            const val = searchInput.value.trim();
            clearBtn.classList.toggle("hidden", val.length === 0);
            clearBtn.classList.toggle("flex", val.length > 0);
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => fetchAutocomplete(val), DEBOUNCE_MS);
        });

        searchInput.addEventListener("keydown", (e) => {
            const items = acDropdown.querySelectorAll(".ac-item, .ac-item-card");
            if (e.key === "Enter") { 
                e.preventDefault(); 
                if (currentFocus > -1 && items.length > 0) {
                    items[currentFocus].click();
                } else {
                    submitSearch(); 
                }
            } else if (e.key === "Escape") { 
                closeAutocomplete(); 
            } else if (e.key === "ArrowDown") {
                if (!items.length) return;
                e.preventDefault();
                currentFocus++;
                if (currentFocus >= items.length) currentFocus = 0;
                setActiveItem(items);
            } else if (e.key === "ArrowUp") {
                if (!items.length) return;
                e.preventDefault();
                currentFocus--;
                if (currentFocus < 0) currentFocus = items.length - 1;
                setActiveItem(items);
            }
        });

        function setActiveItem(items) {
            items.forEach(x => x.classList.remove("bg-gray-100", "outline-none", "ring-2", "ring-orange-200"));
            if (currentFocus > -1) {
                items[currentFocus].classList.add("bg-gray-100", "outline-none", "ring-2", "ring-orange-200");
                items[currentFocus].scrollIntoView({ block: "nearest", behavior: "smooth" });
            }
        }

        clearBtn.addEventListener("click", () => {
            searchInput.value = "";
            clearBtn.classList.add("hidden");
            clearBtn.classList.remove("flex");
            closeAutocomplete();
            filters.q = "";
            filters.page = 1;
            doSearch();
        });

        searchBtn.addEventListener("click", submitSearch);

        // Close autocomplete on outside click
        document.addEventListener("click", (e) => {
            if (!document.getElementById("search-container").contains(e.target)) closeAutocomplete();
        });

        // Toggle filter panel
        toggleFilterBtn.addEventListener("click", () => {
            filterPanel.classList.toggle("hidden");
            if (!filterPanel.classList.contains("hidden")) {
                filterPanel.querySelector(":scope > div").classList.add("filter-panel-open");
            }
        });

        // Chip filters (type & status)
        document.querySelectorAll(".filter-chip").forEach(chip => {
            chip.addEventListener("click", () => {
                const filterName = chip.dataset.filter;
                const value = chip.dataset.value;
                filters[filterName] = value;
                filters.page = 1;

                // Update chip styles
                document.querySelectorAll(`.${filterName}-chip`).forEach(c => {
                    c.className = c.className.replace(/active-\w+/g, "").replace("inactive", "").trim();
                    c.classList.add("filter-chip", "inactive");
                });
                chip.classList.remove("inactive");
                if (filterName === "type") {
                    if (value === "Lost") chip.classList.add("active-lost");
                    else if (value === "Found") chip.classList.add("active-found");
                    else chip.classList.add("active-generic");
                } else {
                    chip.classList.add("active-generic");
                }

                doSearch();
            });
        });

        // Location cascade
        locSelect.addEventListener("change", () => {
            filters.location = locSelect.value;
            filters.sub_location = "";
            filters.page = 1;
            populateSubLocations(locSelect.value);
            doSearch();
        });

        subLocSelect.addEventListener("change", () => {
            filters.sub_location = subLocSelect.value;
            filters.page = 1;
            doSearch();
        });

        // Category
        catSelect.addEventListener("change", () => {
            filters.category = catSelect.value;
            filters.page = 1;
            doSearch();
        });

        // Sort
        sortSelect.addEventListener("change", () => {
            filters.sort = sortSelect.value;
            filters.page = 1;
            doSearch();
        });
    }

    // ─── Search submit ────────────────────────────────────
    function submitSearch() {
        filters.q = searchInput.value.trim();
        filters.page = 1;
        closeAutocomplete();
        doSearch();
    }

    // ─── Autocomplete ─────────────────────────────────────
    async function fetchAutocomplete(q) {
        if (!q) { closeAutocomplete(); return; }
        try {
            const res = await fetch(`${API_COMPLETE}?q=${encodeURIComponent(q)}`);
            const data = await res.json();
            renderAutocomplete(data, q);
        } catch (e) { console.error("Autocomplete error:", e); }
    }

    function renderAutocomplete(data, query) {
        let html = "";

        if (data.keywords && data.keywords.length) {
            html += `<div class="ac-section-title">Gợi ý từ khóa</div>`;
            data.keywords.forEach(kw => {
                html += `
                <div class="ac-item" data-keyword="${esc(kw)}">
                    <div class="ac-icon bg-orange-50 text-orange-500"><i class="fas fa-search"></i></div>
                    <span class="text-sm text-gray-700 font-medium">${highlight(kw, query)}</span>
                </div>`;
            });
        }

        if (data.items && data.items.length) {
            html += `<div class="ac-section-title">Kết quả khớp nhanh</div>`;
            data.items.forEach(item => {
                const badge = item.item_type === "Lost"
                    ? `<span class="text-xs font-semibold text-red-500">Mất đồ</span>`
                    : `<span class="text-xs font-semibold text-green-500">Nhặt được</span>`;
                const img = item.image_url
                    ? `<img src="${esc(item.image_url)}" alt="">`
                    : `<div class="w-12 h-12 rounded-lg bg-gray-100 flex items-center justify-center text-gray-400"><i class="fas fa-image"></i></div>`;
                html += `
                <div class="ac-item-card" data-id="${item.id}">
                    ${img}
                    <div class="flex-1 min-w-0">
                        <p class="text-sm font-semibold text-gray-800 truncate">${highlight(esc(item.title), query)}</p>
                        <div class="flex items-center gap-2">${badge}
                            <span class="text-xs text-gray-400">${esc(item.location)}</span>
                        </div>
                    </div>
                </div>`;
            });
        }

        if (!html) { closeAutocomplete(); return; }

        acDropdown.innerHTML = html;
        acDropdown.classList.add("active");

        // Click handlers
        acDropdown.querySelectorAll(".ac-item").forEach(el => {
            el.addEventListener("click", () => {
                searchInput.value = el.dataset.keyword;
                submitSearch();
            });
        });
        acDropdown.querySelectorAll(".ac-item-card").forEach(el => {
            el.addEventListener("click", () => {
                closeAutocomplete();
                if (typeof openDetailModal === "function") openDetailModal(el.dataset.id);
            });
        });
    }

    function closeAutocomplete() { acDropdown.classList.remove("active"); }

    // ─── Main search via API ──────────────────────────────
    async function doSearch() {
        showSkeleton();
        updateActiveFilters();

        const params = new URLSearchParams();
        if (filters.q) params.set("q", filters.q);
        if (filters.type) params.set("type", filters.type);
        if (filters.status) params.set("status", filters.status);
        if (filters.location) params.set("location", filters.location);
        if (filters.sub_location) params.set("sub_location", filters.sub_location);
        if (filters.category) params.set("category", filters.category);
        params.set("sort", filters.sort);
        params.set("page", filters.page);

        try {
            const res = await fetch(`${API_SEARCH}?${params.toString()}`);
            const data = await res.json();
            renderResults(data);
        } catch (e) {
            console.error("Search error:", e);
            grid.innerHTML = `<div class="col-span-full text-center py-8 text-red-500">Có lỗi xảy ra, vui lòng thử lại.</div>`;
        }
    }

    // ─── Render results ───────────────────────────────────
    function renderResults(data) {
        // Counter
        resultCounter.textContent = `Tìm thấy ${data.total} kết quả`;
        resultCounter.classList.add("counter-pulse");
        setTimeout(() => resultCounter.classList.remove("counter-pulse"), 350);

        // Update live tab counts
        if (data.counts) {
            const lostChip = document.querySelector('.type-chip[data-value="Lost"]');
            const foundChip = document.querySelector('.type-chip[data-value="Found"]');
            if (lostChip) lostChip.innerHTML = `<i class="fas fa-exclamation-circle text-xs"></i> Mất đồ (${data.counts.lost})`;
            if (foundChip) foundChip.innerHTML = `<i class="fas fa-check-circle text-xs"></i> Nhặt được (${data.counts.found})`;
        }

        // Cards
        if (!data.items.length) {
            grid.innerHTML = renderEmptyState();
            paginationEl.innerHTML = "";
            return;
        }

        let html = "";
        data.items.forEach((item, i) => {
            const borderClass = item.item_type === "Lost" ? "card-lost" : "card-found";
            const badgeClasses = item.item_type === "Lost"
                ? "bg-red-100 text-red-600 border border-red-200"
                : "bg-green-100 text-green-600 border border-green-200";
            const badgeText = item.item_type === "Lost" ? "Mất đồ" : "Nhặt được";
            const dateStr = formatDate(item.incident_date || item.date_posted);
            const initial = item.user ? item.user.charAt(0).toUpperCase() : "?";
            const username = item.user || "Ẩn danh";

            const imgHtml = item.image_url ? `
                <div class="h-48 w-full overflow-hidden bg-gray-100 relative group">
                    <img src="${esc(item.image_url)}" class="w-full h-full object-cover transition duration-500 group-hover:scale-110" loading="lazy">
                    <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition duration-300"></div>
                </div>` : "";

            html += `
            <div onclick="openDetailModal(${item.id})"
                 class="card-animate ${borderClass} bg-white rounded-xl shadow hover:shadow-xl transition duration-300 overflow-hidden relative border border-gray-100 flex flex-col cursor-pointer transform hover:-translate-y-1"
                 style="animation-delay:${i * 60}ms">
                ${imgHtml}
                <div class="p-6 flex-grow">
                    <div class="flex justify-between items-start mb-4">
                        <span class="inline-block px-3 py-1 rounded-full text-xs font-semibold shadow-sm ${badgeClasses}">${badgeText}</span>
                        <span class="text-gray-400 text-xs font-mono"><i class="far fa-clock mr-1"></i>${dateStr}</span>
                    </div>
                    <h3 class="text-xl font-bold text-gray-800 mb-2 truncate hover:text-orange-600 transition">${esc(item.title)}</h3>
                    <p class="text-gray-600 text-sm mb-4 line-clamp-2">${esc(item.description)}</p>
                    <div class="flex items-center text-gray-500 text-sm">
                        <i class="fas fa-map-marker-alt text-orange-500 mr-2"></i>${esc(item.location)}
                    </div>
                </div>
                <div class="px-6 py-4 bg-gray-50 border-t flex justify-between items-center text-sm">
                    <div class="flex items-center space-x-2">
                        <div class="w-8 h-8 rounded-full bg-white overflow-hidden border border-gray-200 shadow-sm flex items-center justify-center">
                            <img src="${item.user_avatar}" alt="${esc(username)}" class="w-full h-full object-cover">
                        </div>
                        <span class="font-medium text-gray-700 truncate max-w-[100px]">${esc(username)}</span>
                    </div>
                    <div class="flex items-center space-x-3">
                        ${item.phone_number ? `
                            <a href="tel:${esc(item.phone_number)}" onclick="event.stopPropagation()" class="text-green-600 hover:scale-110 transition-transform p-1" title="Gọi điện">
                                <i class="fas fa-phone-alt"></i>
                            </a>
                        ` : ''}
                        ${item.facebook_url ? `
                            <a href="${item.facebook_url.startsWith('http') ? esc(item.facebook_url) : 'https://www.facebook.com/' + esc(item.facebook_url)}" 
                               target="_blank" onclick="event.stopPropagation()" class="text-blue-600 hover:scale-110 transition-transform p-1" title="Facebook">
                                <i class="fab fa-facebook text-lg"></i>
                            </a>
                        ` : ''}
                        
                        ${(!item.phone_number && !item.facebook_url) ? `
                            <span class="text-orange-600 font-bold ml-1">Xem chi tiết <i class="fas fa-arrow-right ml-0.5"></i></span>
                        ` : `
                            <i class="fas fa-chevron-right text-gray-300 ml-1"></i>
                        `}
                    </div>
                </div>
            </div>`;
        });
        grid.innerHTML = html;

        // Pagination
        renderPagination(data.page, data.total_pages);
    }

    function renderEmptyState() {
        return `
        <div class="col-span-full text-center py-16">
            <div class="mx-auto mb-6 w-28 h-28 bg-gray-100 rounded-full flex items-center justify-center">
                <i class="fas fa-search-minus text-gray-300 text-5xl"></i>
            </div>
            <h3 class="text-xl font-bold text-gray-800 mb-2">Không tìm thấy kết quả</h3>
            <p class="text-gray-500 mb-6 max-w-md mx-auto">
                Rất tiếc, chưa có món đồ nào khớp với tìm kiếm của bạn.<br>
                Thử bỏ bớt một vài bộ lọc xem sao nhé!
            </p>
            <button onclick="resetAllFilters()"
                    class="px-6 py-2.5 border-2 border-orange-400 text-orange-600 rounded-lg font-semibold
                           hover:bg-orange-50 transition text-sm">
                <i class="fas fa-undo mr-1"></i> Xóa tất cả bộ lọc
            </button>
        </div>`;
    }

    // ─── Pagination ───────────────────────────────────────
    function renderPagination(current, total) {
        if (total <= 1) { paginationEl.innerHTML = ""; return; }
        let html = "";
        html += `<button class="page-btn" ${current === 1 ? "disabled" : ""} data-page="${current - 1}"><i class="fas fa-chevron-left text-xs"></i></button>`;

        const range = getPaginationRange(current, total);
        range.forEach(p => {
            if (p === "...") {
                html += `<span class="px-2 text-gray-400">…</span>`;
            } else {
                html += `<button class="page-btn ${p === current ? 'active' : ''}" data-page="${p}">${p}</button>`;
            }
        });

        html += `<button class="page-btn" ${current === total ? "disabled" : ""} data-page="${current + 1}"><i class="fas fa-chevron-right text-xs"></i></button>`;
        paginationEl.innerHTML = html;

        paginationEl.querySelectorAll(".page-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                if (btn.disabled) return;
                filters.page = parseInt(btn.dataset.page, 10);
                doSearch();
                window.scrollTo({ top: 0, behavior: "smooth" });
            });
        });
    }

    function getPaginationRange(current, total) {
        if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
        if (current <= 3) return [1, 2, 3, 4, "...", total];
        if (current >= total - 2) return [1, "...", total - 3, total - 2, total - 1, total];
        return [1, "...", current - 1, current, current + 1, "...", total];
    }

    // ─── Skeleton ─────────────────────────────────────────
    function showSkeleton() {
        let html = "";
        for (let i = 0; i < 6; i++) {
            html += `
            <div class="skeleton-card bg-white rounded-xl shadow border border-gray-100 flex flex-col">
                <div class="skeleton skeleton-img"></div>
                <div class="p-6">
                    <div class="skeleton skeleton-badge"></div>
                    <div class="skeleton skeleton-title"></div>
                    <div class="skeleton skeleton-text"></div>
                    <div class="skeleton skeleton-text2"></div>
                    <div class="skeleton skeleton-loc"></div>
                </div>
                <div class="px-6 py-4 bg-gray-50 border-t">
                    <div class="skeleton" style="height:14px;width:50%"></div>
                </div>
            </div>`;
        }
        grid.innerHTML = html;
    }

    // ─── Active filter tags ──────────────────────────────
    function updateActiveFilters() {
        const tags = [];
        if (filters.q) tags.push({ label: `"${filters.q}"`, key: "q" });
        if (filters.type) tags.push({ label: filters.type === "Lost" ? "Mất đồ" : "Nhặt được", key: "type" });
        if (filters.status === "Closed") tags.push({ label: "Đã hoàn trả", key: "status" });
        if (filters.status === "all") tags.push({ label: "Mọi trạng thái", key: "status" });
        if (filters.location) tags.push({ label: filters.location, key: "location" });
        if (filters.sub_location) tags.push({ label: filters.sub_location, key: "sub_location" });
        if (filters.category) tags.push({ label: filters.category, key: "category" });

        // Badge count
        const count = tags.length;
        if (count) {
            filterCountBadge.textContent = count;
            filterCountBadge.classList.remove("hidden");
        } else {
            filterCountBadge.classList.add("hidden");
        }

        // Tags
        if (!tags.length) {
            activeFiltersEl.classList.add("hidden");
            activeFiltersEl.innerHTML = "";
            return;
        }
        activeFiltersEl.classList.remove("hidden");
        let html = tags.map(t =>
            `<span class="active-tag">${esc(t.label)} <span class="remove-tag" data-key="${t.key}">&times;</span></span>`
        ).join("");
        html += `<button class="text-xs text-orange-600 hover:underline font-semibold ml-1" id="clear-all-filters">Xóa tất cả</button>`;
        activeFiltersEl.innerHTML = html;

        // Remove individual filter
        activeFiltersEl.querySelectorAll(".remove-tag").forEach(el => {
            el.addEventListener("click", () => {
                removeFilter(el.dataset.key);
            });
        });

        const clearAll = document.getElementById("clear-all-filters");
        if (clearAll) clearAll.addEventListener("click", resetAllFilters);
    }

    function removeFilter(key) {
        if (key === "q") { searchInput.value = ""; clearBtn.classList.add("hidden"); }
        if (key === "location") { locSelect.value = ""; subLocSelect.classList.add("hidden"); filters.sub_location = ""; }
        if (key === "sub_location") { subLocSelect.value = ""; }
        if (key === "category") { catSelect.value = ""; }
        if (key === "type") {
            document.querySelectorAll(".type-chip").forEach((c, i) => {
                c.className = "filter-chip " + (i === 0 ? "active-generic" : "inactive");
            });
        }
        if (key === "status") {
            document.querySelectorAll(".status-chip").forEach((c, i) => {
                c.className = "filter-chip " + (i === 0 ? "active-generic" : "inactive");
            });
        }
        filters[key] = "";
        filters.page = 1;
        doSearch();
    }

    // Expose globally so empty-state button can call it
    window.resetAllFilters = function () {
        filters = { q: "", type: "", status: "", location: "", sub_location: "", category: "", sort: "newest", page: 1 };
        searchInput.value = "";
        clearBtn.classList.add("hidden");
        clearBtn.classList.remove("flex");
        sortSelect.value = "newest";
        locSelect.value = "";
        subLocSelect.value = "";
        subLocSelect.classList.add("hidden");
        catSelect.value = "";
        // Reset chips
        document.querySelectorAll(".type-chip").forEach((c, i) => {
            c.className = "filter-chip " + (i === 0 ? "active-generic" : "inactive");
        });
        document.querySelectorAll(".status-chip").forEach((c, i) => {
            c.className = "filter-chip " + (i === 0 ? "active-generic" : "inactive");
        });
        doSearch();
    };

    // ─── Load metadata ────────────────────────────────────
    async function loadLocations() {
        try {
            const res = await fetch(API_LOCATIONS);
            locationsData = await res.json();
            locSelect.innerHTML = `<option value="">Tất cả khu vực</option>`;
            locationsData.forEach(loc => {
                locSelect.innerHTML += `<option value="${esc(loc.name)}">${esc(loc.name)}</option>`;
            });
        } catch (e) { console.error("Load locations error:", e); }
    }

    function populateSubLocations(locationName) {
        subLocSelect.innerHTML = `<option value="">Tất cả các khu vực</option>`;
        if (!locationName) { subLocSelect.classList.add("hidden"); return; }

        const loc = locationsData.find(l => l.name === locationName);
        if (loc && loc.sub_locations.length) {
            loc.sub_locations.forEach(s => {
                subLocSelect.innerHTML += `<option value="${esc(s)}">${esc(s)}</option>`;
            });
            subLocSelect.classList.remove("hidden");
        } else {
            subLocSelect.classList.add("hidden");
        }
    }

    async function loadCategories() {
        try {
            const res = await fetch(API_CATEGORIES);
            const cats = await res.json();
            catSelect.innerHTML = `<option value="">Tất cả danh mục</option>`;
            cats.forEach(c => {
                catSelect.innerHTML += `<option value="${esc(c)}">${esc(c)}</option>`;
            });
        } catch (e) { console.error("Load categories error:", e); }
    }

    // ─── Helpers ──────────────────────────────────────────
    function esc(str) {
        if (!str) return "";
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }

    function highlight(text, query) {
        if (!query) return text;
        const re = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi");
        return text.replace(re, `<mark class="bg-orange-100 text-orange-800 rounded px-0.5">$1</mark>`);
    }

    function formatDate(isoStr) {
        if (!isoStr) return "";
        const d = new Date(isoStr);
        const day = String(d.getDate()).padStart(2, "0");
        const month = String(d.getMonth() + 1).padStart(2, "0");
        const hours = String(d.getHours()).padStart(2, "0");
        const mins = String(d.getMinutes()).padStart(2, "0");
        return `${day}/${month} ${hours}:${mins}`;
    }

})();
