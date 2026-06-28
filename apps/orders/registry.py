# 📂 apps/orders/registry.py

from apps.orders.routes import orders_bp # نفترض وجود هذا المجلد للـ routes

def register_module(app):
    # تسجيل الـ routes الخاصة بالطلبات
    app.register_blueprint(orders_bp)
    
    # هنا يمكنك إضافة مهام "بدء التشغيل" للمزامنة إذا أردت
    # مثلاً: تشغيل مؤقت (Timer) للمزامنة التلقائية
    print("🚀 [Orders Module]: تم تفعيل نظام الطلبات وربطه بالمحفظة.")
