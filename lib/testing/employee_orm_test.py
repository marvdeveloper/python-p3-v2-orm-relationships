from __init__ import CONN, CURSOR
from employee import Employee
from department import Department
import pytest


class TestEmployee:
    '''Class Employee in employee.py'''

    @pytest.fixture(autouse=True)
    def drop_tables(self):
        '''Drop tables prior to each test.'''
        CURSOR.execute("DROP TABLE IF EXISTS employees")
        CURSOR.execute("DROP TABLE IF EXISTS departments")
        CONN.commit()
        Department.all = {}
        Employee.all = {}

    def test_creates_table(self):
        '''Method "create_table()" creates table "employees" if it does not exist.'''
        Employee.create_table()
        CONN.commit()
        result = CURSOR.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'").fetchone()
        assert result is not None

    def test_drops_table(self):
        '''Method "drop_table()" drops table "employees" if it exists.'''
        sql = """
            CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            job_title TEXT,
            department_id INTEGER,
            FOREIGN KEY(department_id) REFERENCES departments(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

        Employee.drop_table()
        CONN.commit()

        sql_table_names = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='employees'
        """
        result = CURSOR.execute(sql_table_names).fetchone()
        assert result is None

    def test_saves_employee(self):
        '''Method "save()" saves an Employee instance to the DB and assigns the instance an id.'''
        Department.create_table()
        Employee.create_table()
        CONN.commit()

        department = Department.create("Payroll", "Building A, 5th Floor")

        employee = Employee("Raha", "Accountant", department.id)
        employee.save()

        sql = "SELECT * FROM employees"
        row = CURSOR.execute(sql).fetchone()

        assert (row[0], row[1], row[2], row[3]) == (employee.id, employee.name, employee.job_title, employee.department_id)

    def test_creates_employee(self):
        '''Method "create()" creates a new row and returns an Employee instance.'''
        Department.create_table()
        Employee.create_table()
        CONN.commit()

        department = Department.create("Payroll", "Building A, 5th Floor")
        employee = Employee.create("Raha", "Accountant", department.id)

        sql = "SELECT * FROM employees"
        row = CURSOR.execute(sql).fetchone()

        assert (row[0], row[1], row[2], row[3]) == (employee.id, employee.name, employee.job_title, employee.department_id)

    def test_updates_row(self):
        '''Method "update()" updates the DB row to match instance attribute values.'''
        Department.create_table()
        Employee.create_table()
        CONN.commit()

        department1 = Department.create("Human Resources", "Building C, East Wing")
        department2 = Department.create("Marketing", "Building B, 3rd Floor")

        employee1 = Employee.create("Raha", "Accountant", department1.id)
        id1 = employee1.id
        employee2 = Employee.create("Tal", "Senior Accountant", department2.id)
        id2 = employee2.id

        employee2.name = "Talisha"
        employee2.job_title = "Lead Accountant"
        employee2.department_id = department1.id
        employee2.update()

        employee = Employee.find_by_id(id1)
        assert (employee.id, employee.name, employee.job_title, employee.department_id) == (id1, "Raha", "Accountant", department1.id)

        employee = Employee.find_by_id(id2)
        assert (employee.id, employee.name, employee.job_title, employee.department_id) == (id2, "Talisha", "Lead Accountant", department1.id)

    def test_deletes_row(self):
        '''Method "delete()" deletes the instance's corresponding DB row.'''
        Department.create_table()
        Employee.create_table()
        CONN.commit()

        department1 = Department.create("Human Resources", "Building C, East Wing")
        department2 = Department.create("Marketing", "Building B, 3rd Floor")

        employee1 = Employee.create("Raha", "Accountant", department1.id)
        id1 = employee1.id
        employee2 = Employee.create("Tal", "Senior Accountant", department2.id)
        id2 = employee2.id

        employee2.delete()

        employee = Employee.find_by_id(id1)
        assert (employee.id, employee.name, employee.job_title, employee.department_id) == (id1, "Raha", "Accountant", department1.id)

        assert Employee.find_by_id(id2) is None
        assert (employee2.id, employee2.name, employee2.job_title, employee2.department_id) == (None, "Tal", "Senior Accountant", department2.id)
        assert Employee.all.get(id2) is None

    def test_instance_from_db(self):
        '''Method "instance_from_db()" takes a table row and returns an Employee instance.'''
        Department.create_table()
        Employee.create_table()
        CONN.commit()

        department = Department.create("Payroll", "Building A, 5th Floor")
        Employee.create("Raha", "Accountant", department.id)

        sql = "SELECT * FROM employees"
        row = CURSOR.execute(sql).fetchone()

        employee = Employee.instance_from_db(row)
        assert (row[0], row[1], row[2], row[3]) == (employee.id, employee.name, employee.job_title, employee.department_id)

    def test_gets_all(self):
        '''Method "get_all()" returns a list of Employee instances for every row in the DB.'''
        Department.create_table()
        Employee.create_table()
        CONN.commit()

        department1 = Department.create("Human Resources", "Building C, East Wing")
        department2 = Department.create("Marketing", "Building B, 3rd Floor")

        employee1 = Employee.create("Raha", "Accountant", department1.id)
        employee2 = Employee.create("Tal", "Senior Accountant", department2.id)

        employees = Employee.get_all()
        assert len(employees) == 2

        assert (employees[0].id, employees[0].name, employees[0].job_title, employees[0].department_id) == (employee1.id, employee1.name, employee1.job_title, employee1.department_id)
        assert (employees[1].id, employees[1].name, employees[1].job_title, employees[1].department_id) == (employee2.id, employee2.name, employee2.job_title, employee2.department_id)

    def test_finds_by_id(self):
        '''Method "find_by_id()" returns Employee instance by id.'''
        Department.create_table()
        Employee.create_table()
        CONN.commit()

        department1 = Department.create("Human Resources", "Building C, East Wing")
        department2 = Department.create("Marketing", "Building B, 3rd Floor")

        employee1 = Employee.create("Raha", "Accountant", department1.id)
        employee2 = Employee.create("Tal", "Senior Accountant", department2.id)

        employee = Employee.find_by_id(employee1.id)
        assert (employee.id, employee.name, employee.job_title, employee.department_id) == (employee1.id, employee1.name, employee1.job_title, employee1.department_id)

        employee = Employee.find_by_id(employee2.id)
        assert (employee.id, employee.name, employee.job_title, employee.department_id) == (employee2.id, employee2.name, employee2.job_title, employee2.department_id)

        employee = Employee.find_by_id(0)
        assert employee is None
