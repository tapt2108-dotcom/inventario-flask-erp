from app import create_app, db
import app.models  # Import models to ensure they are known to SQLAlchemy

app = create_app()

with app.app_context():
    db.create_all()
    
    # Create an admin user if not exists (Optional, for easy access)
    from app.models import User
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@example.com', is_admin=True, role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: admin / admin123")

if __name__ == '__main__':
    app.run(debug=True)
