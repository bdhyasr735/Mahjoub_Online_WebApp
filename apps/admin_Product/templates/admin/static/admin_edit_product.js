// static/admin_edit_product.js

document.addEventListener("DOMContentLoaded", function () {
    initTinyMCE();
    initCollectionHandlers();
    initImageHandlers();
    initVariantHandlers();
    initTagHandlers();
    updateCollectionsCount();
    console.log("✅ [admin_edit_product] تم تهيئة جميع الوظائف بنجاح");
});

// تهيئة محرر النصوص TinyMCE
function initTinyMCE() {
    tinymce.init({
        selector: "#productDescription",
        height: 350,
        menubar: true,
        plugins: [
            "advlist", "autolink", "lists", "link", "image", "charmap", "preview",
            "anchor", "searchreplace", "visualblocks", "code", "fullscreen",
            "insertdatetime", "media", "table", "help", "wordcount"
        ],
        toolbar: 'undo redo | blocks | bold italic backcolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | help | link image media | fullscreen | code',
        content_style: 'body { font-family: "Cairo", system-ui, sans-serif; font-size: 16px; line-height: 1.8; padding: 12px; }',
        directionality: "rtl",
        language: "ar",
        images_upload_handler: function (e, t) {
            return new Promise(function (t, n) {
                const o = new FileReader();
                o.onload = function (e) { t(e.target.result); };
                o.readAsDataURL(e.blob());
            });
        }
    });
}

// إدارة القوائم المنسدلة للمجموعات (Collections)
function initCollectionHandlers() {
    document.addEventListener("click", function (e) {
        const t = document.querySelector(".collection-multiselect-container");
        if (t && !t.contains(e.target)) {
            const dropdown = document.getElementById("collectionDropdownMenu");
            if (dropdown) dropdown.style.display = "none";
        }
    });
}

function toggleCollectionDropdown() {
    const e = document.getElementById("collectionDropdownMenu");
    if (!e) return;
    e.style.display = "block" === e.style.display ? "none" : "block";
    if ("block" === e.style.display) {
        const t = document.getElementById("collectionSearchInput");
        if (t) {
            t.focus();
            t.value = "";
            filterCollections("");
        }
    }
}

function filterCollections(query) {
    const items = document.querySelectorAll(".collection-option-item");
    let found = false;
    query = query.toLowerCase().trim();
    
    items.forEach(item => {
        const title = item.getAttribute("data-title") || "";
        const match = title.toLowerCase().includes(query);
        item.style.display = match ? "flex" : "none";
        if (match) found = true;
    });

    const noResults = document.getElementById("collectionsNoResults");
    if (noResults) {
        noResults.style.display = found ? "none" : "block";
    }
}

function toggleCollectionSelection(element, id, title) {
    const checkbox = element.querySelector(".col-checkbox");
    if (!checkbox) return;
    
    checkbox.checked = !checkbox.checked;
    if (checkbox.checked) {
        addCollectionBadge(id, title);
        element.classList.add("selected");
    } else {
        removeCollection(id);
        element.classList.remove("selected");
    }
}

function addCollectionBadge(id, title) {
    const box = document.getElementById("selectedCollectionsBox");
    const placeholder = document.getElementById("collectionPlaceholder");
    if (!box) return;

    if (placeholder) placeholder.style.display = "none";
    if (box.querySelector(`.collection-badge[data-id="${id}"]`)) return;

    const badge = document.createElement("span");
    badge.className = "collection-badge";
    badge.setAttribute("data-id", id);
    badge.innerHTML = `
        <i class="fas fa-folder"></i> 
        ${title} 
        <span class="remove-collection" onclick="event.stopPropagation(); removeCollection('${id}')">&times;</span>
    `;
    box.appendChild(badge);

    const hiddenInputs = document.getElementById("hiddenCollectionsInputs");
    if (hiddenInputs && !document.getElementById(`col-input-${id}`)) {
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = "collection_ids";
        input.value = id;
        input.id = `col-input-${id}`;
        hiddenInputs.appendChild(input);
    }
    updateCollectionsCount();
}

