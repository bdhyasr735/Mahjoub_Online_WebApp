# coding: utf-8
# 📂 apps/suppliers_dashboard/settings_routes.py

from flask import Blueprint, render_template, abort, session, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
import traceback
import os
import json

from apps.models import db, Supplier, SupplierWallet
from apps.models.supplier_profile_db import SupplierProfile
from apps.data.yemen_governorates import YEMEN_GOVERNORATES
from apps.data.store_categories import STORE_CATEGORIES, CATEGORIES_LIST
from apps.data.yemen_banks import YEMEN_BANKS, BANKS_LIST
from apps.data.financial_companies import FINANCIAL_COMPANIES, FINANCIAL_COMPANIES_LIST

settings_bp = Blueprint(
    'suppliers_settings',
    __name__,
    template_folder='templates'
)


def get_supplier_context():
    """
    جلب بيانات المورد والمحفظة من قاعدة البيانات
    مع التحقق من صلاحية المستخدم
    """
    try:
        # ✅ التحقق من نوع المستخدم
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return None
        
        # ✅ تحديد supplier_id
        if user_type == 'staff':
            supplier_id = getattr(current_user, 'supplier_id', None)
        else:
            supplier_id = current_user.id
        
        if not supplier_id:
            return None
        
        # ✅ جلب المورد
        supplier = db.session.get(Supplier, supplier_id)
        if not supplier:
            return None
        
        # ✅ جلب المحفظة
        wallet = db.session.execute(
            db.select(SupplierWallet).filter_by(supplier_id=supplier.id)
        ).unique().scalar_one_or_none()
        supplier.wallet = wallet
        
        return supplier
        
    except Exception as e:
        print(f"❌ خطأ في get_supplier_context: {e}")
        return None


# ============================================================
# ✅ إضافة عناصر جديدة إلى القوائم
# ============================================================

@settings_bp.route('/add-category', methods=['POST'])
@login_required
def add_category():
    """إضافة فئة جديدة"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'الاسم مطلوب'})
        
        # التحقق من عدم التكرار
        if name in CATEGORIES_LIST:
            return jsonify({'success': False, 'message': 'هذه الفئة موجودة بالفعل'})
        
        # ✅ إضافة إلى ملف البيانات
        file_path = os.path.join('apps', 'data', 'store_categories.py')
        
        # قراءة الملف الحالي
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # إنشاء معرف جديد
        import re
        existing_ids = re.findall(r"'id': '([^']+)'", content)
        new_id = f"cat_{len(existing_ids) + 1:03d}"
        
        # إضافة الفئة الجديدة
        new_entry = f"\n    {{'id': '{new_id}', 'name': '{name}', 'icon': 'fa-tag'}}," 
        
        # إدراج قبل آخر قوس
        lines = content.split('\n')
        insert_index = -1
        for i in range(len(lines) - 1, -1, -1):
            if ']' in lines[i]:
                insert_index = i
                break
        
        if insert_index > 0:
            lines.insert(insert_index, new_entry)
            new_content = '\n'.join(lines)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # ✅ تحديث القائمة في الذاكرة
            STORE_CATEGORIES.append({'id': new_id, 'name': name, 'icon': 'fa-tag'})
            CATEGORIES_LIST.append(name)
            
            return jsonify({'success': True, 'name': name, 'id': new_id})
        
        return jsonify({'success': False, 'message': 'خطأ في إضافة الفئة'})
        
    except Exception as e:
        print(f"❌ خطأ في add_category: {e}")
        return jsonify({'success': False, 'message': str(e)})


@settings_bp.route('/add-bank', methods=['POST'])
@login_required
def add_bank():
    """إضافة بنك جديد"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'الاسم مطلوب'})
        
        if name in BANKS_LIST:
            return jsonify({'success': False, 'message': 'هذا البنك موجود بالفعل'})
        
        # ✅ إضافة إلى ملف البيانات
        file_path = os.path.join('apps', 'data', 'yemen_banks.py')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        import re
        existing_ids = re.findall(r"'id': '([^']+)'", content)
        new_id = f"bank_{len(existing_ids) + 1:03d}"
        
        new_entry = f"\n    {{'id': '{new_id}', 'name': '{name}', 'icon': 'fa-building'}},"
        
        lines = content.split('\n')
        insert_index = -1
        for i in range(len(lines) - 1, -1, -1):
            if ']' in lines[i]:
                insert_index = i
                break
        
        if insert_index > 0:
            lines.insert(insert_index, new_entry)
            new_content = '\n'.join(lines)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            YEMEN_BANKS.append({'id': new_id, 'name': name, 'icon': 'fa-building'})
            BANKS_LIST.append(name)
            
            return jsonify({'success': True, 'name': name, 'id': new_id})
        
        return jsonify({'success': False, 'message': 'خطأ في إضافة البنك'})
        
    except Exception as e:
        print(f"❌ خطأ في add_bank: {e}")
        return jsonify({'success': False, 'message': str(e)})


