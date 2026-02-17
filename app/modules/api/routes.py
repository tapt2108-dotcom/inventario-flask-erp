from flask import Blueprint, jsonify, request
from app.models import Product, Setting, Sale
from app import db
from flask_login import login_required, current_user
from datetime import datetime, timedelta

bp = Blueprint('api', __name__, url_prefix='/api')

def get_rate():
    s = Setting.query.get('exchange_rate')
    return float(s.value) if s else 1.0

@bp.route('/products', methods=['GET'])
@login_required
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])

@bp.route('/products', methods=['POST'])
@login_required
def add_product():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    name = data.get('name')
    quantity = data.get('quantity', 0)
    price_usd = data.get('price', 0.0) # JS envía 'price' como el valor en USD
    
    if not name:
        return jsonify({'error': 'Missing name'}), 400
        
    rate = get_rate()
    price_ves = float(price_usd) * rate
    
    new_product = Product(
        name=name,
        quantity=int(quantity),
        price=price_ves,
        price_usd=float(price_usd)
    )
    
    db.session.add(new_product)
    db.session.commit()
    
    return jsonify(new_product.to_dict()), 201

@bp.route('/products/<int:id>', methods=['DELETE'])
@login_required
def delete_product(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({'success': True})

@bp.route('/sales/stats', methods=['GET'])
@login_required
def get_sales_stats():
    # Obtener ventas de los últimos 7 días
    end_date = datetime.now()
    start_date = end_date - timedelta(days=6)
    
    sales = Sale.query.filter(Sale.date >= start_date).all()
    
    daily_stats = {}
    current = start_date
    while current <= end_date:
        daily_stats[current.strftime('%Y-%m-%d')] = 0
        current += timedelta(days=1)
        
    for sale in sales:
        date_str = sale.date.strftime('%Y-%m-%d')
        if date_str in daily_stats:
            daily_stats[date_str] += sale.total_usd
            
    return jsonify({
        'labels': list(daily_stats.keys()),
        'values': list(daily_stats.values())
    })
