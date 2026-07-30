"""
RAG Service Module with Streaming Support
Handles Retrieval-Augmented Generation pipeline.
Includes retrieval, reranking, and generation with multiple LLM providers.
Supports streaming for better UX.
"""

import gc
from threading import Thread
from typing import AsyncGenerator, List, Tuple

import google.generativeai as genai
import torch
from langchain_core.documents import Document
from loguru import logger
from sentence_transformers import CrossEncoder
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

from app.core.config import settings
from app.services.indexing_service import IVectorStoreRepository


class ILLMGenerator:
    """
    Interface for LLM generators (Interface Segregation Principle).
    Allows easy swapping between different LLM providers.
    """

    def generate(self, query: str, context: str) -> str:
        """Generate answer based on query and context."""
        raise NotImplementedError

    async def generate_stream(self, query: str, context: str) -> AsyncGenerator[str, None]:
        """Generate answer with streaming support."""
        raise NotImplementedError


class LocalQwenGenerator(ILLMGenerator):
    """
    Local Qwen LLM generator with streaming support.
    Single Responsibility: Only handles local Qwen model generation.
    """

    def __init__(self):
        logger.info(f"Loading Local Qwen Model: {settings.LOCAL_LLM_MODEL}")

        self.device = settings.DEVICE
        self.max_new_tokens = settings.LOCAL_LLM_MAX_TOKENS
        self.temperature = settings.LOCAL_LLM_TEMPERATURE

        logger.info(f"Loading tokenizer and model for {settings.LOCAL_LLM_MODEL}...")
        self.tokenizer = AutoTokenizer.from_pretrained(settings.LOCAL_LLM_MODEL)
        self.model = AutoModelForCausalLM.from_pretrained(
            settings.LOCAL_LLM_MODEL, torch_dtype="auto", device_map=self.device
        )

        logger.success("Local Qwen Model loaded successfully")

    def _format_prompt(self, query: str, context: str) -> str:
        """Format prompt for Qwen model."""
        system_msg = (
            "Bạn là trợ lý AI hữu ích. Trả lời dựa trên thông tin được cung cấp. "
            "Nếu không có thông tin, hãy nói không biết."
        )
        user_msg = f"Thông tin:\n---\n{context}\n---\nCâu hỏi: {query}"

        messages = [{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}]

        return self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    def generate(self, query: str, context: str) -> str:
        """Generate answer using local Qwen model."""
        prompt = self._format_prompt(query, context)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                temperature=self.temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        generated_ids = outputs[0][inputs["input_ids"].shape[1] :]
        answer = self.tokenizer.decode(generated_ids, skip_special_tokens=True)

        # Cleanup
        torch.cuda.empty_cache()
        gc.collect()

        return answer.strip()

    async def generate_stream(self, query: str, context: str) -> AsyncGenerator[str, None]:
        """Generate answer with streaming using TextIteratorStreamer."""
        prompt = self._format_prompt(query, context)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        # Create streamer
        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)

        # Generation kwargs
        generation_kwargs = dict(
            **inputs,
            max_new_tokens=self.max_new_tokens,
            temperature=self.temperature,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
            streamer=streamer,
        )

        # Run generation in thread
        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()

        # Stream tokens
        for text in streamer:
            yield text

        thread.join()

        # Cleanup
        torch.cuda.empty_cache()
        gc.collect()


class GeminiGenerator(ILLMGenerator):
    """
    Gemini API LLM generator with streaming support.
    Single Responsibility: Only handles Gemini API generation.
    """

    def __init__(self):
        if not settings.GOOGLE_API_KEY or "YOUR_GOOGLE" in settings.GOOGLE_API_KEY:
            raise ValueError("Valid Google API Key is required for Gemini generator")

        logger.info(f"Initializing Gemini Model: {settings.GEMINI_MODEL}")

        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            system_instruction="Bạn là trợ lý AI chuyên trả lời câu hỏi dựa trên tài liệu bằng tiếng Việt.",
        )

        logger.success("Gemini API connected successfully")

    def generate(self, query: str, context: str) -> str:
        """Generate answer using Gemini API."""
        prompt = (
            f"Dưới đây là thông tin trích xuất từ tài liệu:\n"
            f"---\n{context}\n---\n"
            f"Dựa vào thông tin trên, hãy trả lời câu hỏi sau thật chi tiết và đầy đủ "
            f"với kiến thức tổng hợp: {query}"
        )

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=settings.GEMINI_TEMPERATURE, max_output_tokens=settings.GEMINI_MAX_TOKENS
                ),
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            return "Xin lỗi, đã xảy ra lỗi khi kết nối với Gemini."

    async def generate_stream(self, query: str, context: str) -> AsyncGenerator[str, None]:
        """Generate answer with streaming using Gemini API."""
        prompt = (
            f"Dưới đây là thông tin trích xuất từ tài liệu:\n"
            f"---\n{context}\n---\n"
            f"Dựa vào thông tin trên, hãy trả lời câu hỏi sau thật chi tiết và đầy đủ "
            f"với kiến thức tổng hợp: {query}"
        )

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=settings.GEMINI_TEMPERATURE, max_output_tokens=settings.GEMINI_MAX_TOKENS
                ),
                stream=True,
            )

            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Gemini API Streaming Error: {e}")
            yield "Xin lỗi, đã xảy ra lỗi khi kết nối với Gemini."


