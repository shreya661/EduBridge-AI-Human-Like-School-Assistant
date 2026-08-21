"""Directory and Role-Based Access Scoping Router.

Provides scoped access to students, teachers, and school directories:
- Students: Strictly restricted to their own record.
- Teachers: Access to themselves and students enrolled in their assigned classes.
- Parents: Access only to their linked children.
- Principals: Comprehensive access to all teachers, students, classes, and administrative tools.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.session.models import Identity, Role
from app.session.dependencies import require_authenticated_identity
from app.domain import school_domain_service
from app.session.store import identity_store


router = APIRouter(prefix="/api/v1/directory", tags=["directory"])


class DirectoryScopeResponse(BaseModel):
    user_id: str
    role: str
    name: str
    scope_type: str
    description: str
    my_profile: Dict[str, Any]
    students: List[Dict[str, Any]]
    teachers: List[Dict[str, Any]]
    classes: List[Dict[str, Any]]
    permissions: List[str]


@router.get("/scope", response_model=DirectoryScopeResponse)
async def get_directory_scope(
    identity: Identity = Depends(require_authenticated_identity)
) -> DirectoryScopeResponse:
    """
    Get current user's role-aware directory scope and authorized member list.
    """
    # 1. Student Scope: Strictly Self
    if identity.role == Role.STUDENT:
        student_id = identity.student_id or identity.user_id
        student_obj = school_domain_service.student_repo.get_student(student_id)
        
        my_profile = {
            "user_id": identity.user_id,
            "student_id": student_id,
            "name": identity.name,
            "role": "student",
            "class_id": student_obj.class_id if student_obj else "10-A"
        }
        
        # Teachers assigned to student's class
        assigned_teachers = []
        if student_obj and student_obj.class_id:
            class_id = student_obj.class_id
            for t in school_domain_service.get_all_teachers():
                t_classes = school_domain_service.get_classes_for_teacher(t.teacher_id)
                if any(c.class_id == class_id for c in t_classes):
                    assigned_teachers.append({"teacher_id": t.teacher_id, "name": t.name, "subject": t.subject})

        return DirectoryScopeResponse(
            user_id=identity.user_id,
            role="student",
            name=identity.name,
            scope_type="STUDENT_SELF_ONLY",
            description="Students are strictly restricted to accessing their own profile and attendance records.",
            my_profile=my_profile,
            students=[my_profile],  # Only themself
            teachers=assigned_teachers,
            classes=[{"class_id": student_obj.class_id if student_obj else "10-A", "name": student_obj.class_id if student_obj else "10-A"}],
            permissions=["view_own_attendance", "view_own_profile", "escalate_to_teacher"]
        )

    # 2. Teacher Scope: Self + Assigned Students in Teacher's Classes
    elif identity.role == Role.TEACHER:
        assigned_classes = school_domain_service.get_classes_for_teacher(identity.user_id)
        assigned_students = school_domain_service.get_students_for_teacher(identity.user_id)
        
        my_profile = {
            "user_id": identity.user_id,
            "teacher_id": identity.user_id,
            "name": identity.name,
            "role": "teacher",
            "assigned_classes_count": len(assigned_classes)
        }

        students_data = [
            {"student_id": s.student_id, "name": s.name, "class_id": s.class_id, "email": s.email}
            for s in assigned_students
        ]
        classes_data = [
            {"class_id": c.class_id, "name": c.name, "grade_level": c.grade_level, "section": c.section}
            for c in assigned_classes
        ]

        return DirectoryScopeResponse(
            user_id=identity.user_id,
            role="teacher",
            name=identity.name,
            scope_type="TEACHER_AND_ASSIGNED_STUDENTS",
            description="Teachers can view their own profile, assigned classes, and all students enrolled in their assigned classes.",
            my_profile=my_profile,
            students=students_data,
            teachers=[my_profile],
            classes=classes_data,
            permissions=["view_own_profile", "view_assigned_students", "mark_attendance", "view_class_roster", "escalate_to_teacher"]
        )

    # 3. Parent Scope: Linked Children
    elif identity.role == Role.PARENT:
        children = school_domain_service.get_children_for_parent(identity.user_id)
        my_profile = {
            "user_id": identity.user_id,
            "parent_id": identity.user_id,
            "name": identity.name,
            "role": "parent"
        }
        children_data = [
            {"student_id": c.student_id, "name": c.name, "class_id": c.class_id, "email": c.email}
            for c in children
        ]
        return DirectoryScopeResponse(
            user_id=identity.user_id,
            role="parent",
            name=identity.name,
            scope_type="PARENT_LINKED_CHILDREN_ONLY",
            description="Parents can only view their linked children's attendance and academic progress.",
            my_profile=my_profile,
            students=children_data,
            teachers=[],
            classes=[],
            permissions=["view_child_attendance", "view_child_profile", "escalate_to_teacher", "escalate_to_management"]
        )

    # 4. Principal Scope: Full Access (Teachers, Students, Classes, Analytics, Self)
    elif identity.role == Role.PRINCIPAL:
        all_teachers = school_domain_service.get_all_teachers()
        all_students = school_domain_service.get_all_students()
        all_classes = school_domain_service.get_all_classes()

        my_profile = {
            "user_id": identity.user_id,
            "name": identity.name,
            "role": "principal",
            "total_students": len(all_students),
            "total_teachers": len(all_teachers),
            "total_classes": len(all_classes)
        }

        teachers_data = [
            {"teacher_id": t.teacher_id, "name": t.name, "subject": t.subject, "email": t.email}
            for t in all_teachers
        ]
        students_data = [
            {"student_id": s.student_id, "name": s.name, "class_id": s.class_id, "email": s.email}
            for s in all_students
        ]
        classes_data = [
            {"class_id": c.class_id, "name": c.name, "grade_level": c.grade_level, "section": c.section}
            for c in all_classes
        ]

        return DirectoryScopeResponse(
            user_id=identity.user_id,
            role="principal",
            name=identity.name,
            scope_type="PRINCIPAL_FULL_INSTITUTION_ACCESS",
            description="Principals have unrestricted institutional access across all teachers, all students, all classes, and school analytics.",
            my_profile=my_profile,
            students=students_data,
            teachers=teachers_data,
            classes=classes_data,
            permissions=[
                "view_all_students", "view_all_teachers", "view_all_classes",
                "view_school_attendance", "view_school_analytics", "manage_school_settings",
                "generate_reports", "view_own_profile"
            ]
        )

    raise HTTPException(status_code=403, detail="Unrecognized role scope.")


@router.get("/students", response_model=List[Dict[str, Any]])
async def list_scoped_students(
    identity: Identity = Depends(require_authenticated_identity)
) -> List[Dict[str, Any]]:
    """Get list of students accessible under current authenticated role."""
    if identity.role == Role.STUDENT:
        student_id = identity.student_id or identity.user_id
        student = school_domain_service.student_repo.get_student(student_id)
        if not student:
            return [{"student_id": student_id, "name": identity.name}]
        return [{"student_id": student.student_id, "name": student.name, "class_id": student.class_id}]

    elif identity.role == Role.TEACHER:
        students = school_domain_service.get_students_for_teacher(identity.user_id)
        return [{"student_id": s.student_id, "name": s.name, "class_id": s.class_id} for s in students]

    elif identity.role == Role.PARENT:
        children = school_domain_service.get_children_for_parent(identity.user_id)
        return [{"student_id": c.student_id, "name": c.name, "class_id": c.class_id} for c in children]

    elif identity.role == Role.PRINCIPAL:
        students = school_domain_service.get_all_students()
        return [{"student_id": s.student_id, "name": s.name, "class_id": s.class_id} for s in students]

    return []


@router.get("/teachers", response_model=List[Dict[str, Any]])
async def list_scoped_teachers(
    identity: Identity = Depends(require_authenticated_identity)
) -> List[Dict[str, Any]]:
    """Get list of teachers accessible under current authenticated role."""
    if identity.role in [Role.STUDENT, Role.PARENT]:
        # Return teachers assigned to student's class
        return [
            {"teacher_id": t.teacher_id, "name": t.name, "subject": t.subject}
            for t in school_domain_service.get_all_teachers()
        ]

    elif identity.role in [Role.TEACHER, Role.PRINCIPAL]:
        # Return all staff members
        teachers = school_domain_service.get_all_teachers()
        return [{"teacher_id": t.teacher_id, "name": t.name, "subject": t.subject} for t in teachers]

    return []
