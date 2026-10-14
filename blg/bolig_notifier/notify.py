"""Sends listing notifications to a Discord channel via an incoming webhook."""

from __future__ import annotations

import os

import requests

from .scraper import Listing

WEBHOOK_ENV_VAR = "DISCORD_WEBHOOK_URL"


def _format_rent(rent: int | None) -> str:
    if rent is None:
        return "Price unknown"
    return f"{rent:,} kr./md.".replace(",", ".")


def build_message(listing: Listing) -> str:
    lines = [
        f"**New listing:** {listing.headline or 'Bolig'}",
        f"{listing.address}",
        f"{_format_rent(listing.rent)}"
        + (f" · {listing.rooms} rooms" if listing.rooms else "")
        + (f" · {listing.size_m2} m²" if listing.size_m2 else ""),
        listing.url,
    ]
    return "\n".join(lines)


def send_notification(listing: Listing, webhook_url: str | None = None) -> None:
    webhook_url = webhook_url or os.environ.get(WEBHOOK_ENV_VAR)
    if not webhook_url:
        raise RuntimeError(
            f"{WEBHOOK_ENV_VAR} is not set. Add it to your environment or .env file."
        )

    response = requests.post(
        webhook_url,
        json={"content": build_message(listing)},
        timeout=15,
    )
    response.raise_for_status()
