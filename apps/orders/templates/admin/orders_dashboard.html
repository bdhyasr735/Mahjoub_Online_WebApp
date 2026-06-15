{% extends "admin/admin_base.html" %} 

{% block content %}
<div class="container-fluid mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h4 class="mb-0 fw-bold">إدارة الطلبات</h4>
            <small class="text-muted">مزامنة وإدارة الطلبات الواردة من قمرة</small>
        </div>
        <button class="btn btn-primary px-4 shadow-sm" id="syncBtn" onclick="syncOrders()">
            <i class="fas fa-sync me-2"></i> مزامنة الطلبات
        </button>
    </div>

    <div class="card shadow-sm border-0 rounded-3">
        <div class="card-body p-0">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="bg-light text-secondary">
                        <tr>
                            {% for col in columns %}
                                <th class="{{ 'ps-4' if loop.first }}">{{ col.label }}</th>
                            {% endfor %}
                            <th class="text-center">الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% if orders %}
                            {% for order in orders %}
                            <tr>
                                {% for col in columns %}
                                    <td class="{{ 'ps-4' if loop.first }}">
                                        {% if col.key == 'status' %}
                                            <select class="form-select form-select-sm border-0 bg-light w-auto" 
                                                    onchange="updateStatus(this, '{{ order.id }}', '{{ col.key }}')">
                                                <option value="pending" {% if order.status == 'pending' %}selected{% endif %}>قيد الانتظار</option>
                                                <option value="paid" {% if order.status == 'paid' %}selected{% endif %}>مدفوع</option>
                                                <option value="delivered" {% if order.status == 'delivered' %}selected{% endif %}>تم التوصيل</option>
                                            </select>
                                        {% elif col.key == 'total' %}
                                            <span class="badge bg-light text-dark border">{{ order.total }} ريال</span>
                                        {% elif col.key == 'created_at' %}
                                            <span class="text-muted small">{{ order.created_at.strftime('%Y-%m-%d') if order.created_at else '-' }}</span>
                                        {% else %}
                                            <span class="{{ 'fw-bold text-primary' if loop.first }}">{{ order[col.key] or 'غير محدد' }}</span>
                                        {% endif %}
                                    </td>
                                {% endfor %}
                                <td class="text-center">
                                    <button class="btn btn-sm btn-outline-secondary border-0"><i class="fas fa-eye"></i></button>
                                </td>
                            </tr>
                            {% endfor %}
                        {% else %}
                            <tr>
                                <td colspan="{{ columns|length + 1 }}" class="text-center py-5 text-muted">
                                    <i class="fas fa-inbox fa-3x mb-3 d-block opacity-25"></i>
                                    لا توجد طلبات لعرضها حالياً. اضغط على "مزامنة الطلبات" لجلب البيانات.
                                </td>
                            </tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<script>
    async function syncOrders() {
        const btn = document.getElementById('syncBtn');
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> جاري المزامنة...';
        
        try {
            // نستخدم المسار الكامل بناءً على الـ Blueprint (orders)
            const response = await fetch("{{ url_for('orders.sync_orders') }}", { 
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            });
            const result = await response.json();
            if (result.success) {
                location.reload(); 
            } else {
                throw new Error(result.message);
            }
        } catch (e) {
            alert('خطأ في المزامنة: ' + e.message);
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-sync me-2"></i> مزامنة الطلبات';
        }
    }
</script>
{% endblock %}
