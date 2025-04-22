
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(email='admin@admin.com').first()
        if not admin:
            admin = User(
                name='Admin',
                email='admin@admin.com',
                password=generate_password_hash('admin123', method='pbkdf2:sha256'),
                is_verified=True,
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
    
    app.run(debug=True)
