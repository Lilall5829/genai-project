from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
    self.chunk_size = chunk_size
    self.chunk_overlap = chunk_overlap
    self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len, separatorstors=["\n\n", "\n", " ", ""])

def load_pdf(self, file_path: str) -> List[Document]:

def split_documents(self, documents: List[Document]) -> List[Document]:

def process_pdf(self, file_path: str) -> List[Document]: