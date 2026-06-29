{# 📂 apps/supplier_wallet/templates/supplier_wallet/supplier_wallet.html #}
{% extends 'suppliers/base.html' %} 

{% block title %}خزانة المورد | محجوب أونلاين{% endblock %}

{% block content %}
<style>
    :root { 
        --royal-purple: #2e003e; 
        --royal-gold: #d4af37; 
        --light-purple: #5a0077; 
    }
    .text-royal-purple { color: var(--royal-purple) !important; }
    .balance-card { 
        cursor: pointer; 
        transition: all 0.3s ease; 
        color: white; 
        background: linear-gradient(135deg, var(--royal-purple), var(--light-purple)); 
        border-bottom: 4px solid var(--royal-gold); 
    }
    .table-head-custom { background-color: var(--royal-purple) !important; color: var(--royal-gold) !important; }
    .summary-footer { background-color: var(--royal-purple) !important; color: var(--royal-gold) !important; }
    .search-box { border: 2px solid var(--royal-purple); border-radius: 20px; }
</style>

<div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold text-royal-purple"><i class="fas fa-vault"></i> خزانة المورد</h2>
        <button class="btn btn-dark" onclick="window.print()"><i class="fas fa-file-pdf"></i> تصدير (PDF)</button>
    </div>

    <div class="row mb-4 g-2">
        <div class="col-md-8">
            <input type="text" id="searchInput" class="form-control search-box px-3" placeholder="ابحث برقم السند أو تفاصيل الحركة...">
        </div>
        <div class="col-md-4">
            <select class="form-select search-box" onchange="filterTable(this.value)">
                <option value="ALL">جميع العملات</option>
                <option value="SAR">SAR</option>
                <option value="YER">YER</option>
                <option value="USD">USD</option>
            </select>
        </div>
    </div>

    <div class="card shadow-sm border-0">
        <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
                <thead class="table-head-custom">
                    <tr>
                        <th class="px-4">التاريخ</th>
                        <th>البيان</th>
                        <th>رقم السند</th>
                        <th>مدين</th>
                        <th>دائن</th>
                        <th class="text-center">العملة</th>
                    </tr>
                </thead>
                <tbody id="tableBody">
                    {% for trans in transactions %}
                    <tr class="trans-row" data-currency="{{ trans.currency }}" data-search="{{ trans.voucher_number }} {{ trans.description }}">
                        <td class="px-4">{{ trans.created_at.strftime('%Y-%m-%d') }}</td>
                        <td><strong>{{ trans.description }}</strong></td>
                        <td>
                            <a href="{{ url_for('orders.view_order', order_id=trans.reference_number) }}" class="text-decoration-none fw-bold text-primary">
                                {{ trans.voucher_number }}
                            </a>
                        </td>
                        <td class="text-danger fw-bold">{{ trans.amount if trans.trans_type == 'debit' else '-' }}</td>
                        <td class="text-success fw-bold">{{ trans.amount if trans.trans_type == 'credit' else '-' }}</td>
                        <td class="text-center"><span class="badge bg-dark">{{ trans.currency }}</span></td>
                    </tr>
                    {% else %}
                    <tr><td colspan="6" class="text-center py-4">لا توجد حركات مالية حالياً.</td></tr>
                    {% endfor %}
                </tbody>
                <tfoot class="bg-light fw-bold">
                    <tr class="summary-footer">
                        <td colspan="6" class="text-center">
                            إجمالي الرصيد المتاح: {{ "{:,.2f}".format(wallet.balance_sar) }} SAR
                        </td>
                    </tr>
                </tfoot>
            </table>
        </div>
        {# الترقيم الديناميكي #}
        <div class="d-flex justify-content-center py-3 bg-light border-top">
            {{ pagination.links }}
        </div>
    </div>
</div>

<script>
    // فلتر العملات
    function filterTable(currency) {
        document.querySelectorAll('.trans-row').forEach(row => {
            row.style.display = (currency === 'ALL' || row.dataset.currency === currency) ? '' : 'none';
        });
    }

    // فلتر البحث النصي المباشر
    document.getElementById('searchInput').addEventListener('keyup', function() {
        let filter = this.value.toLowerCase();
        document.querySelectorAll('.trans-row').forEach(row => {
            row.style.display = row.dataset.search.toLowerCase().includes(filter) ? '' : 'none';
        });
    });
</script>
{% endblock %}
