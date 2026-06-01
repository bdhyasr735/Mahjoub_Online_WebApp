from apps import create_app

# هذا هو المتغير 'app' الذي يبحث عنه Vercel
app = create_app()

if __name__ == "__main__":
    # تشغيل التطبيق محلياً
    app.run(debug=True)
