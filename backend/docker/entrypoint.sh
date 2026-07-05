#!/usr/bin/env sh
set -eu
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings}"

echo "Waiting for PostgreSQL..."
python - <<'PY'
import time

from django.db import connection
from django.db.utils import OperationalError

for attempt in range(1, 31):
    try:
        connection.ensure_connection()
        break
    except OperationalError as error:
        if attempt == 30:
            raise
        print(f"Database unavailable ({attempt}/30): {error}")
        time.sleep(2)
PY

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static assets..."
python manage.py collectstatic --noinput --clear

exec "$@"
