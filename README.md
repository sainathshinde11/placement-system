# Student Placement Management System

Python + MySQL (OOP, layered: models → services → CLI). Manages students, companies, jobs,
applications and placements with automatic eligibility filtering.

## Features
- Student / company / job CRUD
- Eligibility filter: CGPA, backlogs, deadline, job status, already-placed check
- Skill-match % between student skills and job requirements
- Application workflow: APPLIED → SHORTLISTED → REJECTED / SELECTED
- SELECTED is atomic (transaction): records placement, auto-rejects other pending applications
- Reports: placement %, avg/highest package, company-wise, branch-wise, unplaced students

## Setup
```bash
pip install -r requirements.txt
mysql -u root -p < schema.sql
mysql -u root -p < seed.sql          # optional sample data
export DB_USER=root DB_PASSWORD=yourpass   # Windows: set DB_USER=root
python main.py
```

## Structure
| File | Role |
|---|---|
| schema.sql / seed.sql | Tables, constraints, indexes, sample data |
| config.py | DB credentials via env vars |
| db.py | Connection + query/transaction helper |
| models.py | Dataclasses with validation |
| services.py | Business logic + SQL |
| main.py | Menu-driven CLI |

## Try this flow
1. Option 7, student `1` → eligible jobs with skill-match %
2. Option 8 → apply to a job
3. Option 9 → set `SELECTED` → check option 12 / 14