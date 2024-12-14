"""
This package exposes the datatypes needed for the other packages.

It is important to define a datatype in this package, and use it
across the other packages.
"""
from datetime import datetime

from datatypes.categories import ProductCategories
from datatypes.common import Currencies
from datatypes.common import ReceiptId
from datatypes.ocr_result import OcrResult
from datatypes.ocr_result import OcrStatusTypes
from datatypes.product import Product

__all__ = [
    "Currencies",
    "OcrResult",
    "OcrStatusTypes",
    "Product",
    "ProductCategories",
    "ReceiptId",
    "datetime",
]
