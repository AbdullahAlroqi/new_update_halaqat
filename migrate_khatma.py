"""
Database migration script to add khatma_requests table
Run this script to update the database with the new table
"""

from app import app
from models import db, KhatmaRequest

def migrate():
    """Add khatma_requests table to the database"""
    with app.app_context():
        print("Starting database migration...")
        print("Adding khatma_requests table...")
        
        # Create the new table
        db.create_all()
        
        print("✓ Migration completed successfully!")
        print("The khatma_requests table has been added to the database.")

if __name__ == '__main__':
    migrate()
