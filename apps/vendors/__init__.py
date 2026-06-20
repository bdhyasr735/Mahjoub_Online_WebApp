from flask import Blueprint

# قم بتحديد المسار الصحيح لمجلد القوالب الخاص بك
vendor_bp = Blueprint(
    'vendor', 
    __name__, 
    template_folder='templates'  # هذا سيجعل Flask ينظر داخل apps/vendors/templates
)
