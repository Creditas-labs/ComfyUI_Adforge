"""Top-level package for comfyui_adforge."""

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
]

__author__ = """Creditas-labs"""
__email__ = "martech1@creditas.com"
__version__ = "0.0.1"

import os

# mymodule/__init__.py
import sys

if not hasattr(sys, "_called_from_test"):
    # Add the 'src' directory to the Python path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
    from comfyui_adforge.nodes import (
        NODE_CLASS_MAPPINGS,
        NODE_DISPLAY_NAME_MAPPINGS,
    )
