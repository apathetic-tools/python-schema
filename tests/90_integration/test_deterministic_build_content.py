# tests/90_integration/test_deterministic_build_content.py
"""Integration tests for deterministic build output content.

These tests verify that builds produce identical, reproducible output
when timestamps are disabled. We test both:
1. Basic tool functionality with sample code (to verify tools work)
2. Project-specific builds with our actual code (to verify our config/code works)

Tests serger (stitched .py) builds.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from tests.utils.constants import PROJ_ROOT


# ============================================================================
# Basic tool tests with sample code (verify tools work correctly)
# ============================================================================


def test_serger_build_with_sample_code_is_deterministic(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that serger produces deterministic output with sample code.

    This verifies the tool itself works correctly before testing our code.
    """
    # --- setup ---
    # Create a minimal test package structure
    pkg_dir = tmp_path / "src" / "testpkg"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "__init__.py").write_text('"""Test package."""\n')
    (pkg_dir / "module.py").write_text('"""Test module."""\n\nvalue = 42\n')

    # Create serger config with disable_build_timestamp
    config = tmp_path / ".serger.jsonc"
    config_data = {
        "package": "testpkg",
        "include": ["src/testpkg/**/*.py"],
        "out": "dist/testpkg.py",
        "disable_build_timestamp": True,
    }
    config.write_text(json.dumps(config_data, indent=2))

    monkeypatch.chdir(tmp_path)

    # Use temp directories for builds
    with tempfile.TemporaryDirectory() as build_dir1:
        build_path1 = Path(build_dir1)
        output_file1 = build_path1 / "testpkg.py"

        # --- execute: first build ---
        result1 = subprocess.run(  # noqa: S603
            [
                sys.executable,
                "-m",
                "serger.__main__",
                "--config",
                str(config),
                "--out",
                str(output_file1),
            ],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result1.returncode == 0, (
            f"First build failed: {result1.stdout}\n{result1.stderr}"
        )
        assert output_file1.exists(), "First build output file not created"

        # --- execute: second build ---
        with tempfile.TemporaryDirectory() as build_dir2:
            build_path2 = Path(build_dir2)
            output_file2 = build_path2 / "testpkg.py"

            result2 = subprocess.run(  # noqa: S603
                [
                    sys.executable,
                    "-m",
                    "serger.__main__",
                    "--config",
                    str(config),
                    "--out",
                    str(output_file2),
                ],
                cwd=tmp_path,
                capture_output=True,
                text=True,
                check=False,
            )
            assert result2.returncode == 0, (
                f"Second build failed: {result2.stdout}\n{result2.stderr}"
            )
            assert output_file2.exists(), "Second build output file not created"

            # --- verify: outputs are identical ---
            content1 = output_file1.read_bytes()
            content2 = output_file2.read_bytes()
            assert content1 == content2, (
                "Two builds with disable_build_timestamp=True should produce "
                "identical output"
            )


# ============================================================================
# Project-specific tests with our actual code (verify our config/code works)
# ============================================================================


def test_serger_build_is_deterministic() -> None:
    """Test that two serger builds of the project produce identical output.

    This test:
    1. Builds the project using the actual .serger.jsonc config
    2. Deletes the output and builds again
    3. Verifies both builds produce identical output (with disable_build_timestamp)
    """
    # --- setup ---
    config_file = PROJ_ROOT / ".serger.jsonc"

    # Use temp directories for builds
    with tempfile.TemporaryDirectory() as build_dir1:
        build_path1 = Path(build_dir1)
        output_file1 = build_path1 / "apathetic_utils.py"

        # --- execute: first build with disable_build_timestamp ---
        result1 = subprocess.run(  # noqa: S603
            [
                sys.executable,
                "-m",
                "serger.__main__",
                "--config",
                str(config_file),
                "--disable-build-timestamp",
                "--out",
                str(output_file1),
            ],
            cwd=PROJ_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result1.returncode == 0, (
            f"First build failed: {result1.stdout}\n{result1.stderr}"
        )
        assert output_file1.exists(), "First build output file not created"

        # --- execute: second build with disable_build_timestamp ---
        with tempfile.TemporaryDirectory() as build_dir2:
            build_path2 = Path(build_dir2)
            output_file2 = build_path2 / "apathetic_utils.py"

            result2 = subprocess.run(  # noqa: S603
                [
                    sys.executable,
                    "-m",
                    "serger.__main__",
                    "--config",
                    str(config_file),
                    "--disable-build-timestamp",
                    "--out",
                    str(output_file2),
                ],
                cwd=PROJ_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            assert result2.returncode == 0, (
                f"Second build failed: {result2.stdout}\n{result2.stderr}"
            )
            assert output_file2.exists(), "Second build output file not created"

            # --- verify: outputs are identical ---
            content1 = output_file1.read_bytes()
            content2 = output_file2.read_bytes()
            assert content1 == content2, (
                "Two builds of the project with --disable-build-timestamp should "
                "produce identical output. This ensures reproducible builds of "
                "our actual code."
            )
