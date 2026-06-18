{% extends 'admin/admin_base.html' %}

{% block title %}إدارة الطلبات | القيادة المركزية{% endblock %}

{% block content %}
<div class="container-fluid mt-4" style="direction: rtl; text-align: right; font-family: 'Cairo', sans-serif;">
    
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <a href="{{ url_for('admin_dashboard.dashboard') }}" class="btn btn-outline-secondary px-3 py-2 fw-bold me-2" style="border-radius: 6px; border-color: #6A1B9A; color: #6A1B9A;">
                <i class="bi bi-arrow-right me-1"></i> رجوع
            </a>
        </div>
        
        <form action="{{ url_for('orders.sync_all') }}" method="POST" id="syncForm">
            <button type="submit" class="btn text-white px-4 py-2 fw-bold" id="syncBtn" style="border-radius: 6px; background: linear-gradient(45deg, #6A1B9A, #8E24AA); border: none; box-shadow: 0 4px 12px rgba(106, 27, 154, 0.2);">
                <i class="bi bi-cloud-download me-2"></i> مزامنة البيانات من قمرة
            </button>
        </form>
    </div>

    {# قسم الإحصائيات #}
    <div class="row mb-4">
        {% for title, count, color, icon in [
            ('الطلبات الملغاة', 0, '#D32F2F', 'bi-x-circle'), 
            ('الطلبات المكتملة', 0, '#388E3C', 'bi-check2-circle'), 
            ('إجمالي المبيعات الإقليمية', '0.00 ر.س', '#D4AF37', 'bi-wallet2'), 
            ('عدد الطلبات المتزامنة', pagination.total if pagination else 0, '#6A1B9A', 'bi-boxes')
        ] %}
        <div class="col-md-3">
            <div class="card shadow-sm border-0 position-relative" style="border-radius: 8px; border-right: 4px solid {{ color }} !important;">
                <div class="card-body d-flex align-items-center justify-content-between">
                    <div>
                        <h6 class="text-muted fw-bold mb-1" style="font-size: 0.85rem;">{{ title }}</h6>
                        <h3 class="fw-bold my-1" style="color: #1A1A1A;">{{ count }}</h3>
                    </div>
                    <div class="fs-2 text-muted opacity-25">
                        <i class="bi {{ icon }}" style="color: {{ color }};"></i>
                    </div>
                </div>
                <div class="progress position-absolute bottom-0 start-0 end-0" style="height: 3px; border-radius: 0 0 8px 8px;">
                    <div class="progress-bar" style="width: 100%; background-color: {{ color }};"></div>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>

    {# جدول الطلبات #}
    <div class="card border-0 shadow-sm" style="border-radius: 8px; overflow: hidden; border: 1px solid rgba(106, 27, 154, 0.08);">
        <div class="table-responsive">
            <table class="table table-hover align-middle mb-0" id="ordersTable">
                <thead style="background-color: #FAF7FC; color: #4A148C; font-size: 0.9rem; border-bottom: 2px solid rgba(106, 27, 154, 0.1);">
                    <tr>
                        <th class="ps-4">رقم الطلب</th>
                        <th>العميل</th>
                        <th>التليفون</th>
                        <th>الإجمالي</th>
                        <th>الحالة</th>
                        <th>اسم المورد (محجوب)</th>
                        <th>التاريخ</th>
                        <th class="text-center">الإجراءات</th>
                    </tr>
                </thead>
                <tbody>
                    {% for order in pagination.items %}
                    <tr class="order-row">
                        <td class="ps-4 fw-bold" style="color: #6A1B9A;">#{{ order.order_id or order.id[:8] }}</td>
                        <td class="fw-bold">{{ order.customer_name or '---' }}</td>
                        <td>{{ order.customer_phone or '---' }}</td>
                        <td>{{ "%.2f"|format(order.total_price or 0) }} ر.س</td>
                        <td>
                             <span class="badge bg-light text-dark border">{{ order.order_status }}</span>
                        </td>
                        <td>
                            {# عرض اسم المورد كنص مباشرة بدلاً من القائمة المنسدلة #}
                            <span class="text-primary fw-bold">{{ order.supplier_name or 'غير محدد' }}</span>
                        </td>
                        <td class="text-muted">{{ order.created_at_api.strftime('%Y-%m-%d') if order.created_at_api else '---' }}</td>
                        <td class="text-center">
                            <a href="{{ url_for('orders.process_order', order_id=order.id) }}" class="btn btn-sm" style="color: #6A1B9A;"><i class="bi bi-eye"></i></a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        {# الترقيم المطور #}
        {% if pagination and pagination.pages > 1 %}
        <div class="card-footer bg-white py-4 border-top-0 d-flex justify-content-between align-items-center">
            <div class="text-muted fw-bold" style="font-size: 0.85rem;">
                صفحة <span style="color: #6A1B9A;">{{ pagination.page }}</span> من <span style="color: #6A1B9A;">{{ pagination.pages }}</span>
            </div>
            <nav>
                <ul class="pagination mb-0 shadow-sm" style="border-radius: 8px;">
                    <li class="page-item {% if not pagination.has_prev %}disabled{% endif %}">
                        <a class="page-link" href="{{ url_for('orders.orders_dashboard', page=pagination.prev_num) if pagination.has_prev else '#' }}">السابق</a>
                    </li>
                    {% for page_num in pagination.iter_pages(left_edge=1, right_edge=1, left_current=2, right_current=2) %}
                        {% if page_num %}
                            <li class="page-item {% if page_num == pagination.page %}active{% endif %}">
                                <a class="page-link" href="{{ url_for('orders.orders_dashboard', page=page_num) }}">{{ page_num }}</a>
                            </li>
                        {% else %}
                            <li class="page-item disabled"><span class="page-link">...</span></li>
                        {% endif %}
                    {% endfor %}
                    <li class="page-item {% if not pagination.has_next %}disabled{% endif %}">
                        <a class="page-link" href="{{ url_for('orders.orders_dashboard', page=pagination.next_num) if pagination.has_next else '#' }}">التالي</a>
                    </li>
                </ul>
            </nav>
        </div>
        {% endif %}
    </div>
</div>

<style>
    .page-link { color: #6A1B9A !important; border: none !important; padding: 0.5rem 1rem; }
    .page-item.active .page-link { background-color: #6A1B9A !important; color: #FFF !important; border-radius: 6px; }
</style>
{% endblock %}
