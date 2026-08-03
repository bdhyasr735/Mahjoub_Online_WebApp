{% extends "admin/admin_base.html" %}

{% block title %}تفاصيل الطلب #{{ order.order_number or (order.id|string)[:8] }} | محجوب{% endblock %}

{% block content %}
<div class="container-fluid py-4">

    <!-- ✅ شريط العنوان وأزرار الإجراءات السريعة -->
    <div class="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
        <div class="d-flex align-items-center gap-3">
            <a href="{{ url_for('admin_orders_bp.list_admin_orders') }}" class="btn btn-outline-secondary rounded-circle p-2" title="عودة لجميع الطلبات">
                <i class="fas fa-arrow-right"></i>
            </a>
            <div>
                <h2 class="fw-bold mb-1" style="color: #2d0b36;">
                    📦 طلب رقم #{{ order.order_number or (order.id|string)[:8] }}
                </h2>
                <p class="text-muted text-sm mb-0">
                    تاريخ الطلب: {{ order.created_at.strftime('%Y-%m-%d %H:%M') if order.created_at else 'غير محدد' }}
                </p>
            </div>
        </div>

        <div class="d-flex align-items-center gap-2">
            <button class="btn btn-outline-dark d-flex align-items-center gap-2" onclick="window.print()">
                <i class="fas fa-print"></i> طباعة الطلب
            </button>
        </div>
    </div>

    <div class="row g-4">
        <!-- 👈 العمود الأيمن: تفاصيل المنتجات والموجز -->
        <div class="col-lg-8">
            <!-- جدول عناصر الطلب -->
            <div class="card border-0 shadow-sm rounded-4 mb-4">
                <div class="card-header bg-white py-3 border-0 d-flex align-items-center justify-content-between">
                    <h5 class="fw-bold mb-0" style="color: #2d0b36;">
                        <i class="fas fa-box-open text-warning me-2"></i> عناصر الطلب
                    </h5>
                    <span class="badge bg-light text-dark border rounded-pill px-3 py-2">
                        إجمالي العناصر: {{ order.items|length if order.items else 0 }}
                    </span>
                </div>
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="bg-light">
                            <tr>
                                <th class="py-3 ps-4">المنتج / البيان</th>
                                <th class="py-3">الرمز (SKU)</th>
                                <th class="py-3 text-center">الكمية</th>
                                <th class="py-3 text-end">سعر الوحدة</th>
                                <th class="py-3 pe-4 text-end">الإجمالي</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% if order.items %}
                                {% for item in order.items %}
                                <tr>
                                    <td class="ps-4">
                                        <div class="fw-bold text-dark">{{ item.title or item.name or 'منتج غير محدد' }}</div>
                                    </td>
                                    <td>
                                        <span class="badge bg-light text-muted border font-monospace">
                                            {{ item.sku or 'N/A' }}
                                        </span>
                                    </td>
                                    <td class="text-center fw-bold">{{ item.qty or item.quantity or 1 }}</td>
                                    <td class="text-end">{{ "{:,.2f}".format(item.price_per_unit or item.price or 0.0) }} ر.ي</td>
                                    <td class="pe-4 text-end fw-bold" style="color: #2d0b36;">
                                        {{ "{:,.2f}".format(item.subtotal or ((item.qty or item.quantity or 1) * (item.price_per_unit or item.price or 0.0))) }} ر.ي
                                    </td>
                                </tr>
                                {% endfor %}
                            {% else %}
                                <tr>
                                    <td colspan="5" class="text-center py-4 text-muted">
                                        لا توجد تفاصيل عناصر مسجلة لهذا الطلب.
                                    </td>
                                </tr>
                            {% endif %}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- الملخص المالي للطلب -->
            <div class="card border-0 shadow-sm rounded-4">
                <div class="card-body p-4">
                    <h5 class="fw-bold mb-3" style="color: #2d0b36;">💰 الملخص المالي</h5>
                    <div class="d-flex justify-content-between py-2 border-bottom text-muted">
                        <span>إجمالي المنتجات:</span>
                        <span class="fw-semibold text-dark">{{ "{:,.2f}".format(order.total_price or 0.0) }} ر.ي</span>
                    </div>
                    <div class="d-flex justify-content-between py-2 border-bottom text-muted">
                        <span>حالة الدفع:</span>
                        {% if order.is_paid %}
                            <span class="badge bg-success-subtle text-success border border-success px-3 py-1">مدفوع بالكامل</span>
                        {% else %}
                            <span class="badge bg-warning-subtle text-dark border border-warning px-3 py-1">غير مدفوع / عند الاستلام</span>
                        {% endif %}
                    </div>
                    <div class="d-flex justify-content-between pt-3 fs-5 fw-bold" style="color: #2d0b36;">
                        <span>المبلغ الإجمالي النهائي:</span>
                        <span style="color: #D4AF37;">{{ "{:,.2f}".format(order.total_price or 0.0) }} ر.ي</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- 👈 العمود الأيسر: التحكم والعميل والمورد -->
        <div class="col-lg-4">
            <!-- التحكم بحالة الطلب -->
            <div class="card border-0 shadow-sm rounded-4 mb-4">
                <div class="card-body p-4">
                    <h5 class="fw-bold mb-3" style="color: #2d0b36;">
                        <i class="fas fa-tasks text-primary me-2"></i> حالة الطلب
                    </h5>
                    
                    <div class="mb-3">
                        <label class="form-label text-muted small fw-semibold">تغيير حالة الطلب:</label>
                        <select class="form-select rounded-3 py-2" id="orderStatusSelect" onchange="updateOrderStatus('{{ order.id }}')">
                            <option value="pending" {% if order.status_code == 'pending' %}selected{% endif %}>⏳ قيد الانتظار (Pending)</option>
                            <option value="processing" {% if order.status_code == 'processing' %}selected{% endif %}>⚙️ قيد التجهيز (Processing)</option>
                            <option value="shipped" {% if order.status_code == 'shipped' %}selected{% endif %}>🚚 تم الشحن (Shipped)</option>
                            <option value="delivered" {% if order.status_code == 'delivered' %}selected{% endif %}>✅ تم التسليم (Delivered)</option>
                            <option value="cancelled" {% if order.status_code == 'cancelled' %}selected{% endif %}>❌ ملغي (Cancelled)</option>
                        </select>
                    </div>

                    <div id="statusAlert" class="mt-2" style="display: none;"></div>
                </div>
            </div>

            <!-- إسناد المورد -->
            <div class="card border-0 shadow-sm rounded-4 mb-4">
                <div class="card-body p-4">
                    <h5 class="fw-bold mb-3" style="color: #2d0b36;">
                        <i class="fas fa-truck-loading text-warning me-2"></i> المورد المرتبط
                    </h5>
                    
                    <div class="mb-3">
                        <label class="form-label text-muted small fw-semibold">ربط بالمورد:</label>
                        <select class="form-select rounded-3 py-2" id="supplierSelect" onchange="updateOrderSupplier('{{ order.id }}')">
                            <option value="0">-- غير مرتبط بمورد --</option>
                            {% if suppliers %}
                                {% for supplier in suppliers %}
                                    <option value="{{ supplier.id }}" {% if order.supplier_id == supplier.id %}selected{% endif %}>
                                        {{ supplier.trade_name or supplier.name }}
                                    </option>
                                {% endfor %}
                            {% endif %}
                        </select>
                    </div>

                    <div id="supplierAlert" class="mt-2" style="display: none;"></div>
                </div>
            </div>

            <!-- معلومات العميل -->
            <div class="card border-0 shadow-sm rounded-4">
                <div class="card-body p-4">
                    <h5 class="fw-bold mb-3" style="color: #2d0b36;">
                        <i class="fas fa-user-circle text-info me-2"></i> بيانات العميل
                    </h5>
                    
                    <div class="d-flex align-items-center gap-3 mb-3">
                        <div class="bg-light rounded-circle p-3 text-secondary">
                            <i class="fas fa-user fa-lg"></i>
                        </div>
                        <div>
                            <div class="fw-bold text-dark">{{ order.customer_name or 'عميل زائر' }}</div>
                            <small class="text-muted d-block">معرف الطلب: {{ order.id }}</small>
                            {% if order.customer_phone %}
                                <small class="text-muted d-block"><i class="fas fa-phone me-1"></i> {{ order.customer_phone }}</small>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- حقل CSRF Token -->
