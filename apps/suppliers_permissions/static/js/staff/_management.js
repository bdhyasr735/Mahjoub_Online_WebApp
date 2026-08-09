// apps/supplier_permissions/static/js/staff_management.js

// 1. إعادة تعيين كلمة المرور
async function resetStaffPassword(staffId) {
    if (!confirm('هل أنت متأكد من رغبتك في إعادة تعيين كلمة المرور؟')) return;
    
    try {
        const response = await fetch(`/supplier_perms/staff/${staffId}/reset-password`, { method: 'POST' });
        if (response.ok) alert('تم إعادة تعيين كلمة المرور بنجاح');
        else alert('حدث خطأ أثناء إعادة التعيين');
    } catch (e) { console.error(e); }
}

// 2. تغيير حالة الحساب (تفعيل/إيقاف)
async function toggleStaffActive(staffId) {
    try {
        const response = await fetch(`/supplier_perms/staff/${staffId}/toggle-status`, { method: 'POST' });
        if (response.ok) {
            location.reload(); // إعادة تحميل الصفحة لتحديث أيقونة الحالة
        }
    } catch (e) { console.error(e); }
}

// 3. حذف الموظف
async function deleteStaff(staffId) {
    if (!confirm('هل أنت متأكد من حذف هذا الموظف نهائياً؟')) return;
    
    try {
        const response = await fetch(`/supplier_perms/staff/${staffId}/delete`, { method: 'POST' });
        if (response.ok) {
            document.getElementById(`staff-row-${staffId}`).remove();
        } else {
            alert('تعذر حذف الموظف');
        }
    } catch (e) { console.error(e); }
}

// 4. فتح مودال الصلاحيات (يتم استدعاؤه من الزر)
function openPermissionsModal(staffId, staffName) {
    // هنا تقوم بفتح المودال الخاص بك وتمرير البيانات إليه
    console.log("تعديل صلاحيات الموظف:", staffId);
    // مثال إذا كنت تستخدم Bootstrap:
    // const modal = new bootstrap.Modal(document.getElementById('permissionsModal'));
    // modal.show();
}
