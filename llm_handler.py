import os
import openai
import logging
import asyncio
from typing import List

class LLMHandler:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        # V1.0+ 에서는 클라이언트를 초기화합니다.
        self.client = openai.OpenAI(api_key=self.api_key)

    async def _run_blocking_openai(self, model, messages, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,  # 기본 스레드 풀 사용
            # V1.0+ 구문으로 변경: self.client.chat.completions.create
            lambda: self.client.chat.completions.create(model=model, messages=messages, **kwargs)
        )

    async def summarize_text(self, text: str) -> str:
        prompt = f"Please summarize the following news article in 3-4 sentences in Korean:\n\n{text}"
        try:
            response = await self._run_blocking_openai(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Error summarizing text: {e}")
            return "Summary not available."

    async def extract_keywords(self, text: str) -> List[str]:
        prompt = f"Extract 3 to 5 most important keywords from the following text as a comma-separated list (e.g., keyword1, keyword2, keyword3) in Korean:\n\n{text}"
        try:
            response = await self._run_blocking_openai(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            keywords = response.choices[0].message.content.strip().split(',')
            return [k.strip() for k in keywords]
        except Exception as e:
            logging.error(f"Error extracting keywords: {e}")
            return ["N/A"]

    async def classify_category(self, text: str) -> str:
        categories = ["기술", "경제", "정치", "비즈니스", "사회", "국제", "문화"]
        prompt = f"Classify the following article into one of these categories: {', '.join(categories)}. Respond with only the category name.\n\n{text}"
        try:
            response = await self._run_blocking_openai(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            category = response.choices[0].message.content.strip()
            return category if category in categories else "기타"
        except Exception as e:
            logging.error(f"Error classifying category: {e}")
            return "기타"
