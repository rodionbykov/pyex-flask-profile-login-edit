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
            # Create a test employee for authorization
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

def test_add_employee_page_loads(client):
    login(client)
    response = client.get('/employee/add')
    assert response.status_code == 200
    assert b'Add New Employee' in response.data

def test_add_employee_success(client):
    login(client)
    response = client.post('/employee/add', data={
        'employee_number': '67890',
        'first_name': 'Alice',
        'last_name': 'Wonderland',
        'birth_date': '1992-02-02',
        'gender': 'F'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Employee added successfully' in response.data
    
    # Verify in database
    with app.app_context():
        emp = db.session.get(Employee, '67890')
        assert emp is not None
        assert emp.first_name == 'Alice'
        assert emp.last_name == 'Wonderland'
        assert emp.gender == 'F'

def test_add_employee_unauthorized(client):
    # Try to access add page without login
    response = client.get('/employee/add', follow_redirects=True)
    assert b'Login' in response.data
