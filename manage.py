#!/usr/bin/env python
"""
Django management utility.

Ez a fájl indítja a Django management parancsokat:
    python manage.py runserver
    python manage.py migrate
    python manage.py makemigrations
"""

import os
import sys


def main():
    """Django parancsok futtatása."""

    # Django settings modul
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vpnreport.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django nincs telepítve vagy a virtualenv nincs aktiválva."
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
