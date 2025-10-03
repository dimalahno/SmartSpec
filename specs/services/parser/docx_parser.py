import base64
import logging
import os
from typing import Optional

from docx import Document
from wand.image import Image as WandImage
from specs.services.ai.ai_helper import AIHelper

logger = logging.getLogger(__name__)

class DocxParser:
    def __init__(self, path: str, ai_helper: Optional[AIHelper] = None):
        self.path = path
        self.doc = Document(path)
        self.ai = ai_helper or AIHelper()

    def extract_raw_tables(self) -> list[list[list[str]]]:
        """
        Извлекает все текстовые таблицы из docx без обработки GPT
        """
        results = []
        for table in self.doc.tables:
            rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
            results.append(rows)
        return results

    def extract_images_as_base64(self) -> list[str]:
        """
        Извлекает все изображения из DOCX и возвращает список base64-строк (без префикса)
        EMF конвертируется в PNG в памяти через Wand
        """
        images_b64 = []
        rels = self.doc.part._rels
        for rel in rels:
            rel = rels[rel]
            if "image" not in rel.target_ref.lower():
                continue

            img_bytes = rel.target_part.blob
            ext = os.path.splitext(rel.target_ref)[1].lower()

            # EMF → PNG конвертация in-memory
            if ext == ".emf":
                try:
                    with WandImage(blob=img_bytes, format="emf") as img:
                        img.format = "png"
                        img_bytes = img.make_blob()
                except Exception as e:
                    logger.info(f"[WARNING] Не удалось конвертировать EMF {rel.target_ref}: {e}")
                    continue

            # base64
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
            images_b64.append(img_b64)

        return images_b64

    def normalize_tables(self, raw_tables: list[list[list[str]]]) -> list[str]:
        """
        Прогоняет все текстовые таблицы через GPT для нормализации к CSV
        """
        normalized = []
        for table in raw_tables:
            csv_table = self.ai.normalize_table_from_text(table)
            normalized.append(csv_table)
        return normalized

    def normalize_images(self, b64_images: list[str]) -> list[str]:
        """
        Прогоняет все изображения через GPT для получения CSV
        """
        normalized = []
        for img_b64 in b64_images:
            csv_table = self.ai.extract_table_from_image_b64(img_b64)
            normalized.append(csv_table)
        return normalized

    def parse_all(self) -> list[str]:
        """
        Основной пайплайн:
        1) Пытаемся получить таблицы из текста
        2) Если текстовых таблиц нет — используем изображения
        Возвращает список CSV-таблиц
        """
        raw_tables = self.extract_raw_tables()
        if raw_tables:
            return self.normalize_tables(raw_tables)

        # Если нет текстовых таблиц — пробуем изображения
        images_b64 = self.extract_images_as_base64()
        if not images_b64:
            logger.info("[INFO] Таблицы и изображения не найдены.")
            return []

        return self.normalize_images(images_b64)


# Пример использования
# if __name__ == "__main__":
#     docx_file = '../../../data/docx/инструмент для токарного станка.docx'
#     parser = DocxParserV2(docx_file)
#     csv_tables = parser.parse_all()
#
#     for i, csv in enumerate(csv_tables, 1):
#         logger.info(f"--- Table {i} ---\n{csv}\n")
