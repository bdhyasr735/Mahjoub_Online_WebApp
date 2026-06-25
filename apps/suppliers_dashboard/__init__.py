login_manager = LoginManager()
# هذا هو السطر المسؤول عن توجيهك لبوابة الإدارة بدلاً من الموردين
login_manager.login_view = 'auth.login'
