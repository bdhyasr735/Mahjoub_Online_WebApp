# coding: utf-8
"""
📂 apps/supplier_wallet/services/notification_service.py
خدمة التنبيهات والإشعارات الفورية (Toast & Flash Notifications)
ترسل تنبيهات فورية للمورد عند إيداع رصيد، قبول/رفض سحب، أو إضافة حساب بنكي.
"""

from decimal import Decimal
from typing import Union
from flask import flash


class NotificationService:
    """
    إدارة التنبيهات الفورية في المنصة
    """

    @staticmethod
    def _format_amount(amount: Union[float, int, Decimal, str]) -> str:
        """تنسيق المبالغ المالية بأمان للعرض في التنبيهات"""
        try:
            val = Decimal(str(amount))
            return f"{val:,.2f}"
        except Exception:
            return str(amount)

    @staticmethod
    def notify_success(message: str, title: str = "تمت العملية بنجاح"):
        """إشعار فوري أخضر/ذهبي بنجاح العملية"""
        flash({
            'type': 'success',
            'title': title,
            'message': message,
            'icon': 'check-circle'
        }, category='toast_success')

    @classmethod
    def notify_withdrawal_requested(cls, amount: Union[float, Decimal], request_number: str):
        """تنبيه فوري لتقديم طلب سحب جديد"""
        formatted_amount = cls._format_amount(amount)
        flash({
            'type': 'info',
            'title': 'تم استلام طلب السحب',
            'message': f'تم تسجيل طلب سحب بمبلغ {formatted_amount} ر.س بنجاح برقم {request_number}. الطلب قيد مراجعة الإدارة المالية.',
            'icon': 'clock'
        }, category='toast_info')

    @classmethod
    def notify_withdrawal_approved(cls, amount: Union[float, Decimal], voucher_number: str):
        """تنبيه فوري لاعتماد وقبول طلب السحب المالي"""
        formatted_amount = cls._format_amount(amount)
        flash({
            'type': 'success',
            'title': 'تمت الموافقة وصرف المستحقات',
            'message': f'تمت الموافقة على تحويل مبلغ {formatted_amount} ر.س وإصدار سند الصرف رقم {voucher_number}.',
            'icon': 'dollar-sign'
        }, category='toast_success')

    @classmethod
    def notify_withdrawal_rejected(cls, amount: Union[float, Decimal], reason: str = ""):
        """تنبيه فوري عند رفض طلب السحب وإعادة الرصيد للمورد"""
        formatted_amount = cls._format_amount(amount)
        msg = f'تم رفض طلب السحب بمبلغ {formatted_amount} ر.س وإعادة الرصيد للمحفظة.'
        if reason:
            msg += f' السبب: {reason}'
        flash({
            'type': 'warning',
            'title': 'تم رفض طلب السحب',
            'message': msg,
            'icon': 'x-circle'
        }, category='toast_warning')

    @staticmethod
    def notify_error(message: str, title: str = "تنبيه مالي"):
        """إشعار فوري عند حدوث خطأ أو نقص في الرصيد"""
        flash({
            'type': 'danger',
            'title': title,
            'message': message,
            'icon': 'alert-triangle'
        }, category='toast_danger')
