from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import User
from app.utils.security_utils import (
    is_account_locked, 
    get_lockout_time_remaining, 
    log_login_attempt, 
    clear_successful_attempts,
    get_client_ip
)
from urllib.parse import urlparse
import time

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        ip_address = get_client_ip(request)
        user_agent = request.headers.get('User-Agent', '')[:256]
        
        # Check if account is locked due to too many failed attempts
        if is_account_locked(username, ip_address):
            lockout_info = get_lockout_time_remaining(username, ip_address)
            if lockout_info:
                flash(f'Too many failed login attempts. Please try again in {lockout_info["minutes"]} minutes and {lockout_info["seconds"]} seconds.', 'error')
                return render_template('auth/login.html', username=username)
        
        # Query user
        user = User.query.filter_by(username=username).first()
        
        # Timing attack prevention: always check password even if user doesn't exist
        if user is None:
            # Use a dummy hash check to maintain consistent timing
            from werkzeug.security import check_password_hash
            check_password_hash('dummy_hash_pbkdf2:sha256:260000$dummy$dummy', password)
            # Log failed attempt
            log_login_attempt(username, ip_address, success=False, user_agent=user_agent)
            flash('Invalid credentials. Please check your username and password.', 'error')
            return render_template('auth/login.html', username=username)
        
        # Check password
        if not user.check_password(password):
            # Log failed attempt
            log_login_attempt(username, ip_address, success=False, user_agent=user_agent)
            flash('Invalid credentials. Please check your username and password.', 'error')
            return render_template('auth/login.html', username=username)
        
        # Successful login
        log_login_attempt(username, ip_address, success=True, user_agent=user_agent)
        clear_successful_attempts(username)
        login_user(user)
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('dashboard.index')
        return redirect(next_page)
        
    return render_template('auth/login.html', username=None)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index')) # Changed from main.index
        
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Este nombre de usuario ya está en uso.')
            return redirect(url_for('auth.register'))
            
        user = User(username=username, email=email, role='seller')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('¡Felicitaciones, te has registrado!')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')
