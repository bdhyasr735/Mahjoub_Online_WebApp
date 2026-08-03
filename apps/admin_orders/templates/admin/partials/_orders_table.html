<div class="table-responsive bg-white shadow-sm rounded-4 p-3">
    <table class="table table-hover align-middle mb-0">
        <thead class="bg-light rounded-3">
            <tr>
                <th style="width: 50px;">#</th>
                <th>رقم الطلب</th>
                <th>العميل</th>
                <th style="min-width: 180px;">المورد</th>
                <th>التاريخ</th>
                <th>الإجمالي (ر.س)</th>
                <th style="min-width: 160px;">الحالة</th>
                <th>الإجراءات</th>
            </tr>
        </thead>
        <tbody>
            {% for order in orders %}
            <tr>
                <td>{{ loop.index + (pagination.current_page - 1) * pagination.per_page }}</td>
                <td><strong>{{ order.code or '#' ~ order.id|truncate(8) }}</strong></td>
                <td>{{ order.customer_name or 'غير معروف' }}</td>
                <td>
                    <!-- ✅ قائمة الموردين مع بحث Tom Select -->
                    <select class="form-select form-select-sm supplier-select" onchange="updateOrderSupplier('{{ order.id }}', this.value)">
                        <option value="0">-- غير مرتبط --</option>
                        {% for supplier in suppliers %}
                        <option value="{{ supplier.id }}" {% if order.supplier_id == supplier.id %}selected{% endif %}>
                            {{ supplier.trade_name }}
                        </option>
                        {% endfor %}
                    </select>
                </td>
                <td>{{ order.created_at.strftime('%Y-%m-%d') if order.created_at else '—' }}</td>
                <td class="fw-bold text-dark-purple">{{ order.total_price or 0 }}</td>
                <td>
                    <!-- ✅ قائمة حالات الطلب (قابلة للتعديل) -->
                    <select class="form-select form-select-sm status-select" onchange="updateOrderStatus('{{ order.id }}', this.value)">
                        {% set statuses = ['pending', 'confirmed', 'paid', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded', 'returned'] %}
                        {% for s in statuses %}
                        <option value="{{ s }}" {% if order.status_code == s %}selected{% endif %}>
                            {{ s|title }}
                        </option>
                        {% endfor %}
                    </select>
                </td>
                <td>
                    <a href="{{ url_for('admin_orders_bp.view_admin_order', order_id=order.id) }}" class="btn btn-sm btn-outline-primary">
                        <i class="fas fa-eye"></i>
                    </a>
                </td>
            </tr>
            {% else %}
            <tr>
                <td colspan="8" class="text-center py-4 text-muted">
                    <i class="fas fa-shopping-bag fa-2x mb-2 opacity-25 d-block"></i>
                    لا توجد طلبات في النظام حتى الآن.
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<script>
// ✅ تحديث حالة الطلب
function updateOrderStatus(orderId, status) {
    fetch(`/admin/orders/orders/${orderId}/status`, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token() if csrf_token is defined else '' }}'
        },
        body: JSON.stringify({ status: status })
    })
    .then(r => r.json())
    .then(data => {
        if (!data.success) alert('❌ ' + data.message);
    })
    .catch(() => alert('❌ حدث خطأ في الاتصال'));
}

// ✅ تحديث المورد للطلب
function updateOrderSupplier(orderId, supplierId) {
    fetch(`/admin/orders/orders/${orderId}/supplier`, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token() if csrf_token is defined else '' }}'
        },
        body: JSON.stringify({ supplier_id: supplierId === "0" ? 0 : parseInt(supplierId) })
    })
    .then(r => r.json())
    .then(data => {
        if (!data.success) alert('❌ ' + data.message);
        else location.reload(); // تحديث الصفحة لإظهار اسم المورد الجديد
    })
    .catch(() => alert('❌ حدث خطأ في الاتصال'));
}

// ✅ تفعيل مكتبة Tom Select للموردين
document.addEventListener('DOMContentLoaded', function() {
    if (typeof TomSelect !== 'undefined') {
        document.querySelectorAll('.supplier-select').forEach(el => {
            if (!el.tomselect) new TomSelect(el, {
                plugins: ['remove_button'],
                placeholder: 'ابحث عن المورد...',
                searchField: ['text'],
                maxOptions: 10
            });
        });
    }
});
</script>
