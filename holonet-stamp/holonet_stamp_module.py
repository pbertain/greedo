#!/usr/bin/env python3
"""
holonet_stamp.py — emit a "Holonet timestamp" with optional Star Wars time.

Features:
- Always includes: Fact: Han shot first.
- Optional Star Wars block (--sw-time): SWET / CGT / GSC
- Text output with banner + ANSI color (auto-disables if not a TTY, or --no-color)
- One-line log output (--one-line) and forced one-line minimal (--quiet)
- JSON output (--json), optionally compact with --one-line/--quiet
- Request ID:
  * accepts --request-id
  * otherwise reads inbound X-Request-ID from environment (common proxy style)
  * otherwise auto-generates
  * supports --rid-prefix and auto-detect default prefix
- Propagates request id downstream:
  * quote API request includes X-Request-ID header

Depends on: sw_time.py (same directory or installed module)
Requires: Python 3.9+ (zoneinfo)
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
import urllib.request
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from zoneinfo import ZoneInfo

from sw_time import (
    STAR_WARS_RELEASE_UNIX,
    bby_to_gsc,
    datetime_to_cgt,
    datetime_to_swet,
    format_cgt,
)

DEFAULT_TZ = "America/Los_Angeles"
DEFAULT_FACT = "Han shot first."
DEFAULT_QUOTE_URL = "http://swquotesapi.digitaljedi.dk/api/SWQuote/RandomStarWarsQuote"

# Common env var names seen behind proxies / gateways
ENV_X_REQUEST_ID_CANDIDATES = (
    "X_REQUEST_ID",
    "X-REQUEST-ID",
    "HTTP_X_REQUEST_ID",
    "HTTP_X_REQUEST_ID".lower(),
    "REQUEST_ID",
)


# -------------------------
# Color helpers
# -------------------------

class Ansi:
    RESET = "\033[0m"
    DIM = "\033[2m"
    BOLD = "\033[1m"

    FG_CYAN = "\033[36m"
    FG_GREEN = "\033[32m"
    FG_YELLOW = "\033[33m"
    FG_MAGENTA = "\033[35m"


def _supports_color(stream) -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("TERM", "") in ("", "dumb"):
        return False
    return hasattr(stream, "isatty") and stream.isatty()


def _c(text: str, code: str, enable: bool) -> str:
    return f"{code}{text}{Ansi.RESET}" if enable else text


# -------------------------
# Banner
# -------------------------

BANNER = r"""
   _   _       _                 _      _______ _                           _
  | | | |     | |               | |    |__   __(_)                         | |
  | |_| | ___ | | ___  _ __   __| | ______| |   _ _ __ ___   ___  ___  __ _| |_ __ _ _ __ ___  _ __
  |  _  |/ _ \| |/ _ \| '_ \ / _` |______| |  | | '_ ` _ \ / _ \/ __|/ _` | __/ _` | '_ ` _ \| '_ \
  | | | | (_) | | (_) | | | | (_| |      | |  | | | | | | |  __/\__ \ (_| | || (_| | | | | | | |_) |
  \_| |_/\___/|_|\___/|_| |_|\__,_|      |_|  |_|_| |_| |_|\___||___/\__,_|\__\__,_|_| |_| |_| .__/
                                                                                                | |
                                                                                                |_|
