from flask import Blueprint, render_template

supplier_bp = Blueprint('supplier_app', __name__, template_folder='templates')

@supplier_bp.route('/suppliers')
def list_suppliers():
    return "قريباً: قائمة الموردين السياديين"
