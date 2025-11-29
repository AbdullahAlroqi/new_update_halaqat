"""
Push Notification Service
Handles sending web push notifications to users
"""

from pywebpush import webpush, WebPushException
import json
from models import db, PushSubscription, User, Role

def send_push_notification(user_id, title, body, url=None, icon=None):
    """
    إرسال إشعار push لمستخدم واحد
    
    Args:
        user_id: معرف المستخدم
        title: عنوان الإشعار
        body: محتوى الإشعار
        url: رابط للانتقال إليه عند النقر (اختياري)
        icon: أيقونة الإشعار (اختياري)
    """
    from config import Config
    
    # جلب اشتراكات المستخدم النشطة
    subscriptions = PushSubscription.query.filter_by(
        user_id=user_id,
        is_active=True
    ).all()
    
    if not subscriptions:
        print(f"No active subscriptions for user {user_id}")
        return
    
    _send_to_subscriptions(subscriptions, title, body, url, icon)

def send_push_by_national_id(national_id, title, body, url=None, icon=None):
    """
    إرسال إشعار push باستخدام رقم الهوية (للموظفين بدون تسجيل دخول)
    
    Args:
        national_id: رقم الهوية الوطنية
        title: عنوان الإشعار
        body: محتوى الإشعار
        url: رابط للانتقال إليه عند النقر (اختياري)
        icon: أيقونة الإشعار (اختياري)
    """
    # جلب اشتراكات برقم الهوية
    subscriptions = PushSubscription.query.filter_by(
        national_id=national_id,
        is_active=True
    ).all()
    
    if not subscriptions:
        print(f"No active subscriptions for national_id {national_id}")
        # محاولة إيجاد المستخدم وإرسال عبر user_id
        user = User.query.filter_by(national_id=national_id).first()
        if user:
            send_push_notification(user.id, title, body, url, icon)
        return
    
    _send_to_subscriptions(subscriptions, title, body, url, icon)

def _send_to_subscriptions(subscriptions, title, body, url=None, icon=None):
    """
    دالة مساعدة لإرسال الإشعار لمجموعة من الاشتراكات
    """
    from config import Config
    
    # تحضير بيانات الإشعار
    notification_data = {
        'title': title,
        'body': body,
        'icon': icon or '/static/images/logo.png',
        'badge': '/static/images/badge.png',
        'url': url or '/'
    }
    
    vapid_claims = {
        "sub": Config.VAPID_CLAIMS_SUB
    }
    
    # إرسال الإشعار لكل اشتراك
    for subscription in subscriptions:
        try:
            subscription_info = json.loads(subscription.subscription_json)
            
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(notification_data),
                vapid_private_key=Config.VAPID_PRIVATE_KEY,
                vapid_claims=vapid_claims
            )
            print(f"✓ Push notification sent")
            
        except WebPushException as e:
            print(f"✗ Failed to send push notification: {e}")
            
            # إذا كان الاشتراك غير صالح، قم بتعطيله
            if e.response and e.response.status_code in [404, 410]:
                subscription.is_active = False
                db.session.commit()
                print(f"Subscription {subscription.id} deactivated")
                
        except Exception as e:
            print(f"Error sending notification: {e}")

def send_to_admins(title, body, url=None):
    """
    إرسال إشعار لجميع المدراء
    """
    admins = User.query.filter(
        User.role.in_([Role.MAIN_ADMIN, Role.SUB_ADMIN])
    ).all()
    
    for admin in admins:
        send_push_notification(admin.id, title, body, url)

def send_to_main_supervisors(title, body, url=None):
    """
    إرسال إشعار لجميع المشرفين الرئيسيين
    """
    supervisors = User.query.filter_by(role=Role.MAIN_SUPERVISOR).all()
    
    for supervisor in supervisors:
        send_push_notification(supervisor.id, title, body, url)

def send_to_admins_and_supervisors(title, body, url=None):
    """
    إرسال إشعار للمدراء والمشرفين الرئيسيين
    """
    users = User.query.filter(
        User.role.in_([Role.MAIN_ADMIN, Role.SUB_ADMIN, Role.MAIN_SUPERVISOR])
    ).all()
    
    for user in users:
        send_push_notification(user.id, title, body, url)
