# Mock attendance data for development purposes

mock_attendance_data = [
    {
        "student_id": 1,
        "student_name": "Rahul",
        "attendance_percentage": 91.0,
        "total_working_days": 100,
        "days_present": 91,
        "days_absent": 9,
        "recent_attendance": [True, True, False, True, True, True, False, True, True, True],
        "class_id": 101
    },
    {
        "student_id": 2,
        "student_name": "Ananya",
        "attendance_percentage": 88.0,
        "total_working_days": 100,
        "days_present": 88,
        "days_absent": 12,
        "recent_attendance": [True, True, True, True, False, True, True, True, False, True],
        "class_id": 101
    },
    {
        "student_id": 3,
        "student_name": "Arjun",
        "attendance_percentage": 95.0,
        "total_working_days": 100,
        "days_present": 95,
        "days_absent": 5,
        "recent_attendance": [True, True, True, True, True, True, True, True, True, True],
        "class_id": 102
    },
    {
        "student_id": 4,
        "student_name": "Priya",
        "attendance_percentage": 85.0,
        "total_working_days": 100,
        "days_present": 85,
        "days_absent": 15,
        "recent_attendance": [True, False, True, True, True, False, True, True, True, False],
        "class_id": 102
    }
]

# The development identity store uses stable string identifiers while this mock
# API models the numeric IDs provided by a school system.
identity_student_ids = {
    "student-001": 1,
    "student-002": 2,
    "student-003": 3,
    "student-004": 4,
}

def get_student_attendance(student_id):
    for student in mock_attendance_data:
        if student["student_id"] == student_id:
            return student
    return None

def get_class_attendance(class_id):
    return [student for student in mock_attendance_data if student["class_id"] == class_id]

def get_school_attendance():
    return mock_attendance_data


def find_student_by_name(student_name: str):
    normalized_name = student_name.strip().casefold()
    for student in mock_attendance_data:
        if student["student_name"].casefold() == normalized_name:
            return student
    return None
