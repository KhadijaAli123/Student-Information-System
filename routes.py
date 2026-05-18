from flask import Blueprint, render_template, request, redirect, url_for, jsonify
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
