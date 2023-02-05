#
# Copyright (C) 2023 Scott Dixon
# This software is distributed under the terms of the MIT License.
#
"""
    Command-line entrypoint.
"""

import sys

from .cli import main

sys.exit(main())
