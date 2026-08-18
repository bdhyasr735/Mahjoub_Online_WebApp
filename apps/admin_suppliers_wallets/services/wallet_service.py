# coding: utf-8
# 📂 apps/admin_suppliers_wallets/services/wallet_service.py

"""
طبقة الخدمات المحاسبية وإدارة العمليات المصرفية لمحافظ الموردين
Mahjoub Online WebApp - Treasury & Supplier Wallets Service Layer
"""
import uuid
import random
from datetime import datetime
from decimal import Decimal

# =====================================================================
# ✅ استيراد الموديلات الحقيقية من قاعدة البيانات
# =====================================================================
from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.models.supplier_db import Supplier
from sqlalchemy import or_


def calculate_wallets_kpis():
    """
    حساب المؤشرات المالية المركزية للوحة التحكم (بيانات حقيقية)
    """
    from sqlalchemy import func
    
    total_sar_balance = db.session.query(func.sum(SupplierWallet.balance_sar)).scalar() or 0.00
    total_pending_balance = db.session.query(func.sum(SupplierWallet.balance_pending)).scalar() or 0.00
    pending_withdrawals_amount = db.session.query(func.sum(WalletTransaction.amount)).filter_by(status='pending').scalar() or 0.00
    
    return {
        'total_wallets_balance': float(total_sar_balance) + float(total_pending_balance),
        'total_available_payouts': float(total_sar_balance),
        'total_escrow_held': float(total_pending_balance),
        'total_suppliers_count': SupplierWallet.query.count(),
        'active_suppliers_count': SupplierWallet.query.filter_by(status='active').count(),
        'pending_withdrawals_amount': float(pending_withdrawals_amount),
        'pending_withdrawals_count': WalletTransaction.query.filter_by(status='pending', trans_type='withdrawal').count(),
        'currency': 'SAR'
    }


def get_suppliers_list(search='', status='all', bank='all', page=1, per_page=10):
    """
    استرجاع قائمة محافظ الموردين الحقيقية من قاعدة البيانات
    """
    query = SupplierWallet.query.join(Supplier, Supplier.id == SupplierWallet.supplier_id)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                SupplierWallet.wallet_code.ilike(search_term),
                Supplier.supplier_code.ilike(search_term),
                Supplier.store_name.ilike(search_term),
                Supplier.trade_name.ilike(search_term),
                Supplier.owner_name.ilike(search_term),
                Supplier.username.ilike(search_term)
            )
        )

    if status and status != 'all':
        query = query.filter(SupplierWallet.status == status)

    if bank and bank != 'all':
        query = query.filter(Supplier.bank_name.ilike(f"%{bank}%"))

    query = query.order_by(SupplierWallet.id.desc())
    pagination_obj = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        'items': pagination_obj.items,
        'total_count': pagination_obj.total
    }


def get_supplier_wallet_by_id(supplier_id):
    """
    استرجاع بيانات المحفظة الحقيقية وكشف الحساب
    """
    return SupplierWallet.query.get_or_404(supplier_id)


def toggle_freeze_service(supplier_id, reason='إجراء إداري'):
    """
    تجميد أو فك حظر المحفظة مع التوثيق
    """
    wallet = SupplierWallet.query.get_or_404(supplier_id)
    wallet.status = 'frozen' if wallet.status == 'active' else 'active'
    wallet.updated_at = datetime.utcnow()
    db.session.commit()
    return {
        'status': 'success',
        'message': f'تم تغيير حالة المحفظة بنجاح'
    }


def create_manual_adjustment(supplier_id, amount, entry_type, description):
    """
    إنشاء قيد تسوية مالي يدوي وتوليد سند رسمي
    """
    wallet = SupplierWallet.query.get_or_404(supplier_id)
    current_balance = Decimal(str(wallet.balance_sar))
    new_balance = current_balance + amount if entry_type == 'credit' else current_balance - amount

    transaction = WalletTransaction(
        wallet_id=wallet.id,
        trans_type='deposit' if entry_type == 'credit' else 'withdraw',
        status='completed',
        amount=amount,
        currency='SAR',
        balance_before=current_balance,
        balance_after=new_balance,
        description=description
    )
    db.session.add(transaction)
    wallet.balance_sar = new_balance
    db.session.commit()

    return {
        'status': 'success',
        'voucher_code': f"VCH-{random.randint(100000, 999999)}",
        'ref_code': f"REF-{datetime.utcnow().strftime('%H%M')}",
        'message': 'تم قيد السند المحاسبي بنجاح'
    }


