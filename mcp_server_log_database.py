from database_connector import instance as db
import uuid

class McpServerLogDatabase:
    def __init__(self):
        self.connection = db.get_connection()
        self.cursor = db.get_cursor()
        
        self._create_table_if_not_exists()
        self._add_request_id_column_if_not_exists()

    def _create_table_if_not_exists(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS mcp_answer_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            mcp_server VARCHAR(255),
            name VARCHAR(255),
            description TEXT,
            instruction TEXT,
            prompt TEXT,
            answer TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            request_id VARCHAR(255) NULL
        )
        """
        self.cursor.execute(create_table_query)
        self.connection.commit()
    
    def _add_request_id_column_if_not_exists(self):
        """기존 테이블에 request_id 컬럼이 없으면 추가합니다."""
        check_column_query = """
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE table_schema = DATABASE() 
        AND table_name = 'mcp_answer_log' 
        AND column_name = 'request_id'
        """
        self.cursor.execute(check_column_query)
        column_exists = self.cursor.fetchone()[0]
        
        if column_exists == 0:
            alter_table_query = """
            ALTER TABLE mcp_answer_log 
            ADD COLUMN request_id VARCHAR(255) NULL
            """
            self.cursor.execute(alter_table_query)
            self.connection.commit()

    def save(self, mcp_server: str, name: str, description: str, instruction: str, prompt: str, answer, request_id: str = None):
        insert_query = """
        INSERT INTO mcp_answer_log (mcp_server, name, description, instruction, prompt, answer, request_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (mcp_server, name, description, instruction, prompt, answer, request_id)
        self.cursor.execute(insert_query, values)
        self.connection.commit()
        
        # 방금 저장된 로그의 ID를 반환
        return self.cursor.lastrowid

    def get_logs_by_mcp_server(self, mcp_server: str):
        select_query = """
        SELECT * FROM mcp_answer_log 
        WHERE mcp_server = %s
        ORDER BY created_at DESC
        """
        self.cursor.execute(select_query, (mcp_server,))
        return self.cursor.fetchall()

    def get_all_logs(self, limit: int = 100):
        """
        모든 MCP 서버 로그를 가져옵니다.
        """
        select_query = """
        SELECT * FROM mcp_answer_log 
        ORDER BY created_at DESC
        LIMIT %s
        """
        self.cursor.execute(select_query, (limit,))
        return self.cursor.fetchall()
    
    def get_logs_paginated(self, page: int = 1, per_page: int = 10, server_name: str = None):
        """
        페이지네이션으로 로그를 가져옵니다.
        """
        offset = (page - 1) * per_page
        
        # 조건절 구성
        where_clause = ""
        params = []
        if server_name:
            where_clause = "WHERE mcp_server = %s"
            params.append(server_name)
        
        # 전체 카운트 조회
        count_query = f"SELECT COUNT(*) FROM mcp_answer_log {where_clause}"
        self.cursor.execute(count_query, params)
        total_count = self.cursor.fetchone()[0]
        
        # 페이지네이션된 데이터 조회
        select_query = f"""
        SELECT * FROM mcp_answer_log 
        {where_clause}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """
        params.extend([per_page, offset])
        self.cursor.execute(select_query, params)
        logs = self.cursor.fetchall()
        
        total_pages = (total_count + per_page - 1) // per_page
        
        return {
            "logs": logs,
            "total_count": total_count,
            "current_page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    
    def get_latest_logs_by_instruction(self, instruction: str, server_name: str = None):
        """
        특정 instruction에 대한 최신 실행 로그를 가져옵니다.
        가장 최근 request_id의 로그들을 반환합니다.
        """
        where_clause = "WHERE instruction = %s"
        params = [instruction]
        
        if server_name:
            where_clause += " AND mcp_server = %s"
            params.append(server_name)
        
        # 가장 최근 request_id를 찾습니다
        latest_request_query = f"""
        SELECT request_id FROM mcp_answer_log 
        {where_clause} AND request_id IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 1
        """
        self.cursor.execute(latest_request_query, params)
        result = self.cursor.fetchone()
        
        if result:
            latest_request_id = result[0]
            select_query = f"""
            SELECT * FROM mcp_answer_log 
            {where_clause} AND request_id = %s
            ORDER BY created_at DESC
            """
            params.append(latest_request_id)
            self.cursor.execute(select_query, params)
            return self.cursor.fetchall()
        else:
            return []
    
    def get_logs_by_request_id(self, request_id: str):
        """
        특정 request_id에 해당하는 모든 로그를 가져옵니다.
        """
        select_query = """
        SELECT * FROM mcp_answer_log 
        WHERE request_id = %s
        ORDER BY created_at DESC
        """
        self.cursor.execute(select_query, (request_id,))
        return self.cursor.fetchall()
    
    def get_logs_by_request_id_paginated(self, page: int = 1, per_page: int = 1, server_name: str = None):
        """
        request_id로 그룹화하여 페이지네이션된 로그를 가져옵니다.
        한 페이지에는 하나의 request_id 그룹만 포함됩니다.
        """
        print(f"🔍 MCP DB get_logs_by_request_id_paginated called: page={page}, per_page={per_page}, server_name={server_name}")
        
        # 조건절 구성
        where_clause = "WHERE request_id IS NOT NULL"
        params = []
        if server_name:
            where_clause += " AND mcp_server = %s"
            params.append(server_name)
        
        print(f"🔍 Where clause: {where_clause}, params: {params}")
        
        # 고유한 request_id 개수 조회
        count_query = f"""
        SELECT COUNT(DISTINCT request_id) 
        FROM mcp_answer_log 
        {where_clause}
        """
        print(f"🔍 Count query: {count_query}")
        self.cursor.execute(count_query, params)
        total_count = self.cursor.fetchone()[0]
        print(f"🔍 Total count: {total_count}")
        
        # request_id를 최신 순으로 정렬하여 페이지네이션
        offset = (page - 1) * per_page
        request_id_query = f"""
        SELECT request_id 
        FROM mcp_answer_log 
        {where_clause}
        GROUP BY request_id
        ORDER BY MAX(created_at) DESC
        LIMIT %s OFFSET %s
        """
        params.extend([per_page, offset])
        print(f"🔍 Request ID query: {request_id_query}, params: {params}")
        self.cursor.execute(request_id_query, params)
        request_ids = self.cursor.fetchall()
        print(f"🔍 Request IDs found: {request_ids}")
        
        if not request_ids:
            print("🔍 No request_ids found, returning empty result")
            return {
                "logs": [],
                "total_count": total_count,
                "current_page": page,
                "per_page": per_page,
                "total_pages": 0,
                "has_next": False,
                "has_prev": False
            }
        
        # 해당 request_id의 모든 로그 조회
        request_id = request_ids[0][0]  # 첫 번째 request_id만 (per_page가 1이므로)
        print(f"🔍 Selected request_id: {request_id}")
        logs_query = """
        SELECT * FROM mcp_answer_log 
        WHERE request_id = %s
        ORDER BY created_at DESC
        """
        self.cursor.execute(logs_query, (request_id,))
        logs = self.cursor.fetchall()
        print(f"🔍 Logs for request_id {request_id}: {len(logs)} logs found")
        
        total_pages = total_count
        
        result = {
            "logs": logs,
            "request_id": request_id,
            "total_count": total_count,
            "current_page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
        print(f"🔍 Final result: {result}")
        return result

    def get_logs_by_date_range(self, start_date: str, end_date: str):
        """
        날짜 범위로 로그를 가져옵니다.
        """
        select_query = """
        SELECT * FROM mcp_answer_log 
        WHERE DATE(created_at) BETWEEN %s AND %s
        ORDER BY created_at DESC
        """
        self.cursor.execute(select_query, (start_date, end_date))
        return self.cursor.fetchall()

    def __del__(self):
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'connection'):
            self.connection.close()
            
db = McpServerLogDatabase()
