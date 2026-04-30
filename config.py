import os

class Config:
    # الرابط الجديد الذي زودتني به لربط الترسانة بقاعدة Render
    SQLALCHEMY_DATABASE_URI = 'postgresql://mahjoub_online_1_db_user:S7dxtVGcKwrsM1QEzGOuPPcRL8dKxgXk@dpg-d79tuthr0fns73epej4g-a.oregon-postgres.render.com/mahjoub_online_1_db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'MAHJOUB_SECRET_KEY_2026'
