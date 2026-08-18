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

# [تم اختصار الدوال السابقة (KPIs, get_suppliers_list, etc) للحفاظ على التركيز على التعديل المطلوب]

def update_withdrawal_status(request_id, action, reason='', transfer_number=None, approval_ref=None, payout_bank=None):
    """
    تحديث حالة طلب السحب الحقيقي في قاعدة البيانات مع إرجاع المعرف الفعلي (ID) للطلب.
    """
    try:
        transaction = WalletTransaction.query.get_or_404(request_id)
        
        # ✅ جلب محفظة المورد المرتبطة بالمعاملة
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
                
            message = f'تم اعتماد طلب السحب رقم {transaction.id} بنجاح عبر ({payout_bank or "جهة معتمدة"}) برقم حوالة: ({transfer_number or "---"}).'
            
            # ✅ إرسال إشعار فلاش مباشر للمورد
            try:
                from apps.models.notification_db import Notification
                if supplier_id:
                    notif = Notification(
                        supplier_id=supplier_id,
                        title='تم اعتماد سحب أرباحك',
                        body=f'تم اعتماد وتحويل مبلغ طلب السحب رقم {transaction.id} عبر {payout_bank or "البنك"} برقم حوالة {transfer_number or "---"}',
                        type='success'
                    )
                    db.session.add(notif)
            except Exception:
                pass
            
        elif action == 'reject':
            transaction.status = 'rejected'
            if reason:
                transaction.description = f"{transaction.description or ''} | مرفوض: {reason}"
            message = f'تم رفض طلب السحب رقم {transaction.id} بسبب: {reason}'
            
            try:
                from apps.models.notification_db import Notification
                if supplier_id:
                    notif = Notification(
                        supplier_id=supplier_id,
                        title='تم رفض طلب السحب',
                        body=f'عذراً، تم رفض طلب السحب رقم {transaction.id}. السبب: {reason}',
                        type='danger'
                    )
                    db.session.add(notif)
            except Exception:
                pass
        else:
            return {'success': False, 'message': 'إجراء غير معروف.'}

        transaction.updated_at = datetime.utcnow()
        db.session.commit()
        
        # ✅ الإرجاع يتضمن المعرف الحقيقي من قاعدة البيانات (transaction.id)
        return {
            'success': True, 
            'message': message, 
            'actual_id': transaction.id 
        }

    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'حدث خطأ أثناء التحديث: {str(e)}'}
