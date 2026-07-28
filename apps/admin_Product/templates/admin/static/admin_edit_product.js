{% extends "admin/base.html" %}

{% block title %}{{ 'تعديل المنتج: ' ~ product.title if product else 'إضافة منتج جديد' }}{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('admin_product_bp.static', filename='admin_edit_product.css') }}">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<!-- TinyMCE CDN -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/tinymce/6.8.2/tinymce.min.js" referrerpolicy="origin"></script>
{% endblock %}

{% block content %}
<div class="edit-product-container">
    <form method="POST" action="" enctype="multipart/form-data" onsubmit="preparePayloadBeforeSubmit(event)">
        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
        <input type="hidden" name="variants_payload" id="variantsPayloadInput">

        <!-- رأس الصفحة وأزرار الإجراءات -->
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h1 class="h3 font-weight-bold" style="color: var(--primary);">
                    <i class="fas fa-box-open" style="color: var(--gold);"></i> 
                    {{ product.title if product and product.title else 'إضافة منتج جديد' }}
                </h1>
                <p class="text-muted mb-0">إدارة تفاصيل المنتج، المتغيرات، المجموعات، والصور الاحترافية.</p>
            </div>
            <div class="d-flex gap-2">
                {% if product and product.id %}
                <button type="button" class="btn-action btn-danger" onclick="deleteProduct('{{ product.id }}', '{{ product.title }}')">
                    <i class="fas fa-trash-alt"></i> حذف المنتج
                </button>
                {% endif %}
                <button type="submit" class="btn-action btn-action-gold">
                    <i class="fas fa-save"></i> حفظ التغييرات
                </button>
            </div>
        </div>

        <!-- 1. المعلومات الأساسية -->
        <div class="form-section">
            <div class="form-section-title">
                <i class="fas fa-info-circle"></i> المعلومات الأساسية
            </div>
            <div class="row">
                <div class="col-md-8">
                    <div class="form-group">
                        <label for="productTitle"><i class="fas fa-heading"></i> عنوان المنتج</label>
                        <input type="text" id="productTitle" name="title" value="{{ product.title if product else '' }}" placeholder="أدخل عنوان المنتج الاحترافي..." required oninput="document.getElementById('productSlug').value = this.value.trim().toLowerCase().replace(/[\s]+/g, '-').replace(/[^\w\-]+/g, '')">
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="form-group">
                        <label for="productSlug"><i class="fas fa-link"></i> الرابط المختصر (Slug)</label>
                        <input type="text" id="productSlug" name="slug" value="{{ product.slug if product else '' }}" placeholder="product-slug-url" dir="ltr" required>
                    </div>
                </div>
            </div>
            <div class="form-group mt-3">
                <label for="productDescription"><i class="fas fa-align-right"></i> وصف المنتج المفصل</label>
                <textarea id="productDescription" name="description">{{ product.description if product else '' }}</textarea>
            </div>
        </div>

        <!-- 2. المجموعات والتصنيفات -->
        <div class="form-section">
            <div class="form-section-title">
                <i class="fas fa-folder-tree"></i> مجموعات المنتج
                <span class="badge-count" id="selectedCountDisplay">0</span>
            </div>
            
            <div class="form-group">
                <label><i class="fas fa-tags"></i> اختر المجموعات التابع لها المنتج</label>
                
                <!-- حاوية التحديد المتعدد المخصصة -->
                <div class="collection-multiselect-container position-relative">
                    <div class="form-control d-flex flex-wrap align-items-center gap-2 cursor-pointer" onclick="toggleCollectionDropdown()" style="min-height: 50px; background: #fff;">
                        <span id="collectionPlaceholder" class="text-muted">انقر لاختيار المجموعات...</span>
                        <div id="selectedCollectionsBox" class="d-flex flex-wrap gap-2">
                            <!-- يتم حقن الـ Badges هنا ديناميكياً -->
                        </div>
                    </div>

                    <!-- قائمة منسدلة للبحث والتحديد -->
                    <div id="collectionDropdownMenu" class="dropdown-menu p-3 shadow-lg border-0 w-100 mt-1" style="display: none; position: absolute; top: 100%; right: 0; z-index: 1000; background: #fff; border-radius: 12px; border: 1px solid rgba(212, 175, 55, 0.3) !important;">
                        <input type="text" id="collectionSearchInput" class="form-control mb-3" placeholder="بحث في المجموعات..." oninput="filterCollections(this.value)">
                        
                        <div class="collections-list-scroll" style="max-height: 220px; overflow-y: auto;">
                            {% for col in all_collections %}
                            <div class="collection-option-item d-flex align-items-center justify-content-between p-2 rounded cursor-pointer mb-1" 
                                 data-id="{{ col.id }}" 
                                 data-title="{{ col.title }}"
                                 onclick="toggleCollectionSelection(this, '{{ col.id }}', '{{ col.title }}')"
                                 style="transition: background 0.2s;">
                                <div class="d-flex align-items-center gap-2">
                                    <input type="checkbox" class="col-checkbox form-check-input m-0" {% if product and col in product.collections %}checked{% endif %}>
                                    <span style="font-weight: 500; color: var(--primary);">{{ col.title }}</span>
                                </div>
                                <i class="fas fa-folder text-warning"></i>
                            </div>
                            {% endfor %}
                            <div id="collectionsNoResults" class="text-center text-muted py-2" style="display: none;">لا توجد نتائج مطابقة</div>
                        </div>
                    </div>
                </div>
                
                <!-- حقول مخفية لحفظ المعرفات عند الإرسال -->
                <div id="hiddenCollectionsInputs">
                    {% if product and product.collections %}
                        {% for col in product.collections %}
                        <input type="hidden" name="collection_ids" value="{{ col.id }}" id="col-input-{{ col.id }}">
                        {% endfor %}
                    {% endif %}
                </div>
            </div>
        </div>

        <!-- 3. صور المنتج الرئيسية -->
        <div class="form-section">
            <div class="form-section-title">
                <i class="fas fa-images"></i> معرض الصور
            </div>
            
            <div id="imageUploadArea" class="border border-dashed rounded-3 p-4 text-center cursor-pointer mb-3" style="border: 2px dashed rgba(212, 175, 55, 0.4); background: var(--gray-50); transition: all 0.3s;">
                <i class="fas fa-cloud-upload-alt fa-3x mb-2" style="color: var(--gold);"></i>
                <h5 style="color: var(--primary); font-weight: 600;">اسحب وأفلت صور المنتج هنا، أو انقر للاختيار</h5>
                <p class="text-muted small mb-0">PNG, JPG, WEBP مسموح بها</p>
                <input type="file" id="imageInput" name="images" multiple accept="image/*" style="display: none;">
            </div>

            <div id="imagePreviewGrid" class="d-flex flex-wrap gap-3">
                {% if product and product.images %}
                    {% for img in product.images %}
                    <div class="image-preview-item position-relative rounded overflow-hidden shadow-sm" style="width: 100px; height: 100px; border: 1px solid var(--gray-200);">
                        <img src="{{ img.url }}" alt="صورة المنتج" class="w-100 h-100 object-fit-cover">
                        <button type="button" class="remove-image btn btn-danger btn-sm position-absolute top-0 end-0 m-1 p-0 d-flex align-items-center justify-content-center" style="width: 24px; height: 24px; border-radius: 50%;" onclick="this.parentElement.remove();">✕</button>
                    </div>
                    {% endfor %}
                {% else %}
                    <div class="text-center text-muted w-150 py-3">لا توجد صور مرفوعة حالياً</div>
                {% endif %}
            </div>
        </div>

        <!-- 4. خيارات ومتغيرات المنتج (Variants & Options) -->
        <div class="form-section">
            <div class="form-section-title">
                <i class="fas fa-cubes"></i> خيارات ومتغيرات المنتج (المقاسات، الألوان، إلخ)
            </div>

            <div id="optionsContainer">
                <!-- صف الخيار الافتراضي -->
                <div class="option-row p-3 rounded mb-3" style="background: var(--gray-50); border: 1px solid var(--gray-200);">
                    <div class="option-header d-flex justify-content-between align-items-center mb-2">
                        <input type="text" class="opt-name form-control w-75" placeholder="اسم الخيار (مثل: المقاس أو اللون)" value="المقاس" oninput="generatePayload()">
                        <button class="btn-action btn-danger" type="button" onclick="removeOptionRow(this)"><i class="fas fa-trash"></i> حذف</button>
                    </div>
                    <label style="font-size: 0.85rem; color: var(--gray-600);">القيم المتعددة:</label>
                    <div class="values-container d-flex flex-wrap gap-2 mb-2">
                        <div class="value-tag badge bg-light text-dark border p-2 d-flex align-items-center gap-2">
                            صغير <span class="cursor-pointer text-danger" onclick="this.closest('.value-tag').remove(); updateVariantsTable(); generatePayload();">&times;</span>
                        </div>
                        <div class="value-tag badge bg-light text-dark border p-2 d-flex align-items-center gap-2">
                            كبير <span class="cursor-pointer text-danger" onclick="this.closest('.value-tag').remove(); updateVariantsTable(); generatePayload();">&times;</span>
                        </div>
                    </div>
                    <div class="add-value-group d-flex gap-2">
                        <input type="text" class="val-input form-control" placeholder="أدخل قيمة جديدة واضغط إضافة..." onkeypress="if(event.key==='Enter'){event.preventDefault();addValueToRow(this.closest('.add-value-group').querySelector('button'));}">
                        <button class="btn-action btn-action-gold" type="button" onclick="addValueToRow(this)"><i class="fas fa-plus"></i> إضافة</button>
                    </div>
                </div>
            </div>

            <button type="button" class="btn-action mb-4" onclick="addOptionRow()">
                <i class="fas fa-plus-circle"></i> إضافة خيار جديد (مثل اللون)
            </button>

            <!-- جدول المتغيرات المولدة تلقائياً -->
            <h5 class="font-weight-bold mb-3" style="color: var(--primary); font-size: 1rem;"><i class="fas fa-table" style="color: var(--gold);"></i> جدول المتغيرات والأسعار</h5>
            <div id="variantsTableContainer">
                <!-- يتم توليد الجدول تلقائياً بواسطة JavaScript -->
            </div>
        </div>

        <!-- 5. العلامات (Tags) -->
        <div class="form-section">
            <div class="form-section-title">
                <i class="fas fa-tags"></i> العلامات الدلالية (Tags)
            </div>
            <div class="form-group">
                <div class="d-flex gap-2 mb-3">
                    <input type="text" id="tagInput" class="form-control" placeholder="أدخل علامة واضغط Enter...">
                    <button type="button" class="btn-action btn-action-gold" onclick="addTag()"><i class="fas fa-plus"></i> إضافة علامة</button>
                </div>
                <div id="tagsContainer" class="d-flex flex-wrap gap-2">
                    {% if product and product.tags %}
                        {% for tag in product.tags %}
                        <span class="tag-item">
                            <span class="remove-tag cursor-pointer text-danger" onclick="this.parentElement.remove();">✕</span> 
                            {{ tag }}
                        </span>
                        {% endfor %}
                    {% else %}
                        <span class="text-muted small">لا توجد علامات مضافة.</span>
                    {% endif %}
                </div>
            </div>
        </div>

        <!-- زر الحفظ النهائي السفلي -->
        <div class="d-flex justify-content-end gap-3 mt-4">
            <a href="{{ url_for('admin_product_bp.manage_products_view') }}" class="btn-action bg-secondary text-white">إلغاء</a>
            <button type="submit" class="btn-action btn-action-gold px-5 py-3" style="font-size: 1.05rem;">
                <i class="fas fa-save"></i> حفظ المنتج نهائياً
            </button>
        </div>
    </form>
</div>
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('admin_product_bp.static', filename='admin_edit_product.js') }}"></script>
<script>
    // تهيئة أولية لعرض جدول المتغيرات إن وجد عند التحميل
    document.addEventListener("DOMContentLoaded", function() {
        if (typeof updateVariantsTable === 'function') {
            updateVariantsTable();
        }
    });
</script>
{% endblock %}
