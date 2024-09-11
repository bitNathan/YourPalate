#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import logging


def main():
    # Set up logging
    logging.basicConfig(filename='manage.log', level=logging.INFO)
    logger.info('Starting manage.py')
    
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sample_site.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
    logger.info('Exiting manage.py')


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    main()
