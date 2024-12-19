"""
An LLM that reads and provides receipt information from photos.

This module contains the implementation related to LLM-OCR for reading
receipts and providing structured datatype to the consumers.
"""

from pathlib import Path
from typing import Any

import ollama
from pydantic import BaseModel

from backend.ai.assistants.base import AssistantBase
from backend.ai.assistants.base import AssistantSettings
from backend.ai.assistants.base import ModelAccessType
from backend.ai.datatypes import OcrResponse

OCR_DEFAULT_SETTINGS: AssistantSettings = AssistantSettings(
    model="llama3.2-vision:11b",
    prompt_file="backend/ai/prompts/ocr.txt",
)
OCR_DEFAULT_SETTINGS.response_model = OcrResponse


class OcrAssistant(AssistantBase):
    """OcrAssistant is an LLM agent that acts as OCR.

    This vision agent recognizes the text in receipts and
    returns the list of products to the consumer. If the
    agent cannot read the image, it returns a response
    indicating the OCR has failed.
    """

    def __init__(self, settings: AssistantSettings = OCR_DEFAULT_SETTINGS) -> None:
        """Construct for the OcrAssistant.

        :param settings: AssistantSettings instance with OCR model settings.
        """
        super().__init__(settings)

    def ask(self, input_data: dict[str, Any]) -> BaseModel:
        """Send the receipt image to LLM agent, and ask for OCR.

        :param input_data: A dict contains "image" key with a value
        that holds absolute path of an image.
        :raise NotImplementedError: OcrAssistant with different access type.
        :raise RuntimeError: The model is not accessible.
        :raise ValueError: The input data is not in proper format.
        :raise FileNotFoundError: The image file cannot be found.
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
        if "image" not in input_data:
            error_msg: str = "The input_data should have image key."
            raise ValueError(error_msg)

        # Check the image type.
        allowed_formats: list[str] = ["jpeg", "jpg", "png"]
        if input_data["image"].split(".")[-1] not in allowed_formats:
            error_msg: str = f"The image should be in formats: {allowed_formats}."
            raise TypeError(error_msg)

        # Check if the file exists.
        receipt_image: Path = Path(input_data["image"])
        if not receipt_image.exists():
            error_msg: str = "The image path in the input_data cannot be found in the filesystem."
            raise FileNotFoundError(error_msg)

        # Send the OCR request to agent.
        response: ollama.ChatResponse = ollama.chat(
            model=self._settings.model,
            messages=[
                {
                    "role": "user",
                    "content": self._settings.prompt,
                    "images": [input_data["image"]],
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
