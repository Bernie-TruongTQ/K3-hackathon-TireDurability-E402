import gc
import json
import os
import re
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, List
import torch
from pdf2image import convert_from_path
from PIL import Image
import logging
import argparse
from transformers import AutoModel, AutoTokenizer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeepSeekOCRProcessor:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.prompt = "<image>\n<|grounding|>Convert the document to markdown."
    def process_image(self, image_path: str, output_path: str) -> str:
        """
        Xử lý một tệp hình ảnh duy nhất và trả về kết quả OCR dưới dạng chuỗi Markdown.
        """
        try:
            markdown_content = self.model.infer(
                self.tokenizer,
                prompt=self.prompt,
                image_file=image_path,
                output_path=output_path,
                base_size=1024,
                image_size=1024,
                crop_mode=False,
                save_results=False,
                test_compress=True,
                eval_mode=True,
            )
            logger.info("Successfully processed image with DeepSeek-OCR.")
            return markdown_content
        except Exception as e:
            logger.error(f"Error during DeepSeek-OCR inference: {e}")
            return f"[ERROR: Could not process image {os.path.basename(image_path)} - {e}]"


class MarkdownParser:
    """
    Phân tích đầu ra có cấu trúc của DeepSeek-OCR thành danh sách các phần tử JSON.
    """

    BLOCK_PATTERN = re.compile(
        r"<\|ref\|>(.+?)<\|/ref\|>" r"<\|det\|>(\[\[.+?\]\])<\|/det\|>\n?" r"(.*?)" r"(?=<\|ref\|>|$)", re.DOTALL
    )

    def parse(
        self, markdown_content: str, page_num: int, original_filename: str, file_uuid: str
    ) -> List[Dict[str, Any]]:
        """
        Phân tích đầu ra OCR có cấu trúc thành danh sách các đối tượng JSON.
        """
        if markdown_content is None or not markdown_content.strip():
            logger.warning(f"Received empty or None content for parsing on page {page_num}.")
            return []

        elements = []
        matches = self.BLOCK_PATTERN.findall(markdown_content)

        for i, match in enumerate(matches):
            region_type = match[0].strip()
            coordinates_str = match[1].strip()
            content = match[2].strip()

            try:
                coords_list = json.loads(coordinates_str)
                coordinates = coords_list[0] if isinstance(coords_list[0], list) else coords_list
            except (json.JSONDecodeError, IndexError, TypeError):
                logger.warning(f"Failed to parse coordinates: {coordinates_str}")
                coordinates = []

            content = content.replace("\n", " ").strip()

            json_obj = {
                "file_name": f"{original_filename}_{file_uuid}",
                "page": page_num,
                "region_order": i + 1,
                "region_type": region_type,
                "content": content,
                "original_filename": original_filename,
                "metadata": {
                    "page": page_num,
                    "region_type": region_type,
                    "coordinates": coordinates,
                },
                "saved_link": None,
            }
            elements.append(json_obj)

        logger.info(f"Parsed {len(elements)} elements from page {page_num}.")
        return elements