""".strip("\n")


# -------------------------
# Request ID helpers
# -------------------------

def _read_inbound_x_request_id() -> Optional[str]:
    for k in ENV_X_REQUEST_ID_CANDIDATES:
        v = os.environ.get(k)
        if v and v.strip():
            return v.strip()
    return None


def _gen_request_id(mode: str) -> str:
    """
    Generate a request id.
    - uuid: UUIDv4
    - short: url-safe short id (12 chars)
    """
    if mode == "uuid":
        return str(uuid.uuid4())
    if mode == "short":
        return secrets.token_urlsafe(9)[:12]
    raise ValueError(f"Unknown request-id mode: {mode!r}")


def _auto_prefix(args: argparse.Namespace) -> str:
    """
    Auto-detect prefix when --rid-prefix isn't supplied.

    Heuristic:
    - If --json: treat as API-ish => "api-"
    - Else if --quiet or --one-line: treat as CLI/curl-ish => "curl-"
    - Else: treat as web UI-ish => "web-"
    """
    if args.json:
        return "api-"
    if args.quiet or args.one_line:
        return "curl-"
    return "web-"


def _final_request_id(args: argparse.Namespace) -> str:
    """
    Determine request id precedence:
    1) --request-id
    2) inbound X-Request-ID from env
    3) auto-generated (with prefix)
    """
    rid = args.request_id or _read_inbound_x_request_id()
    prefix = args.rid_prefix if args.rid_prefix is not None else _auto_prefix(args)
    # Normalize prefix: allow empty; ensure it ends with '-' if non-empty and not already.
    if prefix and not prefix.endswith("-"):
        prefix = prefix + "-"
    if rid:
        # If caller supplied an id and also a prefix, don't double-prefix.
        # Only prefix if rid doesn't already begin with prefix.
        if prefix and not rid.startswith(prefix):
            return f"{prefix}{rid}"
        return rid
    return f"{prefix}{_gen_request_id(args.request_id_mode)}"


# -------------------------
# Optional inputs: fact-file, quote API
# -------------------------

def _read_facts(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f.readlines()]
    return [ln for ln in lines if ln and not ln.lstrip().startswith("#")]


def _pick_fact(extra_facts: list[str], unix: int) -> Optional[str]:
    """
    Deterministic rotation: choose based on unix seconds.
    """
    if not extra_facts:
        return None
    idx = unix % len(extra_facts)
    return extra_facts[idx]


def _fetch_quote(url: str, request_id: str, timeout_s: float = 1.5) -> Optional[str]:
    """
    Fetch a random Star Wars quote. If it fails, return None.
    Propagates request id via X-Request-ID header.
    """
    try:
        headers = {
            "User-Agent": "holonet-stamp/1.0",
            "X-Request-ID": request_id,
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        data = json.loads(raw)
        quote = data.get("starWarsQuote")
        if isinstance(quote, str) and quote.strip():
            return quote.strip()
    except Exception:
        return None
    return None


# -------------------------
# Core payload / rendering
# -------------------------

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def build_payload(
    now_utc: datetime,
    tz_name: str,
    include_sw: bool,
    epoch_mode: str,
    request_id: str,
    quote: Optional[str] = None,
    extra_fact: Optional[str] = None,
) -> Dict[str, Any]:
    unix = int(now_utc.timestamp())

    payload: Dict[str, Any] = {
        "request_id": request_id,
        "x_request_id": request_id,  # explicitly called out for headers/logging symmetry
        "fact": DEFAULT_FACT,        # always present
        "time": {
            "utc": now_utc.isoformat().replace("+00:00", "Z"),
            "local": now_utc.astimezone(ZoneInfo(tz_name)).isoformat(),
            "tz": tz_name,
        },
        "unix": unix,
    }

    if extra_fact:
        payload["extra_fact"] = extra_fact
    if quote:
        payload["quote"] = quote

    if include_sw:
        swet = datetime_to_swet(now_utc)
        cgt = datetime_to_cgt(now_utc, mode=epoch_mode)

        payload["sw"] = {
            "swet": swet,
            "cgt": asdict(cgt),
            "cgt_str": format_cgt(cgt),
            # GSC is year-only; we map CGT.year -> a year label for context
            "gsc_year": bby_to_gsc(cgt.year),
            "cgt_epoch_mode": epoch_mode,
            "swet_at_unix_epoch": -STAR_WARS_RELEASE_UNIX,
        }

    return payload


def render_one_line(payload: Dict[str, Any]) -> str:
    dt_utc = datetime.fromisoformat(payload["time"]["utc"].replace("Z", "+00:00"))
    unix = payload["unix"]
    local_dt = datetime.fromisoformat(payload["time"]["local"])
    tz_name = payload["time"]["tz"]
    rid = payload["request_id"]

    parts = [
        f"rid={rid}",
        f'fact="{payload["fact"]}"',
        f"utc={dt_utc:%Y-%m-%dT%H:%M:%SZ}",
        f"unix={unix}",
        f"local={local_dt:%Y-%m-%dT%H:%M:%S}{local_dt:%z}",
        f"tz={tz_name}",
    ]
    if "extra_fact" in payload:
        parts.append(f'extra_fact="{payload["extra_fact"]}"')
    if "quote" in payload:
        parts.append(f'quote="{payload["quote"]}"')
    if "sw" in payload:
        sw = payload["sw"]
        parts.append(f"swet={sw['swet']}")
        parts.append(f'cgt="{sw["cgt_str"]}"')
        parts.append(f"gsc={sw['gsc_year']}")
        parts.append(f"mode={sw['cgt_epoch_mode']}")
    return " ".join(parts)


def render_pretty_text(payload: Dict[str, Any], color: bool, banner: bool) -> str:
    dt_utc = datetime.fromisoformat(payload["time"]["utc"].replace("Z", "+00:00"))
    dt_local = datetime.fromisoformat(payload["time"]["local"])
    unix = payload["unix"]
    rid = payload["request_id"]

    out = []
    if banner:
        out.append(_c(BANNER, Ansi.FG_CYAN, color))
        out.append("")

    out.append(f"{_c('Request', Ansi.BOLD, color)}: {rid}")
    out.append(f"{_c('X-Request-ID', Ansi.DIM, color)}: {rid}")
    out.append(f"{_c('Fact', Ansi.BOLD, color)}: {payload['fact']}")
    if "extra_fact" in payload:
        out.append(f"{_c('Extra', Ansi.BOLD, color)}: {payload['extra_fact']}")
    if "quote" in payload:
        out.append(f"{_c('Quote', Ansi.BOLD, color)}: {payload['quote']}")
    out.append("")

    out.append(_c("Real Time:", Ansi.FG_GREEN, color))
    out.append(f"  UTC   : {dt_utc:%a %Y-%m-%d %H:%M:%S} UTC")
    out.append(f"  Local : {dt_local:%a %Y-%m-%d %H:%M:%S} {dt_local:%Z}")
    out.append("")

    out.append(_c("Unix Epoch:", Ansi.FG_YELLOW, color))
    out.append(f"  Unix  : {unix}")
    out.append("")

    if "sw" in payload:
        sw = payload["sw"]
        out.append(_c("Star Wars Time:", Ansi.FG_MAGENTA, color))
        out.append(f"  SWET  : {sw['swet']}")
        out.append(f"  CGT   : {sw['cgt_str']}")
        out.append(f"  GSC   : {sw['gsc_year']}")
        out.append(f"  Mode  : {sw['cgt_epoch_mode']}")

    return "\n".join(out)


# -------------------------
# CLI
# -------------------------

def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="holonet-stamp",
        description="Print a Holonet timestamp (UTC/local/unix) with optional SW time (SWET/CGT).",
    )

    p.add_argument("--tz", default=DEFAULT_TZ, help="IANA timezone for Local (default: America/Los_Angeles).")

    p.add_argument("--sw-time", action="store_true", help="Include Star Wars time block (SWET, CGT, GSC).")
    p.add_argument("--epoch-mode", choices=["current", "legacy"], default="current", help="CGT epoch mode.")

    p.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    p.add_argument("--one-line", action="store_true", help="Emit a compact single-line log format.")
    p.add_argument("--quiet", action="store_true", help="Force one-line minimal output (no banner/pretty).")

    p.add_argument("--no-banner", action="store_true", help="Disable ASCII banner (text mode only).")
    p.add_argument("--no-color", action="store_true", help="Disable ANSI color in text output.")

    p.add_argument("--fact-file", help="Path to a newline-delimited file of extra facts (optional).")
    p.add_argument("--quote", action="store_true", help="Fetch a random Star Wars quote (best-effort).")
    p.add_argument("--quote-url", default=DEFAULT_QUOTE_URL, help="Override quote API URL.")

    # Request-id / X-Request-ID support
    p.add_argument("--request-id", help="Use this request id (overrides inbound X-Request-ID env).")
    p.add_argument(
        "--request-id-mode",
        choices=["uuid", "short"],
        default="uuid",
        help="Auto request id format when not provided (default: uuid).",
    )
    p.add_argument(
        "--rid-prefix",
        default=None,
        help="Prefix for request id (e.g. api-, curl-, web-). If omitted, auto-detected.",
    )
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    now_utc = _now_utc()
    unix = int(now_utc.timestamp())

    request_id = _final_request_id(args)

    extra_fact = None
    if args.fact_file:
        facts = _read_facts(args.fact_file)
        extra_fact = _pick_fact(facts, unix)

    quote = _fetch_quote(args.quote_url, request_id=request_id) if args.quote else None

    payload = build_payload(
        now_utc=now_utc,
        tz_name=args.tz,
        include_sw=args.sw_time,
        epoch_mode=args.epoch_mode,
        request_id=request_id,
        quote=quote,
        extra_fact=extra_fact,
    )

    if args.json:
        compact = args.one_line or args.quiet
        txt = json.dumps(
            payload,
            indent=None if compact else 2,
            separators=(",", ":") if compact else None,
        )
        print(txt)
        return 0

    if args.quiet or args.one_line:
        print(render_one_line(payload))
        return 0

    color = (not args.no_color) and _supports_color(sys.stdout)
    banner = not args.no_banner
    print(render_pretty_text(payload, color=color, banner=banner))
    return 0


def main_cli() -> None:
    raise SystemExit(main(sys.argv[1:]))


if __name__ == "__main__":
    main_cli()

