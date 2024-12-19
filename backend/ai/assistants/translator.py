"""
An LLM that translates receipt information between languages.

This module contains the implementation related to LLM-TRANSLATE for reading
the product names and translates them into a known language.
"""

from typing import Any

import ollama
from pydantic import BaseModel

from backend.ai.assistants.base import AssistantBase
from backend.ai.assistants.base import AssistantSettings
from backend.ai.assistants.base import ModelAccessType
from backend.ai.datatypes import OcrResponse

TRANSLATOR_DEFAULT_SETTINGS: AssistantSettings = AssistantSettings(
    model="llama3.2-vision:11b",
    prompt_file="backend/ai/prompts/ocr.txt",
)
TRANSLATOR_DEFAULT_SETTINGS.response_model = OcrResponse


class TranslatorAssistant(AssistantBase):
    """TranslateAssistant is an LLM agent that acts as translator."""

    SERIALIZED_OBJECT_PLACEHOLDER: str = "{% SERIALIZED_OBJECT_JSON %}"
    SOURCE_LANG_PLACEHOLDER: str = "{% SOURCE_LANG %}"
    TARGET_LANG_PLACEHOLDER: str = "{% TARGET_LANG %}"

    def __init__(self, settings: AssistantSettings = TRANSLATOR_DEFAULT_SETTINGS) -> None:
        """Construct for the TranslatorAssistant.

        :param settings: AssistantSettings instance with OCR model settings.
        """
        super().__init__(settings)

    def ask(self, input_data: dict[str, Any]) -> BaseModel:
        """Send the receipt data to LLM agent, and ask for translation.

        :param input_data: A dict contains "previous", "source_lang", "target_lang" keys
        :raise NotImplementedError: Assistant with different access type.
        :raise RuntimeError: The model is not accessible.
        :raise ValueError: The input data is not in proper format.
        :returns: A OcrResponse element.
        """
        # Check if access type is OLLAMA.
        if self._settings.access != ModelAccessType.OLLAMA:
            error_msg: str = "The OcrAssistant is only support OLLAMA accesses."
            raise NotImplementedError(error_msg)

        # Check if model is accessible.
        if not self.heartbeat():
            error_msg: str = f"The {self._settings.access.name} is not accessible."
            raise RuntimeError(error_msg)

        # Check the input_data format.
        if "source_lang" not in input_data or "target_lang" not in input_data or "previous" not in input_data:
            error_msg: str = "The input_data should have 'previous', 'source_lang', 'target_lang' key."
            raise ValueError(error_msg)

        # Check the OcrResponse about its products count.
        previous: OcrResponse = input_data["previous"]
        if not len(previous.products):
            error_msg: str = "The product list should be non zero."
            raise ValueError(error_msg)

        # Convert BaseModel to string to provide with prompt.
        content: str = (
            self._settings.prompt.replace(self.SOURCE_LANG_PLACEHOLDER, input_data["source_lang"])
            .replace(self.TARGET_LANG_PLACEHOLDER, input_data["target_lang"])
            .replace(self.SERIALIZED_OBJECT_PLACEHOLDER, previous.model_dump_json())
        )

        # Send the OCR request to agent.
        response: ollama.ChatResponse = ollama.chat(
            model=self._settings.model,
            messages=[
                {
                    "role": "user",
                    "content": content,
                    "options": {"temperature": 0},
                },
            ],
            format=self._settings.response_model_json,
        )

        # Check if content is received.
        if not isinstance(response.message.content, str):
            error_msg: str = f"The LLM did not return str: {response.message.content}."
            raise TypeError(error_msg)

        return self._settings.response_model_class.model_validate_json(response.message.content)
