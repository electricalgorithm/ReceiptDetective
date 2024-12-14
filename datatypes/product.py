"""
This module provides Product datatype that holds information related to single product item.

Each product item provides real life data related to the price, item name, category, etc.
"""
from pydantic import BaseModel

from datatypes import Currencies
from datatypes import ProductCategories


class Product(BaseModel):
    """This datatype holds information related to the items in a receipt."""

    name: str
    category: ProductCategories
    price: float
    price_currency: Currencies
    discount: float | None
