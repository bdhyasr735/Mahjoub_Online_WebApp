from flask import Blueprint, render_template, request, jsonify

admin_suppliers = Blueprint('admin_suppliers', __name__, template_folder='templates')

@admin_suppliers.route('/add', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'GET':
        return render_template('admin/add_supplier.html', next_id=96310)
    
    # منطق الحفظ هنا لاحقاً
    return jsonify({"status": "success"})
