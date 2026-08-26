# backend/app/domain/repositories.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from datetime import date
from .models import (
    Student, Parent, Teacher, Class, 
    ParentStudent, TeacherClass, AttendanceRecord
)


class StudentRepository(ABC):
    @abstractmethod
    def get_student(self, student_id: str) -> Optional[Student]:
        pass
    
    @abstractmethod
    def create_student(self, student: Student) -> Student:
        pass
    
    @abstractmethod
    def get_all_students(self) -> List[Student]:
        pass


class ParentRepository(ABC):
    @abstractmethod
    def get_parent(self, parent_id: str) -> Optional[Parent]:
        pass
    
    @abstractmethod
    def create_parent(self, parent: Parent) -> Parent:
        pass
    
    @abstractmethod
    def get_all_parents(self) -> List[Parent]:
        pass


class TeacherRepository(ABC):
    @abstractmethod
    def get_teacher(self, teacher_id: str) -> Optional[Teacher]:
        pass
    
    @abstractmethod
    def create_teacher(self, teacher: Teacher) -> Teacher:
        pass
    
    @abstractmethod
    def get_all_teachers(self) -> List[Teacher]:
        pass


class ClassRepository(ABC):
    @abstractmethod
    def get_class(self, class_id: str) -> Optional[Class]:
        pass
    
    @abstractmethod
    def create_class(self, class_: Class) -> Class:
        pass
    
    @abstractmethod
    def get_all_classes(self) -> List[Class]:
        pass


class ParentStudentRepository(ABC):
    @abstractmethod
    def get_children_for_parent(self, parent_id: str) -> List[str]:  # Returns student_ids
        pass
    
    @abstractmethod
    def get_parents_for_student(self, student_id: str) -> List[str]:  # Returns parent_ids
        pass
    
    @abstractmethod
    def create_relationship(self, relationship: ParentStudent) -> ParentStudent:
        pass
    
    @abstractmethod
    def get_relationships(self, parent_id: str, student_id: str) -> List[ParentStudent]:
        pass


class TeacherClassRepository(ABC):
    @abstractmethod
    def get_classes_for_teacher(self, teacher_id: str) -> List[str]:  # Returns class_ids
        pass
    
    @abstractmethod
    def get_teachers_for_class(self, class_id: str) -> List[str]:  # Returns teacher_ids
        pass
    
    @abstractmethod
    def create_relationship(self, relationship: TeacherClass) -> TeacherClass:
        pass


class AttendanceRepository(ABC):
    @abstractmethod
    def get_attendance_by_student(self, student_id: str, date_from: Optional[date] = None, date_to: Optional[date] = None) -> List[AttendanceRecord]:
        pass
    
    @abstractmethod
    def get_attendance_by_class(self, class_id: str, date_from: Optional[date] = None, date_to: Optional[date] = None) -> List[AttendanceRecord]:
        pass
    
    @abstractmethod
    def create_attendance_record(self, record: AttendanceRecord) -> AttendanceRecord:
        pass
    
    @abstractmethod
    def get_attendance_record(self, record_id: str) -> Optional[AttendanceRecord]:
        pass
    
    @abstractmethod
    def get_attendance_by_date(self, student_id: str, date: date) -> Optional[AttendanceRecord]:
        pass
