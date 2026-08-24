<!-- 📂 apps/whatsapp_service/templates/admin/chat_view.html -->
<!-- Chat Dashboard Main View -->
<div class="flex-1 flex overflow-hidden bg-white">
  
  <!-- قسم المحادثة النشطة (يسار الشاشة في الاتجاه الينبوعي / العكسي) -->
  <section class="flex-1 flex flex-col h-full bg-slate-50/50 relative overflow-hidden">
    
    <!-- رأس المحادثة النشطة (معلومات العميل والتحكم) -->
    <div id="active-chat-header" class="h-16 px-6 bg-white border-b border-slate-200 flex items-center justify-between shrink-0 shadow-xs z-10">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-full bg-[#570575]/10 border border-[#570575]/20 flex items-center justify-center text-[#570575] font-bold text-sm" id="current-avatar">
          💬
        </div>
        <div>
          <h2 class="text-xs font-bold text-slate-900" id="current-chat-name">اختر محادثة من القائمة</h2>
          <p class="text-[10px] text-slate-400 font-mono" id="current-chat-phone">--</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button onclick="refreshCurrentChat()" class="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors text-xs flex items-center gap-1 cursor-pointer" title="تحديث المحادثة">
          <span>🔄</span>
        </button>
      </div>
    </div>

    <!-- صندوق رسائل المحادثة (الدردشة) -->
    <div id="chat-messages-container" class="flex-1 overflow-y-auto p-6 space-y-4 flex flex-col">
      <!-- رسالة ترحيبية افتراضية عند عدم تحديد محادثة -->
      <div class="m-auto text-center space-y-2 max-w-sm">
        <div class="w-16 h-16 rounded-3xl bg-[#570575]/10 text-[#570575] flex items-center justify-center mx-auto text-2xl shadow-inner">
          📱
        </div>
        <h3 class="text-sm font-bold text-slate-800">مرحباً بك في مركز مراسلات محجوب أونلاين</h3>
        <p class="text-xs text-slate-500">اختر محادثة من قائمة العملاء الجانبية للبدء في إرسال واستقبال الرسائل عبر واتساب كلاود آبي.</p>
      </div>
    </div>

    <!-- شريط إدخال وإرسال الرسالة -->
    <div id="chat-input-bar" class="p-4 bg-white border-t border-slate-200 shrink-0 hidden">
      <form id="sendMessageForm" onsubmit="sendWhatsAppMessage(event)" class="flex items-center gap-3">
        <input type="hidden" id="active-recipient-phone" value="">
        
        <button type="button" class="p-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors text-sm cursor-pointer" title="إرفاق ملف">
          📎
        </button>
        
        <input type="text" id="message-input-text" placeholder="اكتب رسالتك للعميل هنا..." 
               class="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-xs text-slate-800 focus:outline-none focus:border-[#570575] focus:bg-white transition-all">
        
        <button type="submit" id="send-btn" class="bg-[#570575] hover:bg-[#632C8F] text-white px-5 py-2.5 rounded-xl text-xs font-bold transition-all shadow-xs hover:shadow-md cursor-pointer flex items-center gap-1.5">
          <span>إرسال</span>
          <span>📤</span>
        </button>
      </form>
    </div>

  </section>

  <!-- قائمة المحادثات والعملاء الجانبية (يمين الشاشة) -->
  <aside class="w-80 lg:w-96 bg-white border-r border-slate-200 flex flex-col h-full shrink-0">
    
    <!-- بحث في المحادثات -->
    <div class="p-4 border-b border-slate-100 shrink-0 space-y-3">
      <div class="flex items-center justify-between">
        <h3 class="text-xs font-bold text-slate-800">المحادثات النشطة</h3>
        <span id="conversations-count" class="text-[10px] bg-[#570575]/10 text-[#570575] px-2 py-0.5 rounded-full font-bold">0 عميل</span>
      </div>
      <div class="relative">
        <input type="text" id="search-conversations" oninput="filterConversations(this.value)" placeholder="ابحث برقم الهاتف أو اسم العميل..." 
               class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:border-[#570575] transition-all pl-8">
        <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs">🔍</span>
      </div>
    </div>

    <!-- قائمة قائمة العملاء / المحادثات -->
    <div id="conversations-list" class="flex-1 overflow-y-auto divide-y divide-slate-100">
      <!-- يتم حقن المحادثات هنا ديناميكياً عبر الجافاسكريبت -->
      <div class="p-8 text-center text-slate-400 text-xs">
        جاري تحميل المحادثات...
      </div>
    </div>

  </aside>

</div>

<!-- دوال الجافاسكريبت المساعدة للدردشة المباشرة -->
<script>
  let activePhone = null;

  // جلب المحادثات عند تحميل الصفحة
  document.addEventListener('DOMContentLoaded', function() {
    loadConversations();
    // تحديث المحادثات كل 10 ثوانٍ تلقائياً
    setInterval(loadConversations, 10000);
  });

  function loadConversations() {
    fetch('{{ url_for("whatsapp_service.api_get_conversations") }}', {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        renderConversations(data.conversations);
      }
    }).catch(err => console.error('خطأ في جلب المحادثات:', err));
  }

  function renderConversations(conversations) {
    const listEl = document.getElementById('conversations-list');
    document.getElementById('conversations-count').textContent = conversations.length + ' عميل';
    
    if (conversations.length === 0) {
      listEl.innerHTML = '<div class="p-8 text-center text-slate-400 text-xs">لا توجد محادثات نشطة حالياً</div>';
      return;
    }

    listEl.innerHTML = conversations.map(c => `
      <div onclick="selectConversation('${c.phone}', '${c.name || c.phone}')" 
           class="p-4 hover:bg-slate-50 transition-colors cursor-pointer flex items-start gap-3 ${activePhone === c.phone ? 'bg-[#570575]/5 border-r-4 border-[#570575]' : ''}">
        <div class="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center text-slate-700 font-bold text-xs shrink-0">
          ${(c.name || c.phone).substring(0, 2)}
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between mb-1">
            <h4 class="text-xs font-bold text-slate-900 truncate">${c.name || 'عميل واتساب'}</h4>
            <span class="text-[10px] text-slate-400">${c.last_time || ''}</span>
          </div>
          <p class="text-[11px] text-slate-500 truncate" dir="ltr">${c.phone}</p>
          <p class="text-[11px] text-slate-600 truncate mt-0.5">${c.last_message || 'انقر لعرض المحادثة'}</p>
        </div>
        ${c.unread_count ? `<span class="bg-[#570575] text-white text-[10px] px-1.5 py-0.5 rounded-full font-bold">${c.unread_count}</span>` : ''}
      </div>
    `).join('');
  }

  function selectConversation(phone, name) {
    activePhone = phone;
    document.getElementById('active-recipient-phone').value = phone;
    document.getElementById('current-chat-name').textContent = name;
    document.getElementById('current-chat-phone').textContent = phone;
    document.getElementById('current-avatar').textContent = name.substring(0, 2);
    document.getElementById('chat-input-bar').classList.remove('hidden');
    
    loadChatMessages(phone);
  }

  function loadChatMessages(phone) {
    const container = document.getElementById('chat-messages-container');
    container.innerHTML = '<div class="m-auto text-center text-xs text-slate-400">جاري تحميل الرسائل...</div>';

    fetch(`{{ url_for("whatsapp_service.api_get_messages") }}?phone=${phone}`, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        renderMessages(data.messages);
      } else {
        container.innerHTML = '<div class="m-auto text-center text-xs text-rose-500">فشل تحميل الرسائل</div>';
      }
    }).catch(() => {
      container.innerHTML = '<div class="m-auto text-center text-xs text-rose-500">خطأ في الاتصال بالخادم</div>';
    });
  }

  function renderMessages(messages) {
    const container = document.getElementById('chat-messages-container');
    if (messages.length === 0) {
      container.innerHTML = '<div class="m-auto text-center text-xs text-slate-400">لا توجد رسائل سابقة مع هذا العميل. ابدأ المراسلة الآن!</div>';
      return;
    }

    container.innerHTML = messages.map(msg => {
      const isOutbound = msg.direction === 'outbound';
      return `
        <div class="flex flex-col ${isOutbound ? 'items-start' : 'items-end'} animate-fadeIn">
          <div class="max-w-[70%] rounded-2xl px-4 py-3 text-xs shadow-xs ${isOutbound ? 'bg-[#570575] text-white rounded-br-none' : 'bg-white border border-slate-200 text-slate-800 rounded-bl-none'}">
            <p class="leading-relaxed whitespace-pre-wrap">${msg.body}</p>
            <div class="flex items-center justify-end gap-1 mt-1 text-[9px] ${isOutbound ? 'text-purple-200' : 'text-slate-400'}">
              <span>${msg.time || ''}</span>
              ${isOutbound ? '<span>✓✓</span>' : ''}
            </div>
          </div>
        </div>
      `;
    }).join('');
    
    container.scrollTop = container.scrollHeight;
  }

  function sendWhatsAppMessage(event) {
    event.preventDefault();
    const phone = document.getElementById('active-recipient-phone').value;
    const input = document.getElementById('message-input-text');
    const text = input.value.trim();
    
    if (!text || !phone) return;
    
    const sendBtn = document.getElementById('send-btn');
    sendBtn.disabled = true;
    
    fetch('{{ url_for("whatsapp_service.api_send_message") }}', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({ phone: phone, message: text })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        input.value = '';
        loadChatMessages(phone);
        loadConversations();
      } else {
        alert('❌ فشل الإرسال: ' + (data.message || 'حدث خطأ غير معروف'));
      }
    })
    .catch(() => alert('❌ خطأ في الاتصال بالخادم'))
    .finally(() => {
      sendBtn.disabled = false;
    });
  }

  function refreshCurrentChat() {
    if (activePhone) {
      loadChatMessages(activePhone);
      loadConversations();
    }
  }

  function filterConversations(query) {
    const q = query.toLowerCase();
    document.querySelectorAll('#conversations-list > div').forEach(el => {
      const text = el.textContent.toLowerCase();
      el.style.display = text.includes(q) ? 'flex' : 'none';
    });
  }
</script>
