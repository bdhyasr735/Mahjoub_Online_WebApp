# coding: utf-8
from flask import Blueprint, render_template, jsonify, abort
from flask_login import login_required
from apps.extensions import db

# 1. تعريف البلوبرنت بنفس الاسم الذي يتوقعه Registry
admin_permissions_bp = Blueprint(
    'admin_permissions_bp', 
    __name__, 
    template_folder='templates'
)

# 2. المسار الذي يربط بـ LINKS في ملف الـ registry
@admin_permissions_bp.route('/roles', methods=['GET'])
@login_required
def roles_list():
    """عرض قائمة الموظفين والصلاحيات"""
    # استبدل هذا بمنطق استخراج البيانات الخاص بك
    return render_template('admin/permissions.html')

# 3. المسار الذي تستخدمه في الـ AJAX داخل ملف HTML
@admin_permissions_bp.route('/reset-password/<int:staff_id>/<string:staff_type>', methods=['GET'])
@login_required
def reset_password(staff_id, staff_type):
    try:
        # هنا تضع منطق إعادة تعيين كلمة المرور
        # مثال افتراضي للبيانات التي يتوقعها الـ AJAX:
        return jsonify({
            "success": True, 
            "username": "موظف_اختبار", 
            "new_password": "password123",
            "store_name": "متجر_محجوب",
            "store_code": "MH-001"
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
