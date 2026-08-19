{# 📂 apps/supplier_wallet/templates/supplier_wallet/wallet.html #}
{% extends "suppliers/base.html" %}

{% from "supplier_wallet/components/kpi_cards.html" import render_kpi_cards %}
{% from "supplier_wallet/components/pagination.html" import render_pagination %}

{% block title %}Mahjoub Online - كشف حساب المحفظة العام{% endblock %}

{% block content %}
<div class="space-y-6 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6" dir="rtl">

    <!-- Flash Messages -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="space-y-3">
                {% for category, message in messages %}
                    <div class="p-4 rounded-xl border text-sm font-bold flex items-center gap-3 shadow-xs {% if category == 'success' %}bg-emerald-50 border-emerald-200 text-emerald-800{% elif category == 'danger' or category == 'error' %}bg-red-50 border-red-200 text-red-800{% else %}bg-blue-50 border-blue-200 text-blue-800{% endif %}">
                        <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                        <span>{{ message }}</span>
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

    <!-- Page Banner -->
    <div class="bg-white p-6 rounded-2xl border border-gray-200/80 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-6 relative overflow-hidden">
        <div class="space-y-2 relative z-10">
            <div class="flex items-center gap-2">
                <span class="w-3 h-3 rounded-full bg-[#4A154B]"></span>
                <h1 class="text-2xl font-black text-gray-900 tracking-tight">كشف حساب المحفظة</h1>
            </div>
            <p class="text-xs text-gray-500 max-w-2xl leading-relaxed">متابعة تفصيلية لكافة العمليات المالية، المبيعات، والإيداعات، وعمليات السحب الخاصة بحسابك في المنصة.</p>
        </div>
        
        <!-- الأزرار العلوية -->
        <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 shrink-0 relative z-10">
            <a href="{{ url_for('supplier_wallet.wallet_print_statement', **request.args) }}" class="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 font-bold text-xs transition-all shadow-xs">
                <svg class="w-4 h-4 text-rose-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                <span>تصدير PDF</span>
            </a>

            <a href="{{ url_for('supplier_wallet.submit_withdrawal') }}" class="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-[#4A154B] hover:bg-[#3B113F] text-white font-black text-xs shadow-md transition-all">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
                <span>طلب سحب مبيعات جديد</span>
            </a>
        </div>
    </div>

    <!-- 1. Summary KPI Cards Component -->
    {{ render_kpi_cards(summary) }}

    <!-- 2. قسم البحث والتصفية المتكامل (مربوط بمسار wallet_dashboard) -->
    <div class="bg-white p-5 rounded-2xl border border-gray-200/80 shadow-xs">
        <form method="GET" action="{{ url_for('supplier_wallet.wallet_dashboard') }}" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 items-end">
            
            <!-- حقل البحث اللحظي (قابق للبحث بالمرجع أو البيان) -->
            <div>
                <label class="block text-[11px] font-bold text-gray-700 mb-1">بحث برقم المرجع أو البيان</label>
                <input type="text" name="q" value="{{ request.args.get('q', '') }}" placeholder="ابحث هنا..." class="w-full px-3 py-2.5 rounded-xl border border-gray-200 text-xs font-medium focus:border-[#4A154B] focus:ring-1 focus:ring-[#4A154B]">
            </div>

            <!-- فلتر النوع -->
            <div>
                <label class="block text-[11px] font-bold text-gray-700 mb-1">نوع الحركة</label>
                <select name="type" class="w-full px-3 py-2.5 rounded-xl border border-gray-200 text-xs font-bold text-gray-800 focus:border-[#4A154B]">
                    <option value="all" {% if active_type == 'all' %}selected{% endif %}>جميع الأنواع</option>
                    <option value="sale" {% if active_type == 'sale' %}selected{% endif %}>مبيعات</option>
                    <option value="withdrawal" {% if active_type == 'withdrawal' %}selected{% endif %}>سحوبات</option>
                    <option value="deposit" {% if active_type == 'deposit' %}selected{% endif %}>إيداعات</option>
                </select>
            </div>

            <!-- تاريخ البداية -->
            <div>
                <label class="block text-[11px] font-bold text-gray-700 mb-1">من تاريخ</label>
                <input type="date" name="start_date" value="{{ request.args.get('start_date', '') }}" class="w-full px-3 py-2 rounded-xl border border-gray-200 text-xs font-mono">
            </div>

            <!-- تاريخ النهاية -->
            <div>
                <label class="block text-[11px] font-bold text-gray-700 mb-1">إلى تاريخ</label>
                <input type="date" name="end_date" value="{{ request.args.get('end_date', '') }}" class="w-full px-3 py-2 rounded-xl border border-gray-200 text-xs font-mono">
            </div>

            <!-- أزرار تنفيذ الفلترة -->
            <div class="flex gap-2">
                <button type="submit" class="flex-1 py-2.5 bg-gray-900 hover:bg-black text-white rounded-xl text-xs font-bold transition-all shadow-xs flex items-center justify-center gap-1.5">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                    <span>بحث وتصفية</span>
                </button>
                <a href="{{ url_for('supplier_wallet.wallet_dashboard') }}" class="px-3 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-xl text-xs font-bold transition-all" title="إعادة تعيين">
                    إلغاء
                </a>
            </div>

        </form>
    </div>

    <!-- 3. جدول الحركات المالية مع الترقيم التسلسلي الدقيق (1, 2, 3...) -->
    <div class="bg-white rounded-2xl shadow-xs border border-gray-200/80 overflow-hidden">
        <div class="p-5 border-b border-gray-100 flex items-center justify-between">
            <h3 class="text-sm font-black text-gray-800 flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-[#4A154B]"></span>
                سجل الحركات المالية المعتمدة
            </h3>
        </div>
        
        <div class="overflow-x-auto">
            <table class="w-full text-right text-xs">
                <thead class="bg-gray-50 text-gray-500 font-bold border-b border-gray-100">
                    <tr>
                        <th class="py-3 px-4 w-16 text-center">#</th>
                        <th class="py-3 px-4">رقم المرجع / الحوالة</th>
                        <th class="py-3 px-4">التاريخ والوقت</th>
                        <th class="py-3 px-4">نوع الحركة</th>
                        <th class="py-3 px-4">المبلغ</th>
                        <th class="py-3 px-4">البيان / التفاصيل</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-100 text-gray-700">
                    {% if transactions %}
                        {% set page_num = pagination.page if pagination and pagination.page is defined else 1 %}
                        {% set per_page_num = pagination.per_page if pagination and pagination.per_page is defined else 10 %}
                        
                        {% for tx in transactions %}
                        <tr class="hover:bg-gray-50/50 transition-colors">
                            <!-- الترقيم التسلسلي التلقائي المستمر عبر الصفحات -->
                            <td class="py-3.5 px-4 font-mono font-bold text-gray-400 text-center">
                                {{ ((page_num - 1) * per_page_num) + loop.index }}
                            </td>
                            <td class="py-3.5 px-4 font-mono font-bold text-gray-900">{{ tx.reference_number or tx.transfer_number or '-' }}</td>
                            <td class="py-3.5 px-4 font-mono text-gray-500">{{ tx.created_at.strftime('%Y-%m-%d %H:%M') if tx.created_at else '-' }}</td>
                            <td class="py-3.5 px-4 font-bold">
                                <span class="px-2.5 py-1 rounded-lg bg-purple-50 text-[#4A154B] text-[11px]">
                                    {{ tx.trans_type or 'حركة مالية' }}
                                </span>
                            </td>
                            <td class="py-3.5 px-4 font-mono font-black {% if tx.amount and tx.amount > 0 %}text-emerald-600{% else %}text-gray-900{% endif %}" dir="ltr">
                                {{ "{:,.2f}".format(tx.amount) }} {{ summary.currency }}
                            </td>
                            <td class="py-3.5 px-4 text-gray-600 max-w-xs truncate" title="{{ tx.description }}">
                                {{ tx.description or '-' }}
                            </td>
                        </tr>
                        {% endfor %}
                    {% else %}
                        <tr>
                            <td colspan="6" class="py-10 text-center text-gray-400 font-medium">
                                لا توجد حركات مالية مطابقة لخيارات البحث أو التصفية الحالية.
                            </td>
                        </tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
    </div>

    <!-- 4. أزرار الانتقال بين الصفحات (Pagination) -->
    {{ render_pagination(pagination, endpoint='supplier_wallet.wallet_dashboard') }}

</div>
{% endblock %}
