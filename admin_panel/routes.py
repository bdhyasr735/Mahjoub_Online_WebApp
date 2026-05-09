import os
from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import logout_user, login_required, current_user
from sqlalchemy import or_
from datetime import datetime
from functools import wraps
from werkzeug.utils import secure_filename

# الاستيراد من الهيكلية المعتمدة لترسانة محجوب أونلاين
from core.extensions import db 
from core.models.supplier import Supplier, SupplierStaff
from core.models.user import User

from . import admin_bp
from .auth import handle_admin_login

# محاولة استيراد نظام الأرشفة بأمان (لتجنب انهيار النظام إذا غاب الملف)
try:
    from core.utils.archive_manager import archive_sys
    HAS_ARCHIVE_SYSTEM = True
except ImportError:
    HAS_ARCHIVE_SYSTEM = False

# إعدادات رفع الملفات السيادية
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- 1. بروتوكول التحقق السيادي (Sovereign Auth) ---
def is_admin_sovereign():
    """ يضمن أن المؤسس (أو من يحمل رتبة Admin) فقط يمكنه الوصول. """
    return current_user.is_authenticated and getattr(current_user, 'role', '').lower() == 'admin'

def admin_api_required(f):
    """ تأمين الـ APIs لضمان أن الاستدعاءات تتم من داخل مركز القيادة فقط """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_sovereign():
            return jsonify({"status": "error", "message": "Access Denied: Sovereign Auth Required"}), 403
        return f(*args, **kwargs)
    return decorated_function

# --- 2. بوابة الدخول ---
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if is_admin_sovereign(): 
        return redirect(url_for('admin.admin_dashboard'))
    return handle_admin_login()

