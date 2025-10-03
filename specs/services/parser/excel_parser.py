import pandas as pd
from pathlib import Path

from specs.services.ai.ai_helper import AIHelper

ai = AIHelper()

def find_header_row(df):
    """
    Ищем строку, которая похожа на заголовок.
    Эвристика: содержит хотя бы 2 непустых ячейки и НЕ состоит только из чисел
    """
    for i, row in df.iterrows():
        filled = row.astype(str).str.strip()
        non_empty = filled[filled != ""]
        if len(non_empty) >= 2 and not all(s.isdigit() for s in non_empty):
            return i
    return 0  # fallback — первая строка

def process_sheet(sheet_name):
    df = pd.read_excel(INPUT_FILE, sheet_name=sheet_name, header=None, dtype=str)
    df = df.fillna("").map(str)

    # Если весь лист пустой — пропускаем
    if df.replace("", pd.NA).dropna(how="all").empty:
        print(f"⚠️ Sheet '{sheet_name}' is empty, skipping")
        return

    header_idx = find_header_row(df)

    # Если заголовок вне диапазона — пропустить
    if header_idx >= len(df):
        print(f"⚠️ No valid header found in '{sheet_name}', skipping")
        return

    header = df.iloc[header_idx]

    # Если после заголовка нет строк — тоже пропустить
    if header_idx + 1 >= len(df):
        print(f"⚠️ No data under header in '{sheet_name}', skipping")
        return

    table = df.iloc[header_idx+1:].copy()
    table.columns = header

    table = table[~table.apply(lambda r: all(v.strip() == "" for v in r), axis=1)]

    # --- ПОСТОБРАБОТКА ---

    # Удаляем полностью пустые строки
    table = table.dropna(how="all")
    table = table[~table.apply(lambda r: all(v.strip() == "" for v in r), axis=1)]

    # ✅ Удаляем строки, где только одна заполненная ячейка
    table = table[table.apply(lambda r: sum(str(v).strip() != "" for v in r) >= 2, axis=1)]

    # Удаляем полностью пустые столбцы (все NaN или все "")
    table = table.dropna(axis=1, how="all")
    table = table.loc[:, ~(table.apply(lambda col: col.astype(str).str.strip().eq("").all()))]

    # ✅ Удаляем столбцы, где 5 и более пустых ячеек
    table = table.loc[:, table.apply(lambda col: sum(str(v).strip() == "" for v in col) < 5)]

    # ✅ Удаляем строки, где 3 и более пустых ячеек
    table = table[table.apply(lambda r: sum(str(v).strip() == "" for v in r) < 3, axis=1)]

    # --- ПРЕОБРАЗОВАНИЕ В CSV-ТЕКСТ ---
    csv_raw = table.to_csv(index=False, sep=";", encoding="utf-8-sig")

    # --- GPT НОРМАЛИЗАЦИЯ ---
    normalized_csv = ai.normalize_table_from_csv(csv_raw)  # <<< ai = AIHelper()

    # --- СОХРАНЕНИЕ ИТОГОВОГО CSV ---
    out_path = OUTPUT_DIR / f"{INPUT_FILE.stem}__{sheet_name}__normalized.csv"
    with open(out_path, "w", encoding="utf-8-sig") as f:
        f.write(normalized_csv)

    print(f"✅ GPT-normalized saved: {out_path}")

INPUT_FILE = Path("../../../data/xlsx/005_Спецификация инструмент для АПТ_001.xlsx")
# INPUT_FILE = Path("../data/xlsx/36528 зз для 5565 ред. 10.01.2024.xls")
# INPUT_FILE = Path("../data/xlsx/36881 ЗЦ оснастка сандвик.xlsx")
# INPUT_FILE = Path("../data/xlsx/36897 ЗЦ оснастка для ВФ3.xlsx")
# INPUT_FILE = Path("../data/xlsx/39236 оснастка для грс.xlsx")
# INPUT_FILE = Path("../data/xlsx/40323 зц на инструмент ТФ5 7854.xlsx")
# INPUT_FILE = Path("../data/xlsx/41318 ЗЦ Токарный с КШ 6202.xlsx")
# INPUT_FILE = Path("../data/xlsx/test.xlsx")
# INPUT_FILE = Path("../data/xlsx/Заявка_5565_02.07.25 .xlsx")
OUTPUT_DIR = Path("../../../data_output/xlsx")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
# def main():
#     xls = pd.ExcelFile(INPUT_FILE)
#     for sheet in xls.sheet_names:
#         process_sheet(sheet)
#
# if __name__ == "__main__":
#     main()
