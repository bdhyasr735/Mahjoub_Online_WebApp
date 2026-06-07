#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
# تنفيذ الميجريشن لإنشاء الجداول في قاعدة البيانات
flask db upgrade
