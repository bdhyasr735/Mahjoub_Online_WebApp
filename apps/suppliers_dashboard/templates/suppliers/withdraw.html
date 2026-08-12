{% extends "suppliers/base.html" %}

{% block title %}طلب سحب أرباح | منصة محجوب{% endblock %}

{% block content %}
<style>
    /* تنسيقات مطابقة للواجهة */
    .withdraw-wrapper {
        font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    }

    /* البطاقة الداكنة (المحفظة) */
    .wallet-card-dark {
        background: linear-gradient(160deg, #23153c 0%, #130a24 100%);
        border-radius: 20px;
        padding: 35px 28px;
        color: #ffffff;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
        position: relative;
    }

    .wallet-pill-code {
        background-color: #ffffff;
        color: #1a0f30;
        font-weight: 700;
        font-size: 0.82rem;
        padding: 5px 14px;
        border-radius: 20px;
        display: inline-block;
    }

    .balance-label {
        color: #b3abd0;
        font-size: 1rem;
        font-weight: 600;
        margin-top: 25px;
    }

    .balance-val {
        color: #ecc94b;
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -1px;
        margin-top: 5px;
        margin-bottom: 30px;
    }

    .balance-val .curr {
        font-size: 1.8rem;
        font-weight: 700;
        margin-right: 6px;
    }

    .wallet-stats-footer {
        border-top: 1px solid rgba(255, 255, 255, 0.12);
        padding-top: 18px;
    }

    .stat-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.92rem;
        margin-bottom: 8px;
    }

    .stat-row .lbl {
        color: #9288b1;
    }

    .stat-row .val {
        color: #ffffff;
        font-weight: 700;
    }

    /* بطاقة النموذج البيضاء */
    .withdraw-form-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 32px;
        border: 1px solid #f0f2f5;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.02);
    }

    .field-title {
        font-weight: 700;
        color: #1a202c;
        font-size: 0.95rem;
        margin-bottom: 8px;
    }

    .amount-box {
        position: relative;
        display: flex;
        align-items: center;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 6px 16px;
    }

    .amount-box:focus-within {
        border-color: #3182ce;
        background-color: #ffffff;
        box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
    }

    .amount-box input {
        border: none;
        background: transparent;
        font-size: 1.35rem;
        font-weight: 700;
        width: 100%;
        text-align: right;
        outline: none;
        color: #2d3748;
    }

    .amount-box .currency-tag {
        font-weight: 700;
        color: #4a5568;
        font-size: 1rem;
    }

    /* أزرار الاختيار السريع */
    .quick-btn {
        border: 1px solid #e2e8f0;
        background: #ffffff;
        color: #2d3748;
        border-radius: 8px;
        padding: 5px 15px;
        font-weight: 600;
        font-size: 0.88rem;
        transition: all 0.15s ease;
    }

    .quick-btn:hover {
        background-color: #f7fafc;
    }

    .quick-btn.all-btn {
        background-color: #1a0f30;
        color: #ffffff;
        border-color: #1a0f30;
    }

    /* صندوق بيانات المستلم */
    .recipient-card {
        background-color: #f8fafc;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #edf2f7;
    }

    .info-group {
        margin-bottom: 12px;
    }

    .info-group:last-child {
        margin-bottom: 0;
    }

    .info-lbl {
        font-size: 0.82rem;
        color: #718096;
        margin-bottom: 2px;
    }

    .info-txt {
        font-weight: 700;
        color: #2d3748;
        font-size: 0.95rem;
    }

    .bank-badge {
        background-color: #ebf8ff;
        color: #3182ce;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .status-badge-ready {
        background-color: #e6fffa;
        color: #234e52;
        border: 1px solid #b2f5ea;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }

    /* زر التأكيد الأصفر/الذهبي */
    .btn-submit-gold {
        background: linear-gradient(180deg, #ecc94b 0%, #d69e2e 100%);
        color: #1a0f30;
        font-weight: 800;
        font-size: 1.05rem;
        border: none;
        border-radius: 10px;
        padding: 14px;
        width: 100%;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(214, 158, 46, 0.25);
    }

    .btn-submit-gold:hover {
        background: linear-gradient(180deg, #f6ad55 0%, #dd6b20 100%);
        color: #ffffff;
        transform: translateY(-1px);
    }
</style>

<div class="container-fluid py-3 withdraw-wrapper" dir="rtl">

    <!-- رسائل التنبيه والخطأ -->
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <div class="row mb-3">
            <div class="col-12">
                {% for category, message in messages %}
                  <div class="alert alert-{{ 'danger' if category in ['error', 'danger'] else category }} alert-dismissible fade show border-0 shadow-sm" role="alert">
                    <i class="fas {% if category == 'success' %}fa-check-circle text-success{% else %}fa-exclamation-triangle text-danger{% endif %} me-2"></i>
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                  </div>
                {% endfor %}
            </div>
        </div>
      {% endif %}
    {% endwith %}

    <!-- رأس الصفحة -->
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h3 class="fw-bold text-dark mb-1">طلب سحب أرباح</h3>
            <p class="text-muted small mb-0">تحويل سريع وآمن إلى حسابك البنكي / المالي المسجل</p>
        </div>
        <div>
            <span class="badge bg-light text-dark border px-3 py-2 rounded-pill shadow-sm">
                <i class="fas fa-store me-1 text-primary"></i> بوابة الموردين
            </span>
        </div>
    </div>

    <div class="row g-4">
        
        <!-- العمود الأيمن: بطاقة المحفظة (طراز داكن) -->
        <div class="col-lg-5 col-md-12 order-lg-2">
            <div class="wallet-card-dark h-100 d-flex flex-column justify-content-between">
                <div>
                    <div class="text-end">
                        <span class="wallet-pill-code">
                            كود المحفظة: {{ wallet.wallet_code if wallet and hasattr(wallet, 'wallet_code') and wallet.wallet_code else 'MAH-WEL9631' }}
                        </span>
                    </div>

                    <div class="text-center">
                        <div class="balance-label">الرصيد المتاح للسحب</div>
                        <div class="balance-val">
                            <span class="curr">SAR</span>{{ "%.2f"|format(wallet.balance_sar|default(1000.00)) }}
                        </div>
                    </div>
                </div>

                <div class="wallet-stats-footer">
                    <div class="stat-row">
                        <span class="lbl">إجمالي المستحقات المعلقة:</span>
                        <span class="val">SAR {{ "%.2f"|format(total_pending_payouts|default(0.00)) }}</span>
                    </div>
                    <div class="stat-row">
                        <span class="lbl">إجمالي المسحوبات:</span>
                        <span class="val">SAR {{ "%.2f"|format(wallet.total_withdrawn|default(0.00)) }}</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- العمود الأيسر: نموذج طلب السحب -->
        <div class="col-lg-7 col-md-12 order-lg-1">
            <div class="withdraw-form-card">
                <form action="{{ url_for('suppliers_wallet.withdraw') }}" method="POST" id="withdrawForm">
                    {% if csrf_token is defined %}
                        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
                    {% endif %}

                    <!-- إدخال المبلغ -->
                    <div class="mb-4">
                        <label for="amount" class="field-title">المبلغ المطلوب (SAR)</label>
                        <div class="amount-box">
                            <span class="currency-tag">SAR</span>
                            <input type="number" step="0.01" min="10" max="{{ wallet.balance_sar|default(1000.00) }}" id="amount" name="amount" value="0.00" placeholder="0.00" required>
                        </div>

                        <!-- اختيارات سريعة -->
                        <div class="d-flex align-items-center justify-content-between flex-wrap gap-2 mt-3">
                            <div class="d-flex align-items-center gap-2 flex-wrap">
                                <span class="small text-muted fw-semibold me-1">اختيار سريع:</span>
                                <button type="button" class="btn quick-btn" onclick="setQuickAmount(50)">50</button>
                                <button type="button" class="btn quick-btn" onclick="setQuickAmount(100)">100</button>
                                <button type="button" class="btn quick-btn" onclick="setQuickAmount(500)">500</button>
                                <button type="button" class="btn quick-btn" onclick="setQuickAmount(1000)">1000</button>
                                <button type="button" class="btn quick-btn all-btn" onclick="setQuickAmount('all')">الكل</button>
                            </div>
                        </div>
                        <div class="text-muted small mt-2">الحد الأدنى للسحب هو 10 ريال سعودي</div>
                    </div>

                    <!-- جهة التحويل / بيانات المستلم -->
                    <div class="mb-4">
                        <label class="field-title">جهة التحويل (بيانات المستلم)</label>
                        <div class="recipient-card">
                            <div class="row g-3 align-items-center">
                                <div class="col-md-7">
                                    <div class="info-group">
                                        <div class="info-lbl">الاسم الكامل للمالك</div>
                                        <div class="info-txt">
                                            {{ profile.account_holder_name if profile and hasattr(profile, 'account_holder_name') and profile.account_holder_name else (supplier.trade_name or supplier.name or 'المورد التجريبي') }}
                                        </div>
                                    </div>
                                    <div class="info-group">
                                        <div class="info-lbl">رقم الحساب / IBAN</div>
                                        <div class="info-txt text-muted">
                                            {{ profile.bank_account if profile and profile.bank_account else 'غير مدخل' }}
                                        </div>
                                    </div>
                                </div>

                                <div class="col-md-5 text-md-end">
                                    <div class="info-group">
                                        <div class="info-lbl">اسم البنك / جهة الصرف</div>
                                        <div>
                                            <span class="bank-badge">
                                                <i class="fas fa-university"></i>
                                                {{ profile.bank_name if profile and profile.bank_name else 'غير محدد' }}
                                            </span>
                                        </div>
                                    </div>
                                    <div class="mt-2">
                                        <span class="status-badge-ready">
                                            <i class="fas fa-check-circle text-success"></i> جاهز للتحويل
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- الحقول التي يتم إرسالها إلى الـ Route -->
                        <input type="hidden" name="bank_name" value="{{ profile.bank_name if profile and profile.bank_name else '' }}">
                        <input type="hidden" name="bank_account" value="{{ profile.bank_account if profile and profile.bank_account else '' }}">
                        <input type="hidden" name="account_holder_name" value="{{ profile.account_holder_name if profile and hasattr(profile, 'account_holder_name') and profile.account_holder_name else (supplier.trade_name or supplier.name or 'المورد التجريبي') }}">
                    </div>

                    <!-- زر تأكيد الطلب -->
                    <div class="mt-4">
                        <button type="submit" class="btn btn-submit-gold" id="submitBtn">
                            <i class="fas fa-paper-plane me-2"></i> تأكيد إرسال طلب السحب
                        </button>
                    </div>
                </form>
            </div>
        </div>

    </div>
</div>

<script>
    const maxBalance = parseFloat("{{ wallet.balance_sar|default(1000.00) }}");

    function setQuickAmount(val) {
        const input = document.getElementById('amount');
        if (val === 'all') {
            input.value = maxBalance.toFixed(2);
        } else {
            input.value = parseFloat(val).toFixed(2);
        }
    }

    document.getElementById('withdrawForm').addEventListener('submit', function(e) {
        const amount = parseFloat(document.getElementById('amount').value || 0);

        if (amount < 10) {
            e.preventDefault();
            alert('❌ الحد الأدنى لطلب السحب هو 10 ريال سعودي.');
            return false;
        }

        if (amount > maxBalance) {
            e.preventDefault();
            alert(`❌ المبلغ المطلوب (${amount.toFixed(2)} SAR) يتجاوز الرصيد المتاح لديك (${maxBalance.toFixed(2)} SAR).`);
            return false;
        }

        const btn = document.getElementById('submitBtn');
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> جاري إرسال الطلب...';
    });
</script>
{% endblock %}
