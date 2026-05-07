# admin_panel/manage_suppliers.py
from flask import render_template, request, jsonify
from sqlalchemy import or_, cast, String
from core.models.supplier import Supplier
from core.extensions import db
from . import admin_bp

# قائمة الجغرافيا المركزية (Sovereign Geography Registry)
YEMEN_GEOGRAPHY = {
    "الحديدة": ["الخوخة", "حيس", "الحوك", "الميناء", "زبيد", "بيت الفقيه"],
    "أمانة العاصمة": ["السبعين", "التحرير", "الثورة", "صنعاء القديمة"],
    "عدن": ["المنصورة", "كريتر", "الشيخ عثمان", "البريقة"],
    "تعز": ["المخاء", "القاهرة", "المظفر"]
}

# --- 1. عرض الواجهة الرئيسية للإدارة ---
@admin_bp.route('/manage-suppliers')
def manage_suppliers():
    """عرض صفحة الترسانة مع تحميل أولي للموردين"""
    # جلب آخر 20 مورد لضمان سرعة التحميل الأولية
    initial_suppliers = Supplier.query.order_by(Supplier.id.desc()).limit(20).all()
    
    return render_template(
        'manage_suppliers.html', 
        suppliers=initial_suppliers,
        provinces_list=YEMEN_GEOGRAPHY.keys()
    )

# --- 2. محرك البحث الذكي (The Sovereign Search Engine) ---
@admin_bp.route('/api/search-suppliers')
def api_search_suppliers():
    """منطق البحث المتقدم بالفلاتر (AJAX)"""
    q = request.args.get('q', '').strip()
    province = request.args.get('province', '').strip()
    district = request.args.get('district', '').strip()
    tier = request.args.get('tier', '').strip()

    query_obj = Supplier.query

    # البحث النصي الشامل (اسم، هاتف، معرف، محفظة)
    if q:
        clean_q = q.replace('SUP-MAH-', '').replace('WAL-MAH-', '')
        query_obj = query_obj.filter(
            or_(
                Supplier.trade_name.ilike(f"%{q}%"),
                Supplier.phone.ilike(f"%{q}%"),
                Supplier.e_wallet.ilike(f"%{q}%"),
                cast(Supplier.id, String).ilike(f"%{clean_q}%")
            )
        )

    # فلاتر الموقع والرتبة
    if province:
        query_obj = query_obj.filter_by(province=province)
    if district:
        query_obj = query_obj.filter_by(district=district)
    if tier:
        query_obj = query_obj.filter_by(tier=tier)

    suppliers = query_obj.order_by(Supplier.id.desc()).all()
    
    return jsonify({
        "status": "success",
        "count": len(suppliers),
        "suppliers": [s.to_dict() for s in suppliers]
    })

# --- 3. بوابة تحديث الحالة (تفعيل/إيقاف) ---
@admin_bp.route('/api/toggle-supplier-status/<int:s_id>', methods=['POST'])
def toggle_status(s_id):
    """تغيير حالة المورد بين (active) و (suspended)"""
    supplier = Supplier.query.get_or_404(s_id)
    data = request.get_json()
    new_status = data.get('status')

    if new_status in ['active', 'suspended']:
        supplier.status = new_status
        db.session.commit()
        return jsonify({
            "status": "success", 
            "message": f"تم تحديث حالة {supplier.trade_name} بنجاح"
        })
    
    return jsonify({"status": "error", "message": "حالة غير صالحة"}), 400

# --- 4. جلب المديريات ديناميكياً ---
@admin_bp.route('/api/get-districts')
def get_districts():
    province = request.args.get('province')
    districts = YEMEN_GEOGRAPHY.get(province, [])
    return jsonify(districts)
