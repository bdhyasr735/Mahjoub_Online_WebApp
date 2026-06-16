# 📂 apps/utils/orders_engine.py
import logging
from apps.utils.bridge_engine import execute_query

logger = logging.getLogger(__name__)

def get_pending_orders():
    """
    جلب الطلبات مباشرة من قمرة لفرز الحالات المعلقة حياً ومباشراً في الذاكرة.
    """
    # تضمين حقول lineItems و product لتتوافق مع متطلبات الـ Template ومنع انهيار الخادم
    query = """
    query GetPendingOrders {
      allOrders {
        id
        totalPrice
        status
        createdAt
        lineItems {
          id
          product {
            id
            name
          }
        }
      }
    }
    """
    result = execute_query(query)
    
    # تحصين كامل ضد المصفوفات الفارغة أو فشل الاتصال لضمان استقرار اللوحة
    if not result or 'data' not in result:
        return []
        
    data = result.get('data', {})
    
    # إذا كانت قمرة ترجع الحقل باسم orders أو allOrders
    orders = data.get('allOrders') or data.get('orders') or []
    
    # في حالة رجوع قيم None من قمرة لأي سبب، نضمن أنها مصفوفة نظيفة لـ Jinja2
    if not isinstance(orders, list):
        return []

    # تصفية الطلبات المعلقة حياً في الذاكرة لسرعة العرض الفورية مع حماية الحقول
    pending_orders_list = []
    for o in orders:
        if isinstance(o, dict) and o.get('status') == 'pending':
            # تأمين وجود مفتاح lineItems حتى لو لم يرجع من السيرفر لتفادي خطأ 500 في الـ Template
            if 'lineItems' not in o or o['lineItems'] is None:
                o['lineItems'] = []
            pending_orders_list.append(o)
            
    return pending_orders_list
