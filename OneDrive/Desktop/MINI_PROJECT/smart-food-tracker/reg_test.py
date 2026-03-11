import requests
r = requests.post("http://127.0.0.1:8000/auth/register", json={"username": "test", "email": "test@test.com", "password": "password"})
print(r.status_code)
print(r.text)
