{% extends 'admin/admin_base.html' %}

{% block title %}قائمة الشركاء{% endblock %}

{% block content %}
<div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h3 class="fw-bold text-royal-purple"><i class="fas fa-handshake me-2"></i> قائمة الموردين الشاملة</h3>
            <p class="text-muted mb-0">إدارة بيانات الموردين، المواقع، والحسابات</p>
        </div>
        <a href="#" class="btn btn-royal-purple"><i class="fas fa-user-plus me-2"></i>إضافة مورد جديد</a>
    </div>

    <div class="card border-0 shadow-sm p-3 mb-4">
        <form method="GET" action="{{ url_for('supplier_app.list_suppliers') }}" class="row g-3">
            <div class="col-md-3"><input type="text" name="search" class="form-control" placeholder="اسم المورد أو الكود..." value="{{ search or '' }}"></div>
            <div class="col-md-2"><input type="text" name="gov" class="form-control" placeholder="المحافظة" value="{{ gov or '' }}"></div>
            <div class="col-md-2"><select name="rank" class="form-select"><option value="">الرتبة</option><option value="gold">ذهبي</option><option value="silver">فضي</option></select></div>
            <div class="col-md-2"><button type="submit" class="btn btn-royal-purple w-100">فلترة</button></div>
        </form>
    </div>

    <div class="card border-0 shadow-sm">
        <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                    <tr>
                        <th>كود / اسم المورد</th>
                        <th>المالك والموقع</th>
                        <th>التواصل</th>
                        <th>البيانات البنكية/الهوية</th>
                        <th>الرتبة والحالة</th>
                        <th>طاقم العمل</th>
                        <th class="text-center">إجراءات</th>
                    </tr>
                </thead>
                <tbody>
                    {% for s in suppliers %}
                    <tr>
                        <td>
                            <div class="fw-bold">{{ s.trade_name }}</div>
                            <small class="text-muted">{{ s.supplier_code }}</small>
                        </td>
                        <td>
                            <div class="small fw-bold">المالك: {{ s.supplier_profile.owner_name or '---' }}</div>
                            <small class="text-muted">{{ s.supplier_profile.governorate }} - {{ s.supplier_profile.district }}</small>
                        </td>
                        <td>
                            <div class="small"><i class="fas fa-phone"></i> {{ s.phone_primary }}</div>
                            <div class="small text-muted"><i class="fas fa-envelope"></i> {{ s.supplier_profile.email }}</div>
                        </td>
                        <td>
                            <small>ح.بنكي: {{ s.supplier_profile.bank_account_enc[:10] }}***</small><br>
                            <small>هوية: {{ s.supplier_profile.id_number_enc[:4] }}***</small>
                        </td>
                        <td>
                            <span class="badge bg-{{ 'success' if s.status == 'active' else 'danger' }}">{{ s.status }}</span>
                            <span class="badge bg-warning">{{ s.rank }}</span>
                        </td>
                        <td><span class="badge bg-info">{{ s.staff_members|length }} موظف</span></td>
                        <td class="text-center">
                            <a href="{{ url_for('supplier_app.edit_supplier', id=s.id) }}" class="btn btn-sm btn-outline-secondary" title="تعديل"><i class="fas fa-pen"></i></a>
                            <a href="{{ url_for('wallet_app.manage_wallet', supplier_id=s.id) }}" class="btn btn-sm btn-primary" title="المحفظة"><i class="fas fa-wallet"></i></a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}
