"""
طبقة الخدمات المحاسبية وإدارة العمليات المصرفية لمحافظ الموردين
Mahjoub Online WebApp - Treasury & Supplier Wallets Service Layer
"""
import uuid
import random
from datetime import datetime
from decimal import Decimal

def calculate_wallets_kpis():
    """
    حساب المؤشرات المالية المركزية للوحة التحكم
    """
    return {
        'total_wallets_balance': 3828900.50,
        'total_available_payouts': 3012000.00,
        'total_escrow_held': 816900.50,
        'total_suppliers_count': 1420850,
        'active_suppliers_count': 8,
        'frozen_suppliers_count': 1,
        'pending_withdrawals_amount': 345800.00,
        'pending_withdrawals_count': 28,
        'currency': 'SAR'
    }

def get_suppliers_list(search='', status='all', bank='all', page=1, per_page=10):
    """
    استرجاع قائمة محافظ الموردين مع الفلترة والبحث والترقيم
    """
    mock_suppliers = [
        {
            'id': 'sup-001',
            'wallet_code': 'WAL-SA-9011',
            'supplier_name': 'شركة الرياض للتقنية والإلكترونيات المحدودة',
            'commercial_reg': '1010892341',
            'category': 'إلكترونيات وأجهزة ذكية',
            'city': 'الرياض',
            'total_balance': 485200.50,
            'available_balance': 395000.00,
            'pending_escrow_balance': 90200.50,
            'bank_name': 'مصرف الراجحي',
            'iban': 'SA4480000201608010099221',
            'status': 'active',
            'created_at': '2025-03-10'
        },
        {
            'id': 'sup-002',
            'wallet_code': 'WAL-SA-8842',
            'supplier_name': 'مؤسسة أفق التقنية للتجارة والتوريدات',
            'commercial_reg': '4030198273',
            'category': 'حلول برمجية وحواسيب',
            'city': 'جدة',
            'total_balance': 620450.00,
            'available_balance': 540000.00,
            'pending_escrow_balance': 80450.00,
            'bank_name': 'البنك الأهلي السعودي (SNB)',
            'iban': 'SA0310000001234567890123',
            'status': 'active',
            'created_at': '2025-01-18'
        },
        {
            'id': 'sup-003',
            'wallet_code': 'WAL-SA-7731',
            'supplier_name': 'شركة التميز لحلول اللوجستيات والمستودعات',
            'commercial_reg': '2050981245',
            'category': 'خدمات لوجستية وتغليف',
            'city': 'الدمام',
            'total_balance': 195800.00,
            'available_balance': 0.00,
            'pending_escrow_balance': 45800.00,
            'bank_name': 'بنك الرياض',
            'iban': 'SA6520000000987654321098',
            'status': 'frozen',
            'created_at': '2024-11-05'
        }
    ]
    
    return {
        'items': mock_suppliers,
        'total_count': len(mock_suppliers)
    }

def get_supplier_wallet_by_id(supplier_id):
    """
    استرجاع بيانات المحفظة الفردية وكشف الحساب المفصل
    """
    return {
        'id': supplier_id,
        'wallet_code': 'WAL-SA-9011',
        'supplier_name': 'شركة الرياض للتقنية والإلكترونيات المحدودة',
        'commercial_reg': '1010892341',
        'tax_number': '300982716200003',
        'category': 'إلكترونيات وأجهزة ذكية',
        'city': 'الرياض',
        'phone': '+966 50 123 4567',
        'email': 'finance@riyadh-tech.sa',
        'total_balance': 485200.50,
        'available_balance': 395000.00,
        'pending_escrow_balance': 90200.50,
        'total_withdrawn': 1200000.00,
        'total_sales': 2450000.00,
        'bank_name': 'مصرف الراجحي',
        'bank_account_name': 'شركة الرياض للتقنية ش.ش.و',
        'iban': 'SA4480000201608010099221',
        'account_number': '201608010099221',
        'status': 'active',
        'is_verified': True,
        'created_at': '2025-03-10',
        'last_settlement_at': '2026-08-10',
        'recent_transactions': [
            {
                'id': 'tx-101',
                'ref_code': 'TXN-99101',
                'voucher_number': 'VCH-88210',
                'type': 'credit',
                'type_label': 'إيداع أرباح طلبات',
                'amount': 24500.00,
                'balance_after': 485200.50,
                'description': 'تسوية مبيعات مجمعة لطلبات التجزئة #ORD-7710',
                'created_at': '2026-08-14 10:15',
                'status': 'completed'
            },
            {
                'id': 'tx-102',
                'ref_code': 'TXN-99084',
                'voucher_number': 'VCH-88195',
                'type': 'withdrawal',
                'type_label': 'تحويل بنكي صادر (Sarie)',
                'amount': 150000.00,
                'balance_after': 460700.50,
                'description': 'صرف مستحقات بنكية إلى مصرف الراجحي - دفعة رقم 14',
                'created_at': '2026-08-10 14:20',
                'status': 'completed'
            }
        ]
    }

def toggle_freeze_service(supplier_id, reason='إجراء إداري'):
    """
    تجميد أو فك حظر المحفظة مع التوثيق
    """
    return {
        'status': 'success',
        'supplier_id': supplier_id,
        'message': f'تم تحديث حالة المحفظة بنجاح: {reason}'
    }

def create_manual_adjustment(supplier_id, amount, entry_type, description):
    """
    إنشاء قيد تسوية مالي يدوي وتوليد سند رسمي
    """
    voucher_code = f"VCH-{random.randint(100000, 999999)}"
    ref_code = f"TXN-{random.randint(100000, 999999)}"
    
    return {
        'status': 'success',
        'voucher_code': voucher_code,
        'ref_code': ref_code,
        'amount': amount,
        'entry_type': entry_type,
        'message': f'تم قيد السند المحاسبي {voucher_code} بنجاح'
    }
