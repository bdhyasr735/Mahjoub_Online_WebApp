# coding: utf-8
"""
📂 apps/suppliers_wallet/services/notification_service.py
خدمة التنبيهات والإشعارات الفورية (Toast & Flash Notifications)
ترسل تنبيهات فورية للمورد عند إيداع رصيد، قبول سحب، أو إضافة حساب بنكي.
"""

from flask import flash

class NotificationService:
    """
    إدارة التنبيهات الفورية الملكية في منصة محجوب أونلاين
    """

    @staticmethod
    def notify_success(message: str, title: str = "تمت العملية بنجاح"):
        """إشعار فوري أخضر/ذهبي بنجاح العملية"""
        flash({
            'type': 'success',
            'title': title,
            'message': message,
            'icon': 'check-circle'
        }, category='toast_success')

    @staticmethod
    def notify_withdrawal_requested(amount: float, request_number: str):
        """تنبيه فوري لتقديم طلب سحب جديد"""
        flash({
            'type': 'info',
            'title': 'تم استلام طلب السحب',
            'message': f'تم تسجيل طلب سحب بمبلغ {amount:,.2f} SAR بنجاح برقم {request_number}. الطلب قيد مراجعة الإدارة المالية.',
            'icon': 'clock'
        }, category='toast_info')

    @staticmethod
    def notify_withdrawal_approved(amount: float, voucher_number: str):
        """تنبيه فوري لاعتماد وقبول طلب السحب المالي"""
        flash({
            'type': 'success',
            'title': 'تمت الموافقة وصرف المستحقات',
            'message': f'تمت الموافقة على تحويل مبلغ {amount:,.2f} SAR وإصدار سند الصرف رقم {voucher_number}.',
            'icon': 'dollar-sign'
        }, category='toast_success')

    @staticmethod
    def notify_error(message: str, title: str = "تنبيه مالي"):
        """إشعار فوري عند حدوث خطأ أو نقص في الرصيد"""
        flash({
            'type': 'danger',
            'title': title,
            'message': message,
            'icon': 'alert-triangle'
        }, category='toast_danger')
