# coding: utf-8
# 📂 apps/suppliers_dashboard/routes/wallet_routes.py

from flask import Blueprint, render_template, abort, session, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
import traceback

from apps.models import db, Supplier, SupplierWallet
from apps.data.yemen_banks import YEMEN_BANKS, BANKS_LIST

# تعريف الـ Blueprint
wallet_bp = Blueprint(
    'suppliers_wallet',
    __name__,
    template_folder='templates'
)


def get_supplier_context():
    """دالة مساعدة لجلب المورد والمحفظة بأمان"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return None
            
        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id
        supplier = db.session.get(Supplier, supplier_id)
        
        if supplier:
            wallet = db.session.execute(
                db.select(SupplierWallet).filter_by(supplier_id=supplier.id)
            ).unique().scalar_one_or_none()
            supplier.wallet = wallet
            
        return supplier
    except Exception as e:
        print(f"❌ خطأ في get_supplier_context: {e}")
        return None


# ============================================================
# ✅ إضافة بنك جديد (للسحب)
# ============================================================
@wallet_bp.route('/add-bank', methods=['POST'])
@login_required
def add_bank():
    """إضافة بنك جديد من صفحة السحب"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'الاسم مطلوب'})
        
        if name in BANKS_LIST:
            return jsonify({'success': False, 'message': 'هذا البنك موجود بالفعل'})
        
        # ✅ إضافة إلى ملف البيانات
        import os
        import re
        file_path = os.path.join('apps', 'data', 'yemen_banks.py')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        existing_ids = re.findall(r"'id': '([^']+)'", content)
        new_id = f"bank_{len(existing_ids) + 1:03d}"
        
        new_entry = f"\n    {{'id': '{new_id}', 'name': '{name}', 'icon': 'fa-building'}},"
        
        lines = content.split('\n')
        insert_index = -1
        for i in range(len(lines) - 1, -1, -1):
            if ']' in lines[i]:
                insert_index = i
                break
        
        if insert_index > 0:
            lines.insert(insert_index, new_entry)
            new_content = '\n'.join(lines)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # ✅ تحديث القائمة في الذاكرة
            YEMEN_BANKS.append({'id': new_id, 'name': name, 'icon': 'fa-building'})
            BANKS_LIST.append(name)
            
            return jsonify({'success': True, 'name': name, 'id': new_id})
        
        return jsonify({'success': False, 'message': 'خطأ في إضافة البنك'})
        
    except Exception as e:
        print(f"❌ خطأ في add_bank: {e}")
        return jsonify({'success': False, 'message': str(e)})


# ============================================================
# ✅ صفحة السحب
# ============================================================
@wallet_bp.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    """صفحة السحب من المحفظة (عملة SAR فقط)"""
    try:
        supplier = get_supplier_context()
        if not supplier:
            flash('❌ يرجى تسجيل الدخول أولاً', 'danger')
            return redirect(url_for('suppliers_auth.login'))
        
        wallet = supplier.wallet
        if not wallet:
            flash('❌ لا توجد محفظة مرتبطة بحسابك', 'danger')
            return redirect(url_for('suppliers_dashboard.dashboard'))
        
        if request.method == 'POST':
            try:
                amount = float(request.form.get('amount', 0))
                bank_name = request.form.get('bank_name', '').strip()
                bank_account = request.form.get('bank_account', '').strip()
                
                # ✅ التحقق من المبلغ
                if amount <= 0:
                    flash('❌ المبلغ يجب أن يكون أكبر من صفر', 'danger')
                    return redirect(url_for('suppliers_wallet.withdraw'))
                
                if amount < 10:
                    flash('❌ الحد الأدنى للسحب هو 10 ريال سعودي', 'danger')
                    return redirect(url_for('suppliers_wallet.withdraw'))
                
                if amount > wallet.balance_sar:
                    flash(f'❌ الرصيد غير كافٍ. الرصيد الحالي: {wallet.balance_sar:.2f} SAR', 'danger')
                    return redirect(url_for('suppliers_wallet.withdraw'))
                
                # ✅ التحقق من الحساب البنكي
                if not bank_account:
                    flash('❌ يرجى إدخال رقم الحساب البنكي', 'danger')
                    return redirect(url_for('suppliers_wallet.withdraw'))
                
                # ✅ تحديث بيانات البنك في الملف الشخصي إذا لم تكن موجودة
                profile = getattr(supplier, 'supplier_profile', None)
                if profile:
                    if bank_name:
                        profile.bank_name = bank_name
                    if bank_account:
                        profile.bank_account = bank_account
                    db.session.commit()
                
                # ✅ تسجيل طلب السحب
                # هنا يمكن إضافة منطق إنشاء طلب سحب في جدول withdrawals
                
                flash(f'✅ تم تقديم طلب سحب بمبلغ {amount:.2f} SAR بنجاح', 'success')
                return redirect(url_for('suppliers_dashboard.dashboard'))
                
            except ValueError:
                flash('❌ قيمة المبلغ غير صحيحة', 'danger')
                return redirect(url_for('suppliers_wallet.withdraw'))
            except Exception as e:
                db.session.rollback()
                print(f"❌ خطأ في معالجة السحب: {e}")
                flash('❌ حدث خطأ أثناء معالجة طلب السحب', 'danger')
                return redirect(url_for('suppliers_wallet.withdraw'))
        
        # ✅ عرض الصفحة مع تمرير البنوك
        return render_template(
            'suppliers/withdraw.html',
            supplier=supplier,
            wallet=wallet,
            banks=YEMEN_BANKS
        )
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ خطأ في withdraw: {error_details}")
        flash('❌ حدث خطأ تقني، يرجى المحاولة لاحقاً', 'danger')
        return redirect(url_for('suppliers_dashboard.dashboard'))


# ============================================================
# ✅ صفحة تفاصيل المحفظة
# ============================================================
@wallet_bp.route('/wallet', methods=['GET'])
@login_required
def wallet():
    """صفحة تفاصيل المحفظة وعرض المعاملات"""
    try:
        supplier = get_supplier_context()
        if not supplier:
            flash('❌ يرجى تسجيل الدخول أولاً', 'danger')
            return redirect(url_for('suppliers_auth.login'))
        
        wallet = supplier.wallet
        if not wallet:
            flash('❌ لا توجد محفظة مرتبطة بحسابك', 'danger')
            return redirect(url_for('suppliers_dashboard.dashboard'))
        
        # ✅ جلب تاريخ المعاملات
        from apps.models.wallet_db import WalletTransaction
        transactions = WalletTransaction.query.filter_by(
            wallet_id=wallet.id
        ).order_by(WalletTransaction.created_at.desc()).limit(50).all()
        
        return render_template(
            'suppliers/wallet.html',
            supplier=supplier,
            wallet=wallet,
            transactions=transactions
        )
        
    except Exception as e:
        print(f"❌ خطأ في wallet: {e}")
        flash('❌ حدث خطأ في تحميل بيانات المحفظة', 'danger')
        return redirect(url_for('suppliers_dashboard.dashboard'))
