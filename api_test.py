import requests

BASE_URL = "http://localhost:5000/api"

def test_register():
    print("== 测试注册 ==")
    data = {
        "username": "testuser1",
        "password": "testpass123"
    }
    resp = requests.post(f"{BASE_URL}/register", json=data)
    print("注册响应：", resp.status_code, resp.json())

def test_login():
    print("== 测试登录 ==")
    data = {
        "username": "admin",
        "password": "admin123"
    }
    resp = requests.post(f"{BASE_URL}/login", json=data)
    print("登录响应：", resp.status_code, resp.json())
    if resp.status_code == 200 and resp.json().get("access_token"):
        return resp.json()["access_token"]
    return None

def test_get_users(token):
    print("== 测试获取用户列表 ==")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/admin/users", headers=headers)
    print("用户列表响应：", resp.status_code, resp.json())

def test_get_logs(token):
    print("== 测试获取日志 ==")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/admin/logs", headers=headers)
    print("日志响应：", resp.status_code, resp.json())

if __name__ == "__main__":
    test_register()
    token = test_login()
    if token:
        test_get_users(token)
        test_get_logs(token)
    else:
        print("登录失败，无法继续测试。")
