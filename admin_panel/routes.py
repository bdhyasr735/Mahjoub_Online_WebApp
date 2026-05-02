@admin_bp.route('/') 
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    # 🛡️ الخطوة 1: تنظيف أي خطأ سابق فوراً للسماح للصفحة بالتحميل
    db.session.rollback()
    
    # تعريف قيم افتراضية لضمان ظهور الصفحة حتى لو فشلت القاعدة
    suppliers_count = 0
    pending_withdrawals = 0
    orders_count = 0
    total_balance = "0.00"

    try:
        # الخطوة 2: محاولة جلب البيانات بحذر
        suppliers_count = Vendor.query.count()
        if WithdrawRequest:
            pending_withdrawals = WithdrawRequest.query.filter_by(status='pending').count()
        
        # إذا نجحت الأوامر أعلاه، سيتم عرض الأرقام الحقيقية
        return render_template('dashboard.html', 
                               suppliers_count=suppliers_count, 
                               pending_withdrawals=pending_withdrawals,
                               orders_count=orders_count,
                               total_balance=total_balance,
                               show_repair=SHOW_REPAIR_LINK)
                               
    except Exception as e:
        # الخطوة 3: في حال فشل أي أمر (بسبب العمود المفقود)، نعرض الصفحة بالأصفار مع زر الإصلاح
        db.session.rollback() 
        print(f"Database pending repair: {str(e)}")
        return render_template('dashboard.html', 
                               suppliers_count=0, 
                               pending_withdrawals=0,
                               orders_count=0,
                               total_balance="0.00",
                               show_repair=True) # نجبر الرابط على الظهور هنا
