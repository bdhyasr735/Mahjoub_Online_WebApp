def sync_products(self, external_products: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    مزامنة قائمة المنتجات الواردة إلى النظام بطلب واحد أو بذاكرة مؤقتة لتجنب انهيار السيرفر.
    """
    synced_count = 0
    created_count = 0
    updated_count = 0
    errors = []

    # 1. جلب جميع المنتجات الموجودة مرة واحدة مسبقاً لتجنب الطلبات المتكررة
    try:
        existing_list = self.get_all() or []
        existing_map = {str(p.get('qid') or p.get('id', '')): p for p in existing_list}
    except Exception as e:
        return {
            "success": False,
            "syncedCount": 0,
            "createdCount": 0,
            "updatedCount": 0,
            "errors": [{"product": "Bulk Fetch", "error": str(e)}]
        }

    for item in external_products:
        try:
            qid = str(item.get('qid') or item.get('id', ''))
            if not qid:
                continue
            
            product_input = {
                "name": item.get('name'),
                "description": item.get('description', ''),
                "price": float(item.get('price', 0.0)),
                "sku": item.get('sku', '') or '',
                "quantity": int(item.get('quantity', 0)),
                "status": item.get('status', 'PUBLISHED')
            }

            # 2. التحقق محلياً من وجود المنتج بدلاً من إرسال طلب شبكي لكل عنصر
            if qid in existing_map:
                result = self.update(qid, product_input)
                if not result:
                    raise ValueError(f"فشل تحديث المنتج ذو المعرف {qid}")
                updated_count += 1
            else:
                product_input["qid"] = qid
                result = self.create(product_input)
                if not result:
                    raise ValueError(f"فشل إنشاء المنتج الجديد ذو المعرف {qid}")
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
