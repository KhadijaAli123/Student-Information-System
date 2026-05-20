"""
Grade utility functions for calculations
"""

def calculate_gpa(student):
    """Calculate GPA on 4.0 scale for a student"""
    if not student.grades:
        return 0.0
    
    total_points = 0
    total_credits = 0
    
    for grade in student.grades:
        if grade.marks_obtained:
            # Convert percentage to 4.0 scale
            percentage = (grade.marks_obtained / grade.total_marks) * 100
            grade_point = percentage_to_gpa(percentage)
            course_credits = grade.course.credits or 1
            
            total_points += grade_point * course_credits
            total_credits += course_credits
    
    if total_credits == 0:
        return 0.0
    
    return round(total_points / total_credits, 2)

def percentage_to_gpa(percentage):
    """Convert percentage to 4.0 GPA scale"""
    if percentage >= 90:
        return 4.0
    elif percentage >= 85:
        return 3.7
    elif percentage >= 80:
        return 3.3
    elif percentage >= 75:
        return 3.0
    elif percentage >= 70:
        return 2.7
    elif percentage >= 65:
        return 2.3
    elif percentage >= 60:
        return 2.0
    elif percentage >= 55:
        return 1.7
    elif percentage >= 50:
        return 1.3
    elif percentage >= 40:
        return 1.0
    else:
        return 0.0

def get_grade_letter(percentage):
    """Get letter grade based on percentage"""
    if percentage >= 90:
        return 'A'
    elif percentage >= 80:
        return 'B'
    elif percentage >= 70:
        return 'C'
    elif percentage >= 60:
        return 'D'
    else:
        return 'F'

def calculate_student_percentage(student):
    """Calculate overall percentage for a student"""
    if not student.grades:
        return 0.0
    
    total_marks_obtained = 0
    total_marks = 0
    
    for grade in student.grades:
        if grade.marks_obtained:
            total_marks_obtained += grade.marks_obtained
            total_marks += grade.total_marks
    
    if total_marks == 0:
        return 0.0
    
    return round((total_marks_obtained / total_marks) * 100, 2)

def get_total_credits(student):
    """Get total credits for courses taken by student"""
    total = 0
    for course in student.courses:
        total += course.credits or 0
    return total

def get_course_grades_stats(course):
    """Get statistics for grades in a course"""
    if not course.grades:
        return None
    
    marks_list = [g.marks_obtained for g in course.grades if g.marks_obtained]
    
    if not marks_list:
        return None
    
    return {
        'average': round(sum(marks_list) / len(marks_list), 2),
        'highest': max(marks_list),
        'lowest': min(marks_list),
        'total_students': len(course.grades)
    }
