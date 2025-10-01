# Структура проект
# SmartSpec — Django skeleton

This is a minimal Django project skeleton to bootstrap the SmartSpec web service (HTML pages).

## Quick start

1. Create virtualenv and activate it

Linux / macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv venv
venv\\Scripts\\Activate.ps1
```

2. Install required packages

```bash
pip install -r requirements.txt
```

3. Run migrations and start development server

```bash
python manage.py migrate
python manage.py runserver
```

4. Установить ImageMagick 
(Windows installer: https://imagemagick.org/script/download.php#windows).
Настройка системного окружения PATH вручную
Win+R → sysdm.cpl → вкладка «Дополнительно» → «Переменные среды».
В «Системные переменные» найдите Path, нажмите «Изменить».
Добавьте путь до папки с magick.exe, например:
C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\
Нажмите OK, закройте все окна, перезагрузите компьютер.


Open http://127.0.0.1:8000/ in your browser — you should see the SmartSpec welcome page.

## Notes
- Uses SQLite for quick local development (`db.sqlite3`).
- The `specs/services/` package contains placeholders for your existing parser/processing/exporter/ai/utils modules — keep them pure Python (no Django) so they remain reusable.
- Replace `SECRET_KEY` in `smartspec/settings.py` for production and set `DEBUG = False`.
