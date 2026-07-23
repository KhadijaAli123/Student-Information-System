from flask import Flask
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-this'

# Import models and db after app configuration to avoid circular imports
from models import db, Student, Course, Grade, User

db.init_app(app)

# Import blueprints
from routes import main_bp

app.register_blueprint(main_bp)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Student': Student, 'Course': Course, 'Grade': Grade, 'User': User}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
