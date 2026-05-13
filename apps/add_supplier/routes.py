import os
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from .models import Supplier  # تأكد من إنشاء موديل المورد مسبقاً

@login_required
def add_supplier(request):
    """
    معالجة إضافة مورد جديد إلى نظام محجوب أونلاين.
    """
    if request.method == 'POST':
        try:
            # 1. استخراج البيانات من الطلب (Request)
            username = request.POST.get('username')
            password = request.POST.get('password')
            email = request.POST.get('email')
            activity_type = request.POST.get('activity_type')
            owner_name = request.POST.get('owner_name')
            identity_type = request.POST.get('identity_type')
            trade_name = request.POST.get('trade_name')
            phone = request.POST.get('phone')
            bank_name = request.POST.get('bank_name')
            bank_acc = request.POST.get('bank_acc')
            province = request.POST.get('province')
            district = request.POST.get('district')
            address_detail = request.POST.get('address_detail')

            # 2. التحقق من عدم تكرار اسم المستخدم
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': f'اسم المستخدم "{username}" مسجل مسبقاً في النظام.'
                }, status=400)

            # 3. معالجة رفع صورة الهوية
            identity_image_url = None
            if 'identity_image' in request.FILES:
                myfile = request.FILES['identity_image']
                fs = FileSystemStorage(location='media/suppliers/identities/')
                filename = fs.save(myfile.name, myfile)
                identity_image_url = fs.url(filename)

            # 4. إنشاء مستخدم جديد (Account) للمورد في Django Auth
            new_user = User.objects.create_user(
                username=username,
                password=password,
                email=email if email else ""
            )

            # 5. ربط البيانات بموديل المورد (Supplier Profile)
            supplier_profile = Supplier.objects.create(
                user=new_user,
                owner_name=owner_name,
                trade_name=trade_name,
                activity_type=activity_type,
                identity_type=identity_type,
                identity_image=identity_image_url,
                phone=phone,
                bank_name=bank_name,
                bank_account_number=bank_acc,
                province=province,
                district=district,
                address_detail=address_detail,
                is_verified=True  # تعميد سيادي تلقائي عند الإضافة من الإدارة
            )

            # 6. استجابة النجاح (تتوافق مع SweetAlert2 في القالب)
            return JsonResponse({
                'status': 'success',
                'message': f'تم أرشفة المورد {trade_name} بنجاح ضمن "سوقك السمارت".'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'حدث خطأ غير متوقع: {str(e)}'
            }, status=500)

    # في حال طلب الصفحة عبر GET (عرض النموذج)
    # نقوم بحساب المعرف القادم (Next ID) للعرض في القالب
    next_id = Supplier.objects.count() + 1
    return render(request, 'admin/add_supplier.html', {'next_id': next_id})
