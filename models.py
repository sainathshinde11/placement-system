from dataclasses import dataclass, field
from datetime import date


def parse_skills(text: str) -> set:
    return {s.strip().lower() for s in text.split(",") if s.strip()}


@dataclass
class Student:
    name: str
    email: str
    branch: str
    cgpa: float
    backlogs: int = 0
    skills: str = ""
    student_id: int = None

    def __post_init__(self):
        if not 0 <= self.cgpa <= 10:
            raise ValueError("CGPA must be between 0 and 10")
        if self.backlogs < 0:
            raise ValueError("Backlogs cannot be negative")
        if "@" not in self.email:
            raise ValueError("Invalid email")


@dataclass
class Company:
    name: str
    industry: str = ""
    location: str = ""
    company_id: int = None


@dataclass
class Job:
    company_id: int
    title: str
    package_lpa: float
    min_cgpa: float = 0.0
    max_backlogs: int = 0
    required_skills: str = ""
    deadline: date = field(default_factory=date.today)
    job_id: int = None