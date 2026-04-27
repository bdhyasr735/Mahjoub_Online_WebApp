from core import app

if __name__ == '__main__':
    # ملاحظة: Railway يمرر المنفذ تلقائياً عبر متغيرات البيئة
    # ولكن host='0.0.0.0' ضرورية لكي يسمح السيرفر بالاتصالات الخارجية
    app.run(host='0.0.0.0', port=5000, debug=True)
