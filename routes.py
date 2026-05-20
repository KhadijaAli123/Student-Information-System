from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from app import db
from models import Student, Course, Grade
from datetime import datetime
from grade_utils import calculate_gpa, calculate_student_percentage, get_grade_letter, get_total_credits

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page with basic statistics"""
    total_students = Student.query.count()
    total_courses = Course.query.count()
    total_enrollments = db.session.query(enrollments).count()
    total_grades = Grade.query.count()
    
    return render_template('index.html', 
                         total_students=total_students,
                         total_courses=total_courses,
                         total_enrollments=total_enrollments,
                         total_grades=total_grades)

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

# ==================== ENROLLMENT ROUTES ====================

@main_bp.route('/courses/<int:course_id>/enroll', methods=['GET', 'POST'])
def enroll_student(course_id):
    """Enroll a student in a course"""
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        try:
            student_id = request.form.get('student_id')
            student = Student.query.get(student_id)
            
            if not student:
                flash('Student not found!', 'error')
                return redirect(url_for('main.enroll_student', course_id=course_id))
            
            # Check if already enrolled
            if student in course.students:
                flash(f'Student {student.name} is already enrolled in this course!', 'error')
                return redirect(url_for('main.enroll_student', course_id=course_id))
            
            course.students.append(student)
            db.session.commit()
            
            flash(f'Student {student.name} enrolled successfully!', 'success')
            return redirect(url_for('main.view_course', course_id=course_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error enrolling student: {str(e)}', 'error')
    
    # Get students not yet enrolled in this course
    enrolled_student_ids = [s.id for s in course.students]
    available_students = Student.query.filter(~Student.id.in_(enrolled_student_ids)).all()
    
    return render_template('enroll_student.html', course=course, available_students=available_students)

@main_bp.route('/courses/<int:course_id>/remove-enrollment/<int:student_id>', methods=['GET'])
def remove_enrollment(course_id, student_id):
    """Remove a student from a course"""
    course = Course.query.get_or_404(course_id)
    student = Student.query.get_or_404(student_id)
    
    try:
        course.students.remove(student)
        db.session.commit()
        flash(f'Student {student.name} removed from {course.name}!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing student: {str(e)}', 'error')
    
    return redirect(url_for('main.view_course', course_id=course_id))

# ==================== GRADE ROUTES ====================

@main_bp.route('/grades')
def list_grades():
    """Display all grades with search functionality"""
    search = request.args.get('search', '')
    
    if search:
        grades = Grade.query.filter(
            (Student.name.ilike(f'%{search}%')) | 
            (Course.course_code.ilike(f'%{search}%'))
        ).join(Student).join(Course).all()
    else:
        grades = Grade.query.all()
    
    return render_template('grades_list.html', grades=grades, search=search)

@main_bp.route('/grades/add', methods=['GET', 'POST'])
def add_grade():
    """Add a new grade record"""
    if request.method == 'POST':
        try:
            student_id = request.form.get('student_id')
            course_id = request.form.get('course_id')
            marks_obtained = request.form.get('marks_obtained')
            total_marks = float(request.form.get('total_marks', 100))
            grade_letter = request.form.get('grade')
            
            student = Student.query.get(student_id)
            course = Course.query.get(course_id)
            
            if not student or not course:
                flash('Invalid student or course selection', 'error')
                return redirect(url_for('main.add_grade'))
            
            # Check if grade already exists
            existing = Grade.query.filter_by(
                student_id=student_id,
                course_id=course_id
            ).first()
            
            if existing:
                flash(f'Grade already exists for this student-course combination', 'error')
                return redirect(url_for('main.add_grade'))
            
            marks_obtained = float(marks_obtained)
            percentage = (marks_obtained / total_marks) * 100
            
            # Auto-calculate grade if not provided
            if not grade_letter:
                grade_letter = get_grade_letter(percentage)
            
            new_grade = Grade(
                student_id=student_id,
                course_id=course_id,
                marks_obtained=marks_obtained,
                total_marks=total_marks,
                grade=grade_letter
            )
            
            db.session.add(new_grade)
            db.session.commit()
            
            flash(f'Grade recorded successfully for {student.name}!', 'success')
            return redirect(url_for('main.list_grades'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error recording grade: {str(e)}', 'error')
            return redirect(url_for('main.add_grade'))
    
    students = Student.query.all()
    courses = Course.query.all()
    return render_template('add_grade.html', students=students, courses=courses)

@main_bp.route('/grades/<int:grade_id>/edit', methods=['GET', 'POST'])
def edit_grade(grade_id):
    """Edit a grade record"""
    grade = Grade.query.get_or_404(grade_id)
    
    if request.method == 'POST':
        try:
            marks_obtained = float(request.form.get('marks_obtained'))
            total_marks = float(request.form.get('total_marks', 100))
            grade_letter = request.form.get('grade')
            
            grade.marks_obtained = marks_obtained
            grade.total_marks = total_marks
            
            percentage = (marks_obtained / total_marks) * 100
            
            if not grade_letter:
                grade.grade = get_grade_letter(percentage)
            else:
                grade.grade = grade_letter
            
            db.session.commit()
            flash('Grade updated successfully!', 'success')
            return redirect(url_for('main.list_grades'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating grade: {str(e)}', 'error')
    
    return render_template('edit_grade.html', grade=grade)

@main_bp.route('/grades/<int:grade_id>/delete', methods=['GET', 'POST'])
def delete_grade(grade_id):
    """Delete a grade record"""
    grade = Grade.query.get_or_404(grade_id)
    
    try:
        student_name = grade.student.name
        course_name = grade.course.name
        db.session.delete(grade)
        db.session.commit()
        flash(f'Grade deleted for {student_name} in {course_name}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting grade: {str(e)}', 'error')
    
    return redirect(url_for('main.list_grades'))
