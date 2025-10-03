import re
from pathlib import Path
from specs.services.ai.ai_helper import AIHelper


class TxtParser:
    """
    Простой TXT-парсер:
    1) Извлекает строки
    2) Пытается преобразовать в таблицы (по разделителям ; , \t | пробелы)
    3) Прогоняет через GPT для нормализации
    """

    def __init__(self, path: str, ai_helper: AIHelper = None):
        self.path = Path(path)
        self.ai = ai_helper or AIHelper()

    def extract_lines(self) -> list[str]:
        with open(self.path, "r", encoding="utf-8", errors="ignore") as f:
            return [line.rstrip() for line in f if line.strip()]

    def split_into_rows(self, lines: list[str]) -> list[list[str]]:
        rows = []
        for line in lines:
            # пытаемся угадать разделитель
            if ";" in line:
                parts = line.split(";")
            elif "," in line:
                parts = line.split(",")
            elif "\t" in line:
                parts = line.split("\t")
            elif "|" in line:
                parts = line.split("|")
            else:
                # последовательность пробелов
                parts = re.split(r"\s{2,}", line)
            rows.append([p.strip() for p in parts])
        return rows

    def normalize(self) -> str:
        """
        Возвращает одну CSV-таблицу (строка) после GPT-нормализации
        """
        lines = self.extract_lines()
        if not lines:
            return ""

        raw_rows = self.split_into_rows(lines)

        # превращаем в CSV-текст
        csv_text = "\n".join([";".join(row) for row in raw_rows])

        # нормализуем через GPT
        normalized_csv = self.ai.normalize_table_from_csv(csv_text)
        return normalized_csv
