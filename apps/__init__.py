
{% extends "admin/admin_base.html" %}

{% block title %}تعميد مورد جديد - محجوب أونلاين{% endblock %}

{% block content %}
<div style="max-width: 1000px; margin: auto;">
    <div style="background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); overflow: hidden; border-top: 5px solid #D4AF37;">
        
        <div style="background: #1a0b2e; padding: 25px; color: #D4AF37; display: flex; justify-content: space-between; align-items: center;">
            <h2 style="margin: 0; font-size: 1.5rem;"><i class="fas fa-file-signature"></i> وثيقة تعميد مورد سيادي</h2>
            <span style="background: rgba(212, 175, 55, 0.2); padding: 5px 15px; border-radius: 20px; font-size: 0.8rem; border: 1px solid #D4AF37;">
                المعرف: SUP-MHA_963{{ next_id }}
            </span>
        </div>

        <form id="supplierForm" action="{{ url_for('add_supplier.add_supplier') }}" method="POST" enctype="multipart/form-data" style="padding: 30px;">
            
            <!-- القسم الأول: الهوية الرقمية -->
            <h4 style="color: #1a0b2e; border-bottom: 2px solid #f0f2f5; padding-bottom: 10px;"><i class="fas fa-fingerprint"></i> بيانات الحساب والنشاط</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
                <div>
                    <label>اسم المستخدم (النظام)</label>
                    <input type="text" name="username" placeholder="مثلاً: ali_trading" required style="width:100%; padding:10px; border-radius:8px; border:1px solid #ddd;">
                </div>
                <div>
                    <label>نوع النشاط التجاري</label>
                    <select id="activitySelect" class="form-select" style="width:100%; padding:10px; border-radius:8px; border:1px solid #ddd;">
                        <option value="تجزئة">تجزئة</option>
                        <option value="جملة">جملة</option>
                        <option value="توزيع">توزيع</option>
                        <option value="manual">إدخال يدوي...</option>
                    </select>
                    <input type="hidden" name="activity_type" id="activityHidden">
                    <input type="text" id="activityManual" placeholder="اكتب نوع النشاط هنا" style="display:none; width:100%; margin-top:10px; padding:10px; border-radius:8px; border:1px solid #D4AF37;">
                </div>
            </div>

            <!-- القسم الثاني: بيانات التوثيق -->
            <h4 style="color: #1a0b2e; border-bottom: 2px solid #f0f2f5; padding-bottom: 10px;"><i class="fas fa-id-card"></i> التوثيق والهوية السيادية</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
                <div>
                    <label>اسم المالك الكامل</label>
                    <input type="text" name="owner_name" required style="width:100%; padding:10px; border-radius:8px; border:1px solid #ddd;">
                </div>
                <div>
                    <label>صورة الهوية / السجل التجاري</label>
                    <input type="file" name="identity_image" accept="image/*" required style="width:100%; padding:8px;">
                </div>
                <div>
                    <label>الاسم التجاري للمنشأة</label>
                    <input type="text" name="trade_name" placeholder="كما يظهر في اللوحة" required style="width:100%; padding:10px; border-radius:8px; border:1px solid #ddd;">
                </div>
                <div>
                    <label>رقم الهاتف (واتساب)</label>
                    <input type="tel" name="phone" pattern="7[0-9]{8}" placeholder="7XXXXXXXX" required style="width:100%; padding:10px; border-radius:8px; border:1px solid #ddd;">
                </div>
            </div>

            <!-- القسم الثالث: البيانات الجغرافية والمالية -->
            <h4 style="color: #1a0b2e; border-bottom: 2px solid #f0f2f5; padding-bottom: 10px;"><i class="fas fa-map-marker-alt"></i> الموقع والربط المالي</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 30px;">
                <div>
                    <label>المحافظة</label>
                    <select name="province" style="width:100%; padding:10px; border-radius:8px; border:1px solid #ddd;">
                        <option value="عدن">عدن</option>
                        <option value="الحديدة">الحديدة (الخوخة)</option>
                        <option value="تعز">تعز (المخاء)</option>
                    </select>
                </div>
                <div>
                    <label>المديرية</label>
                    <input type="text" name="district" placeholder="الخوخة / المخاء..." style="width:100%; padding:10px; border-radius:8px; border:1px solid #ddd;">
                </div>
                <div>
                    <label>رقم حساب بنك الكريمي</label>
                    <input type="text" name="bank_acc" placeholder="1234567" style="width:100%; padding:10px; border-radius:8px; border:1px solid #ddd;">
                </div>
            </div>

            <div style="text-align: left; background: #f8fafc; padding: 20px; border-radius: 12px;">
                <button type="submit" style="background: #1a0b2e; color: #D4AF37; border: 2px solid #D4AF37; padding: 15px 40px; border-radius: 10px; font-weight: bold; cursor: pointer; transition: 0.3s;">
                    إتمام التعميد والأرشفة <i class="fas fa-check-double"></i>
                </button>
            </div>
        </form>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    // منطق التعامل مع الإدخال اليدوي للنشاط التجاري
    const activitySelect = document.getElementById('activitySelect');
    const activityManual = document.getElementById('activityManual');
    const activityHidden = document.getElementById('activityHidden');

    activitySelect.addEventListener('change', function() {
        if (this.value === 'manual') {
            activityManual.style.display = 'block';
            activityManual.required = true;
        } else {
            activityManual.style.display = 'none';
            activityManual.required = false;
            activityHidden.value = this.value;
        }
    });

    // معالجة إرسال النموذج عبر AJAX لضمان تجربة مستخدم "سيادية"
    document.getElementById('supplierForm').addEventListener('submit', function(e) {
        if (activitySelect.value === 'manual') {
            activityHidden.value = activityManual.value;
        }
        
        e.preventDefault();
        const formData = new FormData(this);

        fetch(this.action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                Swal.fire({
                    title: 'تم التعميد!',
                    text: data.message,
                    icon: 'success',
                    confirmButtonColor: '#1a0b2e',
                    confirmButtonText: 'موافق'
                }).then(() => {
                    window.location.href = "{{ url_for('admin_dashboard.index') }}";
                });
            } else {
                Swal.fire('خطأ في النظام', data.message, 'error');
            }
        });
    });
</script>
{% endblock %}
