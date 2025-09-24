import base64
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class AIHelper:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY не найден. Проверьте .env файл.")
        self.client = OpenAI(api_key=api_key)

    def extract_table_from_image(self, image_path: str) -> str:
        """
        Отправляет изображение в GPT (Responses API) и получает табличные данные в CSV
        сразу в нужном шаблоне:
        №;Обозначение;Наименование;Ед. изм.;Требуемое кол-во, в ед. изм.;Техническое задание
        """
        with open(image_path, "rb") as img_file:
            image_b64 = base64.b64encode(img_file.read()).decode("utf-8")

        response = self.client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Ты OCR-помощник. Твоя задача — извлекать таблицы из изображений "
                                "и всегда возвращать результат в формате CSV с разделителем ';'. "
                                "Фиксированный набор колонок: "
                                "№;Обозначение;Наименование;Ед. изм.;Требуемое кол-во, в ед. изм.;Техническое задание"
                            )
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Распознай таблицу с этого изображения и приведи её "
                                "к указанному шаблону. Если данных для столбца нет — оставь пустую ячейку."
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
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Ты помощник по обработке таблиц. "
                                "Приводи любые таблицы к следующему CSV-шаблону: "
                                "№;Обозначение;Наименование;Ед. изм.;Требуемое кол-во, в ед. изм.;Техническое задание"
                                "Наименование может включать обозначения. Извлекай их."
                            )
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f"Приведи эту таблицу к шаблону:\n{table_text}"
                        }
                    ]
                }
            ]
        )
        return response.output_text
