# coding: utf-8
# 💳 محرك الحوكمة المالية والمسارات السيادية للمحافظ - منصة محجوب أونلاين 2026

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from apps import db
from apps.models.wallet_db import Wallet, WalletTransaction
from apps.models.supplier_db import Supplier

# إنشاء البلوبرينت الخاص بإدارة الحسابات المادية
admin_wallet = Blueprint('admin_wallet', __name__, template_folder='templates')

@admin_wallet.route('/admin/wallet/overview', methods=['GET'])
@login_required
def wallet_overview():
    """
    شاشة فحص وجرد الحسابات المادية:
    تستقبل طلبات التفتيش الفوري بناءً على اسم المتجر أو المعرف السيادي أو كود المحفظة.
    """
    # التأكد من الصلاحيات السيادية للمستخدم (Owner أو Admin)
    if current_user.role not in ['Owner', 'Admin']:
        flash('غير مسموح لك بامتلاك صلاحية دخول الفضاء المالي.', 'danger')
        return redirect(url_for('admin_dashboard.dashboard'))

    search_query = request.args.get('search', '').strip()
    
    # بناء استعلام جلب المحافظ الأساسي مع ربط جدول الموردين لضمان استقرار السيرفر
    query = Wallet.query.join(Supplier, Wallet.supplier_id == Supplier.id)

    # تطبيق التفتيش الذكي إذا وجد نص بحث ولم يكن الرمز العام (#) لجلد السيرفر كاملاً
    if search_query and search_query != '#':
        query = query.filter(
            (Supplier.trade_name.like(f'%{search_query}%')) |
            (Supplier.sovereign_id.like(f'%{search_query}%')) |
            (Wallet.wallet_code.like(f'%{search_query}%'))
        )

    # جلب جميع المحافظ الحية المتوافقة
    wallets = query.all()

    return render_template('admin/overview.html', wallets=wallets)


@admin_wallet.route('/api/wallet/<string:wallet_code>/balance', methods=['GET'])
@login_required
def get_wallet_balance_api(wallet_code):
    """
    واجهة برمجة تطبيقات (API) آمنة لجلب كشف الحساب المالي الفوري للمحفظة بجيسون نقي للواجهات الفرعية.
    """
    if current_user.role not in ['Owner', 'Admin']:
        return jsonify({"status": "error", "message": "صلاحية سيادية مرفوضة"}), 403

    wallet = Wallet.query.filter_by(wallet_code=wallet_code).first()
    
    if not wallet:
        return jsonify({"status": "error", "message": "المحفظة المالية غير موجودة بالنظام"}), 404

    # تصدير البيانات بالقاموس المحدث المستقر لضمان القراءة الصافية بالواجهات
    return jsonify({
        "status": "success",
        "data": wallet.to_dict()
    })


@admin_wallet.route('/admin/wallet/adjust', methods=['POST'])
@login_required
def adjust_balance():
    """
    مسار إدارة المخازن المالية (إيداع، سحب، تعديل أرصدة) من قبل الإدارة العليا.
    """
    if current_user.role != 'Owner':
        flash('هذا الإجراء يتطلب سلطة المالك السيادية المطلقة.', 'danger')
        return redirect(url_for('admin_wallet.wallet_overview'))

    wallet_id = request.form.get('wallet_id')
    currency = request.form.get('currency')  # 'YER', 'SAR', 'USD'
    action_type = request.form.get('action_type')  # 'deposit', 'withdrawal'
    amount_str = request.form.get('amount', '0')

    try:
        amount = float(amount_str)
        if amount <= 0:
            flash('يجب أن تكون القيمة المالية أكبر من صفر.', 'warning')
            return redirect(url_for('admin_wallet.wallet_overview'))
            
        wallet = Wallet.query.get(wallet_id)
        if not wallet:
            flash('المحفظة المستهدفة غير مسجلة في الفضاء الحالي.', 'danger')
            return redirect(url_for('admin_wallet.wallet_overview'))

        # المعالجة الذكية حسب خزنة العملة المحددة وتحديث الحقول المستقرة بالكامل
        if currency == 'YER':
            if action_type == 'deposit':
                wallet.yer_balance = float(wallet.yer_balance) + amount
            elif action_type == 'withdrawal':
                if wallet.yer_available < amount:
                    flash('رصيد الريال اليمني المتاح لا يكفي لإتمام هذه الحركة.', 'danger')
                    return redirect(url_for('admin_wallet.wallet_overview'))
                wallet.yer_balance = float(wallet.yer_balance) - amount

        elif currency == 'SAR':
            if action_type == 'deposit':
                wallet.sar_balance = float(wallet.sar_balance) + amount
            elif action_type == 'withdrawal':
                if wallet.sar_available < amount:
                    flash('رصيد الريال السعودي المتاح لا يكفي لإتمام هذه الحركة.', 'danger')
                    return redirect(url_for('admin_wallet.wallet_overview'))
                wallet.sar_balance = float(wallet.sar_balance) - amount

        elif currency == 'USD':
            if action_type == 'deposit':
                wallet.usd_balance = float(wallet.usd_balance) + amount
            elif action_type == 'withdrawal':
                if wallet.usd_available < amount:
                    flash('رصيد الدولار الأمريكي المتاح لا يكفي لإتمام هذه الحركة.', 'danger')
                    return redirect(url_for('admin_wallet.wallet_overview'))
                wallet.usd_balance = float(wallet.usd_balance) - amount
        
        # تدوين سجل المعاملة الحركية لتوثيق الحوكمة والتدقيق المالي مستقبلاً
        tx_log = WalletTransaction(
            wallet_id=wallet.id,
            transaction_type=action_type,
            currency=currency,
            amount=amount,
            description=f"تعديل إداري مباشر من لوحة تحكم المالك السيادي"
        )
        
        db.session.add(tx_log)
        db.session.commit()
        
        flash(f'تمت معالجة القيمة المادية بنجاح؛ وتحديث كشف {currency} للمحفظة {wallet.wallet_code}.', 'success')

    except ValueError:
        flash('خطأ حوكمي: صيغة المبلغ المدخل غير صالحة برمجياً.', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'تعذر إتمام الموازنة المالية بسبب عطل داخلي: {e}', 'danger')

    return redirect(url_for('admin_wallet.wallet_overview'))
