<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>مركز المراسلات والدعم | منصة محجوب أونلاين</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
  <script src="https://unpkg.com/htmx.org@1.9.12"></script>
  <style> 
    body { font-family: 'Tajawal', sans-serif; } 
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #f1f5f9; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
    .contact-item { cursor: pointer; transition: background 0.15s; }
    .contact-item:hover { background: #f8fafc; }
    .contact-item.active { background: #f3e8ff; border-right: 4px solid #570575; }
  </style>
</head>
<body class="bg-slate-100 h-screen overflow-hidden flex flex-col" dir="rtl">

  <!-- الشريط العلوي (Header) -->
  <header class="bg-[#1a0b2e] border-b border-purple-900/40 h-16 px-6 flex items-center justify-between shrink-0 z-30 shadow-md">
    <div class="flex items-center gap-3">
      <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQCm47_tKjb9Qhn6mPX1sd0qGSuGPXs8R8TgcOWlnf5AnEjRUps" alt="محجوب أونلاين" class="h-9 w-auto object-contain bg-white/10 rounded-lg p-1 border border-[#D4AF37]/30">
      <div class="flex items-center gap-2 border-r border-purple-800/60 pr-3">
        <h1 class="text-xs sm:text-sm font-bold text-white tracking-wide">مركز المراسلات والدعم <span class="text-purple-300 font-normal mx-1">|</span> <span class="text-[#D4AF37]">منصة محجوب أونلاين</span></h1>
      </div>
    </div>
    <div class="flex items-center gap-2">
      <span class="inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
        <span class="w-1.5 h-1.5 ml-1.5 bg-emerald-400 rounded-full animate-pulse"></span>
        متصل بـ Meta API
      </span>
    </div>
  </header>

  <!-- الحاوية الرئيسية -->
  <div class="flex-1 flex flex-row overflow-hidden">
    
    <!-- المحتوى الرئيسي (الشات والأقسام الثلاثة) -->
    <main class="flex-1 h-full overflow-hidden flex flex-col bg-slate-100">
      {% if active_tab == 'chat' or not active_tab %}
        <div class="flex-1 flex flex-row overflow-hidden w-full h-full">
          
          <!-- 1. قائمة المحادثات (يمين) -->
          <div class="w-[320px] shrink-0 border-l border-slate-200 bg-white h-full overflow-y-auto shadow-sm" id="sidebar-contacts-container">
            {% include 'admin/components/_sidebar_contacts.html' %}
          </div>

          <!-- 2. منطقة الدردشة (منتصف) -->
          <div class="flex-1 h-full flex flex-col bg-slate-50 border-l border-slate-200 overflow-hidden relative" id="chat-area-container">
            {% include 'admin/components/_chat_area.html' %}
          </div>

          <!-- 3. تفاصيل العميل (يسار) -->
          <div class="w-[300px] shrink-0 bg-white h-full overflow-y-auto shadow-sm" id="client-details-container">
            {% include 'admin/components/_client_details.html' %}
          </div>

        </div>
      {% elif active_tab == 'logs' %}
        <div class="p-6">
          <h2 class="text-xl font-bold mb-4">سجل الرسائل</h2>
          <table class="w-full bg-white rounded-lg shadow">
            <thead class="bg-slate-100">
              <tr>
                <th class="p-3 text-right">#</th>
                <th class="p-3 text-right">الاتجاه</th>
                <th class="p-3 text-right">المرسل</th>
                <th class="p-3 text-right">المستقبل</th>
                <th class="p-3 text-right">المحتوى</th>
                <th class="p-3 text-right">الحالة</th>
                <th class="p-3 text-right">التوقيت</th>
              </tr>
            </thead>
            <tbody>
              {% for log in logs %}
              <tr class="border-b">
                <td class="p-3">{{ log.id }}</td>
                <td class="p-3">{{ log.direction }}</td>
                <td class="p-3">{{ log.sender_number }}</td>
                <td class="p-3">{{ log.recipient_number }}</td>
                <td class="p-3">{{ log.content|truncate(30) }}</td>
                <td class="p-3">{{ log.status }}</td>
                <td class="p-3">{{ log.timestamp.strftime('%Y-%m-%d %H:%M') if log.timestamp else '' }}</td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      {% elif active_tab == 'settings' %}
        <div class="p-6">
          <h2 class="text-xl font-bold mb-4">إعدادات واتساب</h2>
          <form method="POST" class="bg-white p-6 rounded-lg shadow">
            <div class="mb-4">
              <label class="block text-sm font-medium mb-1">رقم الهاتف المرتبط</label>
              <input type="text" name="phone_number_id" value="{{ settings.phone_number_id }}" class="w-full p-2 border rounded">
            </div>
            <div class="mb-4">
              <label class="block text-sm font-medium mb-1">معرف الأعمال</label>
              <input type="text" name="whatsapp_business_id" value="{{ settings.whatsapp_business_id }}" class="w-full p-2 border rounded">
            </div>
            <div class="mb-4">
              <label class="block text-sm font-medium mb-1">رمز الوصول</label>
              <input type="password" name="access_token" value="{{ settings.access_token }}" class="w-full p-2 border rounded">
            </div>
            <div class="mb-4">
              <label class="block text-sm font-medium mb-1">رمز التحقق</label>
              <input type="text" name="verify_token" value="{{ settings.verify_token }}" class="w-full p-2 border rounded">
            </div>
            <button type="submit" class="bg-[#570575] text-white px-6 py-2 rounded-lg hover:bg-[#632C8F] transition">حفظ الإعدادات</button>
            {% if saved_success %}
            <div class="mt-4 p-3 bg-green-100 text-green-700 rounded">تم الحفظ بنجاح</div>
            {% endif %}
          </form>
        </div>
      {% endif %}
    </main>

    <!-- القائمة الجانبية للأيقونات (أقصى اليسار) -->
    <aside class="w-20 bg-[#1a0b2e] flex flex-col items-center justify-between py-6 shrink-0 shadow-xl z-20 border-r border-purple-900/40">
      <div class="flex flex-col items-center gap-6 w-full">
        <div class="w-12 h-12 rounded-2xl bg-white/10 border border-[#D4AF37]/30 flex items-center justify-center p-1 shadow-md">
          <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQCm47_tKjb9Qhn6mPX1sd0qGSuGPXs8R8TgcOWlnf5AnEjRUps" alt="Logo" class="w-full h-full object-contain rounded-xl">
        </div>
        <div class="w-10 h-[1px] bg-purple-900/60"></div>
        <div class="flex flex-col gap-3 w-full px-3">
          <a href="{{ url_for('whatsapp_service.chat_dashboard') }}" title="المحادثات المباشرة" class="relative group p-3 rounded-2xl transition-all flex justify-center {{ 'bg-[#570575] text-white shadow-lg border border-[#D4AF37]/30' if active_tab == 'chat' or not active_tab else 'text-purple-300 hover:bg-purple-900/50 hover:text-white' }}">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>
            <span class="absolute top-2 left-3 w-2.5 h-2.5 bg-emerald-400 rounded-full border-2 border-[#1a0b2e]"></span>
          </a>
          <a href="{{ url_for('whatsapp_service.logs_dashboard') }}" title="سجل الرسائل" class="p-3 rounded-2xl transition-all flex justify-center {{ 'bg-[#570575] text-white shadow-lg border border-[#D4AF37]/30' if active_tab == 'logs' else 'text-purple-300 hover:bg-purple-900/50 hover:text-white' }}">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8-4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"></path></svg>
          </a>
        </div>
      </div>
      <div class="w-full px-3">
        <a href="{{ url_for('whatsapp_service.settings_dashboard') }}" title="الإعدادات" class="p-3 rounded-2xl transition-all flex justify-center {{ 'bg-[#570575] text-white shadow-lg border border-[#D4AF37]/30' if active_tab == 'settings' else 'text-purple-300 hover:bg-purple-900/50 hover:text-white' }}">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path></svg>
        </a>
      </div>
    </aside>
  </div>

  <script>
    document.addEventListener('htmx:afterSwap', function(evt) {
      if (evt.detail.target.id === 'sidebar-contacts-container') {
        const activeItem = document.querySelector('.contact-item.active');
        if (activeItem) {
          const contactId = activeItem.dataset.contactId;
          if (contactId) {
            htmx.ajax('GET', '/admin/whatsapp/client/' + contactId + '/chat', { target: '#chat-area-container', swap: 'innerHTML' });
            htmx.ajax('GET', '/admin/whatsapp/client/' + contactId + '/details', { target: '#client-details-container', swap: 'innerHTML' });
          }
        }
      }
    });

    document.addEventListener('DOMContentLoaded', function() {
      const activeItem = document.querySelector('.contact-item.active');
      if (!activeItem) {
        const firstItem = document.querySelector('.contact-item');
        if (firstItem) {
          firstItem.classList.add('active');
          const contactId = firstItem.dataset.contactId;
          if (contactId) {
            htmx.ajax('GET', '/admin/whatsapp/client/' + contactId + '/chat', { target: '#chat-area-container', swap: 'innerHTML' });
            htmx.ajax('GET', '/admin/whatsapp/client/' + contactId + '/details', { target: '#client-details-container', swap: 'innerHTML' });
          }
        }
      }
    });
  </script>
</body>
</html>
