from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Product, InventoryMovement
from app.services.inventory_service import InventoryService
from app.utils.decorators import admin_required
from app import db

bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@bp.route('/')
@login_required
def index():
    movements = InventoryMovement.query.order_by(InventoryMovement.date.desc()).all()
    return render_template('inventory/index.html', movements=movements, title='Movimientos de Inventario')

@bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_movement():
    if request.method == 'POST':
        product_id = request.form['product_id']
        movement_type = request.form['type']
        quantity = int(request.form['quantity'])
        description = request.form['description']
        
        try:
            if movement_type == 'entrada':
                InventoryService.add_stock(product_id, quantity, description, current_user.id)
            elif movement_type == 'salida':
                InventoryService.remove_stock(product_id, quantity, description, current_user.id)
            elif movement_type == 'ajuste':
                # For adjustment, we treat it as setting the new stock level
                InventoryService.set_stock(product_id, quantity, description, current_user.id)
                
            db.session.commit()
            flash('Movimiento registrado exitosamente.')
            return redirect(url_for('inventory.index'))
            
        except ValueError as e:
            db.session.rollback()
            flash(f'Error: {str(e)}')
            return redirect(url_for('inventory.add_movement'))
            
    products = Product.query.filter_by(is_active=True).order_by(Product.name).all()
    return render_template('inventory/form.html', title='Registrar Movimiento', products=products)
