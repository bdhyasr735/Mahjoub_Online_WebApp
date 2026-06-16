# 📂 apps/utils/sync_all.py
import logging
from apps.extensions import db
from apps.utils.orders_engine import get_pending_orders
from apps.models.wallet_db import WalletTransaction # تأكد من مطابقة اسم الموديل في مشروعك

logger = logging.getLogger(__name__)

def sync_orders_to_local():
    """
    مزامنة البيانات من قمرة وحفظ الحوالات والطلبات الجديدة في قاعدة البيانات المحلية.
    """
    logger.info("Starting synchronization process with Mahjoub Online...")
    
    try:
        remote_orders = get_pending_orders()
        
        if not remote_orders:
            logger.info("No orders found on the remote server to sync.")
            return {"status": "success", "count": 0}
            
        count = 0
        for order in remote_orders:
            # التحقق من عدم إدراج المعاملة مسبقاً لمنع تكرار الحسابات المعتمدة
            existing = WalletTransaction.query.filter_by(order_id=str(order['id'])).first()
            
            if not existing:
                new_txn = WalletTransaction(
                    order_id=str(order['id']),
                    amount=float(order.get('totalPrice', 0)),
                    currency='SAR',
                    transaction_type='pending',
                    description=f"Automated Sync: Order #{order['id']}",
                    status='pending'
                )
                db.session.add(new_txn)
                count += 1
        
        db.session.commit()
        logger.info(f"Successfully synced {count} new transactions to local database.")
        return {"status": "success", "count": count}

    except Exception as e:
        db.session.rollback()
        logger.error(f"Critical error during sync: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    sync_orders_to_local()
