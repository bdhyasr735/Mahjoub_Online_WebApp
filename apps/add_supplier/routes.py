function copyCredentials() {
    // 1. تحديد النص المراد نسخه من داخل الـ Modal
    // (تأكد من مطابقة الـ ID أو الفئة المستخدمة في قالبك)
    const username = "علي"; 
    const sovereignId = "SUP-MAH9631";
    const walletCode = "WEL-MAH9631";
    const tempPassword = "123456";
    
    const textToCopy = `اسم المستخدم: ${username}\nمعرف المورد السيادي: ${sovereignId}\nمعرف المحفظة التابعة: ${walletCode}\nكلمة المرور: ${tempPassword}`;
    
    // 2. تنفيذ عملية النسخ في الحافظة بشكل آمن
    navigator.clipboard.writeText(textToCopy).then(() => {
        
        // 🎯 التعديل الاحترافي: بدلاً من الـ alert() المزعج، نغير مظهر الزر نفسه
        const copyBtn = document.getElementById('copyCredentialsBtn'); // افترضنا أن هذا ID الزر
        if (copyBtn) {
            const originalText = copyBtn.innerHTML; // حفظ النص الأصلي للزر (نسخ بيانات الاعتماد)
            
            // تحويل الزر إلى الحالة النشطة بنجاح
            copyBtn.innerHTML = `✅ تم النسخ بنجاح!`;
            copyBtn.style.backgroundColor = "#198754"; // تغيير اللون إلى الأخضر للمحاكاة البصرية
            copyBtn.style.borderColor = "#198754";
            copyBtn.disabled = true; // تعطيل مؤقت لمنع التكرار العشوائي
            
            // إعادة الزر لوضعه الطبيعي تلقائياً بعد ثانيتين (2000 مللي ثانية)
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
                copyBtn.style.backgroundColor = ""; // يعود للون التنسيق الأصلي للمنصة
                copyBtn.style.borderColor = "";
                copyBtn.disabled = false;
            }, 2000);
        }
        
    }).catch(err => {
        console.error('فشلت عملية النسخ السريع: ', err);
    });
}
