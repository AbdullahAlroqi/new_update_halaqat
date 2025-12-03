
import requests
import json

# Configuration
BASE_URL = 'http://127.0.0.1:5000'
ADMIN_USERNAME = '1000000001' # Assuming this is the admin ID from create_test_users.py or similar
ADMIN_PASSWORD = 'password123' # Default password

def login(session):
    print(f"Attempting login with {ADMIN_USERNAME}...")
    response = session.post(f'{BASE_URL}/login', data={
        'national_id': ADMIN_USERNAME,
        'password': ADMIN_PASSWORD
    })
    
    if response.status_code == 200 and 'تسجيل الخروج' in response.text:
        print("Login successful!")
        return True
    else:
        print("Login failed!")
        print(f"Status Code: {response.status_code}")
        # print(response.text[:500])
        return False

def trigger_test_notification(session):
    print("Triggering test notification...")
    response = session.post(f'{BASE_URL}/admin/test-notification')
    
    try:
        data = response.json()
        if data.get('success'):
            print("✓ Test notification triggered successfully!")
            print(f"Message: {data.get('message')}")
        else:
            print("✗ Failed to trigger notification.")
            print(f"Message: {data.get('message')}")
    except json.JSONDecodeError:
        print("✗ Failed to parse JSON response.")
        print(f"Response text: {response.text}")

def main():
    session = requests.Session()
    if login(session):
        trigger_test_notification(session)
    else:
        print("Skipping notification test due to login failure.")

if __name__ == '__main__':
    main()
