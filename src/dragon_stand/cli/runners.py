#
# Copyright (C) 2023 Scott Dixon
# This software is distributed under the terms of the MIT License.
#
"""
    Command Line Interface
"""
import argparse

class ArgparseRunner:
    
    def __init__(self, args: argparse.Namespace) :
        self._args = args
    
    def run(self) -> None:
        pass
