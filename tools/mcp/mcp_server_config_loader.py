from database.mcp_server_database import db as mcp_server_db

def get_server_config_from_db(server_name: str, default_name: str = None, default_description: str = None):
    """
    데이터베이스에서 MCP 서버 설정을 가져옵니다.
    데이터베이스에 정보가 없으면 기본값을 반환합니다.
    """
    try:
        # 데이터베이스에서 서버 정보 조회
        db_server = mcp_server_db.get_server_by_name(server_name, default_name or server_name)
        
        if db_server:
            return {
                "name": db_server[2],  # name
                "description": db_server[3],  # description
                "prompt": db_server[4] if db_server[4] != "None" else None  # prompt
            }
        else:
            return {
                "name": default_name or server_name,
                "description": default_description or f"{server_name} MCP Server",
                "prompt": None
            }
    except Exception as e:
        print(f"데이터베이스에서 서버 설정 로드 실패: {e}")
        return {
            "name": default_name or server_name,
            "description": default_description or f"{server_name} MCP Server",
            "prompt": None
        } 