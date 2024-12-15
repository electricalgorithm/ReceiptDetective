"""
This module consists of the datatype to validate receipts after OCR process completes.

The presented class encapsulates all the neccessary information that is shared between
different services.
"""

from pydantic import BaseModel

from datatypes import OcrResult
from datatypes import Product
from datatypes import ProductCategories
from datatypes import ReceiptId
from datatypes import datetime


class ReceiptOcrResult(BaseModel):
    """This class is responsible of storing receipt instances."""

    receipt_id: ReceiptId
    ocr_status: OcrResult
    store_name: str
    store_address: str
    date_time: datetime
    category: list[ProductCategories]
    products: list[Product]
