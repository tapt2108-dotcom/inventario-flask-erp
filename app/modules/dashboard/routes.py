from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Product, InventoryMovement
from app import db
from datetime import datetime, timedelta

bp = Blueprint('dashboard', __name__) 

@bp.route('/')
@login_required
def index():
    # Low stock alert: Active products with quantity <= min_stock
    low_stock_products = Product.query.filter(
        Product.is_active == True,
        Product.quantity <= Product.min_stock
    ).all()

    # No Rotation Alert (Default > 60 days)
    cutoff_date = datetime.now() - timedelta(days=60)
    moved_products_query = db.session.query(InventoryMovement.product_id).filter(
        InventoryMovement.date >= cutoff_date
    )
    no_rotation_count = Product.query.filter(
        Product.is_active == True,
        ~Product.id.in_(moved_products_query)
    ).count()
    
    return render_template('dashboard/index.html', 
                         title='Dashboard', 
                         low_stock_products=low_stock_products,
                         no_rotation_count=no_rotation_count)
