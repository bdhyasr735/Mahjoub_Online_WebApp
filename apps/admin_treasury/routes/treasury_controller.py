# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/routes/treasury_controller.py

import os
from flask import render_template, request, abort
from datetime import datetime
from sqlalchemy import func, or_

# ✅ التغيير المهم هنا: نستورد الـ blueprint من ملف __init__.py بدلاً من إنشائه
from apps.admin_treasury import admin_treasury_bp

from apps.extensions import db
from apps.models.treasury_db import TreasuryEntry
from apps.models.financials_db import OrderFinancial
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet

# ----------------------------------------------------
# (احذف السطر القديم الذي كان يحتوي على: admin_treasury_bp = Blueprint(...) )
# ----------------------------------------------------

# باقي الكود يبقى كما هو تماماً (الدوال، الديكورات @admin_treasury_bp.route، إلخ...)
