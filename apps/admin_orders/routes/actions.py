# coding: utf-8
# 📂 apps/admin_orders/routes/actions.py

import traceback
from flask import Blueprint, request, jsonify, render_template, abort, flash, redirect, url_for
from flask_login import login_required, current_user
from apps.extensions import db
from apps.services import services
from apps.models.orders_db import Order
from apps.models.order_items_db import OrderItem
from apps.models.supplier_db import Supplier

# تعريف الـ Blueprint الخاص بالإجراءات بنفس التسمية
actions_bp = Blueprint('admin_order_actions', __name__, url_prefix='/admin/orders')

# خريطة لتحديث العنوان بناءً على الكود
STATUS_TITLES_MAP = {
    'pending': 'قيد الانتظار',
    'processing': 'قيد التجهيز',
    'shipped': 'تم الشحن',
    'delivered': 'تم التسليم',
    'completed': 'مكتمل',
    'cancelled': 'ملغي',
    'refunded': 'مسترجع'
}

def _parse_id(val):
    """دالة مساعدة لتحويل المعرف إلى رقم صحيح إن كان رقمياً، أو إبقائه كما هو"""
    if val is not None and str(val).isdigit():
        return int(val)
    return val


@actions_bp.route('/<string:order_id>', methods=['GET'], endpoint='view_order_details')
@login_required
def view_order_details(order_id):
    """عرض تفاصيل الطلب الكاملة مع المنتجات والفاتورة"""
    try:
        if session.get('user_type') != 'admin':
            flash('❌ هذا القسم مخصص للإدارة فقط', 'danger')
            return redirect(url_for('admin_dashboard_bp.dashboard'))

        parsed_order_id = _parse_id(order_id)
        order = db.session.get(Order, parsed_order_id)
        
        if not order:
            flash('❌ الطلب غير موجود في قاعدة البيانات المحلية', 'danger')
            return redirect(url_for('admin_orders_bp.list_admin_orders'))

        # جلب قائمة الموردين لإمكانية ربطهم بالعناصر
        suppliers = Supplier.query.all()

        # 🔍 توثيق عملية الاستعراض
        try:
            services.audit.log(
                action="VIEW_ORDER_DETAILS",
                target_type="Order",
                target_id=str(order_id),
                details=f"تم استعراض تفاصيل الطلب رقم {order_id}"
            )
        except Exception:
            pass

        return render_template('admin/admin_order_detail.html', order=order, suppliers=suppliers)

    except Exception as e:
        current_app_logger_err = traceback.format_exc()
        return f"حدث خطأ أثناء عرض تفاصيل الطلب: {str(e)}", 500


@actions_bp.route('/<string:order_id>/invoice', methods=['GET'], endpoint='print_order_invoice')
@login_required
def print_order_invoice(order_id):
    """عرض صفحة الفاتورة الخاصة بالطلب مهيئة للطباعة المباشرة"""
    try:
        parsed_order_id = _parse_id(order_id)
        order = db.session.get(Order, parsed_order_id)
        
        if not order:
            abort(404, description="الطلب غير موجود لطباعة الفاتورة")

        try:
            services.audit.log(
                action="PRINT_INVOICE",
                target_type="Order",
                target_id=str(order_id),
                details=f"تم طباعة/عرض فاتورة الطلب رقم {order_id}"
            )
        except Exception:
            pass

        return render_template('admin/admin_order_invoice.html', order=order)

    except Exception as e:
        return f"حدث خطأ أثناء إنشاء الفاتورة: {str(e)}", 500


