from flask import render_template
from . import vendors_bp

@vendors_bp.route('/vendor/dashboard')
def dashboard():
    # هنا ستعرض بيانات المورد الخاصة به
    return render_template('vendor/dashboard.html')
