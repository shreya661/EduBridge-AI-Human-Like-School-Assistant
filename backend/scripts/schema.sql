-- PostgreSQL Schema for XYZ AI School Assistant
-- Database: school_erp

-- 1. Classes Table
CREATE TABLE IF NOT EXISTS classes (
    class_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    grade_level INTEGER,
    section VARCHAR(10),
    teacher_id VARCHAR(50)
);

-- 2. Students Table
CREATE TABLE IF NOT EXISTS students (
    student_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    class_id VARCHAR(50) REFERENCES classes(class_id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Parents Table
CREATE TABLE IF NOT EXISTS parents (
    parent_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150),
    phone VARCHAR(50)
);

-- 4. Teachers Table
CREATE TABLE IF NOT EXISTS teachers (
    teacher_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    subject VARCHAR(100)
);

-- 5. Parent-Student Relationship Table (Multi-Child Mapping)
CREATE TABLE IF NOT EXISTS parent_students (
    id SERIAL PRIMARY KEY,
    parent_id VARCHAR(50) NOT NULL REFERENCES parents(parent_id) ON DELETE CASCADE,
    student_id VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE
);

-- 6. Teacher-Class Relationship Table
CREATE TABLE IF NOT EXISTS teacher_classes (
    id SERIAL PRIMARY KEY,
    teacher_id VARCHAR(50) NOT NULL REFERENCES teachers(teacher_id) ON DELETE CASCADE,
    class_id VARCHAR(50) NOT NULL REFERENCES classes(class_id) ON DELETE CASCADE
);

-- 7. Attendance Records Table
CREATE TABLE IF NOT EXISTS attendance_records (
    record_id VARCHAR(60) PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    class_id VARCHAR(50),
    date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PRESENT',
    recorded_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance_records(student_id);
CREATE INDEX IF NOT EXISTS idx_attendance_class ON attendance_records(class_id);
CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance_records(date);
CREATE INDEX IF NOT EXISTS idx_parent_students_parent ON parent_students(parent_id);
CREATE INDEX IF NOT EXISTS idx_teacher_classes_teacher ON teacher_classes(teacher_id);
