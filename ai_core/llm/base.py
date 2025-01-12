# ai_core/llm/base.py
from typing import Dict, Any
import openai
from django.conf import settings
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Base class for LLM providers"""

    @abstractmethod
    async def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a response from the LLM"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API integration"""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        openai.api_key = self.api_key
        self.model = settings.OPENAI_MODEL_NAME  # e.g., "gpt-4" or "gpt-3.5-turbo"

    async def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            system_prompt = self._build_system_prompt(context)
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            return {
                'success': True,
                'content': response.choices[0].message.content,
                'usage': response.usage
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _build_system_prompt(self, context: Dict[str, Any] = None) -> str:
        base_prompt = (
            "You are an AI assistant specialized in Django development and project management. "
            "You help users with code generation, debugging, and project organization."
        )

        if context:
            base_prompt += f"\nCurrent context: {context}"

        return base_prompt