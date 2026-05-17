# coding: utf-8
# 🔑 محرك العمليات المالية والتحكم بالمحافظ - منصة محجوب أونلاين 2026

from flask import render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from apps import db
from apps.models import Supplier
from apps.models.wallet_db import Wallet, WalletTransaction
from . import admin_wallet  # استيراد البلوبرينت الخاص بإدارة المحفظة
from sqlalchemy.orm import joinedload

@admin_wallet.route('/overview', methods=['GET'])
@login_required
def overview():
    """
    الواجهة السيادية الموحدة لإدارة وحوكمة المحافظ المالية للإدارة العليا.
    تقوم باحتساب الأرصدة الإجمالية في المنصة لكل عملة على حدة،
    وتمرير طلبات السحب المعلقة التي تنتظر التعميد الإداري.
    """
    try:
        # 1. احتساب المؤشرات المالية الكلية للمنصة (الريال اليمني)
        yer_totals = db.session.query(
            db.func.sum(Wallet.yer_total),
            db.func.sum(Wallet.yer_available),
            db.func.sum(Wallet.yer_pending)
        ).first()

        # 2. احتساب المؤشرات المالية الكلية للمنصة (الريال السعودي)
        sar_totals = db.session.query(
            db.func.sum(Wallet.sar_total),
            db.func.sum(Wallet.sar_available),
            db.func.sum(Wallet.sar_pending)
        ).first()

        # 3. احتساب المؤشرات المالية الكلية للمنصة (الدولار الأمريكي)
        usd_totals = db.session.query(
            db.func.sum(Wallet.usd_total),
            db.func.sum(Wallet.usd_available),
            db.func.sum(Wallet.usd_pending)
        ).first()

        # 4. جلب طلبات السحب المعلقة (Pending) مع بيانات المورد ورتبته لتسهيل الحوكمة
        pending_withdrawals = db.session.query(WalletTransaction)\
            .options(joinedload(WalletTransaction.wallet).joinedload(Wallet.supplier))\
            .filter(WalletTransaction.tx_type == 'withdrawal', WalletTransaction.tx_status == 'pending')\
            .order_by(WalletTransaction.created_at.desc())\
            .all()

        # 5. جلب آخر 50 عملية مالية مبرمة في النظام كأرشيف مراقبة لحظي
        recent_transactions = db.session.query(WalletTransaction)\
            .options(joinedload(WalletTransaction.wallet).joinedload(Wallet.supplier))\
            .order_by(WalletTransaction.created_at.desc())\
            .limit(50)\
            .all()

        # تجميع المؤشرات المالية في قاموس منظم
        platform_metrics = {
            "YER": {"total": yer_totals[0] or 0.0, "available": yer_totals[1] or 0.0, "pending": yer_totals[2] or 0.0},
            "SAR": {"total": sar_totals[0] or 0.0, "available": sar_totals[1] or 0.0, "pending": sar_totals[2] or 0.0},
            "USD": {"total": usd_totals[0] or 0.0, "available": usd_totals[1] or 0.0, "pending": usd_totals[2] or 0.0}
        }

        return render_template(
            'admin/overview.html',
            metrics=platform_metrics,
            pending_tx=pending_withdrawals,
            history_tx=recent_transactions,
            owner=current_user
        )

    except Exception as e:
        current_app.logger.error(f"❌ خطأ حوكمي أثناء تشغيل واجهة المحافظ: {str(e)}")
        return render_template('errors/500.html'), 500


@admin_wallet.route('/approve-withdrawal', methods=['POST'])
@login_required
def approve_withdrawal():
    """
    محرك التعميد المالي السيادي: الموافقة على طلب السحب وتحويل الأموال
    من الحساب (المتاح) وتأكيده تاريخياً في الحساب (المسحوب) بناءً على العملة المحددة للعملية.
    """
    tx_id = request.form.get('tx_id')
    if not tx_id:
        return jsonify({"status": "error", "message": "المعرف الفريد للعملية مفقود."}), 400

    try:
        # جلب العملية المالية مع قفل السطر لمنع تداخل العمليات المتزامنة (Race Condition)
        transaction = WalletTransaction.query.with_for_update().get(tx_id)
        
        if not transaction or transaction.tx_status != 'pending':
            return jsonify({"status": "error", "message": "العملية غير موجودة أو تم تعميدها مسبقاً."}), 400

        wallet = Wallet.query.with_for_update().get(transaction.wallet_id)
        currency = transaction.currency
        amount = transaction.amount

        # الخصم المالي الديناميكي حسب نوع عملة الحوالة المبرمة
        if currency == 'YER':
            if wallet.yer_available < amount:
                return jsonify({"status": "error", "message": "رصيد الريال اليمني المتاح غير كافٍ لإتمام الحوالة."}), 400
            wallet.yer_available -= amount
            wallet.yer_withdrawn += amount
            
        elif currency == 'SAR':
            if wallet.sar_available < amount:
                return jsonify({"status": "error", "message": "رصيد الريال السعودي المتاح غير كافٍ لإتمام الحوالة."}), 400
            wallet.sar_available -= amount
            wallet.sar_withdrawn += amount
            
        elif currency == 'USD':
            if wallet.usd_available < amount:
                return jsonify({"status": "error", "message": "رصيد الدولار المتاح غير كافٍ لإتمام الحوالة."}), 400
            wallet.usd_available -= amount
            wallet.usd_withdrawn += amount

        # تحديث حالة العملية وتوثيق المسؤول المعمد
        transaction.tx_status = 'completed'
        transaction.approved_by_id = current_user.id if hasattr(current_user, 'id') else None
        
        db.session.commit()
        
        return jsonify({
            "status": "success", 
            "message": f"تم تعميد صرف الحوالة بنجاح برقم مرجعي {transaction.transaction_ref}"
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ خطر مالي أثناء تعميد السحب: {str(e)}")
        return jsonify({"status": "error", "message": f"فشل التعميد المالي: {str(e)}"}), 500


@admin_wallet.route('/reject-withdrawal', methods=['POST'])
@login_required
def reject_withdrawal():
    """
    رفض طلب السحب سيادياً: إعادة الأموال المحتجزة إلى رصيد المورد المتاح دون خصمها.
    """
    tx_id = request.form.get('tx_id')
    reason = request.form.get('reason', 'تم الرفض من قبل الإدارة العليا').strip()

    try:
        transaction = WalletTransaction.query.with_for_update().get(tx_id)
        if not transaction or transaction.tx_status != 'pending':
            return jsonify({"status": "error", "message": "العملية غير صالحة لإجراء الرفض."}), 400

        transaction.tx_status = 'rejected'
        transaction.description = f"{transaction.description} | سبب الرفض: {reason}"
        transaction.approved_by_id = current_user.id if hasattr(current_user, 'id') else None
        
        db.session.commit()
        return jsonify({"status": "success", "message": "تم رفض طلب السحب وإرجاع الصلاحية للمحفظة الجارية."}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ خطأ أثناء إسقاط العملية المالية: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
