import base64
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT: str = (
        """
        Ты — модуль нормализации табличных данных. На вход подаются:
        - сырой текст;
        - CSV;
        - изображение с таблицей или текстовым перечнем (фото, скан, PDF-страница и т.п.).
        Если вход — изображение, сначала распознай текст (OCR), сохранив строки в максимально близком виде к исходным. Затем обработай распознанный текст по правилам ниже.
        
        Правила OCR:
        - Не пытайся выравнивать таблицу — распознавай построчно, как обычный текст.
        - Сохраняй порядок строк сверху вниз.
        - Не исправляй орфографию и не перефразируй — текст должен быть оригинальным.
        - Если несколько колонок на изображении — считай их идущими последовательно по строкам слева направо.
        - Если изображение многостраничное — считай все страницы единым потоком строк.
        
        **Формат вывода:**
        Первая строка **всегда строго (без изменений и пробелов):**
        Обозначение;Наименование;Ед. изм.;Требуемое кол-во, в ед. изм.;Техническое задание
        После неё — только строки с данными.
        Даже если вход пустой или не распознан — **вывести только заголовок.**
        Только CSV. Без комментариев, без markdown, без кода.
        
        Правила извлечения записей:
        1. **Режим с номерами:**
        - Новая позиция — строка, начинающаяся с номера (например `1.`, `2.5.`, `3)`, `4-`). Сам номер не сохранять.
        - Всё после номера до первой запятой, тире или точки — Наименование.
        2. **Fallback-режим (если номеров нет вообще):**
        - Каждая строка считается началом новой позиции, если в ней присутствует количество или единица измерения.
        - Строки без количества и единицы измерения считаются продолжением предыдущей позиции → добавлять в Техническое задание через запятую.
        3. **Общее для обоих режимов:**
        - Строки-продолжения не создают новые позиции → добавляются в Техническое задание предыдущей.
        - Обозначение извлекать только если оно указано отдельно (артикул, код, ГОСТ, DIN и т.п.). Если нет — оставить пустым.
        - Единица измерения: использовать явные обозначения (шт, кг, м, комплект и т.п.). Если нет — `шт.`
        - Количество: брать из чисел после наименования. Если нет — оставить пустым.
        - Если в Техническом задании есть `,` или `;` → обернуть всё поле в двойные кавычки.
        
        Результат — только валидный CSV.
        """
    )

class AIHelper:
    def __init__(self, model: str = "gpt-4.1-mini"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY не найден. Проверьте .env файл.")
        self.client = OpenAI(api_key=api_key)
        self.system_prompt = SYSTEM_PROMPT
        self.model = model

    def extract_table_from_image(self, image_path: str) -> str:
        """
        Отправляет изображение в GPT (Responses API)
        и получает табличные данные в CSV в нужном шаблоне
        """
        with open(image_path, "rb") as img_file:
            image_b64 = base64.b64encode(img_file.read()).decode("utf-8")

        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": self.system_prompt
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Распознай таблицу с этого изображения и приведи её к указанному шаблону."
                            )
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{image_b64}"
                        }
                    ]
                }
            ]
        )
        return response.output_text

    def normalize_table_from_text(self, table: list[list[str]]) -> str:
        """
        Отправляет текстовую таблицу в GPT для нормализации к шаблону (CSV).
        """
        table_text = "\n".join([";".join(row) for row in table])

        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": self.system_prompt
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f"Приведи данные к указанному шаблону. \nДанные: {table_text}"
                        }
                    ]
                }
            ]
        )
        return response.output_text

    def normalize_table_from_csv(self, csv_text: str) -> str:
        """
        Принимает CSV-текст (разделители ; или , неважно),
        отправляет в GPT для приведения к шаблону.
        Возвращает CSV с фиксированными колонками:
        №;Обозначение;Наименование;Ед. изм.;Требуемое кол-во, в ед. изм.;Техническое задание
        """
        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": self.system_prompt
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f"Вот сырой CSV: {csv_text}. Приведи данные к указанному шаблону."
                        }
                    ]
                }
            ]
        )
        return response.output_text

    def extract_table_from_image_b64(self, image_b64: str) -> str:
        """
        Принимает чистую base64-строку (без 'data:image') и отправляет в GPT.
        Возвращает CSV в нужном шаблоне.
        """
        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": [
                        {"type": "input_text", "text": self.system_prompt}
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text",
                         "text": "Распознай таблицу с этого изображения и приведи её к указанному шаблону."},
                        {"type": "input_image",
                         "image_url": f"data:image/png;base64,{image_b64}"}
                    ]
                }
            ]
        )
        return response.output_text
