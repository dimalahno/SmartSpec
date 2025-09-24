import pandas as pd


class TableConsolidator:
    KEY_COLUMNS = ["Обозначение", "Наименование", "Ед. изм."]

    def load_and_merge(self, csv_files: list[str]) -> pd.DataFrame:
        """
        Загружает все CSV, объединяет их в один DataFrame.
        """
        dfs = [pd.read_csv(f, sep=";") for f in csv_files]
        combined = pd.concat(dfs, ignore_index=True)
        return combined

    def normalize_text(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Чистит текстовые поля (нижний регистр, убирает пробелы).
        """
        for col in df.columns:
            if col not in ["№", "Требуемое кол-во, в ед. изм."]:
                df[col] = df[col].astype(str).str.strip().str.lower()
        return df

    def consolidate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Объединяет дубли: по ключевым полям суммирует количество.
        """
        df["Требуемое кол-во, в ед. изм."] = pd.to_numeric(
            df["Требуемое кол-во, в ед. изм."], errors="coerce"
        ).fillna(0)

        consolidated = (
            df.groupby(self.KEY_COLUMNS, as_index=False)
            .agg({
                "№": "first",  # можно игнорировать или взять первый
                "Требуемое кол-во, в ед. изм.": "sum",
                "Техническое задание": lambda x: " | ".join(set(map(str, x)))
            })
        )
        return consolidated

    def save_to_csv(self, df: pd.DataFrame, output_path: str):
        """
        Сохраняет объединённую таблицу.
        """
        df.to_csv(output_path, sep=";", index=False, encoding="utf-8")
        return output_path
