# coding: utf-8
# 📂 apps/suppliers_product/edit_product_routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for, session, abort
from flask_login import login_required, current_user
from apps.services.product_sync_service import ProductSyncService
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier_db import Supplier
from apps.extensions import db
import os
import traceback
import base64
from io import BytesIO
from PIL import Image

# ✅ استيراد الـ Blueprint من registry.py
from apps.suppliers_product.registry import suppliers_product_bp

# ✅ تعريف Blueprint منفصل للتعديل
edit_product_bp = Blueprint(
    'edit_product_bp',
    __name__,
    template_folder='templates'
)

# ✅ لا حاجة لـ GRAPHQL_TOKEN
# GRAPHQL_TOKEN = os.environ.get('QUMRA_API_KEY', 'YOUR_ADMIN_API_TOKEN')


def compress_image(image_data, max_size=(1200, 1200), quality=75):
    """
    ضغط الصورة وتقليل حجمها
    
    Args:
        image_data: بيانات الصورة (bytes)
        max_size: tuple (width, height) الحد الأقصى للأبعاد
        quality: جودة الصورة (1-100)
    
    Returns:
        bytes: بيانات الصورة المضغوطة
    """
    try:
        img = Image.open(BytesIO(image_data))
        
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue()
        
    except Exception as e:
        print(f"⚠️ خطأ في ضغط الصورة: {e}")
        return image_data


# ============================================================
# 🟣 مسار عرض صفحة تعديل المنتج
# ============================================================
@edit_product_bp.route('/edit-product/<qid>', methods=['GET'])
@login_required
def edit_product_page(qid):
    """عرض صفحة تعديل المنتج"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            abort(403)
        
        if user_type == 'staff':
            supplier_id = current_user.supplier_id
        else:
            supplier_id = current_user.id
        
        # ✅ التحقق من أن المنتج يخص هذا المورد
        mapping = ProductSupplierMapping.query.filter_by(
            product_qid=qid,
            supplier_id=supplier_id,
            status='active'
        ).first()
        
        if not mapping:
            abort(404)
        
        # ✅ جلب بيانات المنتج من Qumra (بدون token)
        sync_service = ProductSyncService()
        product = sync_service.fetch_product_by_qid(qid)
        
        if not product:
            abort(404)
        
        return render_template(
            'suppliers/edit_product.html',
            product=product,
            supplier=Supplier.query.get(supplier_id)
        )
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ خطأ في edit_product_page: {error_details}")
        flash('❌ حدث خطأ في تحميل صفحة التعديل', 'danger')
        return redirect(url_for('suppliers_product_bp.products'))


# ============================================================
# 🟣 مسار تحديث المنتج
# ============================================================
@edit_product_bp.route('/edit-product/<qid>', methods=['POST'])
@login_required
def update_product(qid):
    """تحديث بيانات المنتج"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            abort(403)
        
        if user_type == 'staff':
            supplier_id = current_user.supplier_id
        else:
            supplier_id = current_user.id
        
        # ✅ التحقق من أن المنتج يخص هذا المورد
        mapping = ProductSupplierMapping.query.filter_by(
            product_qid=qid,
            supplier_id=supplier_id,
            status='active'
        ).first()
        
        if not mapping:
            abort(404)
        
        # ✅ جلب البيانات من النموذج
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', '').strip()
        quantity = request.form.get('quantity', '').strip()
        image = request.files.get('image')
        
        # ✅ التحقق من البيانات
        if not name:
            flash('⚠️ اسم المنتج مطلوب', 'danger')
            return redirect(url_for('edit_product_bp.edit_product_page', qid=qid))
        
        # ✅ تحديث المنتج في Qumra (بدون token)
        sync_service = ProductSyncService()
        
        # ✅ تحويل الصورة إلى base64 إذا تم رفع صورة جديدة
        image_base64 = None
        if image:
            image_data = image.read()
            compressed_data = compress_image(image_data, max_size=(1200, 1200), quality=75)
            image_base64 = base64.b64encode(compressed_data).decode('utf-8')
            image_base64 = f"data:image/jpeg;base64,{image_base64}"
        
        product_data = {
            'title': name,
            'description': description,
            'price': float(price) if price else 0,
            'quantity': int(quantity) if quantity else 0
        }
        
        # ✅ إضافة الصورة إذا وجدت
        if image_base64:
            product_data['images'] = [image_base64]
        
        result = sync_service.update_product(qid, product_data)
        
        if result:
            flash('✅ تم تحديث المنتج بنجاح', 'success')
        else:
            flash('❌ فشل تحديث المنتج', 'danger')
            
        return redirect(url_for('suppliers_product_bp.products'))
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ خطأ في update_product: {error_details}")
        flash('❌ حدث خطأ أثناء تحديث المنتج', 'danger')
        return redirect(url_for('edit_product_bp.edit_product_page', qid=qid))
