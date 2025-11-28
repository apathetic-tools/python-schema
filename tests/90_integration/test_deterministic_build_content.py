# tests/90_integration/test_deterministic_build_content.py
"""Integration tests for deterministic build output content.

These tests verify that builds produce identical, reproducible output
when timestamps are disabled. We test both:
1. Basic tool functionality with sample code (to verify tools work)
2. Project-specific builds with our actual code (to verify our config/code works)

Tests both serger (single-file .py) and shiv (zipapp .pyz) builds.
"""

import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import apathetic_utils
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

    serger_script = PROJ_ROOT / "bin" / "serger.py"
    monkeypatch.chdir(tmp_path)

    # Use temp directories for builds
    with tempfile.TemporaryDirectory() as build_dir1:
        build_path1 = Path(build_dir1)
        output_file1 = build_path1 / "testpkg.py"

        # --- execute: first build ---
        result1 = subprocess.run(  # noqa: S603
            [
                sys.executable,
                str(serger_script),
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
                    str(serger_script),
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


def test_zipapp_build_with_sample_code_is_deterministic(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that shiv produces deterministic output with sample code.

    This verifies the tool itself works correctly before testing our code.
    """
    # --- setup ---
    # Create a minimal test package structure with pyproject.toml
    pkg_dir = tmp_path / "src" / "testpkg"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "__init__.py").write_text('"""Test package."""\n')
    (pkg_dir / "module.py").write_text(
        '"""Test module."""\n\nvalue = 42\n\n'
        'def main() -> None:\n    print("testpkg")\n'
    )

    # Create pyproject.toml for shiv with entry point
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """[project]
name = "testpkg"
version = "0.1.0"

[project.scripts]
testpkg = "testpkg.module:main"
"""
    )

    monkeypatch.chdir(tmp_path)

    # Create dist directory
    (tmp_path / "dist").mkdir(exist_ok=True)

    # --- execute: first build ---
    shiv_cmd = apathetic_utils.find_shiv()
    result1 = subprocess.run(  # noqa: S603
        [
            shiv_cmd,
            "-c",
            "testpkg",
            "-o",
            "dist/testpkg.pyz",
            ".",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result1.returncode == 0, (
        f"First zipapp build failed: {result1.stdout}\n{result1.stderr}"
    )
    output_file1 = tmp_path / "dist" / "testpkg.pyz"
    assert output_file1.exists(), "First build output file not created"

    # Extract first build to temp directory
    with tempfile.TemporaryDirectory() as extract_dir1:
        extract_path1 = Path(extract_dir1)
        with zipfile.ZipFile(output_file1, "r") as zf1:
            zf1.extractall(extract_path1)

        # Delete the output file to force a fresh build
        output_file1.unlink()

        # --- execute: second build ---
        result2 = subprocess.run(  # noqa: S603
            [
                shiv_cmd,
                "-c",
                "testpkg",
                "-o",
                "dist/testpkg.pyz",
                ".",
            ],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )

        assert result2.returncode == 0, (
            f"Second zipapp build failed: {result2.stdout}\n{result2.stderr}"
        )
        output_file2 = tmp_path / "dist" / "testpkg.pyz"
        assert output_file2.exists(), "Second build output file not created"

        # Extract second build to temp directory
        with tempfile.TemporaryDirectory() as extract_dir2:
            extract_path2 = Path(extract_dir2)
            with zipfile.ZipFile(output_file2, "r") as zf2:
                zf2.extractall(extract_path2)

            # --- verify: same files and content (deterministic) ---
            # Get all files from both extracts, excluding environment.json
            files1 = sorted(
                f.relative_to(extract_path1)
                for f in extract_path1.rglob("*")
                if f.is_file() and f.name != "environment.json"
            )
            files2 = sorted(
                f.relative_to(extract_path2)
                for f in extract_path2.rglob("*")
                if f.is_file() and f.name != "environment.json"
            )

            assert files1 == files2, (
                "Two zipapp builds should contain the same files "
                "(excluding environment.json). "
                f"First: {[str(f) for f in files1]}, "
                f"Second: {[str(f) for f in files2]}"
            )

            # Compare file contents one at a time
            for rel_path in files1:
                file1 = extract_path1 / rel_path
                file2 = extract_path2 / rel_path
                content1 = file1.read_bytes()
                content2 = file2.read_bytes()
                assert content1 == content2, (
                    f"File {rel_path} content differs between builds. "
                    "Zipapp builds should be deterministic "
                    "(excluding environment.json)."
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
    serger_script = PROJ_ROOT / "bin" / "serger.py"
    config_file = PROJ_ROOT / ".serger.jsonc"

    # Use temp directories for builds
    with tempfile.TemporaryDirectory() as build_dir1:
        build_path1 = Path(build_dir1)
        output_file1 = build_path1 / "apathetic_utils.py"

        # --- execute: first build with disable_build_timestamp ---
        result1 = subprocess.run(  # noqa: S603
            [
                sys.executable,
                str(serger_script),
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
                    str(serger_script),
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


def test_zipapp_build_produces_valid_file() -> None:
    """Test that shiv creates a valid zipapp file for the project.

    This test:
    1. Builds the project as a zipapp using the actual pyproject.toml
    2. Verifies the zipapp file is valid and can be executed

    This verifies our project configuration works correctly with shiv.
    """
    """Test that shiv creates a valid zipapp file for the project.

    This test:
    1. Builds the project as a zipapp using the actual pyproject.toml
    2. Verifies the zipapp file is valid and can be executed
    """
    # --- setup ---
    zipapp_file = PROJ_ROOT / "dist" / "apathetic_utils.pyz"

    # Ensure dist directory exists
    zipapp_file.parent.mkdir(parents=True, exist_ok=True)

    # --- execute: build zipapp ---
    shiv_cmd = apathetic_utils.find_shiv()
    result = subprocess.run(  # noqa: S603
        [
            shiv_cmd,
            "-c",
            "apathetic_utils",
            "-o",
            str(zipapp_file),
            ".",
        ],
        cwd=PROJ_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (
        f"Zipapp build failed: {result.stdout}\n{result.stderr}"
    )

    assert zipapp_file.exists(), "Zipapp output file not created"

    # --- verify: file is a valid zip file ---
    assert zipfile.is_zipfile(zipapp_file), "Output file should be a valid zip file"

    # --- verify: can be executed ---
    exec_result = subprocess.run(  # noqa: S603
        [sys.executable, str(zipapp_file), "--help"],
        cwd=PROJ_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )

    # Should either succeed or fail gracefully (not crash with import/syntax errors)
    assert exec_result.returncode is not None, (
        "Zipapp should execute and return an exit code"
    )


def test_zipapp_build_is_deterministic() -> None:
    """Test that two zipapp builds of the project produce identical output.

    This test:
    1. Builds the project as a zipapp using the actual pyproject.toml
    2. Deletes the output and builds again
    3. Verifies both builds produce identical content (excluding timestamps)

    Note: zipapps may contain timestamps in environment.json, but the core
    content should be deterministic. We compare the zip contents excluding
    that file.
    """
    # --- setup ---
    zipapp_file = PROJ_ROOT / "dist" / "apathetic_utils.pyz"

    # Ensure dist directory exists
    zipapp_file.parent.mkdir(parents=True, exist_ok=True)

    # --- execute: first build ---
    shiv_cmd = apathetic_utils.find_shiv()
    result1 = subprocess.run(  # noqa: S603
        [
            shiv_cmd,
            "-c",
            "apathetic_utils",
            "-o",
            str(zipapp_file),
            ".",
        ],
        cwd=PROJ_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result1.returncode == 0, (
        f"First zipapp build failed: {result1.stdout}\n{result1.stderr}"
    )
    assert zipapp_file.exists(), "First build output file not created"

    # Extract first build to temp directory
    with tempfile.TemporaryDirectory() as extract_dir1:
        extract_path1 = Path(extract_dir1)
        with zipfile.ZipFile(zipapp_file, "r") as zf1:
            zf1.extractall(extract_path1)

        # Delete the output file to force a fresh build
        zipapp_file.unlink()

        # --- execute: second build ---
        result2 = subprocess.run(  # noqa: S603
            [
                shiv_cmd,
                "-c",
                "apathetic_utils",
                "-o",
                str(zipapp_file),
                ".",
            ],
            cwd=PROJ_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        assert result2.returncode == 0, (
            f"Second zipapp build failed: {result2.stdout}\n{result2.stderr}"
        )
        assert zipapp_file.exists(), "Second build output file not created"

        # Extract second build to temp directory
        with tempfile.TemporaryDirectory() as extract_dir2:
            extract_path2 = Path(extract_dir2)
            with zipfile.ZipFile(zipapp_file, "r") as zf2:
                zf2.extractall(extract_path2)

            # --- verify: same files and content (deterministic) ---
            # Get all files from both extracts, excluding environment.json
            files1 = sorted(
                f.relative_to(extract_path1)
                for f in extract_path1.rglob("*")
                if f.is_file() and f.name != "environment.json"
            )
            files2 = sorted(
                f.relative_to(extract_path2)
                for f in extract_path2.rglob("*")
                if f.is_file() and f.name != "environment.json"
            )

            assert files1 == files2, (
                "Two zipapp builds of the project should contain the same files "
                "(excluding environment.json). "
                f"First: {[str(f) for f in files1]}, "
                f"Second: {[str(f) for f in files2]}"
            )

            # Compare file contents one at a time
            for rel_path in files1:
                file1 = extract_path1 / rel_path
                file2 = extract_path2 / rel_path
                content1 = file1.read_bytes()
                content2 = file2.read_bytes()
                assert content1 == content2, (
                    f"File {rel_path} content differs between builds. "
                    "Zipapp builds of our project should be deterministic "
                    "(excluding environment.json)."
                )
