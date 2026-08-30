# coding: utf-8
# 📂 apps/suppliers_dashboard/dashboard_routes.py

from flask import Blueprint, render_template, session, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from datetime import datetime, timedelta
import traceback

from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.wallet_db import SupplierWallet
from apps.models.orders_db import Order
from apps.models.order_items_db import OrderItem
from apps.models.product_db import Product

# ✅ تعريف الـ Blueprint
suppliers_dashboard_bp = Blueprint(
    'suppliers_dashboard',
    __name__,
    template_folder='templates'
)


def get_supplier_context():
    """جلب بيانات المورد والمحفظة مع التحقق الشامل من الصلاحية ونوع الجلسة"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff', 'supplier_staff']:
            return None

        if user_type in ['staff', 'supplier_staff']:
            supplier_id = getattr(current_user, 'supplier_id', None)
        else:
            supplier_id = getattr(current_user, 'id', None)

        if not supplier_id:
            return None

        supplier = db.session.get(Supplier, supplier_id)
        if not supplier:
            return None

        # جلب المحفظة وربطها بنفس الكائن
        wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
        supplier.wallet = wallet

        return supplier

    except Exception as e:
        print(f"❌ خطأ في get_supplier_context: {e}")
        return None


@suppliers_dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    لوحة تحكم المورد – عرض إحصائيات حقيقية وتفاعلية
    """
    try:
        # ✅ 1. جلب المورد
        supplier = get_supplier_context()
        if not supplier:
            flash('❌ يرجى تسجيل الدخول أولاً', 'danger')
            # ✅ التصحيح: استخدام الـ endpoint الصحيح
            return redirect(url_for('auth_login.login'))

        # ✅ 2. جلب المحفظة أو إنشاؤها تلقائياً إن لم تكن موجودة
        wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
        if not wallet:
            wallet = SupplierWallet(
                supplier_id=supplier.id,
                wallet_code=f"MAH-WEL{supplier.id}",
                balance_sar=0.0,
                balance_pending=0.0
            )
            db.session.add(wallet)
            db.session.commit()

        # ✅ 3. إحصائيات الطلبات
        total_orders = Order.query.filter_by(supplier_id=supplier.id).count()
        pending_orders = Order.query.filter_by(
            supplier_id=supplier.id,
            status='pending'
        ).count()
        completed_orders = Order.query.filter_by(
            supplier_id=supplier.id,
            status='completed'
        ).count()
        cancelled_orders = Order.query.filter_by(
            supplier_id=supplier.id,
            status='cancelled'
        ).count()

        # ✅ 4. إجمالي المبيعات (من عناصر الطلبات المكتملة)
        total_sales = db.session.query(
            func.sum(OrderItem.price * OrderItem.quantity)
        ).join(Order, Order.id == OrderItem.order_id)\
         .filter(
             Order.supplier_id == supplier.id,
             Order.status == 'completed'
         ).scalar() or 0.0

        # ✅ 5. مبيعات اليوم والأمس والأسبوع
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)

        sales_today = db.session.query(
            func.sum(OrderItem.price * OrderItem.quantity)
        ).join(Order, Order.id == OrderItem.order_id)\
         .filter(
             Order.supplier_id == supplier.id,
             Order.status == 'completed',
             func.date(Order.created_at) == today
         ).scalar() or 0.0

        sales_yesterday = db.session.query(
            func.sum(OrderItem.price * OrderItem.quantity)
        ).join(Order, Order.id == OrderItem.order_id)\
         .filter(
             Order.supplier_id == supplier.id,
             Order.status == 'completed',
             func.date(Order.created_at) == yesterday
         ).scalar() or 0.0

        sales_week = db.session.query(
            func.sum(OrderItem.price * OrderItem.quantity)
        ).join(Order, Order.id == OrderItem.order_id)\
         .filter(
             Order.supplier_id == supplier.id,
             Order.status == 'completed',
             func.date(Order.created_at) >= week_ago
         ).scalar() or 0.0

        # حساب نسبة التغيير اليومي
        sales_change_percent = 0
        if sales_yesterday > 0:
            sales_change_percent = ((sales_today - sales_yesterday) / sales_yesterday) * 100

        # ✅ 6. عدد المنتجات النشطة
        try:
            from apps.models.product_db import Product
            active_products = Product.query.filter(
                Product.supplier_id == supplier.id,
                Product.status == 'active'
            ).count() if hasattr(Product, 'status') else Product.query.filter_by(supplier_id=supplier.id).count()
        except:
            active_products = 0

        # ✅ 7. أحدث 5 طلبات
        recent_orders = Order.query.filter_by(
            supplier_id=supplier.id
        ).order_by(
            Order.created_at.desc()
        ).limit(5).all()

        # ✅ 8. مبيعات الشهر الحالي (للشريط البياني)
        current_month = datetime.now().month
        current_year = datetime.now().year

        monthly_sales = db.session.query(
            func.extract('day', Order.created_at).label('day'),
            func.sum(OrderItem.price * OrderItem.quantity).label('total')
        ).join(Order, Order.id == OrderItem.order_id)\
         .filter(
             Order.supplier_id == supplier.id,
             Order.status == 'completed',
             extract('month', Order.created_at) == current_month,
             extract('year', Order.created_at) == current_year
         ).group_by(
             func.extract('day', Order.created_at)
         ).order_by(
             func.extract('day', Order.created_at)
         ).all()

        chart_days = [str(int(record.day)) for record in monthly_sales]
        chart_values = [float(record.total) for record in monthly_sales]

        # ✅ 9. أحدث 3 طلبات معلقة
        quick_orders = Order.query.filter_by(
            supplier_id=supplier.id,
            status='pending'
        ).order_by(
            Order.created_at.desc()
        ).limit(3).all()

        # ✅ 10. تقييمات المورد
        try:
            from apps.models.review_db import Review
            avg_rating = db.session.query(
                func.avg(Review.rating)
            ).filter_by(
                supplier_id=supplier.id
            ).scalar() or 0.0
            total_reviews = Review.query.filter_by(supplier_id=supplier.id).count()
        except Exception:
            avg_rating = 0.0
            total_reviews = 0

        # ✅ 11. إشعارات المورد الآمنة
        notifications = []
        if pending_orders > 0:
            notifications.append({
                'type': 'warning',
                'title': f'📦 {pending_orders} طلب قيد التنفيذ',
                'message': 'تأكد من تجهيز الطلبات في أسرع وقت',
                'link': '/supplier/orders'
            })

        if wallet and wallet.balance_sar < 100:
            notifications.append({
                'type': 'danger',
                'title': f'⚠️ رصيد منخفض: {wallet.balance_sar:.2f} SAR',
                'message': 'يرجى شحن المحفظة لتجنب توقف الخدمات',
                'link': '/supplier/wallet'
            })

        # ✅ 12. عرض القالب
        return render_template(
            'suppliers/dashboard.html',
            supplier=supplier,
            wallet=wallet,
            total_orders=total_orders,
            pending_orders=pending_orders,
            pending_orders_count=pending_orders,
            completed_orders=completed_orders,
            cancelled_orders=cancelled_orders,
            total_sales=total_sales,
            sales_today=sales_today,
            sales_yesterday=sales_yesterday,
            sales_week=sales_week,
            sales_change_percent=sales_change_percent,
            active_products=active_products,
            avg_rating=avg_rating,
            total_reviews=total_reviews,
            chart_days=chart_days,
            chart_values=chart_values,
            recent_orders=recent_orders,
            quick_orders=quick_orders,
            notifications=notifications
        )

    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ خطأ في dashboard: {error_details}")
        flash('❌ حدث خطأ تقني في عرض لوحة التحكم', 'danger')
        # ✅ التصحيح: استخدام الـ endpoint الصحيح
        return redirect(url_for('auth_login.login'))


