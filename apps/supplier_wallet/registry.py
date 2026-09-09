def prepare_links_for_template(supplier_modules):
    """
    توحيد صيغة الروابط في جميع الموديولات.
    تحويل الروابط النصية (Strings) إلى روابط جاهزة (Objects) تحتوي على title و url.
    """
    if not supplier_modules:
        return {}

    final_modules = {}
    for key, module in supplier_modules.items():
        if 'links' in module and isinstance(module['links'], dict):
            final_links = {}
            for endpoint, link_data in module['links'].items():
                if isinstance(link_data, str):
                    # الروابط قديمة (نصية)
                    title = link_data
                    try:
                        if 'supplier_wallet' in endpoint:
                            # جلب wallet_id
                            wallet_id = '1'
                            try:
                                from flask_login import current_user
                                from apps.models.wallet_db import SupplierWallet
                                if current_user.is_authenticated:
                                    wallet = SupplierWallet.query.filter_by(supplier_id=current_user.id).first()
                                    if wallet:
                                        wallet_id = wallet.wallet_code or wallet.id
                            except Exception:
                                pass
                            url = url_for(endpoint, wallet_id=wallet_id)
                        else:
                            url = url_for(endpoint)
                    except Exception:
                        url = '#'  # مسار آمن في حالة الفشل
                    final_links[endpoint] = {'title': title, 'url': url}
                else:
                    # الروابط جاهزة (كائنات) - استخدمها كما هي
                    final_links[endpoint] = link_data
            module['links'] = final_links
        final_modules[key] = module

    return final_modules
