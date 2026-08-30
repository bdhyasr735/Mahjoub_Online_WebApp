```python
# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/auth_login.py

"""
بوابة تسجيل دخول الموردين وموظفي الموردين
محجوب أونلاين

يدعم:
    - حساب المورد Supplier
    - موظف المورد SupplierStaff
    - تسجيل الدخول باسم المستخدم
    - البريد الإلكتروني
    - رقم الهاتف
    - كلمة المرور المشفرة عبر Werkzeug
    - remember_me
    - Flask-Login
    - JSON API لتسجيل الدخول
    - صفحات GET عبر login.html
"""

from datetime import datetime
from urllib.parse import urlparse, urljoin

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for,
    flash,
    current_app,
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
)

from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff


# ============================================================
# Blueprint
# ============================================================

bp = Blueprint(
    "auth_login",
    __name__,
)


# ============================================================
# أدوات مساعدة
# ============================================================

def extract_phone_digits(value):
    """
    استخراج الأرقام فقط من رقم الهاتف.

    يتم توحيد البحث إلى آخر 9 أرقام،
    بما يتوافق مع Supplier و SupplierStaff.
    """
    if not value:
        return None

    digits = "".join(
        filter(str.isdigit, str(value))
    )

    if not digits:
        return None

    return digits[-9:] if len(digits) >= 9 else digits


def parse_bool(value):
    """
    تحويل القيم القادمة من JSON / Form إلى Boolean حقيقي.

    مهم جدًا لأن:
        bool("false") == True

    ولذلك لا نستخدم bool() مباشرة.
    """
    if isinstance(value, bool):
        return value

    if value is None:
        return False

    if isinstance(value, (int, float)):
        return bool(value)

    value = str(value).strip().lower()

    return value in {
        "1",
        "true",
        "yes",
        "on",
        "y",
        "نعم",
    }


def get_request_data():
    """
    قراءة بيانات تسجيل الدخول سواء كانت JSON أو Form.
    """
    if request.is_json:
        return request.get_json(silent=True) or {}

    return request.form.to_dict()


def is_safe_url(target):
    """
    التحقق من أن next URL داخلي وآمن.

    يمنع إعادة توجيه المستخدم إلى نطاق خارجي.
    """
    if not target:
        return False

    try:
        host_url = urlparse(request.host_url)
        redirect_url = urlparse(
            urljoin(request.host_url, target)
        )

        return (
            redirect_url.scheme in {"http", "https"}
            and host_url.netloc == redirect_url.netloc
        )

    except Exception:
        return False


def get_redirect_url():
    """
    تحديد وجهة المستخدم بعد تسجيل الدخول.
    """
    next_url = request.args.get("next")

    if not next_url and request.is_json:
        data = request.get_json(silent=True) or {}
        next_url = data.get("next")

    if next_url and is_safe_url(next_url):
        return next_url

    return url_for("suppliers_dashboard.dashboard")


# ============================================================
# البحث عن المورد
# ============================================================

def find_supplier(identifier):
    """
    البحث عن المورد بواسطة:

        1. username
        2. email
        3. search_phone

    ملاحظة:
    رقم الهاتف الحقيقي مشفر في _phone_enc،
    لذلك يتم البحث بواسطة search_phone.
    """

    identifier = (identifier or "").strip()

    if not identifier:
        return None

    search_phone = extract_phone_digits(identifier)

    filters = [
        Supplier.username == identifier,
        Supplier.email == identifier,
    ]

    if search_phone:
        filters.append(
            Supplier.search_phone == search_phone
        )

    return (
        Supplier.query
        .filter(or_(*filters))
        .first()
    )


# ============================================================
# البحث عن موظف المورد
# ============================================================

def find_staff(identifier):
    """
    البحث عن موظف المورد.

    username:
        يمكن البحث عنه مباشرة.

    phone:
        يتم البحث باستخدام search_phone.

    email:
        البريد مشفر في SupplierStaff._email_enc،
        ولذلك لا يمكن عمل:

            SupplierStaff.email == identifier

        لأن email Property وليس Column حقيقي.

        لذلك إذا كان الإدخال بريدًا،
        يتم جلب الموظفين المطابقين المحتملين
        ثم مقارنة البريد بعد فك التشفير عبر property.
    """

    identifier = (identifier or "").strip()

    if not identifier:
        return None

    search_phone = extract_phone_digits(identifier)

    filters = [
        SupplierStaff.username == identifier,
    ]

    if search_phone:
        filters.append(
            SupplierStaff.search_phone == search_phone
        )

    # البحث السريع باسم المستخدم أو الهاتف
    staff = (
        SupplierStaff.query
        .filter(or_(*filters))
        .first()
    )

    if staff:
        return staff

    # ========================================================
    # البحث بالبريد الإلكتروني
    # البريد مشفر في قاعدة البيانات
    # ========================================================

    if "@" in identifier:

        # لا نستطيع استخدام:
        # SupplierStaff.email == identifier
        #
        # لأن email Property مشفرة.
        #
        # لذلك نحصل على الموظفين ثم نقارن القيمة المفكوكة.

        all_staff = (
            SupplierStaff.query
            .filter(
                SupplierStaff.status == "active"
            )
            .all()
        )

        identifier_lower = identifier.lower()

        for candidate in all_staff:

            try:
                candidate_email = candidate.email

                if (
                    candidate_email
                    and candidate_email.strip().lower()
                    == identifier_lower
                ):
                    return candidate

            except Exception as exc:
                current_app.logger.warning(
                    "تعذر قراءة بريد الموظف ID=%s: %s",
                    getattr(candidate, "id", None),
                    exc,
                )

    return None


# ============================================================
# GET / POST
# ============================================================

@bp.route(
    "/login",
    methods=["GET", "POST"],
)
def login():

    # ========================================================
    # إذا كان المستخدم مسجلًا مسبقًا
    # ========================================================

    if current_user.is_authenticated:

        return redirect(
            url_for(
                "suppliers_dashboard.dashboard"
            )
        )

    # ========================================================
    # GET
    # ========================================================

    if request.method == "GET":

        try:
            return render_template(
                "suppliers_auth_portal/login.html"
            )

        except Exception as exc:

            current_app.logger.exception(
                "❌ خطأ أثناء تحميل صفحة تسجيل دخول الموردين: %s",
                exc,
            )

            # لا نخفي الخطأ الحقيقي في سجل الخادم
            # لكن لا نعرض تفاصيله للمستخدم.

            return (
                "حدث خطأ أثناء تحميل صفحة تسجيل الدخول",
                500,
            )

    # ========================================================
    # POST
    # ========================================================

    try:

        # ----------------------------------------------------
        # قراءة البيانات
        # ----------------------------------------------------

        data = get_request_data()

        identifier = str(
            data.get("identifier", "")
        ).strip()

        password = data.get(
            "password",
            "",
        )

        user_type = str(
            data.get(
                "user_type",
                "supplier",
            )
        ).strip().lower()

        remember_me = parse_bool(
            data.get(
                "remember_me",
                False,
            )
        )

        # ----------------------------------------------------
        # التحقق الأساسي
        # ----------------------------------------------------

        if not identifier or not password:

            return jsonify({
                "success": False,
                "message": "يرجى إدخال اسم المستخدم أو الهاتف أو البريد وكلمة المرور",
            }), 400

        # ----------------------------------------------------
        # التحقق من نوع المستخدم
        # ----------------------------------------------------

        if user_type not in {
            "supplier",
            "employee",
        }:

            return jsonify({
                "success": False,
                "message": "نوع المستخدم غير مدعوم",
            }), 400

        # ----------------------------------------------------
        # البحث عن الحساب
        # ----------------------------------------------------

        user = None

        if user_type == "supplier":

            user = find_supplier(
                identifier
            )

        elif user_type == "employee":

            user = find_staff(
                identifier
            )

        # ----------------------------------------------------
        # الحساب غير موجود
        # ----------------------------------------------------

        if not user:

            current_app.logger.warning(
                "⚠️ محاولة دخول فاشلة - الحساب غير موجود | "
                "type=%s | identifier=%s",
                user_type,
                identifier,
            )

            return jsonify({
                "success": False,
                "message": "بيانات الدخول غير صحيحة",
            }), 401

        # ----------------------------------------------------
        # التحقق من حالة الحساب
        # ----------------------------------------------------

        status = (
            getattr(user, "status", None)
            or ""
        ).strip().lower()

        if status != "active":

            status_messages = {
                "inactive": "الحساب غير نشط",
                "suspended": "تم تعليق الحساب",
                "blocked": "تم حظر الحساب",
                "pending": "الحساب قيد المراجعة",
            }

            message = status_messages.get(
                status,
                f"الحساب {status or 'غير متاح'}",
            )

            current_app.logger.warning(
                "⚠️ محاولة دخول لحساب غير نشط | "
                "id=%s | type=%s | status=%s",
                getattr(user, "id", None),
                user_type,
                status,
            )

            return jsonify({
                "success": False,
                "message": message,
            }), 403

        # ----------------------------------------------------
        # التحقق من كلمة المرور
        # ----------------------------------------------------

        try:

            password_valid = user.check_password(
                password
            )

        except Exception as exc:

            current_app.logger.exception(
                "❌ خطأ أثناء فحص كلمة مرور المستخدم ID=%s: %s",
                getattr(user, "id", None),
                exc,
            )

            return jsonify({
                "success": False,
                "message": "تعذر التحقق من بيانات الدخول",
            }), 500

        if not password_valid:

            current_app.logger.warning(
                "⚠️ كلمة مرور خاطئة | "
                "id=%s | type=%s | username=%s",
                getattr(user, "id", None),
                user_type,
                getattr(user, "username", None),
            )

            return jsonify({
                "success": False,
                "message": "بيانات الدخول غير صحيحة",
            }), 401

        # ====================================================
        # تسجيل الدخول عبر Flask-Login
        # ====================================================

        login_user(
            user,
            remember=remember_me,
        )

        # ----------------------------------------------------
        # حفظ نوع الحساب في Session
        # ----------------------------------------------------

        session["supplier_auth_user_type"] = user_type

        session["supplier_auth_user_id"] = user.id

        # ----------------------------------------------------
        # إذا كان موظفًا، نحفظ supplier_id
        # ----------------------------------------------------

        if user_type == "employee":

            session["supplier_id"] = user.supplier_id

            session["staff_id"] = user.id

            session["staff_role"] = user.role

        else:

            session["supplier_id"] = user.id

            session.pop(
                "staff_id",
                None,
            )

            session.pop(
                "staff_role",
                None,
            )

        # ----------------------------------------------------
        # تحديث آخر تسجيل دخول
        # ----------------------------------------------------

        user.last_login = datetime.utcnow()

        db.session.commit()

        # ====================================================
        # تحديد وجهة الدخول
        # ====================================================

        redirect_url = get_redirect_url()

        current_app.logger.info(
            "✅ تسجيل دخول ناجح | "
            "id=%s | username=%s | type=%s",
            user.id,
            user.username,
            user_type,
        )

        # ====================================================
        # الاستجابة
        # ====================================================

        return jsonify({
            "success": True,
            "message": "تم تسجيل الدخول بنجاح",
            "redirect_url": redirect_url,
            "user": {
                "id": user.id,
                "username": user.username,
                "user_type": user_type,
                "status": user.status,
            },
        }), 200

    # ========================================================
    # أخطاء SQLAlchemy
    # ========================================================

    except SQLAlchemyError as exc:

        db.session.rollback()

        current_app.logger.exception(
            "❌ خطأ قاعدة البيانات أثناء تسجيل الدخول: %s",
            exc,
        )

        return jsonify({
            "success": False,
            "message": "حدث خطأ في قاعدة البيانات",
        }), 500

    # ========================================================
    # الأخطاء العامة
    # ========================================================

    except Exception as exc:

        db.session.rollback()

        current_app.logger.exception(
            "❌ خطأ غير متوقع في تسجيل الدخول: %s",
            exc,
        )

        return jsonify({
            "success": False,
            "message": "حدث خطأ داخلي في الخادم",
        }), 500


# ============================================================
# تسجيل الخروج
# ============================================================

@bp.route(
    "/logout",
    methods=["GET", "POST"],
)
@login_required
def logout():

    try:

        username = getattr(
            current_user,
            "username",
            None,
        )

        logout_user()

        # تنظيف بيانات بوابة المورد
        session.pop(
            "supplier_auth_user_type",
            None,
        )

        session.pop(
            "supplier_auth_user_id",
            None,
        )

        session.pop(
            "supplier_id",
            None,
        )

        session.pop(
            "staff_id",
            None,
        )

        session.pop(
            "staff_role",
            None,
        )

        # يمكن تنظيف باقي الجلسة أيضًا
        # إذا كانت هذه الجلسة خاصة ببوابة المورد فقط.
        #
        # لا نستخدم session.clear()
        # حتى لا نمسح بيانات جلسات أخرى قد يحتاجها النظام.

        flash(
            "تم تسجيل الخروج بنجاح",
            "success",
        )

        current_app.logger.info(
            "✅ تسجيل خروج ناجح | username=%s",
            username,
        )

        return redirect(
            url_for(
                "auth_login.login"
            )
        )

    except Exception as exc:

        current_app.logger.exception(
            "❌ خطأ أثناء تسجيل الخروج: %s",
            exc,
        )

        return redirect(
            url_for(
                "auth_login.login"
            )
        )


# ============================================================
# حماية الصفحات - 401
# ============================================================

@bp.errorhandler(401)
def unauthorized_error(error):

    if request.is_json:

        return jsonify({
            "success": False,
            "message": "يرجى تسجيل الدخول أولاً",
        }), 401

    flash(
        "يرجى تسجيل الدخول للوصول إلى هذه الصفحة",
        "warning",
    )

    return redirect(
        url_for(
            "auth_login.login"
        )
    )


# ============================================================
# حماية الصفحات - 403
# ============================================================

@bp.errorhandler(403)
def forbidden_error(error):

    if request.is_json:

        return jsonify({
            "success": False,
            "message": "لا تملك صلاحية للوصول إلى هذه الصفحة",
        }), 403

    flash(
        "لا تملك صلاحية للوصول إلى هذه الصفحة",
        "danger",
    )

    return redirect(
        url_for(
            "auth_login.login"
        )
    )
```
