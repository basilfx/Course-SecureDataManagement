#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # Append path
    sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__))))

    # Set settings file
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phr_cli.settings")

    # Load Django environment
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
