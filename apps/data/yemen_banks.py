# coding: utf-8
# 📂 apps/data/yemen_banks.py

"""
قائمة البنوك العاملة في اليمن
"""

YEMEN_BANKS = [
    {'id': 'cby', 'name': 'البنك المركزي اليمني', 'icon': 'fa-university'},
    {'id': 'aden', 'name': 'بنك عدن', 'icon': 'fa-building'},
    {'id': 'saba', 'name': 'بنك سبأ', 'icon': 'fa-building'},
    {'id': 'yemen_bank', 'name': 'البنك اليمني للإنشاء والتعمير', 'icon': 'fa-building'},
    {'id': 'islamic', 'name': 'البنك الإسلامي اليمني', 'icon': 'fa-mosque'},
    {'id': 'international', 'name': 'البنك اليمني الدولي', 'icon': 'fa-globe'},
    {'id': 'agricultural', 'name': 'المصرف الزراعي التعاوني', 'icon': 'fa-seedling'},
    {'id': 'housing', 'name': 'مصرف الإسكان', 'icon': 'fa-home'},
    {'id': 'tadhamon', 'name': 'بنك تضامن', 'icon': 'fa-handshake'},
    {'id': 'kuraimi', 'name': 'بنك الكريمي', 'icon': 'fa-building'},
    {'id': 'queity', 'name': 'بنك القطيبي', 'icon': 'fa-building'},          # ✅ بنك القطيبي
    {'id': 'baseri', 'name': 'بنك البسيري', 'icon': 'fa-building'},          # ✅ بنك البسيري
    {'id': 'shamil', 'name': 'بنك الشامل', 'icon': 'fa-building'},
    {'id': 'yemen_gulf', 'name': 'بنك اليمن والخليج', 'icon': 'fa-building'},
    {'id': 'national', 'name': 'البنك الوطني اليمني', 'icon': 'fa-building'},
    {'id': 'modern', 'name': 'المصرف الحديث', 'icon': 'fa-building'},
    {'id': 'future', 'name': 'بنك المستقبل', 'icon': 'fa-rocket'},
    {'id': 'trust', 'name': 'بنك الأمانة', 'icon': 'fa-shield-alt'},
    {'id': 'cooperative', 'name': 'المصرف التعاوني', 'icon': 'fa-hand-holding-heart'},
    {'id': 'other', 'name': 'بنك آخر', 'icon': 'fa-ellipsis-h'}
]

# ✅ قائمة بأسماء البنوك فقط (للقوائم المنسدلة)
BANKS_LIST = [bank['name'] for bank in YEMEN_BANKS]

# ✅ دالة للحصول على أيقونة البنك
def get_bank_icon(bank_name):
    for bank in YEMEN_BANKS:
        if bank['name'] == bank_name:
            return bank['icon']
    return 'fa-university'

# ✅ دالة للحصول على معرف البنك
def get_bank_id(bank_name):
    for bank in YEMEN_BANKS:
        if bank['name'] == bank_name:
            return bank['id']
    return None

# ✅ دالة للبحث عن بنك بالاسم
def search_bank(query):
    query = query.lower()
    return [bank for bank in YEMEN_BANKS if query in bank['name'].lower()]
