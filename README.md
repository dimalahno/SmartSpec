# Структура проект
SmartSpec/
│── app.py                  # точка входа (запуск GUI)
│
│── gui/                    # интерфейс
│   ├── main_window.py      # главное окно (drag & drop, кнопки)
│   ├── file_dialogs.py     # выбор файлов
│   └── dialogs.py          # диалоги (мн. число, дубли, сопоставление колонок)
│
│── parsers/                # парсинг исходных файлов
│   ├── txt_parser.py       # работа с txt
│   ├── pdf_parser.py       # pdf (текстовые)
│   ├── pdf_image_parser.py # pdf с изображениями (OCR + GPT)
│   └── utils.py
│
│── processing/             # обработка данных
│   ├── normalize.py        # pymorphy2 (ед. число и т.п.)
│   ├── duplicates.py       # поиск и объединение дублей
│   ├── consolidation.py    # объединение таблиц с разными столбцами
│   └── distribution.py     # умное/упрощённое распределение по колонкам
│
│── ai/                     # модуль работы с GPT
│   ├── ai_helper.py        # универсальный вызов GPT
│   ├── ocr_parser.py       # OCR изображений (GPT + fallback pytesseract)
│   └── schema_mapper.py    # сопоставление нестандартных колонок к шаблону
│
│── exporter/               
│   └── excel_exporter.py   # запись и форматирование Excel
│
│── data/                   # входящие данные (тестовые)
│── output/                 # результаты (Excel)
│── .env                    # ключи API (OPENAI_API_KEY=...)
│── requirements.txt

# Установка
Установить ImageMagick (Windows installer: https://imagemagick.org/script/download.php#windows).
Настройка PATH вручную
Win+R → sysdm.cpl → вкладка «Дополнительно» → «Переменные среды».
В «Системные переменные» найдите Path, нажмите «Изменить».
Добавьте путь до папки с magick.exe, например:
C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\
Нажмите OK, закройте все окна, перезагрузите компьютер.