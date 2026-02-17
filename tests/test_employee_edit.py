import pytest
from app import app, db, Employee
from datetime import date

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create a test employee for all tests in this file
            emp = Employee(
                employee_number='12345', 
                first_name='John', 
                last_name='Doe',
                birth_date=date(1990, 1, 1),
                gender='M'
            )
            db.session.add(emp)
            db.session.commit()
            yield client
        with app.app_context():
            db.drop_all()

def login(client, employee_number='12345'):
    return client.post('/login', data={'employee_number': employee_number}, follow_redirects=True)

def test_edit_profile_page_loads(client):
    login(client)
    response = client.get('/profile/edit')
    assert response.status_code == 200
    assert b'Edit Profile' in response.data
    assert b'John' in response.data
    assert b'Doe' in response.data

def test_edit_profile_success(client):
    login(client)
    response = client.post('/profile/edit', data={
        'first_name': 'Jane',
        'last_name': 'Smith',
        'birth_date': '1995-05-05',
        'gender': 'F'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Profile updated successfully' in response.data
    assert b'Jane Smith' in response.data
    assert b'1995-05-05' in response.data
    assert b'F' in response.data

    # Verify in database
    with app.app_context():
        emp = db.session.get(Employee, '12345')
        assert emp.first_name == 'Jane'
        assert emp.last_name == 'Smith'
        assert emp.gender == 'F'

def test_edit_profile_unauthorized(client):
    # Try to access edit page without login
    response = client.get('/profile/edit', follow_redirects=True)
    assert b'Login' in response.data
