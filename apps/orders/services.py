# coding: utf-8
# 📂 apps/orders/services.py

from apps.models.orders_db import Order
from apps.models.financials_db import OrderFinancial
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.extensions import db
from decimal import Decimal, InvalidOperation

class OrderService:
    @staticmethod
    def get_order_details(order_id):
        """جلب تفاصيل الطلب والبيانات المالية المرتبطة به."""
        # استخدام STR لضمان التوافق مع المعرف النصي (String ID)
        result = db.session.query(Order, OrderFinancial)\
            .outerjoin(OrderFinancial, Order.id == OrderFinancial.order_id)\
            .filter(Order.id == str(order_id)).first()
        return result if result else (None, None)

    @staticmethod
    def complete_order_and_settle(order_id):
        """
        محرك التسوية: يحول الطلب لمكتمل ويوزع الأرباح للمورد في محفظته.
        يعتمد على أحداث (Events) في WalletTransaction لتحديث الرصيد تلقائياً.
        """
        order_id_str = str(order_id)
        order = Order.query.get(order_id_str)
        financial = OrderFinancial.query.filter_by(order_id=order_id_str).first()
        
        # التأكد من وجود الطلب والبيانات المالية وأنه لم يسبق تسويته
        if order and financial and order.status != 'completed':
            try:
                # 1. تحديث حالة الطلب والمالية
                order.status = 'completed'
                financial.settlement_status = 'settled'
                
                # 2. إيداع المبلغ في محفظة المورد
                # نستخدم supplier_id من البيانات المالية (Integer)
                s_id = int(financial.supplier_id)
                wallet = SupplierWallet.query.filter_by(supplier_id=s_id).first()
                
                if wallet:
                    # تحويل المبلغ لـ Decimal بأمان لتجنب أخطاء العمليات الحسابية
                    amount_val = Decimal(str(financial.total_paid_raw or 0))
                    
                    # إنشاء سجل حركة مالية
                    # الـ Event في WalletTransaction سيقوم بتحديث balance_after في المحفظة
                    transaction = WalletTransaction(
                        wallet_id=wallet.id,
                        owner_type='supplier',
                        owner_id=s_id, 
                        trans_type='sale_revenue',
                        amount=amount_val,
                        currency=financial.currency or 'SAR',
                        description=f"تسوية الطلب رقم {order.order_id_display or order.id}",
                        related_order_id=order_id_str
                    )
                    db.session.add(transaction)
                
                db.session.commit()
                return True
                
            except (ValueError, InvalidOperation, Exception) as e:
                db.session.rollback()
                print(f"❌ خطأ أثناء تسوية الطلب {order_id}: {e}")
                return False
                
        return False
