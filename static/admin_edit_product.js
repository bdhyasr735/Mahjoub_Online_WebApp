// ============================================================
// 🚀 التطبيق المتكامل لصفحة تعديل المنتج - النسخة الاحترافية
// (نسخة منسقة ومستقرة - تم تنظيفها بالكامل)
// ============================================================

(function() {
    'use strict';

    // ============================================================
    // 📝 TinyMCE Editor
    // ============================================================
    function initTinyMCE() {
        if (typeof tinymce === 'undefined') {
            console.warn('⚠️ TinyMCE غير محمل');
            return;
        }

        tinymce.init({
            selector: '#productDescription',
            height: 400,
            menubar: true,
            language: 'ar',
            directionality: 'rtl',
            plugins: [
                'advlist', 'autolink', 'lists', 'link', 'image', 'charmap',
                'preview', 'anchor', 'searchreplace', 'visualblocks', 'code',
                'fullscreen', 'insertdatetime', 'media', 'table', 'help', 'wordcount'
            ],
            toolbar: [
                'undo redo | blocks | fontfamily fontsize',
                'bold italic underline strikethrough | forecolor backcolor | ' +
                'alignleft aligncenter alignright alignjustify',
                'bullist numlist | outdent indent | link image media | table | code',
                'removeformat | fullscreen | help'
            ],
            content_style: `
                body {
                    font-family: "Cairo", system-ui, sans-serif;
                    font-size: 16px;
                    line-height: 1.8;
                    padding: 20px;
                    color: #1e293b;
                }
                h1, h2, h3, h4 { color: #0f172a; }
                a { color: #D4AF37; text-decoration: underline; }
                table {
                    border-collapse: collapse;
                    width: 100%;
                    margin: 16px 0;
                }
                th, td {
                    border: 1px solid #e2e8f0;
                    padding: 8px 12px;
                    text-align: right;
                }
                th { background: #f1f5f9; font-weight: 600; }
                blockquote {
                    border-right: 4px solid #D4AF37;
                    padding: 12px 20px;
                    background: #f8fafc;
                    border-radius: 4px;
                    margin: 16px 0;
                }
                img {
                    max-width: 100%;
                    height: auto;
                    border-radius: 8px;
                }
            `,
            images_upload_handler: function(blobInfo) {
                return new Promise(function(resolve) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        resolve(e.target.result);
                    };
                    reader.readAsDataURL(blobInfo.blob());
                });
            },
            setup: function(editor) {
                editor.on('change', function() {
                    const descInput = document.querySelector('textarea[name="description"]');
                    if (descInput) {
                        descInput.value = editor.getContent();
                    }
                });
            }
        });
    }

    // ============================================================
    // 📂 إدارة المجموعات
    // ============================================================
    function initCollectionHandlers() {
        document.addEventListener('click', function(e) {
            const container = document.querySelector('.collection-multiselect-container');
            if (container && !container.contains(e.target)) {
                const menu = document.getElementById('collectionDropdownMenu');
                if (menu) menu.style.display = 'none';
            }
        });
    }

    function toggleCollectionDropdown() {
        const menu = document.getElementById('collectionDropdownMenu');
        if (!menu) return;
        menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
        if (menu.style.display === 'block') {
            const input = document.getElementById('collectionSearchInput');
            if (input) {
                input.focus();
                input.value = '';
                filterCollections('');
            }
        }
    }

    function filterCollections(query) {
        const items = document.querySelectorAll('.collection-option-item');
        query = query.toLowerCase().trim();
        let visibleCount = 0;
        items.forEach(item => {
            const title = item.getAttribute('data-title') || '';
            const isVisible = title.toLowerCase().includes(query);
            item.style.display = isVisible ? 'flex' : 'none';
            if (isVisible) visibleCount++;
        });
        const noResults = document.getElementById('collectionsNoResults');
        if (noResults) {
            noResults.style.display = visibleCount === 0 ? 'block' : 'none';
        }
    }

    function toggleCollectionSelection(element, id, title) {
        const checkbox = element.querySelector('.col-checkbox');
        if (!checkbox) return;
        checkbox.checked = !checkbox.checked;
        if (checkbox.checked) {
            addCollectionBadge(id, title);
            element.classList.add('selected');
        } else {
            removeCollection(id);
            element.classList.remove('selected');
        }
    }

    function addCollectionBadge(id, title) {
        const box = document.getElementById('selectedCollectionsBox');
        if (!box) return;
        const placeholder = document.getElementById('collectionPlaceholder');
        if (placeholder) placeholder.style.display = 'none';
        if (box.querySelector(`[data-id="${id}"]`)) return;

        const badge = document.createElement('span');
        badge.className = 'collection-badge';
        badge.setAttribute('data-id', id);
        badge.innerHTML = `
            <i class="fas fa-folder"></i> ${title}
            <span class="remove-collection" onclick="event.stopPropagation(); removeCollection('${id}')">&times;</span>
        `;
        box.appendChild(badge);

        const hiddenContainer = document.getElementById('hiddenCollectionsInputs');
        if (hiddenContainer && !document.getElementById(`col-input-${id}`)) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'collection_ids';
            input.value = id;
            input.id = `col-input-${id}`;
            hiddenContainer.appendChild(input);
        }
        updateCollectionsCount();
    }

    function removeCollection(id) {
        const box = document.getElementById('selectedCollectionsBox');
        if (!box) return;
        const badge = box.querySelector(`[data-id="${id}"]`);
        if (badge) badge.remove();

        const input = document.getElementById(`col-input-${id}`);
        if (input) input.remove();

        const checkbox = document.querySelector(`.collection-option-item[data-id="${id}"] .col-checkbox`);
        if (checkbox) checkbox.checked = false;

        const remaining = box.querySelectorAll('.collection-badge');
        const placeholder = document.getElementById('collectionPlaceholder');
        if (placeholder && remaining.length === 0) {
            placeholder.style.display = 'block';
        }
        updateCollectionsCount();
    }

    function updateCollectionsCount() {
        const box = document.getElementById('selectedCollectionsBox');
        if (!box) return;
        const count = box.querySelectorAll('.collection-badge').length;
        const display = document.getElementById('selectedCountDisplay');
        if (display) display.textContent = count;
    }

    // ============================================================
    // 🖼️ إدارة الصور
    // ============================================================
    function initImageHandlers() {
        const uploadArea = document.getElementById('imageUploadArea');
        const input = document.getElementById('imageInput');
        if (!uploadArea || !input) return;

        uploadArea.addEventListener('click', function() {
            input.click();
        });

        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.style.borderColor = '#D4AF37';
            this.style.background = 'rgba(212, 175, 55, 0.05)';
        });

        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.style.borderColor = '';
            this.style.background = '';
        });

        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            this.style.borderColor = '';
            this.style.background = '';
            if (e.dataTransfer.files.length > 0) {
                input.files = e.dataTransfer.files;
                input.dispatchEvent(new Event('change'));
            }
        });

        input.addEventListener('change', function() {
            const files = this.files;
            const grid = document.getElementById('imagePreviewGrid');
            if (!grid) return;

            const emptyMsg = grid.querySelector('.text-center.text-muted');
            if (emptyMsg) emptyMsg.remove();

            for (let i = 0; i < files.length; i++) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    const div = document.createElement('div');
                    div.className = 'image-preview-item';
                    div.innerHTML = `
                        <img src="${event.target.result}" alt="صورة المنتج">
                        <button type="button" class="remove-image" onclick="this.parentElement.remove();">✕</button>
                    `;
                    grid.appendChild(div);
                };
                reader.readAsDataURL(files[i]);
            }
            this.value = '';
        });
    }

    // ============================================================
    // 🧩 إدارة المتغيرات
    // ============================================================
    function addOptionRow() {
        const container = document.getElementById('optionsContainer');
        if (!container) return;

        const row = document.createElement('div');
        row.className = 'option-row p-3 rounded-3 bg-white';
        row.innerHTML = `
            <div class="option-header d-flex gap-2 mb-2 flex-wrap">
                <input type="text" class="form-control custom-input opt-name"
                       placeholder="اسم الخيار (مثل: اللون)"
                       oninput="generatePayload()" style="flex:1;min-width:150px;">
                <button class="btn btn-outline-danger btn-sm px-3 delete-opt-btn"
                        type="button" onclick="removeOptionRow(this)" title="حذف الخيار">
                    <i class="fas fa-trash-alt"></i> حذف
                </button>
            </div>
            <label class="form-label text-muted" style="font-size:0.85rem;margin-bottom:6px;">
                القيم المتعددة:
            </label>
            <div class="values-container d-flex flex-wrap gap-2 mb-2"></div>
            <div class="add-value-group input-group input-group-sm">
                <input type="text" class="form-control custom-input val-input"
                       placeholder="أدخل قيمة ثم اضغط إضافة (مثل: أحمر)">
                <button class="btn btn-gold-gradient" type="button" onclick="addValueToRow(this)">
                    <i class="fas fa-plus me-1"></i> إضافة قيمة
                </button>
            </div>
        `;
        container.appendChild(row);
    }

    function removeOptionRow(button) {
        const row = button.closest('.option-row');
        if (!row) return;
        if (row.parentElement.children.length <= 1) {
            alert('⚠️ يجب أن يبقى خيار واحد على الأقل');
            return;
        }
        if (confirm('⚠️ هل أنت متأكد من حذف هذا الخيار؟')) {
            row.remove();
            updateVariantsTable();
            generatePayload();
        }
    }

    function addValueToRow(button) {
        const row = button.closest('.option-row');
        if (!row) return;

        const input = row.querySelector('.val-input');
        if (!input) return;

        const value = input.value.trim();
        if (!value) {
            alert('⚠️ الرجاء إدخال قيمة');
            return;
        }

        const container = row.querySelector('.values-container');
        if (!container) return;

        const existing = container.querySelectorAll('.value-tag');
        for (let tag of existing) {
            if (tag.textContent.trim().replace('×', '').trim() === value) {
                alert('⚠️ هذه القيمة موجودة بالفعل');
                return;
            }
        }

        const tag = document.createElement('div');
        tag.className = 'value-tag';
        tag.innerHTML = `
            ${value}
            <span onclick="this.closest('.value-tag').remove(); updateVariantsTable(); generatePayload();">&times;</span>
        `;
        container.appendChild(tag);

        input.value = '';
        input.focus();
        updateVariantsTable();
        generatePayload();
    }

    function cartesianProduct(arr) {
        return arr.reduce((a, b) => a.flatMap(d => b.map(e => [].concat(d, e))), [[]]);
    }

    function updateVariantsTable() {
        const optionRows = document.querySelectorAll('.option-row');
        const valuesArrays = [];

        optionRows.forEach(row => {
            const optName = row.querySelector('.opt-name').value.trim();
            const tags = row.querySelectorAll('.value-tag');
            const values = Array.from(tags).map(tag =>
                tag.textContent.trim().replace('×', '').trim()
            );
            if (optName && values.length > 0) {
                valuesArrays.push(values);
            }
        });

        const container = document.getElementById('variantsTableContainer');
        if (!container) return;

        if (valuesArrays.length === 0) {
            container.innerHTML = `
                <p class="text-muted text-center">
                    قم بإضافة الخيارات والقيم لتوليد جدول المتغيرات تلقائياً...
                </p>
            `;
            return;
        }

        const combinations = cartesianProduct(valuesArrays);
        let html = `
            <table class="table table-bordered variants-table">
                <thead>
                    <tr>
                        <th>المتغير</th>
                        <th>SKU</th>
                        <th>السعر</th>
                        <th>الكمية</th>
                    </tr>
                </thead>
                <tbody>
        `;

        combinations.forEach((combo, index) => {
            const variantLabel = combo.join(' / ');
            html += `
                <tr data-index="${index}">
                    <td><strong>${variantLabel}</strong></td>
                    <td>
                        <input type="text" class="var-sku form-control"
                               value="SKU-${String(index + 1).padStart(3, '0')}"
                               oninput="generatePayload()">
                    </td>
                    <td>
                        <input type="text" class="var-price form-control"
                               value="0" oninput="generatePayload()">
                    </td>
                    <td>
                        <input type="text" class="var-qty form-control"
                               value="0" oninput="generatePayload()">
                    </td>
                </tr>
            `;
        });

        html += `</tbody></table>`;
        container.innerHTML = html;
        generatePayload();
    }

    // 🔄 تحميل الخيارات والمتغيرات الحالية للمنتج عند فتح الصفحة
    function initExistingVariants(existingOptions, existingVariants) {
        if (!existingOptions || !Array.isArray(existingOptions) || existingOptions.length === 0) return;

        const container = document.getElementById('optionsContainer');
        if (!container) return;

        container.innerHTML = '';

        existingOptions.forEach(opt => {
            const row = document.createElement('div');
            row.className = 'option-row p-3 rounded-3 bg-white';

            let valuesHtml = '';
            if (opt.values && Array.isArray(opt.values)) {
                opt.values.forEach(val => {
                    const valText = typeof val === 'object' ?
                        (val.label || val.name || '') :
                        val;
                    if (valText) {
                        valuesHtml += `
                            <div class="value-tag">
                                ${valText}
                                <span onclick="this.closest('.value-tag').remove(); updateVariantsTable(); generatePayload();">&times;</span>
                            </div>
                        `;
                    }
                });
            }

            row.innerHTML = `
                <div class="option-header d-flex gap-2 mb-2 flex-wrap">
                    <input type="text" class="form-control custom-input opt-name"
                           value="${opt.name || ''}"
                           placeholder="اسم الخيار (مثل: اللون)"
                           oninput="generatePayload()" style="flex:1;min-width:150px;">
                    <button class="btn btn-outline-danger btn-sm px-3 delete-opt-btn"
                            type="button" onclick="removeOptionRow(this)" title="حذف الخيار">
                        <i class="fas fa-trash-alt"></i> حذف
                    </button>
                </div>
                <label class="form-label text-muted" style="font-size:0.85rem;margin-bottom:6px;">
                    القيم المتعددة:
                </label>
                <div class="values-container d-flex flex-wrap gap-2 mb-2">${valuesHtml}</div>
                <div class="add-value-group input-group input-group-sm">
                    <input type="text" class="form-control custom-input val-input"
                           placeholder="أدخل قيمة ثم اضغط إضافة (مثل: أحمر)">
                    <button class="btn btn-gold-gradient" type="button" onclick="addValueToRow(this)">
                        <i class="fas fa-plus me-1"></i> إضافة قيمة
                    </button>
                </div>
            `;
            container.appendChild(row);
        });

        updateVariantsTable();

        // تعبئة بيانات المتغيرات إذا كانت موجودة
        if (existingVariants && Array.isArray(existingVariants) && existingVariants.length > 0) {
            const variantRows = document.querySelectorAll(
                '#variantsTableContainer table tbody tr, .variants-table tbody tr'
            );
            variantRows.forEach((tr, index) => {
                if (existingVariants[index]) {
                    const v = existingVariants[index];
                    const skuInput = tr.querySelector('.var-sku');
                    const priceInput = tr.querySelector('.var-price');
                    const qtyInput = tr.querySelector('.var-qty');

                    if (skuInput && v.sku) skuInput.value = v.sku;
                    if (priceInput && (v.price !== undefined)) priceInput.value = v.price;
                    if (qtyInput && (v.quantity !== undefined)) qtyInput.value = v.quantity;
                }
            });
        }
        generatePayload();
    }

    function generatePayload() {
        const title = document.getElementById('productTitle')?.value ||
            document.querySelector('input[name="title"]')?.value || '';
        const slug = document.getElementById('productSlug')?.value || '';

        const optionRows = document.querySelectorAll('.option-row');
        const options = [];
        optionRows.forEach(row => {
            const name = row.querySelector('.opt-name')?.value.trim() || '';
            const tags = row.querySelectorAll('.value-tag');
            const values = Array.from(tags).map(tag =>
                tag.textContent.trim().replace('×', '').trim()
            );
            if (name && values.length > 0) {
                options.push({
                    name,
                    values: values.map((label, index) => ({ label, sortOrder: index }))
                });
            }
        });

        const variantRows = document.querySelectorAll(
            '#variantsTableContainer table tbody tr, .variants-table tbody tr'
        );
        const variants = [];
        variantRows.forEach((tr, index) => {
            const sku = tr.querySelector('.var-sku')?.value ||
                `SKU-${String(index + 1).padStart(3, '0')}`;
            const price = parseFloat(tr.querySelector('.var-price')?.value) || 0;
            const quantity = parseInt(tr.querySelector('.var-qty')?.value) || 0;
            variants.push({ sku, price, compareAtPrice: 0, quantity });
        });

        const payload = {
            input: {
                title: title || '',
                slug: slug || '',
                status: 'active',
                options,
                variants
            }
        };
        const payloadInput = document.getElementById('variantsPayloadInput');
        if (payloadInput) {
            payloadInput.value = JSON.stringify(payload);
        }
    }

    function preparePayloadBeforeSubmit(e) {
        generatePayload();
    }

    // ============================================================
    // 🏷️ إدارة العلامات
    // ============================================================
    function initTagHandlers() {
        const input = document.getElementById('tagInput');
        if (input) {
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    addTag();
                }
            });
        }
    }

    function addTag() {
        const input = document.getElementById('tagInput');
        if (!input) return;
        const tag = input.value.trim();
        if (!tag) {
            alert('⚠️ الرجاء إدخال علامة');
            return;
        }

        const container = document.getElementById('tagsContainer');
        if (!container) return;

        const existing = container.querySelectorAll('.tag-item');
        for (let item of existing) {
            if (item.textContent.trim().replace('✕', '').trim() === tag) {
                alert('⚠️ هذه العلامة موجودة بالفعل');
                return;
            }
        }

        const noTagsMsg = container.querySelector('.text-muted');
        if (noTagsMsg) noTagsMsg.remove();

        const span = document.createElement('span');
        span.className = 'tag-item';
        span.innerHTML = `
            <span class="remove-tag" onclick="this.parentElement.remove();">✕</span> ${tag}
        `;
        container.appendChild(span);

        input.value = '';
        input.focus();
    }

    // ============================================================
    // 🗑️ حذف المنتج
    // ============================================================
    function deleteProduct(id, name) {
        if (!confirm(`⚠️ هل أنت متأكد من حذف المنتج "${name}"؟`)) return;

        const csrfToken = document.querySelector('[name="csrf_token"]')?.value || '';
        fetch(`/admin/products/delete/${id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                alert('✅ ' + data.message);
                window.location.href = '/admin/products';
            } else {
                alert('❌ ' + data.message);
            }
        })
        .catch(e => alert('❌ حدث خطأ: ' + e.message));
    }

    // ============================================================
    // 🔔 نظام الإشعارات
    // ============================================================
    function showNotification(message, type = 'success') {
        const colors = {
            success: '#22c55e',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };

        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: white;
            padding: 16px 24px;
            border-radius: 12px;
            box-shadow: 0 12px 48px rgba(0,0,0,0.15);
            border-right: 4px solid ${colors[type] || '#3b82f6'};
            z-index: 99999;
            font-weight: 600;
            font-size: 0.95rem;
            max-width: 400px;
            animation: slideIn 0.4s cubic-bezier(0.4,0,0.2,1);
            display: flex;
            align-items: center;
            gap: 10px;
            backdrop-filter: blur(8px);
        `;
        toast.innerHTML = `${icons[type] || 'ℹ️'} ${message}`;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.4s cubic-bezier(0.4,0,0.2,1)';
            setTimeout(() => toast.remove(), 400);
        }, 4000);
    }

    // ============================================================
    // 🚀 التهيئة الرئيسية
    // ============================================================
    function init() {
        // إضافة أنماط الإشعارات
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100px); opacity: 0; }
            }
        `;
        document.head.appendChild(style);

        initTinyMCE();
        initCollectionHandlers();
        initImageHandlers();
        initTagHandlers();
        updateCollectionsCount();

        // ربط الدوال بالـ window لضمان عمل الأزرار داخل القوالب
        window.addOptionRow = addOptionRow;
        window.removeOptionRow = removeOptionRow;
        window.addValueToRow = addValueToRow;
        window.generatePayload = generatePayload;
        window.initExistingVariants = initExistingVariants;
        window.preparePayloadBeforeSubmit = preparePayloadBeforeSubmit;
        window.deleteProduct = deleteProduct;
        window.showNotification = showNotification;
        window.toggleCollectionDropdown = toggleCollectionDropdown;
        window.filterCollections = filterCollections;
        window.toggleCollectionSelection = toggleCollectionSelection;
        window.addCollectionBadge = addCollectionBadge;
        window.removeCollection = removeCollection;
        window.addTag = addTag;

        console.log('✅ [admin_edit_product] تم تهيئة جميع الوظائف بنجاح تام');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
