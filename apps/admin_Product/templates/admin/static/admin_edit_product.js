// static/admin_edit_product.js

// ========================================
// TinyMCE Editor
// ========================================
function initTinyMCE() {
    tinymce.init({
        selector: '#productDescription',
        height: 300,
        menubar: true,
        plugins: ['advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview', 'searchreplace', 'visualblocks', 'code', 'fullscreen', 'insertdatetime', 'media', 'table', 'help', 'wordcount'],
        toolbar: 'undo redo | blocks | bold italic backcolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | help | link image media | fullscreen | code',
        content_style: 'body { font-family: system-ui, -apple-system, sans-serif; font-size: 16px; }',
        directionality: 'rtl',
        language: 'ar',
        images_upload_handler: function(blobInfo, progress) {
            return new Promise(function(resolve, reject) {
                const reader = new FileReader();
                reader.onload = e => resolve(e.target.result);
                reader.readAsDataURL(blobInfo.blob());
            });
        }
    });
}

// ========================================
// إدارة المجموعات
// ========================================
function initCollectionHandlers() {
    document.addEventListener('click', function(e) {
        const container = document.querySelector('.collection-multiselect-container');
        if (container && !container.contains(e.target)) {
            document.getElementById('collectionDropdownMenu').style.display = 'none';
        }
    });
}

function toggleCollectionDropdown() {
    const menu = document.getElementById('collectionDropdownMenu');
    menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
    if (menu.style.display === 'block') {
        document.getElementById('collectionSearchInput').focus();
    }
}

function filterCollections(query) {
    const items = document.querySelectorAll('.collection-option-item');
    query = query.toLowerCase();
    items.forEach(item => {
        const title = item.getAttribute('data-title').toLowerCase();
        item.style.display = title.includes(query) ? 'flex' : 'none';
    });
}

function toggleCollectionSelection(element, id, title) {
    const checkbox = element.querySelector('.col-checkbox');
    checkbox.checked = !checkbox.checked;
    if (checkbox.checked) {
        addCollectionBadge(id, title);
    } else {
        removeCollection(id);
    }
}

function addCollectionBadge(id, title) {
    const box = document.getElementById('selectedCollectionsBox');
    const placeholder = document.getElementById('collectionPlaceholder');
    if (placeholder) placeholder.style.display = 'none';
    if (box.querySelector(`.collection-badge[data-id="${id}"]`)) return;
    const badge = document.createElement('span');
    badge.className = 'collection-badge';
    badge.setAttribute('data-id', id);
    badge.innerHTML = `<i class="fas fa-folder"></i> ${title} <span class="remove-collection" onclick="event.stopPropagation(); removeCollection('${id}')">&times;</span>`;
    box.appendChild(badge);
    const hiddenContainer = document.getElementById('hiddenCollectionsInputs');
    if (!document.getElementById(`col-input-${id}`)) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'collection_ids';
        input.value = id;
        input.id = `col-input-${id}`;
        hiddenContainer.appendChild(input);
    }
}

function removeCollection(id) {
    const box = document.getElementById('selectedCollectionsBox');
    const badge = box.querySelector(`.collection-badge[data-id="${id}"]`);
    if (badge) badge.remove();
    const input = document.getElementById(`col-input-${id}`);
    if (input) input.remove();
    const checkbox = document.querySelector(`.collection-option-item[data-id="${id}"] .col-checkbox`);
    if (checkbox) checkbox.checked = false;
    if (box.querySelectorAll('.collection-badge').length === 0) {
        const placeholder = document.getElementById('collectionPlaceholder');
        if (placeholder) placeholder.style.display = 'block';
    }
}

