"""Grounded text/visual RAG orchestration with lazy AI providers."""

from __future__ import annotations

import base64
import json
import logging
import mimetypes
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import AsyncGenerator, Iterable, List, Protocol

from app.core.config import settings
from app.services.indexing_service import Document, IVectorStoreRepository, _tokenize

logger = logging.getLogger(__name__)


VISUAL_INTENT_RE = re.compile(
    r"\b(hình|ảnh|biểu đồ|đồ thị|sơ đồ|bảng|công thức|chart|figure|diagram|table|formula)\b",
    re.I,
)
AMBIGUOUS_RE = re.compile(r"\b(cái này|hình này|ảnh này|bảng này|phần này)\b", re.I)
IDENTITY_RE = re.compile(r"\b(ai trong ảnh|người trong ảnh là ai|nhận diện người)\b", re.I)
WEB_REQUEST_RE = re.compile(
    r"\b(google|tìm trên web|tìm thêm nguồn|tra cứu internet|nguồn bên ngoài)\b",
    re.I,
)
SOURCE_OVERRIDE_RE = re.compile(
    r"\b(bỏ qua tài liệu|bỏ qua nguồn|ignore (the )?(document|source)|"
    r"trả lời theo kiến thức của bạn)\b",
    re.I,
)
REGION_SELECTION_RE = re.compile(
    r"\b(khoanh|đánh dấu|hai biểu đồ|so sánh .*biểu đồ)\b",
    re.I,
)


class ILLMGenerator(Protocol):
    provider_name: str
    model_name: str
    is_mock: bool

    def generate(self, query: str, context: str, image_paths: List[str]) -> str: ...


class DemoExtractiveGenerator:
    """Explicitly labelled mock provider for UI work without an API/model."""

    provider_name = "demo"
    model_name = "demo-extractive"
    is_mock = True

    def generate(self, query: str, context: str, image_paths: List[str]) -> str:
        first_source = context.split("\n\n[SOURCE", 1)[0]
        excerpt = first_source[-700:].strip()
        return (
            "[DEMO — chưa phải lời gọi AI thật]\n"
            "Nguồn truy xuất liên quan nhất cho câu hỏi của bạn:\n\n"
            f"{excerpt}"
        )


class LocalQwenGenerator:
    provider_name = "qwen"
    is_mock = False

    def __init__(self):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.torch = torch
        self.model_name = settings.LOCAL_LLM_MODEL
        self.tokenizer = AutoTokenizer.from_pretrained(settings.LOCAL_LLM_MODEL)
        self.model = AutoModelForCausalLM.from_pretrained(
            settings.LOCAL_LLM_MODEL,
            torch_dtype="auto",
            device_map=settings.DEVICE,
        )

    def generate(self, query: str, context: str, image_paths: List[str]) -> str:
        system = (
            "Bạn là trợ lý VLearn. Chỉ trả lời bằng thông tin trong SOURCE. "
            "Mọi kết luận phải kèm [S#]. Nếu SOURCE không đủ, nói rõ không tìm "
            "thấy căn cứ. Không dùng kiến thức bên ngoài."
        )
        if image_paths:
            system += " Model này không nhìn ảnh gốc; chỉ dùng mô tả OCR và phải nêu giới hạn đó."
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": f"{context}\n\nCâu hỏi: {query}"},
        ]
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(settings.DEVICE)
        with self.torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=settings.LOCAL_LLM_MAX_TOKENS,
                temperature=settings.LOCAL_LLM_TEMPERATURE,
                do_sample=settings.LOCAL_LLM_TEMPERATURE > 0,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        generated = outputs[0][inputs["input_ids"].shape[1] :]
        return self.tokenizer.decode(generated, skip_special_tokens=True).strip()