function removeCollection(id) {
    const box = document.getElementById("selectedCollectionsBox");
    if (!box) return;

    const badge = box.querySelector(`.collection-badge[data-id="${id}"]`);
    if (badge) badge.remove();

    const input = document.getElementById(`col-input-${id}`);
    if (input) input.remove();

    const checkbox = document.querySelector(`.collection-option-item[data-id="${id}"] .col-checkbox`);
    if (checkbox) checkbox.checked = false;

    const badges = box.querySelectorAll(".collection-badge");
    const placeholder = document.getElementById("collectionPlaceholder");
    if (placeholder && badges.length === 0) {
        placeholder.style.display = "block";
    }
    updateCollectionsCount();
}

function updateCollectionsCount() {
    const box = document.getElementById("selectedCollectionsBox");
    if (!box) return;
    const count = box.querySelectorAll(".collection-badge").length;
    const countBadge = document.querySelector(".collection-count-badge");
    if (countBadge) {
        countBadge.textContent = count;
        countBadge.style.display = count > 0 ? "inline-block" : "none";
    }
}

// إدارة صور المنتج (رفع، سحب وإفلات، معاينة)
function initImageHandlers() {
    const uploadArea = document.getElementById("imageUploadArea");
    const fileInput = document.getElementById("imageInput");

    if (uploadArea) {
        uploadArea.addEventListener("click", () => fileInput && fileInput.click());
        uploadArea.addEventListener("dragover", function (e) {
            e.preventDefault();
            this.style.borderColor = "var(--gold)";
            this.style.background = "rgba(212, 175, 55, 0.05)";
        });
        uploadArea.addEventListener("dragleave", function (e) {
            e.preventDefault();
            this.style.borderColor = "";
            this.style.background = "";
        });
        uploadArea.addEventListener("drop", function (e) {
            e.preventDefault();
            this.style.borderColor = "";
            this.style.background = "";
            if (fileInput && e.dataTransfer.files.length > 0) {
                fileInput.files = e.dataTransfer.files;
                fileInput.dispatchEvent(new Event("change"));
            }
        });
    }

    if (fileInput) {
        fileInput.addEventListener("change", function (e) {
            const files = e.target.files;
            const grid = document.getElementById("imagePreviewGrid");
            if (!grid) return;

            for (let i = 0; i < files.length; i++) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    const item = document.createElement("div");
                    item.className = "image-preview-item";
                    item.innerHTML = `
                        <img src="${e.target.result}" alt="صورة المنتج">
                        <button type="button" class="remove-image" onclick="this.parentElement.remove();">✕</button>
                    `;
                    grid.appendChild(item);
                };
                reader.readAsDataURL(files[i]);
            }
            this.value = "";
        });
    }
}

function initVariantHandlers() {}

// إدارة خيارات المنتج وتوليد الجدول
function addOptionRow() {
    const container = document.getElementById("optionsContainer");
    if (!container) return;

    const row = document.createElement("div");
    row.className = "option-row";
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
    row.scrollIntoView({ behavior: "smooth", block: "center" });
}

function removeOptionRow(btn) {
    const row = btn.closest(".option-row");
    if (row && row.parentElement.children.length > 1) {
        if (confirm("⚠️ هل أنت متأكد من حذف هذا الخيار وجميع قيمه؟")) {
            row.remove();
            updateVariantsTable();
            generatePayload();
        }
    } else {
        showNotification("⚠️ يجب يبقى خيار واحد على الأقل", "warning");
    }
}

function addValueToRow(btn) {
    const row = btn.closest(".option-row");
    if (!row) return;
    const input = row.querySelector(".val-input");
    if (!input) return;

    const val = input.value.trim();
    if (!val) {
        showNotification("⚠️ الرجاء إدخال قيمة", "warning");
        return;
    }

    const valuesContainer = row.querySelector(".values-container");
    if (!valuesContainer) return;

    const existingTags = valuesContainer.querySelectorAll(".value-tag");
    for (let tag of existingTags) {
        if (tag.textContent.trim().replace("×", "").trim() === val) {
            showNotification("⚠️ هذه القيمة موجودة بالفعل", "warning");
            return;
        }
    }

    const tag = document.createElement("div");
    tag.className = "value-tag";
    tag.innerHTML = `
        ${val} 
        <span onclick="this.closest('.value-tag').remove(); updateVariantsTable(); generatePayload();">&times;</span>
    `;
    valuesContainer.appendChild(tag);
    input.value = "";
    input.focus();
    updateVariantsTable();
    generatePayload();
}

