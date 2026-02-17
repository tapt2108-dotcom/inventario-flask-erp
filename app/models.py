from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)  # Keep for backward compatibility during migration
    role = db.Column(db.String(20), default='seller', nullable=False)  # 'admin' or 'seller'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role):
        """Check if user has a specific role"""
        return self.role == role
    
    @property
    def is_admin_role(self):
        """Property to check if user is admin (for template usage)"""
        return self.role == 'admin'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Float, nullable=False, default=0.0)
    price_usd = db.Column(db.Float, nullable=True, default=0.0)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    
    # New fields for Auto Parts
    part_number = db.Column(db.String(50), unique=True, nullable=True)
    manufacturer = db.Column(db.String(50), nullable=True)
    compatibility = db.Column(db.Text, nullable=True) # JSON or comma-separated list of compatible models
    location = db.Column(db.String(50), nullable=True) # Warehouse location
    min_stock = db.Column(db.Integer, default=0)
    # New fields for Auto Parts (requested)
    brand = db.Column(db.String(50), nullable=True)
    vehicle_type = db.Column(db.String(20), nullable=True) # 'Auto', 'Moto', etc.
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'quantity': self.quantity,
            'price': self.price,
            'price_usd': self.price_usd,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'part_number': self.part_number,
            'manufacturer': self.manufacturer,
            'brand': self.brand,
            'vehicle_type': self.vehicle_type,
            'compatibility': self.compatibility,
            'location': self.location,
            'min_stock': self.min_stock
        }

class InventoryMovement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False) # 'entrada', 'salida', 'ajuste'
    quantity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    description = db.Column(db.String(200), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    product = db.relationship('Product', backref=db.backref('movements', lazy=True))
    user = db.relationship('User', backref=db.backref('movements', lazy=True))

class Setting(db.Model):
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(100))

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    total_bs = db.Column(db.Float, nullable=False, default=0.0)
    total_usd = db.Column(db.Float, nullable=False, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Track who created the sale
    items = db.relationship('SaleItem', backref='sale', lazy=True, cascade="all, delete-orphan")
    user = db.relationship('User', backref=db.backref('sales', lazy=True))

class SaleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False) # Guardamos el nombre por si se borra el producto
    quantity = db.Column(db.Integer, nullable=False)
    price_at_moment_bs = db.Column(db.Float, nullable=False)
    price_at_moment_usd = db.Column(db.Float, nullable=False)

class LoginAttempt(db.Model):
    """Track login attempts for security monitoring and rate limiting"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, index=True)  # Not FK to track non-existent users too
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 can be up to 45 chars
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False, index=True)
    success = db.Column(db.Boolean, default=False, nullable=False)
    user_agent = db.Column(db.String(256), nullable=True)  # Browser/device info