// ========================================
// إدارة الصور
// ========================================
function initImageHandlers() {
    document.getElementById('imageUploadArea')?.addEventListener('click', () => {
        document.getElementById('imageInput').click();
    });

    document.getElementById('imageInput')?.addEventListener('change', function(e) {
        const files = e.target.files;
        const grid = document.getElementById('imagePreviewGrid');
        for (let i = 0; i < files.length; i++) {
            const reader = new FileReader();
            reader.onload = function(event) {
                const div = document.createElement('div');
                div.className = 'image-preview-item';
                div.innerHTML = `
                    <img src="${event.target.result}" alt="صورة">
                    <button type="button" class="remove-image" onclick="this.parentElement.remove()">✕</button>
                `;
                grid.appendChild(div);
            };
            reader.readAsDataURL(files[i]);
        }
        this.value = '';
    });
}

// ========================================
// إدارة المتغيرات
// ========================================
function initVariantHandlers() {
    // الدوال موجودة بالفعل في window
}

function addOptionRow() {
    const container = document.getElementById('optionsContainer');
    const row = document.createElement('div');
    row.className = 'option-row';
    row.innerHTML = `
        <div class="option-header">
            <input type="text" class="opt-name" placeholder="اسم الخيار (مثل: المقاس)" oninput="generatePayload()">
            <button class="btn-action btn-danger" type="button" onclick="removeOptionRow(this)">حذف الخيار</button>
        </div>
        <label style="font-size: 0.85rem; color: #64748b; margin-bottom: 4px;">القيم المتعددة:</label>
        <div class="values-container"></div>
        <div class="add-value-group">
            <input type="text" class="val-input" placeholder="أدخل قيمة ثم اضغط إضافة (مثل: كبير)">
            <button class="btn-action" type="button" onclick="addValueToRow(this)">+ إضافة قيمة</button>
        </div>
    `;
    container.appendChild(row);
}

function removeOptionRow(button) {
    button.closest('.option-row').remove();
    updateVariantsTable();
    generatePayload();
}

function addValueToRow(button) {
    const row = button.closest('.option-row');
    const input = row.querySelector('.val-input');
    const valText = input.value.trim();
    if (valText) {
        const valuesContainer = row.querySelector('.values-container');
        const tag = document.createElement('div');
        tag.className = 'value-tag';
        tag.innerHTML = `${valText} <span onclick="this.closest('.value-tag').remove(); updateVariantsTable(); generatePayload();">&times;</span>`;
        valuesContainer.appendChild(tag);
        input.value = '';
        updateVariantsTable();
        generatePayload();
    }
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
        const valuesArray = Array.from(tagElements).map(tag => tag.firstChild.textContent.trim());
        if (optName && valuesArray.length > 0) {
            valuesArrays.push(valuesArray);
        }
    });
    const container = document.getElementById('variantsTableContainer');
    if (valuesArrays.length === 0) {
        container.innerHTML = `<p style="color: #64748b; font-size: 0.9rem; text-align: center; padding: 15px; background: #f8fafc; border: 1px dashed var(--border-color); border-radius: 6px;">قم بإضافة الخيارات والقيم لتوليد جدول المتغيرات تلقائياً...</p>`;
        return;
    }
    const combinations = cartesian(valuesArrays);
    let html = `<table class="variants-table"><thead><tr><th>المتغير</th><th>صورة المتغير</th><th>SKU</th><th>السعر</th><th>الكمية</th></tr></thead><tbody>`;
    combinations.forEach((combo, index) => {
        const optionValues = Array.isArray(combo) ? combo : [combo];
        const variantLabel = optionValues.join(' / ');
        html += `<tr data-index="${index}"><td><strong>${variantLabel}</strong></td><td><div class="variant-img-wrapper"><input type="file" class="var-img-file" accept="image/*" style="display: none;" onchange="handleVariantImage(this, ${index})"><img id="thumb-${index}" class="variant-thumb" src="" alt="Variant Image"><button type="button" class="btn-action" style="padding: 5px 10px; font-size: 0.8rem;" onclick="this.previousElementSibling.previousElementSibling.click()">📷 رفع</button><button type="button" id="del-btn-${index}" class="btn-action btn-danger" style="padding: 5px 8px; font-size: 0.75rem; display: none;" onclick="removeVariantImage(${index})">×</button></div></td><td><input type="text" class="var-sku" value="SKU-VAR-${index + 1}" oninput="generatePayload()"></td><td><input type="number" class="var-price" value="0" step="0.01" oninput="generatePayload()" dir="ltr"></td><td><input type="number" class="var-qty" value="0" oninput="generatePayload()" dir="ltr"></td></tr>`;
    });
    html += `</tbody></table>`;
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
            thumb.src = e.target.result;
            thumb.style.display = 'block';
            delBtn.style.display = 'inline-block';
            generatePayload();
        };
        reader.readAsDataURL(file);
    }
}

