# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/receipt_routes.py

import traceback
from decimal import Decimal
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash, jsonify, send_file
from flask_login import login_required, current_user

from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.models.supplier_db import Supplier
from apps.supplier_wallet.utils import get_current_supplier_id
from apps.supplier_wallet.routes import get_sidebar_modules  # ✅ استيراد الدالة المسؤولة عن القائمة الجانبية

# إنشاء Blueprint فرعي للإيصالات
receipt_bp = Blueprint('receipt_bp', __name__, url_prefix='/supplier/wallet/receipt')


# =========================================================
# 📄 مسار عرض الإيصال
# =========================================================

@receipt_bp.route('/<string:transaction_id>')
@login_required
def view_receipt(transaction_id):
    """عرض إيصال المعاملة المالية."""
    supplier_id = get_current_supplier_id()
    if not supplier_id and hasattr(current_user, 'id'):
        supplier_id = current_user.id

    if not supplier_id:
        flash('يرجى تسجيل الدخول أولاً', 'warning')
        return redirect(url_for('supplier_wallet_bp.transactions_redirect'))

    transaction = WalletTransaction.query.filter_by(id=transaction_id).first()
    if not transaction:
        flash('المعاملة غير موجودة', 'danger')
        return redirect(url_for('supplier_wallet_bp.transactions_redirect'))

    wallet = SupplierWallet.query.filter_by(id=transaction.wallet_id).first()
    if not wallet or wallet.supplier_id != supplier_id:
        flash('غير مصرح لك بعرض هذا الإيصال', 'danger')
        return redirect(url_for('supplier_wallet_bp.transactions_redirect'))

    supplier = Supplier.query.filter_by(id=supplier_id).first()
    balance = wallet.balance if wallet.balance else Decimal('0.0')
    
    # ✅ جلب الموديولات للقائمة الجانبية
    modules = get_sidebar_modules()

    return render_template(
        'supplier_wallet/receipt.html',
        transaction=transaction,
        wallet=wallet,
        supplier=supplier,
        balance=balance,
        now=datetime.now(),
        supplier_modules=modules,      # ✅ تمرير القائمة الجانبية
        modules_registry=modules       # ✅ تمرير نسخة احتياطية
    )


# =========================================================
# 🖨️ مسار طباعة الإيصال
# =========================================================

@receipt_bp.route('/<string:transaction_id>/print')
@login_required
def print_receipt(transaction_id):
    """طباعة إيصال المعاملة."""
    supplier_id = get_current_supplier_id()
    if not supplier_id and hasattr(current_user, 'id'):
        supplier_id = current_user.id

    if not supplier_id:
        flash('يرجى تسجيل الدخول أولاً', 'warning')
        return redirect(url_for('supplier_wallet_bp.transactions_redirect'))

    transaction = WalletTransaction.query.filter_by(id=transaction_id).first()
    if not transaction:
        flash('المعاملة غير موجودة', 'danger')
        return redirect(url_for('supplier_wallet_bp.transactions_redirect'))

    wallet = SupplierWallet.query.filter_by(id=transaction.wallet_id).first()
    if not wallet or wallet.supplier_id != supplier_id:
        flash('غير مصرح لك بطباعة هذا الإيصال', 'danger')
        return redirect(url_for('supplier_wallet_bp.transactions_redirect'))

    supplier = Supplier.query.filter_by(id=supplier_id).first()
    balance = wallet.balance if wallet.balance else Decimal('0.0')

    # ✅ جلب الموديولات للقائمة الجانبية
    modules = get_sidebar_modules()

    return render_template(
        'supplier_wallet/print_receipt.html',
        transaction=transaction,
        wallet=wallet,
        supplier=supplier,
        balance=balance,
        now=datetime.now(),
        supplier_modules=modules,      # ✅ تمرير القائمة الجانبية
        modules_registry=modules       # ✅ تمرير نسخة احتياطية
    )


# =========================================================
# 📊 مسار تصدير الإيصال كـ PDF
# =========================================================

