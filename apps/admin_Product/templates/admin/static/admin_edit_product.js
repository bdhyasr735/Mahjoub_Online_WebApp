// static/admin_edit_product.js
// ============================================================
// 🚀 التطبيق المتكامل لصفحة تعديل المنتج - النسخة الاحترافية
// ============================================================

(function() {
    'use strict';

    // ============================================================
    // 📝 TinyMCE Editor - محرر النصوص المتقدم
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
                'bold italic underline strikethrough | forecolor backcolor | alignleft aligncenter alignright alignjustify',
                'bullist numlist | outdent indent | link image media | table | code',
                'removeformat | fullscreen | help'
            ],
            
            font_family_formats: [
                'Cairo=ج', 'Arial=Arial', 'Helvetica=Helvetica',
                'Times New Roman=Times New Roman', 'Georgia=Georgia',
                'Tahoma=Tahoma', 'Verdana=Verdana'
            ].join(';'),
            
            font_size_formats: '8pt 10pt 12pt 14pt 18pt 24pt 36pt 48pt 72pt',
            
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
                table { border-collapse: collapse; width: 100%; margin: 16px 0; }
                th, td { border: 1px solid #e2e8f0; padding: 8px 12px; text-align: right; }
                th { background: #f1f5f9; font-weight: 600; }
                blockquote { 
                    border-right: 4px solid #D4AF37; 
                    padding: 12px 20px; 
                    background: #f8fafc;
                    border-radius: 4px;
                    margin: 16px 0;
                }
                img { max-width: 100%; height: auto; border-radius: 8px; }
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
                    document.querySelector('textarea[name="description"]').value = editor.getContent();
                });
            }
        });
    }

    // ============================================================
    // 📂 إدارة المجموعات
    // ============================================================
    function initCollectionHandlers() {
        // إغلاق القائمة عند النقر خارجها
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
        
        const isOpen = menu.style.display === 'block';
        menu.style.display = isOpen ? 'none' : 'block';
        
        if (!isOpen) {
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
        const normalizedQuery = query.toLowerCase().trim();
        let visibleCount = 0;
        
        items.forEach(item => {
            const title = item.getAttribute('data-title') || '';
            const isVisible = title.toLowerCase().includes(normalizedQuery);
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
        
        // إخفاء placeholder
        const placeholder = document.getElementById('collectionPlaceholder');
        if (placeholder) placeholder.style.display = 'none';
        
        // منع التكرار
        if (box.querySelector(`.collection-badge[data-id="${id}"]`)) return;
        
        // إنشاء badge
        const badge = document.createElement('span');
        badge.className = 'collection-badge';
        badge.setAttribute('data-id', id);
        badge.innerHTML = `
            <i class="fas fa-folder"></i> 
            ${title} 
            <span class="remove-collection" onclick="event.stopPropagation(); removeCollection('${id}')">&times;</span>
        `;
        box.appendChild(badge);
        
        // إضافة الحقل المخفي
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
        
        // حذف badge
        const badge = box.querySelector(`.collection-badge[data-id="${id}"]`);
        if (badge) badge.remove();
        
        // حذف الحقل المخفي
        const input = document.getElementById(`col-input-${id}`);
        if (input) input.remove();
        
        // تحديث checkbox
        const checkbox = document.querySelector(`.collection-option-item[data-id="${id}"] .col-checkbox`);
        if (checkbox) checkbox.checked = false;
        
        // إظهار placeholder إذا لم يتبقى مجموعات
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
        
        const badge = document.querySelector('.collection-count-badge');
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline-block' : 'none';
        }
    }

    // ============================================================
    // 🖼️ إدارة الصور
    // ============================================================
    function initImageHandlers() {
        const uploadArea = document.getElementById('imageUploadArea');
        const input = document.getElementById('imageInput');
        
        if (!uploadArea || !input) return;
        
        // رفع بالضغط
        uploadArea.addEventListener('click', function() {
            input.click();
        });
        
        // سحب وإفلات
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
        
        // معاينة الصور
        input.addEventListener('change', function() {
            const files = this.files;
            const grid = document.getElementById('imagePreviewGrid');
            if (!grid) return;
            
            // إزالة رسالة "لا توجد صور"
            const emptyMsg = grid.querySelector('.text-center.text-muted');
            if (emptyMsg) emptyMsg.remove();
            
            for (let i = 0; i < files.length; i++) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    const div = document.createElement('div');
                    div.className = 'image-preview-item';
                    div.innerHTML = `
                        <img src="${event.target.result}" alt="صورة المنتج" loading="lazy">
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
        row.className = 'option-row';
        row.innerHTML = `
            <div class="option-header">
                <input type="text" class="opt-name" placeholder="اسم الخيار (مثل: المقاس)" oninput="generatePayload()">
                <button class="btn-action btn-danger" type="button" onclick="removeOptionRow(this)">🗑️ حذف</button>
            </div>
            <label style="font-size: 0.85rem; color: #64748b;">القيم المتعددة:</label>
            <div class="values-container"></div>
            <div class="add-value-group">
                <input type="text" class="val-input" placeholder="أدخل قيمة" onkeypress="if(event.key==='Enter'){event.preventDefault();addValueToRow(this.closest('.add-value-group').querySelector('button'));}">
                <button class="btn-action" type="button" onclick="addValueToRow(this)">➕ إضافة</button>
            </div>
        `;
        container.appendChild(row);
        row.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function removeOptionRow(button) {
        const row = button.closest('.option-row');
        if (!row) return;
        
        if (row.parentElement.children.length <= 1) {
            showNotification('⚠️ يجب أن يبقى خيار واحد على الأقل', 'warning');
            return;
        }
        
        if (confirm('⚠️ هل أنت متأكد من حذف هذا الخيار وجميع قيمه؟')) {
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
            showNotification('⚠️ الرجاء إدخال قيمة', 'warning');
            return;
        }
        
        const container = row.querySelector('.values-container');
        if (!container) return;
        
        // منع التكرار
        const existing = container.querySelectorAll('.value-tag');
        for (let tag of existing) {
            if (tag.textContent.trim().replace('×', '').trim() === value) {
                showNotification('⚠️ هذه القيمة موجودة بالفعل', 'warning');
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

    function updateVariantsTable() {
        const optionRows = document.querySelectorAll('.option-row');
        const valuesArrays = [];
        
        optionRows.forEach(row => {
            const optName = row.querySelector('.opt-name').value.trim();
            const tags = row.querySelectorAll('.value-tag');
            const values = Array.from(tags).map(tag => tag.textContent.trim().replace('×', '').trim());
            
            if (optName && values.length > 0) {
                valuesArrays.push(values);
            }
        });
        
        const container = document.getElementById('variantsTableContainer');
        if (!container) return;
        
        if (valuesArrays.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5 text-muted">
                    <i class="fas fa-cubes fa-3x mb-3 d-block" style="color: #D4AF37;"></i>
                    <p class="mb-0">قم بإضافة الخيارات والقيم لتوليد جدول المتغيرات</p>
                </div>
            `;
            return;
        }
        
        const combinations = cartesianProduct(valuesArrays);
        let html = `
            <div class="table-responsive">
                <table class="variants-table">
                    <thead>
                        <tr>
                            <th>المتغير</th>
                            <th>صورة</th>
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
                        <div class="variant-img-wrapper">
                            <input type="file" class="var-img-file" accept="image/*" style="display:none;" onchange="handleVariantImage(this, ${index})">
                            <img id="thumb-${index}" class="variant-thumb" src="" alt="صورة المتغير">
                            <button class="btn-action btn-sm" onclick="this.previousElementSibling.previousElementSibling.click()">📷</button>
                            <button id="del-btn-${index}" class="btn-action btn-danger btn-sm" style="display:none;" onclick="removeVariantImage(${index})">×</button>
                        </div>
                    </td>
                    <td><input type="text" class="var-sku" value="SKU-${String(index + 1).padStart(3, '0')}" oninput="generatePayload()"></td>
                    <td><input type="number" class="var-price" value="0" step="0.01" oninput="generatePayload()" dir="ltr"></td>
                    <td><input type="number" class="var-qty" value="0" oninput="generatePayload()" dir="ltr"></td>
                </tr>
            `;
        });
        
        html += `</tbody></table></div>`;
        container.innerHTML = html;
        generatePayload();
    }

    function cartesianProduct(arr) {
        return arr.reduce((a, b) => a.flatMap(d => b.map(e => [].concat(d, e))), [[]]);
    }

    function handleVariantImage(input, index) {
        const file = input.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = function(e) {
            const thumb = document.getElementById(`thumb-${index}`);
            const delBtn = document.getElementById(`del-btn-${index}`);
            if (thumb) {
                thumb.src = e.target.result;
                thumb.style.display = 'block';
            }
            if (delBtn) delBtn.style.display = 'inline-block';
            generatePayload();
        };
        reader.readAsDataURL(file);
    }

    function removeVariantImage(index) {
        const tr = document.querySelector(`tr[data-index="${index}"]`);
        if (tr) {
            const input = tr.querySelector('.var-img-file');
            if (input) input.value = '';
        }
        
        const thumb = document.getElementById(`thumb-${index}`);
        const delBtn = document.getElementById(`del-btn-${index}`);
        if (thumb) {
            thumb.src = '';
            thumb.style.display = 'none';
        }
        if (delBtn) delBtn.style.display = 'none';
        generatePayload();
    }

    function generatePayload() {
        const title = document.getElementById('productTitle')?.value || '';
        const slug = document.getElementById('productSlug')?.value || '';
        
        const optionRows = document.querySelectorAll('.option-row');
        const options = [];
        
        optionRows.forEach(row => {
            const name = row.querySelector('.opt-name')?.value.trim() || '';
            const tags = row.querySelectorAll('.value-tag');
            const values = Array.from(tags).map(tag => tag.textContent.trim().replace('×', '').trim());
            
            if (name && values.length > 0) {
                options.push({
                    name: name,
                    values: values.map((label, index) => ({ label, sortOrder: index }))
                });
            }
        });
        
        const variantRows = document.querySelectorAll('.variants-table tbody tr');
        const variants = [];
        
        variantRows.forEach((tr, index) => {
            const sku = tr.querySelector('.var-sku')?.value || `SKU-${String(index + 1).padStart(3, '0')}`;
            const price = parseFloat(tr.querySelector('.var-price')?.value) || 0;
            const quantity = parseInt(tr.querySelector('.var-qty')?.value) || 0;
            
            const optionValuesText = tr.querySelector('td:first-child strong')?.textContent || '';
            const optionValues = optionValuesText.split(' / ');
            
            const thumb = document.getElementById(`thumb-${index}`);
            const image = (thumb && thumb.style.display === 'block') ? thumb.src : null;
            
            variants.push({
                sku,
                price,
                compareAtPrice: 0,
                quantity,
                optionValues,
                image
            });
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
            showNotification('⚠️ الرجاء إدخال علامة', 'warning');
            return;
        }
        
        const container = document.getElementById('tagsContainer');
        if (!container) return;
        
        // منع التكرار
        const existing = container.querySelectorAll('.tag-item');
        for (let item of existing) {
            if (item.textContent.trim().replace('✕', '').trim() === tag) {
                showNotification('⚠️ هذه العلامة موجودة بالفعل', 'warning');
                return;
            }
        }
        
        // إزالة رسالة "لا توجد علامات"
        const noTagsMsg = container.querySelector('.text-muted');
        if (noTagsMsg) noTagsMsg.remove();
        
        const span = document.createElement('span');
        span.className = 'tag-item';
        span.innerHTML = `
            <span class="remove-tag" onclick="this.parentElement.remove();">✕</span> 
            ${tag}
        `;
        container.appendChild(span);
        input.value = '';
        input.focus();
    }

    // ============================================================
    // 🗑️ حذف المنتج
    // ============================================================
    function deleteProduct(qid, name) {
        if (!confirm(`⚠️ هل أنت متأكد من حذف/أرشفة المنتج "${name}"؟\nلا يمكن التراجع عن هذا الإجراء!`)) return;
        
        const csrfToken = document.querySelector('[name="csrf_token"]')?.value || '';
        
        fetch(`{{ url_for('admin_product_bp.delete_product', qid='') }}${qid}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('✅ ' + data.message, 'success');
                setTimeout(() => {
                    window.location.href = '{{ url_for("admin_product_bp.manage_products_view") }}';
                }, 1500);
            } else {
                showNotification('❌ ' + data.message, 'error');
            }
        })
        .catch(error => {
            showNotification('❌ حدث خطأ: ' + error.message, 'error');
        });
    }

    // ============================================================
    // 🔔 نظام الإشعارات
    // ============================================================
    function showNotification(message, type = 'success') {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        
        const colors = {
            success: '#22c55e',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };
        
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || 'ℹ️'}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">✕</button>
        `;
        
        // أنماط الإشعار
        Object.assign(toast.style, {
            position: 'fixed',
            bottom: '24px',
            right: '24px',
            background: '#ffffff',
            padding: '16px 24px',
            borderRadius: '12px',
            boxShadow: '0 12px 48px rgba(0,0,0,0.12)',
            borderRight: `4px solid ${colors[type]}`,
            zIndex: '99999',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            fontFamily: 'system-ui, sans-serif',
            fontSize: '0.95rem',
            fontWeight: '600',
            color: '#1e293b',
            maxWidth: '420px',
            animation: 'slideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
            backdropFilter: 'blur(8px)',
            background: 'rgba(255,255,255,0.95)'
        });
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
            setTimeout(() => toast.remove(), 400);
        }, 4000);
    }

    // ============================================================
    // 🎨 إضافة أنماط الإشعارات
    // ============================================================
    function addNotificationStyles() {
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
            .toast-close {
                background: none;
                border: none;
                cursor: pointer;
                font-size: 1.2rem;
                color: #94a3b8;
                padding: 0 4px;
                transition: all 0.3s ease;
            }
            .toast-close:hover {
                color: #ef4444;
                transform: rotate(90deg);
            }
        `;
        document.head.appendChild(style);
    }

    // ============================================================
    // 🚀 التهيئة الرئيسية
    // ============================================================
    function init() {
        // إضافة أنماط الإشعارات
        addNotificationStyles();
        
        // تهيئة المكونات
        initTinyMCE();
        initCollectionHandlers();
        initImageHandlers();
        initTagHandlers();
        
        // تحديث عداد المجموعات
        updateCollectionsCount();
        
        // ربط دوال المتغيرات بالـ window
        window.addOptionRow = addOptionRow;
        window.removeOptionRow = removeOptionRow;
        window.addValueToRow = addValueToRow;
        window.handleVariantImage = handleVariantImage;
        window.removeVariantImage = removeVariantImage;
        window.generatePayload = generatePayload;
        window.preparePayloadBeforeSubmit = preparePayloadBeforeSubmit;
        window.deleteProduct = deleteProduct;
        window.showNotification = showNotification;
        
        // ربط دوال المجموعات
        window.toggleCollectionDropdown = toggleCollectionDropdown;
        window.filterCollections = filterCollections;
        window.toggleCollectionSelection = toggleCollectionSelection;
        window.addCollectionBadge = addCollectionBadge;
        window.removeCollection = removeCollection;
        
        // ربط دوال العلامات
        window.addTag = addTag;
        
        console.log('✅ [admin_edit_product] تم تهيئة جميع الوظائف بنجاح');
    }

    // التهيئة عند تحميل الصفحة
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
