"""Scrapes rental listings from kereby.dk/bolig/.

The listings are server-rendered directly into the HTML as
`<article class="jorato-case-card" data-card-id="..." data-rent="..." ...>`
elements, so a plain HTTP GET + regex/BeautifulSoup parse is enough —
no browser automation or API needed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

LISTINGS_URL = "https://kereby.dk/bolig/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    )
}


@dataclass(frozen=True)
class Listing:
    id: str
    address: str
    headline: str
    zip_code: str
    rooms: int | None
    rent: int | None
    size_m2: int | None
    available: bool

    @property
    def url(self) -> str:
        return LISTINGS_URL


def _to_int(value: str | None) -> int | None:
    if value is None:
        return None
    value = value.strip()
    if not value.isdigit():
        return None
    return int(value)


def fetch_listings() -> list[Listing]:
    response = requests.get(LISTINGS_URL, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return parse_listings(response.text)


def parse_listings(html: str) -> list[Listing]:
    soup = BeautifulSoup(html, "html.parser")
    listings = []

    for card in soup.select("article.jorato-case-card[data-card-id]"):
        card_id = card.get("data-card-id", "").strip()
        if not card_id:
            continue

        location_el = card.select_one(".jorato-case-card__location-text")
        headline_el = card.select_one(".jorato-case-card__headline")

        available = "jorato-case-card--unavailable" not in card.get("class", [])

        listings.append(
            Listing(
                id=card_id,
                address=location_el.get_text(strip=True) if location_el else "",
                headline=headline_el.get_text(strip=True) if headline_el else "",
                zip_code=card.get("data-zip", "").strip(),
                rooms=_to_int(card.get("data-rooms")),
                rent=_to_int(card.get("data-rent")),
                size_m2=_to_int(card.get("data-size")),
                available=available,
            )
        )

    return listings
