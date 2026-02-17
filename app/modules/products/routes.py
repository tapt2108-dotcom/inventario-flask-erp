from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Product, Setting, Category
from app.utils.decorators import admin_required
from app import db

bp = Blueprint('products', __name__, url_prefix='/products')

def get_rate():
    s = Setting.query.get('exchange_rate')
    return float(s.value) if s else 1.0

@bp.route('/')
@login_required
def list_products():
    search_query = request.args.get('search')
    if search_query:
        products = Product.query.filter(
            Product.is_active == True,
            (Product.name.ilike(f'%{search_query}%')) |
            (Product.part_number.ilike(f'%{search_query}%')) |
            (Product.compatibility.ilike(f'%{search_query}%')) |
            (Product.manufacturer.ilike(f'%{search_query}%'))
        ).all()
    else:
        products = Product.query.filter_by(is_active=True).all()
    return render_template('products/list.html', products=products, title='Productos', search_query=search_query)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form.get('quantity', 0, type=int)
        price_usd = request.form.get('price_usd', 0.0, type=float)
        category_id = request.form.get('category_id', type=int)
        
        # New fields
        part_number = request.form.get('part_number')
        manufacturer = request.form.get('manufacturer')
        compatibility = request.form.get('compatibility')
        location = request.form.get('location')
        min_stock = request.form.get('min_stock', 0, type=int)
        
        # Calculate VES price
        rate = get_rate()
        price = price_usd * rate
        
        new_product = Product(
            name=name, 
            quantity=quantity, 
            price=price, 
            price_usd=price_usd, 
            category_id=category_id,
            part_number=request.form.get('part_number'),
            manufacturer=request.form.get('manufacturer'),
            brand=request.form.get('brand'),
            vehicle_type=request.form.get('vehicle_type'),
            compatibility=request.form.get('compatibility'),
            location=request.form.get('location'),
            min_stock=int(request.form.get('min_stock', 0))
        )
        try:
            db.session.add(new_product)
            db.session.commit()
            flash('Producto agregado exitosamente.')
            return redirect(url_for('products.list_products'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar producto: {str(e)}')
            return redirect(url_for('products.add_product'))
    
    categories = Category.query.all()
    return render_template('products/form.html', title='Agregar Producto', categories=categories)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.quantity = request.form.get('quantity', 0, type=int)
        product.price_usd = request.form.get('price_usd', 0.0, type=float)
        product.category_id = request.form.get('category_id')
        product.part_number = request.form['part_number']
        product.manufacturer = request.form['manufacturer']
        product.brand = request.form['brand']
        product.vehicle_type = request.form['vehicle_type']
        product.compatibility = request.form['compatibility']
        product.location = request.form['location']
        product.min_stock = int(request.form.get('min_stock', 0))
        
        # Recalculate VES price (if price_usd changed)
        rate = get_rate()
        product.price = product.price_usd * rate
        
        try:
            db.session.commit()
            flash('Producto actualizado exitosamente.')
            return redirect(url_for('products.list_products'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar producto: {str(e)}')
            # fall through to render template with error
        
    categories = Category.query.all()
    # Inject current rate for the template calculation
    s = Setting.query.get('exchange_rate')
    current_rate = float(s.value) if s else 1.0
    
    return render_template('products/form.html', title='Editar Producto', product=product, categories=categories, current_rate=current_rate)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_product(id):
        
    product = Product.query.get_or_404(id)
    product.is_active = False
    db.session.commit()
    flash('Producto eliminado exitosamente (archivado).')
    return redirect(url_for('products.list_products'))
