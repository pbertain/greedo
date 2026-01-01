"""
sw_time.py — Star Wars time/calendar conversion utilities.

Includes:
- CGT (Combine Galactic Time) <-> real UTC datetime
  * 365-day years, day 1..365, 24h days
  * epoch modes:
      - "current": CGT 0/1 00:00:00 == 1998-12-03 07:00:00 UTC
      - "legacy" : CGT 0/1 00:00:00 == 1998-12-03 00:00:00 UTC
- Timezone conversions (IANA tz names, e.g. America/Los_Angeles for PT)
- SWET (Star Wars Epoch Time): seconds since Star Wars release
  * SWET 0 == 1977-05-25 00:00:00 UTC
- Year-system conversions (Crystal Odenkirk page logic) via BBY as the base:
  * GSC, BTC, GrS, TYA, Ruusan, LY

Requires: Python 3.9+ (zoneinfo)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Literal

# -----------------------------
# Types / constants
# -----------------------------

EpochMode = Literal["current", "legacy"]

# CGT epoch offsets (Unix seconds for CGT Year 0 Day 1 00:00:00)
# current: 1998-12-037:00:00 UTC
CGT_EPOCH_OFFSET_CURRENT = 912_668_400
# legacy:  1998-12-03 00:00:00 UTC
CGT_EPOCH_OFFSET_LEGACY = 912_643_200

SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 60 * 60
SECONDS_PER_DAY = 24 * 60 * 60
DAYS_PER_CGT_YEAR = 365
SECONDS_PER_CGT_YEAR = DAYS_PER_CGT_YEAR * SECONDS_PER_DAY

# Star Wars Epoch Time (SWET)
# SWET 0 = theatrical release date anchor (chosen for determinism): 1977-05-25 00:00:00 UTC
STAR_WARS_RELEASE_UTC = datetime(1977, 5, 25, 0, 0, 0, tzinfo=timezone.utc)
STAR_WARS_RELEASE_UNIX = int(STAR_WARS_RELEASE_UTC.timestamp())  # 233_366_400


def _epoch_offset(mode: EpochMode) -> int:
    if mode == "current":
        return CGT_EPOCH_OFFSET_CURRENT
    if mode == "legacy":
        return CGT_EPOCH_OFFSET_LEGACY
    raise ValueError(f"Unknown epoch mode: {mode!r}")


# -----------------------------
# CGT data model
# -----------------------------

@dataclass(frozen=True)
class CGT:
    """CGT timestamp: (year, day-of-year 1..365, hour, minute, second)."""
    year: int
    day: int
    hour: int
    minute: int
    second: int

    def __post_init__(self) -> None:
        if not (1 <= self.day <= 365):
            raise ValueError(f"CGT.day must be 1..365, got {self.day}")
        if not (0 <= self.hour <= 23):
            raise ValueError(f"CGT.hour must be 0..23, got {self.hour}")
        if not (0 <= self.minute <= 59):
            raise ValueError(f"CGT.minute must be 0..59, got {self.minute}")
        if not (0 <= self.second <= 59):
            raise ValueError(f"CGT.second must be 0..59, got {self.second}")

    def to_cgt_seconds(self) -> int:
        """
        Convert CGT fields to "CGT seconds" as in the JS:
          year*365days + (day-1)*1day + time-of-day.
        """
        return (
            int(self.year) * SECONDS_PER_CGT_YEAR
            + int(self.day - 1) * SECONDS_PER_DAY
            + int(self.hour) * SECONDS_PER_HOUR
            + int(self.minute) * SECONDS_PER_MINUTE
            + int(self.second)
        )


def _cgt_from_seconds(cgt_seconds: int) -> CGT:
    """
    Deterministic decomposition of seconds into CGT fields (supports negatives).
    """
    total_days = cgt_seconds // SECONDS_PER_DAY  # floor division
    sod = cgt_seconds - total_days * SECONDS_PER_DAY  # 0..86399

    hour = sod // SECONDS_PER_HOUR
    minute = (sod // SECONDS_PER_MINUTE) % 60
    second = sod % 60

    doy0 = total_days % DAYS_PER_CGT_YEAR  # 0..364
    day = doy0 + 1

    year = total_days // DAYS_PER_CGT_YEAR
    return CGT(year=year, day=day, hour=hour, minute=minute, second=second)


# -----------------------------
# CGT <-> datetime (UTC / tz)
# -----------------------------

def cgt_to_datetime_utc(cgt: CGT, mode: EpochMode = "current") -> datetime:
    """CGT -> UTC datetime."""
    unix_seconds = cgt.to_cgt_seconds() + _epoch_offset(mode)
    return datetime.fromtimestamp(unix_seconds, tz=timezone.utc)


def datetime_to_cgt(dt: datetime, mode: EpochMode = "current") -> CGT:
    """
    datetime -> CGT.
    - If dt is timezone-aware, converted to UTC.
    - If dt is naive, treated as UTC.
    """
    if dt.tzinfo is None:
        dt_utc = dt.replace(tzinfo=timezone.utc)
    else:
        dt_utc = dt.astimezone(timezone.utc)

    unix_seconds = int(dt_utc.timestamp())
    cgt_seconds = unix_seconds - _epoch_offset(mode)
    return _cgt_from_seconds(cgt_seconds)


def cgt_to_timezone(cgt: CGT, tz_name: str, mode: EpochMode = "current") -> datetime:
    """
    CGT -> datetime in an IANA timezone.
    Example tz_name: 'America/Los_Angeles' (PT; PST/PDT automatically).
    """
    dt_utc = cgt_to_datetime_utc(cgt, mode=mode)
    return dt_utc.astimezone(ZoneInfo(tz_name))


def timezone_to_cgt(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int,
    tz_name: str,
    mode: EpochMode = "current",
) -> CGT:
    """Local clock fields in tz_name -> CGT."""
    tz = ZoneInfo(tz_name)
    dt_local = datetime(year, month, day, hour, minute, second, tzinfo=tz)
    return datetime_to_cgt(dt_local, mode=mode)


# -----------------------------
# SWET (Star Wars Epoch Time)
# -----------------------------

def datetime_to_swet(dt: datetime) -> int:
    """
    datetime -> SWET seconds, where SWET 0 = 1977-05-25 00:00:00 UTC.
    - If dt is timezone-aware, converted to UTC.
    - If dt is naive, treated as UTC.
    """
    if dt.tzinfo is None:
        dt_utc = dt.replace(tzinfo=timezone.utc)
    else:
        dt_utc = dt.astimezone(timezone.utc)
    return int(dt_utc.timestamp()) - STAR_WARS_RELEASE_UNIX


def swet_to_datetime_utc(swet: int) -> datetime:
    """SWET seconds -> UTC datetime."""
    return datetime.fromtimestamp(swet + STAR_WARS_RELEASE_UNIX, tz=timezone.utc)


def cgt_to_swet(cgt: CGT, mode: EpochMode = "current") -> int:
    """CGT -> SWET seconds."""
    return datetime_to_swet(cgt_to_datetime_utc(cgt, mode=mode))


def swet_to_cgt(swet: int, mode: EpochMode = "current") -> CGT:
    """SWET seconds -> CGT."""
    return datetime_to_cgt(swet_to_datetime_utc(swet), mode=mode)


# -----------------------------
# Pretty formatting helpers
# -----------------------------

def format_cgt(cgt: CGT) -> str:
    return f"CGT {cgt.year:02d} {cgt.day:03d} {cgt.hour:02d}:{cgt.minute:02d}:{cgt.second:02d}"


def format_dt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S %Z%z")


# -----------------------------
# Year-system conversions (Crystal Odenkirk logic)
# Everything is routed through BBY as the base year number.
# Note: these are YEAR conversions only (no months/days).
# -----------------------------

def gsc_to_bby(gsc: float) -> float:
    # 0 GSC == 25043 BBY  => BBY = GSC - 25043
    return gsc - 25043


def bby_to_gsc(bby: float) -> float:
    return bby + 25043


def btc_to_bby(btc: float) -> float:
    # 0 BTC == 3653 BBY
    return btc - 3653


def bby_to_btc(bby: float) -> float:
    return bby + 3653


def grs_to_bby(grs: float) -> float:
    # 0 GrS == 35 BBY
    return grs - 35


def bby_to_grs(bby: float) -> float:
    return bby + 35


def tya_to_bby(tya: float) -> float:
    # 0 TYA == 36453 BBY
    return tya - 36453


def bby_to_tya(bby: float) -> float:
    return bby + 36453


def ruus_to_bby(ruus: float) -> float:
    # 0 Ruusan Reformation == 1000 BBY
    return ruus - 1000


def bby_to_ruus(bby: float) -> float:
    return bby + 1000


def ly_to_bby(ly: float) -> float:
    # page uses 3277 offset
    return ly - 3277


def bby_to_ly(bby: float) -> float:
    return bby + 3277


# -----------------------------
# Demo (optional)
# -----------------------------
if __name__ == "__main__":
    demo_cgt = CGT(year=27, day=36, hour=11, minute=37, second=1)
    dt_utc = cgt_to_datetime_utc(demo_cgt, mode="current")
    dt_pt = cgt_to_timezone(demo_cgt, "America/Los_Angeles", mode="current")

    print(format_cgt(demo_cgt))
    print("UTC:", format_dt(dt_utc))
    print("PT :", format_dt(dt_pt))

    sw_release_cgt = datetime_to_cgt(STAR_WARS_RELEASE_UTC, mode="current")
    print("SW release UTC:", format_dt(STAR_WARS_RELEASE_UTC))
    print("SW release CGT:", format_cgt(sw_release_cgt))
    print("SW release SWET:", datetime_to_swet(STAR_WARS_RELEASE_UTC))

