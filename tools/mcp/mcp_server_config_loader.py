def get_server_config_from_db(server_name: str, default_name: str = None, default_description: str = None):
    """
    데이터베이스에서 MCP 서버 설정을 가져옵니다.
    데이터베이스에 정보가 없으면 기본값을 반환합니다.
    """
    
    return {
        "name": default_name or server_name,
        "description": default_description or f"{server_name} MCP Server",
        "prompt": None
    }