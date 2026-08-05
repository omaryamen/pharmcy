"""Wait for the database to become available before starting the app.

Used by the container entrypoint to avoid race conditions with the
PostgreSQL service on first boot.
"""

from __future__ import annotations

import os
import sys
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

import django  # noqa: E402

django.setup()

from django.db import connection  # noqa: E402
from django.db.utils import OperationalError  # noqa: E402

MAX_ATTEMPTS = 60
RETRY_DELAY_SECONDS = 1


def wait_for_database() -> None:
    attempts = 0
    while True:
        try:
            connection.ensure_connection()
            print("[wait_for_db] Database is ready.")
            return
        except OperationalError as exc:
            attempts += 1
            if attempts >= MAX_ATTEMPTS:
                print(f"[wait_for_db] Database not reachable after {MAX_ATTEMPTS} attempts: {exc}", file=sys.stderr)
                sys.exit(1)
            print(f"[wait_for_db] Database not ready (attempt {attempts}/{MAX_ATTEMPTS}), retrying...")
            time.sleep(RETRY_DELAY_SECONDS)


if __name__ == "__main__":
    wait_for_database()
