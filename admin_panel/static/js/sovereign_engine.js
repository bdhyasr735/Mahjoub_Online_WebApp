/**
 * محرك الحوكمة السيادي - محجوب أونلاين v3.5
 * إدارة الموردين، الموظفين، والخزينة الثلاثية
 */

// --- 1. إعدادات المحرك الاستدعائي ---
let currentSupplierId = null;

document.addEventListener('DOMContentLoaded', function() {
    // مراقبة حقل البحث للضغط على Enter
    const searchInput = document.getElementById('mainSearch');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') triggerSearch();
        });
    }
});

// --- 2. منطق البحث والاستدعاء الذكي (#) ---
function triggerSearch() {
    const query = document.getElementById('mainSearch').value.trim();
    const province = document.getElementById('filterProvince').value;
    const tier = document.getElementById('filterTier').value;
    const status = document.getElementById('filterStatus').value;

    if (!query && !province && !tier && !status) {
        alert("يرجى إدخال كلمة بحث أو استخدام الفلاتر أو رمز (#)");
        return;
    }

    // إظهار منطقة النتائج وإخفاء رسالة الحالة الفارغة
    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('resultsArea').style.display = 'block';
    
    const tbody = document.getElementById('suppliersTableBody');
    tbody.innerHTML = `<tr><td colspan="7" class="py-4 text-royal"><i class="fas fa-spinner fa-spin"></i> جاري استدعاء البيانات من الترسانة...</td></tr>`;

    fetch(`/admin/api/search-suppliers?q=${encodeURIComponent(query)}&province=${province}&tier=${tier}&status=${status}`)
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                renderSuppliers(data.suppliers);
            }
        });
}

// --- 3. عرض الموردين في الجدول السيادي ---
function renderSuppliers(suppliers) {
    const tbody = document.getElementById('suppliersTableBody');
    tbody.innerHTML = '';

    if (suppliers.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="py-4 text-muted">لا توجد نتائج تطابق هذا البحث</td></tr>`;
        return;
    }

    suppliers.forEach(s => {
        const row = `
            <tr>
                <td class="fw-bold text-royal small">${s.e_wallet || 'WAL-MAH-' + s.id}</td>
                <td class="text-end">
                    <div class="fw-bold">${s.trade_name}</div>
                    <div class="small text-muted">${s.owner_name} | ${s.phone}</div>
                </td>
                <td class="small">${s.province} / ${s.district}</td>
                <td><span class="badge bg-soft-royal text-royal border border-primary px-3">${s.tier}</span></td>
                <td>
                    <div class="small text-success fw-bold">${s.balances.YER} YER</div>
                    <div class="small text-primary">${s.balances.SAR} SAR</div>
                    <div class="small text-warning">${s.balances.USD} USD</div>
                </td>
                <td>
                    <span class="badge ${s.status === 'active' ? 'bg-success' : 'bg-danger'} rounded-pill">
                        ${s.status === 'active' ? 'نشط' : 'موقف'}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-royal" onclick="openSovereignModal(${s.id})" title="إدارة الكيان">
                        <i class="fas fa-tools"></i>
                    </button>
                </td>
            </tr>
        `;
        tbody.insertAdjacentHTML('beforeend', row);
    });
}

// --- 4. فتح النافذة السيادية وسحب البيانات الكاملة ---
function openSovereignModal(id) {
    currentSupplierId = id;
    const modal = new bootstrap.Modal(document.getElementById('sovereignModal'));
    
    fetch(`/admin/api/get-supplier-full-details/${id}`)
        .then(res => res.json())
        .then(data => {
            // تعبئة البيانات الأساسية
            document.getElementById('m_title').innerText = `إدارة كيان: ${data.trade_name}`;
            document.getElementById('m_owner_name').value = data.owner_name;
            document.getElementById('m_username').value = data.username || '';
            document.getElementById('m_province').value = data.province;
            document.getElementById('m_district').value = data.district;
            document.getElementById('m_tier').value = data.tier;
            
            // تعبئة الخزينة الثلاثية
            document.getElementById('m_bal_yer').value = data.balances.YER;
            document.getElementById('m_bal_sar').value = data.balances.SAR;
            document.getElementById('m_bal_usd').value = data.balances.USD;
            
            // تصفير حقل كلمة المرور
            document.getElementById('m_new_pass').value = '';

            // تعبئة الموظفين
            renderStaff(data.staff);
            
            modal.show();
        });
}

// --- 5. إدارة طاقم العمل (الموظفين) ---
function renderStaff(staff) {
    const list = document.getElementById('staffList');
    list.innerHTML = '';
    
    if (!staff || staff.length === 0) {
        list.innerHTML = '<p class="text-center text-muted small py-3">لا يوجد موظفين مسجلين حالياً</p>';
        return;
    }

    staff.forEach(user => {
        const item = `
            <div class="d-flex justify-content-between align-items-center bg-white p-2 rounded-3 mb-2 border-end border-3 border-royal shadow-sm">
                <div>
                    <div class="fw-bold small">${user.username}</div>
                    <span class="badge bg-light text-muted" style="font-size: 10px;">موظف صلاحيات كاملة</span>
                </div>
                <button class="btn btn-sm btn-outline-danger border-0" onclick="resetStaffPass('${user.username}')">
                    <i class="fas fa-key"></i>
                </button>
            </div>
        `;
        list.insertAdjacentHTML('beforeend', item);
    });
}

// --- 6. تعميد التعديلات وإرسالها للقاعدة ---
function saveAllChanges() {
    if (!currentSupplierId) return;

    const payload = {
        owner_name: document.getElementById('m_owner_name').value,
        province: document.getElementById('m_province').value,
        district: document.getElementById('m_district').value,
        tier: document.getElementById('m_tier').value,
        balance_yer: document.getElementById('m_bal_yer').value,
        balance_sar: document.getElementById('m_bal_sar').value,
        balance_usd: document.getElementById('m_bal_usd').value,
        new_password: document.getElementById('m_new_pass').value
    };

    fetch(`/admin/api/update-sovereign-data/${currentSupplierId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            alert("✅ تم تعميد كافة التعديلات في قاعدة البيانات بنجاح");
            bootstrap.Modal.getInstance(document.getElementById('sovereignModal')).hide();
            triggerSearch(); // تحديث الجدول
        } else {
            alert("❌ خطأ: " + data.message);
        }
    });
}

// وظائف مساعدة
function togglePass() {
    const x = document.getElementById("m_new_pass");
    x.type = x.type === "password" ? "text" : "password";
}

function resetFilters() {
    document.getElementById('mainSearch').value = '';
    document.getElementById('filterProvince').value = '';
    document.getElementById('filterTier').value = '';
    document.getElementById('filterStatus').value = '';
    document.getElementById('resultsArea').style.display = 'none';
    document.getElementById('emptyState').style.display = 'block';
}
