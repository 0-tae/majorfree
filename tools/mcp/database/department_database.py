from database.database_connector import instance as db

class DepartmentsDatabase:
    def __init__(self):
        self.connection = db.get_connection()
        self.cursor = db.get_cursor()
        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS departments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            college VARCHAR(255),
            department VARCHAR(255)
        )
        """
        self.cursor.execute(create_table_query)
        self.connection.commit()

    def readAll(self):
        """
        departments 테이블의 모든 row를 college, department로 이루어진 딕셔너리 리스트로 반환합니다.
        """
        select_query = "SELECT college, department FROM departments"
        self.cursor.execute(select_query)
        rows = self.cursor.fetchall()
        return [{"college": row[0], "department": row[1]} for row in rows]

    def readCollegesAll(self):
        """
        departments 테이블에서 distinct college 목록만 리스트로 반환합니다.
        """
        select_query = "SELECT DISTINCT college FROM departments"
        self.cursor.execute(select_query)
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]

    def readDepartmentsAll(self):
        """
        departments 테이블에서 distinct department 목록만 리스트로 반환합니다.
        """
        select_query = "SELECT DISTINCT department FROM departments"
        self.cursor.execute(select_query)
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]

    # 추후 readAll, readCollegesAll, readDepartmentsAll 메서드 추가 예정 