from apps import create_app

app = create_app()

if __name__ == '__main__':
    # يجب تحديد الهوست 0.0.0.0 للعمل داخل الحاويات (Docker/Containers)
    # والمنفذ 8080 كما هو ظاهر في سجلاتك
    app.run(host='0.0.0.0', port=8080)
