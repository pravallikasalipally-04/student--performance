CREATE DATABASE IF NOT EXISTS student_performance_db;
USE student_performance_db;

CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    student_id INT NULL,
    CONSTRAINT fk_user_student FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE IF NOT EXISTS grades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    date DATE NOT NULL,
    CONSTRAINT fk_grade_student FOREIGN KEY (student_id) REFERENCES students(id),
    CONSTRAINT fk_grade_course FOREIGN KEY (course_id) REFERENCES courses(id)
);

INSERT INTO students(name,email) VALUES
('Rahul Kumar','rahul@example.com'),
('Priya Sharma','priya@example.com'),
('Anu Reddy','anu@example.com')
ON DUPLICATE KEY UPDATE name=VALUES(name);

INSERT INTO courses(name,code) VALUES
('Python Full Stack','PFS101'),
('Database Management','DBMS101'),
('Data Analytics','DA101')
ON DUPLICATE KEY UPDATE name=VALUES(name);

INSERT INTO grades(student_id,course_id,score,date) VALUES
(1,1,85,'2026-09-20'),
(1,2,78,'2026-09-21'),
(2,1,92,'2026-09-20'),
(2,2,88,'2026-09-21'),
(3,1,74,'2026-09-20'),
(3,3,81,'2026-09-22');
