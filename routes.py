from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, session, g
from app import db
from models import Student, Course, Grade, User, enrollments
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from grade_utils import calculate_gpa, calculate_student_percentage, get_grade_letter, get_total_credits, get_course_grades_stats

main_bp = Blueprint('main', __name__)


# AI GPT suggested pattern: set global user context once and use it across routes for cleaner auth checks. 
def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.current_user is None:
            flash('Please login to access this page', 'error')
            return redirect(url_for('main.login'))
        return view(**kwargs)
    return wrapped_view


def role_required(role):
    def decorator(view):
        @wraps(view)
        def wrapped_view(**kwargs):
            if g.current_user is None:
                flash('Please login to access this page', 'error')
                return redirect(url_for('main.login'))
            if g.current_user.role != role:
                flash('You do not have permission to access this page', 'error')
                return redirect(url_for('main.index'))
            return view(**kwargs)
        return wrapped_view
    return decorator


@main_bp.before_app_request
def load_current_user():
    user_id = session.get('user_id')
    g.current_user = None
    g.is_admin = False
    if user_id:
        g.current_user = User.query.get(user_id)
        g.is_admin = g.current_user.role == 'admin'


@main_bp.route('/')
def index():
    """Home page with basic statistics"""
    total_students = Student.query.count()
    total_courses = Course.query.count()
    total_enrollments = db.session.query(enrollments).count()
    total_grades = Grade.query.count()
    
    all_students = Student.query.all()
    student_gpa_values = [calculate_gpa(student) for student in all_students if student.grades]
    average_gpa = round(sum(student_gpa_values) / len(student_gpa_values), 2) if student_gpa_values else 0.0
    top_students = sorted(
        [(student, calculate_gpa(student)) for student in all_students if student.grades],
        key=lambda item: item[1], reverse=True
    )[:3]
    
    return render_template('index.html', 
                         total_students=total_students,
                         total_courses=total_courses,
                         total_enrollments=total_enrollments,
                         total_grades=total_grades,
                         average_gpa=average_gpa,
                         top_students=top_students)

@main_bp.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Student Information System is running'}), 200

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_role'] = user.role
            flash(f'Welcome back, {user.email}', 'success')
            return redirect(url_for('main.index'))

        flash('Invalid email or password', 'error')
        return redirect(url_for('main.login'))

    return render_template('login.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('main.register'))

        if User.query.filter_by(email=email).first():
            flash('Email is already registered', 'error')
            return redirect(url_for('main.register'))

        role = 'student'
        if User.query.count() == 0:
            role = 'admin'

        new_user = User(
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. You can login now.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')

@main_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('main.login'))

@main_bp.route('/profile')
@login_required
def profile():
    """Display the current user profile"""
    return render_template('profile.html', user=g.current_user)

# ==================== STUDENT ROUTES ====================

@main_bp.route('/students')
@login_required
def list_students():
    """Display all students"""
    students = Student.query.all()
    return render_template('students_list.html', students=students)

@main_bp.route('/students/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
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
@login_required
def view_student(student_id):
    """View a specific student"""
    student = Student.query.get_or_404(student_id)
    return render_template('view_student.html', student=student)

@main_bp.route('/students/<int:student_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
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
@login_required
@role_required('admin')
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
@login_required
def list_courses():
    """Display all courses"""
    courses = Course.query.all()
    return render_template('courses_list.html', courses=courses)

@main_bp.route('/courses/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
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
@login_required
def view_course(course_id):
    """View a specific course"""
    course = Course.query.get_or_404(course_id)
    return render_template('view_course.html', course=course)

@main_bp.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
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
@login_required
@role_required('admin')
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
@login_required
@role_required('admin')
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
@login_required
@role_required('admin')
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
@login_required
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
@login_required
@role_required('admin')
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
@login_required
@role_required('admin')
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
@login_required
@role_required('admin')
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

# ==================== TRANSCRIPT ROUTES ====================

@main_bp.route('/students/<int:student_id>/transcript')
@login_required
def view_transcript(student_id):
    """Display student academic transcript with GPA and performance metrics"""
    student = Student.query.get_or_404(student_id)
    
    gpa = calculate_gpa(student)
    overall_percentage = calculate_student_percentage(student)
    total_credits = get_total_credits(student)
    
    return render_template('transcript.html',
                         student=student,
                         gpa=gpa,
                         overall_percentage=overall_percentage,
                         total_credits=total_credits)

@main_bp.route('/reports')
@login_required
def reports():
    """Display dashboard reports and course performance summaries"""
    total_students = Student.query.count()
    total_courses = Course.query.count()
    total_enrollments = db.session.query(enrollments).count()
    total_grades = Grade.query.count()

    students = Student.query.all()
    graded_student_records = [
        (student, calculate_gpa(student)) for student in students if student.grades
    ]
    top_students = sorted(graded_student_records, key=lambda item: item[1], reverse=True)[:5]
    average_gpa = round(sum([gpa for _, gpa in graded_student_records]) / len(graded_student_records), 2) if graded_student_records else 0.0

    courses = Course.query.all()
    course_reports = []
    for course in courses:
        stats = get_course_grades_stats(course)
        course_reports.append({
            'course': course,
            'stats': stats,
            'enrolled': len(course.students)
        })

    distribution = {
        'A': 0,
        'B': 0,
        'C': 0,
        'D': 0,
        'F': 0,
        'N/A': 0
    }
    for grade in Grade.query.all():
        key = grade.grade if grade.grade in distribution else 'N/A'
        distribution[key] += 1

    return render_template('reports.html',
                         total_students=total_students,
                         total_courses=total_courses,
                         total_enrollments=total_enrollments,
                         total_grades=total_grades,
                         average_gpa=average_gpa,
                         top_students=top_students,
                         course_reports=course_reports,
                         distribution=distribution)
 
