import pandas as pd
import os

def save_final_dataframe(df: pd.DataFrame, output_path: str):
    """
    Сохраняет итоговую таблицу.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, sep=";", index=False, encoding="utf-8")
    return output_path

def save_final_dataframe_xlsx(df: pd.DataFrame, output_path: str):
    """
    Сохраняет итоговую таблицу в Excel (.xlsx).
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_excel(output_path, index=False)
    return output_path