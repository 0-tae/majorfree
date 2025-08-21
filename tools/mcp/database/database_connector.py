import mysql.connector
import json,os

class DatabaseConnector:
    def __init__(self):
        with open("database/database_config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        db_config = config['database']

        self.connection = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
        self.cursor = self.connection.cursor()

    def get_connection(self):
        """
        MySQL 연결 객체를 반환합니다.
        """
        return self.connection

    def get_cursor(self):
        """
        MySQL 커서 객체를 반환합니다.
        """
        return self.cursor

    def __del__(self):
        """
        소멸자에서 연결과 커서를 정리합니다.
        """
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'connection'):
            self.connection.close()

instance = DatabaseConnector()