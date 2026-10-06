"""CLI entry point: python main.py"""
from datetime import datetime
from tabulate import tabulate
from db import Database
from models import Student, Company, Job
from services import (StudentService, CompanyService, JobService, EligibilityService,
                      ApplicationService, ReportService, PlacementError)

MENU = """
===== STUDENT PLACEMENT MANAGEMENT SYSTEM =====
 1. Add student              8. Apply to job
 2. List / search students   9. Update application status
 3. Add company             10. Applications of a student
 4. List companies          11. Applicants of a job
 5. Add job                 12. Placement summary
 6. List open jobs          13. Company-wise / branch-wise report
 7. Eligible jobs (student) 14. Unplaced students
 0. Exit
"""


def show(rows):
    print(tabulate(rows, headers="keys", tablefmt="rounded_outline") if rows else "No records.")


def ask(prompt, cast=str):
    return cast(input(prompt).strip())


def main():
    db = Database()
    students, companies, jobs = StudentService(db), CompanyService(db), JobService(db)
    eligibility, apps, reports = EligibilityService(db), ApplicationService(db), ReportService(db)

    actions = {
        "1": lambda: print("Student ID:", students.add(Student(
            ask("Name: "), ask("Email: "), ask("Branch: "), ask("CGPA: ", float),
            ask("Backlogs: ", int), ask("Skills (comma separated): ")))),
        "2": lambda: show(students.search(k) if (k := ask("Keyword (blank = all): ")) else students.list_all()),
        "3": lambda: print("Company ID:", companies.add(Company(ask("Name: "), ask("Industry: "), ask("Location: ")))),
        "4": lambda: show(companies.list_all()),
        "5": lambda: print("Job ID:", jobs.add(Job(
            ask("Company ID: ", int), ask("Title: "), ask("Package (LPA): ", float),
            ask("Min CGPA: ", float), ask("Max backlogs: ", int), ask("Required skills: "),
            datetime.strptime(ask("Deadline (YYYY-MM-DD): "), "%Y-%m-%d").date()))),
        "6": lambda: show(jobs.list_open()),
        "7": lambda: show(eligibility.eligible_jobs(ask("Student ID: ", int))),
        "8": lambda: print("Application ID:", apps.apply(ask("Student ID: ", int), ask("Job ID: ", int))),
        "9": lambda: (apps.update_status(ask("Application ID: ", int),
                      ask("New status (APPLIED/SHORTLISTED/REJECTED/SELECTED): ")), print("Updated.")),
        "10": lambda: show(apps.for_student(ask("Student ID: ", int))),
        "11": lambda: show(apps.for_job(ask("Job ID: ", int))),
        "12": lambda: show([reports.summary()]),
        "13": lambda: (show(reports.company_wise()), show(reports.branch_wise())),
        "14": lambda: show(reports.unplaced()),
    }

    try:
        while True:
            print(MENU)
            choice = input("Choice: ").strip()
            if choice == "0":
                break
            action = actions.get(choice)
            if not action:
                print("Invalid choice.")
                continue
            try:
                action()
            except PlacementError as e:
                print("Error:", e)
            except ValueError as e:
                print("Invalid input:", e)
            except Exception as e:  # DB errors (duplicate email, FK violation, etc.)
                print("Database error:", e)
    finally:
        db.close()
        print("Bye.")


if __name__ == "__main__":
    main()