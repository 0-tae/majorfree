from databases.database_connector import instance as db
from models import Chat, ChatType
from typing import List

def get_chats_by_session_id(session_id: str) -> List[Chat]:
    try:
        """
        chat_session.session_id로 JOIN하여 해당 세션의 모든 Chat을 반환합니다.
        """
        connection = db.get_connection()
        cursor = connection.cursor()
        query = """
        SELECT chat.id, chat.created_at, chat.is_deleted, chat.modified_at, chat.chat_type, chat.content, chat.is_bot, chat.chat_session_id, chat.member_id
        FROM chat
        JOIN chat_session ON chat_session.id = chat.chat_session_id
        WHERE chat_session.session_id = %s
        ORDER BY chat.created_at ASC
        """
        cursor.execute(query, (session_id,))
        rows = cursor.fetchall()
        chats = []
        for row in rows:
            chats.append(Chat(
                id=row[0],
                created_at=row[1],
                is_deleted=bool(row[2]),
                modified_at=row[3],
                chat_type=ChatType(row[4]) if row[4] else None,
                content=row[5],
                is_bot=bool(row[6]),
                chat_session_id=row[7],
                member_id=row[8]
            ))
        return chats
    finally:
        cursor.close()
