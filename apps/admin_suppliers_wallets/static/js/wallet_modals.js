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
        alert('⚠️ الرجاء إدخال مبلغ صحيح أكبر من الصفر');
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
        } else {
            alert('❌ فشل تنفيذ العملية: ' + (data.message || 'خطأ غير معروف'));
        }
    } catch (error) {
        console.error('Adjustment Error:', error);
        alert('❌ حدث خطأ في الاتصال بالخادم.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg> اعتماد وقيد السند فوراً';
    }
}

function confirmWalletStatusToggle(walletId, supplierName, currentStatus, endpointUrl) {
    const isFreezing = currentStatus === 'active';
    const actionText = isFreezing ? 'تجميد' : 'تنشيط وفك حظر';
    const confirmButtonColor = isFreezing ? '#e11d48' : '#10b981';

    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: `تأكيد ${actionText} محفظة المورد`,
            html: `<div class="text-right text-xs text-slate-300 space-y-2 mt-2"><p>هل أنت متأكد من رغبتك في <strong>${actionText}</strong> محفظة المورد: <strong class="text-amber-600">${supplierName}</strong>؟</p><p class="text-slate-400">${isFreezing ? 'سيتم إيقاف عمليات السحب والتحويلات البنكية فوراً.' : 'سيتم تمكين المورد من طلبات السحب والمعاملات فوراً.'}</p><div class="mt-3"><label class="block text-slate-300 font-bold mb-1">سبب الإجراء (للتوثيق المحاسبي):</label><input id="swal-freeze-reason" class="swal2-input !bg-[#120A1F] !border-[#362052] !text-white !text-xs !w-full !m-0 !p-2" placeholder="اكتب سبب الإجراء..."></div></div>`,
            icon: isFreezing ? 'warning' : 'question',
            showCancelButton: true,
            confirmButtonColor: confirmButtonColor,
            cancelButtonColor: '#362052',
            confirmButtonText: `نعم، قم بـ ${actionText} الآن`,
            cancelButtonText: 'إلغاء',
            background: '#1A102A',
            color: '#fff',
            preConfirm: () => { const reason = document.getElementById('swal-freeze-reason').value; return { reason: reason || 'إجراء إداري دوري' }; }
        }).then(async (result) => {
            if (result.isConfirmed) {
                try {
                    const response = await fetch(endpointUrl, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }, body: JSON.stringify({ reason: result.value.reason }) });
                    const data = await response.json();
                    if (response.ok && data.status === 'success') {
                        Swal.fire({ title: 'تم بنجاح!', text: data.message || 'تم تحديث حالة المحفظة بنجاح', icon: 'success', background: '#1A102A', color: '#fff' }).then(() => { window.location.reload(); });
                    }
                } catch (e) { Swal.fire('خطأ', 'فشل تحديث الحالة', 'error'); }
            }
        });
    } else {
        if (confirm(`هل أنت متأكد من ${actionText} محفظة ${supplierName}؟`)) {
            fetch(endpointUrl, { method: 'POST', headers: { 'Content-Type': 'application/json' } }).then(r => r.json()).then(() => window.location.reload()).catch(() => alert('فشلت العملية'));
        }
    }
}
