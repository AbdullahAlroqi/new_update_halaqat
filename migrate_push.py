"""
Database migration script to add push_subscriptions table
Run this script to update the database
"""

from app import app
from models import db, PushSubscription

def migrate():
    """Add push_subscriptions table to the database"""
    with app.app_context():
        print("Starting database migration...")
        print("Adding push_subscriptions table...")
        
        # Create the new table
        db.create_all()
        
        print("✓ Migration completed successfully!")
        print("The push_subscriptions table has been added to the database.")
        print("\nPush notifications are now enabled!")
        print("Users will be prompted to allow notifications when they log in.")

if __name__ == '__main__':
    migrate()
