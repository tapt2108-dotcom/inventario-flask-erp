const API_URL = '/api/products';

// DOM Elements
const productForm = document.getElementById('productForm');
const productList = document.getElementById('productList');

// Load products on startup
document.addEventListener('DOMContentLoaded', fetchProducts);

// Handle Form Submit
productForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('name').value;
    const quantity = parseInt(document.getElementById('quantity').value);
    const price = parseFloat(document.getElementById('price').value);

    const product = { name, quantity, price };

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(product)
        });

        if (response.ok) {
            productForm.reset();
            fetchProducts(); // Refresh list
        }
    } catch (error) {
        console.error('Error adding product:', error);
    }
});

// Fetch and Display Products
async function fetchProducts() {
    try {
        const response = await fetch(API_URL);
        const products = await response.json();
        renderProducts(products);
    } catch (error) {
        console.error('Error fetching products:', error);
    }
}

function renderProducts(products) {
    productList.innerHTML = '';
    
    products.forEach(product => {
        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <h3>${product.name}</h3>
            <div class="product-details">
                <p>Cantidad: ${product.quantity}</p>
                <p>Precio: $${product.price.toFixed(2)}</p>
            </div>
            <button class="btn-delete" onclick="deleteProduct(${product.id})">Eliminar</button>
        `;
        productList.appendChild(card);
    });
}

// Delete Product
window.deleteProduct = async (id) => {
    if (!confirm('¿Estás seguro de eliminar este producto?')) return;

    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            fetchProducts();
        }
    } catch (error) {
        console.error('Error deleting product:', error);
    }
};
