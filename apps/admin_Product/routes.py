{# 📂 apps/admin_Product/templates/admin_Product/products_list.html #}
{% extends "admin/admin_base.html" %}

{% block title %}إدارة المنتجات - متجر محجوب أونلاين{% endblock %}

{% block content %}
<!-- Toolbar Section -->
<section class="bg-slate-900 border border-slate-700 rounded-2xl p-5 shadow-xl mb-6">
    <form method="GET" action="{{ url_for('admin_Product.list_products') }}" class="grid grid-cols-1 md:grid-cols-4 gap-4">
        
        <div class="md:col-span-2">
            <label class="block text-[10px] uppercase tracking-widest font-bold text-slate-400 mb-2">البحث</label>
            <input type="text" name="search" value="{{ search }}" placeholder="ابحث باسم المنتج أو SKU..." 
                   class="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-slate-200 focus:ring-2 focus:ring-amber-400 outline-none transition-all">
        </div>

        <div>
            <label class="block text-[10px] uppercase tracking-widest font-bold text-slate-400 mb-2">الحالة</label>
            <select name="status" onchange="this.form.submit()" class="w-full py-2 px-3 bg-slate-800 border border-slate-700 rounded-xl text-sm text-slate-200 focus:ring-2 focus:ring-amber-400 outline-none">
                <option value="all">الكل</option>
                <option value="active" {% if selected_status == 'active' %}selected{% endif %}>نشط</option>
                <option value="draft" {% if selected_status == 'draft' %}selected{% endif %}>مسودة</option>
            </select>
        </div>

        <div>
            <label class="block text-[10px] uppercase tracking-widest font-bold text-slate-400 mb-2">التصنيف</label>
            <select name="collection" onchange="this.form.submit()" class="w-full py-2 px-3 bg-slate-800 border border-slate-700 rounded-xl text-sm text-slate-200 focus:ring-2 focus:ring-amber-400 outline-none">
                <option value="all">جميع التصنيفات</option>
                {% for c in collections %}<option value="{{ c }}" {% if selected_collection == c %}selected{% endif %}>{{ c }}</option>{% endfor %}
            </select>
        </div>
    </form>
</section>

<!-- Table Section -->
<section class="bg-slate-900 border border-slate-700 rounded-2xl shadow-xl overflow-hidden">
    <div class="px-6 py-4 border-b border-slate-700 bg-slate-800/50 flex justify-between items-center">
        <h2 class="font-bold text-slate-200 text-sm">قائمة المنتجات ({{ pagination.total_items or 0 }})</h2>
    </div>

    <div class="overflow-x-auto">
        <table class="w-full text-right text-sm">
            <thead class="bg-slate-950 text-slate-500 font-bold uppercase text-[10px] tracking-widest">
                <tr>
                    <th class="px-6 py-4">المنتج</th>
                    <th class="px-6 py-4">الحالة</th>
                    <th class="px-6 py-4">المخزون</th>
                    <th class="px-6 py-4">السعر</th>
                    <th class="px-6 py-4 text-center">الإجراءات</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-slate-700">
                {% for p in products %}
                <tr class="hover:bg-slate-800 transition-colors group">
                    <td class="px-6 py-4">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center overflow-hidden">
                                {% if p.images and p.images[0].fileUrl %}
                                    <img src="{{ p.images[0].fileUrl }}" class="w-full h-full object-cover">
                                {% else %}
                                    <span class="text-[8px] text-slate-500">N/A</span>
                                {% endif %}
                            </div>
                            <span class="font-bold text-slate-200">{{ p.title }}</span>
                        </div>
                    </td>
                    <td class="px-6 py-4">
                        <span class="px-2 py-1 rounded text-[10px] font-bold {% if p.status == 'active' %}bg-emerald-900 text-emerald-400{% else %}bg-slate-700 text-slate-400{% endif %}">
                            {{ p.status }}
                        </span>
                    </td>
                    <td class="px-6 py-4 text-slate-300">{{ p.quantity }}</td>
                    <td class="px-6 py-4 font-black text-amber-400">{{ p.price }} ر.س</td>
                    <td class="px-6 py-4 text-center">
                        <a href="{{ url_for('admin_Product.edit_product', product_id=p.id) }}" class="text-slate-400 hover:text-amber-400">تعديل</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</section>
{% endblock %}
