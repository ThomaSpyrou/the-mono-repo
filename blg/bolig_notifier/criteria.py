"""Match listings against the search criteria: Copenhagen or Vanløse, max 13,000 kr/month.

If the price can't be parsed, the listing still matches (per user preference) as
long as the location matches.
"""

from __future__ import annotations

import re

from .scraper import Listing

MAX_RENT = 13_000

_LOCATION_KEYWORDS = ("kobenhavn", "vanlose")

_DANISH_MAP = str.maketrans({"æ": "ae", "ø": "o", "å": "a"})


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z]", "", text.lower().translate(_DANISH_MAP))


def is_match(listing: Listing) -> bool:
    if not listing.available:
        return False

    normalized_address = _normalize(listing.address)
    if not any(keyword in normalized_address for keyword in _LOCATION_KEYWORDS):
        return False

    if listing.rent is None:
        return True

    return listing.rent <= MAX_RENT
