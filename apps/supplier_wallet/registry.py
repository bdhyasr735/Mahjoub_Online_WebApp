def prepare_modules_for_template(supplier_modules):
    """
    تحويل الموديولات إلى صيغة جاهزة للعرض في القالب.
    - تحويل الروابط القديمة (نصية) إلى روابط جاهزة (title + url).
    """
    if not supplier_modules:
        return {}

    final_modules = {}
    for key, module in supplier_modules.items():
        if 'links' in module and isinstance(module['links'], dict):
            final_links = {}
            for endpoint, link_data in module['links'].items():
                try:
                    # إذا كانت الروابط قديمة (نصية فقط)
                    if isinstance(link_data, str):
                        # نحتاج لبناء الرابط - هنا نستخدم إعدادات آمنة
                        if 'supplier_wallet' in endpoint:
                            # محاولة الحصول على wallet_id من المتغيرات المتاحة
                            wallet_id = '1'  # قيمة افتراضية آمنة
                            try:
                                from flask_login import current_user
                                from apps.models.wallet_db import SupplierWallet
                                if current_user.is_authenticated:
                                    wallet = SupplierWallet.query.filter_by(supplier_id=current_user.id).first()
                                    if wallet:
                                        wallet_id = wallet.wallet_code or wallet.id
                            except Exception:
                                pass
                            final_links[endpoint] = {
                                'title': link_data,
                                'url': url_for(endpoint, wallet_id=wallet_id)
                            }
                        else:
                            final_links[endpoint] = {
                                'title': link_data,
                                'url': url_for(endpoint)
                            }
                    # إذا كانت الروابط جاهزة (dict)
                    else:
                        final_links[endpoint] = link_data
                except Exception:
                    # في حالة فشل بناء الرابط، نعرض رابطاً وهمياً
                    final_links[endpoint] = {
                        'title': link_data if isinstance(link_data, str) else 'رابط',
                        'url': '#'
                    }
            module['links'] = final_links
        final_modules[key] = module

    return final_modules
