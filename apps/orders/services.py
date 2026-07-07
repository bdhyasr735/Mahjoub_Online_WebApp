# 📂 apps/orders/services.py (نسخة مطورة)

from apps.models.orders_db import Order
from apps.models.financials_db import OrderFinancial
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.extensions import db
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class OrderService:
    @staticmethod
    def complete_order_and_settle(order_id):
        order_id_str = str(order_id)
        order = Order.query.get(order_id_str)
        financial = OrderFinancial.query.filter_by(order_id=order_id_str).first()
        
        # 1. التحقق من وجود الطلب وعدم إكمال التسوية مسبقاً
        if not order or not financial or order.status == 'completed' or financial.settlement_status == 'settled':
            logger.warning(f"⚠️ محاولة تسوية غير صالحة أو مكررة للطلب {order_id}")
            return False

        try:
            # 2. تحديث الحالات
            order.status = 'completed'
            financial.settlement_status = 'settled'
            
            s_id = int(financial.supplier_id)
            amount_val = Decimal(str(financial.supplier_cost or 0))
            
            wallet = SupplierWallet.query.filter_by(supplier_id=s_id).first()
            if not wallet:
                raise Exception(f"المحفظة غير موجودة للمورد {s_id}")

            # 3. إنشاء حركة مالية
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
            
            # 4. تحديث رصيد المحفظة يدوياً (لضمان الدقة)
            wallet.balance = (wallet.balance or 0) + amount_val
            
            db.session.commit()
            logger.info(f"✅ تمت تسوية الطلب {order_id} وإيداع {amount_val} لمحفظة المورد {s_id}.")
            return True
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ خطأ حرج أثناء تسوية الطلب {order_id}: {e}")
            return False