function removeVariantImage(index) {
    const tr = document.querySelector(`tr[data-index="${index}"]`);
    tr.querySelector('.var-img-file').value = "";
    const thumb = document.getElementById(`thumb-${index}`);
    const delBtn = document.getElementById(`del-btn-${index}`);
    thumb.src = "";
    thumb.style.display = 'none';
    delBtn.style.display = 'none';
    generatePayload();
}

function generatePayload() {
    const title = document.getElementById('productTitle').value;
    const slug = document.getElementById('productSlug').value;
    const optionRows = document.querySelectorAll('.option-row');
    const options = [];
    optionRows.forEach(row => {
        const optName = row.querySelector('.opt-name').value.trim();
        const tagElements = row.querySelectorAll('.value-tag');
        const valuesArray = Array.from(tagElements).map(tag => tag.firstChild.textContent.trim());
        if (optName && valuesArray.length > 0) {
            options.push({ name: optName, values: valuesArray.map((val, idx) => ({ label: val, sortOrder: idx })) });
        }
    });
    const variantRows = document.querySelectorAll('.variants-table tbody tr');
    const variants = [];
    variantRows.forEach((tr, index) => {
        const sku = tr.querySelector('.var-sku').value;
        const price = parseFloat(tr.querySelector('.var-price').value) || 0;
        const quantity = parseInt(tr.querySelector('.var-qty').value) || 0;
        const optionValuesText = tr.cells[0].innerText.trim();
        const optionValues = optionValuesText.split(' / ');
        const thumb = document.getElementById(`thumb-${index}`);
        const variantImage = (thumb && thumb.style.display === 'block') ? thumb.src : null;
        variants.push({ sku: sku, price: price, compareAtPrice: 0, quantity: quantity, optionValues: optionValues, image: variantImage });
    });
    const payload = { input: { title: title || "", slug: slug || "", status: "active", options: options, variants: variants } };
    document.getElementById('variantsPayloadInput').value = JSON.stringify(payload);
}

function preparePayloadBeforeSubmit(e) {
    generatePayload();
}

// ========================================
// إدارة العلامات
// ========================================
function initTagHandlers() {
    document.getElementById('tagInput')?.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            addTag();
        }
    });
}

function addTag() {
    const input = document.getElementById('tagInput');
    const tag = input.value.trim();
    if (!tag) return;
    const container = document.getElementById('tagsContainer');
    const noTagsMsg = container.querySelector('.text-muted');
    if (noTagsMsg) noTagsMsg.remove();
    const span = document.createElement('span');
    span.className = 'tag-item';
    span.innerHTML = `<span class="remove-tag" onclick="this.parentElement.remove()">✕</span> ${tag}`;
    container.appendChild(span);
    input.value = '';
}

// ========================================
// حذف المنتج
// ========================================
function deleteProduct(qid, name) {
    if (!confirm(`⚠️ هل أنت متأكد من حذف/أرشفة المنتج "${name}"؟`)) return;
    const csrfToken = document.querySelector('[name="csrf_token"]')?.value || '';
    fetch(`{{ url_for('admin_product_bp.delete_product', qid='') }}${qid}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest' }
    }).then(response => response.json()).then(data => {
        if (data.success) { alert('✅ ' + data.message); window.location.href = '{{ url_for("admin_product_bp.manage_products_view") }}'; } 
        else { alert('❌ ' + data.message); }
    }).catch(error => alert('❌ حدث خطأ: ' + error));
}
