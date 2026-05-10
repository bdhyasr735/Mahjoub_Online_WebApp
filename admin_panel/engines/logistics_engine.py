
ش# admin_panel/engines/logistics_engine.py
from core import db
from core.models.supplier import Supplier

class LogisticsEngine:
    """المحرك المسؤول عن إدارة العمليات الميدانية والربط بين المورد والعميل"""

    @staticmethod
    def get_zone_density():
        """تحليل كثافة الموردين في كل منطقة (الخوخة، المخا، عدن)"""
        # هذا يساعدك كأدمن لتعرف أين تحتاج لزيادة عدد المناديب
        stats = db.session.query(
            Supplier.province, 
            db.func.count(Supplier.id)
        ).group_by(Supplier.province).all()
        return dict(stats)

    @staticmethod
    def calculate_shipping(origin_data, destination_data):
        """محرك حساب تكلفة الشحن الفوري بناءً على المسافة بين المورد والمستهلك"""
        # المنطق: إذا كان المورد والمستهلك في نفس المديرية (مثلاً الخوخة) التكلفة أقل
        if origin_data['district'] == destination_data['district']:
            return 1000 # تسعيرة التوصيل الداخلي
        
        return 2500 # تسعيرة الشحن بين المديريات أو المحافظات

    @staticmethod
    def validate_delivery_route(supplier_id, customer_district):
        """التأكد من أن خط السير مدعوم برمجياً وأمنياً من قبل مناديبنا"""
        supplier = Supplier.query.get(supplier_id)
        supported_districts = ["الخوخة", "المخا", "المنصورة", "الحوك"] # النطاق الحالي
        
        if customer_district in supported_districts:
            return True, "المسار مدعوم، المندوب متاح."
        return False, "عذراً، لم يتم تفعيل خدمة التوصيل لهذه المنطقة بعد."

    @staticmethod
    def generate_shipping_label(order_id, supplier, customer):
        """توليد بيانات بوليصة الشحن السيادية لمحجوب أونلاين"""
        return {
            "order_ref": f"MHA-LOG-{order_id}",
            "from": f"{supplier.trade_name} - {supplier.province}",
            "to": f"{customer.name} - {customer.district}",
            "courier_status": "قيد التعيين"
        }
