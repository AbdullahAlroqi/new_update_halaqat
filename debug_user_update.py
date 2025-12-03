
from app import app
from models import db, User, Role, KhatmaRequest
from datetime import date

def debug():
    with app.app_context():
        print("Starting debug user update...")
        
        # 1. Create/Get Employee
        employee = User.query.filter_by(national_id='9999999999').first()
        if not employee:
            employee = User(
                national_id='9999999999',
                name='Debug Employee',
                role=Role.EMPLOYEE,
                gender='ذكر'
            )
            db.session.add(employee)
            db.session.commit()
            print(f"Created employee: {employee.id}")
        else:
            print(f"Found employee: {employee.id}")
            
        # 2. Create Khatma Request linked to employee
        req = KhatmaRequest.query.filter_by(student_name='Debug Student').first()
        if not req:
            req = KhatmaRequest(
                employee_id=employee.id,
                student_name='Debug Student',
                khatma_date=date.today(),
                riwaya_type='Hafs',
                status='قيد الانتظار'
            )
            db.session.add(req)
            db.session.commit()
            print(f"Created request: {req.id}")
        else:
            print(f"Found request: {req.id}")
            
        # 3. Simulate Update (Logic from routes_admin.py edit_employee)
        try:
            print("Simulating employee update...")
            # Reload employee
            emp = User.query.get(employee.id)
            
            # Update fields
            emp.name = 'Debug Employee Updated'
            emp.department = 'IT'
            
            print(f"Before commit. Employee ID: {emp.id}")
            print(f"Employee Khatma Requests: {emp.khatma_requests}")
            
            db.session.commit()
            print("Commit successful!")
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            
        # Cleanup
        # db.session.delete(req)
        # db.session.delete(employee)
        # db.session.commit()
        print("Cleanup done")

if __name__ == '__main__':
    debug()
