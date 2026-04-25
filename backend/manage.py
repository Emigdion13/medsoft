#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Fix Django 5.1 bug: Constraint.max_name_length is missing
from django.db.models.constraints import BaseConstraint, UniqueConstraint
from django.db.models import Index
if not hasattr(BaseConstraint, 'max_name_length'):
    BaseConstraint.max_name_length = 63
if not hasattr(Index, 'max_name_length'):
    Index.max_name_length = 63

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
