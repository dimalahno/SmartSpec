# SmartSpec — каркас проекта на Django

Это минимальный каркас Django-проекта для запуска веб-сервиса **SmartSpec** (HTML-страницы).  
Подходит для быстрого старта и локальной разработки.

---

## Быстрый старт

### 1. Создайте и активируйте виртуальное окружение

**Linux / macOS:**
```
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```
python -m venv venv
venv\Scripts\Activate
```

### 2. Установите зависимости
```
pip install -r requirements.txt
```

### 3. Выполните миграции и запустите сервер разработки
```
python manage.py migrate
python manage.py runserver
```

После запуска откройте в браузере: http://127.0.0.1:8000/

Вы должны увидеть приветственную страницу SmartSpec.

### 4. Установка ImageMagick (для работы с изображениями)

#### Linux / macOS

Установите ImageMagick через пакетный менеджер вашей системы:

**Ubuntu / Debian:**
```
sudo apt update
sudo apt install imagemagick
```

#### MacOS (через Homebrew)
```
brew install imagemagick
```

#### Windows
Скачайте установщик:
https://imagemagick.org/script/download.php#windows
После установки настройте системную переменную PATH вручную.

**Проверьте установку:**
```
magick -version
```
### Настройки окружения

Создайте файл .env в корне проекта и укажите в нём:
```
OPENAI_API_KEY==your-secret-key
```
