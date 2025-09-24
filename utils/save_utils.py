import os

def save_csv(csv_text: str, output_dir="output", file_name="result.csv"):
    """
    Сохраняет CSV-текст в файл.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_path = os.path.join(output_dir, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(csv_text)

    print(f"✅ Файл сохранён: {file_path}")
    return file_path
