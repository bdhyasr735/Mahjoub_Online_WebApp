# 📂 apps/wallet/routes.py
from flask import Blueprint, render_template, request
from flask_login import login_required
from apps.models.wallet_db import SupplierWallet
from apps.models.supplier_db import Supplier

# تعريف الـ Blueprint (تأكد أن الاسم يطابق المسجل في __init__.py)
wallet_app = Blueprint('wallet_app', __name__)

@wallet_app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    # 1. استقبال نص البحث من القالب
    search_query = request.args.get('search', '')
    
    # 2. جلب البيانات من قاعدة البيانات (استخدام outerjoin لضمان عدم ضياع المحافظ)
    query = SupplierWallet.query.outerjoin(Supplier)
    
    # 3. تطبيق فلتر البحث إذا وُجد
    if search_query:
        query = query.filter(
            (Supplier.trade_name.contains(search_query)) | 
            (Supplier.owner_name.contains(search_query)) |
            (Supplier.owner_phone.contains(search_query))
        )
    
    # 4. تنفيذ الاستعلام
    wallets = query.all()
    
    # 5. إرسال البيانات للمحرك (القالب)
    return render_template('admin/wallet_app.html', wallets=wallets)

@wallet_app.route('/view/<int:supplier_id>')
@login_required
def view_wallet(supplier_id):
    # جلب المحفظة المحددة
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first_or_404()
    return render_template('admin/view_wallet.html', wallet=wallet)
