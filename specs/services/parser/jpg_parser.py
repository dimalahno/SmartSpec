import base64
import logging
from io import BytesIO
from pathlib import Path
from typing import Optional

import pandas as pd
from PIL import Image

from specs.services.ai.ai_helper import AIHelper


logger = logging.getLogger(__name__)

class JpgParser:
    """
    Парсер JPG/JPEG изображений:
    - открытие изображения
    - разрезание на части
    - отправка каждой части в GPT через AIHelper
    - парсинг ответа (markdown-таблица)
    - сбор и возврат CSV
    """

    def __init__(self, path: str, ai_helper: Optional[AIHelper] = None):
        self.input_file = Path(path)
        self.ai = ai_helper or AIHelper()

        if not self.input_file.exists():
            raise FileNotFoundError(f"JPG/JPEG file not found: {self.input_file}")

        if self.input_file.suffix.lower() not in (".jpg", ".jpeg"):
            raise ValueError(f"Unsupported image type: {self.input_file.suffix}")

    def parse(self) -> str:
        """
        Основной метод: обрабатывает изображение (режет -> GPT -> парсинг -> CSV).
        """
        logger.info(f"Extracting table from image: {self.input_file}")

        image = Image.open(self.input_file).convert("RGB")

        image_64 = self._encode_image(image)
        response_text = self.ai.extract_table_from_image_b64(image_b64=image_64)
        return response_text

    # --- Внутренние методы ---

    @staticmethod
    def _encode_image(pil_img) -> str:
        buf = BytesIO()
        pil_img.save(buf, format="JPEG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    @staticmethod
    def _parse_markdown_table(md_text: str):
        lines = [line.strip() for line in md_text.split("\n") if line.strip()]
        rows = []
        for line in lines:
            if line.startswith("|") and "|" in line[1:]:
                parts = [p.strip() for p in line.strip("|").split("|")]
                if len(parts) >= 2 and parts[0].lower() != "название":
                    rows.append(parts[:2])
        return rows