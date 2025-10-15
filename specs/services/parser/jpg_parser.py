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

        # Промпт, используемый для каждой части
        self.question = """
Ты видишь часть таблицы. Извлеки ВСЕ строки именно из этой части.
Формат ответа строго markdown-таблица:

| Название | Количество |
|----------|-------------|
| ...      | ...         |

❗ Правила:
- Никакого текста до или после таблицы
- В колонке 'Количество' только число (без 'шт.')
"""

    def parse(self) -> str:
        """
        Основной метод: обрабатывает изображение (режет -> GPT -> парсинг -> CSV).
        """
        logger.info(f"Extracting table from image: {self.input_file}")

        image = Image.open(self.input_file).convert("RGB")
        width, height = image.size

        # Режем на 3 части
        parts = [
            image.crop((0, 0, width, height // 3)),
            image.crop((0, height // 3, width, 2 * height // 3)),
            image.crop((0, 2 * height // 3, width, height)),
        ]

        all_rows = []

        image_64 = self._encode_image(image)
        response_text = self.ai.extract_table_from_image_b64(image_b64=image_64)

        for part in parts:
            img_b64 = self._encode_image(part)

            response_text = self.ai.send_image_and_get_text(
                prompt=self.question,
                image_b64=img_b64
            )
            rows = self._parse_markdown_table(response_text)
            if rows:
                all_rows.extend(rows)

        if not all_rows:
            logger.warning("No data extracted from any image fragment.")
            return ""

        # Преобразуем в DataFrame
        df = pd.DataFrame(all_rows, columns=["Название", "Количество"])
        df["Количество"] = pd.to_numeric(df["Количество"], errors="coerce").fillna(0).astype(int)
        df = df.groupby("Название", as_index=False)["Количество"].sum()

        # Возвращаем CSV (как у других парсеров)
        return df.to_csv(index=False, sep=";", encoding="utf-8-sig")

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