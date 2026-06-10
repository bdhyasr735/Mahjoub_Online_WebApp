from flask import Blueprint, render_template, request, jsonify
from apps import db
from apps.models.wallet import Wallet
from apps.models.supplier import Supplier
from sqlalchemy import or_

# تعريف الـ Blueprint
wallet_app = Blueprint('wallet_app', __name__, template_folder='templates')

# 1. لوحة التحكم الرئيسية للمحافظ
@wallet_app.route('/wallet', methods=['GET'])
def dashboard():
    search = request.args.get('search', '')
    query = Wallet.query.join(Supplier)
    
    if search:
        query = query.filter(or_(
            Supplier.trade_name.contains(search),
            Supplier.phone.contains(search),
            Wallet.id.contains(search)
        ))
    
    wallets = query.all()
    return render_template('admin/wallet_app.html', wallets=wallets)

# 2. البحث الذكي (Select2)
@wallet_app.route('/wallet/search_suppliers')
def search_suppliers():
    term = request.args.get('term', '')
    suppliers = Supplier.query.filter(
        or_(Supplier.trade_name.contains(term), Supplier.phone.contains(term))
    ).limit(10).all()
    
    results = [{'id': s.id, 'text': f"{s.trade_name} - {s.phone}"} for s in suppliers]
    return jsonify({'results': results})

# 3. جلب قائمة الموردين (للجدول داخل صفحة view_wallet)
@wallet_app.route('/wallet/get_suppliers_list')
def get_suppliers_list():
    page = request.args.get('page', 1, type=int)
    suppliers = Supplier.query.paginate(page=page, per_page=10)
    return render_template('admin/partials/suppliers_table.html', suppliers=suppliers)

# 4. عرض كشف حساب المورد (عبر AJAX)
@wallet_app.route('/wallet/view/<int:supplier_id>')
def view_wallet(supplier_id):
    wallet = Wallet.query.filter_by(supplier_id=supplier_id).first_or_404()
    # هنا يتم جلب العمليات المرتبطة بهذه المحفظة
    # transactions = wallet.transactions.all() 
    return render_template('admin/partials/wallet_details.html', wallet=wallet)

# 5. عرض تفاصيل المحفظة للمشرف (الرابط الثابت)
@wallet_app.route('/wallet/manage/<int:supplier_id>')
def manage_wallet(supplier_id):
    wallet = Wallet.query.filter_by(supplier_id=supplier_id).first_or_404()
    return render_template('admin/view_wallet.html', wallet=wallet)
