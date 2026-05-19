@admin_wallet.route('/admin/wallet/overview', methods=['GET'])
@login_required
def overview():
    if current_user.role not in ['Owner', 'Admin']:
        flash('غير مسموح لك بامتلاك صلاحية دخول الفضاء المالي.', 'danger')
        return redirect(url_for('admin_dashboard.dashboard_home'))

    # استعلام آمن للإجماليات (استخدام try-except لتجنب الانهيار)
    totals = {'total_yer': 0, 'total_sar': 0, 'total_usd': 0}
    try:
        res = db.session.query(
            func.sum(Wallet.yer_balance),
            func.sum(Wallet.sar_balance),
            func.sum(Wallet.usd_balance)
        ).first()
        if res:
            totals = {'total_yer': res[0] or 0, 'total_sar': res[1] or 0, 'total_usd': res[2] or 0}
    except Exception as e:
        print(f"Error calculating totals: {e}")

    # جلب المحافظ بطريقة آمنة (دون JOIN قسري لتجنب خطأ 500)
    wallets = []
    try:
        # جلب المحافظ أولاً ثم ربط الموردين برمجياً إذا لزم الأمر لتجنب الـ SQL Error
        wallets = Wallet.query.all()
    except Exception as e:
        print(f"Error fetching wallets: {e}")
        flash('تعذر جلب بيانات الخزائن من قاعدة البيانات.', 'danger')

    return render_template('admin/overview.html', wallets=wallets, totals=totals)
