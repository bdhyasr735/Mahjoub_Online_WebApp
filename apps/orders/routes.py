# 📂 apps/orders/routes.py
from flask import Blueprint, render_template, request, jsonify
from apps.models.order_db import Order
from apps.extensions import db
import requests
import logging
from flask_login import login_required

logger = logging.getLogger(__name__)
orders_bp = Blueprint('orders', __name__, template_folder='templates')

class OrdersEngine:
    def __init__(self):
        self.api_url = "https://mahjoub.online/admin/graphql"
        self.api_key = "qmr_e063f7f4-ed44-4c86-b105-8405326b9eb9"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}", 
            "Content-Type": "application/json"
        }

    def fetch_orders_from_qumra(self):
        # الاستعلام مصحح بالأسماء الحقيقية المستخرجة من الـ Schema
        payload = {
            "query": """
            query {
                findAllOrders(input: { limit: 50, page: 1 }) {
                    data {
                        _id
                        totalPrice
                        status { name }
                        account { name }
                        createdAt
                    }
                }
            }
            """
        }
        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers, timeout=15)
            result = response.json()
            return result.get('data', {}).get('findAllOrders', {}).get('data', [])
        except Exception as e:
            print(f"DEBUG: خطأ في الاتصال: {str(e)}")
            return []

    def sync_orders_to_db(self):
        orders = self.fetch_orders_from_qumra()
        count = 0
        for item in orders:
            order_id = str(item.get('_id'))
            if not order_id: continue
            
            order = Order.query.filter_by(order_id_qumra=order_id).first() or Order(order_id_qumra=order_id)
            
            # تحديث الحقول بالأسماء المعتمدة في Schema قمرة
            order.total = float(item.get('totalPrice', 0))
            
            status_obj = item.get('status')
            order.status = status_obj.get('name', 'pending') if isinstance(status_obj, dict) else 'pending'
            
            account_obj = item.get('account')
            order.customer_name = account_obj.get('name', 'غير معروف') if isinstance(account_obj, dict) else 'غير معروف'
            
            order.raw_data = item 
            db.session.add(order)
            count += 1
        
        db.session.commit()
        return count

@orders_bp.route('/admin/orders', methods=['GET'])
@login_required
def orders_dashboard():
    page = request.args.get('page', 1, type=int)
    pagination = Order.query.order_by(Order.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/orders_dashboard.html', orders=pagination.items, pagination=pagination)

@orders_bp.route('/admin/orders/sync', methods=['POST'])
@login_required
def sync_orders():
    try:
        engine = OrdersEngine()
        count = engine.sync_orders_to_db()
        return jsonify({'success': True, 'message': f'تمت المزامنة بنجاح، تم إضافة {count} طلب.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@orders_bp.route('/admin/orders/update-status', methods=['POST'])
@login_required
def update_order_status():
    data = request.json
    order = Order.query.get(data.get('orderId'))
    if order:
        order.status = data.get('value')
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 404
