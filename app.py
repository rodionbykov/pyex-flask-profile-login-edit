import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///employees.db')
# If you want to use PostgreSQL, set the DATABASE_URL environment variable, e.g.:
# DATABASE_URL=postgresql://postgres:postgres@localhost/postgres
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Employee(db.Model):
    __tablename__ = 'employees'
    employee_number = db.Column("emp_no", db.String(20), unique=True, nullable=False, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date)
    gender = db.Column(db.String(1))

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        employee_number = request.form.get('employee_number')
        employee = Employee.query.filter_by(employee_number=employee_number).first()
        if employee:
            session['employee_id'] = employee.employee_number
            return redirect(url_for('profile'))
        else:
            flash('Invalid employee number')
    return render_template('login.html')

@app.route('/profile')
def profile():
    employee_id = session.get('employee_id')
    if not employee_id:
        return redirect(url_for('login'))
    employee = Employee.query.get(employee_id)
    return render_template('profile.html', employee=employee)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)