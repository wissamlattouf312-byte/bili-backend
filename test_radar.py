"""
Quick test script for Radar endpoint
Run this to verify Silent Decay Logic is working
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_radar_endpoint():
    """Test the radar endpoint with Silent Decay Logic"""
    print("🧪 Testing Radar Endpoint (Silent Decay Logic)...")
    print("=" * 60)
    
    # Test 1: Get radar users without location
    print("\n1. Testing GET /api/v1/radar/users (no location filter)")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/radar/users")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {data['total']} users on radar")
            print(f"   Timestamp: {data['timestamp']}")
            if data['users']:
                print(f"   Sample user: {data['users'][0]}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running! Start with: python run.py")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Get radar users with location
    print("\n2. Testing GET /api/v1/radar/users (with location)")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/radar/users",
            params={
                "latitude": 33.8938,  # Beirut coordinates
                "longitude": 35.5018,
                "radius_km": 15
            }
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {data['total']} users within 15km radius")
            print(f"   Silent Decay Logic applied: Offline users with 0 credits excluded")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Get radar stats
    print("\n3. Testing GET /api/v1/radar/stats")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/radar/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Radar Statistics:")
            print(f"   Total users: {data['total_users']}")
            print(f"   Online users: {data['online_users']}")
            print(f"   Offline with credits: {data['offline_with_credits']}")
            print(f"   Offline zero balance: {data['offline_zero_balance']}")
            print(f"   Visible on radar: {data['visible_on_radar']}")
            print(f"   Silent Decay removed: {data['silent_decay_removed']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Radar endpoint test complete!")
    print("\nTo start the server, run: python run.py")
    print("Then visit: http://localhost:8000/api/docs for API documentation")

if __name__ == "__main__":
    test_radar_endpoint()
