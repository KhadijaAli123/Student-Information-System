# Student Information System

A comprehensive web-based Student Information System built with Flask and SQLite.

## Project Structure

```
/
├── app.py                 # Main Flask application
├── models.py             # Database models (Student, Course, Grade)
├── routes.py             # Application routes
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   └── index.html       # Home page
└── README.md            # This file
```

## Features (7-Day Development Plan)

### Day 1: Project Setup & Database Models ✓
- Flask project initialization
- SQLAlchemy models (Student, Course, Grade)
- Database configuration
- Basic home route

### Day 2: Student Management Module
- CRUD operations for students
- Student list, add, edit, delete
- Student forms and validation

### Day 3: Course Management Module
- CRUD operations for courses
- Enroll students in courses
- Course management

### Day 4: Grade Management Module
- Record grades for students
- Calculate GPA
- View transcripts

### Day 5: Dashboard & Reports
- Student performance dashboard
- Generate reports
- Statistics visualization

### Day 6: Authentication & Security
- User login/registration
- Role-based access control
- Security enhancements

### Day 7: Polish & Deployment
- Bug fixes
- UI/UX improvements
- Final testing
- Deployment preparation

## Installation

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python app.py
```

The application will run on `http://localhost:5000`

## First User and Admin Access

- The first user to register is assigned the `admin` role automatically.
- Subsequent users are assigned the `student` role by default.
- Admin users can manage students, courses, enrollments, grades, and reports.

## Features

- User login and registration
- Role-based access control for admin users
- Student CRUD operations
- Course CRUD operations
- Enrollment management
- Grade tracking and transcript generation
- Dashboard reports with GPA and grade distribution metrics

## Database Models

### Student
- Roll Number (unique)
- Name
- Email (unique)
- Phone
- Date of Birth
- Address
- Enrollment Date

### Course
- Course Code (unique)
- Name
- Description
- Credits
- Semester

### Grade
- Student ID (Foreign Key)
- Course ID (Foreign Key)
- Marks Obtained
- Total Marks 
- Grade (Letter)
- Date Recorded
 
### References
Pallets Projects (2024) Flask Documentation. Available at: https://flask.palletsprojects.com/en/latest/ (Accessed: 14 June 2026).

SQLAlchemy Authors (2024) SQLAlchemy Documentation. Available at: https://docs.sqlalchemy.org/en/20/ (Accessed: 14 June 2026).

SQLite Consortium (2024) SQLite Official Documentation. Available at: https://www.sqlite.org/docs.html (Accessed: 14 June 2026).

Werkzeug Contributors (2024) Werkzeug Documentation. Available at: https://werkzeug.palletsprojects.com/en/latest/ (Accessed: 14 June 2026).

MDN Web Docs (2024) HTTP and Web Security Basics. Available at: https://developer.mozilla.org/en-US/docs/Web/HTTP (Accessed: 14 June 2026).
