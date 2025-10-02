import pandas as pd
from io import StringIO

class ConsolidatorV2:
    """
    Новая версия консолидатора:
    - Работает напрямую со списком CSV-строк (без промежуточных файлов)
    - Удаляет повторяющиеся заголовки
    - Консолидирует дубли по ключевым полям
    - Сортирует по № как числовому
    - Сбрасывает индекс и возвращает DataFrame в фиксированном виде
    """

    HEADERS = {
        "number": "№",
        "designation": "Обозначение",
        "name": "Наименование",
        "unit": "Ед. изм.",
        "quantity": "Требуемое кол-во, в ед. изм.",
        "tech_spec": "Техническое задание"
    }

    KEY_COLUMNS = [
        HEADERS["designation"],
        HEADERS["name"],
        HEADERS["unit"],
    ]

    def _load_tables(self, csv_tables: list[str]) -> pd.DataFrame:
        """
        Загружает CSV-строки в общий DataFrame.
        """
        dfs = []
        for csv_text in csv_tables:
            df = pd.read_csv(StringIO(csv_text), sep=";")
            dfs.append(df)

        combined = pd.concat(dfs, ignore_index=True)

        # Удаляем строки, которые полностью равны заголовку
        header_row = list(self.HEADERS.values())
        combined = combined[~(combined.astype(str).eq(header_row).all(axis=1))]

        return combined

    def _normalize_text(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Чистит текст в строковых колонках.
        """
        for col in df.columns:
            if col not in [self.HEADERS["number"], self.HEADERS["quantity"]]:
                df[col] = df[col].astype(str).str.strip()
        return df

    def _consolidate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Группирует по ключевым колонкам и суммирует количество.
        """
        df[self.HEADERS["number"]] = pd.to_numeric(df[self.HEADERS["number"]], errors="coerce")
        df[self.HEADERS["quantity"]] = pd.to_numeric(
            df[self.HEADERS["quantity"]], errors="coerce"
        ).fillna(0)

        consolidated = (
            df.groupby(self.KEY_COLUMNS, as_index=False)
            .agg({
                self.HEADERS["number"]: "first",  # берем первый номер как референс
                self.HEADERS["quantity"]: "sum",
                self.HEADERS["tech_spec"]: lambda x: " | ".join(
                    sorted(set(map(str, x)))
                ),
            })
        )

        # Сортировка по номеру
        consolidated = consolidated.sort_values(by=self.HEADERS["number"], ascending=True, na_position="last")

        # Переставляем колонки в нужном порядке
        ordered_columns = [
            self.HEADERS["number"],
            self.HEADERS["designation"],
            self.HEADERS["name"],
            self.HEADERS["unit"],
            self.HEADERS["quantity"],
            self.HEADERS["tech_spec"],
        ]
        consolidated = consolidated[ordered_columns]

        return consolidated.reset_index(drop=True)

    def merge_and_consolidate(self, csv_tables: list[str]) -> pd.DataFrame:
        """
        Основной метод для объединения всех таблиц.
        """
        df = self._load_tables(csv_tables)
        df = self._normalize_text(df)
        df = self._consolidate(df)

        # Убираем NaN после всех трансформаций
        df = df.fillna("")
        return df
