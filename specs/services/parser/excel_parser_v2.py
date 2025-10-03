import logging

import pandas as pd
from pathlib import Path
from typing import Optional

from specs.services.ai.ai_helper import AIHelper

logger = logging.getLogger(__name__)

class ExcelParserV2:
    """
    Парсер Excel-таблиц с постобработкой и нормализацией через AIHelper.
    """

    def __init__(self, input_file: Path, output_dir: Path, ai_helper: Optional[AIHelper] = None):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.ai = ai_helper or AIHelper()

        if not self.input_file.exists():
            raise FileNotFoundError(f"Excel file not found: {self.input_file}")
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def _find_header_row(self, df: pd.DataFrame) -> int:
        """
        Ищем строку, которая похожа на заголовок.
        Эвристика: содержит >= 2 непустых ячеек и НЕ состоит только из чисел.
        """
        for i, row in df.iterrows():
            filled = row.astype(str).str.strip()
            non_empty = filled[filled != ""]
            if len(non_empty) >= 2 and not all(s.isdigit() for s in non_empty):
                return i
        return 0  # fallback — первая строка

    def parse_sheet(self, sheet_name: str) -> str | None:
        """
        Обрабатывает один лист Excel, нормализует через GPT и сохраняет в CSV.
        Возвращает путь к итоговому файлу или None, если лист пуст/невалиден.
        """
        df = pd.read_excel(self.input_file, sheet_name=sheet_name, header=None, dtype=str)
        df = df.fillna("").map(str)

        # Если весь лист пустой
        if df.replace("", pd.NA).dropna(how="all").empty:
            logger.info(f"Sheet '{sheet_name}' is empty, skipping")
            return None

        header_idx = self._find_header_row(df)
        if header_idx >= len(df):
            logger.info(f"No valid header found in '{sheet_name}', skipping")
            return None

        if header_idx + 1 >= len(df):
            logger.info(f"No data under header in '{sheet_name}', skipping")
            return None

        header = df.iloc[header_idx]
        table = df.iloc[header_idx + 1:].copy()
        table.columns = header

        # --- очистка ---
        table = table.dropna(how="all")
        table = table[~table.apply(lambda r: all(v.strip() == "" for v in r), axis=1)]
        table = table[table.apply(lambda r: sum(str(v).strip() != "" for v in r) >= 2, axis=1)]
        table = table.dropna(axis=1, how="all")
        table = table.loc[:, ~(table.apply(lambda col: col.astype(str).str.strip().eq("").all()))]
        table = table.loc[:, table.apply(lambda col: sum(str(v).strip() == "" for v in col) < 5)]
        table = table[table.apply(lambda r: sum(str(v).strip() == "" for v in r) < 3, axis=1)]

        # --- в CSV ---
        csv_raw = table.to_csv(index=False, sep=";", encoding="utf-8-sig")

        # --- GPT нормализация ---
        normalized_csv = self.ai.normalize_table_from_csv(csv_raw)

        return normalized_csv

    def parse_all_sheets(self) -> Optional[str]:
        """
        Прогоняет все листы Excel, собирает все CSV-строки и объединяет в один общий CSV.
        Если ни один лист не дал результата, возвращает None.
        """
        xls = pd.ExcelFile(self.input_file)
        csv_list = []

        for sheet_name in xls.sheet_names:
            csv_data = self.parse_sheet(sheet_name)
            if csv_data:
                csv_list.append(csv_data)

        if not csv_list:
            return None

        # Берем заголовок из первого CSV
        header, *first_rows = csv_list[0].splitlines()

        # Остальные CSV — берем только строки без заголовка
        rows = first_rows.copy()
        for csv in csv_list[1:]:
            rows.extend(csv.splitlines()[1:])  # пропускаем заголовок

        # Собираем обратно
        return "\n".join([header] + rows)
