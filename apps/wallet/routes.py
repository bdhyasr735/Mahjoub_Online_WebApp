# 📂 apps/wallet/routes.py
from flask import Blueprint, render_template, request, abort
from flask_login import login_required
from apps.models.wallet_db import SupplierWallet
from apps.models.wallet_db import WalletTransaction # قمت بإضافته تحسباً لاستخدامه لاحقاً
from apps.models.supplier_db import Supplier

# 🛡️ التصحيح: إزالة template_folder ليعتمد Flask على المجلد العام للقوالب (apps/templates)
# هذا يمنع تعارض مسارات القوالب ويحل خطأ TemplateNotFound
wallet_app = Blueprint('wallet_app', __name__)

@wallet_app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    # 1. استقبال نص البحث
    search_query = request.args.get('search', '')
    
    # 2. جلب البيانات باستخدام join
    # نستخدم join مع Supplier للوصول لبيانات المورد
    query = SupplierWallet.query.join(Supplier, SupplierWallet.supplier_id == Supplier.id)
    
    # 3. تطبيق فلتر البحث باستخدام ilike (غير حساس لحالة الأحرف)
    if search_query:
        search_filter = f"%{search_query}%"
        query = query.filter(
            Supplier.trade_name.ilike(search_filter) | 
            Supplier.owner_name.ilike(search_filter) |
            Supplier.owner_phone.ilike(search_filter)
        )
    
    # 4. تنفيذ الاستعلام
    wallets = query.all()
    
    # 5. إرسال البيانات للقالب
    # سيبحث Flask في: apps/templates/admin/wallet_app.html
    return render_template('admin/wallet_app.html', wallets=wallets)

@wallet_app.route('/view/<int:supplier_id>')
@login_required
def view_wallet(supplier_id):
    # جلب المحفظة مع التأكد من وجودها
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first_or_404()
    
    # سيبحث Flask في: apps/templates/admin/view_wallet.html
    return render_template('admin/view_wallet.html', wallet=wallet)
