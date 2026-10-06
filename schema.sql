-- Student Placement Management System (MySQL)
CREATE DATABASE IF NOT EXISTS placement_db;
USE placement_db;

DROP TABLE IF EXISTS placements;
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS students;

CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(120) NOT NULL UNIQUE,
    branch     VARCHAR(50)  NOT NULL,
    cgpa       DECIMAL(4,2) NOT NULL CHECK (cgpa BETWEEN 0 AND 10),
    backlogs   INT NOT NULL DEFAULT 0 CHECK (backlogs >= 0),
    skills     VARCHAR(255) NOT NULL DEFAULT ''
);

CREATE TABLE companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL UNIQUE,
    industry   VARCHAR(60),
    location   VARCHAR(60)
);

CREATE TABLE jobs (
    job_id          INT AUTO_INCREMENT PRIMARY KEY,
    company_id      INT NOT NULL,
    title           VARCHAR(100) NOT NULL,
    package_lpa     DECIMAL(5,2) NOT NULL,
    min_cgpa        DECIMAL(4,2) NOT NULL DEFAULT 0,
    max_backlogs    INT NOT NULL DEFAULT 0,
    required_skills VARCHAR(255) NOT NULL DEFAULT '',
    deadline        DATE NOT NULL,
    status          ENUM('OPEN','CLOSED') NOT NULL DEFAULT 'OPEN',
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

CREATE TABLE applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id     INT NOT NULL,
    job_id         INT NOT NULL,
    applied_on     DATE NOT NULL DEFAULT (CURRENT_DATE),
    status         ENUM('APPLIED','SHORTLISTED','REJECTED','SELECTED') NOT NULL DEFAULT 'APPLIED',
    UNIQUE KEY uq_student_job (student_id, job_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (job_id)     REFERENCES jobs(job_id)         ON DELETE CASCADE
);

CREATE TABLE placements (
    placement_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id   INT NOT NULL UNIQUE,
    job_id       INT NOT NULL,
    package_lpa  DECIMAL(5,2) NOT NULL,
    placed_on    DATE NOT NULL DEFAULT (CURRENT_DATE),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (job_id)     REFERENCES jobs(job_id)         ON DELETE CASCADE
);

CREATE INDEX idx_jobs_status_deadline ON jobs(status, deadline);
CREATE INDEX idx_apps_status ON applications(status);