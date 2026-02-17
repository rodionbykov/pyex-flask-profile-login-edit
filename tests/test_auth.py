import pytest
from app import app, db, Employee

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
        with app.app_context():
            db.drop_all()

def test_login_page_loads(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Employee Number' in response.data

def test_login_success(client):
    # Create a test employee
    emp = Employee(employee_number='12345', first_name='John', last_name='Doe')
    db.session.add(emp)
    db.session.commit()

    response = client.post('/login', data={'employee_number': '12345'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'John Doe' in response.data

def test_login_failure(client):
    response = client.post('/login', data={'employee_number': '99999'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid employee number' in response.data
