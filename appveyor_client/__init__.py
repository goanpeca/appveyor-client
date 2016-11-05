# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Gonzalo Pena-Castellanos (@goanpeca)
#
# Licensed under the terms of the MIT License
# (See LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Appveyor Python Client."""

from .client import AppveyorClient

VERSION_INFO = (0, 1, 0)
__version__ = '.'.join(map(str, VERSION_INFO))
