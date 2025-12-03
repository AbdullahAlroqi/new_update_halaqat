"""
Clear all push subscriptions to force re-subscription
This will help if there's a mismatch between VAPID keys and subscriptions
"""

from app import app
from models import db, PushSubscription

def clear_subscriptions():
    with app.app_context():
        print("Clearing all push subscriptions...")
        
        # Get count before
        count = PushSubscription.query.count()
        print(f"Found {count} subscriptions")
        
        # Delete all
        PushSubscription.query.delete()
        db.session.commit()
        
        print("✓ All subscriptions cleared")
        print("\nNext steps:")
        print("1. Restart the Flask app")
        print("2. Open the site in your browser")
        print("3. Click the notification bell icon")
        print("4. Allow notifications when prompted")
        print("5. Test by submitting a leave or khatma request")

if __name__ == '__main__':
    clear_subscriptions()
