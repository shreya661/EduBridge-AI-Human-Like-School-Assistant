"""Tests for Granular Role Scoping:
- Student: Only self.
- Teacher: Self + Students enrolled in assigned classes.
- Parent: Linked children only.
- Principal: Full access (All Teachers, All Students, and Self).
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_student_restricted_to_self_only():
    """Students can only view their own profile; access to other students/teachers is forbidden."""
    # Login as Student S001
    login_res = client.post("/api/v1/auth/login", json={"user_id": "S001"})
    assert login_res.status_code == 200
    cookies = login_res.cookies

    # 1. Accessing own profile -> 200 OK
    res_self = client.get("/api/v1/users/S001", cookies=cookies)
    assert res_self.status_code == 200
    assert res_self.json()["user_id"] == "S001"

    # 2. Accessing another student S002 -> 403 Forbidden
    res_other_student = client.get("/api/v1/users/S002", cookies=cookies)
    assert res_other_student.status_code == 403
    assert "Students are restricted" in res_other_student.json()["detail"]

    # 3. Accessing teacher profile -> 403 Forbidden
    res_teacher = client.get("/api/v1/users/T001", cookies=cookies)
    assert res_teacher.status_code == 403

    # 4. Directory scope returns only self
    res_scope = client.get("/api/v1/directory/scope", cookies=cookies)
    assert res_scope.status_code == 200
    data = res_scope.json()
    assert data["scope_type"] == "STUDENT_SELF_ONLY"
    assert len(data["students"]) == 1
    assert data["students"][0]["user_id"] == "S001"


def test_teacher_access_self_and_assigned_students_only():
    """Teachers can view self and students in their assigned classes, but not unassigned students or peers."""
    # Login as Teacher T001 (assigned to C001, which has S001 and S003)
    login_res = client.post("/api/v1/auth/login", json={"user_id": "T001"})
    assert login_res.status_code == 200
    cookies = login_res.cookies

    # 1. Accessing self -> 200 OK
    res_self = client.get("/api/v1/users/T001", cookies=cookies)
    assert res_self.status_code == 200
    assert res_self.json()["user_id"] == "T001"

    # 2. Accessing assigned student in C001 (S001) -> 200 OK
    res_assigned_student = client.get("/api/v1/users/S001", cookies=cookies)
    assert res_assigned_student.status_code == 200

    # 3. Accessing unassigned student in C002 (S002) -> 403 Forbidden
    res_unassigned_student = client.get("/api/v1/users/S002", cookies=cookies)
    assert res_unassigned_student.status_code == 403
    assert "Teachers are restricted" in res_unassigned_student.json()["detail"]

    # 4. Accessing another teacher (teacher-001) -> 403 Forbidden
    res_peer_teacher = client.get("/api/v1/users/teacher-001", cookies=cookies)
    assert res_peer_teacher.status_code == 403

    # 5. Directory scope returns teacher and their assigned students
    res_scope = client.get("/api/v1/directory/scope", cookies=cookies)
    assert res_scope.status_code == 200
    data = res_scope.json()
    assert data["scope_type"] == "TEACHER_AND_ASSIGNED_STUDENTS"
    student_ids = [s["student_id"] for s in data["students"]]
    assert "S001" in student_ids
    assert "S002" not in student_ids


def test_parent_access_linked_children_only():
    """Parents can view their linked children, but not unlinked students."""
    # Login as Parent P001 (linked to S001 and S003)
    login_res = client.post("/api/v1/auth/login", json={"user_id": "P001"})
    assert login_res.status_code == 200
    cookies = login_res.cookies

    # 1. Accessing self -> 200 OK
    res_self = client.get("/api/v1/users/P001", cookies=cookies)
    assert res_self.status_code == 200

    # 2. Accessing linked child (S001) -> 200 OK
    res_child = client.get("/api/v1/users/S001", cookies=cookies)
    assert res_child.status_code == 200

    # 3. Accessing unlinked student (S002) -> 403 Forbidden
    res_unlinked = client.get("/api/v1/users/S002", cookies=cookies)
    assert res_unlinked.status_code == 403


def test_principal_unrestricted_institutional_access():
    """Principals can access all teachers, all students, all classes, and themselves."""
    # Login as Principal
    login_res = client.post("/api/v1/auth/login", json={"user_id": "PRN10A99X1", "password": "Password@123"})
    assert login_res.status_code == 200
    cookies = login_res.cookies

    # 1. Accessing self -> 200 OK
    res_self = client.get("/api/v1/users/PRN10A99X1", cookies=cookies)
    assert res_self.status_code == 200

    # 2. Accessing any teacher -> 200 OK
    res_teacher = client.get("/api/v1/users/T001", cookies=cookies)
    assert res_teacher.status_code == 200

    # 3. Accessing any student across any class -> 200 OK
    res_student1 = client.get("/api/v1/users/S001", cookies=cookies)
    assert res_student1.status_code == 200

    res_student2 = client.get("/api/v1/users/S002", cookies=cookies)
    assert res_student2.status_code == 200

    # 4. Directory scope returns all institutional members
    res_scope = client.get("/api/v1/directory/scope", cookies=cookies)
    assert res_scope.status_code == 200
    data = res_scope.json()
    assert data["scope_type"] == "PRINCIPAL_FULL_INSTITUTION_ACCESS"
    assert len(data["teachers"]) >= 2
    assert len(data["students"]) >= 3
    assert len(data["classes"]) >= 2
