from database.department_database import DepartmentsDatabase

class Departments:
    def __init__(self):
        db = DepartmentsDatabase()
        self._colleges = db.readCollegesAll()
        self._departments = db.readDepartmentsAll()
        self._college_department_pairs = db.readAll()

    @property
    def colleges(self):
        return self._colleges

    @property
    def departments(self):
        return self._departments

    @property
    def college_department_pairs(self):
        return self._college_department_pairs