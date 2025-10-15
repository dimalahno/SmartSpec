import base64
import os

from dotenv import load_dotenv
from openai import OpenAI

from specs.services.ai.prompts import SYSTEM_PROMPT

load_dotenv()


class AIHelper:
    def __init__(self, model: str = "gpt-5-mini"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY не найден. Проверьте .env файл.")
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.system_prompt = {
            "role": "system",
            "content": [
                {
                    "type": "input_text",
                    "text": SYSTEM_PROMPT
                }
            ]
        }

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
                self.system_prompt,
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
                self.system_prompt,
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
                self.system_prompt,
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
                self.system_prompt,
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

    def send_image_and_get_text(self, prompt: str, image_b64: str) -> str:
        """
        Отправляет base64-картинку + prompt.
        Возвращает сырой ответ от модели (текст).
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                self.system_prompt,
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}
                        }
                    ]
                }
            ]
        )
        return response.choices[0].message.content.strip()
