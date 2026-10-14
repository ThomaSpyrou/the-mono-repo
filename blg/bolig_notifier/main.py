from __future__ import annotations

import logging
import os
from pathlib import Path

from . import criteria, notify, storage
from .scraper import fetch_listings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("bolig_notifier")

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


def _load_dotenv(path: Path = ENV_FILE) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def run() -> None:
    _load_dotenv()

    seen_ids = storage.load_seen_ids()
    listings = fetch_listings()
    log.info("Fetched %d listings from kereby.dk", len(listings))

    new_listings = [listing for listing in listings if listing.id not in seen_ids]
    log.info("%d listings are new since last run", len(new_listings))

    matches = [listing for listing in new_listings if criteria.is_match(listing)]

    for listing in matches:
        log.info("Match: %s (%s)", listing.headline, listing.address)
        try:
            notify.send_notification(listing)
        except Exception:
            log.exception("Failed to send notification for listing %s", listing.id)

    seen_ids.update(listing.id for listing in listings)
    storage.save_seen_ids(seen_ids)

    log.info("Done. %d new matches notified.", len(matches))


if __name__ == "__main__":
    run()
