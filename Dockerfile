# Базовый образ с Python
FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    imagemagick \
    libmagickwand-dev \
    && rm -rf /var/lib/apt/lists/*

# Настраиваем рабочую директорию
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . .

# Настраиваем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Запуск через gunicorn
CMD ["gunicorn", "smartspec.wsgi", "--bind", "0.0.0.0:8080"]