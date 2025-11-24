from pydantic import BaseModel, Field
from typing import Optional, List
class IndexRequest(BaseModel):
    chunk_size: int = Field(
        default=500,
        ge=100,
        le=2000,
        description="The size of the chunks to index"
    )
    chunk_overlap: int = Field(
        default=50,
        ge=10,
        le=500,
        description="The overlap between chunks"
    )
    index_name:Optional[str] = Field(
        default="rag_index",
        description="The name of the index"
    )
    class Config:
        json_schema_extra = {
            "example":{
                "chunk_size": 500,
                "chunk_overlap": 50,
                "index_name": "rag_index"
            }
        }
class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="The query from user"
    )
    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="The number of results to return"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="The temperature of the model"
    )
    max_tokens: int = Field(
        default=1000,
        ge=50,
        le=2000,
        description="The maximum number of tokens to generate"
    )
    index_name:Optional[str] = Field(
        default="rag_index",
        description="The name of the index"
    )
    include_sources:bool = Field(
        default=True,
        description="Whether to include the sources in the response"
    )
    class Config:
        json_schema_extra = {
            "example":{
                "question": "What is the capital of France?",
                "top_k": 3,
                "temperature": 0.7,
                "max_tokens": 1000,
                "index_name": "rag_index",
                "include_sources": True
            }
        }
    
class Source(BaseModel):
    content: str = Field(
        description="The content of the source"
    )
    score: float = Field(
        description="The score of the source"
    )
    chunk_id: Optional[int] = Field(
        default=None,
        description="The chunk id of the source"
    )
    metadata: Optional[dict] = Field(
        default=None,
        description="The metadata of the source"
    )
    
class AskResponse(BaseModel):
    answer: str = Field(
        ...,
        description="The answer to the question"
    )
    sources: Optional[List[Source]] = Field(
        default=None,
        description="The sources of the answer"
    )

    class Config:
        json_schema_extra = {
            "example":{
                "answer": "What is the best way to learn Python?",
                "sources": [
                    {
                        "content": "Python is a great language for beginners",
                        "score": 0.95,
                        "chunk_id": "1234567890",
                        "metadata": {"source": "https://www.python.org", "page_number": 1}
                    }
                ]
            }
        }
    