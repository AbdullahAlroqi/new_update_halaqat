"""
Diagnostic script for push notifications
This will help identify why notifications are not being delivered
"""

from app import app
from models import db, PushSubscription, User, Role
import push_service
from config import Config
import json

def diagnose_push_notifications():
    with app.app_context():
        print("=" * 60)
        print("PUSH NOTIFICATION DIAGNOSTIC REPORT")
        print("=" * 60)
        
        # 1. Check VAPID Configuration
        print("\n1. VAPID Configuration:")
        print(f"   Public Key: {Config.VAPID_PUBLIC_KEY[:50]}...")
        print(f"   Private Key: {Config.VAPID_PRIVATE_KEY[:20]}...")
        print(f"   Claims Sub: {Config.VAPID_CLAIMS_SUB}")
        
        # 2. Check for active subscriptions
        print("\n2. Active Subscriptions:")
        all_subs = PushSubscription.query.filter_by(is_active=True).all()
        print(f"   Total active subscriptions: {len(all_subs)}")
        
        for sub in all_subs:
            print(f"\n   Subscription ID: {sub.id}")
            print(f"   User ID: {sub.user_id}")
            print(f"   National ID: {sub.national_id}")
            print(f"   Created: {sub.created_at}")
            
            # Parse subscription JSON
            try:
                sub_data = json.loads(sub.subscription_json)
                print(f"   Endpoint: {sub_data.get('endpoint', 'N/A')[:80]}...")
                print(f"   Has keys: {('keys' in sub_data)}")
            except Exception as e:
                print(f"   ERROR parsing subscription JSON: {e}")
        
        # 3. Check admin/supervisor users
        print("\n3. Admin/Supervisor Users:")
        admins = User.query.filter(
            User.role.in_([Role.MAIN_ADMIN, Role.SUB_ADMIN, Role.MAIN_SUPERVISOR])
        ).all()
        print(f"   Total admins/supervisors: {len(admins)}")
        
        for admin in admins:
            print(f"\n   User: {admin.name} (ID: {admin.id})")
            print(f"   Role: {admin.role}")
            print(f"   National ID: {admin.national_id}")
            
            # Check if they have subscriptions
            user_subs = PushSubscription.query.filter_by(
                user_id=admin.id,
                is_active=True
            ).count()
            print(f"   Active subscriptions: {user_subs}")
        
        # 4. Test sending a notification
        print("\n4. Test Notification:")
        print("   Attempting to send test notification to all admins...")
        
        try:
            push_service.send_to_admins_and_supervisors(
                'اختبار الإشعارات',
                'هذا إشعار تجريبي من سكربت التشخيص',
                '/admin/dashboard'
            )
            print("   ✓ Test notification function executed")
        except Exception as e:
            print(f"   ✗ Error sending test notification: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("DIAGNOSTIC COMPLETE")
        print("=" * 60)
        
        # 5. Recommendations
        print("\nRECOMMENDATIONS:")
        if len(all_subs) == 0:
            print("   ⚠ No active subscriptions found!")
            print("   → Users need to click the notification bell and allow notifications")
        
        if len(admins) > 0 and len(all_subs) == 0:
            print("   ⚠ Admins exist but have no subscriptions")
            print("   → Admins need to enable notifications in their browser")
        
        print("\nCHECKLIST FOR MOBILE NOTIFICATIONS:")
        print("   □ Browser notifications enabled for the site")
        print("   □ Phone not in Do Not Disturb mode")
        print("   □ Browser has permission to show notifications")
        print("   □ Site is accessed via HTTPS (required for push)")
        print("   □ Service Worker registered successfully")
        print("   □ User clicked 'Allow' when prompted for notifications")

if __name__ == '__main__':
    diagnose_push_notifications()
