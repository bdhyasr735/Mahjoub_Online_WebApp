# coding: utf-8
# 📂 apps/services/order_service.py

import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

from apps.services.graphql_client import GraphQLClient

logger = logging.getLogger(__name__)


class OrderService:
    """
    خدمة الطلبات (Orders) المسؤولة عن:
    - جلب طلب واحد (مفصل أو مختصر)
    - جلب قائمة الطلبات مع ترقيم (Pagination)
    - جلب طلبات متعددة باستخدام قائمة IDs
    """

    def __init__(self, client: GraphQLClient):
        self.client = client

        # (اختياري) تحميل الاستعلامات من ملف .graphql إذا كان موجوداً
        # وإلا سنستخدم الاستعلامات المضمنة في الأسفل
        queries_path = Path(__file__).parent / "orders_queries.graphql"
        self.queries_raw = ""
        if queries_path.exists():
            try:
                with open(queries_path, "r", encoding="utf-8") as f:
                    self.queries_raw = f.read()
                logger.info("✅ تم تحميل orders_queries.graphql بنجاح")
            except Exception as e:
                logger.error(f"❌ فشل تحميل ملف الاستعلامات: {e}")

    # =========================================================
    # 1. جلب طلب واحد بالمعرف (إصدار كامل ومفصل)
    # =========================================================
    def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        يستخدم الاستعلام المعقد الذي يعيد { data, success, message }
        ويعيد لك الكائن الداخلي (data) مباشرة لتسهيل التعامل.
        """
        query = """
        fragment OrderFull on Order {
            _id
            status { _id title code }
            COD
            type
            currency { _id title currencyCode currencySymbol }
            freeze
            totalPrice
            totalPriceWithTax
            priceWithShipping
            shippingPrice
            handel
            taxAmount
            taxType
            taxValue
            taxLines { title amountType value amount base }
            paymentMethod {
                _id
                payment {
                    _id key descreption installed enable deleted schema
                    createdAt updatedAt icon iconUrl needConfig methods name instructions id
                }
                enable unable action install deleted complete createdAt updatedAt data
            }
            market {
                _id app title status
                countryIds { _id name image { image imageUrl } code continent capital active deleted phonekey }
                countryCodes
                targetCurrency { _id title currencyCode currencySymbol }
                targetCurrencyId { _id title currencyCode currencySymbol }
                targetCurrencyCode enableRounding localCurrencies fxMode exchangeRate providerName
                lastUpdated history { rate updatedAt } createdAt updatedAt
            }
            marketSnapshot
            shippingAddress {
                _id
                country { _id name code continent capital active deleted phonekey }
                city { _id name description active deleted isSelected createdAt }
                street neighborhood zipCode description device deleted createdAt updatedAt
            }
            app
            isPaid
            isFastOrder
            createdAt
            salesLead {
                _id firstName lastName district street phone1 phone2 email
            }
            account {
                _id app
                account {
                    _id fullname phone type verified blocked blockedReason status avatarUrl createdAt updatedAt
                }
                verified blocked orderCount lastSeen createdAt updatedAt
            }
            items {
                _id orderId productId variantId
                productData { title slug app image { _id fileUrl } price }
                variantData {
                    price compareAtPrice
                    options {
                        _id
                        option { _id name type product }
                        label sortOrder
                    }
                }
                quantity weight price compareAtPrice totalPrice totalCompareAtPrice totalSavings
            }
        }

        query FindOrderById($id: ID!) {
            findOrderById(id: $id) {
                data { ...OrderFull }
                success
                message
            }
        }
        """

        variables = {"id": order_id}
        result = self.client.execute(query, variables)

        # التحقق من وجود أخطاء في الاستجابة
        if "errors" in result:
            logger.error(f"❌ خطأ في GraphQL: {result['errors']}")
            return None

        # استخراج البيانات من الطبقة الداخلية
        data_wrapper = result.get("data", {}).get("findOrderById", {})
        if not data_wrapper.get("success", False):
            logger.warning(f"⚠️ الطلب غير موجود أو فشل: {data_wrapper.get('message')}")
            return None

        return data_wrapper.get("data")  # هنا الكائن الكامل للطلب

    # =========================================================
    # 2. جلب طلب واحد ولكن بإصدار مختصر (خفيف للقوائم)
    # =========================================================
    def get_order_summary(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        يستخدم الاستعلام البسيط (الأول في مشاركتك) الذي يعيد الحقول مباشرة
        مناسب لعرض سريع بدون تفاصيل الدفع والشحن المعقدة.
        """
        query = """
        query FindOrderById($id: ID!) {
            findOrderById(id: $id) {
                _id
                type
                totalPrice
                isPaid
                createdAt
                status { code title }
                account {
                    account { fullname }
                }
                items {
                    productId
                    quantity
                    price
                    productData {
                        title
                        price
                        image { fileUrl }
                        images { fileUrl }
                    }
                }
            }
        }
        """
        variables = {"id": order_id}
        result = self.client.execute(query, variables)

        if "errors" in result:
            logger.error(f"❌ خطأ في GraphQL: {result['errors']}")
            return None

        return result.get("data", {}).get("findOrderById")

    # =========================================================
    # 3. جلب قائمة الطلبات (مع Pagination)
    # =========================================================
    def get_all_orders(
        self,
        page: int = 1,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        جلب قائمة الطلبات مع دعم الترقيم والفلترة.
        المدخلات:
            - page: رقم الصفحة (افتراضي 1)
            - limit: عدد العناصر في الصفحة (افتراضي 10)
            - filters: كائن Filter اختياري (مثل { status: "PAID" })
        المخرجات:
            {
                "data": [OrderSummary, ...],
                "pagination": { totalItems, totalPages, currentPage, limit, hasNextPage }
            }
        """
        query = """
        fragment OrderSummary on Order {
            _id
            totalPrice
            isPaid
            createdAt
            status { code title }
            account { account { fullname } }
            items {
                productId
                quantity
                price
                productData { title price image { fileUrl } }
            }
        }

        query FindAllOrders($input: FindAllOrdersInput!) {
            findAllOrders(input: $input) {
                data { ...OrderSummary }
                pagination {
                    totalItems
                    totalPages
                    currentPage
                    limit
                    hasNextPage
                }
            }
        }
        """

        # بناء كائن الإدخال حسب الـ Schema المتوقعة
        input_data = {
            "page": page,
            "limit": limit,
        }
        if filters:
            input_data["filters"] = filters

        variables = {"input": input_data}
        result = self.client.execute(query, variables)

        if "errors" in result:
            logger.error(f"❌ خطأ في جلب الطلبات: {result['errors']}")
            return {"data": [], "pagination": {}}

        return result.get("data", {}).get("findAllOrders", {})

    # =========================================================
    # 4. جلب طلبات متعددة باستخدام قائمة المعرفات
    # =========================================================
    def get_orders_by_ids(self, ids: List[str]) -> Dict[str, Any]:
        """
        يستخدم getOrdersByIds لجلب عدة طلبات دفعة واحدة (مفصلة).
        """
        query = """
        fragment OrderFull on Order {
            _id
            status { _id title code }
            COD
            type
            currency { _id title currencyCode currencySymbol }
            freeze
            totalPrice
            totalPriceWithTax
            priceWithShipping
            shippingPrice
            handel
            taxAmount
            taxType
            taxValue
            taxLines { title amountType value amount base }
            paymentMethod {
                _id
                payment {
                    _id key descreption installed enable deleted schema
                    createdAt updatedAt icon iconUrl needConfig methods name instructions id
                }
                enable unable action install deleted complete createdAt updatedAt data
            }
            market {
                _id app title status
                countryIds { _id name image { image imageUrl } code continent capital active deleted phonekey }
                countryCodes
                targetCurrency { _id title currencyCode currencySymbol }
                targetCurrencyId { _id title currencyCode currencySymbol }
                targetCurrencyCode enableRounding localCurrencies fxMode exchangeRate providerName
                lastUpdated history { rate updatedAt } createdAt updatedAt
            }
            marketSnapshot
            shippingAddress {
                _id
                country { _id name code continent capital active deleted phonekey }
                city { _id name description active deleted isSelected createdAt }
                street neighborhood zipCode description device deleted createdAt updatedAt
            }
            app
            isPaid
            isFastOrder
            createdAt
            salesLead {
                _id firstName lastName district street phone1 phone2 email
            }
            account {
                _id app
                account {
                    _id fullname phone type verified blocked blockedReason status avatarUrl createdAt updatedAt
                }
                verified blocked orderCount lastSeen createdAt updatedAt
            }
            items {
                _id orderId productId variantId
                productData { title slug app image { _id fileUrl } price }
                variantData {
                    price compareAtPrice
                    options {
                        _id
                        option { _id name type product }
                        label sortOrder
                    }
                }
                quantity weight price compareAtPrice totalPrice totalCompareAtPrice totalSavings
            }
        }

        query GetOrdersByIds($input: FindOrdersByIdsInput!) {
            getOrdersByIds(input: $input) {
                data { ...OrderFull }
                pagination {
                    totalItems
                    hasPreviousPage
                    totalPages
                    currentPage
                    limit
                    hasNextPage
                }
            }
        }
        """

        variables = {"input": {"ids": ids}}
        result = self.client.execute(query, variables)

        if "errors" in result:
            logger.error(f"❌ خطأ في جلب الطلبات بالـ IDs: {result['errors']}")
            return {"data": [], "pagination": {}}

        return result.get("data", {}).get("getOrdersByIds", {})

    # =========================================================
    # 5. دالة مساعدة للتنظيف (اختياري)
    # =========================================================
    @staticmethod
    def extract_order_items(order_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """استخراج قائمة العناصر من كائن الطلب مع معالجة البيانات الناقصة."""
        if not order_data:
            return []
        return order_data.get("items", [])
