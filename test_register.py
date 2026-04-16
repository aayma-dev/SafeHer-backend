import requests
import json

# Register a new user
url = "http://localhost:8000/api/auth/register"

user_data = {
    "username": "safetest",
    "email": "safetest@example.com",
    "password": "Test@1234",
    "confirm_password": "Test@1234"
}

print("📝 Registering user...")
response = requests.post(url, json=user_data)

if response.status_code == 201:
    print("✅ User registered successfully!")
    print("Response:", json.dumps(response.json(), indent=2))
elif response.status_code == 400:
    print("⚠️ User might already exist!")
    print("Error:", response.json())
else:
    print(f"❌ Error {response.status_code}:", response.json())