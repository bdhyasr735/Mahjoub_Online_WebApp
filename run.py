from core import create_app

app = create_app()

if __name__ == "__main__":
    # بايثون سيتعرف على بورت Railway آلياً
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
