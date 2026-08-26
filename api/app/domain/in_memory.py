# backend/app/domain/in_memory.py
from datetime import date, datetime
from typing import Dict, List, Optional
from .models import (
    Student, Parent, Teacher, Class,
    ParentStudent, TeacherClass, AttendanceRecord, AttendanceStatus
)
from .repositories import (
    StudentRepository, ParentRepository, TeacherRepository,
    ClassRepository, ParentStudentRepository, TeacherClassRepository,
    AttendanceRepository
)


class InMemoryStudentRepository(StudentRepository):
    def __init__(self, students: Optional[List[Student]] = None):
        self._students: Dict[str, Student] = {s.student_id: s for s in (students or [])}

    def get_student(self, student_id: str) -> Optional[Student]:
        return self._students.get(student_id)

    def create_student(self, student: Student) -> Student:
        self._students[student.student_id] = student
        return student

    def get_all_students(self) -> List[Student]:
        return list(self._students.values())


class InMemoryParentRepository(ParentRepository):
    def __init__(self, parents: Optional[List[Parent]] = None):
        self._parents: Dict[str, Parent] = {p.parent_id: p for p in (parents or [])}

    def get_parent(self, parent_id: str) -> Optional[Parent]:
        return self._parents.get(parent_id)

    def create_parent(self, parent: Parent) -> Parent:
        self._parents[parent.parent_id] = parent
        return parent

    def get_all_parents(self) -> List[Parent]:
        return list(self._parents.values())


class InMemoryTeacherRepository(TeacherRepository):
    def __init__(self, teachers: Optional[List[Teacher]] = None):
        self._teachers: Dict[str, Teacher] = {t.teacher_id: t for t in (teachers or [])}

    def get_teacher(self, teacher_id: str) -> Optional[Teacher]:
        return self._teachers.get(teacher_id)

    def create_teacher(self, teacher: Teacher) -> Teacher:
        self._teachers[teacher.teacher_id] = teacher
        return teacher

    def get_all_teachers(self) -> List[Teacher]:
        return list(self._teachers.values())


class InMemoryClassRepository(ClassRepository):
    def __init__(self, classes: Optional[List[Class]] = None):
        self._classes: Dict[str, Class] = {c.class_id: c for c in (classes or [])}

    def get_class(self, class_id: str) -> Optional[Class]:
        return self._classes.get(class_id)

    def create_class(self, class_: Class) -> Class:
        self._classes[class_.class_id] = class_
        return class_

    def get_all_classes(self) -> List[Class]:
        return list(self._classes.values())


class InMemoryParentStudentRepository(ParentStudentRepository):
    def __init__(self, relationships: Optional[List[ParentStudent]] = None):
        self._relationships: List[ParentStudent] = list(relationships or [])

    def get_children_for_parent(self, parent_id: str) -> List[str]:
        return [r.student_id for r in self._relationships if r.parent_id == parent_id and r.active]

    def get_parents_for_student(self, student_id: str) -> List[str]:
        return [r.parent_id for r in self._relationships if r.student_id == student_id and r.active]

    def create_relationship(self, relationship: ParentStudent) -> ParentStudent:
        for r in self._relationships:
            if r.parent_id == relationship.parent_id and r.student_id == relationship.student_id:
                return r
        self._relationships.append(relationship)
        return relationship

    def get_relationships(self, parent_id: str, student_id: str) -> List[ParentStudent]:
        return [
            r for r in self._relationships
            if r.parent_id == parent_id and r.student_id == student_id and r.active
        ]


class InMemoryTeacherClassRepository(TeacherClassRepository):
    def __init__(self, relationships: Optional[List[TeacherClass]] = None):
        self._relationships: List[TeacherClass] = list(relationships or [])

    def get_classes_for_teacher(self, teacher_id: str) -> List[str]:
        return [r.class_id for r in self._relationships if r.teacher_id == teacher_id and r.active]

    def get_teachers_for_class(self, class_id: str) -> List[str]:
        return [r.teacher_id for r in self._relationships if r.class_id == class_id and r.active]

    def create_relationship(self, relationship: TeacherClass) -> TeacherClass:
        for r in self._relationships:
            if r.teacher_id == relationship.teacher_id and r.class_id == relationship.class_id:
                return r
        self._relationships.append(relationship)
        return relationship


class InMemoryAttendanceRepository(AttendanceRepository):
    def __init__(self, records: Optional[List[AttendanceRecord]] = None):
        self._records: Dict[str, AttendanceRecord] = {r.record_id: r for r in (records or [])}

    def get_attendance_by_student(self, student_id: str, date_from: Optional[date] = None, date_to: Optional[date] = None) -> List[AttendanceRecord]:
        results = [r for r in self._records.values() if r.student_id == student_id]
        if date_from:
            results = [r for r in results if r.date >= date_from]
        if date_to:
            results = [r for r in results if r.date <= date_to]
        return results

    def get_attendance_by_class(self, class_id: str, date_from: Optional[date] = None, date_to: Optional[date] = None) -> List[AttendanceRecord]:
        results = [r for r in self._records.values() if r.class_id == class_id]
        if date_from:
            results = [r for r in results if r.date >= date_from]
        if date_to:
            results = [r for r in results if r.date <= date_to]
        return results

    def create_attendance_record(self, record: AttendanceRecord) -> AttendanceRecord:
        self._records[record.record_id] = record
        return record

    def get_attendance_record(self, record_id: str) -> Optional[AttendanceRecord]:
        return self._records.get(record_id)

    def get_attendance_by_date(self, student_id: str, target_date: date) -> Optional[AttendanceRecord]:
        for r in self._records.values():
            if r.student_id == student_id and r.date == target_date:
                return r
        return None
