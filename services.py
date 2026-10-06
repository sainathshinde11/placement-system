from datetime import date
from models import Student, Company, Job, parse_skills

STATUSES = ("APPLIED", "SHORTLISTED", "REJECTED", "SELECTED")


class PlacementError(Exception):
    pass


class StudentService:
    def __init__(self, db):
        self.db = db

    def add(self, s: Student) -> int:
        return self.db.execute(
            "INSERT INTO students (name,email,branch,cgpa,backlogs,skills) VALUES (%s,%s,%s,%s,%s,%s)",
            (s.name, s.email, s.branch, s.cgpa, s.backlogs, s.skills),
        )

    def get(self, student_id):
        row = self.db.fetch_one("SELECT * FROM students WHERE student_id=%s", (student_id,))
        if not row:
            raise PlacementError(f"Student {student_id} not found")
        return row

    def list_all(self):
        return self.db.fetch_all("SELECT student_id,name,branch,cgpa,backlogs,skills FROM students ORDER BY name")

    def search(self, keyword):
        like = f"%{keyword}%"
        return self.db.fetch_all(
            "SELECT student_id,name,branch,cgpa,backlogs,skills FROM students "
            "WHERE name LIKE %s OR skills LIKE %s OR branch LIKE %s ORDER BY cgpa DESC",
            (like, like, like),
        )

    def update_cgpa(self, student_id, cgpa):
        if not 0 <= cgpa <= 10:
            raise PlacementError("CGPA must be between 0 and 10")
        self.get(student_id)
        self.db.execute("UPDATE students SET cgpa=%s WHERE student_id=%s", (cgpa, student_id))

    def delete(self, student_id):
        self.get(student_id)
        self.db.execute("DELETE FROM students WHERE student_id=%s", (student_id,))


class CompanyService:
    def __init__(self, db):
        self.db = db

    def add(self, c: Company) -> int:
        return self.db.execute(
            "INSERT INTO companies (name,industry,location) VALUES (%s,%s,%s)",
            (c.name, c.industry, c.location),
        )

    def list_all(self):
        return self.db.fetch_all("SELECT * FROM companies ORDER BY name")


class JobService:
    def __init__(self, db):
        self.db = db

    def add(self, j: Job) -> int:
        return self.db.execute(
            "INSERT INTO jobs (company_id,title,package_lpa,min_cgpa,max_backlogs,required_skills,deadline) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (j.company_id, j.title, j.package_lpa, j.min_cgpa, j.max_backlogs, j.required_skills, j.deadline),
        )

    def get(self, job_id):
        row = self.db.fetch_one(
            "SELECT j.*, c.name AS company FROM jobs j JOIN companies c USING(company_id) WHERE job_id=%s",
            (job_id,),
        )
        if not row:
            raise PlacementError(f"Job {job_id} not found")
        return row

    def list_open(self):
        return self.db.fetch_all(
            "SELECT j.job_id, c.name AS company, j.title, j.package_lpa, j.min_cgpa, j.max_backlogs, "
            "j.required_skills, j.deadline FROM jobs j JOIN companies c USING(company_id) "
            "WHERE j.status='OPEN' AND j.deadline >= CURDATE() ORDER BY j.package_lpa DESC"
        )

    def close(self, job_id):
        self.get(job_id)
        self.db.execute("UPDATE jobs SET status='CLOSED' WHERE job_id=%s", (job_id,))


class EligibilityService:
    """Core business rule: academic + backlog + deadline + not already placed."""

    def __init__(self, db):
        self.db = db

    @staticmethod
    def check(student: dict, job: dict):
        """Returns (eligible: bool, reasons: list[str])."""
        reasons = []
        if job["status"] != "OPEN":
            reasons.append("Job is closed")
        if job["deadline"] < date.today():
            reasons.append("Deadline passed")
        if student["cgpa"] < job["min_cgpa"]:
            reasons.append(f"CGPA {student['cgpa']} < required {job['min_cgpa']}")
        if student["backlogs"] > job["max_backlogs"]:
            reasons.append(f"Backlogs {student['backlogs']} > allowed {job['max_backlogs']}")
        return (not reasons, reasons)

    def eligible_jobs(self, student_id):
        """Open jobs the student qualifies for and hasn't applied to, with skill-match %."""
        student = self.db.fetch_one("SELECT * FROM students WHERE student_id=%s", (student_id,))
        if not student:
            raise PlacementError(f"Student {student_id} not found")
        rows = self.db.fetch_all(
            "SELECT j.job_id, c.name AS company, j.title, j.package_lpa, j.required_skills "
            "FROM jobs j JOIN companies c USING(company_id) "
            "WHERE j.status='OPEN' AND j.deadline >= CURDATE() "
            "AND j.min_cgpa <= %s AND j.max_backlogs >= %s "
            "AND j.job_id NOT IN (SELECT job_id FROM applications WHERE student_id=%s) "
            "ORDER BY j.package_lpa DESC",
            (student["cgpa"], student["backlogs"], student_id),
        )
        have = parse_skills(student["skills"])
        for r in rows:
            need = parse_skills(r["required_skills"])
            r["skill_match_%"] = round(100 * len(have & need) / len(need)) if need else 100
        return rows


