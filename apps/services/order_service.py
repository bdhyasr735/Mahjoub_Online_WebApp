# coding: utf-8
# 📂 apps/services/order_service.py

from typing import Dict, Any, Optional
from .graphql_client import GraphQLClient


class OrderService:
    """خدمة إدارة الطلبات والمزامنة"""
    
    def __init__(self, client: GraphQLClient):
        self.client = client

    def get_order(self, qid: str) -> Optional[Dict[str, Any]]:
        """جلب تفاصيل الطلب باستخدام المعرف qid"""
        query = """
        query GetOrder($qid: ID!) {
            order(qid: $qid) { 
                qid 
                total 
                status 
                createdAt
                items { 
                    productQid 
                    quantity 
                    price 
                } 
            }
        }
        """
        result = self.client.execute(query, {"qid": qid})
        return result.get('order') if result else None

    def create_order(self, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """إنشاء طلب جديد"""
        mutation = """
        mutation CreateOrder($input: OrderInput!) {
            createOrder(input: $input) { 
                qid 
                total 
                status 
            }
        }
        """
        result = self.client.execute(mutation, {"input": input_data})
        return result.get('createOrder') if result else None
