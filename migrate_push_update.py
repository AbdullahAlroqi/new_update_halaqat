"""
Database migration script to update push_subscriptions table
Adds national_id column for non-logged employee notifications
"""

from app import app
from models import db
from sqlalchemy import text

def migrate():
    """Add national_id column to push_subscriptions table"""
    with app.app_context():
        print("Starting database migration...")
        print("Adding national_id column to push_subscriptions table...")
        
        try:
            # Check if column already exists
            result = db.session.execute(text("PRAGMA table_info(push_subscriptions)"))
            columns = [row[1] for row in result]
            
            if 'national_id' not in columns:
                # Add the column
                db.session.execute(text(
                    "ALTER TABLE push_subscriptions ADD COLUMN national_id VARCHAR(10)"
                ))
               # Make user_id nullable
                # Note: SQLite doesn't support modifying columns directly,
                # so user_id should already be nullable from new model definition
                
                db.session.commit()
                print("✓ Migration completed successfully!")
                print("The national_id column has been added.")
            else:
                print("✓ Column already exists, no migration needed.")
                
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrate()
