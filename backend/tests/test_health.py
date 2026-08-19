"""Basic tests for the Phase 1 application foundation."""

import unittest

from app.main import health_check


class HealthCheckTests(unittest.TestCase):
    def test_health_check_returns_expected_payload(self) -> None:
        self.assertEqual(
            health_check(),
            {"status": "ok", "service": "XYZ AI"},
        )
