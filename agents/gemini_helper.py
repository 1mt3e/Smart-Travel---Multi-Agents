"""Shared Gemini client via google.genai (REST/HTTP, no grpc)."""
from google import genai
import time
import re


class GeminiHelper:
    def __init__(self, api_key: str, model_name: str, system_instruction: str | None = None):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.system_instruction = system_instruction

    def _build_config(self, json_output: bool = False) -> dict:
        config = {}
        if self.system_instruction:
            config["system_instruction"] = self.system_instruction
        if json_output:
            config["response_mime_type"] = "application/json"
        return config

    def _get_sleep_time(self, error_str: str, attempt: int) -> float:
        match = re.search(r"retry in ([\d\.]+)s", error_str)
        if match:
            return float(match.group(1)) + 1.0
        return 5.0 * (attempt + 1)

    def generate_text(self, prompt: str, max_retries=5) -> str:
        config = self._build_config(json_output=False)
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config or None,
                )
                return (response.text or "").strip()
            except Exception as e:
                error_str = str(e)
                if ("429" in error_str or "RESOURCE_EXHAUSTED" in error_str) and attempt < max_retries - 1:
                    sleep_time = self._get_sleep_time(error_str, attempt)
                    print(f"[Gemini API] 429 Rate Limit. Waiting {sleep_time:.1f}s to retry... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(sleep_time)
                else:
                    raise e

    def generate_json(self, prompt: str, max_retries=5) -> str:
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=self._build_config(json_output=True),
                )
                return (response.text or "").strip()
            except Exception as e:
                error_str = str(e)
                if ("429" in error_str or "RESOURCE_EXHAUSTED" in error_str) and attempt < max_retries - 1:
                    sleep_time = self._get_sleep_time(error_str, attempt)
                    print(f"[Gemini API] 429 Rate Limit. Waiting {sleep_time:.1f}s to retry... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(sleep_time)
                else:
                    raise e
