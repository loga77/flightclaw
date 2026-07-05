# FlightClaw repo: instructions for Claude

This repo tracks flight prices via GitHub Actions on a 4-hour cron.
Price history lives in `data/tracked.json`. Alerts go to Telegram.

## How to add a route to tracking

Trigger the `Track a new route` workflow with inputs. Use the gh CLI:

```bash
gh workflow run track-route.yml \
  -f origin=ZRH \
  -f destination=JFK \
  -f date=2026-09-10 \
  -f return_date=2026-09-20 \
  -f target_price=450 \
  -f cabin=ECONOMY
```

## How to check prices on demand

```bash
gh workflow run check-prices.yml
# then, after ~1 min:
gh run list --workflow=check-prices.yml --limit 1
gh run view --log $(gh run list --workflow=check-prices.yml --limit 1 --json databaseId -q '.[0].databaseId')
```

Or locally (requires `pip install flights`):

```bash
python scripts/check-prices.py --threshold 5
python scripts/list-tracked.py
```

## How to analyze price history

Read `data/tracked.json` directly. Each tracked route contains its price
history over time. When asked "should I book now", compare the latest
price to the historical min/max/median in that file and give a
recommendation with reasoning.

## How to search flights interactively (MCP)

If the FlightClaw MCP server is connected, prefer these tools:
- `search_flights`, `search_dates` for exploration
- `track_flight` for local tracking (remember: local tracking is NOT
  the same as repo tracking; for the always-on cron, use the
  `track-route.yml` workflow so the route lands in the repo's
  `data/tracked.json`)

## Rules

- Never remove tracked routes without explicit confirmation.
- Dates must be in the future; validate before triggering workflows.
- Prices from GitHub runners resolve in USD (US IPs). Mention this
  when discussing target prices.

## How to stop tracking a route

Stopping a route runs the `Stop tracking a route` workflow, which calls
`scripts/untrack-flight.py` and commits the updated `data/tracked.json`.

```bash
# Remove a specific route (narrow match on the route id)
gh workflow run untrack-route.yml -f match=ZRH-NAP

# Remove all routes to a destination (broad match)
gh workflow run untrack-route.yml -f match=NAP

# Clear everything
gh workflow run untrack-route.yml -f remove_all=true
```

The match term is a case-insensitive substring of the route id
(e.g. `ZRH-NAP-2026-07-18-RT-2026-07-25`). Prefer the narrowest term
that identifies the route. To see current ids first, read
`data/tracked.json` or run `python scripts/untrack-flight.py --list`
locally. Always confirm which routes will be removed before running a
broad match or `remove_all`.

## Note on pushing

The price-check workflow commits price history to `data/tracked.json`
autonomously, so the remote is often ahead of local. Before pushing any
change, pull first: `git pull --no-rebase` then push.
