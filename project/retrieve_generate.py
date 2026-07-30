import gc
import os
from typing import List

import google.generativeai as genai
import torch
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from loguru import logger
from sentence_transformers import CrossEncoder
from transformers import AutoModelForCausalLM, AutoTokenizer

from config import CONFIG


class BaseGenerator:
    """Class cha định nghĩa giao diện chung cho việc sinh câu trả lời."""

    def generate(self, query: str, context: str) -> str:
        raise NotImplementedError


class LocalQwenGenerator(BaseGenerator):
    def __init__(self, config: dict):
        logger.info(f"Initializing Local Qwen Model: {config['local_model_path']}...")
        self.device = config["device"]
        self.max_new_tokens = config["max_new_tokens"]

        self.tokenizer = AutoTokenizer.from_pretrained(config["local_model_path"])
        self.model = AutoModelForCausalLM.from_pretrained(
            config["local_model_path"], torch_dtype="auto", device_map=self.device
        )
        logger.success("Local Qwen Model loaded successfully.")

    def _format_prompt(self, query: str, context: str) -> str:
        system_msg = (
            "Bạn là trợ lý AI hữu ích. Trả lời dựa trên thông tin được cung cấp. "
            "Nếu không có thông tin, hãy nói không biết."
        )
        user_msg = f"Thông tin:\n---\n{context}\n---\nCâu hỏi: {query}"

        messages = [{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}]
        return self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    def generate(self, query: str, context: str) -> str:
        prompt = self._format_prompt(query, context)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                temperature=0.3,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        generated_ids = outputs[0][inputs["input_ids"].shape[1] :]
        answer = self.tokenizer.decode(generated_ids, skip_special_tokens=True)

        # Dọn dẹp GPU
        torch.cuda.empty_cache()
        gc.collect()
        return answer.strip()



class GeminiGenerator(BaseGenerator):
    def __init__(self, config: dict):
        api_key = config.get("google_api_key")
        if not api_key or "YOUR_GOOGLE" in api_key:
            raise ValueError("Vui lòng cung cấp Google API Key hợp lệ trong CONFIG.")

        logger.info(f"Initializing Gemini Model: {config['gemini_model_name']}...")
        genai.configure(api_key=api_key)

        # Cấu hình model
        self.model = genai.GenerativeModel(
            model_name=config["gemini_model_name"],
            system_instruction="Bạn là trợ lý AI chuyên trả lời câu hỏi dựa trên tài liệu bằng tiếng Việt.",
        )
        logger.success("Gemini API connected successfully.")

    def generate(self, query: str, context: str) -> str:
        prompt = (
            f"Dưới đây là thông tin trích xuất từ tài liệu:\n"
            f"---\n{context}\n---\n"
            f"Dựa vào thông tin trên, hãy trả lời câu hỏi sau thật chi tiết và đầy đủ với kiến thức tổng hợp: {query}"
        )

        try:
            response = self.model.generate_content(
                prompt, generation_config=genai.types.GenerationConfig(temperature=0.3, max_output_tokens=1024)
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            return "Xin lỗi, đã xảy ra lỗi khi kết nối với Gemini."

class Reranker:
    def __init__(self, model_name: str, device: str):
        logger.info(f"Loading Reranker: {model_name}")
        self.model = CrossEncoder(model_name, device=device)

    def rank(self, query: str, docs: List[str], top_k: int) -> List[str]:
        if not docs:
            return []
        pairs = [[query, doc] for doc in docs]
        scores = self.model.predict(pairs, show_progress_bar=False)
        scored_docs = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, score in scored_docs[:top_k]]


class RAGPipeline:
    def __init__(self, config: dict):
        self.config = config

        # 1. Vector Store (Khởi tạo giống nhau cho cả 2 trường hợp)
        logger.info("Initializing Retrieval System...")
        self.embeddings = HuggingFaceEmbeddings(model_name=config["embedding_model"])
        self.vector_store = Chroma(
            collection_name=config["collection_name"],
            embedding_function=self.embeddings,
            persist_directory=config["db_path"],
        )
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": config["retrieval_k"]})

        # 2. Reranker
        self.reranker = Reranker(config["reranker_model"], config["device"])

        # 3. LLM Generator Selection (Strategy Pattern)
        if config["llm_provider"] == "gemini":
            self.generator = GeminiGenerator(config)
        elif config["llm_provider"] == "qwen":
            self.generator = LocalQwenGenerator(config)
        else:
            raise ValueError(f"Unknown llm_provider: {config['llm_provider']}")

    def run(self, query: str) -> str:
        logger.info(f"Processing Query ({self.config['llm_provider']}): '{query}'")

        # Step 1: Retrieve
        docs = self.retriever.invoke(query)
        if not docs:
            return "Không tìm thấy tài liệu liên quan."
        doc_texts = [d.page_content for d in docs]

        # Step 2: Rerank
        top_docs = self.reranker.rank(query, doc_texts, self.config["rerank_top_k"])
        logger.info(f"Reranked top {len(top_docs)} docs.")

        # Step 3: Context Building
        context = "\n\n".join(top_docs)
        # print(f"\n--- Context Provided to LLM ---\n{context}\n-------------------------------")

        # Step 4: Generate (gọi hàm generate của class đã chọn)
        answer = self.generator.generate(query, context)

        return answer



if __name__ == "__main__":

    CONFIG["google_api_key"] = ""

    try:
        rag = RAGPipeline(CONFIG)

        print(f"\n--- RAG SYSTEM READY (Provider: {CONFIG['llm_provider'].upper()}) ---")
        while True:
            user_query = input("\nBạn hỏi: ")
            if user_query.lower() in ["exit", "quit"]:
                break
            if not user_query.strip():
                continue

            response = rag.run(user_query)
            print(f"\nAnswer:\n{response}")
            print("-" * 50)

    except Exception as e:
        logger.error(f"Critical Error: {e}")
