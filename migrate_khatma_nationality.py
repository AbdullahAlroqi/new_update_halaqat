"""
Database migration script to update khatma_requests table
Adds nationality column for student nationality
"""

from app import app
from models import db
from sqlalchemy import text

def migrate():
    """Add nationality column to khatma_requests table"""
    with app.app_context():
        print("Starting database migration...")
        print("Adding nationality column to khatma_requests table...")
        
        try:
            # Check if column already exists
            result = db.session.execute(text("PRAGMA table_info(khatma_requests)"))
            columns = [row[1] for row in result]
            
            if 'nationality' not in columns:
                # Add the column
                db.session.execute(text(
                    "ALTER TABLE khatma_requests ADD COLUMN nationality VARCHAR(100)"
                ))
                
                db.session.commit()
                print("✓ Migration completed successfully!")
                print("The nationality column has been added.")
            else:
                print("✓ Column already exists, no migration needed.")
                
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrate()
