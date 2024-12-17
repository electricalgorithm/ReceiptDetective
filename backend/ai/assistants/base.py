"""
This module provides the base class for assistants.

Each assistant that will be implemented should inherit the
base class below. Furthermore, each assistant must follow the
input and output patterns.
"""

from abc import ABC
from abc import abstractmethod
from enum import Enum
from enum import auto
from enum import unique
from pathlib import Path
from typing import Any

import ollama
from pydantic import BaseModel


@unique
class ModelAccessType(int, Enum):
    """This enum represents the LLM API type.

    Currently only supported value is OLLAMA.
    """

    OLLAMA = auto()


class AssistantSettings:
    """A Settings Class for Assistant Constructions"""

    def __init__(
        self,
        model: str,
        prompt_file: str,
        access: ModelAccessType = ModelAccessType.OLLAMA,
    ) -> None:
        """Construct a AssistantSettingsBase instance.

        :param model: The model name.
        :param prompt_file: The system prompt file absolute location.
        :param access: The access type for LLM API. Defaults to OLLAMA.
        :return: AssistantSettingsBase instance.
        """
        self.model: str = model
        self.access: ModelAccessType = access
        self._prompt_file: str = prompt_file

    @property
    def prompt(self) -> str:
        """This property returns the prompt text from the given prompt file.

        :raise ValueError: When no prompt file exists or given.
        :return: The system prompt as string
        """
        # Read the prompt file and return its contents.
        if not self._prompt_file:
            error_msg: str = "Prompt file is missing."
            raise ValueError(error_msg)

        file_path: Path = Path(self._prompt_file)
        try:
            with Path.open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError as err:
            error_msg: str = f"Prompt file {file_path} is not found."
            raise ValueError(error_msg) from err

    @property
    def response_model_json(self) -> dict[str, Any]:
        """This property getter returns the respose model as JSON/dict.

        :raise RuntimeError: The response model is not selected yet.
        :returns: Response Model as JSON/dict.
        """
        if self._response_model_type is None:
            error_msg: str = "Response Model is not selected yet."
            raise RuntimeError(error_msg)
        return self._response_model_json

    @property
    def response_model_class(self) -> type[BaseModel]:
        """This property getter returns the response model as BaseModel.

        :raise RuntimeError: The response model is not selected yet.
        :returns: Response Model as BaseModel.
        """
        if self._response_model_type is None:
            error_msg: str = "Response Model is not selected yet."
            raise RuntimeError(error_msg)
        return self._response_model_type

    @property
    def response_model(self) -> None:
        """This property is write-only. Use response_model_class or response_model_json.

        :raise AttributeError: Property is write-only.
        """
        error_msg: str = "Property is write-only."
        raise AttributeError(error_msg)

    @response_model.setter
    def response_model(self, model_type: type[BaseModel]) -> None:
        """Set the response model used for structured outputs of LLM.

        :param model: A BaseModel instance
        """
        self._response_model_type: type[BaseModel] = model_type
        self._response_model_json = model_type.model_json_schema()


class AssistantBase(ABC):
    """This class is a base class that interfaces how assistants configured."""

    def __init__(self, settings: AssistantSettings) -> None:
        """Construct an assistant from the settings.

        :param settings: AssistantSettings instance
        """
        self._settings: AssistantSettings = settings

    @abstractmethod
    def ask(self, input_data: dict[str, Any]) -> BaseModel:
        """Communicate with the LLM agent.

        :param input_data: Data to sent the LLM agent.
        :returns: The response as BaseModel in structured form.
        """
        error_msg: str = "Abstract Method is not implemented yet."
        raise NotImplementedError(error_msg)

    def heartbeat(self) -> bool:
        """Check if model is alive to recieve inputs.

        :return: True if alive, False if not.
        """
        if self._settings.access != ModelAccessType.OLLAMA:
            error_msg: str = "The selected access type is not implemented yet."
            raise NotImplementedError(error_msg)

        try:
            ollama.list()
        except Exception:  # noqa: BLE001
            return False
        return True