# ====================================================================
# ✅ الدوال الجديدة المطلوبة لصفحة طلبات السحب (النسخة الحقيقية)
# ====================================================================

def get_withdraw_requests(status='pending', search='', page=1, per_page=10):
    """
    جلب طلبات السحب الحقيقية من قاعدة البيانات وربطها ببيانات المورد.
    """
    # 1. ربط الجداول: المعاملة -> المحفظة -> المورد
    query = WalletTransaction.query.join(
        SupplierWallet, SupplierWallet.id == WalletTransaction.wallet_id
    ).join(
        Supplier, Supplier.id == SupplierWallet.supplier_id
    )

    # 2. فلترة نوع المعاملة: السحب فقط
    query = query.filter(WalletTransaction.trans_type == 'withdrawal')

    # 3. فلترة الحالة (افتراضي: pending)
    if status and status != 'all':
        query = query.filter(WalletTransaction.status == status)

    # 4. البحث في اسم المتجر أو كود المحفظة
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Supplier.store_name.ilike(search_term),
                Supplier.trade_name.ilike(search_term),
                SupplierWallet.wallet_code.ilike(search_term)
            )
        )

    # 5. الترتيب والترقيم
    query = query.order_by(WalletTransaction.created_at.desc())
    pagination_obj = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        'items': pagination_obj.items,
        'pagination': {
            'current_page': pagination_obj.page,
            'total_pages': pagination_obj.pages,
            'has_prev': pagination_obj.has_prev,
            'has_next': pagination_obj.has_next,
            'total_count': pagination_obj.total,
            'per_page': per_page,
        }
    }


def update_withdrawal_status(request_id, action, reason='', transfer_number=None, approval_ref=None, payout_bank=None):
    """
    تحديث حالة طلب السحب الحقيقي في قاعدة البيانات (اعتماد أو رفض) مع حفظ بيانات التوثيق وإرسال إشعار للمورد.
    """
    try:
        transaction = WalletTransaction.query.get_or_404(request_id)
        
        # ✅ جلب محفظة المورد المرتبطة بالمعاملة للوصول إلى المورد وإرسال الفلاش/الإشعار
        wallet = SupplierWallet.query.get(transaction.wallet_id)
        supplier_id = wallet.supplier_id if wallet else None

        if action == 'approve':
            transaction.status = 'completed'
            
            # ✅ حفظ معلومات التحويل البنكي والتوثيق المالي
            if transfer_number:
                transaction.transfer_number = transfer_number
            if approval_ref:
                transaction.approval_ref = approval_ref
            if payout_bank:
                transaction.payout_bank = payout_bank
                
            message = f'تم اعتماد طلب السحب رقم {request_id} بنجاح عبر ({payout_bank or "جهة معتمدة"}) برقم حوالة: ({transfer_number or "---"}).'
            
            # ✅ إرسال إشعار فلاش مباشر للمورد (تخزين في سجل إشعارات النظام إن وجد)
            try:
                from apps.models.notification_db import Notification
                if supplier_id:
                    notif = Notification(
                        supplier_id=supplier_id,
                        title='تم اعتماد سحب أرباحك',
                        body=f'تم اعتماد وتحويل مبلغ طلب السحب رقم {request_id} عبر {payout_bank or "البنك"} برقم حوالة {transfer_number or "---"}',
                        type='success'
                    )
                    db.session.add(notif)
            except Exception:
                pass
            
        elif action == 'reject':
            transaction.status = 'rejected'
            if reason:
                transaction.description = f"{transaction.description or ''} | مرفوض: {reason}"
            message = f'تم رفض طلب السحب رقم {request_id} بسبب: {reason}'
            
            try:
                from apps.models.notification_db import Notification
                if supplier_id:
                    notif = Notification(
                        supplier_id=supplier_id,
                        title='تم رفض طلب السحب',
                        body=f'عذراً، تم رفض طلب السحب رقم {request_id}. السبب: {reason}',
                        type='danger'
                    )
                    db.session.add(notif)
            except Exception:
                pass
        else:
            return {'success': False, 'message': 'إجراء غير معروف.'}

        transaction.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {'success': True, 'message': message}

    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'حدث خطأ أثناء التحديث: {str(e)}'}
