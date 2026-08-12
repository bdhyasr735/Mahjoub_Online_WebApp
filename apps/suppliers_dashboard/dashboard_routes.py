# coding: utf-8
# 📂 apps/suppliers_dashboard/dashboard_routes.py

from flask import Blueprint, render_template, session, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from datetime import datetime, timedelta
import traceback

from apps.models import db, Supplier, Order, OrderItem, SupplierWallet, Product

# ✅ تعريف الـ Blueprint بالاسم الصحيح
suppliers_dashboard_bp = Blueprint(
    'suppliers_dashboard',
    __name__,
    template_folder='templates'
)


def get_supplier_context():
    """جلب بيانات المورد والمحفظة مع التحقق من الصلاحية"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return None

        if user_type == 'staff':
            supplier_id = getattr(current_user, 'supplier_id', None)
        else:
            supplier_id = current_user.id

        if not supplier_id:
            return None

        supplier = db.session.get(Supplier, supplier_id)
        if not supplier:
            return None

        # جلب المحفظة
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
        # ✅ جلب المورد
        supplier = get_supplier_context()
        if not supplier:
            flash('❌ يرجى تسجيل الدخول أولاً', 'danger')
            return redirect(url_for('suppliers_auth.login'))

        # ✅ جلب المحفظة بشكل منفصل لضمان وجودها
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

        # ✅ ============================================================
        # ✅ 1. إحصائيات الطلبات
        # ✅ ============================================================
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

        # ✅ ============================================================
        # ✅ 2. إجمالي المبيعات (من عناصر الطلبات المكتملة)
        # ✅ ============================================================
        total_sales = db.session.query(
            func.sum(OrderItem.price * OrderItem.quantity)
        ).join(Order, Order.id == OrderItem.order_id)\
         .filter(
             Order.supplier_id == supplier.id,
             Order.status == 'completed'
         ).scalar() or 0.0

        # ✅ ============================================================
        # ✅ 3. مبيعات اليوم والأمس والأسبوع
        # ✅ ============================================================
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

        # ✅ حساب نسبة التغيير اليومي
        sales_change_percent = 0
        if sales_yesterday > 0:
            sales_change_percent = ((sales_today - sales_yesterday) / sales_yesterday) * 100

        # ✅ ============================================================
        # ✅ 4. عدد المنتجات النشطة
        # ✅ ============================================================
        active_products = Product.query.filter(
            Product.supplier_id == supplier.id,
            Product.status == 'active'
        ).count() if hasattr(Product, 'status') else Product.query.filter_by(supplier_id=supplier.id).count()

        # ✅ ============================================================
        # ✅ 5. آخر 5 طلبات (للجدول)
        # ✅ ============================================================
        recent_orders = Order.query.filter_by(
            supplier_id=supplier.id
        ).order_by(
            Order.created_at.desc()
        ).limit(5).all()

        # ✅ ============================================================
        # ✅ 6. مبيعات الشهر الحالي (للشريط البياني)
        # ✅ ============================================================
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

        # ✅ تحويل إلى قوائم للرسم البياني
        chart_days = [str(record.day) for record in monthly_sales]
        chart_values = [float(record.total) for record in monthly_sales]

        # ✅ ============================================================
        # ✅ 7. طلب سريع – أحدث 3 طلبات معلقة
        # ✅ ============================================================
        quick_orders = Order.query.filter_by(
            supplier_id=supplier.id,
            status='pending'
        ).order_by(
            Order.created_at.desc()
        ).limit(3).all()

        # ✅ ============================================================
        # ✅ 8. تقييمات المورد (إذا كان لديك نموذج Reviews)
        # ✅ ============================================================
        try:
            from apps.models.review_db import Review
            avg_rating = db.session.query(
                func.avg(Review.rating)
            ).filter_by(
                supplier_id=supplier.id
            ).scalar() or 0.0
            total_reviews = Review.query.filter_by(supplier_id=supplier.id).count()
        except:
            avg_rating = 0.0
            total_reviews = 0

        # ✅ ============================================================
        # ✅ 9. إشعارات (مهام أو تنبيهات)
        # ✅ ============================================================
        notifications = []

        # تنبيه: طلبات معلقة
        if pending_orders > 0:
            notifications.append({
                'type': 'warning',
                'title': f'📦 {pending_orders} طلب قيد التنفيذ',
                'message': 'تأكد من تجهيز الطلبات في أسرع وقت',
                'link': url_for('suppliers_orders.index')
            })

        # تنبيه: رصيد منخفض (افتراضي أقل من 100 ريال)
        if wallet and wallet.balance_sar < 100:
            notifications.append({
                'type': 'danger',
                'title': f'⚠️ رصيد منخفض: {wallet.balance_sar:.2f} SAR',
                'message': 'يرجى شحن المحفظة لتجنب توقف الخدمات',
                'link': url_for('suppliers_wallet.deposit')
            })

        # ✅ ============================================================
        # ✅ 10. عرض القالب
        # ✅ ============================================================
        return render_template(
            'suppliers/dashboard.html',
            supplier=supplier,
            wallet=wallet,
            # إحصائيات
            total_orders=total_orders,
            pending_orders=pending_orders,
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
            # البيانات للرسوم البيانية
            chart_days=chart_days,
            chart_values=chart_values,
            # القوائم
            recent_orders=recent_orders,
            quick_orders=quick_orders,
            notifications=notifications
        )

    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ خطأ في dashboard: {error_details}")

        flash('❌ حدث خطأ تقني، يرجى المحاولة لاحقاً', 'danger')
        return redirect(url_for('suppliers_dashboard.dashboard')), 500


# ============================================================
# ✅ API لجلب البيانات للحظية (للرسوم البيانية والتحديث)
# ============================================================

@suppliers_dashboard_bp.route('/api/dashboard-stats', methods=['GET'])
@login_required
def api_dashboard_stats():
    """
    API لجلب إحصائيات محدثة للوحة التحكم (للاستخدام مع AJAX)
    """
    try:
        supplier = get_supplier_context()
        if not supplier:
            return jsonify({'error': 'المورد غير موجود'}), 404

        # ✅ إحصائيات سريعة
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
