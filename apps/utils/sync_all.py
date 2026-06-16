# 📂 apps/utils/sync_all.py
import logging
from apps.utils.orders_engine import get_pending_orders
from apps.utils.products_engine import get_products_by_supplier

logger = logging.getLogger(__name__)

def check_live_sync_status():
    """
    مزامنة والتحقق من تدفق البيانات الحية (الطلبات والمنتجات) 
    مباشرة من متجر قمرة المركزي دون الحاجة لأي جداول محلية.
    """
    try:
        # جلب البيانات حية من المحركات الميكروية
        live_products = get_products_by_supplier("all")
        live_orders = get_pending_orders()
        
        # إرجاع تقرير التدفق الحي في الذاكرة فوراً للمتصفح
        return {
            "status": "success",
            "products_count": len(live_products),
            "orders_count": len(live_orders)
        }
    except Exception as e:
        logger.error(f"Error checking live data stream in sync_all: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }
