from database_connector import instance as db
import uuid

class SqlAgentLogDatabase:
    def __init__(self):
        self.connection = db.get_connection()
        self.cursor = db.get_cursor()
        
        self._create_table_if_not_exists()
        self._add_request_id_column_if_not_exists()

    def _create_table_if_not_exists(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS sql_agent_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            instruction TEXT,
            tool_name VARCHAR(255),
            tool_input TEXT,
            tool_output TEXT,
            step_order INT,
            execution_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
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
        AND table_name = 'sql_agent_log' 
        AND column_name = 'request_id'
        """
        self.cursor.execute(check_column_query)
        column_exists = self.cursor.fetchone()[0]
        
        if column_exists == 0:
            alter_table_query = """
            ALTER TABLE sql_agent_log 
            ADD COLUMN request_id VARCHAR(255) NULL
            """
            self.cursor.execute(alter_table_query)
            self.connection.commit()

    def save_intermediate_step(self, instruction: str, tool_name: str, tool_input: str, tool_output: str, step_order: int, request_id: str = None):
        """
        SQL Agent의 중간 단계 출력을 저장합니다.
        """
        insert_query = """
        INSERT INTO sql_agent_log (instruction, tool_name, tool_input, tool_output, step_order, request_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (instruction, tool_name, tool_input, tool_output, step_order, request_id)
        self.cursor.execute(insert_query, values)
        self.connection.commit()

    def get_logs_by_instruction(self, instruction: str):
        """
        특정 instruction에 대한 모든 로그를 가져옵니다.
        """
        select_query = """
        SELECT * FROM sql_agent_log 
        WHERE instruction = %s
        ORDER BY step_order ASC, created_at ASC
        """
        self.cursor.execute(select_query, (instruction,))
        return self.cursor.fetchall()

    def get_all_logs(self, limit: int = 100):
        """
        최근 로그들을 가져옵니다.
        """
        select_query = """
        SELECT * FROM sql_agent_log 
        ORDER BY created_at DESC
        LIMIT %s
        """
        self.cursor.execute(select_query, (limit,))
        return self.cursor.fetchall()
    
    def get_logs_paginated(self, page: int = 1, per_page: int = 10):
        """
        페이지네이션으로 로그를 가져옵니다.
        """
        offset = (page - 1) * per_page
        
        # 전체 카운트 조회
        count_query = "SELECT COUNT(*) FROM sql_agent_log"
        self.cursor.execute(count_query)
        total_count = self.cursor.fetchone()[0]
        
        # 페이지네이션된 데이터 조회
        select_query = """
        SELECT * FROM sql_agent_log 
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """
        self.cursor.execute(select_query, (per_page, offset))
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
    
    def get_latest_logs_by_instruction(self, instruction: str, execution_time_threshold: str = None):
        """
        특정 instruction에 대한 최신 실행 로그를 가져옵니다.
        가장 최근 request_id의 로그들을 반환합니다.
        """
        # 가장 최근 request_id를 찾습니다
        latest_request_query = """
        SELECT request_id FROM sql_agent_log 
        WHERE instruction = %s AND request_id IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 1
        """
        self.cursor.execute(latest_request_query, (instruction,))
        result = self.cursor.fetchone()
        
        if result:
            latest_request_id = result[0]
            select_query = """
            SELECT * FROM sql_agent_log 
            WHERE instruction = %s AND request_id = %s
            ORDER BY step_order ASC, created_at ASC
            """
            self.cursor.execute(select_query, (instruction, latest_request_id))
            return self.cursor.fetchall()
        else:
            return []
    
    def get_logs_by_request_id_paginated(self, page: int = 1, per_page: int = 1):
        """
        request_id로 그룹화하여 페이지네이션된 로그를 가져옵니다.
        한 페이지에는 하나의 request_id 그룹만 포함됩니다.
        """
        # 고유한 request_id 개수 조회 (NULL 제외)
        count_query = """
        SELECT COUNT(DISTINCT request_id) 
        FROM sql_agent_log 
        WHERE request_id IS NOT NULL
        """
        self.cursor.execute(count_query)
        total_count = self.cursor.fetchone()[0]
        
        # request_id를 최신 순으로 정렬하여 페이지네이션
        offset = (page - 1) * per_page
        request_id_query = """
        SELECT request_id 
        FROM sql_agent_log 
        WHERE request_id IS NOT NULL
        GROUP BY request_id
        ORDER BY MAX(created_at) DESC
        LIMIT %s OFFSET %s
        """
        self.cursor.execute(request_id_query, (per_page, offset))
        request_ids = self.cursor.fetchall()
        
        if not request_ids:
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
        logs_query = """
        SELECT * FROM sql_agent_log 
        WHERE request_id = %s
        ORDER BY step_order ASC, created_at ASC
        """
        self.cursor.execute(logs_query, (request_id,))
        logs = self.cursor.fetchall()
        
        total_pages = total_count
        
        return {
            "logs": logs,
            "request_id": request_id,
            "total_count": total_count,
            "current_page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }

    def get_logs_by_date_range(self, start_date: str, end_date: str):
        """
        날짜 범위로 로그를 가져옵니다.
        """
        select_query = """
        SELECT * FROM sql_agent_log 
        WHERE DATE(created_at) BETWEEN %s AND %s
        ORDER BY created_at DESC
        """
        self.cursor.execute(select_query, (start_date, end_date))
        return self.cursor.fetchall()

    def get_latest_logs_by_latest_request_id(self):
        """
        가장 최근의 created_at 값을 가진 request_id를 포함하는 모든 로그를 가져옵니다.
        """
        # 가장 최근 created_at을 가진 request_id를 찾습니다
        latest_request_query = """
        SELECT request_id FROM sql_agent_log 
        WHERE request_id IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 1
        """
        self.cursor.execute(latest_request_query)
        result = self.cursor.fetchone()
        
        if result:
            latest_request_id = result[0]
            select_query = """
            SELECT * FROM sql_agent_log 
            WHERE request_id = %s
            ORDER BY step_order ASC, created_at ASC
            """
            self.cursor.execute(select_query, (latest_request_id,))
            return self.cursor.fetchall()
        else:
            return []

    def __del__(self):
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'connection'):
            self.connection.close()
            
sql_agent_log_db = SqlAgentLogDatabase() 