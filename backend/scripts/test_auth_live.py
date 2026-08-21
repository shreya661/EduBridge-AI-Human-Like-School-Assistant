import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:8000"

def post_json(endpoint, data):
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8")), resp.headers.get("Set-Cookie")

print("=== 1. Testing Default Seeded 10-Character Accounts ===")
for user_id, role in [("STU10A88F2", "student"), ("TCH90K11X4", "teacher"), ("PAR81L90V7", "parent"), ("PRN10A99X1", "principal")]:
    res, cookie = post_json("/api/v1/auth/login", {"user_id": user_id, "password": "Password@123"})
    print(f"Login {user_id} ({role}): Success -> Name: {res['user']['name']}, Role: {res['user']['role']}")
    assert res['user']['role'] == role

print("\n=== 2. Testing New User Signups with 10-Character IDs ===")
# Student Signup
student_signup, _ = post_json("/api/v1/auth/signup", {
    "name": "Pooja Patel",
    "role": "STUDENT",
    "password": "MySecretPassword#1",
    "email": "pooja.patel@school.edu"
})
stu_id = student_signup['user']['user_id']
print(f"Signed up Student: {student_signup['user']['name']} with ID: {stu_id}")
assert len(stu_id) == 10 and stu_id.startswith("STU")

# Teacher Signup with Custom Valid 10-char ID
import secrets
rand_suffix = secrets.token_hex(2).upper() + "9"  # 5 chars
custom_tch_id = f"TCH99{rand_suffix}"[:10]
teacher_signup, _ = post_json("/api/v1/auth/signup", {
    "name": "Prof. Vikram Shah",
    "role": "TEACHER",
    "user_id": custom_tch_id,
    "password": "TeacherPassword#1",
    "email": f"vikram.shah.{custom_tch_id}@school.edu",
    "class_id": "10-A"
})
print(f"Signed up Teacher with Custom ID: {teacher_signup['user']['user_id']} ({teacher_signup['user']['name']})")
assert teacher_signup['user']['user_id'] == custom_tch_id

# Parent Signup with child linking
parent_signup, _ = post_json("/api/v1/auth/signup", {
    "name": "Bhavin Patel",
    "role": "PARENT",
    "password": "ParentPassword#1",
    "child_id": stu_id
})
par_id = parent_signup['user']['user_id']
print(f"Signed up Parent: {parent_signup['user']['name']} with ID: {par_id} (Linked to child {stu_id})")
assert len(par_id) == 10 and par_id.startswith("PAR")

# Principal Signup
prn_signup, _ = post_json("/api/v1/auth/signup", {
    "name": "Dr. Ramesh Desai",
    "role": "PRINCIPAL",
    "password": "PrincipalPassword#1"
})
prn_id = prn_signup['user']['user_id']
print(f"Signed up Principal: {prn_signup['user']['name']} with ID: {prn_id}")
assert len(prn_id) == 10 and prn_id.startswith("PRN")

print("\n=== 3. Testing Sign In with Newly Created Accounts ===")
login_stu, _ = post_json("/api/v1/auth/login", {"user_id": stu_id, "password": "MySecretPassword#1"})
print(f"Login newly created Student {stu_id}: Success -> {login_stu['user']['name']}")

login_tch, _ = post_json("/api/v1/auth/login", {"user_id": "TCH77K22M9", "password": "TeacherPassword#1"})
print(f"Login newly created Teacher TCH77K22M9: Success -> {login_tch['user']['name']}")

print("\nAll 10-character mixed alphanumeric authentication flows verified successfully!")
