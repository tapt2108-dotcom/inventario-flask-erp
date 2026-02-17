from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Por favor inicia sesión para acceder a esta página.'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)

    # Register Blueprints
    from app.modules.dashboard.routes import bp as dashboard_bp
    from app.modules.reports.routes import bp as reports_bp
    from app.modules.users.routes import bp as auth_bp
    from app.modules.products.routes import bp as products_bp
    from app.modules.products.categories import bp as categories_bp
    from app.modules.settings.routes import bp as settings_bp
    from app.modules.api.routes import bp as api_bp
    from app.modules.sales.routes import bp as sales_bp
    from app.modules.inventory.routes import bp as inventory_bp
    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(products_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(inventory_bp)

    from app.models import Setting
    @app.context_processor
    def inject_rate():
        try:
            s = Setting.query.get('exchange_rate')
            rate = float(s.value) if s else 1.0
        except:
            rate = 1.0
        return dict(current_rate=rate)

    return app
