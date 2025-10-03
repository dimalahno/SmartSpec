import os

from django.conf import settings
from django.shortcuts import render

from specs.services.parser.docx_parser import DocxParser
from specs.services.parser.excel_parser import ExcelParser
from specs.services.processing.consolidator_v2 import ConsolidatorV2
from specs.services.processing.file_service import save_final_dataframe_xlsx


def index(request):
    uploaded_file = None
    message = None
    result_file_url = None
    table_html = None

    if request.method == 'POST' and request.FILES.get('specfile'):
        uploaded_file = request.FILES['specfile']

        # 1. сохраняем загруженный файл
        upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, uploaded_file.name)
        with open(file_path, "wb+") as dest:
            for chunk in uploaded_file.chunks():
                dest.write(chunk)

        try:
            # 2. Определяем тип файла и парсим
            ext = os.path.splitext(file_path)[1].lower()

            if ext == ".docx":
                parser = DocxParser(file_path)
                csv_tables = parser.parse_all()

            elif ext in [".xls", ".xlsx"]:
                parser = ExcelParser(file_path)
                merged_csv = parser.parse_all_sheets()
                csv_tables = [merged_csv] if merged_csv else []

            else:
                raise ValueError(f"Unsupported file type: {ext}")

            # 3. объединяем и сохраняем результат
            consolidator = ConsolidatorV2()
            df = consolidator.merge_and_consolidate(csv_tables)

            # ✅ Генерируем HTML-таблицу
            table_html = df.to_html(classes="table table-striped table-bordered", index=False)

            output_dir = os.path.join(settings.MEDIA_ROOT, "output")
            os.makedirs(output_dir, exist_ok=True)

            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_path = os.path.join(output_dir, f"{base_name}_consolidated.xlsx")
            save_final_dataframe_xlsx(df, output_path)

            # 4. готовим ссылку для скачивания
            result_file_url = os.path.relpath(output_path, settings.MEDIA_ROOT)
            result_file_url = settings.MEDIA_URL + result_file_url.replace("\\", "/")

            message = f"Файл {uploaded_file.name} успешно обработан!"

        except Exception as e:
            message = f"Ошибка при обработке: {str(e)}"

    return render(request, 'specs/index.html', {
        'title': 'SmartSpec',
        'message': message,
        'result_file_url': result_file_url,
        'table_html': table_html,
        'uploaded_filename': uploaded_file.name if request.FILES.get('specfile') else None
    })
