"""
Copyright 2024. github.com/electricalgorithm

This module consists of the datatype store possible receipt categories.
"""

from enum import Enum
from enum import auto
from enum import unique


@unique
class ProductCategories(int, Enum):
    """This class holds the possible category types."""

    TEXTILE = auto()
    FOOD = auto()
    VEGETABLE = auto()
    FRUIT = auto()
    KITCHEN_STUFF = auto()
    GROCERY = auto()
    TECHNOLOGY = auto()
    HOBBY = auto()
