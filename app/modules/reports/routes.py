from flask import Blueprint, render_template
from flask_login import login_required
from io import BytesIO
from flask import make_response
from app.utils.pdf_utils import generate_inventory_pdf, generate_sales_pdf
from app.models import Product, Sale, InventoryMovement
from datetime import datetime, timedelta
from flask import request
from app.utils.decorators import admin_required
from app import db

bp = Blueprint('reports', __name__, url_prefix='/reports')

@bp.route('/')
@login_required
@admin_required
def index():
    return render_template('dashboard/reports.html', title='Reportes')

@bp.route('/no-rotation')
@login_required
@admin_required
def no_rotation():
    days = request.args.get('days', 60, type=int)
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Subquery: Products with movements since cutoff_date
    moved_products_query = db.session.query(InventoryMovement.product_id).filter(
        InventoryMovement.date >= cutoff_date
    )
    
    # Products NOT in the subquery AND Active
    no_rotation_products = Product.query.filter(
        Product.is_active == True,
        ~Product.id.in_(moved_products_query)
    ).all()
    
    # Enrich with last movement date
    results = []
    for p in no_rotation_products:
        last_movement = InventoryMovement.query.filter_by(product_id=p.id).order_by(InventoryMovement.date.desc()).first()
        results.append({
            'product': p,
            'last_movement_date': last_movement.date if last_movement else None
        })
        
    return render_template('reports/no_rotation.html', 
                         products=results, 
                         days=days, 
                         title='Productos Sin Rotación')

@bp.route('/download/inventory')
@login_required
@admin_required
def download_inventory_report():
    products = Product.query.all()
    pdf = generate_inventory_pdf(products)
    
    pdf_output = pdf.output()
    out = BytesIO(pdf_output)

    response = make_response(out.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=inventario.pdf'
    return response

@bp.route('/download/sales')
@login_required
@admin_required
def download_sales_report():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    sales = Sale.query.filter(Sale.date >= start_date).order_by(Sale.date).all()
    
    sales_by_day = {}
    current = start_date
    while current <= end_date:
        sales_by_day[current.strftime('%Y-%m-%d')] = 0
        current += timedelta(days=1)
        
    for sale in sales:
        day_str = sale.date.strftime('%Y-%m-%d')
        if day_str in sales_by_day:
            sales_by_day[day_str] += sale.total_usd
            
    sales_data = {
        'labels': list(sales_by_day.keys()),
        'values': list(sales_by_day.values())
    }
    
    pdf = generate_sales_pdf(sales_data)
    out = BytesIO(pdf.output())
    
    response = make_response(out.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=ventas.pdf'
    return response
