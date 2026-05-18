from app import db
from datetime import datetime

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.String(200))
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    grades = db.relationship('Grade', backref='student', lazy=True, cascade='all, delete-orphan')
    courses = db.relationship('Course', secondary='enrollments', backref='students')
    
    def __repr__(self):
        return f'<Student {self.name}>'

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    credits = db.Column(db.Integer, default=3)
    semester = db.Column(db.Integer)
    
    # Relationships
    grades = db.relationship('Grade', backref='course', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Course {self.course_code}>'

class Grade(db.Model):
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    marks_obtained = db.Column(db.Float)
    total_marks = db.Column(db.Float, default=100)
    grade = db.Column(db.String(2))
    date_recorded = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Grade {self.student_id}-{self.course_id}>'

# Association table for many-to-many relationship
enrollments = db.Table('enrollments',
    db.Column('student_id', db.Integer, db.ForeignKey('students.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'))
)