// حساب الضرب الكارتيزي للخيارات
function cartesian(arr) {
    return arr.reduce((a, b) => a.flatMap(d => b.map(e => [].concat(d, e))), [[]]);
}

function updateVariantsTable() {
    const optionRows = document.querySelectorAll(".option-row");
    let optionsData = [];

    optionRows.forEach(row => {
        const optName = row.querySelector(".opt-name").value.trim();
        const tags = row.querySelectorAll(".value-tag");
        const values = Array.from(tags).map(tag => tag.textContent.trim().replace("×", "").trim());
        if (optName && values.length > 0) {
            optionsData.push(values);
        }
    });

    const tableContainer = document.getElementById("variantsTableContainer");
    if (!tableContainer) return;

    if (optionsData.length === 0) {
        tableContainer.innerHTML = `
            <div class="text-center py-4 text-muted">
                <i class="fas fa-cubes fa-2x mb-2 d-block" style="color: #D4AF37;"></i>
                <p>قم بإضافة الخيارات والقيم لتوليد جدول المتغيرات تلقائياً</p>
            </div>
        `;
        generatePayload();
        return;
    }

    const combinations = cartesian(optionsData);
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
        const comboArray = Array.isArray(combo) ? combo : [combo];
        const comboString = comboArray.join(" / ");
        
        html += `
            <tr data-index="${index}">
                <td><strong>${comboString}</strong></td>
                <td>
                    <div class="variant-img-wrapper">
                        <input type="file" class="var-img-file" accept="image/*" style="display: none;" onchange="handleVariantImage(this, ${index})">
                        <img id="thumb-${index}" class="variant-thumb" src="" alt="صورة المتغير" style="display: none; width: 40px; height: 40px; object-fit: cover; border-radius: 4px; margin-bottom: 4px;">
                        <button type="button" class="btn-action" style="padding: 4px 8px; font-size: 0.75rem;" onclick="this.previousElementSibling.previousElementSibling.click()">📷</button>
                        <button type="button" id="del-btn-${index}" class="btn-action btn-danger" style="padding: 4px 6px; font-size: 0.7rem; display: none;" onclick="removeVariantImage(${index})">×</button>
                    </div>
                </td>
                <td><input type="text" class="var-sku" value="SKU-${String(index + 1).padStart(3, "0")}" oninput="generatePayload()"></td>
                <td><input type="number" class="var-price" value="0" step="0.01" min="0" oninput="generatePayload()" dir="ltr"></td>
                <td><input type="number" class="var-qty" value="0" min="0" oninput="generatePayload()" dir="ltr"></td>
            </tr>
        `;
    });

    html += `</tbody></table></div>`;
    tableContainer.innerHTML = html;
    generatePayload();
}

function handleVariantImage(input, index) {
    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const thumb = document.getElementById(`thumb-${index}`);
            const delBtn = document.getElementById(`del-btn-${index}`);
            if (thumb) {
                thumb.src = e.target.result;
                thumb.style.display = "block";
            }
            if (delBtn) delBtn.style.display = "inline-block";
            generatePayload();
        };
        reader.readAsDataURL(file);
    }
}

function removeVariantImage(index) {
    const row = document.querySelector(`tr[data-index="${index}"]`);
    if (row) {
        const fileInput = row.querySelector(".var-img-file");
        if (fileInput) fileInput.value = "";
    }
    const thumb = document.getElementById(`thumb-${index}`);
    const delBtn = document.getElementById(`del-btn-${index}`);
    if (thumb) {
        thumb.src = "";
        thumb.style.display = "none";
    }
    if (delBtn) delBtn.style.display = "none";
    generatePayload();
}

