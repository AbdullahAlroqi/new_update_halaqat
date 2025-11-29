"""
Script to create test admin and supervisor users
"""
from app import app
from models import db, User, Role

def create_test_users():
    """Create test admin and supervisor"""
    with app.app_context():
        # Create Admin
        admin = User.query.filter_by(national_id='1111111111').first()
        if not admin:
            admin = User(
                name='مدير النظام',
                national_id='1111111111',
                role=Role.MAIN_ADMIN,
                gender='ذكر',
                phone='0500000000',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin created!")
        else:
            print("✓ Admin exists")
        
        # Create Supervisor
        supervisor = User.query.filter_by(national_id='2222222222').first()
        if not supervisor:
            supervisor = User(
                name='المشرف الرئيسي',
                national_id='2222222222',
                role=Role.MAIN_SUPERVISOR,
                gender='ذكر',
                phone='0511111111',
                is_active=True
            )
            supervisor.set_password('super123')
            db.session.add(supervisor)
            db.session.commit()
            print("✅ Supervisor created!")
        else:
            print("✓ Supervisor exists")
        
        print("\n" + "="*60)
        print("LOGIN CREDENTIALS:")
        print("="*60)
        print("ADMIN:")
        print("  National ID: 1111111111")
        print("  Password: admin123")
        print("\nSUPERVISOR:")
        print("  National ID: 2222222222")
        print("  Password: super123")
        print("="*60)
        print(f"\nLogin at: http://localhost:5000/login")

if __name__ == '__main__':
    create_test_users()
