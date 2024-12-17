"""
This module contains a response datatype for OCR AI.

The class will be used to retrieve structured output from the LLM.
"""
from datetime import datetime
from enum import StrEnum
from enum import unique

from pydantic import BaseModel

from datatypes import Currencies
from datatypes import Product


@unique
class OcrStatus(StrEnum):
    """This enum represents the status of the OCR, and selected by LLM."""

    FAILED = "I AM HAVING PROBLEM TO RECOGNIZE OR UNDERSTAND EVERYTHING"
    SUCCESS = "I CAN RECOGNIZE EVERY FIELD AND UNDERSTAND"


class OcrResponse(BaseModel):
    """This class is the structure definition of the LLM output for OCR step."""

    ocr_status: OcrStatus
    store_name: str | None
    store_address: str | None
    date_time: datetime | None
    products: list[Product] | None
    total_price: float | None
    total_price_currency: Currencies | None