@receipt_bp.route('/<string:transaction_id>/pdf')
@login_required
def export_receipt_pdf(transaction_id):
    """تصدير الإيصال كملف PDF."""
    try:
        supplier_id = get_current_supplier_id()
        if not supplier_id and hasattr(current_user, 'id'):
            supplier_id = current_user.id

        if not supplier_id:
            return jsonify({'error': 'غير مصرح'}), 401

        transaction = WalletTransaction.query.filter_by(id=transaction_id).first()
        if not transaction:
            return jsonify({'error': 'المعاملة غير موجودة'}), 404

        wallet = SupplierWallet.query.filter_by(id=transaction.wallet_id).first()
        if not wallet or wallet.supplier_id != supplier_id:
            return jsonify({'error': 'غير مصرح'}), 403

        try:
            from weasyprint import HTML
            import tempfile
            import os

            supplier = Supplier.query.filter_by(id=supplier_id).first()
            balance = wallet.balance if wallet.balance else Decimal('0.0')

            html_content = render_template(
                'supplier_wallet/pdf_receipt.html',
                transaction=transaction,
                wallet=wallet,
                supplier=supplier,
                balance=balance,
                now=datetime.now()
            )

            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                pdf_path = tmp_file.name

            HTML(string=html_content).write_pdf(pdf_path)

            return send_file(
                pdf_path,
                as_attachment=True,
                download_name=f'إيصال_#{transaction.id}.pdf',
                mimetype='application/pdf'
            )

        except ImportError:
            flash('مكتبة PDF غير مثبتة، يرجى تثبيت weasyprint', 'warning')
            return redirect(url_for('receipt_bp.view_receipt', transaction_id=transaction_id))

        except Exception as e:
            print(f"⚠️ [PDF Export Error]: {str(e)}")
            traceback.print_exc()
            flash('حدث خطأ أثناء تصدير الـ PDF', 'danger')
            return redirect(url_for('receipt_bp.view_receipt', transaction_id=transaction_id))

    except Exception as e:
        print(f"⚠️ [PDF Export Error]: {str(e)}")
        traceback.print_exc()
        flash('حدث خطأ أثناء تصدير الـ PDF', 'danger')
        return redirect(url_for('supplier_wallet_bp.transactions_redirect'))


# =========================================================
# 📧 مسار إرسال الإيصال عبر البريد الإلكتروني
# =========================================================

@receipt_bp.route('/<string:transaction_id>/email', methods=['POST'])
@login_required
def email_receipt(transaction_id):
    """إرسال الإيصال عبر البريد الإلكتروني."""
    try:
        supplier_id = get_current_supplier_id()
        if not supplier_id and hasattr(current_user, 'id'):
            supplier_id = current_user.id

        if not supplier_id:
            return jsonify({'error': 'غير مصرح'}), 401

        transaction = WalletTransaction.query.filter_by(id=transaction_id).first()
        if not transaction:
            return jsonify({'error': 'المعاملة غير موجودة'}), 404

        wallet = SupplierWallet.query.filter_by(id=transaction.wallet_id).first()
        if not wallet or wallet.supplier_id != supplier_id:
            return jsonify({'error': 'غير مصرح'}), 403

        supplier = Supplier.query.filter_by(id=supplier_id).first()
        if not supplier or not supplier.email:
            return jsonify({'error': 'البريد الإلكتروني للمورد غير متوفر'}), 400

        subject = f'إيصال معاملة #{transaction.id}'
        body = f"""
مرحباً {supplier.trade_name or 'مورد'}،

نرفق لكم إيصال المعاملة المالية رقم #{transaction.id}.

المبلغ: {transaction.amount} ريال
النوع: {transaction.transaction_type}
التاريخ: {transaction.created_at.strftime('%Y-%m-%d %H:%M')}

شكراً لتعاملكم معنا.
"""

        try:
            from flask_mail import Message
            from apps.extensions import mail

            msg = Message(subject, sender=current_app.config.get('MAIL_DEFAULT_SENDER'), recipients=[supplier.email])
            msg.body = body

            try:
                from weasyprint import HTML
                import tempfile
                import os

                balance = wallet.balance if wallet.balance else Decimal('0.0')
                html_content = render_template(
                    'supplier_wallet/pdf_receipt.html',
                    transaction=transaction,
                    wallet=wallet,
                    supplier=supplier,
                    balance=balance,
                    now=datetime.now()
                )

                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                    pdf_path = tmp_file.name

                HTML(string=html_content).write_pdf(pdf_path)

                with open(pdf_path, 'rb') as f:
                    msg.attach(f'إيصال_#{transaction.id}.pdf', 'application/pdf', f.read())

                os.unlink(pdf_path)

            except ImportError:
                pass

            mail.send(msg)
            flash('تم إرسال الإيصال بنجاح إلى بريدك الإلكتروني', 'success')

        except ImportError:
            flash('خدمة البريد الإلكتروني غير متاحة', 'warning')
        except Exception as e:
            flash(f'فشل إرسال البريد الإلكتروني: {str(e)}', 'danger')

        return redirect(url_for('receipt_bp.view_receipt', transaction_id=transaction_id))

    except Exception as e:
        print(f"⚠️ [Email Receipt Error]: {str(e)}")
        traceback.print_exc()
        flash('حدث خطأ أثناء إرسال الإيصال', 'danger')
        return redirect(url_for('supplier_wallet_bp.transactions_redirect'))
