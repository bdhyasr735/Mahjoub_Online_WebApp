<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {
            background-color: #1a0b2e; /* البصمة اللونية: البنفسجي الملكي */
            color: #ffffff;
            font-family: 'Cairo', sans-serif;
        }
    </style>
</head>
<body class="flex items-center justify-center min-h-screen">

    <div class="w-full max-w-md p-8 space-y-6 bg-slate-900 border border-purple-900 rounded-2xl shadow-2xl">
        <div class="text-center">
            <h1 class="text-2xl font-bold text-amber-400">محجوب أونلاين</h1>
            <p class="text-sm text-gray-400 mt-2">البوابة السيادية الإدارية</p>
        </div>

        <form id="loginForm" class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-300">اسم المستخدم أو البريد الإلكتروني</label>
                <input type="text" id="username" name="username" required
                    class="w-full mt-1 px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg focus:ring-2 focus:ring-purple-600 focus:outline-none text-white">
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-300">كلمة المرور</label>
                <input type="password" id="password" name="password" required
                    class="w-full mt-1 px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg focus:ring-2 focus:ring-purple-600 focus:outline-none text-white">
            </div>

            <div id="errorMsg" class="hidden p-3 bg-red-950/50 border border-red-800 text-red-300 text-sm text-center rounded-lg"></div>

            <button type="submit" id="submitBtn"
                class="w-full py-3 px-4 bg-gradient-to-r from-purple-700 to-indigo-800 hover:from-purple-800 hover:to-indigo-900 text-white font-semibold rounded-lg shadow-lg transition duration-200">
                تسجيل الدخول السيادي
            </button>
        </form>
    </div>

    <script>
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            const errorMsg = document.getElementById('errorMsg');
            const submitBtn = document.getElementById('submitBtn');

            errorMsg.classList.add('hidden');
            errorMsg.textContent = '';
            submitBtn.disabled = true;
            submitBtn.textContent = 'جاري التحقق...';

            try {
                const response = await fetch("{{ url_for('auth_portal_bp.login') }}", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                });

                const rawText = await response.text();
                let data;

                try {
                    data = JSON.parse(rawText);
                } catch (parseErr) {
                    console.error("Server returned non-JSON response:", rawText);
                    throw new Error("خطأ داخلي في الخادم (استجابة غير صالحة من السيرفر)");
                }

                if (response.ok && data.status === 'success') {
                    window.location.href = data.redirect;
                } else {
                    errorMsg.textContent = data.message || 'فشل تسجيل الدخول، يرجى المحاولة مرة أخرى.';
                    errorMsg.classList.remove('hidden');
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'تسجيل الدخول السيادي';
                }
            } catch (err) {
                console.error("Fetch Error:", err);
                errorMsg.textContent = err.message || 'حدث خطأ في الاتصال بالخادم.';
                errorMsg.classList.remove('hidden');
                submitBtn.disabled = false;
                submitBtn.textContent = 'تسجيل الدخول السيادي';
            }
        });
    </script>
</body>
</html>
