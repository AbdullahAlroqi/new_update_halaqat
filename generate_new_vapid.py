"""
Generate new VAPID keys for push notifications
"""

from py_vapid import Vapid

# Generate new VAPID keys
vapid = Vapid()
vapid.generate_keys()

# Get the keys
private_key = vapid.private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
).decode('utf-8').strip()

public_key = vapid.public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint
)

# Convert to base64url
import base64
public_key_b64 = base64.urlsafe_b64encode(public_key).decode('utf-8').rstrip('=')

print("=" * 60)
print("NEW VAPID KEYS GENERATED")
print("=" * 60)
print("\nAdd these to your config.py:")
print(f"\nVAPID_PRIVATE_KEY = '{vapid.private_pem().decode('utf-8').strip()}'")
print(f"\nVAPID_PUBLIC_KEY = '{public_key_b64}'")
print("\nVAPID_CLAIMS_SUB = 'mailto:admin@halaqat.com'")
print("\n" + "=" * 60)
print("\nIMPORTANT:")
print("1. Update config.py with these new keys")
print("2. Users will need to re-subscribe to notifications")
print("3. Clear old subscriptions from database or mark as inactive")
print("=" * 60)
