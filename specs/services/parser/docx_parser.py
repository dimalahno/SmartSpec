import os
from docx import Document
from specs.services.ai.ai_helper import AIHelper
from specs.services.processing import consolidator
from specs.services.processing.file_service import save_final_dataframe
from specs.services.utils.emf_converter import emf_to_png


class DocxParser:
    def __init__(self, path):
        self.path = path
        self.doc = Document(path)
        self.ai = AIHelper()

    def parse_tables(self):
        """
        Извлекает текстовые таблицы из docx и приводит их к шаблону (CSV).
        """
        results = []
        for table in self.doc.tables:
            rows = []
            for row in table.rows:
                rows.append([cell.text.strip() for cell in row.cells])
            # нормализация через GPT
            csv_table = self.ai.normalize_table_from_text(rows)
            results.append(csv_table)
        return results

    def extract_images(self, output_dir="extracted_images"):
        """
        Извлекает все изображения из docx документа и сохраняет их в указанную директорию.
        Автоматически конвертирует EMF файлы в PNG формат.

        Args:
            output_dir (str): Путь к директории для сохранения изображений. По умолчанию "extracted_images"

        Returns:
            list: Список путей к сохраненным изображениям
        """

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        images = []
        rels = self.doc.part._rels
        for rel in rels:
            rel = rels[rel]
            if "image" in rel.target_ref:
                img = rel.target_part.blob
                filename = os.path.join(output_dir, os.path.basename(rel.target_ref))
                with open(filename, "wb") as f:
                    f.write(img)

                if filename.lower().endswith(".emf"):
                    filename = emf_to_png(filename, output_dir)

                images.append(filename)
        return images


    def parse_images_with_gpt(self, output_dir="extracted_images"):
        """
        Извлекает таблицы с картинок через GPT и приводит их к шаблону (CSV).
        """
        images = self.extract_images(output_dir)
        results = []
        for img in images:
            table_csv = self.ai.extract_table_from_image(img)
            results.append(table_csv)
        return results


    def save_results_to_csv(self, results, output_dir="output"):
        """
        Сохраняет список CSV-таблиц в отдельные файлы.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        base_name = os.path.splitext(os.path.basename(self.path))[0]
        saved_files = []

        for i, csv_table in enumerate(results, start=1):
            output_path = os.path.join(output_dir, f"{base_name}_table_{i}.csv")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(csv_table.strip())
            saved_files.append(output_path)

        return saved_files

def main():
    # docx_file = '../../../data/docx/test_small.docx'
    # docx_file = '../../../data/docx/33290 Оснастка Авиастар.docx'
    docx_file = '../../../data/docx/инструмент для токарного станка.docx'
    # docx_file = '../../../data/docx/test.docx'

    parser = DocxParser(docx_file)

    # 1. Сначала пробуем таблицы
    tables = parser.parse_tables()

    # 2. Если таблиц нет → GPT по картинкам
    if not tables:
        tables = parser.parse_images_with_gpt()

    # 3. Новый пайплайн: сразу обрабатываем внутри consolidator
    df = consolidator.merge_and_consolidate(tables)

    # 4. Сохраняем результат
    base_name = os.path.splitext(os.path.basename(docx_file))[0]  # например "test_small"
    output_path = save_final_dataframe(df, f"../../../data_output/doc/{base_name}_consolidated.csv")

    print(f"Файл с объединёнными таблицами: {output_path}")

# if __name__ == "__main__":
#     main()