class GeminiGenerator:
    provider_name = "gemini"
    is_mock = False

    def __init__(self):
        if not settings.GOOGLE_API_KEY or "YOUR_GOOGLE" in settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY chưa được cấu hình")
        import google.generativeai as genai

        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.genai = genai
        self.model_name = settings.GEMINI_MODEL
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            system_instruction=(
                "Bạn là trợ lý VLearn. Chỉ dùng SOURCE và ảnh được cung cấp. "
                "Mọi claim phải kèm [S#]. Không có căn cứ thì nói không tìm thấy; "
                "không bổ sung kiến thức ngoài."
            ),
        )

    def generate(self, query: str, context: str, image_paths: List[str]) -> str:
        from PIL import Image

        parts: List[object] = [
            f"{context}\n\nCâu hỏi: {query}\n"
            "Trả lời tiếng Việt ngắn gọn và gắn citation [S#] ngay sau claim."
        ]
        for image_path in image_paths[:3]:
            path = Path(image_path)
            if path.exists():
                parts.append(Image.open(path))
        response = self.model.generate_content(
            parts,
            generation_config=self.genai.types.GenerationConfig(
                temperature=settings.GEMINI_TEMPERATURE,
                max_output_tokens=settings.GEMINI_MAX_TOKENS,
            ),
        )
        return response.text.strip()


class OpenAIResponsesGenerator:
    """Multimodal grounded generation through the OpenAI Responses API."""

    provider_name = "openai"
    model_name = settings.OPENAI_MODEL
    is_mock = False

    def __init__(self):
        if not settings.OPENAI_API_KEY or "YOUR_OPENAI" in settings.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY chưa được cấu hình. "
                "Đặt VISUALRAG_OPENAI_API_KEY trong project/.env."
            )
        from openai import OpenAI

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    @staticmethod
    def _image_data_url(image_path: str) -> str | None:
        path = Path(image_path)
        if not path.exists() or not path.is_file():
            return None
        content_type = mimetypes.guess_type(path.name)[0] or "image/png"
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:{content_type};base64,{encoded}"

    def generate(self, query: str, context: str, image_paths: List[str]) -> str:
        content: List[dict] = [
            {
                "type": "input_text",
                "text": (
                    f"{context}\n\nCâu hỏi: {query}\n\n"
                    "Chỉ trả lời từ SOURCE và ảnh đính kèm. Gắn citation [S#] ngay "
                    "sau từng claim. Nếu evidence không đủ, mâu thuẫn hoặc không đọc "
                    "được thì nói rõ; tuyệt đối không đoán."
                ),
            }
        ]
        for image_path in image_paths[:3]:
            data_url = self._image_data_url(image_path)
            if data_url:
                content.append(
                    {
                        "type": "input_image",
                        "image_url": data_url,
                        "detail": "high",
                    }
                )

        response = self.client.responses.create(
            model=settings.OPENAI_MODEL,
            instructions=(
                "Bạn là trợ lý VLearn VisualRAG. Nguồn sự thật duy nhất là các "
                "SOURCE và ảnh được cung cấp. Không dùng web hoặc kiến thức ngoài. "
                "Trả lời tiếng Việt ngắn gọn. Nếu không đủ căn cứ, phải abstain."
            ),
            input=[{"role": "user", "content": content}],
            temperature=settings.OPENAI_TEMPERATURE,
            max_output_tokens=settings.OPENAI_MAX_OUTPUT_TOKENS,
        )
        return response.output_text.strip()


class IReranker(Protocol):
    def rank(self, query: str, documents: List[Document], top_k: int) -> List[Document]: ...


class LexicalReranker:
    def rank(self, query: str, documents: List[Document], top_k: int) -> List[Document]:
        query_tokens = set(_tokenize(query))
        for document in documents:
            overlap = len(query_tokens & set(_tokenize(document.page_content)))
            base_score = document.score or 0.0
            document.score = base_score + overlap / max(1, len(query_tokens))
        return sorted(documents, key=lambda item: item.score or 0.0, reverse=True)[:top_k]


class CrossEncoderReranker:
    def __init__(self):
        from sentence_transformers import CrossEncoder

        self.model = CrossEncoder(settings.RERANKER_MODEL, device=settings.DEVICE)

    def rank(self, query: str, documents: List[Document], top_k: int) -> List[Document]:
        if not documents:
            return []
        scores = self.model.predict(
            [[query, document.page_content] for document in documents],
            show_progress_bar=False,
        )
        for document, score in zip(documents, scores):
            document.score = float(score)
        return sorted(documents, key=lambda item: item.score or 0.0, reverse=True)[:top_k]


