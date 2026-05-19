"""
Course utility functions and helpers
"""

def get_course_statistics(course):
    """Get statistics for a course"""
    return {
        'total_students': len(course.students),
        'total_grades': len(course.grades),
        'average_grade': calculate_average_grade(course),
        'credits': course.credits
    }

def calculate_average_grade(course):
    """Calculate average grade for a course"""
    if not course.grades:
        return 0.0
    
    total_marks = sum(g.marks_obtained for g in course.grades if g.marks_obtained)
    count = len([g for g in course.grades if g.marks_obtained])
    
    return round(total_marks / count, 2) if count > 0 else 0.0

def get_student_enrollment_status(student, course):
    """Check if student is enrolled in course"""
    return student in course.students

def get_student_courses(student):
    """Get all courses for a student"""
    return student.courses

def get_course_enrollment_percentage(course, total_students):
    """Get enrollment percentage"""
    if total_students == 0:
        return 0
    return round((len(course.students) / total_students) * 100, 2)
