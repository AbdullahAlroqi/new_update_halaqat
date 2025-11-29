"""
VAPID Keys Generator
Run this script once to generate VAPID keys for push notifications
"""

from pywebpush import webpush
import os

def generate_vapid_keys():
    """Generate VAPID public and private keys"""
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.backends import default_backend
    from base64 import urlsafe_b64encode
    
    # Generate elliptic curve private key
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    
    # Get private key bytes
    private_key_bytes = private_key.private_numbers().private_value.to_bytes(32, 'big')
    
    # Get public key bytes
    public_numbers = private_key.public_key().public_numbers()
    public_key_bytes = b'\x04' + \
                       public_numbers.x.to_bytes(32, 'big') + \
                       public_numbers.y.to_bytes(32, 'big')
    
    # Encode as base64 URL-safe
    private_key_b64 = urlsafe_b64encode(private_key_bytes).decode('utf-8').rstrip('=')
    public_key_b64 = urlsafe_b64encode(public_key_bytes).decode('utf-8').rstrip('=')
    
    return private_key_b64, public_key_b64

if __name__ == '__main__':
    print("Generating VAPID keys...")
    private_key, public_key = generate_vapid_keys()
    
    print("\n" + "="*80)
    print("VAPID Keys Generated Successfully!")
    print("="*80)
    print("\nAdd these to your config.py file:\n")
    print(f"VAPID_PRIVATE_KEY = '{private_key}'")
    print(f"VAPID_PUBLIC_KEY = '{public_key}'")
    print(f"VAPID_CLAIMS_SUB = 'mailto:your-email@example.com'  # Change this to your email")
    print("\n" + "="*80)
    print("\n⚠️  IMPORTANT: Keep the private key secret!")
    print("   Add it to .env or config.py but DO NOT commit it to git\n")
