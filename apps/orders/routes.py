# coding: utf-8
# 📂 apps/orders/routes.py - إدارة الطلبات السيادية والموردين (النسخة النهائية الشاملة والمطابقة لعام 2026)

from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required
from apps.models.orders_db import ProcessedOrder, db
from apps.models.supplier_db import Supplier  # استيراد نموذج الموردين المحليين للربط
from apps.api.sync_engine import SyncEngine
import logging

orders_blueprint = Blueprint('orders', __name__, template_folder='templates')
logger = logging.getLogger(__name__)

@orders_blueprint.route('/dashboard', methods=['GET'])
@login_required
def orders_dashboard():
    """عرض قائمة الطلبات المطابقة للبوابة مع الفلاتر والموردين المحليين"""
    page = request.args.get('page', 1, type=int)
    
    # جلب الطلبات مرتبة من الأحدث تنازلياً حسب التاريخ المجلوب بأمان
    pagination = ProcessedOrder.query.order_by(ProcessedOrder.created_at_api.desc()).paginate(page=page, per_page=10)
    
    # جلب قائمة الموردين المحليين من قاعدتك لعرضهم في القائمة المنسدلة بالجدول
    suppliers = Supplier.query.all()
    
    return render_template('admin/orders_dashboard.html', pagination=pagination, suppliers=suppliers)

@orders_blueprint.route('/sync-all', methods=['POST'])
@login_required
def sync_all():
    """مزامنة شاملة وموسعة للبيانات والتفاصيل عبر محرك المزامنة المستقر"""
    try:
        success = SyncEngine.fetch_and_sync_order()
        if success:
            flash("✅ تمت مزامنة الطلبات وتحديث البيانات التفصيلية بنجاح.", "success")
        else:
            flash("⚠️ فشلت المزامنة. يرجى التحقق من سجلات النظام (Logs).", "danger")
    except Exception as e:
        logger.error(f"❌ خطأ في المزامنة: {e}")
        flash(f"حدث خطأ تقني أثناء الاتصال بالخادم: {str(e)}", "danger")
    return redirect(url_for('orders.orders_dashboard'))

