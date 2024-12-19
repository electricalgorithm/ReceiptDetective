"""
This model analyzes each Product in the Receipt OCR and fixes.

Within the module, an analyzer LLM agent is proposed. The LLM agent
looks for the problems in the receipt OCR and solves if something
seems different. It is a truth-check model on top of vision model.
"""

from typing import Any

import ollama
from pydantic import BaseModel

from backend.ai.assistants.base import AssistantBase
from backend.ai.assistants.base import AssistantSettings
from backend.ai.assistants.base import ModelAccessType
from backend.ai.datatypes.ocr_response import OcrResponse

ANALYZER_DEFAULT_SETTINGS: AssistantSettings = AssistantSettings(
    model="llama3.1:8b",
    prompt_file="backend/ai/prompts/analyzer.txt",
)
ANALYZER_DEFAULT_SETTINGS.response_model = OcrResponse


class AnalyzerAssistant(AssistantBase):
    """AnalyzerAssistant is an LLM agent that acts as OCR.

    It provides truth-check on top of the vision results and
    properly writes the product names into human readable form.
    """

    SERIALIZED_OBJECT_PLACEHOLDER: str = "{% SERIALIZED_OBJECT_JSON %}"
    PRODUCTS_LIST_PLACEHOLDER: str = "{% PRODUCT_LIST %}"

    def __init__(self, settings: AssistantSettings = ANALYZER_DEFAULT_SETTINGS) -> None:
        """Construct the analyzer assistant that detects problems in the receipt.

        :param settings: A settings object for LLM agent.
        """
        super().__init__(settings)

    def ask(self, input_data: dict[str, Any]) -> BaseModel:
        """Query the LLM agent with a given OCR result.

        :param input_data: The JSON string of the OCR result.
        :raises NotImplementedError: If the model access type is not OLLAMA.
        :raises RuntimeError: If the model server is not reachable.
        :raises ValueError: If the expected input is not available in the param.
        :raises TypeError: If the ocr_result is not a BaseModel instance.
        :returns: A BaseModel object, a better OCR Response
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
        if "ocr_result" not in input_data:
            error_msg: str = "The input_data should have ocr_result key."
            raise ValueError(error_msg)

        # Check if ocr_result holds a string.
        if not isinstance(input_data["ocr_result"], BaseModel):
            error_msg: str = "The input data does not contain a BaseModel OCR result."
            raise TypeError(error_msg)

        # Check the OcrResponse about its products count.
        ocr_result: OcrResponse = input_data["ocr_result"]
        if not len(ocr_result.products):
            error_msg: str = "The product list should be non zero."
            raise ValueError(error_msg)

        # Convert BaseModel to string to provide with prompt.
        product_abbrvs: str = "".join([f"- {abbrv.name}\n" for abbrv in ocr_result.products])
        content: str = self._settings.prompt.replace(self.PRODUCTS_LIST_PLACEHOLDER, product_abbrvs).replace(
            self.SERIALIZED_OBJECT_PLACEHOLDER,
            ocr_result.model_dump_json(),
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
