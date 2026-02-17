from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Category
from app.utils.decorators import admin_required
from app import db

bp = Blueprint('categories', __name__, url_prefix='/categories')

@bp.route('/')
@login_required
def list_categories():
    categories = Category.query.all()
    return render_template('categories/list.html', categories=categories, title='Categorías')

@bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        
        existing = Category.query.filter_by(name=name).first()
        if existing:
            flash('Ya existe una categoría con ese nombre.')
            return redirect(url_for('categories.add_category'))
        
        new_category = Category(name=name)
        db.session.add(new_category)
        db.session.commit()
        flash('Categoría agregada exitosamente.')
        return redirect(url_for('categories.list_categories'))
    
    return render_template('categories/form.html', title='Agregar Categoría')

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form['name']
        
        existing = Category.query.filter_by(name=name).first()
        if existing and existing.id != id:
            flash('Ya existe una categoría con ese nombre.')
            return redirect(url_for('categories.edit_category', id=id))
            
        category.name = name
        db.session.commit()
        flash('Categoría actualizada exitosamente.')
        return redirect(url_for('categories.list_categories'))
        
    return render_template('categories/form.html', category=category, title='Editar Categoría')

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_category(id):
        
    category = Category.query.get_or_404(id)
    
    # Optional: Check if products exist in category before deleting, or let them be nullified/cascaded
    if category.products:
        flash('No se puede eliminar la categoría porque tiene productos asociados.')
        return redirect(url_for('categories.list_categories'))

    db.session.delete(category)
    db.session.commit()
    flash('Categoría eliminada exitosamente.')
    return redirect(url_for('categories.list_categories'))
