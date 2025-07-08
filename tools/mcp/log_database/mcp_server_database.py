from log_database.database_connector import instance as db

class McpServerLogDatabase:
    def __init__(self):
        self.connection = db.get_connection()
        self.cursor = db.get_cursor()
        
        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS mcp_server (
            id INT AUTO_INCREMENT PRIMARY KEY,
            server_name VARCHAR(255),
            name VARCHAR(255),
            description TEXT,
            prompt TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
        self.cursor.execute(create_table_query)
        self.connection.commit()
        
    def save(self, server_name: str, name: str, description: str, prompt: str = "None"):
        insert_query = """
        INSERT INTO mcp_server (server_name, name, description, prompt)
        VALUES (%s, %s, %s, %s)
        """
        values = (server_name, name, description, prompt)
        self.cursor.execute(insert_query, values)
        self.connection.commit()
        
    def update(self, server_name: str, name: str, description: str, prompt: str = "None"):
        update_query = """
        UPDATE mcp_server
        SET description = %s, prompt = %s
        WHERE server_name = %s AND name = %s
        """
        values = (description, prompt, server_name, name)
        self.cursor.execute(update_query, values)
        self.connection.commit()
    
    def read(self, mcp_server: str):
        select_query = """
        SELECT * FROM mcp_server
        WHERE server_name = %s
        """
        self.cursor.execute(select_query, (mcp_server,))
        return self.cursor.fetchall()
    
    def get_all_servers(self):
        """
        모든 MCP 서버 정보를 가져옵니다.
        """
        select_query = """
        SELECT * FROM mcp_server
        ORDER BY created_at DESC
        """
        self.cursor.execute(select_query)
        return self.cursor.fetchall()
    
    def get_server_by_name(self, server_name: str, name: str):
        """
        특정 서버의 정보를 가져옵니다.
        """
        select_query = """
        SELECT * FROM mcp_server
        WHERE server_name = %s AND name = %s
        """
        self.cursor.execute(select_query, (server_name, name))
        return self.cursor.fetchone()
        
db = McpServerLogDatabase()
