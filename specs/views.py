import os

from django.conf import settings
from django.shortcuts import render

from specs.services.parser.docx_parser import DocxParser
from specs.services.processing import consolidator
from specs.services.processing.file_service import save_final_dataframe


def index(request):
    message = None
    result_file_url = None

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
            # 2. запускаем парсер
            parser = DocxParser(file_path)
            tables = parser.parse_tables()

            if not tables:
                tables = parser.parse_images_with_gpt()

            # 3. объединяем и сохраняем результат
            df = consolidator.merge_and_consolidate(tables)

            output_dir = os.path.join(settings.MEDIA_ROOT, "output")
            os.makedirs(output_dir, exist_ok=True)

            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_path = os.path.join(output_dir, f"{base_name}_consolidated.csv")
            save_final_dataframe(df, output_path)

            # 4. готовим ссылку для скачивания
            result_file_url = os.path.relpath(output_path, settings.MEDIA_ROOT)
            result_file_url = settings.MEDIA_URL + result_file_url.replace("\\", "/")

            message = f"Файл {uploaded_file.name} успешно обработан!"

        except Exception as e:
            message = f"Ошибка при обработке: {str(e)}"

    return render(
        request,
        'specs/index.html',
        {
            'title': 'SmartSpec',
            'message': message,
            'result_file_url': result_file_url
        }
    )
