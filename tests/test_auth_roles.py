import unittest

from app import app, db
from models import User


class AdminRoleRegistrationTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, SQLALCHEMY_DATABASE_URI='sqlite:///:memory:')
        self.client = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_admin_role_can_be_selected_during_registration(self):
        with app.app_context():
            db.session.add(User(email='existing@example.com', password_hash='x', role='admin'))
            db.session.commit()

        response = self.client.post('/register', data={
            'email': 'admin@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'role': 'admin'
        }, follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        with app.app_context():
            user = User.query.filter_by(email='admin@example.com').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.role, 'admin')


if __name__ == '__main__':
    unittest.main()
