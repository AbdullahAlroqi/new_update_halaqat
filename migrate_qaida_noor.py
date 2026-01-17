"""
Database migration script to create qaida_noor_requests table
"""

from app import app
from models import db
from sqlalchemy import text

def migrate():
    """Create qaida_noor_requests table"""
    with app.app_context():
        print("Starting database migration...")
        print("Creating qaida_noor_requests table...")
        
        try:
            # Create table
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS qaida_noor_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    student_name VARCHAR(100) NOT NULL,
                    student_type VARCHAR(50),
                    student_id VARCHAR(20),
                    nationality VARCHAR(100),
                    request_date DATE NOT NULL,
                    additional_info TEXT,
                    status VARCHAR(20) DEFAULT 'قيد الانتظار',
                    reviewed_by INTEGER,
                    reviewed_at DATETIME,
                    review_notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES users (id),
                    FOREIGN KEY (reviewed_by) REFERENCES users (id)
                )
            """))
            
            db.session.commit()
            print("✓ Migration completed successfully!")
            print("The qaida_noor_requests table has been created.")
                
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrate()
