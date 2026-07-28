// static/admin_edit_product.js
// ============================================================
// 🚀 التطبيق المتكامل لصفحة تعديل المنتج
// ============================================================

// ============================================================
// 📝 TinyMCE Editor - محرر النصوص المتقدم
// ============================================================
function initTinyMCE() {
    tinymce.init({
        selector: '#productDescription',
        height: 350,
        menubar: true,
        plugins: [
            'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
            'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
            'insertdatetime', 'media', 'table', 'help', 'wordcount'
        ],
        toolbar: 'undo redo | blocks | ' +
            'bold italic backcolor | alignleft aligncenter ' +
            'alignright alignjustify | bullist numlist outdent indent | ' +
            'removeformat | help | link image media | fullscreen | code',
        content_style: 'body { font-family: "Cairo", system-ui, sans-serif; font-size: 16px; line-height: 1.8; padding: 12px; }',
        directionality: 'rtl',
        language: 'ar',
        images_upload_handler: function(blobInfo, progress) {
            return new Promise(function(resolve, reject) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    resolve(e.target.result);
                };
                reader.readAsDataURL(blobInfo.blob());
            });
        }
    });
}

// ============================================================
// 📂 إدارة المجموعات (Collections) - البحث والاختيار المتعدد
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
    let hasVisible = false;
    
    items.forEach(item => {
        const title = item.getAttribute('data-title') || '';
        const isVisible = title.toLowerCase().includes(query);
        item.style.display = isVisible ? 'flex' : 'none';
        if (isVisible) hasVisible = true;
    });
    
    const noResults = document.getElementById('collectionsNoResults');
    if (noResults) {
        noResults.style.display = hasVisible ? 'none' : 'block';
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
    const placeholder = document.getElementById('collectionPlaceholder');
    if (!box) return;
    
    if (placeholder) placeholder.style.display = 'none';
    
    // منع التكرار
    if (box.querySelector(`.collection-badge[data-id="${id}"]`)) return;
    
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
    
    // تحديث عدد المجموعات المختارة
    updateCollectionsCount();
}

function removeCollection(id) {
    const box = document.getElementById('selectedCollectionsBox');
    if (!box) return;
    
    const badge = box.querySelector(`.collection-badge[data-id="${id}"]`);
    if (badge) badge.remove();
    
    const input = document.getElementById(`col-input-${id}`);
    if (input) input.remove();
    
    // تحديث حالة checkbox في القائمة المنسدلة
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
    const badge = document.querySelector('.collection-count-badge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline-block' : 'none';
    }
}

