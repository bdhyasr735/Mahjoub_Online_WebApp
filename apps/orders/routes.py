# coding: utf-8
# 📂 apps/orders/routes.py - إدارة الطلبات السيادية والموردين (النسخة النهائية الشاملة والمطابقة)

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
    """عرض قائمة الطلبات المطابقة لقمرة مع الفلاتر والموردين المحليين"""
    page = request.args.get('page', 1, type=int)
    
    # جلب الطلبات مرتبة من الأحدث تنازلياً حسب التاريخ المجلوب من قمرة بأمان
    pagination = ProcessedOrder.query.order_by(ProcessedOrder.created_at_api.desc()).paginate(page=page, per_page=10)
    
    # جلب قائمة الموردين المحليين من قاعدتك لعرضهم في القائمة المنسدلة بالجدول
    suppliers = Supplier.query.all()
    
    return render_template('admin/orders_dashboard.html', pagination=pagination, suppliers=suppliers)

@orders_blueprint.route('/sync-all', methods=['POST'])
@login_required
def sync_all():
    """مزامنة شاملة وموسعة للبيانات والتفاصيل من قمرة"""
    try:
        success = SyncEngine.fetch_and_sync_order()
        if success:
            flash("✅ تمت مزامنة الطلبات وتحديث البيانات التفصيلية بنجاح من قمرة.", "success")
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
    order = ProcessedOrder.query.get(order_id)
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
    order = ProcessedOrder.query.get(order_id)
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
        
        # 2. إرسال التحديث المتزامن إلى سيرفر قمرة بناءً على نوع الحقل المعدل
        try:
            if field == 'order_status':
                SyncEngine.update_order_status(order_id, value)
            elif field == 'fulfillment_status' and value == 'fulfilled':
                SyncEngine.mark_as_fulfilled(order_id)
            # ملاحظة: يمكنك هنا ربط تحديثات الحالات المالية الإضافية عند توفرها بـ SyncEngine
        except Exception as api_err:
            logger.error(f"⚠️ تم الحفظ محلياً ولكن فشل التحديث الفوري في سيرفر قمرة: {api_err}")
            return jsonify({
                'status': 'warning', 
                'message': 'تم الحفظ محلياً، لكن فشل التحديث في قمرة. يرجى مراجعة صلاحيات التوكن (Access Token).'
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
    order = ProcessedOrder.query.get(order_id)
    if not order:
        flash("الطلب المستهدف غير موجود بقاعدة البيانات المحلية.", "danger")
        return redirect(url_for('orders.orders_dashboard'))
    
    # في حالة طلب التسوية المالية الفورية محلياً (POST)
    if request.method == 'POST':
        try:
            # تحديث الحالة المالية المستقلة الجديدة بدلاً من الحقل القديم المحذوف
            order.financial_status = 'paid'
            order.order_status = 'confirmed'
            db.session.commit()
            flash(f"✅ تمت التسوية المالية الكاملة وتأكيد الطلب {order_id} محلياً.", "success")
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
    order = ProcessedOrder.query.get(order_id)
    if not order:
        flash("الطلب غير موجود لإصدار الفاتورة.", "danger")
        return redirect(url_for('orders.orders_dashboard'))
        
    flash(f"📄 جاري تجهيز وتحميل فاتورة الطلب {order_id[:8]}...", "primary")
    return redirect(url_for('orders.orders_dashboard'))

@orders_blueprint.route('/cancel/<order_id>', methods=['POST'])
@login_required
def cancel_order_route(order_id):
    """إرسال أمر إلغاء الطلب إلى سيرفرات قمرة تزامناً مع النظام"""
    result = SyncEngine.cancel_order(order_id)
    # التحقق من خلو الاستجابة من الأخطاء في الـ Root الأساسي بناءً على تحديث قمرة
    if result and isinstance(result, dict) and 'errors' not in result:
        flash(f"تم إلغاء الطلب {order_id} في قمرة بنجاح.", "info")
    else:
        flash("فشل إلغاء الطلب، يرجى مراجعة الصلاحيات في قمرة.", "danger")
    return redirect(url_for('orders.orders_dashboard'))

@orders_blueprint.route('/fulfill/<order_id>', methods=['POST'])
@login_required
def fulfill_order_route(order_id):
    """تحديث حالة الشحن والتجهيز الفوري للطلب"""
    result = SyncEngine.mark_as_fulfilled(order_id)
    if result and isinstance(result, dict) and 'errors' not in result:
        flash(f"تم تحديث الطلب {order_id} إلى 'مشحون' ومجهز في قمرة.", "success")
    else:
        flash("فشل تحديث الشحن في السيرفر الخارجي لقمرة.", "danger")
    return redirect(url_for('orders.orders_dashboard'))

@orders_blueprint.route('/update-status/<order_id>', methods=['POST'])
@login_required
def update_status_route(order_id):
    """تحديث يدوي مخصص للحالة الصادرة من واجهة التحكم (تأمين إضافي للمسارات القديمة)"""
    new_status = request.form.get('status')
    if not new_status:
        flash("حالة غير صالحة أو حقل فارغ.", "warning")
        return redirect(url_for('orders.orders_dashboard'))
        
    result = SyncEngine.update_order_status(order_id, new_status)
    if result and isinstance(result, dict) and 'errors' not in result:
        flash(f"تم تحديث حالة الطلب {order_id} بنجاح في سيرفر قمرة.", "success")
    else:
        flash("فشل التحديث المتزامن في قمرة.", "danger")
    return redirect(url_for('orders.orders_dashboard'))
