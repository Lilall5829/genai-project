import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
class DocumentProcessor:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len, separators=["\n\n", "\n", " ", ""])

    def load_pdf(self, file_path: str) -> List[Document]:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        return documents
    def load_text(self, file_path: str) -> List[Document]:
        loader = TextLoader(file_path)
        documents = loader.load()
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        return self.text_splitter.split_documents(documents)

    def process_pdf(self, file_path: str) -> List[Document]:
        documents = self.load_pdf(file_path)
        return self.split_documents(documents)
    def process_text(self, file_path: str) -> List[Document]:
        documents = self.load_text(file_path)
        return self.split_documents(documents)

    def process_file(self, file_path: str) -> List[Document]:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        if ext == '.pdf':
            return self.process_pdf(file_path)
        elif ext in ['.txt', '.md']:
            return self.process_text(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

        