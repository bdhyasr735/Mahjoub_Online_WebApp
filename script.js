import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 200 }, // تصاعد تدريجي إلى 200 مستخدم متزامن
    { duration: '1m', target: 1000 },  // الوصول والضغط بـ 1000 مستخدم متزامن
    { duration: '20s', target: 0 },   // تهدئة النزول والانخفاض التدريجي
  ],
};

const BASE_URL = 'https://mahjoubonlinewebapp-production-7236.up.railway.app';

export default function () {
  // 1. اختبار الصفحة الرئيسية للبلاتفورم
  let homeResponse = http.get(`${BASE_URL}/`);
  check(homeResponse, {
    'Home status is 200 or redirect': (r) => r.status === 200 || r.status === 302,
  });

  sleep(1);

  // 2. اختبار البوابة الإدارية السرية (Sovereign HQ)
  let adminResponse = http.get(`${BASE_URL}/m7jb_sovereign_hq_v2_99x`);
  check(adminResponse, {
    'Admin Sovereign HQ status is 200 or requires auth': (r) => r.status === 200 || r.status === 302 || r.status === 401,
  });

  sleep(1);

  // 3. اختبار بوابة دخول الموردين (Supplier Login Portal)
  let supplierResponse = http.get(`${BASE_URL}/supplier/login`);
  check(supplierResponse, {
    'Supplier Login status is 200 or redirect': (r) => r.status === 200 || r.status === 302,
  });

  sleep(2);
}
