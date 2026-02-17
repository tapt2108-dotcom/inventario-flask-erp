from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Setting, Product
from app.utils.decorators import admin_required
from app import db

bp = Blueprint('settings', __name__, url_prefix='/settings')

def get_exchange_rate():
    setting = Setting.query.get('exchange_rate')
    if setting:
        return float(setting.value)
    return 1.0

@bp.route('/rate', methods=['POST'])
@login_required
@admin_required
def update_rate():

    try:
        new_rate = float(request.form['exchange_rate'])
        setting = Setting.query.get('exchange_rate')
        if not setting:
            setting = Setting(key='exchange_rate', value=str(new_rate))
            db.session.add(setting)
        else:
            setting.value = str(new_rate)
        
        # Update all products prices
        products = Product.query.all()
        for product in products:
            if product.price_usd: # Only if price_usd is set
                product.price = product.price_usd * new_rate
        
        db.session.commit()
        flash(f'Tasa de cambio actualizada a {new_rate}. Precios recalculados.')
    except ValueError:
        flash('Por favor ingrese una tasa válida.')
    
    # Redirect back to where the request came from or dashboard
    return redirect(request.referrer or url_for('dashboard.index')) # Changed from main.index
