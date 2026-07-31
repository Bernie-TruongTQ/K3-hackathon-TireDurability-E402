"""
OCR Service Module
Handles document OCR processing with DeepSeek-OCR model.
Follows Single Responsibility Principle - only responsible for OCR operations.
"""

import gc
import json
import logging
import os
import re
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, List, Tuple

from app.core.config import settings

logger = logging.getLogger(__name__)


class IOCRProcessor:
    """Interface for OCR processors (Interface Segregation Principle)."""

    def process_image(self, image_path: str, output_path: str) -> str:
        """Process a single image and return OCR result as markdown."""
        raise NotImplementedError


class DeepSeekOCRProcessor(IOCRProcessor):
    """
    Concrete implementation of OCR processor using DeepSeek-OCR model.
    Encapsulates all DeepSeek-specific logic.
    """

    def __init__(self, model: Any, tokenizer: Any):
        self.model = model
        self.tokenizer = tokenizer
        self.prompt = "<image>\n<|grounding|>Convert the document to markdown."
        logger.info("DeepSeekOCRProcessor initialized")

    def process_image(self, image_path: str, output_path: str) -> str:
        """
        Process a single image file and return OCR result.

        Args:
            image_path: Path to input image
            output_path: Path to save temporary output

        Returns:
            Markdown content from OCR
        """
        try:
            markdown_content = self.model.infer(
                self.tokenizer,
                prompt=self.prompt,
                image_file=image_path,
                output_path=output_path,
                base_size=settings.OCR_BASE_SIZE,
                image_size=settings.OCR_IMAGE_SIZE,
                crop_mode=False,
                save_results=False,
                test_compress=True,
                eval_mode=True,
            )
            logger.debug(f"Successfully processed image: {os.path.basename(image_path)}")
            return markdown_content
        except Exception as e:
            logger.error(f"Error during OCR inference: {e}")
            raise RuntimeError(f"Could not process image {os.path.basename(image_path)}") from e


class MarkdownParser:
    """
    Parses structured markdown output from DeepSeek-OCR into JSON elements.
    Single Responsibility: Only handles markdown parsing.
    """

    BLOCK_PATTERN = re.compile(
        r"<\|ref\|>(.+?)<\|/ref\|>" r"<\|det\|>(\[\[.+?\]\])<\|/det\|>\n?" r"(.*?)" r"(?=<\|ref\|>|$)", re.DOTALL
    )

    def parse(
        self, markdown_content: str, page_num: int, original_filename: str, file_uuid: str
    ) -> List[Dict[str, Any]]:
        """
        Parse OCR markdown output into structured JSON elements.

        Args:
            markdown_content: Markdown text from OCR
            page_num: Current page number
            original_filename: Original file name
            file_uuid: Unique file identifier

        Returns:
            List of parsed JSON elements
        """
        if not markdown_content or not markdown_content.strip():
            logger.warning(f"Empty content for page {page_num}")
            return []

        elements = []
        matches = self.BLOCK_PATTERN.findall(markdown_content)

        # Some DeepSeek-OCR versions return clean Markdown without grounding
        # markers. Keep that content instead of silently producing zero chunks.
        if not matches:
            return [
                {
                    "file_name": f"{original_filename}_{file_uuid}",
                    "page": page_num,
                    "region_order": 1,
                    "region_type": "text",
                    "content": markdown_content.strip(),
                    "original_filename": original_filename,
                    "metadata": {
                        "page": page_num,
                        "region_type": "text",
                        "coordinates": [],
                    },
                    "saved_link": None,
                }
            ]

        for i, match in enumerate(matches):
            region_type = match[0].strip().lower()
            coordinates_str = match[1].strip()
            content = match[2].strip()

            try:
                coords_list = json.loads(coordinates_str)
                coordinates = coords_list[0] if isinstance(coords_list[0], list) else coords_list
            except (json.JSONDecodeError, IndexError, TypeError):
                logger.warning(f"Failed to parse coordinates: {coordinates_str}")
                coordinates = []

            # Newlines carry Markdown hierarchy, lists, tables and formulas.
            content = content.strip()

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

        logger.info(f"Parsed {len(elements)} elements from page {page_num}")
        return elements


