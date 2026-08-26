# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/service.py
"""
سوق محجوب أونلاين - خدمة الواتساب ومحرك الذكاء الاصطناعي
WhatsApp Service for Meta Cloud API v26.0 & Gemini AI
"""

import os
import json
import hmac
import hashlib
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional

# استيراد النماذج من قاعدة البيانات
from apps.whatsapp_service.models import WhatsAppCustomerContact, WhatsAppMessageLog
from apps.extensions import db

class WhatsAppService:
    def __init__(self):
        # إعدادات الربط مع Meta Cloud API v26.0
        self.api_version = os.getenv("WHATSAPP_API_VERSION", "v26.0")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "1336881386166971")
        self.waba_id = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "160492837156903")
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
        self.verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "mahjoob_webhook_secret_2026")
        self.app_secret = os.getenv("WHATSAPP_APP_SECRET", "")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")

        # روابط Meta Graph API
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"
        self.media_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/media"

    # =========================================================================
    # 1. إرسال الرسائل والقوالب والوسائط (Outbound Meta API)
    # =========================================================================

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def send_message(self, recipient_phone: str, text: str) -> Dict[str, Any]:
        """إرسال رسالة نصية فردية عبر Meta WhatsApp Cloud API"""
        clean_phone = recipient_phone.replace("+", "").replace(" ", "").strip()
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_phone,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": text
            }
        }

        # حفظ الرسالة محلياً في قاعدة البيانات
        self._record_outbound_message(clean_phone, text)

        if not self.access_token:
            return {"status": "simulated", "message_id": f"sim_{int(datetime.utcnow().timestamp())}", "to": clean_phone}

        try:
            response = requests.post(self.base_url, headers=self._get_headers(), json=payload, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    def _record_outbound_message(self, phone: str, content: str) -> None:
        """تسجيل الرسالة الصادرة في قاعدة البيانات"""
        try:
            msg = WhatsAppMessageLog(
                direction='outbound',
                sender_number='967784439991',  # رقمك
                recipient_number=phone,
                content=content,
                message_type='text',
                status='sent'
            )
            db.session.add(msg)
            
            # تحديث جهة الاتصال
            contact = WhatsAppCustomerContact.query.filter_by(phone=phone).first()
            if not contact:
                contact = WhatsAppCustomerContact(phone=phone, name=f"عميل (+{phone})")
                db.session.add(contact)
            contact.last_message = content
            contact.last_timestamp = datetime.utcnow()
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [خطأ تسجيل رسالة صادرة]: {e}")

    # =========================================================================
    # 2. معالجة الـ Webhook الوارد والذكاء الاصطناعي (Inbound Webhook)
    # =========================================================================

    def verify_webhook_signature(self, raw_payload: bytes, signature_header: str) -> bool:
        """التحقق الأمني من أن الطلب صادر من خوادم Meta باستخدام App Secret"""
        if not self.app_secret or not signature_header:
            return True
        expected_hash = hmac.new(
            self.app_secret.encode('utf-8'),
            raw_payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected_hash}", signature_header)

    def process_incoming_payload(self, data: Dict[str, Any]) -> None:
        """تحليل ومعالجة الرسائل والأحداث الواردة من Meta Webhook"""
        try:
            entries = data.get("entry", [])
            for entry in entries:
                changes = entry.get("changes", [])
                for change in changes:
                    value = change.get("value", {})
                    
                    # استخراج اسم العميل إن وُجد في بيانات جهات اتصال Meta
                    contact_profile_name = "عميل محجوب"
                    if "contacts" in value and len(value["contacts"]) > 0:
                        contact_profile_name = value["contacts"][0].get("profile", {}).get("name", "عميل محجوب")

                    # 1. حالة وصول رسالة جديدة من عميل
                    if "messages" in value:
                        for msg in value["messages"]:
                            sender_phone = str(msg.get("from", "")).replace("+", "").strip()
                            msg_type = msg.get("type")
                            msg_text = ""

                            if msg_type == "text":
                                msg_text = msg.get("text", {}).get("body", "")
                            elif msg_type == "button":
                                msg_text = msg.get("button", {}).get("text", "")
                            elif msg_type == "interactive":
                                msg_text = msg.get("interactive", {}).get("button_reply", {}).get("title", "")

                            # تسجيل الرسالة وجهة الاتصال في قاعدة البيانات
                            self._record_inbound_message(sender_phone, contact_profile_name, msg_text, msg_type)

                            # توليد رد ذكي تلقائي إذا تم تفعيل الذكاء الاصطناعي
                            self._handle_smart_ai_reply(sender_phone, msg_text)

                    # 2. حالة تحديث حالة التسليم والقراءة
                    if "statuses" in value:
                        for status_update in value["statuses"]:
                            recipient_id = str(status_update.get("recipient_id", "")).replace("+", "").strip()
                            status = status_update.get("status")  # sent, delivered, read
                            # تحديث حالة الرسالة في قاعدة البيانات
                            self._update_message_status(recipient_id, status)

        except Exception as e:
            print(f"❌ [خطأ معالجة Webhook]: {e}")

    def _record_inbound_message(self, phone: str, name: str, content: str, msg_type: str = "text") -> None:
        """تسجيل الرسالة الواردة وجهة الاتصال في قاعدة البيانات"""
        try:
            # تحديث جهة الاتصال
            contact = WhatsAppCustomerContact.query.filter_by(phone=phone).first()
            if not contact:
                contact = WhatsAppCustomerContact(
                    phone=phone,
                    name=name if name != "عميل محجوب" else f"عميل (+{phone})",
                    whatsapp_profile_name=name,
                    unread_count=1
                )
                db.session.add(contact)
            else:
                if name and name != "عميل محجوب":
                    contact.name = name
                    contact.whatsapp_profile_name = name
                contact.unread_count += 1
            
            contact.last_message = content
            contact.last_timestamp = datetime.utcnow()
            
            # إضافة سجل الرسالة
            msg = WhatsAppMessageLog(
                direction='inbound',
                sender_number=phone,
                recipient_number='967784439991',  # رقمك
                content=content,
                message_type=msg_type,
                status='received'
            )
            db.session.add(msg)
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [خطأ تسجيل رسالة واردة]: {e}")

    def _update_message_status(self, phone: str, status: str) -> None:
        """تحديث حالة الرسائل (تم الإرسال، التسليم، القراءة)"""
        try:
            # يمكن تحديث آخر رسالة لهذا الرقم
            contact = WhatsAppCustomerContact.query.filter_by(phone=phone).first()
            if contact:
                contact.last_timestamp = datetime.utcnow()
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [خطأ تحديث الحالة]: {e}")

    def _handle_smart_ai_reply(self, sender_phone: str, customer_message: str) -> None:
        """توليد وإرسال رد ذكي فوري باسم سوق محجوب أونلاين"""
        prompt = (
            "أنت المساعد الذكي الرسمي لخدمة عملاء 'سوق محجوب أونلاين'. "
            "أجب بأسلوب تجاري راقٍ وموجز وودود، واستفسر عما إذا كان العميل بحاجة للمساعدة "
            "في إتمام طلبه أو الاستعلام عن الشحنات والأسعار.\n"
            f"رسالة العميل: {customer_message}"
        )
        
        reply_text = self._generate_gemini_reply(prompt)
        if reply_text:
            self.send_message(sender_phone, reply_text)

    def _generate_gemini_reply(self, prompt: str) -> str:
        """استدعاء نموذج Gemini AI لتوليد الردود الفورية"""
        if not self.gemini_api_key:
            return "أهلاً بك في سوق محجوب أونلاين! تم استلام رسالتك وسيتواصل معك أحد ممثلي الخدمة في أقرب وقت."

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            res = requests.post(url, json=payload, timeout=8)
            res_json = res.json()
            return res_json['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            return "مرحباً بك في سوق محجوب أونلاين! نسعد بخدمتك دائماً، كيف يمكننا مساعدتك اليوم؟"

    # =========================================================================
    # 3. إقراءة البيانات من قاعدة البيانات (لوحة التحكم)
    # =========================================================================

    def get_all_contacts(self) -> List[Dict[str, Any]]:
        """جلب قائمة جهات الاتصال من قاعدة البيانات"""
        try:
            contacts = WhatsAppCustomerContact.query.order_by(WhatsAppCustomerContact.last_timestamp.desc()).all()
            return [c.to_dict() for c in contacts]
        except Exception as e:
            print(f"⚠️ [خطأ جلب جهات الاتصال]: {e}")
            return []

    def get_chat_history(self, phone: str) -> List[Dict[str, Any]]:
        """جلب سجل المحادثة من قاعدة البيانات"""
        try:
            clean_phone = phone.replace("+", "").strip()
            messages = WhatsAppMessageLog.query.filter(
                (WhatsAppMessageLog.sender_number == clean_phone) |
                (WhatsAppMessageLog.recipient_number == clean_phone)
            ).order_by(WhatsAppMessageLog.timestamp.asc()).all()
            return [m.to_dict() for m in messages]
        except Exception as e:
            print(f"⚠️ [خطأ جلب المحادثة]: {e}")
            return []

    def get_webhook_logs(self) -> List[Dict[str, Any]]:
        """عرض سجل أحداث الويب هوك (من قاعدة البيانات إذا توفرت)"""
        # ملاحظة: إذا لم يكن لديك جدول أحداث، يمكنك إرجاع سجل بسيط
        return []

    def get_approved_templates(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "mahjoob_order_confirmation",
                "category": "خدمات وطلبات (Utility)",
                "language": "ar",
                "status": "APPROVED",
                "body_text": "مرحباً {{1}}، تم تأكيد طلبك رقم #{{2}} بقيمة {{3}} ر.س من سوق محجوب أونلاين بنجاح. سنوافيك برابط التتبع فور انطلاق الشحنة."
            },
            {
                "name": "mahjoob_shipping_update",
                "category": "الشحن والتوصيل (Utility)",
                "language": "ar",
                "status": "APPROVED",
                "body_text": "أهلاً {{1}}، شحنتك رقم #{{2}} خرجت للتوصيل الآن مع شركة الشحن. رقم البوليصة: {{3}}."
            },
            {
                "name": "mahjoob_merchant_alert",
                "category": "تنبيهات التجار (Alert)",
                "language": "ar",
                "status": "APPROVED",
                "body_text": "عزيزي التاجر {{1}}، ورد طلب جملة جديد رقم #{{2}} على منتجاتك. يرجى تجهيز الشحنة."
            }
        ]

    def get_current_config(self) -> Dict[str, Any]:
        return {
            "whatsapp_phone_number_id": self.phone_number_id,
            "whatsapp_business_account_id": self.waba_id,
            "whatsapp_access_token": self.access_token,
            "whatsapp_verify_token": self.verify_token,
            "whatsapp_api_version": self.api_version
        }

    def update_config(self, new_config: Dict[str, Any]) -> None:
        self.phone_number_id = new_config.get("whatsapp_phone_number_id", self.phone_number_id)
        self.waba_id = new_config.get("whatsapp_business_account_id", self.waba_id)
        self.access_token = new_config.get("whatsapp_access_token", self.access_token)
        self.verify_token = new_config.get("whatsapp_verify_token", self.verify_token)

    def clear_demo_data(self) -> Dict[str, Any]:
        """تفريغ كافة البيانات من قاعدة البيانات"""
        try:
            WhatsAppMessageLog.query.delete()
            WhatsAppCustomerContact.query.delete()
            db.session.commit()
            return {"success": True, "message": "تم تفريغ كافة البيانات بنجاح. النظام جاهز للإنتاج الفعلي."}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": f"خطأ في تفريغ البيانات: {e}"}
