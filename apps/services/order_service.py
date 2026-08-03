# coding: utf-8
# 📂 apps/services/order_service.py

import os
from typing import Dict, Any, Optional, List
from .graphql_client import GraphQLClient


class OrderService:
    """خدمة إدارة الطلبات والمزامنة"""
    
    def __init__(self, client: GraphQLClient):
        self.client = client
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.query_file_path = os.path.join(current_dir, 'orders_queries.graphql')
        
        try:
            with open(self.query_file_path, 'r', encoding='utf-8') as f:
                self.queries_content = f.read()
        except FileNotFoundError:
            print(f"⚠️ [OrderService]: لم يتم العثور على ملف الاستعلامات")
            self.queries_content = ""

    def _extract_query(self, query_name: str) -> str:
        """استخراج استعلام معين من ملف الاستعلامات"""
        if not self.queries_content:
            return ""
        
        lines = self.queries_content.split('\n')
        result = []
        found = False
        brace_count = 0
        
        for line in lines:
            if f"query {query_name}" in line or f"mutation {query_name}" in line:
                found = True
            
            if found:
                result.append(line)
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0 and len(result) > 1:
                    break
        
        return '\n'.join(result)

    def get_order(self, qid: str) -> Optional[Dict[str, Any]]:
        """جلب تفاصيل الطلب باستخدام المعرف qid"""
        query = self._extract_query("FindOrderById")
        try:
            result = self.client.execute(query, {"id": qid}, operation_name="FindOrderById")
            if result and 'findOrderById' in result:
                return result['findOrderById']
            return None
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في جلب الطلب {qid}: {e}")
            return None

    def get_all_orders(self, page: int = 1, per_page: int = 10, supplier_id: str = None, status: str = None, search: str = None, date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """
        جلب قائمة الطلبات مع دعم الترقيم وتصفية المورد والحالة.
        """
        input_data = {
            "page": page,
            "limit": per_page
        }
        if supplier_id:
            input_data["supplierId"] = supplier_id
        if status:
            input_data["status"] = status
        if search:
            input_data["search"] = search
        if date_from:
            input_data["dateFrom"] = date_from
        if date_to:
            input_data["dateTo"] = date_to

        query = self._extract_query("FindAllOrders")
        try:
            result = self.client.execute(query, {"input": input_data}, operation_name="FindAllOrders")
            if result and 'findAllOrders' in result:
                return {
                    "data": result['findAllOrders'].get('data', []),
                    "pagination": result['findAllOrders'].get('pagination', {
                        "totalItems": 0,
                        "totalPages": 1,
                        "currentPage": page,
                        "limit": per_page,
                        "hasNextPage": False
                    })
                }
            return {"data": [], "pagination": {"totalItems": 0, "totalPages": 1, "currentPage": page, "limit": per_page, "hasNextPage": False}}
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في جلب الطلبات: {e}")
            return {"data": [], "pagination": {"totalItems": 0, "totalPages": 1, "currentPage": page, "limit": per_page, "hasNextPage": False}}

    def create_order(self, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """إنشاء طلب جديد"""
        mutation = self._extract_query("CreateOrder")
        try:
            result = self.client.execute(mutation, {"input": input_data}, operation_name="CreateOrder")
            return result.get('createOrder') if result else None
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في إنشاء الطلب: {e}")
            return None

    def update_order_status(self, qid: str, status: str) -> Optional[Dict[str, Any]]:
        """تحديث حالة الطلب"""
        mutation = self._extract_query("UpdateOrderStatus")
        try:
            result = self.client.execute(mutation, {"id": qid, "status": status}, operation_name="UpdateOrderStatus")
            return result.get('updateOrderStatus') if result else None
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في تحديث حالة الطلب {qid}: {e}")
            return None

    def delete_order(self, qid: str) -> bool:
        """حذف طلب"""
        mutation = self._extract_query("DeleteOrder")
        try:
            result = self.client.execute(mutation, {"id": qid}, operation_name="DeleteOrder")
            return result.get('deleteOrder', False) if result else False
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في حذف الطلب {qid}: {e}")
            return False
