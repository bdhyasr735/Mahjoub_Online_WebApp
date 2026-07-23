# coding: utf-8
# 📂 apps/suppliers_product/add_product_routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for, session, abort
from flask_login import login_required, current_user
from apps.models.supplier_db import Supplier
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.extensions import db
from apps.services.product_sync_service import ProductSyncService
import os
import traceback
import base64
from io import BytesIO
from PIL import Image

# ✅ استيراد الـ Blueprint من registry.py
from apps.suppliers_product.registry import suppliers_product_bp

# ✅ تعريف Blueprint منفصل للإضافة
add_product_bp = Blueprint(
    'add_product_bp',
    __name__,
    template_folder='templates'
)


def compress_image(image_data, max_size=(800, 800), quality=50):
    """
    ضغط الصورة وتقليل حجمها
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


@add_product_bp.route('/add-product', methods=['GET'])
@login_required
def add_product():
    """صفحة إضافة منتج جديد للمورد"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            abort(403)
        
        if user_type == 'staff':
            supplier_id = current_user.supplier_id
        else:
            supplier_id = current_user.id
        
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            abort(404)
        
        return render_template(
            'suppliers/add_product.html',
            supplier=supplier
        )
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ خطأ في add_product: {error_details}")
        flash('❌ حدث خطأ في تحميل الصفحة', 'danger')
        return redirect(url_for('suppliers_product_bp.products'))


@add_product_bp.route('/add-product', methods=['POST'])
@login_required
def save_product():
    """حفظ منتج جديد للمورد"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            abort(403)
        
        if user_type == 'staff':
            supplier_id = current_user.supplier_id
        else:
            supplier_id = current_user.id
        
        # ✅ جلب البيانات من النموذج
        name = request.form.get('name', '').strip()
        cost_price = request.form.get('cost_price', '').strip()
        description = request.form.get('description', '').strip()
        image = request.files.get('image')
        
        # ✅ التحقق من البيانات
        if not name:
            flash('⚠️ اسم المنتج مطلوب', 'danger')
            return redirect(url_for('add_product_bp.add_product'))
        
        if not cost_price or float(cost_price) <= 0:
            flash('⚠️ سعر التكلفة يجب أن يكون أكبر من 0', 'danger')
            return redirect(url_for('add_product_bp.add_product'))
        
        if not image:
            flash('⚠️ صورة المنتج مطلوبة', 'danger')
            return redirect(url_for('add_product_bp.add_product'))
        
        # ✅ قراءة الصورة وضغطها
        image_data = image.read()
        compressed_data = compress_image(image_data, max_size=(800, 800), quality=50)
        
        # ✅ رفع المنتج إلى Qumra
        sync_service = ProductSyncService()
        
        # ✅ رفع الصورة إلى مكتبة قمرة (بدلاً من base64)
        image_url = sync_service.upload_image(compressed_data, image.filename)
        
        if not image_url:
            flash('❌ فشل رفع الصورة إلى قمرة', 'danger')
            return redirect(url_for('add_product_bp.add_product'))
        
        # ✅ إنشاء المنتج مع رابط الصورة
        product_data = {
            'title': name,
            'price': float(cost_price),
            'quantity': 0,
            'supplier_id': str(supplier_id),
            'images': [image_url],  # ✅ رابط الصورة من قمرة
            'description': description
        }
        
        result = sync_service.create_product(product_data)
        
        if result.get('success'):
            # ✅ حفظ الربط في قاعدة البيانات المحلية
            mapping = ProductSupplierMapping(
                product_qid=result['qid'],
                supplier_id=supplier_id,
                status='active'
            )
            db.session.add(mapping)
            db.session.commit()
            
            flash('✅ تم إضافة المنتج بنجاح، سيراجعه فريق الإدارة', 'success')
            return redirect(url_for('suppliers_product_bp.products'))
        else:
            flash(f'❌ فشل إضافة المنتج: {result.get("message", "خطأ غير معروف")}', 'danger')
            return redirect(url_for('add_product_bp.add_product'))
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ خطأ في save_product: {error_details}")
        flash('❌ حدث خطأ أثناء إضافة المنتج', 'danger')
        return redirect(url_for('add_product_bp.add_product'))
