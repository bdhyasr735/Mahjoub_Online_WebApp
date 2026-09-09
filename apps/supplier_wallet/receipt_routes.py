except ImportError:
    flash('مكتبة PDF غير مثبتة، يرجى تثبيت weasyprint', 'warning')
    return redirect(url_for('receipt_bp.view_receipt', transaction_id=transaction_id))

except Exception as e:   # ← السطر 222
    print(f"⚠️ [PDF Export Error]: {str(e)}")   # ← السطر 223 (منزاح ✅)
    traceback.print_exc()   # ← منزاح ✅
    flash('حدث خطأ أثناء تصدير الـ PDF', 'danger')   # ← منزاح ✅
    return redirect(url_for('receipt_bp.view_receipt', transaction_id=transaction_id))   # ← منزاح ✅