class ImageExtractor:
    """
    Extracts and saves image regions from document pages.
    Single Responsibility: Only handles image extraction.
    """

    def extract_images_from_elements(
        self, elements: List[Dict[str, Any]], page_image: Any, output_dir: str, image_counter: int
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Extract image regions from page and save them.

        Args:
            elements: List of page elements
            page_image: PIL Image of the page
            output_dir: Directory to save images
            image_counter: Current image counter

        Returns:
            Updated elements and new image counter
        """
        width, height = page_image.size

        for element in elements:
            if element["region_type"] in {"image", "figure", "chart", "table", "formula"}:
                image_counter += 1
                image_filename = f"image_{image_counter}.jpg"
                saved_link_path = os.path.join(output_dir, image_filename)

                coords = element["metadata"]["coordinates"]
                if len(coords) == 4:
                    x1_norm, y1_norm, x2_norm, y2_norm = coords
                    x1 = int(x1_norm / 1000 * width)
                    y1 = int(y1_norm / 1000 * height)
                    x2 = int(x2_norm / 1000 * width)
                    y2 = int(y2_norm / 1000 * height)

                    try:
                        cropped_image = page_image.crop((x1, y1, x2, y2))
                        cropped_image.save(saved_link_path, "JPEG", quality=90)

                        element["saved_link"] = str(saved_link_path)
                        element["content"] = (
                            element.get("content")
                            or f"Nội dung trực quan image_{image_counter} ở trang {element['page']}."
                        )
                        logger.debug(f"Extracted image: {image_filename}")
                    except Exception as e:
                        logger.error(f"Failed to extract image: {e}")
                else:
                    logger.warning(f"Invalid coordinates for image: {coords}")

        return elements, image_counter


class ResultSaver:
    """
    Saves OCR results to JSON and Markdown files.
    Single Responsibility: Only handles result persistence.
    """

    @staticmethod
    def save(json_objects: List[Dict[str, Any]], output_dir: str, base_filename: str) -> Tuple[str, str]:
        """
        Save OCR results to JSON and Markdown files.

        Args:
            json_objects: List of JSON elements
            output_dir: Output directory
            base_filename: Base filename without extension

        Returns:
            Tuple of (json_path, markdown_path)
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Create markdown content
        final_md_blocks = [obj["content"] for obj in json_objects]
        final_md_output = "\n\n---\n\n".join(final_md_blocks)

        # Save JSON
        json_path = os.path.join(output_dir, f"{base_filename}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"elements": json_objects}, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved JSON: {json_path}")

        # Save Markdown
        md_path = os.path.join(output_dir, f"{base_filename}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(final_md_output)
        logger.info(f"Saved Markdown: {md_path}")

        return json_path, md_path


class OCRService:
    """
    Main OCR service orchestrating the OCR pipeline.
    Follows Dependency Inversion Principle - depends on abstractions (IOCRProcessor).
    Open/Closed Principle - open for extension (can add new processors), closed for modification.
    """

    def __init__(
        self,
        ocr_processor: IOCRProcessor,
        parser: MarkdownParser,
        image_extractor: ImageExtractor,
        result_saver: ResultSaver,
    ):
        self.ocr_processor = ocr_processor
        self.parser = parser
        self.image_extractor = image_extractor
        self.result_saver = result_saver
        logger.info("OCRService initialized")

    def process_document(self, file_path: str, output_dir: str) -> Dict[str, Any]:
        """
        Process a document (PDF or image) and extract text and images.

        Args:
            file_path: Path to input document
            output_dir: Directory to save outputs

        Returns:
            Dictionary with processing results
        """
        logger.info(f"Starting OCR processing: {file_path}")

        base_filename = Path(file_path).stem
        file_uuid = uuid.uuid4().hex

        # Determine if PDF or image
        if file_path.lower().endswith(".pdf"):
            return self._process_pdf(file_path, output_dir, base_filename, file_uuid)
        else:
            return self._process_image(file_path, output_dir, base_filename, file_uuid)

    def _process_pdf(self, pdf_path: str, output_dir: str, base_filename: str, file_uuid: str) -> Dict[str, Any]:
        """Process PDF document."""
        from pdf2image import convert_from_path

        try:
            page_images = convert_from_path(pdf_path, dpi=settings.OCR_DPI)
            logger.info(f"Converted PDF to {len(page_images)} images")
        except Exception as e:
            logger.error(f"Error converting PDF: {e}")
            raise

        all_json_objects = []
        image_counter = 0
        image_output_dir = os.path.join(output_dir, "images")
        os.makedirs(image_output_dir, exist_ok=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            for page_num, page_image in enumerate(page_images):
                actual_page_num = page_num + 1

                # Skip first N pages if configured
                if actual_page_num <= settings.SKIP_FIRST_N_PAGES:
                    logger.info(f"Skipping page {actual_page_num}")
                    continue

                logger.info(f"Processing page {actual_page_num}/{len(page_images)}")

                # Save temp image
                temp_image_path = os.path.join(temp_dir, f"page_{actual_page_num}.png")
                page_image.save(temp_image_path, "PNG")

                # Run OCR
                page_markdown = self.ocr_processor.process_image(temp_image_path, temp_dir)

                # Parse markdown
                page_elements = self.parser.parse(page_markdown, actual_page_num, base_filename, file_uuid)

                # Extract images
                page_elements, image_counter = self.image_extractor.extract_images_from_elements(
                    page_elements, page_image, image_output_dir, image_counter
                )

                all_json_objects.extend(page_elements)

        # Save results
        json_path, md_path = self.result_saver.save(all_json_objects, output_dir, base_filename)

        # Cleanup
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
        gc.collect()

        logger.info(f"OCR processing completed: {pdf_path}")

        return {
            "json_path": json_path,
            "markdown_path": md_path,
            "total_pages": max(0, len(page_images) - settings.SKIP_FIRST_N_PAGES),
            "elements_count": len(all_json_objects),
            "output_dir": output_dir,
        }

    def _process_image(self, image_path: str, output_dir: str, base_filename: str, file_uuid: str) -> Dict[str, Any]:
        """Process single image file."""
        from PIL import Image

        logger.info(f"Processing single image: {image_path}")

        page_image = Image.open(image_path)
        image_output_dir = os.path.join(output_dir, "images")
        os.makedirs(image_output_dir, exist_ok=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            # Run OCR
            page_markdown = self.ocr_processor.process_image(image_path, temp_dir)

            # Parse markdown
            page_elements = self.parser.parse(page_markdown, 1, base_filename, file_uuid)  # Single page

            # Extract images
            page_elements, _ = self.image_extractor.extract_images_from_elements(
                page_elements, page_image, image_output_dir, 0
            )

        # Save results
        json_path, md_path = self.result_saver.save(page_elements, output_dir, base_filename)

        logger.info(f"Image processing completed: {image_path}")

        return {
            "json_path": json_path,
            "markdown_path": md_path,
            "total_pages": 1,
            "elements_count": len(page_elements),
            "output_dir": output_dir,
        }


def create_ocr_service() -> OCRService:
    """
    Factory function to create OCRService with all dependencies.
    Dependency Injection pattern.
    """
    import torch
    from transformers import AutoModel, AutoTokenizer

    logger.info(f"Loading DeepSeek-OCR model: {settings.OCR_MODEL_NAME}")

    tokenizer = AutoTokenizer.from_pretrained(settings.OCR_MODEL_NAME, trust_remote_code=True)

    model = (
        AutoModel.from_pretrained(
            settings.OCR_MODEL_NAME,
            trust_remote_code=True,
            use_safetensors=True,
        )
        .to(settings.DEVICE)
        .eval()
    )

    if settings.USE_BFLOAT16:
        model = model.to(torch.bfloat16)
        logger.info("Model converted to bfloat16")

    logger.info("DeepSeek-OCR model loaded successfully")

    # Create dependencies
    ocr_processor = DeepSeekOCRProcessor(model, tokenizer)
    parser = MarkdownParser()
    image_extractor = ImageExtractor()
    result_saver = ResultSaver()

    # Create and return service
    return OCRService(ocr_processor, parser, image_extractor, result_saver)
