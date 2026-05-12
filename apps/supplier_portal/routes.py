from flask import Blueprint

supplier_bp = Blueprint('supplier_portal', __name__, template_folder='templates')

@supplier_bp.route('/supplier/dashboard')
def supplier_home():
    return "<h1 style='color:#3D0066; text-align:center;'>📦 بوابة الموردين - إدارة المنتجات</h1>"