// توليد الـ JSON Payload للإرسال
function generatePayload() {
    const title = document.getElementById("productTitle")?.value || "";
    const slug = document.getElementById("productSlug")?.value || "";
    
    const optionRows = document.querySelectorAll(".option-row");
    const options = [];

    optionRows.forEach(row => {
        const optName = row.querySelector(".opt-name")?.value.trim() || "";
        const tags = row.querySelectorAll(".value-tag");
        const values = Array.from(tags).map(tag => tag.textContent.trim().replace("×", "").trim());
        if (optName && values.length > 0) {
            options.push({
                name: optName,
                values: values.map((val, idx) => ({ label: val, sortOrder: idx }))
            });
        }
    });

    const variantRows = document.querySelectorAll(".variants-table tbody tr");
    const variants = [];

    variantRows.forEach((row, index) => {
        const sku = row.querySelector(".var-sku")?.value || `SKU-${String(index + 1).padStart(3, "0")}`;
        const price = parseFloat(row.querySelector(".var-price")?.value) || 0;
        const qty = parseInt(row.querySelector(".var-qty")?.value) || 0;
        const strongText = row.querySelector("td:first-child strong")?.textContent || "";
        const optionValues = strongText.split(" / ");
        
        const thumb = document.getElementById(`thumb-${index}`);
        const image = thumb && "block" === thumb.style.display ? thumb.src : null;

        variants.push({
            sku: sku,
            price: price,
            compareAtPrice: 0,
            quantity: qty,
            optionValues: optionValues,
            image: image
        });
    });

    const payload = {
        input: {
            title: title || "",
            slug: slug || "",
            status: "active",
            options: options,
            variants: variants
        }
    };

    const payloadInput = document.getElementById("variantsPayloadInput");
    if (payloadInput) {
        payloadInput.value = JSON.stringify(payload);
    }
}

function preparePayloadBeforeSubmit(e) {
    generatePayload();
}

// إدارة العلامات (Tags)
function initTagHandlers() {
    const tagInput = document.getElementById("tagInput");
    if (tagInput) {
        tagInput.addEventListener("keypress", function (e) {
            if ("Enter" === e.key) {
                e.preventDefault();
                addTag();
            }
        });
    }
}

function addTag() {
    const tagInput = document.getElementById("tagInput");
    if (!tagInput) return;

    const val = tagInput.value.trim();
    if (!val) {
        showNotification("⚠️ الرجاء إدخال علامة", "warning");
        return;
    }

    const container = document.getElementById("tagsContainer");
    if (!container) return;

    const existingTags = container.querySelectorAll(".tag-item");
    for (let tag of existingTags) {
        if (tag.textContent.trim().replace("✕", "").trim() === val) {
            showNotification("⚠️ هذه العلامة موجودة بالفعل", "warning");
            return;
        }
    }

    const mutedText = container.querySelector(".text-muted");
    if (mutedText) mutedText.remove();

    const tagItem = document.createElement("span");
    tagItem.className = "tag-item";
    tagItem.innerHTML = `
        <span class="remove-tag" onclick="this.parentElement.remove();">✕</span> 
        ${val}
    `;
    container.appendChild(tagItem);
    tagInput.value = "";
    tagInput.focus();
}

// حذف المنتج
function deleteProduct(productId, productTitle) {
    if (!confirm(`⚠️ هل أنت متأكد من حذف/أرشفة المنتج "${productTitle}"؟\nلا يمكن التراجع عن هذا الإجراء!`)) return;

    const csrfToken = document.querySelector('[name="csrf_token"]')?.value || "";

    fetch(`{{ url_for('admin_product_bp.delete_product', qid='') }}${productId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
            "X-Requested-With": "XMLHttpRequest"
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showNotification("✅ " + data.message, "success");
            setTimeout(() => {
                window.location.href = "{{ url_for('admin_product_bp.manage_products_view') }}";
            }, 1500);
        } else {
            showNotification("❌ " + data.message, "error");
        }
    })
    .catch(err => {
        showNotification("❌ حدث خطأ: " + err.message, "error");
    });
}

// نظام الإشعارات المنبثقة
function showNotification(message, type = "success") {
    const colors = { success: "#22c55e", error: "#ef4444", warning: "#f59e0b", info: "#3b82f6" };
    const icons = { success: "✅", error: "❌", warning: "⚠️", info: "ℹ️" };

    const notification = document.createElement("div");
    notification.style.cssText = `
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
    notification.innerHTML = `${icons[type] || ""} ${message}`;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = "slideOut 0.4s cubic-bezier(0.4, 0, 0.2, 1)";
        setTimeout(() => notification.remove(), 400);
    }, 4000);
}

// إدراج حركات الـ Animations للإشعارات
(function () {
    const style = document.createElement("style");
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
