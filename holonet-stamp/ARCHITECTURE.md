# ARCHITECTURE.md — Holonet Timestamp System

## Overview

The Holonet Timestamp System is composed of two primary layers:

1. **Core Time Library (`sw_time.py`)**
2. **Presentation & Integration Layer (`holonet_stamp.py`)**

The system is intentionally small, deterministic, and dependency-light so it can be embedded in:
- CLI tools
- Web services
- API gateways
- Logging pipelines

---

## Design goals

- Deterministic and reproducible time calculations
- No hidden global state
- Clear separation between *time math* and *output formatting*
- Safe for production logging
- Easy to reason about for both humans and automated tools

---

## Layer 1: Core Time Library (`sw_time.py`)

### Responsibilities

- All Star Wars–related time math
- No I/O
- No CLI parsing
- No logging
- No network access

### Concepts

#### CGT (Combine Galactic Time)
- Calendar:
  - 365 days/year
  - 24 hours/day
  - Day-of-year range: 1–365
- Epochs:
  - `current`: CGT(0,1,0,0,0) == 1998-12-03 07:00:00 UTC
  - `legacy`:  CGT(0,1,0,0,0) == 1998-12-03 00:00:00 UTC

#### SWET (Star Wars Epoch Time)
- Seconds since 1977-05-25 00:00:00 UTC
- Intended as a compact, integer-based Star Wars timestamp

#### Calendar offsets
- Year-only offsets derived from published Star Wars timelines
- Used for context and labeling, not canonical chronology

### Invariants

- CGT <-> UTC round-trips must be lossless
- SWET(0) == Star Wars theatrical release
- No DST logic exists in CGT (handled only when converting to real timezones)

---

## Layer 2: CLI & Integration (`holonet_stamp.py`)

### Responsibilities

- CLI argument parsing
- Output formatting
- ANSI color and ASCII banner
- Request ID generation and propagation
- Optional network calls (quotes API)

### Output modes

- Pretty (human-facing)
- One-line (log-facing)
- JSON (machine-facing)

### Request ID subsystem

- Single request ID per invocation
- Precedence:
  1. Explicit CLI `--request-id`
  2. Inbound `X-Request-ID` (env)
  3. Auto-generated ID
- Prefixing:
  - Explicit (`--rid-prefix`)
  - Auto-detected based on output mode

### Downstream propagation

- All outbound HTTP requests include `X-Request-ID`
- Ensures traceability across services

---

## Data flow

```
UTC now
  |
  v
sw_time.py  (CGT / SWET calculations)
  |
  v
holonet_stamp.py
  |
  +--> Text / JSON output
  |
  +--> Optional quote API (with propagated X-Request-ID)
```

---

## Non-goals

- Full Star Wars canonical chronology enforcement
- Leap seconds or leap years in CGT
- Persistent storage
- Distributed tracing replacement

---

## Extensibility

Safe extension points:

- Add new Star Wars calendars in `sw_time.py`
- Add new output formats in `holonet_stamp.py`
- Add new downstream integrations (ensure RID propagation)

Unsafe changes:

- Mixing I/O into `sw_time.py`
- Adding non-deterministic behavior to core conversions

---

## Summary

The architecture is intentionally boring:

- Pure math at the core
- Formatting at the edges
- Clear seams for testing and extension

This keeps the system trustworthy and easy to maintain.
