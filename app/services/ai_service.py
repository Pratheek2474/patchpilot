"""AI service — abstraction over Google Gemini API."""

from __future__ import annotations

from typing import Type, TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel

from app.config import settings

T = TypeVar("T", bound=BaseModel)


class AIService:
    """Manages structured interactions with the Google Gemini API."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self._api_key = api_key or settings.gemini_api_key
        self._model = model or settings.ai_model
        self._client: genai.Client | None = None

    def _get_client(self) -> genai.Client:
        if self._client is None:
            if not self._api_key:
                raise ValueError("No Gemini API key configured. Set GEMINI_API_KEY in .env")
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    def chat_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        temperature: float = 0.2,
        max_tokens: int = 8192,
    ) -> T:
        """Send a structured generation request and return a parsed Pydantic model."""
        client = self._get_client()

        response = client.models.generate_content(
            model=self._model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
                max_output_tokens=max_tokens,
                response_mime_type="application/json",
                response_schema=response_model,
            ),
        )

        raw_text = response.text
        if not raw_text:
            raise ValueError(f"Empty response from Gemini for {response_model.__name__}")

        try:
            return response_model.model_validate_json(raw_text)
        except Exception as e:
            raise ValueError(
                f"Failed to parse Gemini response into {response_model.__name__}: {e}"
            ) from e


ai_service = AIService()
