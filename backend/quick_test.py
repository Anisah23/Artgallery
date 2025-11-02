import requests
import json

BASE_URL = "http://localhost:5000"
token = None
artwork_id = None

def test_endpoint(method, url, data=None, headers=None, desc=""):
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PATCH":
            response = requests.patch(url, json=data, headers=headers)
        
        print(f"{desc or method + ' ' + url}")
        print(f"Status: {response.status_code}")
        if response.status_code < 400:
            print("✓ SUCCESS")
            return response
        else:
            print(f"✗ FAILED: {response.text[:100]}")
            return response
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return None
    finally:
        print("-" * 50)

print("🎨 Art Gallery API Complete Test")
print("=" * 50)

# 1. Health Check
print("\n1. HEALTH CHECK")
test_endpoint("GET", f"{BASE_URL}/health", desc="Health Check")

# 2. Authentication Flow
print("\n2. AUTHENTICATION")
user_data = {
    "email": "test@example.com", 
    "password": "Test123456",
    "fullName": "Test User",
    "role": "collector"
}

# Register
test_endpoint("POST", f"{BASE_URL}/api/auth/register", user_data, desc="Register User")

# Login
login_data = {"email": "test@example.com", "password": "Test123456"}
response = test_endpoint("POST", f"{BASE_URL}/api/auth/login", login_data, desc="Login User")

if response and response.status_code == 200:
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✓ Token received: {token[:20]}...")
    
    # 3. Gallery
    print("\n3. GALLERY")
    response = test_endpoint("GET", f"{BASE_URL}/api/gallery/", headers=headers, desc="Get Gallery")
    if response and response.status_code == 200:
        artworks = response.json()
        artworks_list = artworks.get('items', artworks) if isinstance(artworks, dict) else artworks
        if artworks_list and len(artworks_list) > 0:
            artwork_id = artworks_list[0].get('id')
            print(f"✓ Found {len(artworks_list)} artworks, using ID: {artwork_id}")
    
    # 4. Cart Operations
    print("\n4. CART OPERATIONS")
    test_endpoint("GET", f"{BASE_URL}/api/cart/", headers=headers, desc="Get Cart")
    
    if artwork_id:
        test_endpoint("POST", f"{BASE_URL}/api/cart/", {"artworkId": artwork_id}, headers, "Add to Cart")
        test_endpoint("PATCH", f"{BASE_URL}/api/cart/{artwork_id}", {"quantity": 2}, headers, "Update Cart")
    
    # 5. Wishlist Operations
    print("\n5. WISHLIST OPERATIONS")
    test_endpoint("GET", f"{BASE_URL}/api/wishlist/", headers=headers, desc="Get Wishlist")
    
    if artwork_id:
        test_endpoint("POST", f"{BASE_URL}/api/wishlist/", {"artworkId": artwork_id}, headers, "Add to Wishlist")
    
    # 6. Orders
    print("\n6. ORDERS")
    test_endpoint("GET", f"{BASE_URL}/api/orders/", headers=headers, desc="Get Orders")
    
    if artwork_id:
        order_data = {
            "items": [{"artwork_id": artwork_id, "quantity": 1, "price": 100}],
            "shipping_details": {
                "fullName": "Test User",
                "address": "123 Test St",
                "city": "Test City",
                "postalCode": "12345",
                "country": "US"
            },
            "total_amount": 100
        }
        test_endpoint("POST", f"{BASE_URL}/api/orders/", order_data, headers, "Create Order")
    
    # 7. Payment
    print("\n7. PAYMENT")
    payment_data = {"amount": 100, "currency": "usd", "description": "Test payment"}
    response = test_endpoint("POST", f"{BASE_URL}/api/payments/create-intent", payment_data, headers, "Create Payment Intent")
    if response and response.status_code == 200:
        client_secret = response.json().get('client_secret')
        if client_secret:
            print(f"✓ Payment intent created: {client_secret[:20]}...")
    
    # 8. Notifications
    print("\n8. NOTIFICATIONS")
    test_endpoint("GET", f"{BASE_URL}/api/collectors/notifications", headers=headers, desc="Get Notifications")
    
    print("\n🎉 ALL TESTS COMPLETED!")
else:
    print("❌ Login failed - cannot test authenticated endpoints")

print("\n" + "=" * 50)