@settings_bp.route('/add-financial-company', methods=['POST'])
@login_required
def add_financial_company():
    """إضافة شركة مالية جديدة"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'الاسم مطلوب'})
        
        if name in FINANCIAL_COMPANIES_LIST:
            return jsonify({'success': False, 'message': 'هذه الشركة موجودة بالفعل'})
        
        # ✅ إضافة إلى ملف البيانات
        file_path = os.path.join('apps', 'data', 'financial_companies.py')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        import re
        existing_ids = re.findall(r"'id': '([^']+)'", content)
        new_id = f"comp_{len(existing_ids) + 1:03d}"
        
        new_entry = f"\n    {{'id': '{new_id}', 'name': '{name}', 'icon': 'fa-building', 'type': 'أخرى'}},"
        
        lines = content.split('\n')
        insert_index = -1
        for i in range(len(lines) - 1, -1, -1):
            if ']' in lines[i]:
                insert_index = i
                break
        
        if insert_index > 0:
            lines.insert(insert_index, new_entry)
            new_content = '\n'.join(lines)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            FINANCIAL_COMPANIES.append({'id': new_id, 'name': name, 'icon': 'fa-building', 'type': 'أخرى'})
            FINANCIAL_COMPANIES_LIST.append(name)
            
            return jsonify({'success': True, 'name': name, 'id': new_id})
        
        return jsonify({'success': False, 'message': 'خطأ في إضافة الشركة'})
        
    except Exception as e:
        print(f"❌ خطأ في add_financial_company: {e}")
        return jsonify({'success': False, 'message': str(e)})


# ============================================================
# ✅ صفحة الإعدادات الرئيسية
# ============================================================

@settings_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """
    صفحة إعدادات المتجر - فقط للموردين المسجلين
    """
    try:
        # ✅ التحقق من وجود المورد
        supplier = get_supplier_context()
        if not supplier:
            flash('❌ يرجى تسجيل الدخول أولاً', 'danger')
            return redirect(url_for('suppliers_auth.login'))
        
        # ✅ معالجة POST (حفظ البيانات)
        if request.method == 'POST':
            try:
                # ✅ تحديث اسم المتجر
                supplier.trade_name = request.form.get('trade_name', supplier.trade_name)
                
                # ❌ owner_name لا يتم تحديثه (للقراءة فقط)
                
                # ✅ تحديث رقم الهاتف مع التحقق
                new_phone = request.form.get('phone', '').strip()
                if new_phone and len(new_phone) == 9 and new_phone.isdigit():
                    if new_phone != supplier.phone:
                        supplier.phone = new_phone
                elif new_phone:
                    flash('⚠️ رقم الهاتف يجب أن يكون 9 أرقام', 'warning')
                    return redirect(url_for('suppliers_settings.settings'))
                
                # ✅ تحديث الملف الشخصي
                profile = getattr(supplier, 'supplier_profile', None)
                if not profile:
                    profile = SupplierProfile(supplier_id=supplier.id)
                    db.session.add(profile)
                
                # ✅ حفظ جميع البيانات
                profile.email = request.form.get('email', '').strip()
                profile.address = request.form.get('address', '').strip()
                profile.description = request.form.get('description', '').strip()
                profile.governorate = request.form.get('governorate', '').strip()
                profile.city = request.form.get('city', '').strip()
                profile.category = request.form.get('category', '').strip()
                profile.bank_name = request.form.get('bank_name', '').strip()
                profile.bank_account = request.form.get('bank_account', '').strip()
                profile.company_name = request.form.get('financial_company', '').strip()
                profile.id_number = request.form.get('id_number', '').strip()
                profile.commercial_reg = request.form.get('commercial_reg', '').strip()
                
                db.session.commit()
                flash('✅ تم تحديث بيانات المتجر بنجاح', 'success')
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ خطأ في حفظ البيانات: {e}")
                flash(f'❌ حدث خطأ أثناء الحفظ: {str(e)}', 'danger')
            
            return redirect(url_for('suppliers_settings.settings'))
        
        # ✅ عرض الصفحة مع تمرير جميع البيانات
        return render_template(
            'suppliers/settings.html',
            supplier=supplier,
            governorates=YEMEN_GOVERNORATES,
            categories=STORE_CATEGORIES,
            banks=YEMEN_BANKS,
            financial_companies=FINANCIAL_COMPANIES
        )
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ خطأ في settings: {error_details}")
        flash('❌ حدث خطأ تقني، يرجى المحاولة لاحقاً', 'danger')
        return redirect(url_for('suppliers_dashboard.dashboard'))


# ============================================================
# ✅ API للبحث المتقدم في البنوك
# ============================================================

@settings_bp.route('/api/banks', methods=['GET'])
@login_required
def api_get_banks():
    """جلب البنوك مع فلتر بحث متقدم"""
    try:
        search = request.args.get('search', '').strip()
        limit = request.args.get('limit', 50, type=int)
        
        from apps.data.yemen_banks import YEMEN_BANKS
        
        # فلتر البحث
        if search:
            filtered = [
                bank for bank in YEMEN_BANKS 
                if search.lower() in bank['name'].lower() 
                or search.lower() in bank.get('id', '').lower()
                or search.lower() in bank.get('name_ar', '').lower()
            ]
        else:
            filtered = YEMEN_BANKS.copy()
        
        # ترتيب حسب الاسم
        filtered.sort(key=lambda x: x.get('name', ''))
        
        # تحديد العدد
        filtered = filtered[:limit]
        
        return jsonify({
            'success': True,
            'banks': filtered,
            'total': len(filtered),
            'search': search
        })
        
    except Exception as e:
        print(f"❌ خطأ في api_get_banks: {e}")
        return jsonify({
            'success': False,
            'banks': [],
            'message': str(e)
        }), 500


# ============================================================
# ✅ API للبحث المتقدم في الشركات المالية
# ============================================================

@settings_bp.route('/api/financial-companies', methods=['GET'])
@login_required
def api_get_financial_companies():
    """جلب الشركات المالية مع فلتر بحث متقدم"""
    try:
        search = request.args.get('search', '').strip()
        type_filter = request.args.get('type', '').strip()
        limit = request.args.get('limit', 50, type=int)
        
        from apps.data.financial_companies import FINANCIAL_COMPANIES
        
        filtered = FINANCIAL_COMPANIES.copy()
        
        # فلتر حسب النوع
        if type_filter:
            filtered = [
                comp for comp in filtered 
                if comp.get('type', '').lower() == type_filter.lower()
            ]
        
        # فلتر حسب البحث
        if search:
            filtered = [
                comp for comp in filtered 
                if search.lower() in comp['name'].lower() 
                or search.lower() in comp.get('id', '').lower()
                or search.lower() in comp.get('type', '').lower()
            ]
        
        # ترتيب حسب الاسم
        filtered.sort(key=lambda x: x.get('name', ''))
        
        # تحديد العدد
        filtered = filtered[:limit]
        
        return jsonify({
            'success': True,
            'companies': filtered,
            'total': len(filtered),
            'search': search,
            'type_filter': type_filter
        })
        
    except Exception as e:
        print(f"❌ خطأ في api_get_financial_companies: {e}")
        return jsonify({
            'success': False,
            'companies': [],
            'message': str(e)
        }), 500


# ============================================================
# ✅ API للبحث المتقدم في المدن
# ============================================================

@settings_bp.route('/api/cities', methods=['GET'])
@login_required
def api_get_cities():
    """جلب المدن مع فلتر بحث متقدم"""
    try:
        search = request.args.get('search', '').strip()
        governorate = request.args.get('governorate', '').strip()
        limit = request.args.get('limit', 50, type=int)
        
        from apps.data.yemen_governorates import YEMEN_GOVERNORATES
        
        all_cities = []
        
        if governorate:
            # جلب مدن محافظة محددة
            cities = YEMEN_GOVERNORATES.get(governorate, [])
            all_cities = [{'name': city, 'governorate': governorate} for city in cities]
        else:
            # جلب جميع المدن من جميع المحافظات
            for gov, cities in YEMEN_GOVERNORATES.items():
                for city in cities:
                    all_cities.append({'name': city, 'governorate': gov})
        
        # فلتر البحث
        if search:
            all_cities = [
                city for city in all_cities 
                if search.lower() in city['name'].lower() 
                or search.lower() in city['governorate'].lower()
            ]
        
        # ترتيب حسب المحافظة ثم المدينة
        all_cities.sort(key=lambda x: (x['governorate'], x['name']))
        
        # تحديد العدد
        all_cities = all_cities[:limit]
        
        return jsonify({
            'success': True,
            'cities': all_cities,
            'total': len(all_cities),
            'search': search,
            'governorate_filter': governorate
        })
        
    except Exception as e:
        print(f"❌ خطأ في api_get_cities: {e}")
        return jsonify({
            'success': False,
            'cities': [],
            'message': str(e)
        }), 500


# ============================================================
# ✅ API للتحقق من رقم الحساب البنكي
# ============================================================

@settings_bp.route('/api/validate-bank-account', methods=['POST'])
@login_required
def api_validate_bank_account():
    """التحقق من صحة رقم الحساب البنكي"""
    try:
        data = request.get_json()
        bank_account = data.get('bank_account', '').strip()
        bank_name = data.get('bank_name', '').strip()
        
        if not bank_account:
            return jsonify({
                'valid': False,
                'message': '⚠️ رقم الحساب البنكي مطلوب'
            })
        
        # التحقق من أن الرقم يحتوي على أرقام فقط
        if not bank_account.isdigit():
            return jsonify({
                'valid': False,
                'message': '⚠️ رقم الحساب يجب أن يحتوي على أرقام فقط'
            })
        
        # التحقق من طول الرقم (بين 10 و 20 رقم)
        if len(bank_account) < 10 or len(bank_account) > 20:
            return jsonify({
                'valid': False,
                'message': f'⚠️ رقم الحساب يجب أن يكون بين 10 و 20 رقم (الطول الحالي: {len(bank_account)})'
            })
        
        # التحقق من وجود البنك (اختياري)
        if bank_name:
            from apps.data.yemen_banks import BANKS_LIST
            if bank_name not in BANKS_LIST:
                return jsonify({
                    'valid': True,
                    'message': f'✅ رقم الحساب صحيح، ولكن البنك "{bank_name}" غير مسجل في النظام',
                    'warning': True
                })
        
        return jsonify({
            'valid': True,
            'message': '✅ رقم الحساب صحيح',
            'bank_name': bank_name
        })
        
    except Exception as e:
        print(f"❌ خطأ في api_validate_bank_account: {e}")
        return jsonify({
            'valid': False,
            'message': '❌ حدث خطأ في التحقق'
        }), 500


# ============================================================
# ✅ API للتحقق من اسم الشركة المالية
# ============================================================

@settings_bp.route('/api/validate-financial-company', methods=['POST'])
@login_required
def api_validate_financial_company():
    """التحقق من صحة اسم الشركة المالية"""
    try:
        data = request.get_json()
        company_name = data.get('company_name', '').strip()
        
        if not company_name:
            return jsonify({
                'valid': False,
                'message': '⚠️ اسم الشركة المالية مطلوب'
            })
        
        # التحقق من وجود الشركة في القائمة
        from apps.data.financial_companies import FINANCIAL_COMPANIES_LIST
        
        if company_name in FINANCIAL_COMPANIES_LIST:
            return jsonify({
                'valid': True,
                'exists': True,
                'message': f'✅ الشركة "{company_name}" مسجلة في النظام'
            })
        else:
            return jsonify({
                'valid': True,
                'exists': False,
                'message': f'⚠️ الشركة "{company_name}" غير مسجلة، يمكنك إضافتها',
                'can_add': True
            })
        
    except Exception as e:
        print(f"❌ خطأ في api_validate_financial_company: {e}")
        return jsonify({
            'valid': False,
            'message': '❌ حدث خطأ في التحقق'
        }), 500


# ============================================================
# ✅ API للحصول على أنواع الشركات المالية
# ============================================================

@settings_bp.route('/api/financial-company-types', methods=['GET'])
@login_required
def api_get_financial_company_types():
    """جلب أنواع الشركات المالية المتاحة"""
    try:
        from apps.data.financial_companies import FINANCIAL_COMPANIES
        
        types = list(set([comp.get('type', 'أخرى') for comp in FINANCIAL_COMPANIES]))
        types.sort()
        
        return jsonify({
            'success': True,
            'types': types
        })
        
    except Exception as e:
        print(f"❌ خطأ في api_get_financial_company_types: {e}")
        return jsonify({
            'success': False,
            'types': []
        }), 500


# ============================================================
# ✅ API لإضافة عنصر جديد مع التحقق المسبق
# ============================================================

@settings_bp.route('/api/add-item', methods=['POST'])
@login_required
def api_add_item():
    """إضافة عنصر جديد (فئة، بنك، شركة مالية) مع التحقق المسبق"""
    try:
        data = request.get_json()
        item_type = data.get('type', '').strip()
        name = data.get('name', '').strip()
        
        if not item_type or not name:
            return jsonify({
                'success': False,
                'message': '⚠️ نوع العنصر والاسم مطلوبان'
            })
        
        if len(name) < 2:
            return jsonify({
                'success': False,
                'message': '⚠️ الاسم يجب أن يكون حرفين على الأقل'
            })
        
        # معالجة حسب النوع
        if item_type == 'category':
            return add_category()
        elif item_type == 'bank':
            return add_bank()
        elif item_type == 'company':
            return add_financial_company()
        else:
            return jsonify({
                'success': False,
                'message': f'⚠️ نوع غير معروف: {item_type}'
            })
        
    except Exception as e:
        print(f"❌ خطأ في api_add_item: {e}")
        return jsonify({
            'success': False,
            'message': f'❌ حدث خطأ: {str(e)}'
        }), 500
