# apps/auth_portal/registry.py

class AuthPortalRegistry:
    """
    سجل مركزي لإدارة مسارات، صلاحيات ووحدات المصادقة السيادية في منصة محجوب أونلاين.
    """
    def __init__(self):
        self._registry = {}

    def register(self, module_name, config):
        """تسجيل وحدة أو مسار جديد ضمن المنظومة السيادية."""
        self._registry[module_name] = config

    def get_config(self, module_name):
        """استرجاع إعدادات وحدة معينة."""
        return self._registry.get(module_name)

    def list_modules(self):
        """استعراض كافة الوحدات المسجلة."""
        return self._registry

# كائن عام موحد للسجل السيادي
auth_registry = AuthPortalRegistry()

# تسجيل مسار الدخول السيادي والمسارات التمويهية المرتبطة بها
auth_registry.register('secure_admin_auth', {
    'DISPLAY_NAME': 'البوابة السيادية للإدارة',
    'SECRET_PATH': '/m7jb_sovereign_hq_v2_99x',
    'DECOY_PATH': '/auth_portal/login',
    'STATUS': 'active',
    'REQUIRES_OTP': True
})
