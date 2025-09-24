from parser.docx_parser import DocxParser
from processing.consolidator import TableConsolidator

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
consolidator = TableConsolidator()
df = consolidator.load_and_merge(csv_files)
df = consolidator.normalize_text(df)
df = consolidator.consolidate(df)

# сохраняем результат
output_path = consolidator.save_to_csv(df, "output/consolidated.csv")
print(f"Файл с объединёнными таблицами: {output_path}")