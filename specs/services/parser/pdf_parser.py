import logging
from pathlib import Path
from typing import Optional
import pdfplumber
import pandas as pd
import re

from specs.services.ai.ai_helper import AIHelper

logger = logging.getLogger(__name__)

class PDFParser:
    """
    Парсер PDF-файлов с табличными данными (например, коммерческих предложений),
    с возможностью постобработки и нормализации через AIHelper.
    """

    def __init__(self, path: str, ai_helper: Optional[AIHelper] = None):
        self.input_file = Path(path)
        self.ai = ai_helper or AIHelper()

        if not self.input_file.exists():
            raise FileNotFoundError(f"PDF file not found: {self.input_file}")

    def _extract_text_lines(self) -> list[str]:
        """
        Извлекает все строки текста из PDF.
        """
        lines = []
        with pdfplumber.open(self.input_file) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if not text:
                    continue
                page_lines = [line.strip() for line in text.split("\n") if line.strip()]
                lines.extend(page_lines)
                logger.debug(f"Page {page_num}: {len(page_lines)} lines extracted")
        return lines

    def _group_table_rows(self, lines: list[str]) -> list[str]:
        """
        Группирует строки таблицы, объединяя многострочные описания в одну запись.
        Эвристика: строка начинается с числа — это начало новой позиции.
        """
        rows = []
        buffer = ""

        for line in lines:
            # начало новой строки таблицы
            if re.match(r"^\d+\s", line):
                if buffer:
                    rows.append(buffer.strip())
                buffer = line
            else:
                buffer += " " + line.strip()
        if buffer:
            rows.append(buffer.strip())

        logger.info(f"Grouped into {len(rows)} table rows")
        return rows

    def _parse_rows_to_df(self, rows: list[str]) -> pd.DataFrame:
        """
        Преобразует строки в DataFrame с базовой структурой.
        """
        data = []
        pattern = re.compile(
            r"^(\d+)\s+(.+?)\s+(\d+)\s+([\d\s,\.]+)\s+([A-Z]+)\s+([\d,\.]+)\s+([\d,\.]+)$"
        )

        for row in rows:
            match = pattern.search(row)
            if match:
                data.append(match.groups())
            else:
                data.append((None, row, None, None, None, None, None))

        df = pd.DataFrame(
            data,
            columns=[
                "№",
                "Наименование",
                "Кол-во",
                "Цена за шт.",
                "Валюта",
                "Скидка, %",
                "Сумма без НДС",
            ],
        )
        return df

    def parse(self) -> Optional[str]:
        """
        Основной метод: извлекает таблицу из PDF, нормализует и возвращает CSV.
        """
        lines = self._extract_text_lines()

        if not lines:
            logger.warning("PDF is empty or unreadable")
            return None

        table_lines = self._group_table_rows(lines)
        if not table_lines:
            logger.warning("No table-like rows found in PDF")
            return None

        df = self._parse_rows_to_df(table_lines)

        # очистка
        df = df.dropna(how="all")
        df = df[df["Наименование"].notna()]

        csv_raw = df.to_csv(index=False, sep=";", encoding="utf-8-sig")

        # нормализация через GPT (если нужно)
        normalized_csv = self.ai.normalize_table_from_csv(csv_raw)

        return normalized_csv
