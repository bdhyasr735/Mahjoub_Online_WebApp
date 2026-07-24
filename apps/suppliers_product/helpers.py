# coding: utf-8
# 📂 apps/suppliers_product/helpers.py

from io import BytesIO
from PIL import Image
import logging

logger = logging.getLogger(__name__)


def compress_image(image_data, max_size=(600, 600), quality=40):
    """ضغط الصورة"""
    try:
        img = Image.open(BytesIO(image_data))
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue()
    except Exception:
        return image_data


def paginate(items, page=1, limit=20):
    """تقسيم القائمة إلى صفحات"""
    total = len(items)
    start = (page - 1) * limit
    return {
        'items': items[start:start+limit],
        'total': total,
        'page': page,
        'limit': limit,
        'total_pages': (total + limit - 1) // limit if total > 0 else 1
    }


def filter_by_search(items, search, key='title'):
    """فلترة حسب البحث"""
    if not search:
        return items
    search_lower = search.lower()
    return [item for item in items if search_lower in str(item.get(key, '')).lower()]


def get_status_badge(status):
    """الحصول على لون البادج حسب الحالة"""
    colors = {
        'ACTIVE': 'success',
        'PUBLISHED': 'success',
        'DRAFT': 'warning',
        'INACTIVE': 'danger',
        'ARCHIVED': 'secondary',
        'REJECTED': 'danger'
    }
    return colors.get(status.upper(), 'secondary')
