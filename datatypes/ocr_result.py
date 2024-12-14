"""
Copyright 2024. github.com/electricalgorithm

This module consists of the datatype to validate OCR statuses.
"""
from enum import Enum
from enum import auto
from enum import unique

from pydantic import BaseModel

from datatypes import ReceiptId


@unique
class OcrStatusTypes(int, Enum):
    """This enum holds the possible OCR statuses."""

    NOT_PROCCESSED = auto()
    SUCCESS = auto()
    ERROR = auto()


class OcrResult(BaseModel):
    """This class holds the data about the OCR process result."""

    receipt_id: ReceiptId
    status: OcrStatusTypes
    details: str
