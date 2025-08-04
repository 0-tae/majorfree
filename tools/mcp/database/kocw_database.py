from database.database_connector import instance

ALLOWED_TABLES = {
    # "kocw_lecture_engineering",
    # "kocw_lecture_education",
    # "kocw_lecture_humanities",
    # "kocw_lecture_natural_science",
    "kocw_lecture"
}

def get_department_list(table_name: str) -> list:
    """
    주어진 테이블에서 department 목록을 조회합니다.
    :param table_name: 조회할 테이블명
    :return: department 목록(list)
    :raises ValueError: 허용되지 않은 테이블명일 경우
    """
    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"허용되지 않은 테이블명입니다: {table_name}")

    query = f"SELECT DISTINCT department FROM {table_name}"
    cursor = instance.get_cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        department_list = [row[0] for row in result]
        return department_list
    except Exception as e:
        raise RuntimeError(f"department 목록 조회 중 오류 발생: {e}")

