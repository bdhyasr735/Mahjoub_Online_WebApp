# coding: utf-8
# 📂 apps/suppliers_product/helpers.py

from io import BytesIO
from PIL import Image
import logging

logger = logging.getLogger(__name__)


def compress_image(image_data, max_size=(800, 800), quality=70):
    """
    ضغط وتقليل حجم الصورة مع الحفاظ على الخلفية البيضاء للصور الشفافة (PNG/RGBA)
    """
    try:
        img = Image.open(BytesIO(image_data))
        
        # معالجة الصور الشفافة لمنع التحلل إلى اللون الأسود عند تحويلها لـ JPEG
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[-1])
            else:
                background.paste(img)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # إعادة الحجم مع الحفاظ على أبعاد الصورة
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue()
    except Exception as e:
        logger.error(f"❌ خطأ أثناء ضغط الصورة: {e}")
        return image_data


def paginate(items, page=1, limit=20):
    """تقسيم القائمة إلى صفحات بشكل آمن"""
    page = max(1, int(page) if str(page).isdigit() else 1)
    limit = max(1, int(limit) if str(limit).isdigit() else 20)
    
    total = len(items) if items else 0
    start = (page - 1) * limit
    
    return {
        'items': items[start:start+limit] if items else [],
        'total': total,
        'page': page,
        'limit': limit,
        'total_pages': (total + limit - 1) // limit if total > 0 else 1
    }


def filter_by_search(items, search, key='title'):
    """
    فلترة العناصر حسب البحث (يدعم البحث المباشر وفي العناصر المدمجة مثل 'product' أو 'mapping')
    """
    if not search or not items:
        return items or []
    
    search_lower = str(search).strip().lower()

    filtered = []
    for item in items:
        # البحث في المستوى الأعلى أولاً
        val = item.get(key)
        
        # البحث داخل كائن المنتج المتداخل إن وجد
        if val is None and isinstance(item.get('product'), dict):
            product_dict = item['product']
            val = product_dict.get(key) or product_dict.get('name') or product_dict.get('title')
        
        # البحث بواسطة QID أيضاً لتسهيل البحث على المورد
        qid_val = item.get('qid') or (item.get('mapping', {}).get('qid') if isinstance(item.get('mapping'), dict) else None)

        target_text = f"{str(val or '')} {str(qid_val or '')}".lower()
        if search_lower in target_text:
            filtered.append(item)

    return filtered


def get_status_badge(status):
    """الحصول على لون البادج حسب الحالة بشكل آمن"""
    if not status:
        return 'secondary'
        
    colors = {
        'ACTIVE': 'success',
        'PUBLISHED': 'success',
        'DRAFT': 'warning',
        'INACTIVE': 'danger',
        'ARCHIVED': 'secondary',
        'REJECTED': 'danger'
    }
    return colors.get(str(status).strip().upper(), 'secondary')
