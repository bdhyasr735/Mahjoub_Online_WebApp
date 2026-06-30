# coding: utf-8
# 📂 apps/utils/logger.py - نظام الرقابة السيادي المحدث

import logging
import os
from apps.utils.time_utils import format_full_timestamp, get_current_utc

# إنشاء مجلد للسجلات إذا لم يكن موجوداً
LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # تنسيق السجل: [التوقيت الموحد] - [المستوى] - [الرسالة]
        # سنستخدم التنسيق الذي يوفره time_utils
        formatter = logging.Formatter('%(message)s') 
        
        # ملف السجلات العام
        file_handler = logging.FileHandler(f'{LOG_DIR}/system_activity.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    return logger

# وظيفة لتسجيل محاولات الاختراق مع التوقيت الموحد
def log_security_event(event_type, details):
    logger = get_logger('security')
    # استخدام المرجع الزمني الموحد للنظام
    timestamp = format_full_timestamp(get_current_utc())
    logger.warning(f"🚨 [{timestamp}] [SECURITY EVENT] {event_type} | Details: {details}")

# وظيفة لتسجيل الحركات المالية (للاستخدام في الأستاذ العام)
def log_treasury_event(event_type, details):
    logger = get_logger('treasury')
    timestamp = format_full_timestamp(get_current_utc())
    logger.info(f"💰 [{timestamp}] [TREASURY] {event_type} | Details: {details}")
