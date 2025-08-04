import mysql.connector
import json,os

class DatabaseConnector:
    def __init__(self):
        
        # 현재 파일(chat_gpt.py 등)의 디렉토리 기준으로 경로 설정
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, 'database_config.json')

        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        db_config = config['database']

        self.connection = mysql.connector.connect(
            host=db_config.get('host', 'localhost'),
            port=db_config.get('port', 3306),
            database=db_config.get('name', ''),
            user=db_config.get('user', ''),
            password=db_config.get('password', '')
        )

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