class ResultFormatter:
    """
    Định dạng và lưu kết quả cuối cùng.
    """

    @staticmethod
    def save(
        json_objects: List[Dict[str, Any]],
        output_dir: str,
        base_filename: str,
    ):
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Tạo nội dung markdown cuối cùng từ các đối tượng JSON đã xử lý
        final_md_blocks = [obj["content"] for obj in json_objects]
        final_md_output = "\n\n---\n\n".join(final_md_blocks)

        json_path = os.path.join(output_dir, f"{base_filename}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"elements": json_objects}, f, ensure_ascii=False, indent=2)
        logger.success(f"Saved JSON output to {json_path}")

        md_path = os.path.join(output_dir, f"{base_filename}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(final_md_output)
        logger.success(f"Saved Markdown output to {md_path}")


# --- COMPONENT 4: Main Pipeline ---


class OCRPipeline:
    """
    Điều phối toàn bộ quy trình OCR.
    """

    def __init__(self, ocr_processor: DeepSeekOCRProcessor, parser: MarkdownParser):
        self.ocr_processor = ocr_processor
        self.parser = parser

    def run(self, pdf_path: str, output_dir: str) -> None:
        logger.info(f"--- Starting OCR Pipeline for: {pdf_path} ---")
        base_filename = Path(pdf_path).stem
        file_uuid = uuid.uuid4().hex

        try:
            logger.info("Converting PDF to images...")
            page_images = convert_from_path(pdf_path, dpi=200)
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            return

        all_json_objects = []
        image_global_counter = 0

        image_output_subdir = os.path.join(output_dir, "images")
        os.makedirs(image_output_subdir, exist_ok=True)
        logger.info(f"Image directory created at: {image_output_subdir}")

        with tempfile.TemporaryDirectory() as temp_dir:
            for page_num, page_image_pil in enumerate(page_images):
                page_num_actual = page_num + 1
                logger.info(f"\n--- Processing Page {page_num_actual}/{len(page_images)} ---")

                # Lưu ảnh tạm thời để xử lý (Bỏ qua bước cắt Logo)
                temp_image_path = os.path.join(temp_dir, f"page_{page_num_actual}.png")
                page_image_pil.save(temp_image_path, "PNG")
                width, height = page_image_pil.size

                # Chạy OCR
                page_markdown = self.ocr_processor.process_image(temp_image_path, output_path=temp_dir)

                # Phân tích kết quả
                page_json_elements = self.parser.parse(
                    markdown_content=page_markdown,
                    page_num=page_num_actual,
                    original_filename=base_filename,
                    file_uuid=file_uuid,
                )

                # Xử lý các phần tử hình ảnh (cắt ảnh con từ ảnh gốc)
                for element in page_json_elements:
                    if element["region_type"] == "image":
                        image_global_counter += 1
                        image_filename = f"image_{image_global_counter}.jpg"
                        saved_link_path = os.path.join(image_output_subdir, image_filename)

                        coords = element["metadata"]["coordinates"]
                        if len(coords) == 4:
                            x1_norm, y1_norm, x2_norm, y2_norm = coords
                            x1 = int(x1_norm / 1000 * width)
                            y1 = int(y1_norm / 1000 * height)
                            x2 = int(x2_norm / 1000 * width)
                            y2 = int(y2_norm / 1000 * height)

                            # Cắt ảnh từ ảnh gốc (đầy đủ, không bị cắt logo)
                            cropped_image = page_image_pil.crop((x1, y1, x2, y2))
                            cropped_image.save(saved_link_path, "JPEG", quality=90)

                            element["saved_link"] = str(saved_link_path)
                            element["content"] = f"|<image_{image_global_counter}>|"
                        else:
                            logger.warning(f"Image block on page {page_num_actual} has invalid coordinates: {coords}")

                all_json_objects.extend(page_json_elements)

        # Lưu kết quả cuối cùng
        ResultFormatter.save(
            json_objects=all_json_objects,
            output_dir=output_dir,
            base_filename=base_filename,
        )

        torch.cuda.empty_cache()
        gc.collect()
        logger.success(f"\n--- OCR Pipeline finished successfully for: {pdf_path} ---\n")


# --- Hàm chính để thực thi ---


def main():
    parser = argparse.ArgumentParser(description="Run the DeepSeek-OCR pipeline on a directory of PDFs.")
    parser.add_argument("--input_dir", type=str, required=True, help="Directory containing the PDF files to process.")
    parser.add_argument(
        "--output_dir", type=str, required=True, help="Directory to save the output JSON and Markdown files."
    )
    # Đã xóa --model_path vì không còn dùng YOLO nữa
    args = parser.parse_args()

    # --- Tải các mô hình ---
    logger.info("Loading DeepSeek-OCR model: deepseek-ai/DeepSeek-OCR...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if not torch.cuda.is_available():
        logger.warning("CUDA not available, running on CPU. This will be very slow.")

    tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-OCR", trust_remote_code=True)
    model = (
        AutoModel.from_pretrained(
            "deepseek-ai/DeepSeek-OCR",
            trust_remote_code=True,
            use_safetensors=True,
        )
        .to(device)
        .eval()
    )

    if device == "cuda" and torch.cuda.is_bf16_supported():
        model = model.to(torch.bfloat16)
        logger.info("Model converted to bfloat16.")
    else:
        logger.info("bfloat16 not supported, using default precision.")

    logger.success("DeepSeek-OCR model loaded successfully.")

    # --- Khởi tạo các thành phần của pipeline ---
    ocr_processor = DeepSeekOCRProcessor(model, tokenizer)
    markdown_parser = MarkdownParser()

    # Khởi tạo Pipeline không còn tham số logo_processor
    pipeline = OCRPipeline(ocr_processor, markdown_parser)

    # --- Xử lý các tệp PDF ---
    os.makedirs(args.output_dir, exist_ok=True)

    for filename in os.listdir(args.input_dir):
        if filename.lower().endswith(".pdf"):
            pdf_file_path = os.path.join(args.input_dir, filename)
            pdf_base_name = Path(filename).stem

            # Tạo một thư mục con cho mỗi tệp PDF
            pdf_output_dir = os.path.join(args.output_dir, pdf_base_name)
            os.makedirs(pdf_output_dir, exist_ok=True)

            logger.info(f"Processing PDF: {filename}")
            pipeline.run(pdf_path=pdf_file_path, output_dir=pdf_output_dir)
        else:
            logger.info(f"Skipping non-PDF file: {filename}")


if __name__ == "__main__":
    main()

"""
python ocr.py --input_dir output_pdfs --output_dir ocr_output_ds
"""
