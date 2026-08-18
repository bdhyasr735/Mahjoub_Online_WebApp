# 📂 apps/admin_suppliers_wallets/routes/withdraw_requests.py

from flask import Blueprint
from apps.admin_suppliers_wallets.controllers import withdraw_requests_controller

# ✅ تعريف الـ Blueprint هنا هو الحل للخطأ الذي يظهر لك
bp = Blueprint('withdraw_requests', __name__)

# ✅ ربط المسارات بالدوال الموجودة في الـ controller
bp.add_url_rule('/withdraw-requests', view_func=withdraw_requests_controller.withdraw_requests_list, methods=['GET'])
bp.add_url_rule('/withdraw-requests/process', view_func=withdraw_requests_controller.process_withdraw_request_post, methods=['POST'])