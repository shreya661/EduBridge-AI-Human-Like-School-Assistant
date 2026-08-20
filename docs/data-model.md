<!-- docs/data-model.md -->
# School Domain Data Model

## Entities

### Student
- `student_id`: Unique identifier (e.g., "S001")
- `name`: Student's full name
- `email`: Contact email
- `class_id`: Associated class
- `active`: Whether student is active
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Parent
- `parent_id`: Unique identifier (e.g., "P001")
- `name`: Parent's full name
- `email`: Contact email
- `phone`: Phone number
- `active`: Whether parent account is active
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Teacher
- `teacher_id`: Unique identifier (e.g., "T001")
- `name`: Teacher's full name
- `email`: Contact email
- `subject`: Subject taught
- `active`: Whether teacher is active
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Class
- `class_id`: Unique identifier (e.g., "C001")
- `name`: Class name (e.g., "10-A")
- `grade_level`: Grade level (e.g., 10)
- `section`: Section (e.g., "A")
- `academic_year`: Academic year (e.g., "2026-2027")
- `teacher_id`: Assigned teacher
- `active`: Whether class is active
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

---

## Relationships

### Parent-Student
- Connects parents to their children
- Allows parents to access their children's data
- Supports multiple children per parent

### Teacher-Class
- Connects teachers to their assigned classes
- Allows teachers to manage assigned classes
- Supports multiple classes per teacher

---

## Attendance

### Attendance Record
- `record_id`: Unique identifier
- `student_id`: Associated student
- `class_id`: Associated class
- `date`: Date of attendance
- `status`: `PRESENT`, `ABSENT`, `LATE`, `EXCUSED`
- `recorded_by`: User who recorded attendance
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

---

## Domain Entity Diagram

```mermaid
erDiagram
    STUDENT ||--o{ PARENT_STUDENT : has
    PARENT ||--o{ PARENT_STUDENT : has
    TEACHER ||--o{ TEACHER_CLASS : assigned
    CLASS ||--o{ TEACHER_CLASS : assigned
    CLASS ||--o{ STUDENT : contains
    STUDENT ||--o{ ATTENDANCE_RECORD : logs
    CLASS ||--o{ ATTENDANCE_RECORD : logs

    STUDENT {
        string student_id PK
        string name
        string email
        string class_id FK
        boolean active
        datetime created_at
        datetime updated_at
    }

    PARENT {
        string parent_id PK
        string name
        string email
        string phone
        boolean active
        datetime created_at
        datetime updated_at
    }

    PARENT_STUDENT {
        string parent_id FK
        string student_id FK
        string relationship_type
        boolean active
        datetime created_at
    }

    TEACHER {
        string teacher_id PK
        string name
        string email
        string subject
        boolean active
        datetime created_at
        datetime updated_at
    }

    CLASS {
        string class_id PK
        string name
        int grade_level
        string section
        string academic_year
        string teacher_id FK
        boolean active
        datetime created_at
        datetime updated_at
    }

    TEACHER_CLASS {
        string teacher_id FK
        string class_id FK
        date assigned_date
        boolean active
        datetime created_at
    }

    ATTENDANCE_RECORD {
        string record_id PK
        string student_id FK
        string class_id FK
        date date
        string status
        string recorded_by
        datetime created_at
        datetime updated_at
    }
```

---

## Storage Strategy

The domain uses an in-memory repository pattern that can be easily replaced with database implementations later. The architecture maintains clear separation between:
- **Identity:** Authentication credentials and session tokens (`Identity`, `Role`).
- **Domain Data:** Relationships and school entities (`Student`, `Parent`, `Teacher`, `Class`).
- **Authorization:** Deterministic permission gates and ownership validation (`is_allowed`, `validate_ownership`).
- **Tools / Services:** Business workflows and attendance operations (`SchoolDomainService`, `AttendanceTool`).
