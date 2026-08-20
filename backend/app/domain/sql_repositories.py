"""SQLAlchemy / PostgreSQL implementations of domain repositories."""

from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

from app.domain.models import (
    Student, Parent, Teacher, Class,
    ParentStudent, TeacherClass, AttendanceRecord,
    AttendanceStatus
)
from app.domain.sql_models import (
    SQLStudent, SQLParent, SQLTeacher, SQLClass,
    SQLParentStudent, SQLTeacherClass, SQLAttendanceRecord
)
from app.domain.repositories import (
    StudentRepository, ParentRepository, TeacherRepository, ClassRepository,
    ParentStudentRepository, TeacherClassRepository, AttendanceRepository
)


class SQLStudentRepository(StudentRepository):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def get_student(self, student_id: str) -> Optional[Student]:
        with self.session_factory() as session:
            obj = session.query(SQLStudent).filter(SQLStudent.student_id == student_id).first()
            if obj:
                return Student(student_id=obj.student_id, name=obj.name, class_id=obj.class_id, created_at=obj.created_at)
            return None

    def create_student(self, student: Student) -> Student:
        with self.session_factory() as session:
            sql_obj = SQLStudent(student_id=student.student_id, name=student.name, class_id=student.class_id, created_at=student.created_at)
            session.merge(sql_obj)
            session.commit()
            return student

    def get_all_students(self) -> List[Student]:
        with self.session_factory() as session:
            objs = session.query(SQLStudent).all()
            return [Student(student_id=o.student_id, name=o.name, class_id=o.class_id, created_at=o.created_at) for o in objs]


class SQLParentRepository(ParentRepository):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def get_parent(self, parent_id: str) -> Optional[Parent]:
        with self.session_factory() as session:
            obj = session.query(SQLParent).filter(SQLParent.parent_id == parent_id).first()
            if obj:
                return Parent(parent_id=obj.parent_id, name=obj.name, email=obj.email, phone=obj.phone)
            return None

    def create_parent(self, parent: Parent) -> Parent:
        with self.session_factory() as session:
            sql_obj = SQLParent(parent_id=parent.parent_id, name=parent.name, email=parent.email, phone=parent.phone)
            session.merge(sql_obj)
            session.commit()
            return parent

    def get_all_parents(self) -> List[Parent]:
        with self.session_factory() as session:
            objs = session.query(SQLParent).all()
            return [Parent(parent_id=o.parent_id, name=o.name, email=o.email, phone=o.phone) for o in objs]


class SQLTeacherRepository(TeacherRepository):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def get_teacher(self, teacher_id: str) -> Optional[Teacher]:
        with self.session_factory() as session:
            obj = session.query(SQLTeacher).filter(SQLTeacher.teacher_id == teacher_id).first()
            if obj:
                return Teacher(teacher_id=obj.teacher_id, name=obj.name, subject=obj.subject)
            return None

    def create_teacher(self, teacher: Teacher) -> Teacher:
        with self.session_factory() as session:
            sql_obj = SQLTeacher(teacher_id=teacher.teacher_id, name=teacher.name, subject=teacher.subject)
            session.merge(sql_obj)
            session.commit()
            return teacher

    def get_all_teachers(self) -> List[Teacher]:
        with self.session_factory() as session:
            objs = session.query(SQLTeacher).all()
            return [Teacher(teacher_id=o.teacher_id, name=o.name, subject=o.subject) for o in objs]


class SQLClassRepository(ClassRepository):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def get_class(self, class_id: str) -> Optional[Class]:
        with self.session_factory() as session:
            obj = session.query(SQLClass).filter(SQLClass.class_id == class_id).first()
            if obj:
                return Class(class_id=obj.class_id, name=obj.name, grade_level=obj.grade_level, section=obj.section, teacher_id=obj.teacher_id)
            return None

    def create_class(self, class_: Class) -> Class:
        with self.session_factory() as session:
            sql_obj = SQLClass(
                class_id=class_.class_id,
                name=class_.name,
                grade_level=class_.grade_level,
                section=class_.section,
                teacher_id=class_.teacher_id
            )
            session.merge(sql_obj)
            session.commit()
            return class_

    def get_all_classes(self) -> List[Class]:
        with self.session_factory() as session:
            objs = session.query(SQLClass).all()
            return [Class(class_id=o.class_id, name=o.name, grade_level=o.grade_level, section=o.section, teacher_id=o.teacher_id) for o in objs]