class ApplicationService:
    def __init__(self, db):
        self.db = db
        self.students = StudentService(db)
        self.jobs = JobService(db)

    def apply(self, student_id, job_id) -> int:
        student = self.students.get(student_id)
        job = self.jobs.get(job_id)
        if self.db.fetch_one("SELECT 1 FROM placements WHERE student_id=%s", (student_id,)):
            raise PlacementError("Student is already placed")
        ok, reasons = EligibilityService.check(student, job)
        if not ok:
            raise PlacementError("Not eligible: " + "; ".join(reasons))
        if self.db.fetch_one(
            "SELECT 1 FROM applications WHERE student_id=%s AND job_id=%s", (student_id, job_id)
        ):
            raise PlacementError("Already applied to this job")
        return self.db.execute(
            "INSERT INTO applications (student_id, job_id) VALUES (%s,%s)", (student_id, job_id)
        )

    def update_status(self, application_id, new_status):
        new_status = new_status.upper()
        if new_status not in STATUSES:
            raise PlacementError(f"Status must be one of {STATUSES}")
        app = self.db.fetch_one("SELECT * FROM applications WHERE application_id=%s", (application_id,))
        if not app:
            raise PlacementError(f"Application {application_id} not found")
        if app["status"] == "SELECTED":
            raise PlacementError("Application already finalised as SELECTED")

        if new_status != "SELECTED":
            self.db.execute(
                "UPDATE applications SET status=%s WHERE application_id=%s", (new_status, application_id)
            )
            return

        # SELECTED -> atomic: mark selected, record placement, reject other open applications
        if self.db.fetch_one("SELECT 1 FROM placements WHERE student_id=%s", (app["student_id"],)):
            raise PlacementError("Student already has an offer")
        job = self.jobs.get(app["job_id"])
        with self.db.transaction() as cur:
            cur.execute("UPDATE applications SET status='SELECTED' WHERE application_id=%s", (application_id,))
            cur.execute(
                "INSERT INTO placements (student_id, job_id, package_lpa) VALUES (%s,%s,%s)",
                (app["student_id"], app["job_id"], job["package_lpa"]),
            )
            cur.execute(
                "UPDATE applications SET status='REJECTED' "
                "WHERE student_id=%s AND application_id<>%s AND status IN ('APPLIED','SHORTLISTED')",
                (app["student_id"], application_id),
            )

    def for_student(self, student_id):
        return self.db.fetch_all(
            "SELECT a.application_id, c.name AS company, j.title, j.package_lpa, a.applied_on, a.status "
            "FROM applications a JOIN jobs j USING(job_id) JOIN companies c USING(company_id) "
            "WHERE a.student_id=%s ORDER BY a.applied_on DESC",
            (student_id,),
        )

    def for_job(self, job_id):
        return self.db.fetch_all(
            "SELECT a.application_id, s.student_id, s.name, s.cgpa, s.skills, a.status "
            "FROM applications a JOIN students s USING(student_id) WHERE a.job_id=%s ORDER BY s.cgpa DESC",
            (job_id,),
        )


class ReportService:
    def __init__(self, db):
        self.db = db

    def summary(self):
        return self.db.fetch_one(
            "SELECT (SELECT COUNT(*) FROM students) AS total_students, "
            "(SELECT COUNT(*) FROM placements) AS placed, "
            "ROUND(100*(SELECT COUNT(*) FROM placements)/NULLIF((SELECT COUNT(*) FROM students),0),2) AS placement_pct, "
            "(SELECT ROUND(AVG(package_lpa),2) FROM placements) AS avg_package, "
            "(SELECT MAX(package_lpa) FROM placements) AS highest_package"
        )

    def company_wise(self):
        return self.db.fetch_all(
            "SELECT c.name AS company, COUNT(p.placement_id) AS hires, "
            "ROUND(AVG(p.package_lpa),2) AS avg_package "
            "FROM companies c LEFT JOIN jobs j USING(company_id) "
            "LEFT JOIN placements p ON p.job_id=j.job_id GROUP BY c.company_id ORDER BY hires DESC"
        )

    def branch_wise(self):
        return self.db.fetch_all(
            "SELECT s.branch, COUNT(*) AS students, COUNT(p.placement_id) AS placed, "
            "ROUND(100*COUNT(p.placement_id)/COUNT(*),2) AS placement_pct "
            "FROM students s LEFT JOIN placements p USING(student_id) GROUP BY s.branch"
        )

    def unplaced(self):
        return self.db.fetch_all(
            "SELECT s.student_id, s.name, s.cgpa, s.backlogs FROM students s "
            "LEFT JOIN placements p USING(student_id) WHERE p.placement_id IS NULL ORDER BY s.cgpa DESC"
        )