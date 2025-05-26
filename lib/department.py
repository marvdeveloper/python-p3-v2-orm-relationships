import time
import sqlite3
from lib import CURSOR, CONN

class Department:
    all = {}

    def __init__(self, name, location, id=None):
        self.id = id
        self.name = name
        self.location = location

    def __repr__(self):
        return f"<Department {self.id}: {self.name}, {self.location}>"

    @classmethod
    def _execute_with_retry(cls, sql, params=(), commit=False, fetchone=False, fetchall=False):
        retries = 5
        for attempt in range(retries):
            cursor = None
            try:
                cursor = CONN.cursor()
                cursor.execute(sql, params)
                if commit:
                    CONN.commit()
                if fetchone:
                    result = cursor.fetchone()
                elif fetchall:
                    result = cursor.fetchall()
                else:
                    result = cursor.lastrowid
                return result
            except sqlite3.OperationalError as e:
                if 'database is locked' in str(e):
                    time.sleep(0.1)  # wait 100ms before retrying
                else:
                    raise
            finally:
                if cursor:
                    cursor.close()
        raise sqlite3.OperationalError("database is locked after several retries")

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY,
                name TEXT,
                location TEXT
            )
        """
        cls._execute_with_retry(sql, commit=True)

    @classmethod
    def drop_table(cls):
        sql = "DROP TABLE IF EXISTS departments;"
        cls._execute_with_retry(sql, commit=True)

    def save(self):
        sql = """
            INSERT INTO departments (name, location)
            VALUES (?, ?)
        """
        self.id = self._execute_with_retry(sql, (self.name, self.location), commit=True)
        type(self).all[self.id] = self

    def update(self):
        sql = """
            UPDATE departments
            SET name = ?, location = ?
            WHERE id = ?
        """
        self._execute_with_retry(sql, (self.name, self.location, self.id), commit=True)

    def delete(self):
        sql = "DELETE FROM departments WHERE id = ?"
        self._execute_with_retry(sql, (self.id,), commit=True)
        if self.id in type(self).all:
            del type(self).all[self.id]
        self.id = None

    @classmethod
    def create(cls, name, location):
        department = cls(name, location)
        department.save()
        return department

    @classmethod
    def instance_from_db(cls, row):
        department = cls.all.get(row[0])
        if department:
            department.name = row[1]
            department.location = row[2]
        else:
            department = cls(row[1], row[2], id=row[0])
            cls.all[department.id] = department
        return department

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM departments"
        rows = cls._execute_with_retry(sql, fetchall=True)
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        sql = "SELECT * FROM departments WHERE id = ?"
        row = cls._execute_with_retry(sql, (id,), fetchone=True)
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        sql = "SELECT * FROM departments WHERE name = ?"
        row = cls._execute_with_retry(sql, (name,), fetchone=True)
        return cls.instance_from_db(row) if row else None

    # Lazy import to avoid circular dependencies
    def employees(self):
        from lib.employee import Employee
        all_employees = Employee.get_all()
        return [emp for emp in all_employees if emp.department_id == self.id]