<input type="hidden" name="csrf_token" value="{{ csrf_token() if csrf_token is defined else '' }}">

<script>
function updateOrderStatus(orderId) {
    const statusSelect = document.getElementById('orderStatusSelect');
    const alertDiv = document.getElementById('statusAlert');
    const newStatus = statusSelect.value;
    const csrfToken = document.querySelector('[name="csrf_token"]')?.value || '';

    statusSelect.disabled = true;

    fetch(`/admin/orders/${orderId}/status`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ status: newStatus })
    })
    .then(res => res.json())
    .then(data => {
        alertDiv.style.display = 'block';
        if (data.success) {
            alertDiv.className = 'alert alert-success py-2 px-3 small rounded-3';
            alertDiv.innerText = '✅ ' + (data.message || 'تم تحديث الحالة بنجاح');
        } else {
            alertDiv.className = 'alert alert-danger py-2 px-3 small rounded-3';
            alertDiv.innerText = '❌ ' + (data.message || 'حدث خطأ أثناء التحديث');
        }
    })
    .catch(err => {
        alertDiv.style.display = 'block';
        alertDiv.className = 'alert alert-danger py-2 px-3 small rounded-3';
        alertDiv.innerText = '❌ خطأ في الاتصال: ' + err.message;
    })
    .finally(() => {
        statusSelect.disabled = false;
        setTimeout(() => { alertDiv.style.display = 'none'; }, 4000);
    });
}

function updateOrderSupplier(orderId) {
    const supplierSelect = document.getElementById('supplierSelect');
    const alertDiv = document.getElementById('supplierAlert');
    const supplierId = supplierSelect.value;
    const csrfToken = document.querySelector('[name="csrf_token"]')?.value || '';

    supplierSelect.disabled = true;

    fetch(`/admin/orders/${orderId}/supplier`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ supplier_id: supplierId })
    })
    .then(res => res.json())
    .then(data => {
        alertDiv.style.display = 'block';
        if (data.success) {
            alertDiv.className = 'alert alert-success py-2 px-3 small rounded-3';
            alertDiv.innerText = '✅ ' + (data.message || 'تم تحديث المورد بنجاح');
        } else {
            alertDiv.className = 'alert alert-danger py-2 px-3 small rounded-3';
            alertDiv.innerText = '❌ ' + (data.message || 'حدث خطأ أثناء التحديث');
        }
    })
    .catch(err => {
        alertDiv.style.display = 'block';
        alertDiv.className = 'alert alert-danger py-2 px-3 small rounded-3';
        alertDiv.innerText = '❌ خطأ في الاتصال: ' + err.message;
    })
    .finally(() => {
        supplierSelect.disabled = false;
        setTimeout(() => { alertDiv.style.display = 'none'; }, 4000);
    });
}
</script>
{% endblock %}
