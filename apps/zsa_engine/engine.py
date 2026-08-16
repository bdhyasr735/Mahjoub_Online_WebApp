import numpy as np
from scipy.sparse import csr_matrix

class ZSAEngine:
    def __init__(self):
        # تهيئة المعاملات الرياضية الأساسية للمحرك
        self.beta = 0.01

    def process_window_data(self, raw_data_list):
        """
        دالة معالجة البيانات عبر مصفوفة الإلسقاط المتعامد للحصول على سرعة فائقة
        """
        if not raw_data_list:
            return []
        
        try:
            # تحويل البيانات الخام إلى مصفوفة متناثرة (Sparse Matrix) لتوفير الذاكرة وسرعة الحساب
            data_array = np.array(raw_data_list, dtype=float)
            sparse_data = csr_matrix(data_array)
            
            # تطبيق دالة الإلسقاط وحساب الناتج الفوري بزمن خطي
            projection_matrix = sparse_data.toarray() * (1 - self.beta)
            results = projection_matrix.sum(axis=1).tolist()
            
            return results
        except Exception as e:
            # معالجة أي استثناء داخلي في الحسابات
            raise ValueError(f"ZSA Processing Error: {str(e)}")

# كائن عام لاستخدامه داخل مسارات الـ Flask
zsa_core = ZSAEngine()
