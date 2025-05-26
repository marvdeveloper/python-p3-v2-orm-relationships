from __init__ import CONN, CURSOR
from department import Department
import pytest


class TestDepartment:
    '''Class Department in department.py'''

    @pytest.fixture(autouse=True)
    def drop_tables(self):
        '''Drop tables prior to each test.'''
        CURSOR.execute("DROP TABLE IF EXISTS employees")
        CURSOR.execute("DROP TABLE IF EXISTS departments")
        CONN.commit()
        Department.all = {}

    def test_creates_table(self):
        '''Method "create_table()" creates table "departments" if it does not exist.'''
        Department.create_table()
        # Commit to ensure table is created before select
        CONN.commit()
        result = CURSOR.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='departments'").fetchone()
        assert result is not None

    def test_drops_table(self):
        '''Method "drop_table()" drops table "departments" if it exists.'''
        sql = """
            CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY,
            name TEXT,
            location TEXT)
        """
        CURSOR.execute(sql)
        CONN.commit()

        Department.drop_table()
        CONN.commit()

        sql_table_names = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='departments'
        """
        result = CURSOR.execute(sql_table_names).fetchone()
        assert result is None

    def test_saves_department(self):
        '''Method "save()" saves a Department instance to the DB and assigns the instance an id.'''
        Department.create_table()
        CONN.commit()
        department = Department("Payroll", "Building A, 5th Floor")
        department.save()

        sql = "SELECT * FROM departments"
        row = CURSOR.execute(sql).fetchone()
        assert (row[0], row[1], row[2]) == (department.id, department.name, department.location) == (row[0], "Payroll", "Building A, 5th Floor")

    def test_creates_department(self):
        '''Method "create()" creates a new row and returns a Department instance.'''
        Department.create_table()
        CONN.commit()
        department = Department.create("Payroll", "Building A, 5th Floor")

        sql = "SELECT * FROM departments"
        row = CURSOR.execute(sql).fetchone()
        assert (row[0], row[1], row[2]) == (department.id, department.name, department.location) == (row[0], "Payroll", "Building A, 5th Floor")

    def test_updates_row(self):
        '''Method "update()" updates the DB row to match instance attribute values.'''
        Department.create_table()
        CONN.commit()

        department1 = Department.create("Human Resources", "Building C, East Wing")
        id1 = department1.id
        department2 = Department.create("Marketing", "Building B, 3rd Floor")
        id2 = department2.id

        department2.name = "Sales and Marketing"
        department2.location = "Building B, 4th Floor"
        department2.update()

        department = Department.find_by_id(id1)
        assert (department.id, department.name, department.location) == (id1, "Human Resources", "Building C, East Wing") == (department1.id, department1.name, department1.location)

        department = Department.find_by_id(id2)
        assert (department.id, department.name, department.location) == (id2, "Sales and Marketing", "Building B, 4th Floor") == (department2.id, department2.name, department2.location)

    def test_deletes_row(self):
        '''Method "delete()" deletes the instance's corresponding DB row.'''
        Department.create_table()
        CONN.commit()

        department1 = Department.create("Human Resources", "Building C, East Wing")
        id1 = department1.id
        department2 = Department.create("Sales and Marketing", "Building B, 4th Floor")
        id2 = department2.id

        department2.delete()

        department = Department.find_by_id(id1)
        assert (department.id, department.name, department.location) == (id1, "Human Resources", "Building C, East Wing") == (department1.id, department1.name, department1.location)

        assert Department.find_by_id(id2) is None
        assert (department2.id, department2.name, department2.location) == (None, "Sales and Marketing", "Building B, 4th Floor")
        assert Department.all.get(id2) is None

    def test_instance_from_db(self):
        '''Method "instance_from_db()" takes a table row and returns a Department instance.'''
        Department.create_table()
        CONN.commit()

        Department.create("Payroll", "Building A, 5th Floor")

        sql = "SELECT * FROM departments"
        row = CURSOR.execute(sql).fetchone()
        department = Department.instance_from_db(row)

        assert (row[0], row[1], row[2]) == (department.id, department.name, department.location) == (row[0], "Payroll", "Building A, 5th Floor")

    def test_gets_all(self):
        '''Method "get_all()" returns a list of Department instances for every row in the DB.'''
        Department.create_table()
        CONN.commit()

        department1 = Department.create("Human Resources", "Building C, East Wing")
        department2 = Department.create("Marketing", "Building B, 3rd Floor")

        departments = Department.get_all()

        assert len(departments) == 2
        assert (departments[0].id, departments[0].name, departments[0].location) == (department1.id, "Human Resources", "Building C, East Wing")
        assert (departments[1].id, departments[1].name, departments[1].location) == (department2.id, "Marketing", "Building B, 3rd Floor")

    def test_finds_by_id(self):
        '''Method "find_by_id()" returns Department instance by id.'''
        Department.create_table()
        CONN.commit()

        department1 = Department.create("Human Resources", "Building C, East Wing")
        department2 = Department.create("Marketing", "Building B, 3rd Floor")

        department = Department.find_by_id(department1.id)
        assert (department.id, department.name, department.location) == (department1.id, "Human Resources", "Building C, East Wing")

        department = Department.find_by_id(department2.id)
        assert (department.id, department.name, department.location) == (department2.id, "Marketing", "Building B, 3rd Floor")

        department = Department.find_by_id(0)
        assert department is None

    def test_finds_by_name(self):
        '''Method "find_by_name()" returns Department instance by name.'''
        Department.create_table()
        CONN.commit()

        department1 = Department.create("Human Resources", "Building C, East Wing")
        department2 = Department.create("Marketing", "Building B, 3rd Floor")

        department = Department.find_by_name("Human Resources")
        assert (department.id, department.name, department.location) == (department1.id, "Human Resources", "Building C, East Wing")

        department = Department.find_by_name("Marketing")
        assert (department.id, department.name, department.location) == (department2.id, "Marketing", "Building B, 3rd Floor")

        department = Department.find_by_name("Unknown")
        assert department is None

    def test_get_employees(self):
        '''Method "employees()" gets employees for the current Department instance.'''
        from employee import Employee  # avoid circular import
        Employee.all = {}

        Department.create_table()
        CONN.commit()

        department1 = Department.create("Payroll", "Building A, 5th Floor")
        department2 = Department.create("Human Resources", "Building C, 2nd Floor")

        Employee.create_table()
        CONN.commit()

        employee1 = Employee.create("Raha", "Accountant", department1.id)
        employee2 = Employee.create("Tal", "Senior Accountant", department1.id)
        employee3 = Employee.create("Amir", "Manager", department2.id)

        employees = department1.employees()
        assert len(employees) == 2

        assert (employees[0].id, employees[0].name, employees[0].job_title, employees[0].department_id) == (employee1.id, employee1.name, employee1.job_title, employee1.department_id)
        assert (employees[1].id, employees[1].name, employees[1].job_title, employees[1].department_id) == (employee2.id, employee2.name, employee2.job_title, employee2.department_id)
