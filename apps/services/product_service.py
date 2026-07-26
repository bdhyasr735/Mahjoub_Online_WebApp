def sync_products(self, external_products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        مزامنة قائمة المنتجات الواردة إلى النظام مع التحقق الصارم من نجاح العمليات الفعلية.
        """
        synced_count = 0
        created_count = 0
        updated_count = 0
        errors = []

        for item in external_products:
            try:
                qid = str(item.get('qid') or item.get('id', ''))
                if not qid:
                    continue
                
                # تجهيز البيانات المدخلة مع التأكد من مطابقتها لأنواع البيانات المطلوبة
                product_input = {
                    "name": item.get('name'),
                    "description": item.get('description', ''),
                    "price": float(item.get('price', 0.0)),
                    "sku": item.get('sku', '') or '',
                    "quantity": int(item.get('quantity', 0)),
                    "status": item.get('status', 'PUBLISHED')
                }

                # التحقق مما إذا كان المنتج موجوداً مسبقاً
                existing_product = self.get_product_by_qid(qid)
                
                if existing_product:
                    result = self.update(qid, product_input)
                    if not result:
                        raise ValueError(f"فشل تحديث المنتج ذو المعرف {qid} عبر خادم GraphQL")
                    updated_count += 1
                else:
                    product_input["qid"] = qid
                    result = self.create(product_input)
                    if not result:
                        raise ValueError(f"فشل إنشاء المنتج الجديد ذو المعرف {qid} عبر خادم GraphQL")
                    created_count += 1
                
                synced_count += 1
                
            except Exception as e:
                errors.append({
                    "product": item.get('name', 'Unknown'),
                    "qid": item.get('qid', ''),
                    "error": str(e)
                })

        return {
            "success": len(errors) == 0,
            "syncedCount": synced_count,
            "createdCount": created_count,
            "updatedCount": updated_count,
            "errors": errors
        }
