# coding: utf-8
# 🔑 محرك العمليات المالية والتحكم بالمحافظ - منصة محجوب أونلاين 2026

from flask import render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from apps import db
from apps.models.wallet_db import Wallet, WalletTransaction
from apps.models.supplier_db import Supplier  # استدعاء موديل المورد
from . import admin_wallet  
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import func
from sqlalchemy import or_

@admin_wallet.route('/overview', methods=['GET'])
@login_required
def overview():
    """
    الواجهة السيادية الموحدة لإدارة وحوكمة المحافظ المالية للإدارة العليا.
    مؤمنة بالكامل ضد حقول التداخل البرمجي القاتلة N+1.
    """
    try:
        # 1. احتساب المؤشرات المالية الكلية للمنصة (الريال اليمني)
        yer_totals = db.session.query(
            func.coalesce(func.sum(Wallet.yer_total), 0.0),
            func.coalesce(func.sum(Wallet.yer_available), 0.0),
            func.coalesce(func.sum(Wallet.yer_pending), 0.0)
        ).first()

        # 2. احتساب المؤشرات المالية الكلية للمنصة (الريال السعودي)
        sar_totals = db.session.query(
            func.coalesce(func.sum(Wallet.sar_total), 0.0),
            func.coalesce(func.sum(Wallet.sar_available), 0.0),
            func.coalesce(func.sum(Wallet.sar_pending), 0.0)
        ).first()

        # 3. احتساب المؤشرات المالية الكلية للمنصة (الدولار الأمريكي)
        usd_totals = db.session.query(
            func.coalesce(func.sum(Wallet.usd_total), 0.0),
            func.coalesce(func.sum(Wallet.usd_available), 0.0),
            func.coalesce(func.sum(Wallet.usd_pending), 0.0)
        ).first()

        # 4. جلب طلبات السحب المعلقة
        pending_withdrawals = db.session.query(WalletTransaction)\
            .options(joinedload(WalletTransaction.wallet))\
            .filter(WalletTransaction.tx_type == 'withdrawal', WalletTransaction.tx_status == 'pending')\
            .order_by(WalletTransaction.created_at.desc())\
            .all()

        platform_metrics = {
            "YER": {"total": yer_totals[0] or 0.0, "available": yer_totals[1] or 0.0, "pending": yer_totals[2] or 0.0},
            "SAR": {"total": sar_totals[0] or 0.0, "available": sar_totals[1] or 0.0, "pending": sar_totals[2] or 0.0},
            "USD": {"total": usd_totals[0] or 0.0, "available": usd_totals[1] or 0.0, "pending": usd_totals[2] or 0.0}
        }

        return render_template(
            'admin/overview.html',
            metrics=platform_metrics,
            pending_tx=pending_withdrawals,
            owner=current_user
        )

    except Exception as e:
        current_app.logger.error(f"❌ خطأ حوكمي أثناء تشغيل واجهة المحافظ: {str(e)}")
        return f"<h3>خطأ مالي في السيرفر الداخلي للعملات:</h3> <p>{str(e)}</p>", 500