@orders_blueprint.route('/update-supplier/<order_id>', methods=['POST'])
@login_required
def update_supplier(order_id):
    """استقبال طلبات AJAX لتحديث وحفظ المورد المحلي للطلب فورا بدون ريفريش"""
    # البحث المرن باستخدام المعرف المحلي أو معرف طلب الخارجي لضمان عدم الفشل
    order = ProcessedOrder.query.filter((ProcessedOrder.id == order_id) | (ProcessedOrder.order_id == order_id)).first()
    if not order:
        return jsonify({'status': 'error', 'message': 'الطلب غير موجود محلياً'}), 404
        
    data = request.get_json() or {}
    supplier_id = data.get('supplier_id')
    
    try:
        # إذا كانت القيمة فارغة يتم تعيينها كـ None في القاعدة
        order.supplier_id = int(supplier_id) if supplier_id else None
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'تم ربط المورد بالطلب بنجاح'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ خطأ أثناء ربط المورد بالطلب {order_id}: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@orders_blueprint.route('/update-order-field/<order_id>', methods=['POST'])
@login_required
def update_order_field(order_id):
    """استقبال تحديثات فورية وديناميكية لحالة الطلب، المالية، أو الشحن عبر AJAX ومزامنتها"""
    order = ProcessedOrder.query.filter((ProcessedOrder.id == order_id) | (ProcessedOrder.order_id == order_id)).first()
    if not order:
        return jsonify({'status': 'error', 'message': 'الطلب غير موجود محلياً'}), 404
        
    data = request.get_json() or {}
    field = data.get('field')       # 'order_status', 'financial_status', 'fulfillment_status'
    value = data.get('value')       # القيمة الجديدة المحددة من القائمة المنسدلة
    
    if field not in ['order_status', 'financial_status', 'fulfillment_status']:
        return jsonify({'status': 'error', 'message': 'اسم الحقل المستهدف غير صالح'}), 400

    try:
        # 1. تحديث قاعدة البيانات المحلية فوراً لإبقاء اللوحة سريعة الاستجابة
        setattr(order, field, value)
        db.session.commit()
        
        # 2. إرسال التحديث المتزامن إلى خادم الـ API بناءً على خريطة الحالات المقبولة
        try:
            # السيرفر الخارجي يقبل حقل الحالات الموحد (status) عبر الميثود المحدثة
            if field == 'order_status':
                SyncEngine.update_order_status(order.id, value)
            elif field == 'fulfillment_status' and value == 'fulfilled':
                SyncEngine.mark_as_fulfilled(order.id)
            elif field == 'financial_status' and value == 'paid':
                # إذا تم تعليمها كمدفوعة محلياً، نرفع إشارة التسليم المالي والجسدي للسيرفر
                SyncEngine.update_order_status(order.id, 'delivered')
        except Exception as api_err:
            logger.error(f"⚠️ تم الحفظ محلياً ولكن فشل التحديث الفوري في السيرفر: {api_err}")
            return jsonify({
                'status': 'warning', 
                'message': 'تم الحفظ محلياً، لكن فشل التحديث في السيرفر الخارجي. يرجى مراجعة الصلاحيات والربط.'
            })

        return jsonify({'status': 'success', 'message': 'تم تحديث حالة الطلب بنجاح محلياً ومزامنته'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ خطأ تقني أثناء معالجة تحديث حقل {field} للطلب {order_id}: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@orders_blueprint.route('/process/<order_id>', methods=['GET', 'POST'])
@login_required
def process_order(order_id):
    """عرض تفاصيل المعالجة العميقة للطلب والتسوية المالية عند النقر على الرقم"""
    order = ProcessedOrder.query.filter((ProcessedOrder.id == order_id) | (ProcessedOrder.order_id == order_id)).first()
    if not order:
        flash("الطلب المستهدف غير موجود بقاعدة البيانات المحلية.", "danger")
        return redirect(url_for('orders.orders_dashboard'))
    
    # في حالة طلب التسوية المالية الفورية محلياً (POST)
    if request.method == 'POST':
        try:
            # تحديث الحالة المالية المستقلة الجديدة
            order.financial_status = 'paid'
            order.order_status = 'confirmed'
            db.session.commit()
            
            # مزامنة الحالة المدفوعة والمؤكدة مع السيرفر الخارجي عبر المحرك الموحد
            SyncEngine.update_order_status(order.id, 'delivered')
            
            flash(f"✅ تمت التسوية المالية الكاملة وتأكيد الطلب {order_id} محلياً ومزامنتها كـ delivered.", "success")
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ خطأ في التسوية: {e}")
            flash("فشل إتمام العملية المالية.", "danger")
        return redirect(url_for('orders.orders_dashboard'))
        
    # في حالة النقر فقط لاستعراض البيانات والتفاصيل (GET)
    return render_template('admin/order_details.html', order=order)

@orders_blueprint.route('/download-invoice/<order_id>', methods=['GET'])
@login_required
def download_invoice(order_id):
    """توليد أو تحميل الفاتورة الخاصة بالطلب المستهدف"""
    order = ProcessedOrder.query.filter((ProcessedOrder.id == order_id) | (ProcessedOrder.order_id == order_id)).first()
    if not order:
        flash("الطلب غير موجود لإصدار الفاتورة.", "danger")
        return redirect(url_for('orders.orders_dashboard'))
        
    flash(f"📄 جاري تجهيز وتحميل فاتورة الطلب {order_id[:8]}...", "primary")
    return redirect(url_for('orders.orders_dashboard'))

@orders_blueprint.route('/cancel/<order_id>', methods=['POST'])
@login_required
def cancel_order_route(order_id):
    """إرسال أمر إلغاء الطلب إلى السيرفر تزامناً مع النظام المحلي"""
    order = ProcessedOrder.query.filter((ProcessedOrder.id == order_id) | (ProcessedOrder.order_id == order_id)).first()
    result = SyncEngine.cancel_order(order_id)
    
    # فحص صارم للرد للتأكد من عدم وجود أخطاء من بوابة GraphQL
    if result and isinstance(result, dict) and 'errors' not in result:
        if order:
            order.order_status = 'cancelled'  # تحديث حقل الحالة الثلاثية محلياً
            order.financial_status = 'unpaid'
            order.fulfillment_status = 'unfulfilled'
            db.session.commit()
        flash(f"تم إلغاء الطلب {order_id} وتحديثه محلياً بنجاح.", "info")
    else:
        flash("فشل إلغاء الطلب، يرجى مراجعة صلاحيات التوكن والـ Schema وطبيعة الاتصال.", "danger")
    return redirect(url_for('orders.orders_dashboard'))

@orders_blueprint.route('/fulfill/<order_id>', methods=['POST'])
@login_required
def fulfill_order_route(order_id):
    """تحديث حالة الشحن والتجهيز الفوري للطلب"""
    order = ProcessedOrder.query.filter((ProcessedOrder.id == order_id) | (ProcessedOrder.order_id == order_id)).first()
    result = SyncEngine.mark_as_fulfilled(order_id)
    
    if result and isinstance(result, dict) and 'errors' not in result:
        if order:
            order.fulfillment_status = 'fulfilled'  # تحديث حالة التجهيز محلياً فور نجاح طلب السيرفر
            order.order_status = 'delivered'       # السيرفر يحول الحالة تلقائياً عند التوصيل لـ delivered
            db.session.commit()
        flash(f"تم تحديث الطلب {order_id} إلى 'مشحون' ومجهز بنجاح.", "success")
    else:
        flash("فشل تحديث الشحن في السيرفر الخارجي.", "danger")
    return redirect(url_for('orders.orders_dashboard'))

@orders_blueprint.route('/update-status/<order_id>', methods=['POST'])
@login_required
def update_status_route(order_id):
    """تحديث يدوي مخصص للحالة الصادرة من واجهة التحكم (تأمين إضافي للمسارات القديمة)"""
    new_status = request.form.get('status')
    if not new_status:
        flash("حالة غير صالحة أو حقل فارغ.", "warning")
        return redirect(url_for('orders.orders_dashboard'))
        
    order = ProcessedOrder.query.filter((ProcessedOrder.id == order_id) | (ProcessedOrder.order_id == order_id)).first()
    result = SyncEngine.update_order_status(order_id, new_status)
    
    if result and isinstance(result, dict) and 'errors' not in result:
        if order:
            order.order_status = new_status  # التحديث محلياً لضمان التطابق المستمر
            if new_status == 'delivered':
                order.financial_status = 'paid'
                order.fulfillment_status = 'fulfilled'
            db.session.commit()
        flash(f"تم تحديث حالة الطلب {order_id} بنجاح في السيرفر والمستودع المحلي.", "success")
    else:
        flash("فشل التحديث المتزامن بسبب عدم مطابقة الحالات المسموحة.", "danger")
    return redirect(url_for('orders.orders_dashboard'))
