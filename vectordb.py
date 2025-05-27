import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any

class ChromaDB:
    """
    ChromaDB를 사용하여 벡터 데이터베이스를 관리하는 클래스입니다.
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        ChromaDB 클라이언트를 초기화합니다.
        
        Args:
            persist_directory (str): 데이터를 저장할 디렉토리 경로
        """
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            is_persistent=True
        ))
        
    def query(self, collection_name: str, query_texts: List[str], n_results: int = 5) -> List[Dict[str, Any]]:
        """
        벡터 데이터베이스에서 유사한 문서를 검색합니다.
        
        Args:
            collection_name (str): 검색할 컬렉션 이름
            query_texts (List[str]): 검색할 텍스트 목록
            n_results (int): 반환할 결과 개수 (기본값: 5)
            
        Returns:
            List[Dict[str, Any]]: 검색 결과 목록
        """
        try:
            collection = self.client.get_collection(collection_name)
            results = collection.query(
                query_texts=query_texts,
                n_results=n_results
            )
            return results
        except Exception as e:
            raise Exception(f"ChromaDB 검색 중 오류 발생: {str(e)}")
