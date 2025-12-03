
from app import app
from models import db
from sqlalchemy import text

def migrate():
    """Add student_type and student_id columns to khatma_requests table"""
    with app.app_context():
        print("Starting database migration v2...")
        
        try:
            # Add student_type column
            print("Adding student_type column...")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE khatma_requests ADD COLUMN student_type VARCHAR(50)"))
                conn.commit()
                print("✓ Added student_type column")
        except Exception as e:
            print(f"! student_type column might already exist: {e}")

        try:
            # Add student_id column
            print("Adding student_id column...")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE khatma_requests ADD COLUMN student_id VARCHAR(20)"))
                conn.commit()
                print("✓ Added student_id column")
        except Exception as e:
            print(f"! student_id column might already exist: {e}")
            
        print("Migration completed!")

if __name__ == '__main__':
    migrate()
