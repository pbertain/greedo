import unittest
from datetime import datetime, timezone

from sw_time import (
    CGT,
    cgt_to_datetime_utc,
    datetime_to_cgt,
    cgt_to_timezone,
    datetime_to_swet,
    swet_to_datetime_utc,
    STAR_WARS_RELEASE_UTC,
    STAR_WARS_RELEASE_UNIX,
    bby_to_gsc,
    gsc_to_bby,
)


class TestStarWarsTime(unittest.TestCase):
    # -----------------
    # CGT epoch tests
    # -----------------

    def test_cgt_epoch_current(self):
        # CGT(0,1,0,0,0) -> 1998-12-03 07:00:00 UTC
        cgt = CGT(0, 1, 0, 0, 0)
        dt = cgt_to_datetime_utc(cgt, mode="current")
        self.assertEqual(dt, datetime(1998, 12, 3, 7, 0, 0, tzinfo=timezone.utc))

    def test_cgt_epoch_legacy(self):
        # CGT(0,1,0,0,0) -> 1998-12-03 00:00:00 UTC
        cgt = CGT(0, 1, 0, 0, 0)
        dt = cgt_to_datetime_utc(cgt, mode="legacy")
        self.assertEqual(dt, datetime(1998, 12, 3, 0, 0, 0, tzinfo=timezone.utc))

    def test_cgt_roundtrip_current(self):
        original = CGT(27, 36, 11, 37, 1)
        dt = cgt_to_datetime_utc(original, mode="current")
        back = datetime_to_cgt(dt, mode="current")
        self.assertEqual(back, original)

    def test_cgt_roundtrip_legacy(self):
        original = CGT(27, 36, 11, 37, 1)
        dt = cgt_to_datetime_utc(original, mode="legacy")
        back = datetime_to_cgt(dt, mode="legacy")
        self.assertEqual(back, original)

    def test_cgt_timezone_conversion_pt(self):
        # Ensure tz conversion is consistent with UTC for the same instant.
        cgt = CGT(0, 1, 0, 0, 0)
        dt_pt = cgt_to_timezone(cgt, "America/Los_Angeles", mode="current")

        # tzinfo.key exists on ZoneInfo objects
        self.assertEqual(dt_pt.tzinfo.key, "America/Los_Angeles")
        self.assertEqual(
            dt_pt.astimezone(timezone.utc),
            datetime(1998, 12, 3, 7, 0, 0, tzinfo=timezone.utc),
        )

    # -----------------
    # SWET tests
    # -----------------

    def test_swet_epoch_is_zero(self):
        self.assertEqual(datetime_to_swet(STAR_WARS_RELEASE_UTC), 0)

    def test_swet_unix_epoch_is_negative(self):
        unix_epoch = datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        # SWET at Unix epoch should be -STAR_WARS_RELEASE_UNIX
        self.assertEqual(datetime_to_swet(unix_epoch), -STAR_WARS_RELEASE_UNIX)
        self.assertEqual(STAR_WARS_RELEASE_UNIX, 233_366_400)

    def test_swet_roundtrip(self):
        dt = datetime(1998, 12, 3, 7, 0, 0, tzinfo=timezone.utc)
        swet = datetime_to_swet(dt)
        self.assertEqual(swet_to_datetime_utc(swet), dt)

    def test_star_wars_release_to_cgt_current(self):
        # This pins down the specific CGT decomposition for the chosen SWET epoch moment.
        # Star Wars Release (1977-05-25 00:00:00 UTC) -> CGT (current mode)
        cgt = datetime_to_cgt(STAR_WARS_RELEASE_UTC, mode="current")
        self.assertEqual((cgt.year, cgt.day, cgt.hour, cgt.minute, cgt.second), (-22, 304, 17, 0, 0))

    # -----------------
    # GSC/BBY year-offset tests
    # -----------------

    def test_gsc_bby_offsets(self):
        # Roundtrip identity for year offsets:
        self.assertEqual(gsc_to_bby(bby_to_gsc(1234)), 1234)
        # Definition checks:
        self.assertEqual(gsc_to_bby(0), -25043)
        self.assertEqual(bby_to_gsc(0), 25043)


if __name__ == "__main__":
    unittest.main(verbosity=2)

