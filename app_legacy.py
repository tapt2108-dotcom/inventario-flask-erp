from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configuración de la Base de Datos
# Guardamos la DB en la carpeta 'instance' para mantener orden
db_path = os.path.join(app.instance_path, 'inventory.db')
# Aseguramos que la carpeta instance exista
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de Datos (La estructura de nuestra tabla de productos)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Float, nullable=False, default=0.0)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'quantity': self.quantity,
            'price': self.price
        }

# Rutas de la Aplicación

# 1. Ruta Principal: Sirve el HTML
@app.route('/')
def index():
    return render_template('index.html')

# 2. API: Obtener todos los productos
@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])

# 3. API: Crear un nuevo producto
@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.json
    new_product = Product(
        name=data['name'], 
        quantity=data.get('quantity', 0), 
        price=data.get('price', 0.0)
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify(new_product.to_dict()), 201

# 4. API: Borrar un producto
@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return '', 204

# 5. API: Actualizar un producto
@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.json
    product.name = data.get('name', product.name)
    product.quantity = data.get('quantity', product.quantity)
    product.price = data.get('price', product.price)
    db.session.commit()
    return jsonify(product.to_dict())

# Inicializar la base de datos al arrancar
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
