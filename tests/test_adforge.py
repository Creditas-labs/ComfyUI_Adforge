#!/usr/bin/env python

"""Tests for `comfyui_adforge` package."""

import os
import sys

import pytest

from src.comfyui_adforge.nodes import Example

# Add the project root directory to Python path
# This allows the tests to import the project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# Get the ComfyUI path from your "COMFYUI_CODE_PATH" environment variable
comfy_path = os.environ.get("COMFYUI_CODE_PATH")

# If a path is found, add ComfyUI root and custom_nodes to the import path
if comfy_path and os.path.isdir(comfy_path):
    sys.path.append(comfy_path)
    sys.path.append(os.path.join(comfy_path, "custom_nodes"))
    print(f"\nAdded ComfyUI path: {comfy_path}")
else:
    print("\n---")
    print("Warning: COMFYUI_CODE_PATH env var not set or invalid.")
    print("Tests requiring 'comfy_api' will fail.")
    print("---")


@pytest.fixture
def example_node():
    """Fixture to create an Example node instance."""
    return Example()


def test_example_node_initialization(example_node):
    """Test that the node can be instantiated."""
    assert isinstance(example_node, Example)


def test_return_types():
    """Test the node's metadata."""
    assert Example.RETURN_TYPES == ("IMAGE",)
    assert Example.FUNCTION == "test"
    assert Example.CATEGORY == "Example"
