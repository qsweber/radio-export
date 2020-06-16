from datetime import datetime

from typing import NamedTuple


Song = NamedTuple(
    'Song',
    [
        ('datetime', datetime),
        ('artist', str),
        ('song', str),
    ]
)
