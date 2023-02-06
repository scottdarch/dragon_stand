#
# Copyright (C) 2023 Scott Dixon
# This software is distributed under the terms of the MIT License.
#
"""
    Command-line entrypoint.
"""

import sys
import asyncio

from .cli import main

loop = asyncio.get_event_loop()
sys.exit(loop.run_until_complete(main()))
