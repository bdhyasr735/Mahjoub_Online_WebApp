from flask import Blueprint, render_template, request, redirect, url_for, flash
from core.models import db, Supplier, Product

# تعريف البلوبرنت الخاص بلوحة الإدارة
admin_bp = Blueprint('admin', __name__, template_folder='templates')

@admin_bp.route('/')
def dashboard():
    """الصفحة الرئيسية للوحة الإدارة - عرض الإحصائيات"""
    suppliers_count = Supplier.query.count()
    products_count = Product.query.count()
    return f"<h1>لوحة إدارة محجوب أونلاين</h1><p>الموردين: {suppliers_count}</p><p>المنتجات: {products_count}</p>"

@admin_bp.route('/suppliers')
def list_suppliers():
    """عرض قائمة الموردين"""
    all_suppliers = Supplier.query.all()
    return "قائمة الموردين قيد التطوير - تم الاتصال بقاعدة البيانات بنجاح"

@admin_bp.route('/add_supplier', methods=['POST'])
def add_supplier():
    """إضافة مورد جديد يدوياً للاختبار"""
    name = request.form.get('name')
    phone = request.form.get('phone')
    
    if name and phone:
        new_supplier = Supplier(name=name, phone=phone, status='active')
        db.session.add(new_supplier)
        db.session.commit()
        return f"تم إضافة المورد {name} بنجاح في قاعدة بيانات Render!"
    
    return "خطأ في البيانات", 400

@admin_bp.route('/sync_qumra')
def sync_with_qumra():
    """هذا المسار سيتم ربطه لاحقاً بمجلد الـ webhooks لجلب المنتجات"""
    return "سيتم هنا تنفيذ عملية المزامنة مع قمرة باستخدام مفاتيح API الخاصة بك"