# ============================================================
# ✅ API لجلب البيانات اللحظية (AJAX)
# ============================================================

@suppliers_dashboard_bp.route('/api/dashboard-stats', methods=['GET'])
@login_required
def api_dashboard_stats():
    """API لجلب إحصائيات محدثة للوحة التحكم"""
    try:
        supplier = get_supplier_context()
        if not supplier:
            return jsonify({'error': 'المورد غير موجود'}), 404

        total_orders = Order.query.filter_by(supplier_id=supplier.id).count()
        pending_orders = Order.query.filter_by(
            supplier_id=supplier.id,
            status='pending'
        ).count()

        total_sales = db.session.query(
            func.sum(OrderItem.price * OrderItem.quantity)
        ).join(Order, Order.id == OrderItem.order_id)\
         .filter(
             Order.supplier_id == supplier.id,
             Order.status == 'completed'
         ).scalar() or 0.0

        wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()

        return jsonify({
            'success': True,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'total_sales': float(total_sales),
            'balance_sar': float(wallet.balance_sar) if wallet else 0.0,
            'balance_pending': float(wallet.balance_pending) if wallet else 0.0
        })

    except Exception as e:
        print(f"❌ خطأ في api_dashboard_stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# ✅ API المساعد الذكي (AI Assistant)
# ============================================================

@suppliers_dashboard_bp.route('/api/ask-ai', methods=['POST'])
@login_required
def api_ask_ai():
    """معالجة استفسارات المورد عبر المساعد الذكي"""
    try:
        supplier = get_supplier_context()
        if not supplier:
            return jsonify({'success': False, 'error': 'غير مسموح'}), 403

        data = request.get_json() or {}
        question = data.get('question', '').strip()

        if not question:
            return jsonify({'success': False, 'answer': 'يرجى كتابة سؤال صحيح.'}), 400

        answer_text = (
            f"أهلاً بك في متجر **{supplier.trade_name or 'المورد'}**.\n"
            f"لقد تلقيت استفسارك حول: ({question}).\n"
            f"متجرك يعمل بكفاءة ونحن مستعدون دائماً لدعمك."
        )

        return jsonify({
            'success': True,
            'answer': answer_text
        })

    except Exception as e:
        print(f"❌ خطأ في api_ask_ai: {e}")
        return jsonify({'success': False, 'answer': '⚠️ حدث خطأ تقني أثناء معالجة السؤال.'}), 500
