import pandas as pd
import os

def save_final_dataframe(df: pd.DataFrame, output_path: str):
    """
    Сохраняет итоговую таблицу.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, sep=";", index=False, encoding="utf-8")
    return output_path
