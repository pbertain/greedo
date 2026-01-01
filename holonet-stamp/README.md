# Holonet Timestamp System

A deterministic, log-friendly timestamp system that combines **real-world time** with **Star Wars–themed time systems**.

This project consists of:

- `sw_time.py` — a pure Python Star Wars time conversion library
- `holonet_stamp.py` — a CLI tool for emitting “Holonet timestamps” for logs, APIs, and UIs

And yes:

> **Han shot first.**

---

## Why this exists

Unix time is great for machines, but not very fun for humans.

This project adds a *galactic-flavored* layer on top of standard timestamps so logs and request output can be:

- deterministic
- testable
- human-readable
- log-ingestion friendly
- mildly delightful

The CLI outputs both **real time** and **Star Wars time**, with a stable request ID that propagates across services.

---

## Files and responsibilities

### `sw_time.py` — Star Wars time conversion library

A pure-Python module with no I/O.

Provides:

- **CGT (Combine Galactic Time) ↔ UTC**
  - 365-day years, 24-hour days
  - Day-of-year range: 1–365
  - Supported epochs:
    - `current`: `CGT(0,1,0,0,0)` → `1998-12-03 07:00:00 UTC`
    - `legacy`:  `CGT(0,1,0,0,0)` → `1998-12-03 00:00:00 UTC`

- **Timezone conversion**
  - Uses IANA timezone names (`America/Los_Angeles`, etc.)
  - Automatically handles DST (PST/PDT)

- **SWET (Star Wars Epoch Time)**
  - Seconds since *Star Wars* theatrical release  
    `1977-05-25 00:00:00 UTC`

- **Year-only Star Wars calendar conversions**
  - BTC / ATC — Treaty of Coruscant
  - BBY / ABY — Battle of Yavin
  - GrS — Great ReSynchronization
  - GSC — Galactic Standard Calendar
  - TYA — Tho Yor Arrival
  - Ruus — Ruusan Reformation
  - LY — Lothal Years

Design notes:

- Safe to import from other code
- Deterministic math only
- Fully unit-tested

---

### `holonet_stamp.py` — Holonet timestamp CLI

A command-line utility for emitting timestamps suitable for:

- APIs
- Web UIs
- curl/plaintext endpoints
- Logs and tracing

Always outputs:

- `Fact: Han shot first.`
- UTC timestamp
- Local timestamp (configurable timezone)
- Unix epoch seconds

Optional (`--sw-time`):

- SWET
- CGT (formatted)
- GSC year label
- CGT epoch mode (`current` / `legacy`)

---

## Output formats

### Pretty text (default)

- Multi-line
- ASCII “Holonet” banner
- ANSI color (auto-disabled if not a TTY)

```bash
holonet-stamp --sw-time
```

---

### One-line log format

Single-line, key=value format for grep and log ingestion.

```bash
holonet-stamp --sw-time --one-line
```

---

### Forced minimal logs

Best for systemd / cron / plain-text endpoints.

```bash
holonet-stamp --sw-time --quiet
```

---

### JSON output

Structured output for ingestion pipelines.

```bash
holonet-stamp --sw-time --json
```

Compact JSON:

```bash
holonet-stamp --sw-time --json --one-line
```

---

## Request ID (RID) and X-Request-ID

Each output includes a **request ID** for correlation.

### Precedence (highest → lowest)

1. `--request-id`
2. Inbound `X-Request-ID` from environment  
   (`HTTP_X_REQUEST_ID`, `X_REQUEST_ID`, etc.)
3. Auto-generated ID

### Auto prefixing

If `--rid-prefix` is not supplied:

- `--json` → `api-`
- `--one-line` / `--quiet` → `curl-`
- Pretty output → `web-`

Example IDs:

```text
api-550e8400-e29b-41d4-a716-446655440000
curl-Qs9x2LmP4dA1
web-1b7d4c0e-acde-4a7b-9f09-1a3d9c02d0f8
```

### Downstream propagation

All outbound HTTP requests (e.g. quote API) include:

```
X-Request-ID: <request_id>
```

---

## Optional extras

### Extra facts file

Rotate additional facts deterministically:

```bash
holonet-stamp --fact-file facts.txt
```

- One fact per line
- Blank lines and `#` comments ignored

### Random Star Wars quote

```bash
holonet-stamp --quote
```

- Best-effort fetch
- Safe fallback if API is unavailable
- Request ID propagated

---

## Common usage patterns

### Web UI

```bash
holonet-stamp --sw-time
```

### API endpoint

```bash
holonet-stamp --sw-time --json
```

### curl / plaintext

```bash
holonet-stamp --sw-time --quiet
```

### Explicit override

```bash
holonet-stamp --request-id 123 --rid-prefix api- --json
```

---

## Testing

Run all tests:

```bash
python -m unittest -v
```

### `test_sw_time.py` verifies

- CGT epoch correctness (current + legacy)
- Round-trip CGT ↔ UTC
- Timezone conversion
- SWET epoch (Star Wars release == SWET 0)
- Calendar offset sanity

### `test_holonet_stamp.py` verifies

- Fact always present
- Request ID always present
- Auto-prefix logic (`api-`, `curl-`, `web-`)
- Inbound `X-Request-ID` handling
- One-line output contract
- Star Wars block only when enabled

---

## References

### Star Wars calendar conversions

Crystal Odenkirk — Star Wars Date Converter  
https://crysodenkirk.com/conlangs/SWtimeline.php

Covers:

- BTC / ATC (Treaty of Coruscant)
- BBY / ABY (Battle of Yavin)
- GrS (Great ReSynchronization)
- GSC (Galactic Standard Calendar)
- TYA (Tho Yor Arrival)
- Ruus (Ruusan Reformation)
- LY (Lothal Years)

### Combine Galactic Time (CGT)

SWCombine rules and converter:

- https://www.swcombine.com/rules/?Timeframe#Combine_Galactic_Time
- https://www.swcombine.com/rules/?Timeframe#CGT/GMT_time_Convertor

---

## Final note

This system is intentionally:

- deterministic
- testable
- log-friendly
- human-readable

It is safe to use in production logs, APIs, and debugging tools.

And once again:

**Han shot first.**
