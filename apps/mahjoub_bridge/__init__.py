# 📂 apps/mahjoub_bridge/__init__.py
from flask import Blueprint

# تعريف الـ Blueprint
# ملاحظة: تأكد أن الاسم يطابق ما تستخدمه في routes.py
mahjoub_bridge = Blueprint('mahjoub_bridge', __name__, template_folder='templates')
