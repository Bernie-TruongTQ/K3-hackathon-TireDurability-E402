"""Document chunking and retrieval storage for VLearn VisualRAG.

The default local store keeps the prototype runnable on a laptop. Chroma remains
available as an optional adapter for the full semantic-retrieval configuration.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Protocol

from app.core.config import settings

logger = logging.getLogger(__name__)


WORD_RE = re.compile(r"\w+", re.UNICODE)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
VISUAL_TYPES = {"image", "figure", "chart", "table", "formula"}
STOPWORDS = {
    "ai",
    "bài",
    "bạn",
    "cái",
    "cho",
    "có",
    "của",
    "giúp",
    "gì",
    "hãy",
    "không",
    "là",
    "mình",
    "một",
    "nào",
    "này",
    "những",
    "nội",
    "phần",
    "trong",
    "trên",
    "tài",
    "và",
    "về",
}


@dataclass
class Document:
    page_content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    score: Optional[float] = None


class IChunker(Protocol):
    def chunk(self, json_data: Dict[str, Any], source_path: str) -> List[Document]: ...


class IVectorStoreRepository(Protocol):
    def add_documents(self, documents: List[Document]) -> None: ...

    def search(self, query: str, k: int, document_id: str | None = None) -> List[Document]: ...


def _tokenize(text: str) -> List[str]:
    return [
        token.lower()
        for token in WORD_RE.findall(text)
        if token.lower() not in STOPWORDS and len(token) > 1
    ]


def _stable_id(*parts: object) -> str:
    payload = "|".join(str(part) for part in parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]


class HierarchicalMarkdownChunker:
    """Heading-aware chunker that preserves page, region and visual metadata."""

    def __init__(self, max_tokens: int | None = None):
        self.max_tokens = max_tokens or settings.MAX_CHUNK_TOKENS

    @staticmethod
    def count_tokens(text: str) -> int:
        # Stable offline approximation. The embedding tokenizer may be used by
        # the Chroma adapter, but chunk boundaries must not require a download.
        return len(_tokenize(text))

    def _split_to_limit(self, text: str) -> Iterable[str]:
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
        if not paragraphs:
            return
        buffer: List[str] = []
        size = 0
        for paragraph in paragraphs:
            paragraph_tokens = self.count_tokens(paragraph)
            if paragraph_tokens > self.max_tokens:
                words = paragraph.split()
                if buffer:
                    yield "\n\n".join(buffer)
                    buffer, size = [], 0
                for start in range(0, len(words), self.max_tokens):
                    yield " ".join(words[start : start + self.max_tokens])
                continue
            if buffer and size + paragraph_tokens > self.max_tokens:
                yield "\n\n".join(buffer)
                buffer, size = [], 0
            buffer.append(paragraph)
            size += paragraph_tokens
        if buffer:
            yield "\n\n".join(buffer)

    def chunk(self, json_data: Dict[str, Any], source_path: str) -> List[Document]:
        elements = sorted(
            json_data.get("elements", []),
            key=lambda item: (int(item.get("page", 0)), int(item.get("region_order", 0))),
        )
        if not elements:
            return []

        original_filename = elements[0].get("original_filename") or Path(source_path).stem
        document_id = (
            json_data.get("document_id")
            or elements[0].get("file_name")
            or _stable_id(original_filename, source_path)
        )
        header_stack: List[str] = []
        documents: List[Document] = []

        for element in elements:
            page = int(element.get("page", 0))
            region_order = int(element.get("region_order", 0))
            region_type = str(element.get("region_type", "text")).lower()
            raw_content = str(element.get("content", "")).strip()
            image_path = element.get("saved_link")
            coordinates = element.get("metadata", {}).get("coordinates", [])

            if region_type in VISUAL_TYPES or image_path:
                for line in raw_content.splitlines():
                    heading = HEADING_RE.match(line.strip())
                    if heading:
                        level = len(heading.group(1))
                        header_stack = header_stack[: level - 1]
                        header_stack.append(heading.group(2).strip())
                description = raw_content
                if not description or description.startswith("|<image_"):
                    description = f"Nội dung trực quan ở trang {page}, vùng {region_order}."
                chunk_text = (
                    f"Tài liệu: {original_filename}\n"
                    f"Trang: {page}\n"
                    f"Loại vùng: {region_type}\n"
                    f"Tiêu đề ngữ cảnh: {' > '.join(header_stack) or '(không có)'}\n"
                    f"Mô tả OCR: {description}"
                )
                source_id = _stable_id(document_id, page, region_order, region_type)
                documents.append(
                    Document(
                        page_content=chunk_text,
                        metadata={
                            "source_id": source_id,
                            "document_id": document_id,
                            "source": source_path,
                            "filename": original_filename,
                            "page": page,
                            "region_order": region_order,
                            "region_type": region_type,
                            "header_path": " > ".join(header_stack),
                            "coordinates": json.dumps(coordinates, ensure_ascii=False),
                            "image_path": str(image_path or ""),
                            "token_count": self.count_tokens(chunk_text),
                            "chunk_type": "visual",
                        },
                    )
                )
                continue

            segments: List[tuple[List[str], str]] = []
            segment_lines: List[str] = []
            segment_headers = list(header_stack)
            for line in raw_content.splitlines():
                heading = HEADING_RE.match(line.strip())
                if heading:
                    if any(item.strip() for item in segment_lines):
                        segments.append((segment_headers, "\n".join(segment_lines).strip()))
                    level = len(heading.group(1))
                    header_stack = header_stack[: level - 1]
                    header_stack.append(heading.group(2).strip())
                    segment_headers = list(header_stack)
                    segment_lines = [line]
                else:
                    segment_lines.append(line)
            if any(item.strip() for item in segment_lines):
                segments.append((segment_headers, "\n".join(segment_lines).strip()))

            part_index = 0
            for headers, segment in segments:
                for part in self._split_to_limit(segment) or []:
                    contextualized = (
                        f"Tài liệu: {original_filename}\n"
                        f"Trang: {page}\n"
                        f"Tiêu đề ngữ cảnh: {' > '.join(headers) or '(không có)'}\n"
                        f"Nội dung:\n{part}"
                    )
                    source_id = _stable_id(document_id, page, region_order, part_index)
                    documents.append(
                        Document(
                            page_content=contextualized,
                            metadata={
                                "source_id": source_id,
                                "document_id": document_id,
                                "source": source_path,
                                "filename": original_filename,
                                "page": page,
                                "region_order": region_order,
                                "region_type": region_type,
                                "header_path": " > ".join(headers),
                                "coordinates": json.dumps(coordinates, ensure_ascii=False),
                                "image_path": "",
                                "token_count": self.count_tokens(contextualized),
                                "chunk_type": "text",
                            },
                        )
                    )
                    part_index += 1

        logger.info("Created %s hierarchical chunks from %s", len(documents), original_filename)
        return documents


class LocalDocumentStore:
    """Persistent lexical store used by the laptop-friendly prototype."""

    def __init__(self, persist_path: str | Path | None = None):
        base = Path(persist_path or settings.DB_PATH)
        self.path = base if base.suffix == ".json" else base / "local_documents.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._documents: Dict[str, Document] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            for item in payload:
                document = Document(**item)
                self._documents[document.metadata["source_id"]] = document
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            logger.warning("Ignoring invalid local store %s: %s", self.path, exc)

    def _persist(self) -> None:
        payload = [asdict(document) for document in self._documents.values()]
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def add_documents(self, documents: List[Document]) -> None:
        for document in documents:
            self._documents[document.metadata["source_id"]] = document
        self._persist()
        logger.info("Indexed %s documents in local store", len(documents))

    @staticmethod
    def _score(query_tokens: set[str], document: Document) -> float:
        tokens = _tokenize(document.page_content)
        if not tokens or not query_tokens:
            return 0.0
        token_set = set(tokens)
        overlap = len(query_tokens & token_set)
        return overlap / math.sqrt(len(query_tokens) * len(token_set))

    def search(self, query: str, k: int, document_id: str | None = None) -> List[Document]:
        query_tokens = set(_tokenize(query))
        candidates = [
            document
            for document in self._documents.values()
            if document_id is None or document.metadata.get("document_id") == document_id
        ]
        ranked = sorted(
            ((self._score(query_tokens, document), document) for document in candidates),
            key=lambda pair: pair[0],
            reverse=True,
        )
        return [
            Document(item.page_content, dict(item.metadata), score=score)
            for score, item in ranked[:k]
            if score > 0
        ]


class ChromaVectorStore:
    """Optional semantic store; imports model dependencies only when selected."""

    def __init__(self):
        from langchain_chroma import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings

        embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
        self.vector_store = Chroma(
            collection_name=settings.COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=str(settings.DB_PATH),
        )

    def add_documents(self, documents: List[Document]) -> None:
        from langchain_core.documents import Document as LangChainDocument

        payload = [
            LangChainDocument(page_content=document.page_content, metadata=document.metadata)
            for document in documents
        ]
        ids = [document.metadata["source_id"] for document in documents]
        self.vector_store.add_documents(payload, ids=ids)

    def search(self, query: str, k: int, document_id: str | None = None) -> List[Document]:
        filter_value = {"document_id": document_id} if document_id else None
        pairs = self.vector_store.similarity_search_with_relevance_scores(
            query,
            k=k,
            filter=filter_value,
        )
        return [
            Document(item.page_content, dict(item.metadata), score=float(score))
            for item, score in pairs
        ]


class IndexingService:
    def __init__(self, chunker: IChunker, vector_store: IVectorStoreRepository):
        self.chunker = chunker
        self.vector_store = vector_store

    def index_from_json(self, json_path: str) -> Dict[str, Any]:
        path = Path(json_path)
        json_data = json.loads(path.read_text(encoding="utf-8"))
        documents = self.chunker.chunk(json_data, source_path=str(path))
        if documents:
            self.vector_store.add_documents(documents)
        document_id = documents[0].metadata["document_id"] if documents else None
        return {
            "chunks_indexed": len(documents),
            "json_path": str(path),
            "document_id": document_id,
        }

    def index_from_directory(self, directory_path: str) -> Dict[str, Any]:
        results = [self.index_from_json(str(path)) for path in Path(directory_path).rglob("*.json")]
        return {
            "total_files": len(results),
            "total_chunks": sum(item["chunks_indexed"] for item in results),
            "documents": results,
        }


def create_vector_store() -> IVectorStoreRepository:
    if settings.VECTOR_STORE_PROVIDER == "chroma":
        return ChromaVectorStore()
    return LocalDocumentStore()


def create_indexing_service(
    chunker: IChunker | None = None,
    vector_store: IVectorStoreRepository | None = None,
) -> IndexingService:
    return IndexingService(
        chunker or HierarchicalMarkdownChunker(),
        vector_store or create_vector_store(),
    )
