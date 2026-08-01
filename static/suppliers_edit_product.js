// 📂 apps/suppliers_product/static/suppliers/js/suppliers_edit_product.js

document.addEventListener('DOMContentLoaded', function() {
    const editForm = document.getElementById('productEditForm');
    
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitBtn = document.getElementById('submitBtn');
            const originalBtnText = submitBtn ? submitBtn.innerHTML : '';
            
            // تعطيل زر الحفظ أثناء المعالجة لمنع الإرسال المزدوج
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> جاري الحفظ...';
            }
            
            const formData = new FormData(editForm);
            const actionUrl = editForm.action;
            
            fetch(actionUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (typeof showToast === 'function') {
                        showToast('✅ ' + (data.message || 'تم تحديث بيانات المنتج بنجاح'), 'success');
                    } else {
                        alert(data.message || 'تم تحديث بيانات المنتج بنجاح');
                    }
                    
                    // إعادة تحميل الصفحة بعد ثغرة زمنية بسيطة لرؤية التحديثات
                    setTimeout(() => {
                        window.location.reload();
                    }, 1200);
                } else {
                    if (typeof showToast === 'function') {
                        showToast('❌ ' + (data.message || 'حدث خطأ أثناء حفظ التغييرات'), 'danger');
                    } else {
                        alert(data.message || 'حدث خطأ أثناء حفظ التغييرات');
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (typeof showToast === 'function') {
                    showToast('❌ حدث خطأ غير متوقع في الاتصال بالخادم', 'danger');
                } else {
                    alert('حدث خطأ غير متوقع في الاتصال بالخادم');
                }
            })
            .finally(() => {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalBtnText;
                }
            });
        });
    }
});
