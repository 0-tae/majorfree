import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

class ChromaDB:
    def __init__(self, collection_name:str = "interview_data"):
        self.__client = chromadb.PersistentClient(path="./chroma")
        self.__collection = self.__client.get_or_create_collection(name = collection_name)
        self.__embedding_model = SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS")


    def __get_embeddings(self, input_str: str):
        return self.__embedding_model.encode(input_str)

    def query(self, input: str, filter:list = [], n_results:int = 10):
        doc_embeddings = self.__get_embeddings(input)
        
        query_result = self.__collection.query(
                query_embeddings=doc_embeddings,
                where={"학과명": {"$in": filter}},
                n_results=n_results
        )
        print("ids: ", query_result['ids'][0])
        return query_result['ids'][0],query_result["documents"][0]


db_instance = ChromaDB(collection_name="interview_data")