@actions_bp.route('/<string:order_id>/status', methods=['POST'])
@login_required
def update_status(order_id):
    """تحديث حالة الطلب وإرجاع الحقول الحقيقية المحدثة"""
    try:
        data = request.get_json(silent=True)
        if not data or 'status' not in data:
            return jsonify({'success': False, 'message': 'بيانات غير صالحة أو مفقودة'}), 400

        new_status_code = data.get('status')
        parsed_order_id = _parse_id(order_id)
        order = db.session.get(Order, parsed_order_id)
        
        if not order:
            return jsonify({'success': False, 'message': 'الطلب غير موجود'}), 404

        old_status = getattr(order, 'status_code', 'unknown')
        new_status_title = STATUS_TITLES_MAP.get(new_status_code, 'حالة غير معروفة')
        
        order.status_code = new_status_code
        order.status_title = new_status_title
        
        db.session.commit()

        try:
            services.audit.log(
                action="UPDATE_ORDER_STATUS",
                target_type="Order",
                target_id=str(order_id),
                details=f"تم تغيير حالة الطلب من ({old_status}) إلى ({new_status_code})"
            )
        except Exception:
            pass

        return jsonify({
            'success': True, 
            'message': 'تم تحديث حالة الطلب بنجاح',
            'order': {
                'id': order.id,
                'status_code': order.status_code,
                'status_title': order.status_title
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ داخلي: {str(e)}'}), 500


@actions_bp.route('/<string:order_id>/payment-status', methods=['POST'])
@login_required
def update_payment_status(order_id):
    """تحديث حالة الدفع (isPaid) وإرجاع الحقول الحقيقية"""
    try:
        data = request.get_json(silent=True)
        if not data or 'isPaid' not in data:
            return jsonify({'success': False, 'message': 'بيانات غير صالحة أو مفقودة'}), 400

        is_paid = bool(data.get('isPaid'))
        parsed_order_id = _parse_id(order_id)
        order = db.session.get(Order, parsed_order_id)
        
        if not order:
            return jsonify({'success': False, 'message': 'الطلب غير موجود'}), 404

        order.is_paid = is_paid
        db.session.commit()

        try:
            services.audit.log(
                action="UPDATE_PAYMENT_STATUS",
                target_type="Order",
                target_id=str(order_id),
                details=f"تم تحديث حالة الدفع للطلب لتصبح: {'مدفوع' if is_paid else 'غير مدفوع'}"
            )
        except Exception:
            pass

        return jsonify({
            'success': True, 
            'message': 'تم تحديث حالة الدفع بنجاح',
            'order': {
                'id': order.id,
                'is_paid': order.is_paid
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ داخلي: {str(e)}'}), 500


@actions_bp.route('/<string:order_id>/items/supplier', methods=['POST'])
@login_required
def update_item_supplier(order_id):
    """تحديث المورد لعنصر داخل الطلب"""
    try:
        data = request.get_json(silent=True)
        if not data or 'item_id' not in data:
            return jsonify({'success': False, 'message': 'بيانات غير صالحة أو مفقودة'}), 400

        item_id = _parse_id(data.get('item_id'))
        supplier_id = _parse_id(data.get('supplier_id'))
        parsed_order_id = _parse_id(order_id)

        order = db.session.get(Order, parsed_order_id)
        if not order:
            return jsonify({'success': False, 'message': 'الطلب غير موجود'}), 404

        item = OrderItem.query.filter_by(id=item_id, order_id=parsed_order_id).first()
        if not item:
            return jsonify({'success': False, 'message': 'العنصر غير موجود في هذا الطلب'}), 404

        item.supplier_id = supplier_id if supplier_id else None
        db.session.commit()

        try:
            services.audit.log(
                action="UPDATE_ITEM_SUPPLIER",
                target_type="Order",
                target_id=str(order_id),
                details=f"تم تحديث مورد العنصر (ID: {item_id}) إلى المورد (ID: {supplier_id})"
            )
        except Exception:
            pass

        return jsonify({
            'success': True, 
            'message': 'تم تحديث مورد العنصر بنجاح',
            'item': {
                'id': item.id,
                'supplier_id': item.supplier_id
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ داخلي: {str(e)}'}), 500


@actions_bp.route('/delete/<string:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    """حذف طلب من لوحة الإدارة محلياً وعبر خدمة GraphQL إذا لزم الأمر"""
    try:
        parsed_order_id = _parse_id(order_id)
        order = db.session.get(Order, parsed_order_id)
        if not order:
            return jsonify({'success': False, 'message': 'الطلب غير موجود'}), 404
            
        try:
            if hasattr(services, 'orders') and services.orders:
                services.orders.delete_order(str(order_id))
        except Exception:
            pass

        db.session.delete(order)
        db.session.commit()

        try:
            services.audit.log(
                action="DELETE_ORDER",
                target_type="Order",
                target_id=str(order_id),
                details="تم حذف الطلب نهائياً من لوحة الإدارة"
            )
        except Exception:
            pass

        return jsonify({'success': True, 'message': 'تم حذف الطلب بنجاح'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'فشل حذف الطلب: {str(e)}'}), 500
