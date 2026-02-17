from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import Sale, SaleItem, Product, Setting
from app import db
from datetime import datetime

bp = Blueprint('sales', __name__, url_prefix='/sales')

def get_rate():
    s = Setting.query.get('exchange_rate')
    return float(s.value) if s else 1.0

from app.services.inventory_service import InventoryService

@bp.route('/')
@login_required
def index():
    sales = Sale.query.order_by(Sale.date.desc()).all()
    
    # Calcular resumen
    now = datetime.now()
    today_total = sum(s.total_usd for s in sales if s.date.date() == now.date())
    month_total = sum(s.total_usd for s in sales if s.date.month == now.month and s.date.year == now.year)
    month_count = sum(1 for s in sales if s.date.month == now.month and s.date.year == now.year)
    
    return render_template('sales/index.html', sales=sales, 
                         today_total=today_total, 
                         month_total=month_total, 
                         month_count=month_count)

@bp.route('/new')
@login_required
def new_sale():
    products = Product.query.filter(Product.quantity > 0, Product.is_active == True).all()
    rate = get_rate()
    return render_template('sales/create.html', products=products, rate=rate)

@bp.route('/create', methods=['POST'])
@login_required
def create_sale():
    data = request.get_json()
    items_data = data.get('items', [])
    
    if not items_data:
        return jsonify({'error': 'No hay items en la venta'}), 400

    total_bs = 0
    total_usd = 0
    rate = get_rate()
    
    new_sale = Sale(total_bs=0, total_usd=0, user_id=current_user.id)
    db.session.add(new_sale)
    db.session.flush() # Para obtener ID
    
    for item in items_data:
        product_id = item['product_id']
        quantity = int(item['quantity'])
        
        product = Product.query.get(product_id)
        if not product:
            continue
            
        # Use InventoryService to remove stock
        try:
            InventoryService.remove_stock(
                product_id=product.id,
                quantity=quantity,
                description=f"Venta #{new_sale.id}",
                user_id=current_user.id
            )
        except ValueError as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
        
        # Calcular precios
        price_usd = product.price_usd if product.price_usd else 0
        price_bs = price_usd * rate
        
        sale_item = SaleItem(
            sale_id=new_sale.id,
            product_id=product.id,
            product_name=product.name,
            quantity=quantity,
            price_at_moment_bs=price_bs,
            price_at_moment_usd=price_usd
        )
        db.session.add(sale_item)
        
        total_bs += price_bs * quantity
        total_usd += price_usd * quantity

    new_sale.total_bs = total_bs
    new_sale.total_usd = total_usd
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'sale_id': new_sale.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>')
@login_required
def view_sale(id):
    sale = Sale.query.get_or_404(id)
    return render_template('sales/details.html', sale=sale, title=f'Venta #{sale.id}')