# --- 3. مركز القيادة الإحصائي (Dashboard) ---
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if not is_admin_sovereign():
        return redirect(url_for('admin.login'))
    
    try:
        stats = {
            'users_count': User.query.count() if User else 1,
            'suppliers_count': Supplier.query.count() if Supplier else 0,
            'now': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            from core.models.business import Order
            stats['orders_count'] = Order.query.count()
        except:
            stats['orders_count'] = 0

        return render_template('dashboard.html', **stats)
    except Exception as e:
        return render_template('dashboard.html', users_count=1, suppliers_count=0, orders_count=0, now="إيقاع النظام مستقر")

# --- 4. إدارة الموردين (عرض الواجهة الرئيسية للجدول) ---
@admin_bp.route('/manage-suppliers')
@login_required
def manage_suppliers():
    if not is_admin_sovereign():
        return redirect(url_for('admin.login'))
    return render_template('manage_suppliers.html')

# --- 5. إضافة وتعمد مورد جديد (مع ميزة الأرشفة الذكية وكشف الأخطاء) ---
@admin_bp.route('/add-supplier', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if not is_admin_sovereign(): 
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        try:
            if Supplier.query.filter_by(username=request.form.get('username')).first():
                return jsonify({'status': 'error', 'message': 'عذراً.. اسم المستخدم هذا مسجل مسبقاً'}), 400

            identity_path = None
            if 'identity_image' in request.files:
                file = request.files['identity_image']
                if file and file.filename != '' and allowed_file(file.filename):
                    upload_folder = os.path.join('static', 'uploads', 'suppliers', 'ids')
                    os.makedirs(upload_folder, exist_ok=True)
                    filename = secure_filename(f"ID_{request.form.get('username')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file.filename.rsplit('.', 1)[1].lower()}")
                    file.save(os.path.join(upload_folder, filename))
                    identity_path = f"uploads/suppliers/ids/{filename}"

            new_supplier = Supplier(
                username=request.form.get('username'),
                email=request.form.get('email'),
                owner_name=request.form.get('owner_name'),
                trade_name=request.form.get('trade_name'),
                activity_type=request.form.get('activity_type'),
                phone=request.form.get('phone'),
                identity_type=request.form.get('identity_type'),
                identity_image_url=identity_path,
                province=request.form.get('province'),
                district=request.form.get('district'),
                address_detail=request.form.get('address_detail'),
                bank_name=request.form.get('bank_name'),
                bank_acc=request.form.get('bank_acc'),
                tier=request.form.get('tier', 'مورد مبتدئ'),
                status=request.form.get('status', 'pending')
            )
            
            new_supplier.set_password(request.form.get('password', '123456'))
            db.session.add(new_supplier)
            db.session.flush() 
            new_supplier.mint_sovereign_id()
            
            # --- بروتوكول الأرشفة السيادية مع كشف الأخطاء (Debug) ---
            if HAS_ARCHIVE_SYSTEM:
                try:
                    archive_sys.archive_data_as_json(
                        data_dict=new_supplier.to_dict(),
                        filename=f"REGISTRY_{new_supplier.sovereign_id}",
                        entity_id=new_supplier.sovereign_id
                    )
                    print(f"✅ Archive Success: {new_supplier.sovereign_id}")
                except Exception as archive_err:
                    # طباعة الخطأ في الكونسول لمعرفة سبب فشل الرفع بعد حذف المجلدات
                    print(f"❌ ARCHIVE ERROR: {str(archive_err)}")

            db.session.commit()
            
            if is_ajax: 
                return jsonify({'status': 'success', 'message': f'تم تعميد المورد {new_supplier.trade_name} بنجاح برقم {new_supplier.sovereign_id}'})
            return redirect(url_for('admin.manage_suppliers'))
            
        except Exception as e:
            db.session.rollback()
            if is_ajax: return jsonify({'status': 'error', 'message': f"فشل البروتوكول: {str(e)}"}), 500
            flash(f"خطأ في النظام: {str(e)}", "danger")

    last_s = Supplier.query.order_by(Supplier.id.desc()).first()
    next_id = (last_s.id + 1) if last_s else 1
    return render_template('add_supplier.html', next_id=next_id)

# --- 6. محرك التحديث التلقائي ---
@admin_bp.route('/supplier/<int:supplier_id>/update_field', methods=['POST'])
@admin_api_required
def update_supplier_field(supplier_id):
    data = request.get_json()
    field_name = data.get('field')
    new_value = data.get('value')
    supplier = Supplier.query.get_or_404(supplier_id)
    
    allowed_fields = [
        'username', 'email', 'owner_name', 'trade_name', 'activity_type',
        'phone', 'province', 'district', 'address_detail', 'identity_type',
        'bank_name', 'bank_acc', 'balance_yer', 'balance_sar', 'balance_usd',
        'tier', 'status'
    ]
    
    if field_name not in allowed_fields:
        return jsonify({"status": "error", "message": "محاولة تعديل حقل محظور"}), 403

    try:
        if hasattr(supplier, field_name):
            if 'balance' in field_name:
                try:
                    new_value = float(new_value) if new_value else 0.0
                except ValueError:
                    return jsonify({"status": "error", "message": "يجب إدخال قيمة رقمية"}), 400
            
            setattr(supplier, field_name, new_value)
            db.session.commit()
            
            # أرشفة التعديل مع كشف الأخطاء
            if HAS_ARCHIVE_SYSTEM:
                try:
                    archive_sys.archive_data_as_json(
                        data_dict={"field": field_name, "value": new_value, "time": str(datetime.now())},
                        filename=f"UPDATE_{supplier.sovereign_id}_{field_name}",
                        entity_id=supplier.sovereign_id,
                        folder_name="Updates"
                    )
                except Exception as archive_err:
                    print(f"❌ UPDATE ARCHIVE ERROR: {str(archive_err)}")

            response_data = {"status": "success", "message": f"تم تحديث {field_name} بنجاح"}
            if field_name == 'status':
                response_data['new_color'] = supplier.get_status_color()
            return jsonify(response_data)
        return jsonify({"status": "error", "message": "الحقل غير موجود"}), 404
            
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

# --- 7. إنهاء الجلسة السيادية ---
@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("تم تأمين الخروج من مركز القيادة.", "info")
    return redirect(url_for('admin.login'))