@admin_wallet.route('/api/search', methods=['GET'])
@login_required
def search_wallets():
    """
    نظام استدعاء وفحص المحافظ الموحد:
    يسحب الحقول ديناميكياً من قاعدة البيانات بناءً على الموردين ومحافظهم المرتبطة.
    دعم مرن لأسماء الحقول المختلفة (username/name/phone/mobile) لمنع مخرجات البحث الفارغة.
    """
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({'status': 'success', 'wallets': []})

    try:
        # فحص ديناميكي للحقول المتوفرة في موديل Supplier لتفادي اختلاط أسماء الأعمدة
        supplier_columns = Supplier.__table__.columns.keys()
        
        filters = []
        # التحقق من حقل الاسم
        if 'username' in supplier_columns:
            filters.append(Supplier.username.ilike(f'%{query}%'))
        elif 'name' in supplier_columns:
            filters.append(Supplier.name.ilike(f'%{query}%'))
        elif 'store_name' in supplier_columns:
            filters.append(Supplier.store_name.ilike(f'%{query}%'))

        # التحقق من حقل الهاتف
        if 'phone' in supplier_columns:
            filters.append(Supplier.phone.ilike(f'%{query}%'))
        elif 'mobile' in supplier_columns:
            filters.append(Supplier.mobile.ilike(f'%{query}%'))

        # إذا لم نجد حقول مطابقة نعود بمصفوفة فارغة آمنة
        if not filters:
            return jsonify({'status': 'success', 'wallets': []})

        # تنفيذ الاستعلام الموحد
        suppliers = db.session.query(Supplier).filter(or_(*filters)).all()

        wallets_list = []
        for sup in suppliers:
            # سحب المحفظة المرتبطة بالمورد مباشرة من قاعدة البيانات
            wallet = db.session.query(Wallet).filter(Wallet.supplier_id == sup.id).first()
            
            # تحديد اسم العرض التجاري المتاح ديناميكياً
            trade_name = getattr(sup, 'username', getattr(sup, 'name', getattr(sup, 'store_name', 'مورد غير مسمى')))
            owner_phone = getattr(sup, 'phone', getattr(sup, 'mobile', 'بدون هاتف'))

            wallets_list.append({
                'wallet_id': wallet.id if wallet else f"⏳ غير منشأة (ID: {sup.id})",
                'trade_name': trade_name,  
                'sovereign_id': f"SUP-ID-{sup.id:04d}",
                'owner_phone': owner_phone,
                
                # أرصدة الريال اليمني
                'yer_total': float(wallet.yer_total) if wallet else 0.0,
                'yer_available': float(wallet.yer_available) if wallet else 0.0,
                'yer_pending': float(wallet.yer_pending) if wallet else 0.0,
                
                # أرصدة الريال السعودي
                'sar_total': float(wallet.sar_total) if wallet else 0.0,
                'sar_available': float(wallet.sar_available) if wallet else 0.0,
                'sar_pending': float(wallet.sar_pending) if wallet else 0.0,
                
                # أرصدة الدولار الأمريكي
                'usd_total': float(wallet.usd_total) if wallet else 0.0,
                'usd_available': float(wallet.usd_available) if wallet else 0.0,
                'usd_pending': float(wallet.usd_pending) if wallet else 0.0,
            })

        return jsonify({'status': 'success', 'wallets': wallets_list})

    except Exception as e:
        current_app.logger.error(f"❌ خطأ أثناء استدعاء وسحب بيانات المحافظ: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@admin_wallet.route('/approve-withdrawal', methods=['POST'])
@login_required
def approve_withdrawal():
    """
    محرك التعميد المالي: الموافقة على طلب السحب وتحديث قاعدة البيانات.
    """
    tx_id = request.form.get('tx_id')
    if not tx_id:
        return jsonify({"status": "error", "message": "المعرف الفريد للعملية مفقود."}), 400

    try:
        transaction = WalletTransaction.query.with_for_update().get(tx_id)
        if not transaction or transaction.tx_status != 'pending':
            return jsonify({"status": "error", "message": "العملية غير موجودة أو معمدة مسبقاً."}), 400

        wallet = Wallet.query.with_for_update().get(transaction.wallet_id)
        currency = transaction.currency
        amount = transaction.amount

        if currency == 'YER':
            if wallet.yer_pending < amount:
                return jsonify({"status": "error", "message": "رصيد الريال اليمني المعلق غير كافٍ."}), 400
            wallet.yer_pending -= amount
            wallet.yer_total -= amount
            wallet.yer_withdrawn += amount
        elif currency == 'SAR':
            if wallet.sar_pending < amount:
                return jsonify({"status": "error", "message": "رصيد الريال السعودي المعلق غير كافٍ."}), 400
            wallet.sar_pending -= amount
            wallet.sar_total -= amount
            wallet.sar_withdrawn += amount
        elif currency == 'USD':
            if wallet.usd_pending < amount:
                return jsonify({"status": "error", "message": "رصيد الدولار المعلق غير كافٍ."}), 400
            wallet.usd_pending -= amount
            wallet.usd_total -= amount
            wallet.usd_withdrawn += amount

        transaction.tx_status = 'completed'
        transaction.approved_by_id = current_user.id if hasattr(current_user, 'id') else None
        
        db.session.commit()
        return jsonify({"status": "success", "message": f"تم تعميد الحوالة بنجاح برقم مرجع: {transaction.transaction_ref}"}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ خطأ مالي أثناء تعميد السحب: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@admin_wallet.route('/reject-withdrawal', methods=['POST'])
@login_required
def reject_withdrawal():
    """
    رفض طلب السحب وإعادة المبالغ المحتجزة للرصيد المتاح.
    """
    tx_id = request.form.get('tx_id')
    reason = request.form.get('reason', 'تم الرفض من قبل الإدارة العليا').strip()

    if not tx_id:
        return jsonify({"status": "error", "message": "المعرف الفريد للعملية مفقود."}), 400

    try:
        transaction = WalletTransaction.query.with_for_update().get(tx_id)
        if not transaction or transaction.tx_status != 'pending':
            return jsonify({"status": "error", "message": "العملية غير صالحة لإجراء الرفض."}), 400

        wallet = Wallet.query.with_for_update().get(transaction.wallet_id)
        currency = transaction.currency
        amount = transaction.amount

        if currency == 'YER':
            wallet.yer_pending -= amount
            wallet.yer_available += amount
        elif currency == 'SAR':
            wallet.sar_pending -= amount
            wallet.sar_available += amount
        elif currency == 'USD':
            wallet.usd_pending -= amount
            wallet.usd_available += amount

        transaction.tx_status = 'rejected'
        transaction.description = f"{transaction.description} | سبب الرفض: {reason}"
        transaction.approved_by_id = current_user.id if hasattr(current_user, 'id') else None
        
        db.session.commit()
        return jsonify({"status": "success", "message": "تم رفض طلب السحب وإعادة المبالغ بنجاح."}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ خطأ أثناء إسقاط العملية المالية: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
