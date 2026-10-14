# blg — Bolig (housing) listing notifier

Checks [kereby.dk/bolig](https://kereby.dk/bolig/) for new rental listings and
posts a Discord message when one matches your criteria:

- Location: Copenhagen or Vanløse (matched against the listing's address text)
- Max rent: 13,000 kr./month — if a listing's price can't be parsed, it still
  notifies (per request), as long as the location matches
- Only listings currently marked available (not reserved/rented)

Only `kereby.dk` is covered. `udlejning.cej.dk` was dropped — its search page
sits behind a proof-of-work bot challenge on every request (even from a real
headless browser), so it can't be scraped with a lightweight script.

## How it works

`kereby.dk/bolig/` server-renders every listing directly into the page HTML
as `<article data-card-id="..." data-rent="..." data-zip="..." ...>` elements
— no API, no JS execution needed. The script does a plain HTTP GET, parses
those listing cards, filters by criteria, and diffs against
`data/seen_listings.json` (a list of listing IDs already notified) so you
only get pinged once per listing.

## Setup

1. Install dependencies (already done if you just cloned this):
   ```
   uv sync
   ```

2. Create a Discord webhook: in a Discord server you control, go to
   *Channel Settings → Integrations → Webhooks → New Webhook*, copy the URL.

3. Copy `.env.example` to `.env` and paste your webhook URL:
   ```
   cp .env.example .env
   ```

4. Test it:
   ```
   uv run python -m bolig_notifier.main
   ```
   First run will mark all current listings as "seen" without notifying
   (there's no meaningful "new" on the very first run). Delete
   `data/seen_listings.json` if you want to re-test from scratch — this will
   fire a notification for every currently-matching listing.

## Running on a schedule

Pick whichever matches where this is deployed. All three run the same
`uv run python -m bolig_notifier.main` command every 10 minutes; none of them
require editing paths by hand — the install scripts auto-detect the project
location and your `uv` binary.

Requires [`uv`](https://docs.astral.sh/uv/) to be installed on that machine
(`curl -LsSf https://astral.sh/uv/install.sh | sh`), and a working `.env`
with `DISCORD_WEBHOOK_URL` set (step 3 above) — do this on the server too if
that's where you're deploying, `.env` is gitignored and won't be copied by
`git clone`/`git pull`.

### Linux server (systemd, recommended)

```
bash deploy/systemd/install.sh
```

Runs as a per-user systemd timer — no root needed for the service itself.
On a headless box (no active login session), also run once so it survives
logout/reboot:
```
sudo loginctl enable-linger $USER
```

Status / logs / stop:
```
systemctl --user status bolig-notifier.timer
journalctl --user -u bolig-notifier.service -f
systemctl --user disable --now bolig-notifier.timer
```

### Linux server (plain cron, minimal servers without systemd --user)

See `deploy/cron/crontab.line.example` — fill in your project path and `uv`
path, then `crontab -e` and paste it in.

### macOS (launchd)

```
bash deploy/launchd/install.sh
```

Logs go to `data/notifier.log`. Only runs while the Mac is on and awake.

Stop:
```
launchctl unload ~/Library/LaunchAgents/com.blg.bolig-notifier.plist
rm ~/Library/LaunchAgents/com.blg.bolig-notifier.plist
```

## Adjusting criteria

Edit `bolig_notifier/criteria.py`:
- `MAX_RENT` — the price cap
- `_LOCATION_KEYWORDS` — matched against a normalized (lowercase, no accents)
  version of the listing address
