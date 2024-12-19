"""The common module provides the types that are small to implement on their own files."""

import re
from enum import StrEnum
from enum import unique
from typing import Annotated

from pydantic import AfterValidator
from pydantic import ValidationError


@unique
class Currencies(StrEnum):
    """This enum holds supported currencies."""

    EUR = "€"
    TRY = "₺"
    PLN = "zł"
    USD = "$"
    BGN = "лв"


ReceiptIdPattern: re.Pattern = re.compile(r"^receipt-[a-h0-9]+-[a-h0-9]+-[a-h0-9]+-[a-h0-9]+$")
ReceiptId = Annotated[
    str,
    AfterValidator(
        lambda value: value
        if ReceiptIdPattern.search(value)
        else ValidationError("The receiptid does not follow the pattern."),
    ),
]
