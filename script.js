import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  stages: [
    { duration: '20s', target: 20 }, // تصاعد تدريجي إلى 20 مستخدم متزامن
    { duration: '30s', target: 50 }, // ضغط بـ 50 مستخدم متزامن
    { duration: '10s', target: 0 },  // تهدئة النزول
  ],
};

const BASE_URL = 'https://mahjoubonlinewebapp-production-7236.up.railway.app';

export default function () {
  // 1. اختبار رابط الدخول والصفحة الرئيسية لوحدها
  let loginResponse = http.get(`${BASE_URL}/`);
  check(loginResponse, {
    'Login / Home status is 200': (r) => r.status === 200,
  });

  sleep(1);

  // 2. اختبار رابط لوحة التحكم (التحكم والعمليات الحساسة/السحب) لوحدها
  let dashboardResponse = http.get(`${BASE_URL}/admin/dashboard/`);
  check(dashboardResponse, {
    'Dashboard status is 200 or requires auth': (r) => r.status === 200 || r.status === 302 || r.status === 401,
  });

  sleep(2);
}
