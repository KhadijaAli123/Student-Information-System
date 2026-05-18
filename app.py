from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student_system.db'
app.config['SECRET_KEY'] = 'your-secret-key-change-this'

db = SQLAlchemy(app)

# Import models after db initialization
from models import Student, Course, Grade

# Import blueprints
from routes import main_bp

app.register_blueprint(main_bp)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Student': Student, 'Course': Course, 'Grade': Grade}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