class SQLParentStudentRepository(ParentStudentRepository):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def get_children_for_parent(self, parent_id: str) -> List[str]:
        with self.session_factory() as session:
            objs = session.query(SQLParentStudent).filter(SQLParentStudent.parent_id == parent_id).all()
            return [o.student_id for o in objs]

    def get_parents_for_student(self, student_id: str) -> List[str]:
        with self.session_factory() as session:
            objs = session.query(SQLParentStudent).filter(SQLParentStudent.student_id == student_id).all()
            return [o.parent_id for o in objs]

    def create_relationship(self, relationship: ParentStudent) -> ParentStudent:
        with self.session_factory() as session:
            sql_obj = SQLParentStudent(parent_id=relationship.parent_id, student_id=relationship.student_id)
            session.add(sql_obj)
            session.commit()
            return relationship

    def get_relationships(self, parent_id: str, student_id: str) -> List[ParentStudent]:
        with self.session_factory() as session:
            objs = session.query(SQLParentStudent).filter(
                SQLParentStudent.parent_id == parent_id,
                SQLParentStudent.student_id == student_id
            ).all()
            return [ParentStudent(parent_id=o.parent_id, student_id=o.student_id) for o in objs]


class SQLTeacherClassRepository(TeacherClassRepository):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def get_classes_for_teacher(self, teacher_id: str) -> List[str]:
        with self.session_factory() as session:
            objs = session.query(SQLTeacherClass).filter(SQLTeacherClass.teacher_id == teacher_id).all()
            return [o.class_id for o in objs]

    def get_teachers_for_class(self, class_id: str) -> List[str]:
        with self.session_factory() as session:
            objs = session.query(SQLTeacherClass).filter(SQLTeacherClass.class_id == class_id).all()
            return [o.teacher_id for o in objs]

    def create_relationship(self, relationship: TeacherClass) -> TeacherClass:
        with self.session_factory() as session:
            sql_obj = SQLTeacherClass(teacher_id=relationship.teacher_id, class_id=relationship.class_id)
            session.add(sql_obj)
            session.commit()
            return relationship


class SQLAttendanceRepository(AttendanceRepository):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def get_attendance_by_student(self, student_id: str, date_from: Optional[date] = None, date_to: Optional[date] = None) -> List[AttendanceRecord]:
        with self.session_factory() as session:
            query = session.query(SQLAttendanceRecord).filter(SQLAttendanceRecord.student_id == student_id)
            if date_from:
                query = query.filter(SQLAttendanceRecord.date >= date_from)
            if date_to:
                query = query.filter(SQLAttendanceRecord.date <= date_to)
            objs = query.all()
            return [
                AttendanceRecord(
                    record_id=o.record_id,
                    student_id=o.student_id,
                    class_id=o.class_id,
                    date=o.date,
                    status=AttendanceStatus(o.status),
                    recorded_by=o.recorded_by,
                    created_at=o.created_at,
                    updated_at=o.updated_at
                )
                for o in objs
            ]

    def get_attendance_by_class(self, class_id: str, date_from: Optional[date] = None, date_to: Optional[date] = None) -> List[AttendanceRecord]:
        with self.session_factory() as session:
            query = session.query(SQLAttendanceRecord).filter(SQLAttendanceRecord.class_id == class_id)
            if date_from:
                query = query.filter(SQLAttendanceRecord.date >= date_from)
            if date_to:
                query = query.filter(SQLAttendanceRecord.date <= date_to)
            objs = query.all()
            return [
                AttendanceRecord(
                    record_id=o.record_id,
                    student_id=o.student_id,
                    class_id=o.class_id,
                    date=o.date,
                    status=AttendanceStatus(o.status),
                    recorded_by=o.recorded_by,
                    created_at=o.created_at,
                    updated_at=o.updated_at
                )
                for o in objs
            ]

    def create_attendance_record(self, record: AttendanceRecord) -> AttendanceRecord:
        with self.session_factory() as session:
            sql_obj = SQLAttendanceRecord(
                record_id=record.record_id,
                student_id=record.student_id,
                class_id=record.class_id,
                date=record.date,
                status=record.status.value if hasattr(record.status, "value") else str(record.status),
                recorded_by=record.recorded_by,
                created_at=record.created_at,
                updated_at=record.updated_at
            )
            session.merge(sql_obj)
            session.commit()
            return record

    def get_attendance_record(self, record_id: str) -> Optional[AttendanceRecord]:
        with self.session_factory() as session:
            obj = session.query(SQLAttendanceRecord).filter(SQLAttendanceRecord.record_id == record_id).first()
            if obj:
                return AttendanceRecord(
                    record_id=obj.record_id,
                    student_id=obj.student_id,
                    class_id=obj.class_id,
                    date=obj.date,
                    status=AttendanceStatus(obj.status),
                    recorded_by=obj.recorded_by,
                    created_at=obj.created_at,
                    updated_at=obj.updated_at
                )
            return None

    def get_attendance_by_date(self, student_id: str, date_val: date) -> Optional[AttendanceRecord]:
        with self.session_factory() as session:
            obj = session.query(SQLAttendanceRecord).filter(
                SQLAttendanceRecord.student_id == student_id,
                SQLAttendanceRecord.date == date_val
            ).first()
            if obj:
                return AttendanceRecord(
                    record_id=obj.record_id,
                    student_id=obj.student_id,
                    class_id=obj.class_id,
                    date=obj.date,
                    status=AttendanceStatus(obj.status),
                    recorded_by=obj.recorded_by,
                    created_at=obj.created_at,
                    updated_at=obj.updated_at
                )
            return None