// ============================================================
// 🖼️ إدارة الصور - رفع ومعاينة
// ============================================================
function initImageHandlers() {
    const uploadArea = document.getElementById('imageUploadArea');
    const input = document.getElementById('imageInput');
    
    if (uploadArea) {
        uploadArea.addEventListener('click', () => {
            if (input) input.click();
        });
        
        // دعم السحب والإفلات
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.style.borderColor = 'var(--gold)';
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
            if (input && e.dataTransfer.files.length > 0) {
                input.files = e.dataTransfer.files;
                input.dispatchEvent(new Event('change'));
            }
        });
    }
    
    if (input) {
        input.addEventListener('change', function(e) {
            const files = e.target.files;
            const grid = document.getElementById('imagePreviewGrid');
            if (!grid) return;
            
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
}

// ============================================================
// 🧩 إدارة المتغيرات (Variants) - Cartesian Product
// ============================================================
function initVariantHandlers() {
    // الدوال موجودة في النطاق العام
}

function addOptionRow() {
    const container = document.getElementById('optionsContainer');
    if (!container) return;
    
    const row = document.createElement('div');
    row.className = 'option-row';
    row.innerHTML = `
        <div class="option-header">
            <input type="text" class="opt-name" placeholder="اسم الخيار (مثل: المقاس)" oninput="generatePayload()">
            <button class="btn-action btn-danger" type="button" onclick="removeOptionRow(this)">🗑️ حذف الخيار</button>
        </div>
        <label style="font-size: 0.85rem; color: #64748b; margin-bottom: 4px;">القيم المتعددة:</label>
        <div class="values-container"></div>
        <div class="add-value-group">
            <input type="text" class="val-input" placeholder="أدخل قيمة (مثل: كبير)" onkeypress="if(event.key==='Enter'){event.preventDefault();addValueToRow(this.closest('.add-value-group').querySelector('button'));}">
            <button class="btn-action" type="button" onclick="addValueToRow(this)">➕ إضافة قيمة</button>
        </div>
    `;
    container.appendChild(row);
    row.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function removeOptionRow(button) {
    const row = button.closest('.option-row');
    if (row && row.parentElement.children.length > 1) {
        if (confirm('⚠️ هل أنت متأكد من حذف هذا الخيار وجميع قيمه؟')) {
            row.remove();
            updateVariantsTable();
            generatePayload();
        }
    } else {
        showNotification('⚠️ يجب أن يبقى خيار واحد على الأقل', 'warning');
    }
}

function addValueToRow(button) {
    const row = button.closest('.option-row');
    if (!row) return;
    
    const input = row.querySelector('.val-input');
    if (!input) return;
    
    const valText = input.value.trim();
    if (!valText) {
        showNotification('⚠️ الرجاء إدخال قيمة', 'warning');
        return;
    }
    
    const valuesContainer = row.querySelector('.values-container');
    if (!valuesContainer) return;
    
    // منع التكرار
    const existing = valuesContainer.querySelectorAll('.value-tag');
    for (let tag of existing) {
        if (tag.textContent.trim().replace('×', '').trim() === valText) {
            showNotification('⚠️ هذه القيمة موجودة بالفعل', 'warning');
            return;
        }
    }
    
    const tag = document.createElement('div');
    tag.className = 'value-tag';
    tag.innerHTML = `
        ${valText} 
        <span onclick="this.closest('.value-tag').remove(); updateVariantsTable(); generatePayload();">&times;</span>
    `;
    valuesContainer.appendChild(tag);
    input.value = '';
    input.focus();
    
    updateVariantsTable();
    generatePayload();
}

function cartesian(arr) {
    return arr.reduce((a, b) => a.flatMap(d => b.map(e => [].concat(d, e))), [[]]);
}

function updateVariantsTable() {
    const optionRows = document.querySelectorAll('.option-row');
    let valuesArrays = [];
    
    optionRows.forEach(row => {
        const optName = row.querySelector('.opt-name').value.trim();
        const tagElements = row.querySelectorAll('.value-tag');
        const valuesArray = Array.from(tagElements).map(tag => tag.textContent.trim().replace('×', '').trim());
        
        if (optName && valuesArray.length > 0) {
            valuesArrays.push(valuesArray);
        }
    });
    
    const container = document.getElementById('variantsTableContainer');
    if (!container) return;
    
    if (valuesArrays.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4 text-muted">
                <i class="fas fa-cubes fa-2x mb-2 d-block" style="color: #D4AF37;"></i>
                <p>قم بإضافة الخيارات والقيم لتوليد جدول المتغيرات تلقائياً</p>
            </div>
        `;
        return;
    }
    
    const combinations = cartesian(valuesArrays);
    
    let html = `
        <div class="table-responsive">
            <table class="variants-table">
                <thead>
                    <tr>
                        <th style="min-width:120px;">المتغير</th>
                        <th style="min-width:80px;">صورة</th>
                        <th style="min-width:100px;">SKU</th>
                        <th style="min-width:100px;">السعر</th>
                        <th style="min-width:80px;">الكمية</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    combinations.forEach((combo, index) => {
        const optionValues = Array.isArray(combo) ? combo : [combo];
        const variantLabel = optionValues.join(' / ');
        html += `
            <tr data-index="${index}">
                <td><strong>${variantLabel}</strong></td>
                <td>
                    <div class="variant-img-wrapper">
                        <input type="file" class="var-img-file" accept="image/*" style="display: none;" onchange="handleVariantImage(this, ${index})">
                        <img id="thumb-${index}" class="variant-thumb" src="" alt="صورة المتغير">
                        <button type="button" class="btn-action" style="padding: 4px 8px; font-size: 0.75rem;" onclick="this.previousElementSibling.previousElementSibling.click()">📷</button>
                        <button type="button" id="del-btn-${index}" class="btn-action btn-danger" style="padding: 4px 6px; font-size: 0.7rem; display: none;" onclick="removeVariantImage(${index})">×</button>
                    </div>
                </td>
                <td><input type="text" class="var-sku" value="SKU-${String(index + 1).padStart(3, '0')}" oninput="generatePayload()"></td>
                <td><input type="number" class="var-price" value="0" step="0.01" min="0" oninput="generatePayload()" dir="ltr"></td>
                <td><input type="number" class="var-qty" value="0" min="0" oninput="generatePayload()" dir="ltr"></td>
            </tr>
        `;
    });
    
    html += `</tbody></table></div>`;
    container.innerHTML = html;
    generatePayload();
}

function handleVariantImage(input, index) {
    const file = input.files[0];
    if (file) {
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
}

function removeVariantImage(index) {
    const tr = document.querySelector(`tr[data-index="${index}"]`);
    if (tr) {
        const fileInput = tr.querySelector('.var-img-file');
        if (fileInput) fileInput.value = '';
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

// ============================================================
// 📦 توليد الـ Payload وإرساله
// ============================================================
function generatePayload() {
    const title = document.getElementById('productTitle')?.value || '';
    const slug = document.getElementById('productSlug')?.value || '';
    
    const optionRows = document.querySelectorAll('.option-row');
    const options = [];
    
    optionRows.forEach(row => {
        const optName = row.querySelector('.opt-name')?.value.trim() || '';
        const tagElements = row.querySelectorAll('.value-tag');
        const valuesArray = Array.from(tagElements).map(tag => tag.textContent.trim().replace('×', '').trim());
        
        if (optName && valuesArray.length > 0) {
            options.push({
                name: optName,
                values: valuesArray.map((val, idx) => ({
                    label: val,
                    sortOrder: idx
                }))
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
        const variantImage = (thumb && thumb.style.display === 'block') ? thumb.src : null;
        
        variants.push({
            sku: sku,
            price: price,
            compareAtPrice: 0,
            quantity: quantity,
            optionValues: optionValues,
            image: variantImage
        });
    });
    
    const payload = {
        input: {
            title: title || '',
            slug: slug || '',
            status: 'active',
            options: options,
            variants: variants
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
// 🏷️ إدارة العلامات (Tags)
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
// 🔔 نظام الإشعارات المتقدم
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
        border-right: 4px solid ${colors[type]};
        z-index: 99999;
        font-weight: 600;
        font-size: 0.95rem;
        max-width: 400px;
        animation: slideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        align-items: center;
        gap: 10px;
        backdrop-filter: blur(8px);
    `;
    toast.innerHTML = `${icons[type] || ''} ${message}`;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

// ============================================================
// 🎨 إضافة أنماط الإشعارات ديناميكياً
// ============================================================
(function addNotificationStyles() {
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
})();

// ============================================================
// 🚀 تهيئة جميع الوظائف عند تحميل الصفحة
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    initTinyMCE();
    initCollectionHandlers();
    initImageHandlers();
    initVariantHandlers();
    initTagHandlers();
    
    // تحديث عداد المجموعات
    updateCollectionsCount();
    
    console.log('✅ [admin_edit_product] تم تهيئة جميع الوظائف بنجاح');
});