@dataclass
class RAGResult:
    answer: str
    sources: List[Document] = field(default_factory=list)
    route: str = "text"
    grounded: bool = True
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    provider: str = "demo"
    model: str = "demo-extractive"
    is_mock: bool = False


def _format_context(documents: Iterable[Document]) -> str:
    blocks = []
    for index, document in enumerate(documents, start=1):
        metadata = document.metadata
        blocks.append(
            f"[SOURCE S{index}]\n"
            f"filename={metadata.get('filename', 'unknown')}; "
            f"page={metadata.get('page', 0)}; "
            f"region={metadata.get('region_order', 0)}; "
            f"type={metadata.get('region_type', 'text')}\n"
            f"{document.page_content}"
        )
    return "\n\n".join(blocks)


class RAGService:
    def __init__(
        self,
        vector_store: IVectorStoreRepository,
        reranker: IReranker | None = None,
        generator: ILLMGenerator | None = None,
    ):
        self.vector_store = vector_store
        self.reranker = reranker or LexicalReranker()
        self.generator = generator or DemoExtractiveGenerator()

    def set_generator(self, generator: ILLMGenerator) -> None:
        self.generator = generator

    def _write_trace(self, query: str, result: RAGResult) -> None:
        settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        path = settings.TEMP_DIR / "rag_traces.jsonl"
        record = {
            "trace_id": result.trace_id,
            "query": query,
            "provider": result.provider,
            "model": result.model,
            "is_mock": result.is_mock,
            "route": result.route,
            "grounded": result.grounded,
            "sources": [
                {
                    "source_id": item.metadata.get("source_id"),
                    "filename": item.metadata.get("filename"),
                    "page": item.metadata.get("page"),
                    "region_type": item.metadata.get("region_type"),
                    "image_path": item.metadata.get("image_path"),
                    "score": item.score,
                }
                for item in result.sources
            ],
            "answer": result.answer,
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    def query(
        self,
        user_query: str,
        document_id: str | None = None,
        selected_page: int | None = None,
        selected_image_id: str | None = None,
        retrieval_k: int | None = None,
        rerank_k: int | None = None,
    ) -> RAGResult:
        query = user_query.strip()
        provider = self.generator.provider_name
        model = self.generator.model_name

        if IDENTITY_RE.search(query):
            result = RAGResult(
                answer=(
                    "Mình không suy đoán danh tính người trong ảnh. "
                    "Nếu tài liệu có chú thích, mình có thể giải thích vai trò của ảnh đó."
                ),
                route="refuse",
                grounded=True,
                provider=provider,
                model=model,
                is_mock=self.generator.is_mock,
            )
            self._write_trace(query, result)
            return result

        if WEB_REQUEST_RE.search(query):
            result = RAGResult(
                answer=(
                    "Tính năng này chỉ trả lời từ tài liệu đã nạp và không tự tìm nguồn "
                    "trên web. Bạn có thể tải nguồn chính thức lên để mình kiểm tra."
                ),
                route="refuse",
                grounded=True,
                provider=provider,
                model=model,
                is_mock=self.generator.is_mock,
            )
            self._write_trace(query, result)
            return result

        if SOURCE_OVERRIDE_RE.search(query):
            result = RAGResult(
                answer=(
                    "Mình không bỏ qua tài liệu nguồn. Nếu source hiện tại không đủ căn cứ, "
                    "mình sẽ nói rõ giới hạn thay vì trả lời theo kiến thức ngoài."
                ),
                route="refuse",
                grounded=True,
                provider=provider,
                model=model,
                is_mock=self.generator.is_mock,
            )
            self._write_trace(query, result)
            return result

        if AMBIGUOUS_RE.search(query) and selected_page is None and not selected_image_id:
            result = RAGResult(
                answer="Bạn đang nói tới trang hoặc hình nào? Hãy chọn một nguồn/thumbnail để mình phân tích đúng vùng.",
                route="clarify",
                grounded=True,
                provider=provider,
                model=model,
                is_mock=self.generator.is_mock,
            )
            self._write_trace(query, result)
            return result

        documents = self.vector_store.search(
            query,
            retrieval_k or settings.RETRIEVAL_TOP_K,
            document_id=document_id,
        )
        if selected_page is not None:
            page_documents = [
                document for document in documents if document.metadata.get("page") == selected_page
            ]
            if page_documents:
                documents = page_documents
        if selected_image_id:
            selected = [
                document
                for document in documents
                if document.metadata.get("source_id") == selected_image_id
            ]
            if selected:
                documents = selected

        if not documents:
            result = RAGResult(
                answer="Mình không tìm thấy căn cứ liên quan trong tài liệu đã nạp.",
                route="abstain",
                grounded=True,
                provider=provider,
                model=model,
                is_mock=self.generator.is_mock,
            )
            self._write_trace(query, result)
            return result

        ranked = self.reranker.rank(query, documents, rerank_k or settings.RERANK_TOP_K)
        visual_requested = bool(VISUAL_INTENT_RE.search(query))
        visual_sources = [
            document
            for document in ranked
            if document.metadata.get("chunk_type") == "visual"
            or document.metadata.get("image_path")
        ]
        if (
            visual_requested
            and selected_page is not None
            and not selected_image_id
            and REGION_SELECTION_RE.search(query)
            and len(visual_sources) > 1
        ):
            result = RAGResult(
                answer=(
                    "Trang này có nhiều vùng hình phù hợp. Hãy chọn đúng thumbnail hoặc "
                    "vùng được khoanh để mình không phân tích nhầm."
                ),
                sources=visual_sources,
                route="clarify",
                grounded=True,
                provider=provider,
                model=model,
                is_mock=self.generator.is_mock,
            )
            self._write_trace(query, result)
            return result
        route = "visual" if visual_requested or visual_sources else "text"
        image_paths = [
            str(document.metadata["image_path"])
            for document in visual_sources
            if document.metadata.get("image_path")
        ]

        if route == "visual" and not image_paths and visual_requested:
            result = RAGResult(
                answer=(
                    "Mình tìm thấy ngữ cảnh chữ nhưng chưa xác định được vùng ảnh gốc. "
                    "Hãy chọn đúng trang hoặc thumbnail để tránh mình đoán nội dung hình."
                ),
                sources=ranked,
                route="clarify",
                grounded=True,
                provider=provider,
                model=model,
                is_mock=self.generator.is_mock,
            )
            self._write_trace(query, result)
            return result

        context = _format_context(ranked)
        answer = self.generator.generate(query, context, image_paths if route == "visual" else [])
        result = RAGResult(
            answer=answer,
            sources=ranked,
            route=route,
            grounded=True,
            provider=provider,
            model=model,
            is_mock=self.generator.is_mock,
        )
        self._write_trace(query, result)
        return result

    async def query_stream(self, *args, **kwargs) -> AsyncGenerator[dict, None]:
        yield {"type": "status", "data": "Đang truy xuất nguồn..."}
        result = self.query(*args, **kwargs)
        yield {
            "type": "sources",
            "data": [
                {
                    "source_id": document.metadata.get("source_id"),
                    "filename": document.metadata.get("filename", "unknown"),
                    "page": document.metadata.get("page", 0),
                    "region_type": document.metadata.get("region_type", "text"),
                    "image_path": document.metadata.get("image_path") or None,
                    "score": document.score,
                    "content_preview": document.page_content[:240],
                }
                for document in result.sources
            ],
        }
        yield {
            "type": "meta",
            "data": {
                "route": result.route,
                "grounded": result.grounded,
                "provider": result.provider,
                "is_mock": result.is_mock,
                "trace_id": result.trace_id,
            },
        }
        yield {"type": "text", "data": result.answer}
        yield {"type": "done", "data": ""}


def create_generator(provider: str | None = None) -> ILLMGenerator:
    selected = provider or settings.LLM_PROVIDER
    if selected == "qwen":
        return LocalQwenGenerator()
    if selected == "gemini":
        return GeminiGenerator()
    if selected == "openai":
        return OpenAIResponsesGenerator()
    if selected == "demo":
        return DemoExtractiveGenerator()
    raise ValueError(f"Provider không hợp lệ: {selected}")


def create_reranker() -> IReranker:
    if settings.RERANKER_PROVIDER == "cross_encoder":
        return CrossEncoderReranker()
    return LexicalReranker()


def create_rag_service(
    vector_store: IVectorStoreRepository,
    provider: str | None = None,
) -> RAGService:
    return RAGService(vector_store, create_reranker(), create_generator(provider))
