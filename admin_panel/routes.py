from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from core.models import db, Supplier, Product
import requests
import os

# تعريف البلوبرنت الخاص بلوحة الإدارة
admin_bp = Blueprint('admin', __name__, template_folder='templates')

# --- 1. الصفحة الرئيسية (Dashboard) ---
@admin_bp.route('/')
def dashboard():
    """عرض إحصائيات سريعة من قاعدة بيانات Render"""
    try:
        suppliers_count = Supplier.query.count()
        products_count = Product.query.count()
        return f"""
        <div style="font-family: Arial; text-align: center; padding: 50px;">
            <h1 style="color: #6a0dad;">لوحة تحكم محجوب أونلاين 🚀</h1>
            <div style="display: flex; justify-content: center; gap: 20px;">
                <div style="border: 2px solid #6a0dad; padding: 20px; border-radius: 10px;">
                    <h3>الموردين</h3>
                    <p style="font-size: 24px;">{suppliers_count}</p>
                </div>
                <div style="border: 2px solid #6a0dad; padding: 20px; border-radius: 10px;">
                    <h3>المنتجات</h3>
                    <p style="font-size: 24px;">{products_count}</p>
                </div>
            </div>
            <br>
            <p style="color: green;">✅ النظام متصل بنجاح بقاعدة البيانات</p>
        </div>
        """
    except Exception as e:
        return f"<h1 style='color: red;'>خطأ في الاتصال بقاعدة البيانات:</h1><p>{str(e)}</p>"

# --- 2. إدارة الموردين ---
@admin_bp.route('/suppliers')
def list_suppliers():
    """جلب قائمة الموردين من قاعدة البيانات"""
    suppliers = Supplier.query.all()
    output = "<h1>قائمة الموردين</h1><ul>"
    for s in suppliers:
        output += f"<li>{s.name} - {s.phone} [{s.status}]</li>"
    output += "</ul><a href='/admin/'>العودة للرئيسية</a>"
    return output

# --- 3. إضافة مورد (للاختبار) ---
@admin_bp.route('/add_test_supplier')
def add_test():
    """رابط سريع لإضافة مورد وهمي للتأكد من أن الكتابة في Render تعمل"""
    try:
        test_supplier = Supplier(
            name="مورد تجريبي", 
            phone="000000000", 
            status="active"
        )
        db.session.add(test_supplier)
        db.session.commit()
        return "✅ تم إضافة مورد تجريبي بنجاح! اذهب لصفحة الموردين للتأكد."
    except Exception as e:
        return f"❌ فشل الإضافة: {str(e)}"

# --- 4. مزامنة قمرة (تجهيز مستقبلي) ---
@admin_bp.route('/sync_qumra')
def sync_qumra():
    """مسار مبدئي لاختبار الاتصال بـ API قمرة"""
    api_url = os.environ.get('QUMRA_API_URL')
    if not api_url:
        return "❌ خطأ: لم يتم ضبط رابط API قمرة في المتغيرات."
    return f"✅ جاهز للمزامنة مع: {api_url}"
