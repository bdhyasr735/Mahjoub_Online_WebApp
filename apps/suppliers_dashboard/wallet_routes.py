# coding: utf-8
# 📂 apps/suppliers_dashboard/routes/wallet_routes.py

import os
import re
import traceback
from flask import Blueprint, render_template, abort, session, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user

from apps.models import db, Supplier, SupplierWallet
from apps.models.wallet_db import WalletTransaction
from apps.data.yemen_banks import YEMEN_BANKS, BANKS_LIST

# تعريف الـ Blueprint لمسارات المحفظة
wallet_bp = Blueprint(
    'suppliers_wallet',
    __name__,
    template_folder='templates'
)


def get_supplier_context():
    """دالة مساعدة لجلب المورد والمحفظة المرتبطة بحسابه بأمان"""
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
    """إضافة بنك جديد إلى قائمة البنوك المحلية"""
    try:
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'اسم البنك مطلوب'}), 400
        
        if name in BANKS_LIST:
            return jsonify({'success': False, 'message': 'هذا البنك موجود بالفعل'}), 400
        
        file_path = os.path.join('apps', 'data', 'yemen_banks.py')
        
        if os.path.exists(file_path):
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
                
                YEMEN_BANKS.append({'id': new_id, 'name': name, 'icon': 'fa-building'})
                BANKS_LIST.append(name)
                
                return jsonify({'success': True, 'name': name, 'id': new_id})
        
        return jsonify({'success': False, 'message': 'تعذر كتابة التعديل في ملف البنوك'}), 500
        
    except Exception as e:
        print(f"❌ خطأ في add_bank: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# ✅ صفحة السحب (مع الجلب والتعبئة التلقائية لبيانات الحساب)
# ============================================================
@wallet_bp.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    """صفحة ومعالجة طلبات السحب من المحفظة (عملة SAR)"""
    try:
        supplier = get_supplier_context()
        if not supplier:
            flash('❌ يرجى تسجيل الدخول أولاً', 'danger')
            return redirect(url_for('suppliers_auth.login'))
        
        wallet = supplier.wallet
        if not wallet:
            flash('❌ لا توجد محفظة مرتبطة بحسابك', 'danger')
            return redirect(url_for('suppliers_dashboard.dashboard'))

        profile = getattr(supplier, 'supplier_profile', None)
        
        if request.method == 'POST':
            try:
                amount = float(request.form.get('amount', 0))
                
                # جلب البيانات من الموديل/البروفايل كبديل آمن في حال عدم إرسالها من الواجهة
                bank_name = request.form.get('bank_name', '').strip() or getattr(profile, 'bank_name', '') or ''
                bank_account = request.form.get('bank_account', '').strip() or getattr(profile, 'bank_account', '') or ''
                account_holder = (
                    request.form.get('account_holder_name', '').strip() or 
                    getattr(profile, 'account_holder_name', None) or 
                    getattr(supplier, 'trade_name', '') or 
                    getattr(supplier, 'name', '')
                )
                
                # التحقق من المبلغ
                if amount <= 0:
                    flash('❌ المبلغ يجب أن يكون أكبر من صفر', 'danger')
                    return redirect(url_for('suppliers_wallet.withdraw'))
                
                if amount < 10:
                    flash('❌ الحد الأدنى للسحب هو 10 ريال سعودي', 'danger')
                    return redirect(url_for('suppliers_wallet.withdraw'))
                
                balance = float(getattr(wallet, 'balance_sar', 0.0) or 0.0)
                if amount > balance:
                    flash(f'❌ الرصيد غير كافٍ. الرصيد الحالي: {balance:,.2f} SAR', 'danger')
                    return redirect(url_for('suppliers_wallet.withdraw'))
                
                # تحديث بيانات البنك في البروفايل تلقائياً إذا أرسلت قيم جديدة
                if profile:
                    if request.form.get('bank_name'):
                        profile.bank_name = bank_name
                    if request.form.get('bank_account'):
                        profile.bank_account = bank_account
                    if request.form.get('account_holder_name') and hasattr(profile, 'account_holder_name'):
                        profile.account_holder_name = account_holder

                # تحديث إجمالي المسحوبات للمحفظة
                if hasattr(wallet, 'total_withdrawn'):
                    wallet.total_withdrawn = float(getattr(wallet, 'total_withdrawn', 0.0) or 0.0) + amount

                # إنشاء حركة مالية جديدة متوافقة مع WalletTransaction
                transaction = WalletTransaction(
                    wallet_id=wallet.id,
                    owner_type='supplier',
                    owner_id=supplier.id,
                    trans_type='withdrawal',
                    source_type='manual',
                    amount=amount,
                    currency='SAR',
                    description=f"طلب سحب أرباح - البنك: {bank_name or 'غير محدد'} | الحساب: {bank_account or 'غير محدد'} | المستفيد: {account_holder}",
                    created_by=current_user.id
                )
                
                db.session.add(transaction)
                db.session.commit()
                
                flash(f'✅ تم تقديم طلب سحب بمبلغ {amount:,.2f} SAR بنجاح برقم سند #{transaction.voucher_number or transaction.id}', 'success')
                return redirect(url_for('suppliers_wallet.wallet'))
                
            except ValueError:
                flash('❌ قيمة المبلغ المدخلة غير صحيحة', 'danger')
                return redirect(url_for('suppliers_wallet.withdraw'))
            except Exception as e:
                db.session.rollback()
                print(f"❌ خطأ في معالجة السحب: {e}")
                flash('❌ حدث خطأ أثناء معالجة طلب السحب، يرجى المحاولة لاحقاً', 'danger')
                return redirect(url_for('suppliers_wallet.withdraw'))
        
        # حساب إجمالي طلبات السحب المعلقة لعرضها في الصفحة
        total_pending_payouts = 0.0
        try:
            pending_txs = WalletTransaction.query.filter_by(
                wallet_id=wallet.id,
                trans_type='withdrawal'
            ).all()
            total_pending_payouts = sum(float(tx.amount or 0.0) for tx in pending_txs)
        except Exception as e:
            print(f"⚠️ تعذر حساب طلبات السحب المعلقة: {e}")

        return render_template(
            'suppliers/withdraw.html',
            supplier=supplier,
            profile=profile,
            wallet=wallet,
            banks=YEMEN_BANKS,
            total_pending_payouts=total_pending_payouts
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
    """صفحة تفاصيل المحفظة وعرض سجل المعاملات"""
    try:
        supplier = get_supplier_context()
        if not supplier:
            flash('❌ يرجى تسجيل الدخول أولاً', 'danger')
            return redirect(url_for('suppliers_auth.login'))
        
        wallet = supplier.wallet
        if not wallet:
            flash('❌ لا توجد محفظة مرتبطة بحسابك', 'danger')
            return redirect(url_for('suppliers_dashboard.dashboard'))
        
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
