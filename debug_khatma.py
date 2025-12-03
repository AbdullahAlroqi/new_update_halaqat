
from app import app
from models import db, User, Role, KhatmaRequest
from datetime import datetime, date

def debug():
    with app.app_context():
        print("Starting debug...")
        
        # 1. Create/Get Employee
        employee = User.query.filter_by(national_id='1000000001').first()
        if not employee:
            employee = User(
                national_id='1000000001',
                name='Test Employee',
                role=Role.EMPLOYEE,
                gender='ذكر'
            )
            db.session.add(employee)
            db.session.commit()
            print(f"Created employee: {employee.id}")
        else:
            print(f"Found employee: {employee.id}")
            
        # 2. Create/Get Admin
        admin = User.query.filter_by(national_id='1000000002').first()
        if not admin:
            admin = User(
                national_id='1000000002',
                name='Test Admin',
                role=Role.MAIN_ADMIN,
                gender='ذكر'
            )
            db.session.add(admin)
            db.session.commit()
            print(f"Created admin: {admin.id}")
        else:
            print(f"Found admin: {admin.id}")
            
        # 3. Create Khatma Request
        req = KhatmaRequest(
            employee_id=employee.id,
            student_name='Test Student',
            khatma_date=date.today(),
            riwaya_type='Hafs',
            status='قيد الانتظار'
        )
        db.session.add(req)
        db.session.commit()
        print(f"Created request: {req.id}")
        
        # 4. Simulate Approval (Logic from routes_admin.py)
        try:
            print("Simulating approval...")
            khatma_req = KhatmaRequest.query.get(req.id)
            
            # Logic from approve_khatma_request
            if not khatma_req.original_date:
                khatma_req.original_date = khatma_req.khatma_date
            
            # new_date = ... (skip)
            
            khatma_req.status = 'مقبول'
            khatma_req.reviewed_by = admin.id
            khatma_req.reviewed_at = datetime.utcnow()
            khatma_req.review_notes = 'Test notes'
            
            print(f"Before commit: employee_id={khatma_req.employee_id}")
            db.session.commit()
            print("Commit successful!")
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            
        # Cleanup
        db.session.delete(req)
        # db.session.delete(employee)
        # db.session.delete(admin)
        db.session.commit()
        print("Cleanup done")

if __name__ == '__main__':
    debug()
