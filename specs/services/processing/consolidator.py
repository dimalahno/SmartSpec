import pandas as pd
from io import StringIO

KEY_COLUMNS = ["Обозначение", "Наименование", "Ед. изм."]

def merge_csv_strings(csv_strings: list[str]) -> pd.DataFrame:
    """
    Преобразует список CSV-строк в единый DataFrame.
    """
    dfs = [pd.read_csv(StringIO(csv), sep=";") for csv in csv_strings]
    return pd.concat(dfs, ignore_index=True)


def normalize_text(df: pd.DataFrame) -> pd.DataFrame:
    """
    Чистит текстовые поля (убирает пробелы).
    """
    for col in df.columns:
        if col not in ["№", "Требуемое кол-во, в ед. изм."]:
            df[col] = df[col].astype(str).str.strip()
    return df


def consolidate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Объединяет дубли: по ключевым полям суммирует количество.
    """
    df["Требуемое кол-во, в ед. изм."] = pd.to_numeric(
        df["Требуемое кол-во, в ед. изм."], errors="coerce"
    ).fillna(0)

    consolidated = (
        df.groupby(KEY_COLUMNS, as_index=False)
        .agg({
            "№": "first",
            "Требуемое кол-во, в ед. изм.": "sum",
            "Техническое задание": lambda x: " | ".join(set(map(str, x)))
        })
    )

    # Фиксируем порядок колонок
    final_columns = ["№"] + KEY_COLUMNS + ["Требуемое кол-во, в ед. изм.", "Техническое задание"]
    consolidated = consolidated[final_columns]

    # Сортируем по № (как числовому, если возможно)
    consolidated["№"] = pd.to_numeric(consolidated["№"], errors="ignore")
    consolidated = consolidated.sort_values("№", ignore_index=True)

    return consolidated



def merge_and_consolidate(csv_strings: list[str]) -> pd.DataFrame:
    """
    Финальный пайплайн: CSV-строки → DataFrame → очистка → консолидация
    """
    df = merge_csv_strings(csv_strings)
    df = normalize_text(df)
    # df = consolidate(df)
    return df
