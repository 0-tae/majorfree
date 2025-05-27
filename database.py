import mysql.connector
from mysql.connector import Error

try:
    connection = mysql.connector.connect(
        host='localhost',
        port=3306,
        database='cnu_data',
        user='root',
        password='dydrkfl#7!'
    )
    
    if connection.is_connected():
        db_info = connection.get_server_info()
        print(f"MySQL 서버에 연결되었습니다. 버전: {db_info}")
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print(f"현재 데이터베이스: {record[0]}")

except Error as e:
    print(f"MySQL 연결 중 에러 발생: {e}")