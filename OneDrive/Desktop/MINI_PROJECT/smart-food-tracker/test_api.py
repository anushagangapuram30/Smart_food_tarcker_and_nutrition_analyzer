import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_flow():
    # 1. Register
    print("--- Registering User ---")
    register_data = {
        "username": "anusha_test",
        "email": "anusha@example.com",
        "password": "password123"
    }
    try:
        r = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

    # 2. Login
    print("\n--- Logging In ---")
    login_data = {
        "username": "anusha_test",
        "password": "password123"
    }
    try:
        r = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"Status: {r.status_code}")
        login_res = r.json()
        print(f"Response: {json.dumps(login_res, indent=2)}")
        token = login_res.get("access_token")
    except Exception as e:
        print(f"Error: {e}")
        return

    # 3. Analyze Food Image (Upload dummy file)
    print("\n--- Analyzing Food Image ---")
    with open("test_food.jpg", "wb") as f:
        f.write(b"dummy image data")
    
    files = {"file": ("test_food.jpg", open("test_food.jpg", "rb"), "image/jpeg")}
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        r = requests.post(f"{BASE_URL}/food/upload-food-image", files=files, headers=headers)
        print(f"Status: {r.status_code}")
        print(f"Analysis Output:\n{json.dumps(r.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_flow()
