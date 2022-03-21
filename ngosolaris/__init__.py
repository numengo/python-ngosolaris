# -*- coding: utf-8 -*-

"""Top-level package for NgoSolaris."""

__author__ = """Cedric R, 64 CB Nord"""
__email__ = 'solaris64cotebasquenord@protonmail.com'
__version__ = '1.0.5'

from simple_settings import LazySettings
settings = LazySettings('ngosolaris.config.settings')

# PROTECTED REGION ID(ngosolaris.init) ENABLED START
from ngoschema.loaders import register_module
register_module('ngosolaris')

from .ngosolaris import *
__all__ = [
    'settings',
]
# PROTECTED REGION END
