
286

الخطة المجانية
ترقية
كيف يمكنني مساعدتك؟




أجهزة الكمبيوتر السحابية
جديد

قم بتنزيل Manus لنظامي Windows أو macOS
الوصول إلى الملفات المحلية والعمل بسلاسة مع سطح المكتب.


استخدام Manus في أي مكان

يمكنك أيضًا تنزيل واستخدام Manus على الهاتف المحمول وسطح المكتب للحصول على تجربة مختلفة.

modified_supplier_form.html
{% extends "admin/admin_base.html" %}

{% block title %}تعميد مورد | محجوب أونلاين{% endblock %}

{% block content %}
<div class="container-fluid" id="main-content">
    <div class="mb-4 d-flex justify-content-between align-items-center bg-white p-4 rounded-4 shadow-sm border-end border-4" style="border-color: var(--royal-purple) !important;">
        <div>
            <h2 class="fw-bold mb-1" style="color: var(--royal-purple);">🛡️ تعميد مورد جديد (نظام مشفر)</h2>
            <p class="text-muted mb-0 small">نظام الأرشفة السيادي - AES-256 Encrypted & Smart Learning</p>
        </div>
        <div class="d-flex gap-4 text-center">
            <div class="px-3 border-start"><small class="d-block text-muted fw-bold">معرف المورد</small><span class="fs-5 fw-bold text-dark" id="display-supplier-id">...</span></div>
            <div class="px-3"><small class="d-block text-muted fw-bold">معرف المحفظة</small><span class="fs-5 fw-bold text-success" id="display-wallet-id">...</span></div>
        </div>
    </div>

    <div id="alert-container"></div>

    <!-- إضافة مكتبة التشفير CryptoJS -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js"></script>

    <form id="addSupplierForm" method="POST" enctype="multipart/form-data" action="{{ url_for('add_supplier.add_supplier_submit') }}">
        <input type="hidden" name="sovereign_id" id="hidden-sovereign-id">
        <input type="hidden" name="wallet_code" id="hidden-wallet-code">
        <!-- حقل مخفي لإرسال البيانات المشفرة -->
        <input type="hidden" name="encrypted_payload" id="encrypted-payload">

        <div class="row g-4">
            <div class="col-md-4">
                <div class="card border-0 shadow-sm p-4 h-100">
                    <h5 class="fw-bold mb-4">بيانات الوصول والوثائق</h5>
                    <div class="mb-3"><label class="form-label text-muted small">اسم المستخدم</label><input type="text" id="username" name="username" class="form-control" required></div>
                    <div class="mb-3"><label class="form-label text-muted small">كلمة مرور النظام (تُشفر AES-256 تلقائياً)</label><input type="password" id="password" name="password" class="form-control" required></div>
                    <div class="mb-3"><label class="form-label text-muted small">نوع الوثيقة</label><select id="identity_type" name="identity_type" class="form-select"><option>بطاقة شخصية</option><option>سجل تجاري</option></select></div>
                    <div class="mb-3"><label class="form-label text-muted small">رقم الوثيقة</label><input type="text" id="identity_number" name="identity_number" class="form-control" required></div>
                    <div class="mb-3"><label class="form-label text-muted small">صور الوثيقة</label><input type="file" name="identity_images" class="form-control" multiple required></div>
                </div>
            </div>

            <div class="col-md-4">
                <div class="card border-0 shadow-sm p-4 h-100">
                    <h5 class="fw-bold mb-4">الهوية والتصنيف</h5>
                    <div class="mb-3"><label class="form-label text-muted small">الاسم الكامل</label><input type="text" id="owner_name" name="owner_name" class="form-control" required></div>
                    <div class="mb-3"><label class="form-label text-muted small">الاسم التجاري</label><input type="text" id="trade_name" name="trade_name" class="form-control" required></div>
                    
                    <div class="mb-3">
                        <label class="form-label text-muted small fw-bold">فئة المورد (Activity Category)</label>
                        <div class="input-group">
                            <select name="category" id="categorySelect" class="form-select" required>
                                <option value="" selected disabled>اختر الفئة...</option>
                                <option value="ملابس">ملابس</option>
                                <option value="إلكترونيات">إلكترونيات</option>
                                <option value="القوائم">القوائم</option> <!-- إضافة الفئة المطلوبة -->
                            </select>
                            <button type="button" class="btn btn-outline-primary" onclick="addNewCategory()">+</button>
                        </div>
                    </div>

                    <div class="mb-3"><label class="form-label text-muted small">المحافظة</label><select name="province" id="provinceSelect" class="form-select" required>...</select></div>
                    <div class="mb-3"><label class="form-label text-muted small">المديرية</label><select name="district" id="districtSelect" class="form-select" required disabled>...</select></div>
                </div>
            </div>

            <div class="col-md-4">
                <div class="card border-0 shadow-sm p-4 h-100">
                    <h5 class="fw-bold mb-4">الربط والسيادة المالية</h5>
                    <div class="alert alert-info small">
                        <i class="fas fa-lock"></i> سيتم تشفير كافة البيانات الحساسة باستخدام بروتوكول AES-256 قبل مغادرة المتصفح.
                    </div>
                    <button type="submit" id="submitBtn" class="btn btn-lg w-100 text-white mt-auto" style="background: var(--royal-purple);">اعتماد المورد الآن</button>
                </div>
            </div>
        </div>
    </form>
