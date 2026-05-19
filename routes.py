from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from app import db
from models import Student, Course, Grade
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page with basic statistics"""
    total_students = Student.query.count()
    total_courses = Course.query.count()
    return render_template('index.html', 
                         total_students=total_students,
                         total_courses=total_courses)

@main_bp.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Student Information System is running'}), 200

# ==================== STUDENT ROUTES ====================

@main_bp.route('/students')
def list_students():
    """Display all students"""
    students = Student.query.all()
    return render_template('students_list.html', students=students)

@main_bp.route('/students/add', methods=['GET', 'POST'])
def add_student():
    """Add a new student"""
    if request.method == 'POST':
        try:
            roll_number = request.form.get('roll_number')
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            date_of_birth = request.form.get('date_of_birth')
            address = request.form.get('address')
            
            # Check if student already exists
            if Student.query.filter_by(roll_number=roll_number).first():
                flash(f'Student with roll number {roll_number} already exists!', 'error')
                return redirect(url_for('main.add_student'))
            
            if Student.query.filter_by(email=email).first():
                flash(f'Student with email {email} already exists!', 'error')
                return redirect(url_for('main.add_student'))
            
            new_student = Student(
                roll_number=roll_number,
                name=name,
                email=email,
                phone=phone,
                address=address
            )
            
            if date_of_birth:
                from datetime import datetime as dt
                new_student.date_of_birth = dt.strptime(date_of_birth, '%Y-%m-%d').date()
            
            db.session.add(new_student)
            db.session.commit()
            
            flash(f'Student {name} added successfully!', 'success')
            return redirect(url_for('main.list_students'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding student: {str(e)}', 'error')
            return redirect(url_for('main.add_student'))
    
    return render_template('add_student.html')

@main_bp.route('/students/<int:student_id>')
def view_student(student_id):
    """View a specific student"""
    student = Student.query.get_or_404(student_id)
    return render_template('view_student.html', student=student)

@main_bp.route('/students/<int:student_id>/edit', methods=['GET', 'POST'])
def edit_student(student_id):
    """Edit a student"""
    student = Student.query.get_or_404(student_id)
    
    if request.method == 'POST':
        try:
            student.roll_number = request.form.get('roll_number')
            student.name = request.form.get('name')
            student.email = request.form.get('email')
            student.phone = request.form.get('phone')
            student.address = request.form.get('address')
            
            date_of_birth = request.form.get('date_of_birth')
            if date_of_birth:
                from datetime import datetime as dt
                student.date_of_birth = dt.strptime(date_of_birth, '%Y-%m-%d').date()
            
            db.session.commit()
            flash(f'Student {student.name} updated successfully!', 'success')
            return redirect(url_for('main.view_student', student_id=student.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating student: {str(e)}', 'error')
    
    return render_template('edit_student.html', student=student)

@main_bp.route('/students/<int:student_id>/delete', methods=['GET', 'POST'])
def delete_student(student_id):
    """Delete a student"""
    student = Student.query.get_or_404(student_id)
    
    try:
        student_name = student.name
        db.session.delete(student)
        db.session.commit()
        flash(f'Student {student_name} deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting student: {str(e)}', 'error')
    
    return redirect(url_for('main.list_students'))

# ==================== COURSE ROUTES ====================

@main_bp.route('/courses')
def list_courses():
    """Display all courses"""
    courses = Course.query.all()
    return render_template('courses_list.html', courses=courses)

@main_bp.route('/courses/add', methods=['GET', 'POST'])
def add_course():
    """Add a new course"""
    if request.method == 'POST':
        try:
            course_code = request.form.get('course_code')
            name = request.form.get('name')
            description = request.form.get('description')
            credits = request.form.get('credits', 3)
            semester = request.form.get('semester')
            
            # Check if course already exists
            if Course.query.filter_by(course_code=course_code).first():
                flash(f'Course with code {course_code} already exists!', 'error')
                return redirect(url_for('main.add_course'))
            
            new_course = Course(
                course_code=course_code,
                name=name,
                description=description,
                credits=int(credits),
                semester=int(semester) if semester else None
            )
            
            db.session.add(new_course)
            db.session.commit()
            
            flash(f'Course {name} added successfully!', 'success')
            return redirect(url_for('main.list_courses'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding course: {str(e)}', 'error')
            return redirect(url_for('main.add_course'))
    
    return render_template('add_course.html')

@main_bp.route('/courses/<int:course_id>')
def view_course(course_id):
    """View a specific course"""
    course = Course.query.get_or_404(course_id)
    return render_template('view_course.html', course=course)

@main_bp.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
def edit_course(course_id):
    """Edit a course"""
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        try:
            course.course_code = request.form.get('course_code')
            course.name = request.form.get('name')
            course.description = request.form.get('description')
            course.credits = int(request.form.get('credits', 3))
            
            semester = request.form.get('semester')
            course.semester = int(semester) if semester else None
            
            db.session.commit()
            flash(f'Course {course.name} updated successfully!', 'success')
            return redirect(url_for('main.view_course', course_id=course.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating course: {str(e)}', 'error')
    
    return render_template('edit_course.html', course=course)

@main_bp.route('/courses/<int:course_id>/delete', methods=['GET', 'POST'])
def delete_course(course_id):
    """Delete a course"""
    course = Course.query.get_or_404(course_id)
    
    try:
        course_name = course.name
        db.session.delete(course)
        db.session.commit()
        flash(f'Course {course_name} deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting course: {str(e)}', 'error')
    
    return redirect(url_for('main.list_courses'))
