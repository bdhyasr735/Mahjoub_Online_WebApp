function openModal(id) {
    document.getElementById(id).classList.remove('hidden');
}
function closeModal(id) {
    document.getElementById(id).classList.add('hidden');
}

function openFreezeModal(supplierId, supplierName, walletCode, balance) {
    document.getElementById('freeze_supplier_name').innerText = supplierName || '---';
    document.getElementById('freeze_wallet_code').innerText = walletCode || '---';
    document.getElementById('freeze_balance').innerText = Number(balance).toLocaleString() + ' ريال';
    document.getElementById('freezeModal').setAttribute('data-supplier-id', supplierId);
    openModal('freezeModal');
}

function openFundModal(supplierId, supplierName, walletCode, balance) {
    document.getElementById('fund_supplier_name').innerText = supplierName || '---';
    document.getElementById('fund_wallet_code').innerText = walletCode || '---';
    document.getElementById('fund_balance').innerText = Number(balance).toLocaleString() + ' ريال';
    document.getElementById('fundModal').setAttribute('data-supplier-id', supplierId);
    openModal('fundModal');
}

function submitFreezeWallet() {
    const modal = document.getElementById('freezeModal');
    const supplierId = modal.getAttribute('data-supplier-id');
    const reason = document.getElementById('freeze_reason').value;

    fetch(`/admin/suppliers-wallets/${supplierId}/freeze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason: reason })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            closeModal('freezeModal');
            window.location.reload();
        } else {
            alert('خطأ: ' + data.message);
        }
    })
    .catch(error => alert('تعذر الاتصال بالخادم: ' + error));
}

function submitFundWallet() {
    const modal = document.getElementById('fundModal');
    const supplierId = modal.getAttribute('data-supplier-id');
    const transType = document.getElementById('fund_trans_type').value;
    const amount = document.getElementById('fund_amount').value;
    const currency = document.getElementById('fund_currency').value;
    const reason = document.getElementById('fund_reason').value;

    if(parseFloat(amount) <= 0) {
        alert('يرجى إدخال مبلغ صحيح أكبر من 0.');
        return;
    }

    fetch(`/admin/suppliers-wallets/${supplierId}/fund`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            trans_type: transType,
            amount: amount,
            currency: currency,
            reason: reason
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            closeModal('fundModal');
            window.location.reload();
        } else {
            alert('خطأ: ' + data.message);
        }
    })
    .catch(error => alert('تعذر الاتصال بالخادم: ' + error));
}