class Reranker:
    """
    Document reranker using cross-encoder.
    Single Responsibility: Only handles document reranking.
    """

    def __init__(self):
        logger.info(f"Loading Reranker: {settings.RERANKER_MODEL}")
        self.model = CrossEncoder(settings.RERANKER_MODEL, device=settings.DEVICE)
        logger.success("Reranker loaded successfully")

    def rank(self, query: str, docs: List[str], top_k: int) -> List[Tuple[str, float]]:
        """
        Rank documents by relevance to query.

        Args:
            query: User query
            docs: List of document texts
            top_k: Number of top documents to return

        Returns:
            List of tuples (document_text, score) sorted by relevance
        """
        if not docs:
            return []

        pairs = [[query, doc] for doc in docs]
        scores = self.model.predict(pairs, show_progress_bar=False)

        # Sort by score descending
        scored_docs = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)

        return scored_docs[:top_k]


class RAGService:
    """
    Main RAG service orchestrating the retrieval-augmented generation pipeline.
    Supports both regular and streaming responses.
    """

    def __init__(self, vector_store: IVectorStoreRepository, reranker: Reranker):
        self.vector_store = vector_store
        self.reranker = reranker

    def set_generator(self, generator: ILLMGenerator):
        """Set the LLM generator dynamically."""
        self.generator = generator
        self.generator_type = type(generator).__name__
        logger.info(f"RAGService configured to use generator: {self.generator_type}")

    def query(self, user_query: str, retrieval_k: int = None, rerank_k: int = None) -> Tuple[str, List[Document]]:
        """
        Process user query through RAG pipeline.

        Args:
            user_query: User's question
            retrieval_k: Number of documents to retrieve (default from config)
            rerank_k: Number of documents after reranking (default from config)

        Returns:
            Tuple of (answer, source_documents)
        """
        retrieval_k = retrieval_k or settings.RETRIEVAL_TOP_K
        rerank_k = rerank_k or settings.RERANK_TOP_K

        logger.info(f"Processing query: '{user_query}'")

        # Step 1: Retrieve from vector store
        logger.debug(f"Retrieving top {retrieval_k} documents")
        docs = self.vector_store.search(user_query, retrieval_k)

        if not docs:
            logger.warning("No documents retrieved")
            return "Không tìm thấy tài liệu liên quan để trả lời câu hỏi.", []

        logger.info(f"Retrieved {len(docs)} documents")

        # Step 2: Rerank documents
        doc_texts = [d.page_content for d in docs]
        ranked_results = self.reranker.rank(user_query, doc_texts, rerank_k)

        if not ranked_results:
            logger.warning("No documents after reranking")
            return "Không tìm thấy tài liệu phù hợp để trả lời câu hỏi.", []

        top_docs_texts = [text for text, score in ranked_results]
        logger.info(f"Reranked to top {len(top_docs_texts)} documents")

        # Find original documents for sources
        source_docs = []
        for top_text in top_docs_texts:
            for doc in docs:
                if doc.page_content == top_text:
                    source_docs.append(doc)
                    break

        # Step 3: Build context
        context = "\n\n".join(top_docs_texts)

        # Step 4: Generate answer
        logger.info(f"Generating answer with {self.generator_type}")
        answer = self.generator.generate(user_query, context)

        logger.success("Query processed successfully")
        return answer, source_docs

    async def query_stream(
        self, user_query: str, retrieval_k: int = None, rerank_k: int = None
    ) -> AsyncGenerator[dict, None]:
        """
        Process user query through RAG pipeline with streaming.

        Args:
            user_query: User's question
            retrieval_k: Number of documents to retrieve (default from config)
            rerank_k: Number of documents after reranking (default from config)

        Yields:
            Dictionary with 'type' and 'data' fields for different stages
        """
        retrieval_k = retrieval_k or settings.RETRIEVAL_TOP_K
        rerank_k = rerank_k or settings.RERANK_TOP_K

        logger.info(f"Processing streaming query: '{user_query}'")

        # Step 1: Retrieve from vector store
        yield {"type": "status", "data": "Đang tìm kiếm tài liệu liên quan..."}
        docs = self.vector_store.search(user_query, retrieval_k)

        if not docs:
            yield {"type": "error", "data": "Không tìm thấy tài liệu liên quan."}
            return

        # Step 2: Rerank documents
        yield {"type": "status", "data": "Đang phân tích và sắp xếp thông tin..."}
        doc_texts = [d.page_content for d in docs]
        ranked_results = self.reranker.rank(user_query, doc_texts, rerank_k)

        if not ranked_results:
            yield {"type": "error", "data": "Không tìm thấy tài liệu phù hợp."}
            return

        top_docs_texts = [text for text, score in ranked_results]

        # Find original documents for sources
        source_docs = []
        for top_text in top_docs_texts:
            for doc in docs:
                if doc.page_content == top_text:
                    source_docs.append(doc)
                    break

        # Send sources first
        yield {
            "type": "sources",
            "data": [
                {
                    "page": doc.metadata.get("page", 0),
                    "filename": doc.metadata.get("filename", "unknown"),
                    "content_preview": (
                        doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                    ),
                }
                for doc in source_docs
            ],
        }

        # Step 3: Build context and generate with streaming
        yield {"type": "status", "data": "Đang tạo câu trả lời..."}
        context = "\n\n".join(top_docs_texts)

        # Stream the answer
        async for text_chunk in self.generator.generate_stream(user_query, context):
            yield {"type": "text", "data": text_chunk}

        yield {"type": "done", "data": ""}
        logger.success("Streaming query processed successfully")


def create_rag_service(vector_store: IVectorStoreRepository) -> RAGService:
    """
    Factory function to create RAGService.

    Args:
        vector_store: Vector store repository instance

    Returns:
        Configured RAGService instance
    """
    # Create reranker
    reranker = Reranker()

    rag_service = RAGService(vector_store, reranker)
    return rag_service
