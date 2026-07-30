"""
Indexing Service Module
Handles document chunking and vector database indexing.
Follows SOLID principles for maintainability and extensibility.
"""

import json
import os
from typing import Any, Dict, List

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from loguru import logger
from transformers import AutoTokenizer

from app.core.config import settings


class IChunker:
    """Interface for document chunking strategies (Interface Segregation Principle)."""

    def chunk(self, json_data: Dict[str, Any], source_path: str) -> List[Document]:
        """Convert document data into chunks as LangChain Documents."""
        raise NotImplementedError


class PageBasedChunker(IChunker):
    """
    Page-based chunking strategy: 1 Page = 1 Chunk.
    Single Responsibility: Only handles page-based chunking logic.
    """

    def __init__(self, model_name: str = None):
        model_name = model_name or settings.EMBEDDING_MODEL
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        logger.info("PageBasedChunker initialized (1 Page = 1 Chunk strategy)")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text for metadata."""
        return len(self.tokenizer.encode(text, add_special_tokens=False))

    def chunk(self, json_data: Dict[str, Any], source_path: str) -> List[Document]:
        """
        Convert JSON data into page-based chunks.

        Args:
            json_data: OCR output in JSON format
            source_path: Path to source JSON file

        Returns:
            List of LangChain Documents (one per page)
        """
        elements = json_data.get("elements", [])
        if not elements:
            logger.warning(f"No elements in {source_path}")
            return []

        original_filename = elements[0].get("original_filename", "unknown")

        # Group elements by page
        pages_content: Dict[int, List[str]] = {}
        pages_metadata: Dict[int, Dict[str, Any]] = {}

        # Sort by page and region order
        sorted_elements = sorted(elements, key=lambda x: (x["page"], x["region_order"]))

        for el in sorted_elements:
            page_num = el["page"]
            content = el["content"]

            # Initialize page data if not exists
            if page_num not in pages_content:
                pages_content[page_num] = []
                pages_metadata[page_num] = {
                    "source": source_path,
                    "filename": original_filename,
                    "page": page_num,
                    "image_paths": "",
                }

            # Add text content
            pages_content[page_num].append(content)

            # Track images
            if el["region_type"] == "image" and el.get("saved_link"):
                pages_metadata[page_num]["image_paths"] += el["saved_link"] + "\n"

        # Create Documents
        documents = []
        for page_num, content_list in pages_content.items():
            # Combine page content
            page_text = "\n\n".join(content_list)

            # Add context for better embedding
            contextualized_text = f"Tài liệu: {original_filename}\n" f"Trang: {page_num}\n" f"Nội dung:\n{page_text}"

            # Update metadata
            meta = pages_metadata[page_num]
            meta["token_count"] = self.count_tokens(contextualized_text)

            doc = Document(page_content=contextualized_text, metadata=meta)
            documents.append(doc)

        logger.success(f"Created {len(documents)} chunks from {original_filename}")
        return documents


class IVectorStoreRepository:
    """Interface for vector store operations (Dependency Inversion Principle)."""

    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to vector store."""
        raise NotImplementedError

    def search(self, query: str, k: int) -> List[Document]:
        """Search for similar documents."""
        raise NotImplementedError


class ChromaVectorStore(IVectorStoreRepository):
    """
    Concrete implementation using ChromaDB.
    Single Responsibility: Only handles ChromaDB operations.
    """

    def __init__(
        self,
        collection_name: str = None,
        persist_directory: str = None,
        embedding_function: HuggingFaceEmbeddings = None,
    ):
        collection_name = collection_name or settings.COLLECTION_NAME
        persist_directory = persist_directory or str(settings.DB_PATH)

        if embedding_function is None:
            embedding_function = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)

        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embedding_function,
            persist_directory=persist_directory,
        )
        logger.info(f"ChromaVectorStore initialized: {persist_directory}/{collection_name}")

    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to ChromaDB in batches."""
        batch_size = settings.CHUNK_BATCH_SIZE
        total_batches = (len(documents) - 1) // batch_size + 1

        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]
            self.vector_store.add_documents(batch)
            logger.debug(f"Indexed batch {i // batch_size + 1}/{total_batches}")

        logger.success(f"Successfully indexed {len(documents)} documents")

    def search(self, query: str, k: int) -> List[Document]:
        """Search for similar documents."""
        retriever = self.vector_store.as_retriever(search_kwargs={"k": k})
        return retriever.invoke(query)

    def get_vector_store(self) -> Chroma:
        """Get underlying Chroma instance for advanced operations."""
        return self.vector_store


class IndexingService:
    """
    Main indexing service orchestrating the indexing pipeline.
    Follows Dependency Inversion: depends on abstractions (IChunker, IVectorStoreRepository).
    Open/Closed Principle: open for extension, closed for modification.
    """

    def __init__(self, chunker: IChunker, vector_store: IVectorStoreRepository):
        self.chunker = chunker
        self.vector_store = vector_store
        logger.info("IndexingService initialized")

    def index_from_json(self, json_path: str) -> Dict[str, Any]:
        """
        Index a document from its JSON output.

        Args:
            json_path: Path to OCR JSON output

        Returns:
            Dictionary with indexing results
        """
        logger.info(f"Starting indexing for: {json_path}")

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load JSON: {e}")
            raise

        # Chunk the document
        documents = self.chunker.chunk(json_data, source_path=json_path)

        if not documents:
            logger.warning("No documents created, skipping indexing")
            return {"chunks_indexed": 0, "json_path": json_path}

        # Index into vector store
        logger.info(f"Indexing {len(documents)} chunks...")
        self.vector_store.add_documents(documents)

        logger.success(f"Indexing completed for {json_path}")

        return {"chunks_indexed": len(documents), "json_path": json_path}

    def index_from_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Index all JSON files in a directory.

        Args:
            directory_path: Path to directory containing JSON files

        Returns:
            Dictionary with indexing results
        """
        logger.info(f"Indexing directory: {directory_path}")

        total_chunks = 0
        total_files = 0

        for root, _, files in os.walk(directory_path):
            for filename in files:
                if filename.endswith(".json"):
                    json_path = os.path.join(root, filename)
                    try:
                        result = self.index_from_json(json_path)
                        total_chunks += result["chunks_indexed"]
                        total_files += 1
                    except Exception as e:
                        logger.error(f"Failed to index {json_path}: {e}")

        logger.success(f"Indexed {total_files} files with {total_chunks} total chunks")

        return {"total_files": total_files, "total_chunks": total_chunks, "directory": directory_path}


def create_indexing_service(chunker: IChunker = None, vector_store: IVectorStoreRepository = None) -> IndexingService:
    """
    Factory function to create IndexingService with dependencies.
    Dependency Injection pattern.

    Args:
        chunker: Custom chunker implementation (optional)
        vector_store: Custom vector store implementation (optional)

    Returns:
        Configured IndexingService instance
    """
    if chunker is None:
        chunker = PageBasedChunker()

    if vector_store is None:
        vector_store = ChromaVectorStore()

    return IndexingService(chunker, vector_store)
