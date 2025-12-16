"""
Behavioral tests for task-002: Create tools package foundation.

These tests verify that the tools package:
1. Can be imported successfully
2. Has a properly defined __all__ attribute
3. Provides a clean namespace for tool modules
4. Follows Python package conventions
"""

import importlib
import sys
from pathlib import Path


def test_tools_package_can_be_imported():
    """Test that the tools package can be imported without errors."""
    try:
        import maid_runner_mcp.tools

        # Assert that the import succeeded and module is in sys.modules
        assert "maid_runner_mcp.tools" in sys.modules
        assert maid_runner_mcp.tools is not None
    except ImportError as e:
        raise AssertionError(f"Failed to import maid_runner_mcp.tools package: {e}") from e


def test_tools_package_has_all_attribute():
    """Test that the tools package defines __all__ for public exports."""
    import maid_runner_mcp.tools

    # Assert __all__ exists
    assert hasattr(maid_runner_mcp.tools, "__all__"), "tools package must define __all__ attribute"

    # Assert __all__ is a list or tuple (standard Python convention)
    all_attr = maid_runner_mcp.tools.__all__
    assert isinstance(
        all_attr, (list, tuple)
    ), f"__all__ must be a list or tuple, got {type(all_attr).__name__}"


def test_tools_package_all_is_iterable():
    """Test that __all__ attribute can be iterated for exports."""
    import maid_runner_mcp.tools

    all_attr = maid_runner_mcp.tools.__all__

    # Assert we can iterate over __all__
    try:
        all_list = list(all_attr)
        assert isinstance(all_list, list), "__all__ must be iterable"
    except TypeError as e:
        raise AssertionError(f"__all__ is not iterable: {e}") from e


def test_tools_package_all_contains_only_strings():
    """Test that all exports in __all__ are valid string identifiers."""
    import maid_runner_mcp.tools

    all_attr = maid_runner_mcp.tools.__all__

    # Assert all items are strings
    for item in all_attr:
        assert isinstance(
            item, str
        ), f"All items in __all__ must be strings, found {type(item).__name__}: {item}"

        # Assert strings are valid Python identifiers
        assert item.isidentifier() or "." in item, f"Export name must be a valid identifier: {item}"


def test_tools_package_file_exists():
    """Test that the tools package __init__.py file exists at the expected location."""
    # Get the package's file path
    import maid_runner_mcp.tools

    package_file = Path(maid_runner_mcp.tools.__file__)

    # Assert the file exists
    assert package_file.exists(), f"Package file does not exist: {package_file}"

    # Assert it's an __init__.py file
    assert (
        package_file.name == "__init__.py"
    ), f"Package file must be __init__.py, got {package_file.name}"

    # Assert it's in the correct location
    assert "src/maid_runner_mcp/tools" in str(
        package_file
    ), f"Package file is not in expected location: {package_file}"


def test_tools_package_has_proper_module_path():
    """Test that the tools package has the correct module path."""
    import maid_runner_mcp.tools

    # Assert module name is correct
    assert (
        maid_runner_mcp.tools.__name__ == "maid_runner_mcp.tools"
    ), f"Package __name__ is incorrect: {maid_runner_mcp.tools.__name__}"

    # Assert it's a package (has __path__ attribute)
    assert hasattr(
        maid_runner_mcp.tools, "__path__"
    ), "tools must be a package (should have __path__ attribute)"


def test_tools_package_can_be_reloaded():
    """Test that the tools package can be reloaded without errors."""
    import maid_runner_mcp.tools

    # Store original __all__
    original_all = maid_runner_mcp.tools.__all__

    # Reload the module
    reloaded = importlib.reload(maid_runner_mcp.tools)

    # Assert reload succeeded
    assert reloaded is not None
    assert hasattr(reloaded, "__all__")

    # Assert __all__ is consistent after reload
    assert type(original_all) is type(reloaded.__all__), "__all__ type changed after reload"


def test_tools_package_exports_are_accessible():
    """Test that all items declared in __all__ are actually accessible."""
    import maid_runner_mcp.tools

    all_attr = maid_runner_mcp.tools.__all__

    # Assert each export in __all__ is accessible
    for export_name in all_attr:
        # Handle dotted names (e.g., "submodule.Class")
        if "." in export_name:
            # For dotted names, just verify the string format
            assert isinstance(export_name, str) and export_name.count(".") >= 1
        else:
            # For simple names, verify they're accessible as attributes
            assert hasattr(
                maid_runner_mcp.tools, export_name
            ), f"Export '{export_name}' declared in __all__ but not accessible"
