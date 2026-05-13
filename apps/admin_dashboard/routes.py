from flask import render_template, request, redirect, url_for, flash
from . import admin_dashboard  # استيراد البلوبرينت من ملف __init__.py

# 1. المسار الرئيسي لمركز المراقبة (Dashboard)
@admin_dashboard.route('/')
@admin_dashboard.route('/dashboard')
def dashboard():
    """
    هذه الدالة تعرض لوحة التحكم الرئيسية (الهيكل + المحتوى).
    تأكد من وجود ملف dashboard.html داخل مجلد templates/admin/
    """
    return render_template('admin/dashboard.html')

# 2. مسار عرض سجل الموردين (الحل لخطأ الصورة image_2d0413.png)
@admin_dashboard.route('/suppliers/list')
def list_suppliers():
    """
    هذا المسار هو الذي طلبه نظام القوالب وتسبب في BuildError لأنه كان مفقوداً.
    سيتم ربطه لاحقاً بقاعدة البيانات لجلب قائمة الموردين.
    """
    # مؤقتاً نعرض صفحة فارغة أو نفس صفحة الموردين
    return render_template('admin/list_suppliers.html')

# 3. مسار إحصائيات سريعة (مثال إضافي لدعم الواجهة الديناميكية)
@admin_dashboard.route('/api/stats')
def get_stats():
    """
    دالة اختيارية يمكن استخدامها لتحديث الأرقام في الديشبورد بدون إعادة تحميل الصفحة.
    """
    stats = {
        "suppliers_count": 12,
        "active_orders": 5,
        "system_status": "يعمل بكفاءة"
    }
    return stats

# يمكنك إضافة المزيد من المسارات الإدارية هنا...
