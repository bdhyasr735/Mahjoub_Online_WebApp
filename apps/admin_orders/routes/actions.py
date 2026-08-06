<!-- 📂 apps/admin_orders/templates/admin/order/_items_table_card.html -->
<div class="card shadow mb-4">
    <div class="card-header py-3">
        <h6 class="m-0 font-weight-bold text-primary">عناصر الطلب</h6>
    </div>
    <div class="card-body">
        <div class="table-responsive">
            <table class="table table-bordered text-center align-middle" width="100%">
                <thead class="table-light">
                    <tr>
                        <th class="text-start">المنتج</th>
                        <th>الكمية</th>
                        <th>السعر</th>
                        <th>الإجمالي</th>
                        <th>المورد المسؤول</th>
                    </tr>
                </thead>
                <tbody id="order-items-tbody">
                    {% for item in items_list %}
                        <tr class="item-row" data-order-id="{{ order_id }}" data-item-id="{{ item.id }}">
                            <td class="text-start">
                                <strong>{{ item.productData.title or 'منتج بدون عنوان' }}</strong>
                                <small class="d-block text-muted">QID: {{ item.product_qid or 'N/A' }}</small>
                            </td>
                            <td>{{ item.quantity }}</td>
                            <td>{{ "{:,.2f}".format(item.price or 0) }}</td>
                            <td class="fw-bold">{{ "{:,.2f}".format((item.quantity or 0) * (item.price or 0)) }}</td>
                            <td>
                                <select class="form-select form-select-sm supplier-select" 
                                        onchange="updateSupplier(this, '{{ order_id }}', '{{ item.id }}')">
                                    <option value="">-- بدون مورد --</option>
                                    {% for s in all_suppliers %}
                                        <option value="{{ s.id }}" {% if item.supplier_id == s.id %}selected{% endif %}>
                                            {{ s.trade_name or s.name }}
                                        </option>
                                    {% endfor %}
                                </select>
                            </td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<script>
/**
 * دالة تحديث المورد وربطه بالخريطة السيادية
 */
function updateSupplier(selectElement, orderId, itemId) {
    const supplierId = selectElement.value;
    const row = selectElement.closest('.item-row');
    
    console.log(`جارٍ الربط: طلب ${orderId}، عنصر ${itemId}، مورد ${supplierId}`);

    fetch(`/admin/orders/${orderId}/item/${itemId}/assign-supplier`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ supplier_id: supplierId || null })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log("✅ تم التحديث:", data.message);
            // إشعار بسيط بالتحديث الناجح
            selectElement.classList.add('is-valid');
            setTimeout(() => selectElement.classList.remove('is-valid'), 2000);
        } else {
            alert("خطأ: " + data.message);
            // إرجاع القائمة للحالة السابقة في حال الفشل
            location.reload(); 
        }
    })
    .catch(error => {
        console.error("🚨 خطأ:", error);
        alert("حدث خطأ في الاتصال بالسيرفر");
    });
}
</script>

<style>
    .supplier-select { min-width: 150px; cursor: pointer; }
    .is-valid { border-color: #198754 !important; background-color: #f1fff1; }
</style>
