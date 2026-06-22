# 📂 apps/utils/logger.py - نظام الرقابة السيادي

import logging
from datetime import datetime
import os

# إنشاء مجلد للسجلات إذا لم يكن موجوداً
LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # تنسيق السجل: [التوقيت] - [المستوى] - [الرسالة]
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # ملف السجلات العام
        file_handler = logging.FileHandler(f'{LOG_DIR}/system_activity.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    return logger

# وظيفة لتسجيل محاولات الاختراق
def log_security_event(event_type, details):
    logger = get_logger('security')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.warning(f"🚨 [SECURITY EVENT] {event_type} | Details: {details} | Time: {timestamp}")
