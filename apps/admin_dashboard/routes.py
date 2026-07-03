{# 📂 apps/admin_dashboard/templates/admin/admin_base.html #}
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}القيادة المركزية | MAHJOUB{% endblock %}</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">

    <style>
        :root {
            --royal-purple: #1a0b2e;
            --deep-black: #08020d;
            --mahjoub-gold: #D4AF37;
            --sidebar-width: 280px;
        }
        body { font-family: 'Cairo', sans-serif; background-color: #f4f7f6; margin: 0; }
        .sidebar { width: var(--sidebar-width); background: linear-gradient(180deg, var(--royal-purple) 0%, var(--deep-black) 100%); height: 100vh; position: fixed; right: 0; top: 0; z-index: 1050; transition: all 0.3s; box-shadow: 2px 0 10px rgba(0,0,0,0.3); overflow-y: auto; }
        .logo-container { padding: 30px 10px; text-align: center; border-bottom: 1px solid rgba(212, 175, 55, 0.3); }
        .sidebar-logo { width: 70px; filter: brightness(0) invert(1); }
        .brand-text { color: var(--mahjoub-gold); font-size: 0.9rem; margin-top: 10px; display: block; }
        .nav-menu { padding: 20px 15px; }
        .nav-link { display: flex; align-items: center; padding: 12px 15px; color: rgba(255,255,255,0.7); text-decoration: none; border-radius: 10px; transition: 0.3s; cursor: pointer; }
        .nav-link:hover, .nav-link.active { background: rgba(212, 175, 55, 0.2); color: var(--mahjoub-gold); }
        .dropdown-content { display: none; list-style: none; padding-right: 35px; border-right: 2px solid var(--mahjoub-gold); margin: 5px 0; }
        .dropdown-content a { color: rgba(255,255,255,0.8); display: block; padding: 8px 10px; font-size: 0.9rem; border-radius: 5px; text-decoration: none; }
        .dropdown-content a:hover { background: rgba(212, 175, 55, 0.1); color: var(--mahjoub-gold); }
        .dropdown-content a.active { color: var(--mahjoub-gold); font-weight: bold; }
        .main-wrapper { margin-right: var(--sidebar-width); transition: 0.3s; }
        .top-navbar { background: #fff; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .menu-toggle { display: none; background: none; border: none; font-size: 1.5rem; color: var(--royal-purple); }
        @media (max-width: 992px) {
            .sidebar { right: -280px; }
            .sidebar.active { right: 0; }
            .main-wrapper { margin-right: 0; }
            .menu-toggle { display: block !important; }
        }
    </style>
</head>
<body>

    <aside class="sidebar" id="sidebar">
        <div class="logo-container">
            <img src="https://cdn.qumra.cloud/media/67f7f6d5f0b82f44a47bf845/1770229315912-117966978.webp" class="sidebar-logo" alt="MAHJOUB">
            <h6 class="text-white mt-3 fw-bold mb-0">القيادة المركزية</h6>
            <span class="brand-text">محجوب أونلاين | سوقك الذكي</span>
        </div>

        <nav class="nav-menu">
            <a href="{{ url_for('admin_dashboard.dashboard') }}" class="nav-link {{ 'active' if request.endpoint == 'admin_dashboard.dashboard' }}"><i class="fas fa-chart-line me-3"></i> <span>الإحصائيات</span></a>
            
            <a href="{{ url_for('orders.dashboard') }}" class="nav-link {{ 'active' if request.endpoint == 'orders.dashboard' }}"><i class="fas fa-shopping-bag me-3"></i> <span>إدارة الطلبات</span></a>

            <div class="nav-item">
                <div class="nav-link" onclick="toggleSub(this)"><i class="fas fa-handshake me-3"></i> <span>إدارة الموردين</span> <i class="fas fa-chevron-down ms-auto"></i></div>
                <ul class="dropdown-content">
                    {# تأكد من أن اسم الـ Blueprint هو 'suppliers_bp' في ملف الـ routes الخاص بالموردين #}
                    <li><a href="{{ url_for('suppliers_bp.list_suppliers') }}" class="{{ 'active' if request.endpoint == 'suppliers_bp.list_suppliers' }}"><i class="fas fa-list-ul me-2"></i> قائمة الشركاء</a></li>
                    <li><a href="{{ url_for('admin_suppliers_add_bp.add_supplier_or_staff') }}" class="{{ 'active' if request.endpoint == 'admin_suppliers_add_bp.add_supplier_or_staff' }}"><i class="fas fa-user-plus me-2"></i> إضافة شريك</a></li>
                </ul>
            </div>

            <div class="nav-item">
                <div class="nav-link" id="finance-nav" onclick="toggleSub(this)"><i class="fas fa-wallet me-3"></i> <span>الرقابة المالية</span> <i class="fas fa-chevron-down ms-auto"></i></div>
                <ul class="dropdown-content" id="finance-dropdown">
                    <li>
                        <a href="{{ url_for('treasury_bp.index') }}" class="{{ 'active' if request.endpoint == 'treasury_bp.index' }}">
                           <i class="fas fa-vault me-2"></i> خزينة المنصة
                        </a>
                    </li>
                    <li><a href="{{ url_for('wallet_app.dashboard') }}" class="{{ 'active' if request.endpoint == 'wallet_app.dashboard' }}"><i class="fas fa-money-check-alt me-2"></i> محفظة الموردين</a></li>
                </ul>
            </div>

            <a href="{{ url_for('settings_bp.index') }}" class="nav-link {{ 'active' if request.endpoint == 'settings_bp.index' }}"><i class="fas fa-cog me-3"></i> <span>إعدادات النظام</span></a>

            <hr class="text-white my-3">
            <a href="{{ url_for('auth_portal.logout') }}" class="nav-link text-danger"><i class="fas fa-sign-out-alt me-3"></i> <span>خروج آمن</span></a>
        </nav>
    </aside>

    <main class="main-wrapper" id="main">
        <header class="top-navbar">
            <button class="menu-toggle" onclick="toggleSidebar()"><i class="fas fa-bars"></i></button>
            <div class="user-identity fw-bold"><i class="fas fa-user-circle me-2"></i> {{ current_user.username if current_user.is_authenticated else 'المسؤول' }}</div>
            <div class="badge bg-warning text-dark">بيئة التحكم السيادية</div>
        </header>

        <section class="p-4">
            {% block content %}{% endblock %}
        </section>
    </main>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function toggleSub(el) {
            let drop = el.nextElementSibling;
            drop.style.display = (drop.style.display === "block") ? "none" : "block";
            el.querySelector('.fa-chevron-down').style.transform = (drop.style.display === "block") ? "rotate(180deg)" : "rotate(0deg)";
        }
        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('active');
        }
        
        document.addEventListener("DOMContentLoaded", function() {
            if (window.location.href.includes('treasury')) {
                let drop = document.getElementById('finance-dropdown');
                drop.style.display = "block";
                let icon = document.getElementById('finance-nav').querySelector('.fa-chevron-down');
                icon.style.transform = "rotate(180deg)";
            }
        });
    </script>
</body>
</html>
