from specs.services.parser.docx_parser import DocxParser
from specs.services.processing import consolidator
from specs.services.processing import load_and_merge, normalize_text, save_to_csv

# docx_file = '../data/docx/test_small.docx'
docx_file = '../data/docx/test.docx'
docx_file_img = '../data/docx/инструмент для токарного станка.docx'

parser = DocxParser(docx_file)

# 1. Сначала пробуем таблицы
tables = parser.parse_tables()

# 2. Если таблиц нет или они пустые → используем GPT для картинок
if not tables:
    tables = parser.parse_images_with_gpt()

# 3. Сохраняем все результаты в CSV
csv_files = parser.save_results_to_csv(tables)

# объединяем и убираем дубли
df = load_and_merge(csv_files)
df = normalize_text(df)
df = consolidator.consolidate(df)

# сохраняем результат
output_path = save_to_csv(df, "../data_output/doc/consolidated.csv")
print(f"Файл с объединёнными таблицами: {output_path}")