</div>

<script>
    // مفتاح التشفير (يجب أن يتم تبادله بشكل آمن أو جلبه من الخادم)
    const SECRET_KEY = "YOUR_AES_256_SECRET_KEY_HERE";

    // دالة التعلم التلقائي للفئة
    function addNewCategory() {
        const newCat = prompt("أدخل اسم الفئة الجديدة (مثال: القوائم الذكية):");
        if (newCat && newCat.trim() !== "") {
            const select = document.getElementById('categorySelect');
            
            // التحقق إذا كانت الفئة موجودة مسبقاً
            let exists = false;
            for (let i = 0; i < select.options.length; i++) {
                if (select.options[i].value === newCat) {
                    exists = true;
                    break;
                }
            }

            if (!exists) {
                const option = document.createElement('option');
                option.value = newCat;
                option.textContent = newCat;
                select.appendChild(option);
                select.value = newCat;
                
                // تعلم القائمة: إرسال الفئة الجديدة للخادم ليتم حفظها في قاعدة البيانات
                saveNewCategoryToDB(newCat);
            } else {
                select.value = newCat;
                alert("هذه الفئة موجودة بالفعل في القوائم.");
            }
        }
    }

    function saveNewCategoryToDB(categoryName) {
        console.log("جاري تعلم وحفظ الفئة الجديدة:", categoryName);
        // هنا يتم استدعاء API لحفظ الفئة في قاعدة البيانات
        /*
        fetch('/api/save-category', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ category: categoryName })
        });
        */
    }

    // معالجة إرسال النموذج مع التشفير
    document.getElementById('addSupplierForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = {
            username: document.getElementById('username').value,
            password: document.getElementById('password').value,
            identity_number: document.getElementById('identity_number').value,
            owner_name: document.getElementById('owner_name').value,
            trade_name: document.getElementById('trade_name').value,
            category: document.getElementById('categorySelect').value,
            timestamp: new Date().toISOString()
        };

        // تحويل البيانات إلى نص JSON ثم تشفيرها بـ AES-256
        const jsonString = JSON.stringify(formData);
        const encryptedData = CryptoJS.AES.encrypt(jsonString, SECRET_KEY).toString();

        // وضع البيانات المشفرة في الحقل المخفي
        document.getElementById('encrypted-payload').value = encryptedData;

        console.log("تم تشفير البيانات بنجاح قبل الإرسال.");
        
        // الآن يمكن إرسال النموذج فعلياً
        this.submit();
    });
</script>
{% endblock %}
إضافة فئة تشفير AES-256 وإرسال البيانات مشفرة - Manus
