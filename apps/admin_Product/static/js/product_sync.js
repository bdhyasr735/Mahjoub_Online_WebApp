/**
 * 📂 apps/admin_Product/static/js/product_sync.js
 * هذا السكربت وظيفته سحب البيانات من السيرفر في الخلفية
 * وتحديث واجهة المستخدم دون الحاجة لإعادة تحميل الصفحة.
 */

async function fetchProductsInBackground() {
    console.log("🔄 جاري مزامنة المنتجات في الخلفية...");
    
    try {
        const response = await fetch('/admin/api/get-all-products');
        const data = await response.json();
        
        if (data.products) {
            console.log("✅ تم جلب " + data.products.length + " منتج بنجاح.");
            // هنا يمكنك إرسال البيانات إلى دالة تقوم بتحديث الجدول (DOM Update)
            // أو حفظها في LocalStorage لسرعة الوصول لاحقاً
            localStorage.setItem('cached_products', JSON.stringify(data.products));
            updateProductTableUI(data.products);
        }
    } catch (error) {
        console.error("❌ فشل في المزامنة الخلفية:", error);
    }
}

// دالة لتحديث الجدول ديناميكياً
function updateProductTableUI(products) {
    const tableBody = document.getElementById('productTableBody');
    if (!tableBody) return;

    // هنا نقوم بمسح القديم وإضافة الجديد (أو التحديث الجزئي)
    // هذا سيجعل الجدول يمتلئ بالبيانات بعد لحظات من فتح الصفحة
    console.log("📦 جاري تحديث الجدول في الواجهة...");
}

// تشغيل المزامنة تلقائياً عند فتح الصفحة
document.addEventListener('DOMContentLoaded', () => {
    fetchProductsInBackground();
});
