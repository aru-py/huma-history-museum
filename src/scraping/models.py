"""
models.py
"""

from typing import List
from attr import dataclass


@dataclass
class Event:
    """
    Represents an event in history.
    """
    id: int
    url: str
    title: str
    date: str
    description: str
    items: List[dict]


@dataclass
class Item:
    """
    Represents an image of an historical
    event.
    """
    id: int
    url: str
    description: str
    image_url: str
    metadata: List
