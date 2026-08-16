function openWalletAdjustmentModal(walletId, walletCode, supplierName, currentBalance) {
    document.getElementById('adjWalletId').value = walletId;
    document.getElementById('adjModalWalletCode').innerText = walletCode;
    document.getElementById('adjSupplierName').innerText = supplierName;
    document.getElementById('adjCurrentBalance').innerText = parseFloat(currentBalance).toLocaleString('en-US', { minimumFractionDigits: 2 }) + ' ريال';
    document.getElementById('adjAmount').value = '';
    document.getElementById('adjDescription').value = '';
    document.getElementById('walletAdjustmentModal').classList.remove('hidden');
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.add('hidden');
}

function openVoucherModal(voucherNumber, refCode, amount, typeLabel, date, description) {
    document.getElementById('modalVoucherNumber').innerText = voucherNumber;
    document.getElementById('modalVoucherAmount').innerText = parseFloat(amount).toLocaleString('en-US', { minimumFractionDigits: 2 }) + ' ريال';
    document.getElementById('modalVoucherType').innerText = typeLabel;
    document.getElementById('modalVoucherDate').innerText = date;
    document.getElementById('modalDescription').innerText = description;
    document.getElementById('voucherDetailModal').classList.remove('hidden');
}

async function handleWalletAdjustmentSubmit(event) {
    event.preventDefault();
    const submitBtn = document.getElementById('adjSubmitBtn');
    const walletId = document.getElementById('adjWalletId').value;
    const amount = document.getElementById('adjAmount').value;
    const entryType = document.querySelector('input[name="entry_type"]:checked').value;
    const description = document.getElementById('adjDescription').value;

    if (!amount || parseFloat(amount) <= 0) {
        Swal.fire({
            icon: 'warning',
            title: 'تنبيه',
            text: 'الرجاء إدخال مبلغ صحيح أكبر من الصفر',
            background: '#ffffff',
            color: '#1e293b',
            confirmButtonColor: '#4C1D95'
        });
        return;
    }

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="animate-spin">⏳</span> جاري قيد السند...';

    try {
        const response = await fetch(`/admin/suppliers-wallets/${walletId}/adjust`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
            body: JSON.stringify({ amount: parseFloat(amount), type: entryType, description: description })
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            closeModal('walletAdjustmentModal');
            openVoucherModal(
                data.voucher_code || 'VCH-NEW',
                data.ref_code || 'TXN-NEW',
                amount,
                entryType === 'credit' ? 'سند قبض / تغذية دائنة' : 'سند صرف / تسوية مدينة',
                new Date().toISOString().slice(0, 16).replace('T', ' '),
                description
            );
            // Toast notification for success
            Swal.fire({
                icon: 'success',
                title: 'تم بنجاح!',
                text: data.message || 'تم قيد الحركة المالية بنجاح.',
                timer: 3000,
                showConfirmButton: false,
                toast: true,
                position: 'top-end',
                background: '#ffffff',
                color: '#1e293b',
                iconColor: '#10b981'
            });
        } else {
            Swal.fire({
                icon: 'error',
                title: 'فشل',
                text: data.message || 'حدث خطأ غير معروف',
                background: '#ffffff',
                color: '#1e293b',
                confirmButtonColor: '#4C1D95'
            });
        }
    } catch (error) {
        console.error('Adjustment Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'خطأ',
            text: 'حدث خطأ في الاتصال بالخادم.',
            background: '#ffffff',
            color: '#1e293b'
        });
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg> اعتماد وقيد السند فوراً';
    }
}

function confirmWalletStatusToggle(walletId, supplierName, currentStatus, endpointUrl) {
    const isFreezing = currentStatus === 'active';
    const actionText = isFreezing ? 'تجميد' : 'تنشيط وفك حظر';

    // Light theme settings
    const bgColor = '#ffffff';
    const textColor = '#1e293b';

    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: `تأكيد ${actionText} محفظة المورد`,
            html: `
                <div class="text-right space-y-3 mt-2" style="text-align: right; direction: rtl;">
                    <p class="text-sm font-medium text-gray-700">هل أنت متأكد من رغبتك في <strong>${actionText}</strong> محفظة المورد: <strong class="text-amber-600">${supplierName}</strong>؟</p>
                    <p class="text-xs text-gray-500">${isFreezing ? 'سيتم إيقاف عمليات السحب والتحويلات البنكية فوراً.' : 'سيتم تمكين المورد من طلبات السحب والمعاملات فوراً.'}</p>
                    <div class="mt-4">
                        <label class="block text-xs font-bold text-gray-700 mb-1 text-right">سبب الإجراء (للتوثيق المحاسبي):</label>
                        <input id="swal-freeze-reason" class="swal2-input w-full border border-gray-300 rounded-lg p-2 text-sm" placeholder="اكتب سبب الإجراء..." style="width: 100%; background-color: #f9fafb; color: #1e293b;">
                    </div>
                </div>
            `,
            icon: isFreezing ? 'warning' : 'question',
            showCancelButton: true,
            confirmButtonColor: isFreezing ? '#e11d48' : '#10b981',
            cancelButtonColor: '#9ca3af',
            confirmButtonText: `نعم، قم بـ ${actionText} الآن`,
            cancelButtonText: 'إلغاء',
            background: bgColor,
            color: textColor,
            preConfirm: () => {
                const reason = document.getElementById('swal-freeze-reason').value;
                return { reason: reason || 'إجراء إداري دوري' };
            }
        }).then(async (result) => {
            if (result.isConfirmed) {
                try {
                    const response = await fetch(endpointUrl, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
                        body: JSON.stringify({ reason: result.value.reason })
                    });
                    const data = await response.json();
                    if (response.ok && data.status === 'success') {
                        // Toast notification for success
                        Swal.fire({
                            icon: 'success',
                            title: 'تم بنجاح!',
                            text: data.message || 'تم تحديث حالة المحفظة بنجاح',
                            timer: 2500,
                            showConfirmButton: false,
                            toast: true,
                            position: 'top-end',
                            background: '#ffffff',
                            color: '#1e293b',
                            iconColor: '#10b981'
                        }).then(() => {
                            window.location.reload();
                        });
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'خطأ',
                            text: 'فشل تحديث الحالة',
                            background: '#ffffff',
                            color: '#1e293b'
                        });
                    }
                } catch (e) {
                    Swal.fire({
                        icon: 'error',
                        title: 'خطأ',
                        text: 'فشل تحديث الحالة',
                        background: '#ffffff',
                        color: '#1e293b'
                    });
                }
            }
        });
    } else {
        if (confirm(`هل أنت متأكد من ${actionText} محفظة ${supplierName}؟`)) {
            fetch(endpointUrl, { method: 'POST', headers: { 'Content-Type': 'application/json' } })
                .then(r => r.json())
                .then(() => window.location.reload())
                .catch(() => alert('فشلت العملية'));
        }
    }
}
