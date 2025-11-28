#!/usr/bin/env python3
"""
Serger — Stitch your module into a single file.
This single-file version is auto-generated from modular sources.
Version: 0.1.0
Commit: unknown (local build)
Built: 2025-11-27 01:44:17 UTC
"""
# Serger — Stitch your module into a single file.
# ============LICENSE============
# License: MIT-aNOAI
# Full text: https://github.com/apathetic-tools/serger/blob/main/LICENSE
# ================================
# Version: 0.1.0
# Commit: unknown (local build)
# Build Date: 2025-11-27 01:44:17 UTC
# Repo: https://github.com/apathetic-tools/serger

from __future__ import annotations

import argparse
import builtins
import contextlib
import importlib
import inspect
import json
import logging
import os
import re
import shutil
import site
import subprocess
import sys
import traceback
import types
from collections.abc import Callable, Generator, Iterator
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from difflib import get_close_matches
from fnmatch import fnmatchcase
from functools import lru_cache
from io import StringIO
from pathlib import Path
from types import FrameType, UnionType
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Literal,
    TextIO,
    TypeAlias,
    TypedDict,
    TypeVar,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from typing_extensions import NotRequired


if TYPE_CHECKING:
    from collections.abc import Sequence
import ast
import platform
import py_compile
import tempfile
import time
from collections import OrderedDict
from datetime import datetime, timezone
from typing import TYPE_CHECKING


__version__ = "0.1.0"
__commit__ = "unknown (local build)"
__build_date__ = "2025-11-27 01:44:17 UTC"
__STANDALONE__ = True
__STITCH_SOURCE__ = "serger"
__package__ = "serger"


# === apathetic_logging.constants ===
# src/apathetic_logging/constants.py
"""Constants for Apathetic Logging."""


class ApatheticLogging_Internal_Constants:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Constants for apathetic logging functionality.

    This class contains all constant values used by apathetic_logging.
    It's kept separate for organizational purposes.
    """

    DEFAULT_APATHETIC_LOG_LEVEL: str = "detail"
    """Default log level when no other source is found."""

    DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS: ClassVar[list[str]] = ["LOG_LEVEL"]
    """Default environment variable names to check for log level."""

    SAFE_TRACE_ENABLED: bool = os.getenv("SAFE_TRACE", "").lower() in {
        "1",
        "true",
        "yes",
    }
    """Enable safe trace diagnostics (controlled by SAFE_TRACE env var)."""

    NOTSET_LEVEL: int = logging.NOTSET
    """NOTSET level (0) - logger inherits level from parent."""

    # levels must be careful not to equal 0 to avoid NOTSET
    TEST_LEVEL: int = logging.DEBUG - 8
    """Most verbose level, bypasses capture."""

    TRACE_LEVEL: int = logging.DEBUG - 5
    """More verbose than DEBUG."""

    DETAIL_LEVEL: int = logging.INFO - 5
    """More detailed than INFO."""

    MINIMAL_LEVEL: int = logging.INFO + 5
    """Less detailed than INFO."""

    SILENT_LEVEL: int = logging.CRITICAL + 1
    """Disables all logging (one above the highest builtin level)."""

    LEVEL_ORDER: ClassVar[list[str]] = [
        "test",  # most verbose, bypasses capture for debugging tests
        "trace",
        "debug",
        "detail",
        "info",
        "minimal",
        "warning",
        "error",
        "critical",
        "silent",  # disables all logging
    ]
    """Ordered list of log level names from most to least verbose."""

    class ANSIColors:
        """A selection of ANSI color code constants.

        For a comprehensive reference on ANSI escape codes and color support,
        see: https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
        """

        RESET: str = "\033[0m"
        """Reset ANSI color codes."""

        CYAN: str = "\033[36m"
        """Cyan ANSI color code."""

        YELLOW: str = "\033[93m"  # or \033[33m
        """Yellow ANSI color code."""

        RED: str = "\033[91m"  # or \033[31m # or background \033[41m
        """Red ANSI color code."""

        GREEN: str = "\033[92m"  # or \033[32m
        """Green ANSI color code."""

        GRAY: str = "\033[90m"
        """Gray ANSI color code."""

    TAG_STYLES: ClassVar[dict[str, tuple[str, str]]] = {
        "TEST": (ANSIColors.GRAY, "[TEST]"),
        "TRACE": (ANSIColors.GRAY, "[TRACE]"),
        "DEBUG": (ANSIColors.CYAN, "[DEBUG]"),
        "WARNING": ("", "⚠️ "),
        "ERROR": ("", "❌ "),
        "CRITICAL": ("", "💥 "),
    }
    """Mapping of level names to (color_code, tag_text) tuples."""

    TARGET_PYTHON_VERSION: tuple[int, int] | None = None
    """Target Python version (major, minor).

    If None, target version checks are disabled by default.
    """

    DEFAULT_PROPAGATE: bool = False
    """Default propagate setting for loggers.

    When False, loggers do not propagate messages to parent loggers,
    avoiding duplicate root logs.
    """


# === apathetic_logging.dual_stream_handler ===
# src/apathetic_logging/dual_stream_handler.py
"""DualStreamHandler class for Apathetic Logging.

Docstrings are adapted from the standard library logging.Handler documentation
licensed under the Python Software Foundation License Version 2.
"""


class ApatheticLogging_Internal_DualStreamHandler:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the DualStreamHandler nested class.

    This class contains the DualStreamHandler implementation as a nested class.
    When mixed into apathetic_logging, it provides apathetic_logging.DualStreamHandler.
    """

    class DualStreamHandler(logging.StreamHandler):  # type: ignore[type-arg]
        """Send info to stdout, everything else to stderr.

        INFO, MINIMAL, and DETAIL go to stdout (normal program output).
        TRACE, DEBUG, WARNING, ERROR, and CRITICAL go to stderr
        (diagnostic/error output).
        When logger level is TEST, TEST/TRACE/DEBUG messages bypass capture
        by writing to sys.__stderr__ instead of sys.stderr. This allows
        debugging tests without breaking output assertions while still being
        capturable by subprocess.run(capture_output=True).
        WARNING, ERROR, and CRITICAL always use normal stderr, even in TEST mode.
        """

        enable_color: bool = False
        """Enable ANSI color output for log messages."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            """Initialize the dual stream handler. super().__init__() to StreamHandler.

            Args:
                *args: Additional positional arguments (for future-proofing)
                **kwargs: Additional keyword arguments (for future-proofing)
            """
            # default to stdout, overridden per record in emit()
            super().__init__(*args, **kwargs)  # pyright: ignore[reportUnknownMemberType]

        def emit(self, record: logging.LogRecord, *args: Any, **kwargs: Any) -> None:
            """Routes based on log level and handles colorization.

            Features:
            - Routes messages to stdout or stderr based on log level:
              - DETAIL, INFO, and MINIMAL → stdout (normal program output)
              - TRACE, DEBUG, WARNING, ERROR, and CRITICAL → stderr
                (diagnostic/error output)
            - In TEST mode, TEST/TRACE/DEBUG messages bypass pytest capture
              by writing to sys.__stderr__ instead of sys.stderr
            - Sets enable_color attribute on record for TagFormatter integration

            Args:
                record: The LogRecord to emit
                *args: Additional positional arguments (for future-proofing)
                **kwargs: Additional keyword arguments (for future-proofing)

            logging.Handler.emit() implementation:
            https://docs.python.org/3.10/library/logging.html#logging.Handler.emit
            """
            # Import here to avoid circular dependency

            _constants = ApatheticLogging_Internal_Constants
            level = record.levelno

            # Check if logger is in TEST mode (bypass capture for verbose levels)
            logger_name = record.name
            # from .get_logger import (
            #     ApatheticLogging_Internal_GetLogger,
            # )

            # logger_instance = ApatheticLogging_Internal_GetLogger.getLogger(
            #     logger_name, extend=False
            # )
            # can't use internal getLogger() here
            #   because then it will call extendLoggingModule again
            logger_instance = logging.getLogger(logger_name)

            # Use duck typing to check if this is our Logger class
            # (has test() method) to avoid circular dependency
            has_test_method = hasattr(logger_instance, "test") and callable(
                getattr(logger_instance, "test", None)
            )
            # Use effective level (not explicit level) to detect TEST mode,
            # so child loggers that inherit TEST level from parent are correctly
            # detected
            is_test_mode = has_test_method and logger_instance.getEffectiveLevel() == (
                _constants.TEST_LEVEL
            )

            # Determine target stream
            if level >= logging.WARNING:
                # WARNING, ERROR, CRITICAL → stderr (always, even in TEST mode)
                # This ensures they still break tests as expected
                self.stream = sys.stderr
            elif level <= logging.DEBUG:
                # TEST, TRACE, DEBUG → stderr (normal) or __stderr__ (TEST mode bypass)
                # Use __stderr__ so they bypass pytest capsys but are still
                # capturable by subprocess.run(capture_output=True)
                if is_test_mode:
                    self.stream = sys.__stderr__
                else:
                    self.stream = sys.stderr
            else:
                # DETAIL, INFO, MINIMAL → stdout (normal program output)
                self.stream = sys.stdout

            # used by TagFormatter
            record.enable_color = getattr(self, "enable_color", False)

            super().emit(record, *args, **kwargs)


# === apathetic_logging.registry_data ===
# src/apathetic_logging/registry_data.py
"""Registry for configurable log level settings."""


class ApatheticLogging_Internal_RegistryData:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides registry storage for configurable settings.

    This class contains class-level attributes for storing registered configuration
    values. When mixed into apathetic_logging, it provides centralized storage for
    log level environment variables, default log level, logger name, target
    Python version, and propagate setting.

    Other mixins access these registries via direct class reference:
    ``ApatheticLogging_Internal_RegistryData.registered_internal_*``
    """

    # Registry for configurable log level settings
    # These are class-level attributes to avoid module-level namespace pollution
    # Public but marked with _internal_ to indicate internal use by other mixins
    registered_internal_log_level_env_vars: list[str] | None = None
    """Environment variable names to check for log level configuration.

    If None, falls back to DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS from constants.py.
    The environment variables are checked in order, and the first non-empty value
    found is used. Set via registerLogLevelEnvVars() or register_log_level_env_vars().
    """
    registered_internal_default_log_level: str | None = None
    """Default log level to use when no other source is found.

    If None, falls back to DEFAULT_APATHETIC_LOG_LEVEL from constants.py.
    Used when no environment variable is set and no root log level is provided.
    Set via registerDefaultLogLevel() or register_default_log_level().
    """
    registered_internal_logger_name: str | None = None
    """Registered logger name to use for logger name inference.

    If None, logger names are inferred from the calling module's __package__
    attribute. When set, this value is returned by getDefaultLoggerName() instead
    of inferring from the call stack. Set via registerLogger() or register_logger().
    """
    registered_internal_target_python_version: tuple[int, int] | None = None
    """Target Python version (major, minor) for compatibility checking.

    If None, falls back to TARGET_PYTHON_VERSION from constants.py.
    Used to validate function calls against target version, not just runtime version.
    """
    registered_internal_propagate: bool | None = None
    """Propagate setting for loggers.

    If None, falls back to DEFAULT_PROPAGATE from constants.py.
    When False, loggers do not propagate messages to parent loggers.
    """
    registered_internal_compatibility_mode: bool | None = None
    """Compatibility mode setting for stdlib drop-in replacement.

    If None, defaults to False (current improved behavior).
    When True, restores stdlib-compatible behavior where possible
    (e.g., getLogger(None) returns root logger).
    Set via registerCompatibilityMode() or register_compatibility_mode().
    """


# === apathetic_logging.logging_utils ===
# src/apathetic_logging/logging_utils.py
"""Logging utilities for Apathetic Logging.

Docstrings are adapted from the standard library logging module documentation
licensed under the Python Software Foundation License Version 2.
"""


class ApatheticLogging_Internal_LoggingUtils:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides helper functions for the standard logging module.

    This class contains utility functions that operate directly on or replace
    standard library `logging.*` utilities and functions. These helpers extend
    or wrap the built-in logging module functionality to provide enhanced
    capabilities or safer alternatives.

    When mixed into apathetic_logging, it provides utility functions that
    interact with Python's standard logging module.
    """

    _LoggerType = TypeVar("_LoggerType", bound=logging.Logger)

    @staticmethod
    def _getCompatibilityMode() -> bool:
        """Get the compatibility mode setting from registry.

        Returns the registered compatibility mode setting, or False (improved
        behavior) if not registered. This is an internal helper to avoid
        circular imports (registry.py imports from logging_utils.py).

        Returns:
            Compatibility mode setting (True or False).
            Defaults to False if not registered.
        """
        _registry_data = ApatheticLogging_Internal_RegistryData
        return (
            _registry_data.registered_internal_compatibility_mode
            if _registry_data.registered_internal_compatibility_mode is not None
            else False
        )

    @staticmethod
    def getLevelName(
        level: int | str, *args: Any, strict: bool = False, **kwargs: Any
    ) -> str | int:
        """Return the textual or numeric representation of a logging level.

        Behavior depends on compatibility mode (set via `registerCompatibilityMode()`):

        - Value-add: Uppercases string inputs before processing

        **Compatibility mode disabled (`compat_mode=False`, default):**
        - Accepts both integer and string input
        - For string input: validates level exists and returns canonical
          level name string
        - For integer input: returns level name as string (never returns `int`)
        - Optional strict mode to raise `ValueError` for unknown integer levels

        For string→int conversion, use `getLevelNumber()` instead.

        **Compatibility mode enabled (`compat_mode=True`):**
        - Behaves like stdlib `logging.getLevelName()` (bidirectional)
        - Returns `str` for integer input, `int` for string input (known levels)
        - Returns `"Level {level}"` string for unknown levels

        Args:
            level: Log level as integer or string name
            *args: Additional positional arguments (for future-proofing)
            strict: If True, raise ValueError for unknown levels. If False (default),
                returns "Level {level}" format for unknown integer levels (matching
                stdlib behavior). Only used when compatibility mode is disabled and
                level is an integer.
            **kwargs: Additional keyword arguments (for future-proofing)

        Returns:
            - Compatibility mode enabled: `str | int` (bidirectional like stdlib)
            - Compatibility mode disabled: `str` (always string; string input
              is validated and returns canonical name, int input is converted
              to name)

        Raises:
            ValueError: If string level cannot be resolved to a known level
                (non-compat mode), or if strict=True and level is an integer
                that cannot be resolved to a known level name

        Example:
            >>> # Compatibility mode enabled (stdlib-like behavior):
            >>> from apathetic_logging import registerCompatibilityMode
            >>> registerCompatibilityMode(compat_mode=True)
            >>> getLevelName(10)  # int input
            "DEBUG"
            >>> getLevelName("DEBUG")  # string input
            10
            >>> getLevelName("debug")  # case-insensitive, uppercased
            10

            >>> # Compatibility mode disabled (improved behavior):
            >>> registerCompatibilityMode(compat_mode=False)
            >>> getLevelName(10)
            "DEBUG"
            >>> getLevelName("DEBUG")  # Validates and returns canonical name
            "DEBUG"
            >>> getLevelName("debug")  # Validates and returns canonical name
            "DEBUG"
            >>> getLevelName("UNKNOWN")  # Unknown string raises ValueError
            ValueError: Unknown log level: 'UNKNOWN'

        See Also:
            getLevelNumber() - Convert string to int (when compat mode disabled)
            registerCompatibilityMode() - Enable/disable compatibility mode

        https://docs.python.org/3.10/library/logging.html#logging.getLevelName
        """
        # Check compatibility mode from registry
        compat_mode = ApatheticLogging_Internal_LoggingUtils._getCompatibilityMode()

        # Use unidirectional functions to avoid duplication
        if compat_mode and isinstance(level, str):
            # Compatibility mode with string input → return int (like stdlib)
            return ApatheticLogging_Internal_LoggingUtils.getLevelNumber(level)

        # All other cases: return string (compat mode with int, or non-compat mode)
        return ApatheticLogging_Internal_LoggingUtils.getLevelNameStr(
            level, *args, strict=strict, **kwargs
        )

    @staticmethod
    def getLevelNumber(level: str | int) -> int:
        """Convert a log level name to its numeric value.

        Recommended way to convert string level names to integers. This function
        explicitly performs string->int conversion, unlike `getLevelName()` which
        has bidirectional behavior for backward compatibility.

        Handles all levels registered via logging.addLevelName() (including
        standard library levels, custom apathetic levels, and user-registered levels).

        Args:
            level: Log level as string name (case-insensitive) or integer

        Returns:
            Integer level value

        Raises:
            ValueError: If level cannot be resolved to a known level

        Example:
            >>> getLevelNumber("DEBUG")
            10
            >>> getLevelNumber("TRACE")
            5
            >>> getLevelNumber(20)
            20
            >>> getLevelNumber("UNKNOWN")
            ValueError: Unknown log level: 'UNKNOWN'

        See Also:
            getLevelName() - Convert int to string (intended use)
        """
        if isinstance(level, int):
            return level

        level_str = level.upper()

        # Use getattr() to find level constants registered via logging.addLevelName():
        # - Standard library levels (DEBUG, INFO, etc.) - registered by default
        # - Custom apathetic levels (TEST, TRACE, etc.)
        #   registered via extendLoggingModule()
        # - User-registered levels via our addLevelName() method
        #   (but not stdlib's logging.addLevelName() which doesn't set attribute)
        # - User-registered levels via setattr(logging, level_str, value)
        resolved = getattr(logging, level_str, None)
        if isinstance(resolved, int):
            return resolved

        # Unknown level: always raise
        msg = f"Unknown log level: {level_str!r}"
        raise ValueError(msg)

    @staticmethod
    def getLevelNameStr(
        level: int | str, *args: Any, strict: bool = False, **kwargs: Any
    ) -> str:
        """Convert a log level to its string name representation.

        Unidirectional function that always returns a string. This is the recommended
        way to convert log levels to strings when you want guaranteed string output
        without compatibility mode behavior.

        Unlike `getLevelName()` which has compatibility mode and bidirectional
        behavior, this function always returns a string:
        - Integer input: converts to level name string (returns "Level {level}"
          for unknown levels unless strict=True)
        - String input: validates level exists, then returns uppercased string

        Handles all levels registered via logging.addLevelName() (including
        standard library levels, custom apathetic levels, and user-registered levels).

        Args:
            level: Log level as integer or string name (case-insensitive)
            *args: Additional positional arguments (for future-proofing)
            strict: If True, raise ValueError for unknown integer levels.
                If False (default), returns "Level {level}" format for unknown
                integer levels (matching stdlib behavior).
            **kwargs: Additional keyword arguments (for future-proofing)

        Returns:
            Level name as uppercase string

        Raises:
            ValueError: If string level cannot be resolved to a known level,
                or if strict=True and integer level cannot be resolved to a
                known level

        Example:
            >>> getLevelNameStr(10)
            "DEBUG"
            >>> getLevelNameStr(5)
            "TRACE"
            >>> getLevelNameStr("DEBUG")
            "DEBUG"
            >>> getLevelNameStr("debug")
            "DEBUG"
            >>> getLevelNameStr(999)  # Unknown integer, strict=False (default)
            "Level 999"
            >>> getLevelNameStr(999, strict=True)  # Unknown integer, strict=True
            ValueError: Unknown log level: 999
            >>> getLevelNameStr("UNKNOWN")
            ValueError: Unknown log level: 'UNKNOWN'

        See Also:
            getLevelNumber() - Convert string to int (complementary function)
            getLevelName() - Bidirectional conversion with compatibility mode
        """
        # If string input, validate it exists and return canonical name
        if isinstance(level, str):
            # Validate level exists (raises ValueError if not)
            ApatheticLogging_Internal_LoggingUtils.getLevelNumber(level)
            return level.upper()

        # Integer input: convert to level name string
        result = logging.getLevelName(level, *args, **kwargs)
        # logging.getLevelName always returns str for int input

        # If input was int and result is "Level {level}" format and strict is on, raise
        if result.startswith("Level ") and strict:
            msg = f"Unknown log level: {level}"
            raise ValueError(msg)

        # level name or (strict=False) "Level {int}"
        return result

    @staticmethod
    def hasLogger(logger_name: str) -> bool:
        """Check if a logger exists in the logging manager's registry.

        Args:
            logger_name: The name of the logger to check.

        Returns:
            True if the logger exists in the registry, False otherwise.
        """
        return logger_name in logging.Logger.manager.loggerDict

    @staticmethod
    def removeLogger(logger_name: str) -> None:
        """Remove a logger from the logging manager's registry.

        Args:
            logger_name: The name of the logger to remove.
        """
        logging.Logger.manager.loggerDict.pop(logger_name, None)

    @staticmethod
    def _extractTopLevelPackage(package: str | None) -> str | None:
        """Extract top-level package name from package string.

        Args:
            package: Package string (e.g., "myapp.submodule") or None

        Returns:
            Top-level package name (e.g., "myapp") or None if package is None
        """
        if package is None:
            return None
        if "." in package:
            return package.split(".", 1)[0]
        return package

    @staticmethod
    def _inferFromFrame(skip_frames: int, frame: FrameType | None) -> str | None:
        """Infer logger name from caller's frame.

        Args:
            skip_frames: Number of frames to skip to get to actual caller
            frame: Frame to start from, or None

        Returns:
            Inferred logger name or None if cannot be inferred
        """
        if frame is None:
            return None
        try:
            # Skip the specified number of frames to get to the actual caller
            caller_frame = frame.f_back
            for _ in range(skip_frames):
                if caller_frame is None:
                    break
                caller_frame = caller_frame.f_back
            if caller_frame is None:
                return None
            caller_package = caller_frame.f_globals.get("__package__")
            return ApatheticLogging_Internal_LoggingUtils._extractTopLevelPackage(
                caller_package
            )
        finally:
            del frame

    @staticmethod
    def getDefaultLoggerName(
        logger_name: str | None = None,
        *,
        check_registry: bool = True,
        skip_frames: int = 1,
        raise_on_error: bool = False,
        infer: bool = True,
        register: bool = False,
    ) -> str | None:
        """Get default logger name with optional inference from caller's frame.

        This function handles the common pattern of:
        1. Using explicit name if provided
        2. Checking registry if requested
        3. Inferring from caller's frame if needed (when infer=True)
        4. Storing inferred name in registry (when register=True)
        5. Returning None or raising error if still unresolved

        Args:
            logger_name: Explicit logger name, or None to infer.
            check_registry: If True, check registry before inferring. Use False
                when the caller should actively determine the name from current
                context (e.g., registerLogger() which should re-infer even
                if a name is already registered). Use True when the caller should
                use a previously registered name if available (e.g., getLogger()
                which should use the registered name).
            skip_frames: Number of frames to skip from this function to get to
                the actual caller. Default is 1 (skips this function's frame).
            raise_on_error: If True, raise RuntimeError if logger name cannot be
                resolved. If False (default), return None instead. Use True when
                a logger name is required (e.g., when creating a logger).
            infer: If True (default), attempt to infer logger name from caller's
                frame when not found in registry. If False, skip inference and
                return None if not found in registry.
            register: If True, store inferred name in registry. If False (default),
                do not modify registry. Note: Explicit names are never stored regardless
                of this parameter.

        Returns:
            Resolved logger name, or None if cannot be resolved and
            raise_on_error=False.

        Raises:
            RuntimeError: If logger name cannot be resolved and raise_on_error=True.
        """
        # Import locally to avoid circular import

        _registry_data = ApatheticLogging_Internal_RegistryData

        # If explicit name provided, return it (never store explicit names)
        # Note: Empty string ("") is a special case - it represents the root logger
        # and is returned as-is to match standard library behavior.
        if logger_name is not None:
            return logger_name

        # Check registry if requested
        if check_registry:
            registered_name = _registry_data.registered_internal_logger_name
            if registered_name is not None:
                return registered_name

        # Try to infer from caller's frame if inference is enabled
        if not infer:
            # Inference disabled - return None or raise error
            if raise_on_error:
                error_msg = (
                    "Cannot resolve logger name: not in registry and inference "
                    "is disabled. Please call registerLogger() with an "
                    "explicit logger name or enable inference."
                )
                raise RuntimeError(error_msg)
            return None

        # Get current frame (this function's frame) and skip to caller
        frame = inspect.currentframe()
        inferred_name = ApatheticLogging_Internal_LoggingUtils._inferFromFrame(
            skip_frames, frame
        )

        # Store inferred name in registry if requested
        if inferred_name is not None and register:
            _registry_data.registered_internal_logger_name = inferred_name

        # Return inferred name or handle error
        if inferred_name is not None:
            return inferred_name

        # Handle error case
        if raise_on_error:
            error_msg = (
                "Cannot auto-infer logger name: __package__ is not set in the "
                "calling module. Please call registerLogger() with an "
                "explicit logger name."
            )
            raise RuntimeError(error_msg)

        return None

    @staticmethod
    def checkPythonVersionRequirement(
        required_version: tuple[int, int],
        function_name: str,
    ) -> None:
        """Check if the target or runtime Python version meets the requirement.

        This method validates that a function requiring a specific Python version
        can be called safely. It checks:
        1. Target version (if set via registerTargetPythonVersion), otherwise
           falls back to TARGET_PYTHON_VERSION from constants
        2. Runtime version (as a safety net to catch actual runtime issues)

        This allows developers to catch version incompatibilities during development
        even when running on a newer Python version than their target.

        Args:
            required_version: Target Python version required (major, minor) tuple
            function_name: Name of the function being checked (for error messages)

        Raises:
            NotImplementedError: If target version or runtime version doesn't meet
                the requirement. Error message includes guidance on raising target
                version if applicable.

        Example:
            >>> checkPythonVersionRequirement((3, 11), "get_level_names_mapping")
            # Raises if target version < 3.11 or runtime version < 3.11
        """
        # Import locally to avoid circular imports

        _constants = ApatheticLogging_Internal_Constants
        _registry_data = ApatheticLogging_Internal_RegistryData

        # Determine effective target version
        # If target version is set, use it; otherwise fall back to TARGET_PYTHON_VERSION
        target_version = _registry_data.registered_internal_target_python_version
        if target_version is None:
            target_version = _constants.TARGET_PYTHON_VERSION

        # Check target version first (primary check)
        # Skip check if target_version is None (checks disabled)
        if target_version is not None and target_version < required_version:
            req_major, req_minor = required_version
            tgt_major, tgt_minor = target_version
            msg = (
                f"{function_name} requires Python {req_major}.{req_minor}+, "
                f"but target version is {tgt_major}.{tgt_minor}. "
                f"To use this function, call "
                f"registerTargetPythonVersion(({req_major}, {req_minor})) "
                f"or raise your target version to at least {req_major}.{req_minor}."
            )
            raise NotImplementedError(msg)

        # Check runtime version as safety net
        runtime_version = (sys.version_info.major, sys.version_info.minor)
        if runtime_version < required_version:
            req_major, req_minor = required_version
            rt_major, rt_minor = runtime_version
            msg = (
                f"{function_name} requires Python {req_major}.{req_minor}+, "
                f"but runtime version is {rt_major}.{rt_minor}. "
                f"This function is not available in your Python version."
            )
            raise NotImplementedError(msg)


# === apathetic_logging.safe_logging ===
# src/apathetic_logging/safe_logging.py
"""Safe logging utilities for Apathetic Logging."""


# Lazy, safe import — avoids patched time modules
#   in environments like pytest or eventlet
_real_time = importlib.import_module("time")


class ApatheticLogging_Internal_SafeLogging:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides safe logging utilities.

    This class contains both safeLog and safeTrace implementations as static
    methods. When mixed into apathetic_logging, it provides:
    - apathetic_logging.safeLog
    - apathetic_logging.safeTrace
    - apathetic_logging.makeSafeTrace
    """

    @staticmethod
    def safeLog(msg: str) -> None:
        """Emergency logger that never fails."""
        stream = cast("TextIO", sys.__stderr__)
        try:
            print(msg, file=stream)
        except Exception:  # noqa: BLE001
            # As final guardrail — never crash during crash reporting
            with suppress(Exception):
                stream.write(f"[INTERNAL] {msg}\n")

    @staticmethod
    def makeSafeTrace(icon: str = "🧪") -> Callable[..., Any]:
        """Create a trace function with a custom icon. Assign it to a variable.

        Args:
            icon: Emoji prefix/suffix for easier visual scanning

        Returns:
            A callable trace function
        """
        _safe_logging = ApatheticLogging_Internal_SafeLogging

        def localTrace(label: str, *args: Any) -> Any:
            return _safe_logging.safeTrace(label, *args, icon=icon)

        return localTrace

    @staticmethod
    def safeTrace(label: str, *args: Any, icon: str = "🧪") -> None:
        """Emit a synchronized, flush-safe diagnostic line.

        Mainly for troubleshooting and tests, avoids the
        logging framework and capture systems, can work even
        pre-logging framework initialization.

        Args:
            label: Short identifier or context string.
            *args: Optional values to append.
            icon: Emoji prefix/suffix for easier visual scanning.

        """
        _constants = ApatheticLogging_Internal_Constants
        if not _constants.SAFE_TRACE_ENABLED:
            return

        ts = _real_time.monotonic()
        # builtins.print more reliable than sys.stdout.write + sys.stdout.flush
        builtins.print(
            f"{icon} [SAFE TRACE {ts:.6f}] {label}",
            *args,
            file=sys.__stderr__,
            flush=True,
        )


# === apathetic_logging.registry ===
# src/apathetic_logging/registry.py
"""Registry functionality for Apathetic Logging."""


class ApatheticLogging_Internal_Registry:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides registration methods.

    This class contains static methods for registering configuration values.
    When mixed into apathetic_logging, it provides registration methods for
    log level environment variables, default log level, logger name, and
    target Python version.

    Registry storage is provided by ``ApatheticLogging_Internal_RegistryData``.

    **Static Methods:**
    - ``registerDefaultLogLevel()``: Register the default log level
    - ``registerLogLevelEnvVars()``: Register environment variable names
    - ``registerLogger()``: Register a logger (public API)
    - ``registerTargetPythonVersion()``: Register target Python version
    - ``registerPropagate()``: Register propagate setting
    - ``registerCompatibilityMode()``: Register compatibility mode setting
    """

    _LoggerType = TypeVar("_LoggerType", bound=logging.Logger)

    @staticmethod
    def registerDefaultLogLevel(default_level: str | None) -> None:
        """Register the default log level to use when no other source is found.

        Args:
            default_level: Default log level name (e.g., "info", "warning").
                If None, returns immediately without making any changes.

        Example:
            >>> from apathetic_logging import ApatheticLogging
            >>> apathetic_logging.registerDefaultLogLevel("warning")
        """
        if default_level is None:
            return

        _registry_data = ApatheticLogging_Internal_RegistryData
        _safe_logging = ApatheticLogging_Internal_SafeLogging

        _registry_data.registered_internal_default_log_level = default_level
        _safe_logging.safeTrace(
            "registerDefaultLogLevel() called",
            f"default_level={default_level}",
        )

    @staticmethod
    def registerLogLevelEnvVars(env_vars: list[str] | None) -> None:
        """Register environment variable names to check for log level.

        The environment variables will be checked in order, and the first
        non-empty value found will be used.

        Args:
            env_vars: List of environment variable names to check
                (e.g., ["SERGER_LOG_LEVEL", "LOG_LEVEL"]).
                If None, returns immediately without making any changes.

        Example:
            >>> from apathetic_logging import ApatheticLogging
            >>> apathetic_logging.registerLogLevelEnvVars(
            ...     ["MYAPP_LOG_LEVEL", "LOG_LEVEL"]
            ... )
        """
        if env_vars is None:
            return

        _registry_data = ApatheticLogging_Internal_RegistryData
        _safe_logging = ApatheticLogging_Internal_SafeLogging

        _registry_data.registered_internal_log_level_env_vars = env_vars
        _safe_logging.safeTrace(
            "registerLogLevelEnvVars() called",
            f"env_vars={env_vars}",
        )

    @staticmethod
    def registerLogger(
        logger_name: str | None = None,
        logger_class: type[ApatheticLogging_Internal_Registry._LoggerType]
        | None = None,
        *,
        target_python_version: tuple[int, int] | None = None,
        log_level_env_vars: list[str] | None = None,
        default_log_level: str | None = None,
        propagate: bool | None = None,
        compat_mode: bool | None = None,
    ) -> None:
        """Register a logger for use by getLogger().

        This is the public API for registering a logger. It registers the logger
        name and extends the logging module with custom levels if needed.

        If logger_name is not provided, the top-level package is automatically
        extracted from the calling module's __package__ attribute.

        If logger_class is provided and has an ``extendLoggingModule()``
        method, it will be called to extend the logging module with custom
        levels and set the logger class. If logger_class is provided but does
        not have ``extendLoggingModule()``, ``logging.setLoggerClass()``
        will be called directly to set the logger class. If logger_class is not
        provided, nothing is done with the logger class (the default ``Logger``
        is already extended at import time).

        **Important**: If you're using a custom logger class that has
        ``extendLoggingModule()``, do not call ``logging.setLoggerClass()``
        directly. Instead, pass the class to ``registerLogger()`` and let
        ``extendLoggingModule()`` handle setting the logger class. This
        ensures consistent behavior and avoids class identity issues in
        singlefile mode.

        Args:
            logger_name: The name of the logger to retrieve (e.g., "myapp").
                If None, extracts the top-level package from __package__.
            logger_class: Optional logger class to use. If provided and the class
                has an ``extendLoggingModule()`` method, it will be called.
                If the class doesn't have that method, ``logging.setLoggerClass()``
                will be called directly. If None, nothing is done (default Logger
                is already set up at import time).
            target_python_version: Optional target Python version (major, minor)
                tuple. If provided, sets the target Python version in the registry
                permanently. Defaults to None (no change).
            log_level_env_vars: Optional list of environment variable names to
                check for log level. If provided, sets the log level environment
                variables in the registry permanently. Defaults to None (no change).
            default_log_level: Optional default log level name. If provided, sets
                the default log level in the registry permanently. Defaults to None
                (no change).
            propagate: Optional propagate setting. If provided, sets the propagate
                value in the registry permanently. If None, uses registered propagate
                setting or falls back to DEFAULT_PROPAGATE from constants.py.
                Defaults to None (no change).
            compat_mode: Optional compatibility mode setting. If provided, sets
                the compatibility mode in the registry permanently. When True, restores
                stdlib-compatible behavior where possible (e.g., getLogger(None) returns
                root logger). If None, uses registered compatibility mode setting or
                defaults to False (improved behavior). Defaults to None (no change).

        Example:
            >>> # Explicit registration with default Logger (already extended)
            >>> from apathetic_logging import registerLogger
            >>> registerLogger("myapp")

            >>> # Auto-infer from __package__
            >>> registerLogger()
            ...     # Uses top-level package from __package__

            >>> # Register with custom logger class (has extendLoggingModule)
            >>> from apathetic_logging import Logger
            >>> class AppLogger(Logger):
            ...     pass
            >>> # Don't call AppLogger.extendLoggingModule() or
            >>> # logging.setLoggerClass() directly - registerLogger() handles it
            >>> registerLogger("myapp", AppLogger)

            >>> # Register with any logger class (no extendLoggingModule)
            >>> import logging
            >>> class SimpleLogger(logging.Logger):
            ...     pass
            >>> registerLogger("myapp", SimpleLogger)  # Sets logger class directly
        """
        _registry = ApatheticLogging_Internal_Registry
        _registry_data = ApatheticLogging_Internal_RegistryData
        _logging_utils = ApatheticLogging_Internal_LoggingUtils
        _safe_logging = ApatheticLogging_Internal_SafeLogging

        # Handle convenience parameters that set registry values
        _registry.registerTargetPythonVersion(target_python_version)
        _registry.registerLogLevelEnvVars(log_level_env_vars)
        _registry.registerDefaultLogLevel(default_log_level)
        _registry.registerPropagate(propagate=propagate)
        _registry.registerCompatibilityMode(compat_mode=compat_mode)

        # Import Logger locally to avoid circular import

        # Track if name was auto-inferred
        was_explicit = logger_name is not None

        # Resolve logger name (with inference if needed)
        # skip_frames=1 because: registerLogger -> getDefaultLoggerName -> caller
        # check_registry=False because registerLogger() should actively determine
        # the name from the current context, not return an old registered name. This
        # allows re-inferring from __package__ if the package context has changed.
        # raise_on_error=True because registerLogger() requires a logger name.
        # register=True because registerLogger() should store the resolved name.
        resolved_name = _logging_utils.getDefaultLoggerName(
            logger_name,
            check_registry=False,
            skip_frames=1,
            raise_on_error=True,
            infer=True,
            register=True,
        )

        if logger_class is not None:
            # extendLoggingModule will call setLoggerClass for those that support it
            if hasattr(logger_class, "extendLoggingModule"):
                logger_class.extendLoggingModule()  # type: ignore[attr-defined]
            else:
                # stdlib unwrapped
                logging.setLoggerClass(logger_class)

        # registerLogger always stores the result (explicit or inferred)
        _registry_data.registered_internal_logger_name = resolved_name

        _safe_logging.safeTrace(
            "registerLogger() called",
            f"name={resolved_name}",
            f"auto_inferred={not was_explicit}",
            f"logger_class={logger_class.__name__ if logger_class else None}",
        )

    @staticmethod
    def registerTargetPythonVersion(version: tuple[int, int] | None) -> None:
        """Register the target Python version for compatibility checking.

        This sets the target Python version that will be used to validate
        function calls. If a function requires a Python version newer than
        the target version, it will raise a NotImplementedError even if
        the runtime version is sufficient.

        If not set, the library defaults to TARGET_PYTHON_VERSION (3, 10) from
        constants.py. This allows developers to catch version incompatibilities
        during development even when running on a newer Python version than
        their target.

        Args:
            version: Target Python version as (major, minor) tuple
                (e.g., (3, 10) or (3, 11)). If None, returns immediately
                without making any changes.

        Example:
            >>> from apathetic_logging import registerTargetPythonVersion
            >>> registerTargetPythonVersion((3, 10))
            >>> # Now functions requiring 3.11+ will raise if called

        Note:
            The runtime version is still checked as a safety net. If the
            runtime version is older than required, the function will still
            raise an error even if the target version is sufficient.
        """
        if version is None:
            return

        _registry_data = ApatheticLogging_Internal_RegistryData
        _safe_logging = ApatheticLogging_Internal_SafeLogging

        _registry_data.registered_internal_target_python_version = version
        _safe_logging.safeTrace(
            "registerTargetPythonVersion() called",
            f"version={version[0]}.{version[1]}",
        )

    @staticmethod
    def registerPropagate(*, propagate: bool | None) -> None:
        """Register the propagate setting for loggers.

        This sets the default propagate value that will be used when creating
        loggers. If not set, the library defaults to DEFAULT_PROPAGATE (False)
        from constants.py.

        When propagate is False, loggers do not propagate messages to parent
        loggers, avoiding duplicate root logs.

        Args:
            propagate: Propagate setting (True or False). If None, returns
                immediately without making any changes.

        Example:
            >>> from apathetic_logging import registerPropagate
            >>> registerPropagate(propagate=True)
            >>> # Now new loggers will propagate by default
        """
        if propagate is None:
            return

        _registry_data = ApatheticLogging_Internal_RegistryData
        _safe_logging = ApatheticLogging_Internal_SafeLogging

        _registry_data.registered_internal_propagate = propagate
        _safe_logging.safeTrace(
            "registerPropagate() called",
            f"propagate={propagate}",
        )

    @staticmethod
    def registerCompatibilityMode(*, compat_mode: bool | None) -> None:
        """Register the compatibility mode setting for stdlib drop-in replacement.

        This sets the compatibility mode that will be used when creating loggers.
        If not set, the library defaults to False (improved behavior).

        When compat_mode is True, restores stdlib-compatible behavior where
        possible (e.g., getLogger(None) returns root logger instead of auto-inferring).

        Args:
            compat_mode: Compatibility mode setting (True or False). If None,
                returns immediately without making any changes.

        Example:
            >>> from apathetic_logging import registerCompatibilityMode
            >>> registerCompatibilityMode(compat_mode=True)
            >>> # Now getLogger(None) returns root logger (stdlib behavior)
        """
        if compat_mode is None:
            return

        _registry_data = ApatheticLogging_Internal_RegistryData
        _safe_logging = ApatheticLogging_Internal_SafeLogging

        _registry_data.registered_internal_compatibility_mode = compat_mode
        _safe_logging.safeTrace(
            "registerCompatibilityMode() called",
            f"compat_mode={compat_mode}",
        )

    @staticmethod
    def getLogLevelEnvVars() -> list[str]:
        """Get the environment variable names to check for log level.

        Returns the registered environment variable names, or the default
        environment variables if none are registered.

        Returns:
            List of environment variable names to check for log level.
            Defaults to ["LOG_LEVEL"] if not registered.

        Example:
            >>> from apathetic_logging import getLogLevelEnvVars
            >>> env_vars = getLogLevelEnvVars()
            >>> print(env_vars)
            ["LOG_LEVEL"]
        """
        _constants = ApatheticLogging_Internal_Constants
        _registry_data = ApatheticLogging_Internal_RegistryData

        return (
            _registry_data.registered_internal_log_level_env_vars
            or _constants.DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS
        )

    @staticmethod
    def getDefaultLogLevel() -> str:
        """Get the default log level.

        Returns the registered default log level, or the module default
        if none is registered.

        Returns:
            Default log level name (e.g., "detail", "info").
            Defaults to "detail" if not registered.

        Example:
            >>> from apathetic_logging import getDefaultLogLevel
            >>> level = getDefaultLogLevel()
            >>> print(level)
            "detail"
        """
        _constants = ApatheticLogging_Internal_Constants
        _registry_data = ApatheticLogging_Internal_RegistryData

        return (
            _registry_data.registered_internal_default_log_level
            or _constants.DEFAULT_APATHETIC_LOG_LEVEL
        )

    @staticmethod
    def getRegisteredLoggerName() -> str | None:
        """Get the registered logger name.

        Returns the registered logger name, or None if no logger name
        has been registered. Unlike getDefaultLoggerName(), this does not
        perform inference - it only returns the explicitly registered value.

        Returns:
            Registered logger name, or None if not registered.

        Example:
            >>> from apathetic_logging import getRegisteredLoggerName
            >>> name = getRegisteredLoggerName()
            >>> if name is None:
            ...     print("No logger name registered")
        """
        _registry_data = ApatheticLogging_Internal_RegistryData

        return _registry_data.registered_internal_logger_name

    @staticmethod
    def getTargetPythonVersion() -> tuple[int, int] | None:
        """Get the target Python version.

        Returns the registered target Python version, or the minimum
        supported version if none is registered.

        Returns:
            Target Python version as (major, minor) tuple, or None if
            no version is registered and TARGET_PYTHON_VERSION is None
            (checks disabled).

        Example:
            >>> from apathetic_logging import getTargetPythonVersion
            >>> version = getTargetPythonVersion()
            >>> print(version)
            (3, 10)  # or None if checks are disabled
        """
        _constants = ApatheticLogging_Internal_Constants
        _registry_data = ApatheticLogging_Internal_RegistryData

        return (
            _registry_data.registered_internal_target_python_version
            or _constants.TARGET_PYTHON_VERSION
        )

    @staticmethod
    def getDefaultPropagate() -> bool:
        """Get the default propagate setting.

        Returns the registered propagate setting, or the module default
        if none is registered.

        Returns:
            Default propagate setting (True or False).
            Defaults to False if not registered.

        Example:
            >>> from apathetic_logging import getDefaultPropagate
            >>> propagate = getDefaultPropagate()
            >>> print(propagate)
            False
        """
        _constants = ApatheticLogging_Internal_Constants
        _registry_data = ApatheticLogging_Internal_RegistryData

        return (
            _registry_data.registered_internal_propagate
            if _registry_data.registered_internal_propagate is not None
            else _constants.DEFAULT_PROPAGATE
        )

    @staticmethod
    def getCompatibilityMode() -> bool:
        """Get the compatibility mode setting.

        Returns the registered compatibility mode setting, or False (improved
        behavior) if not registered.

        Returns:
            Compatibility mode setting (True or False).
            Defaults to False if not registered.

        Example:
            >>> from apathetic_logging import getCompatibilityMode
            >>> compat_mode = getCompatibilityMode()
            >>> print(compat_mode)
            False
        """
        _registry_data = ApatheticLogging_Internal_RegistryData

        return (
            _registry_data.registered_internal_compatibility_mode
            if _registry_data.registered_internal_compatibility_mode is not None
            else False
        )


# === apathetic_logging.tag_formatter ===
# src/apathetic_logging/tag_formatter.py
"""TagFormatter class for Apathetic Logging.

Docstrings are adapted from the standard library logging.Formatter documentation
licensed under the Python Software Foundation License Version 2.
"""


class ApatheticLogging_Internal_TagFormatter:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the TagFormatter nested class.

    This class contains the TagFormatter implementation as a nested class.
    When mixed into apathetic_logging, it provides apathetic_logging.TagFormatter.
    """

    class TagFormatter(logging.Formatter):
        """Formatter that adds level tags to log messages.

        Adds colored or plain text tags (e.g., [DEBUG], [ERROR]) based on
        log level. Color support is controlled by the enable_color attribute
        on the LogRecord.
        """

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            """Initialize the TagFormatter.

            Wrapper for logging.Formatter.__init__ with future-proofing.
            """
            super().__init__(*args, **kwargs)

        def format(
            self,
            record: logging.LogRecord,
            *args: Any,
            **kwargs: Any,
        ) -> str:
            """Format a log record with level tag prefix.

            Args:
                record: LogRecord to format
                *args: Additional positional arguments (for future-proofing)
                **kwargs: Additional keyword arguments (for future-proofing)

            Returns:
                Formatted message with optional level tag prefix
            """
            _constants = ApatheticLogging_Internal_Constants
            tag_color, tag_text = _constants.TAG_STYLES.get(record.levelname, ("", ""))
            msg = super().format(record, *args, **kwargs)
            if tag_text:
                if getattr(record, "enable_color", False) and tag_color:
                    prefix = f"{tag_color}{tag_text}{_constants.ANSIColors.RESET}"
                else:
                    prefix = tag_text
                return f"{prefix} {msg}"
            return msg


# === apathetic_logging.logger ===
# src/apathetic_logging/logger.py
"""Core Logger implementation for Apathetic Logging.

See https://docs.python.org/3/library/logging.html#logging.Logger for the
complete list of standard library Logger methods that are extended by this class.

Docstrings are adapted from the standard library logging.Logger documentation
licensed under the Python Software Foundation License Version 2.
"""


class ApatheticLogging_Internal_LoggerCore(logging.Logger):  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Core Logger implementation for all Apathetic tools.

    This class contains the core Logger implementation.
    It provides all the custom methods and functionality for apathetic logging.
    """

    enable_color: bool = False
    """Enable ANSI color output for log messages."""

    _logging_module_extended: bool = False

    # if stdout or stderr are redirected, we need to repoint
    _last_stream_ids: tuple[TextIO, TextIO] | None = None

    DEFAULT_STACKLEVEL = 2
    """Default stacklevel for errorIfNotDebug/criticalIfNotDebug methods."""

    def __init__(
        self,
        name: str,
        level: int = logging.NOTSET,
        *,
        enable_color: bool | None = None,
        propagate: bool = False,
    ) -> None:
        """Initialize the logger.

        Resolves log level, color support, and log propagation.

        Args:
            name: Logger name
            level: Initial logging level (defaults to NOTSET, then auto-resolved)
            enable_color: Force color output on/off, or None for auto-detect
            propagate: False avoids duplicate root logs
        """
        # it is too late to call extendLoggingModule

        # now let's init our logger
        super().__init__(name, level)

        # default level resolution
        if self.level == logging.NOTSET:
            self.setLevel(self.determineLogLevel())

        # detect color support once per instance
        self.enable_color = (
            enable_color
            if enable_color is not None
            else type(self).determineColorEnabled()
        )

        self.propagate = propagate

        # handler attachment will happen in _log() with ensureHandlers()

    def ensureHandlers(self) -> None:
        """Ensure handlers are attached to this logger.

        DualStreamHandler is what will ensure logs go to the write channel.

        Rebuilds handlers if they're missing or if stdout/stderr have changed.
        """
        _dual_stream_handler = ApatheticLogging_Internal_DualStreamHandler
        _tag_formatter = ApatheticLogging_Internal_TagFormatter
        _safe_logging = ApatheticLogging_Internal_SafeLogging
        if self._last_stream_ids is None or not self.handlers:
            rebuild = True
        else:
            last_stdout, last_stderr = self._last_stream_ids
            rebuild = last_stdout is not sys.stdout or last_stderr is not sys.stderr

        if rebuild:
            self.handlers.clear()
            h = _dual_stream_handler.DualStreamHandler()
            h.setFormatter(_tag_formatter.TagFormatter("%(message)s"))
            h.enable_color = self.enable_color
            self.addHandler(h)
            self._last_stream_ids = (sys.stdout, sys.stderr)
            _safe_logging.safeTrace(
                "ensureHandlers()", f"rebuilt_handlers={self.handlers}"
            )

    def _log(  # type: ignore[override]
        self, level: int, msg: str, args: tuple[Any, ...], **kwargs: Any
    ) -> None:
        """Log a message with the specified level.

        Changed:
        - Automatically ensures handlers are attached via ensureHandlers()

        Args:
            level: The numeric logging level
            msg: The message format string
            args: Arguments for the message format string
            **kwargs: Additional keyword arguments passed to the base implementation

        Wrapper for logging.Logger._log.

        https://docs.python.org/3.10/library/logging.html#logging.Logger._log
        """
        self.ensureHandlers()
        super()._log(level, msg, args, **kwargs)

    def setLevel(self, level: int | str, *, minimum: bool | None = False) -> None:
        """Set the logging level of this logger.

        Changed:
        - Accepts both int and str level values (case-insensitive for strings)
        - Automatically resolves string level names to numeric values
        - Supports custom level names (TEST, TRACE, MINIMAL, DETAIL, SILENT)
        - Validates that custom levels are not set to 0, which would cause
          NOTSET inheritance from root logger
        - Added `minimum` parameter: if True, only sets the level if it's more
          verbose (lower numeric value) than the current level

        Args:
            level: The logging level, either as an integer or a string name
                (case-insensitive). Standard levels (DEBUG, INFO, WARNING, ERROR,
                CRITICAL) and custom levels (TEST, TRACE, MINIMAL, DETAIL, SILENT)
                are supported.
            minimum: If True, only set the level if it's more verbose (lower
                numeric value) than the current level. This prevents downgrading
                from a more verbose level (e.g., TRACE) to a less verbose one
                (e.g., DEBUG). Defaults to False. None is accepted and treated
                as False.

        Wrapper for logging.Logger.setLevel.

        https://docs.python.org/3.10/library/logging.html#logging.Logger.setLevel
        """
        _logging_utils = ApatheticLogging_Internal_LoggingUtils

        # Resolve string to integer if needed using utility function
        if isinstance(level, str):
            level = _logging_utils.getLevelNumber(level)

        # Handle minimum level logic (None is treated as False)
        if minimum:
            current_level = self.getEffectiveLevel()
            # Lower number = more verbose, so only set if new level is more verbose
            if level >= current_level:
                # Don't downgrade - keep current level
                return

        # Validate any level <= 0 (prevents NOTSET inheritance)
        # Built-in levels (DEBUG=10, INFO=20, etc.) are all > 0, so they pass
        # validateLevelPositive() will raise if level <= 0
        # At this point, level is guaranteed to be int (resolved above)
        level_name = _logging_utils.getLevelNameStr(level)
        self.validateLevelPositive(level, level_name=level_name)

        super().setLevel(level)

    @classmethod
    def determineColorEnabled(cls) -> bool:
        """Return True if colored output should be enabled."""
        # Respect explicit overrides
        if "NO_COLOR" in os.environ:
            return False
        if os.getenv("FORCE_COLOR", "").lower() in {"1", "true", "yes"}:
            return True

        # Auto-detect: use color if output is a TTY
        return sys.stdout.isatty()

    @staticmethod
    def validateLevelPositive(level: int, *, level_name: str | None = None) -> None:
        """Validate that a level value is positive (> 0).

        Custom levels with values <= 0 will inherit from the root logger,
        causing NOTSET inheritance issues.

        Args:
            level: The numeric level value to validate
            level_name: Optional name for the level (for error messages).
                If None, will attempt to get from getLevelName()

        Raises:
            ValueError: If level <= 0

        Example:
            >>> Logger.validateLevelPositive(5, level_name="TRACE")
            >>> Logger.validateLevelPositive(0, level_name="TEST")
            ValueError: Level 'TEST' has value 0...
        """
        if level <= 0:
            if level_name is None:
                level_name = ApatheticLogging_Internal_LoggingUtils.getLevelNameStr(
                    level
                )
            msg = (
                f"Level '{level_name}' has value {level}, "
                "which is <= 0. This causes NOTSET inheritance from root logger. "
                "Levels must be > 0."
            )
            raise ValueError(msg)

    @staticmethod
    def addLevelName(level: int, level_name: str) -> None:
        """Associate a level name with a numeric level.

        Changed:
        - Validates that level value is positive (> 0) to prevent NOTSET
          inheritance issues
        - Sets logging.<LEVEL_NAME> attribute for convenience, matching the
          pattern of built-in levels (logging.DEBUG, logging.INFO, etc.)
        - Validates existing attributes to ensure consistency

        Args:
            level: The numeric level value (must be > 0 for custom levels)
            level_name: The name to associate with this level

        Raises:
            ValueError: If level <= 0 (which would cause NOTSET inheritance)
            ValueError: If logging.<LEVEL_NAME> already exists with an invalid value
                (not a positive integer, or different from the provided level)

        Wrapper for logging.addLevelName.

        https://docs.python.org/3.10/library/logging.html#logging.addLevelName
        """
        # Validate level is positive
        ApatheticLogging_Internal_LoggerCore.validateLevelPositive(
            level, level_name=level_name
        )

        # Check if attribute already exists and validate it
        existing_value = getattr(logging, level_name, None)
        if existing_value is not None:
            # If it exists, it must be a valid level value (positive integer)
            if not isinstance(existing_value, int):
                msg = (
                    f"Cannot set logging.{level_name}: attribute already exists "
                    f"with non-integer value {existing_value!r}. "
                    "Level attributes must be integers."
                )
                raise ValueError(msg)
            # Validate existing value is positive
            ApatheticLogging_Internal_LoggerCore.validateLevelPositive(
                existing_value, level_name=level_name
            )
            if existing_value != level:
                msg = (
                    f"Cannot set logging.{level_name}: attribute already exists "
                    f"with different value {existing_value} "
                    f"(trying to set {level}). "
                    "Level attributes must match the level value."
                )
                raise ValueError(msg)
            # If it exists and matches, we can proceed (idempotent)

        logging.addLevelName(level, level_name)
        # Set convenience attribute matching built-in levels (logging.DEBUG, etc.)
        setattr(logging, level_name, level)

    @classmethod
    def extendLoggingModule(
        cls,
    ) -> bool:
        """The return value tells you if we ran or not.
        If it is False and you're calling it via super(),
        you can likely skip your code too.

        Note for tests:
            When testing isinstance checks on logger instances, use
            ``logging.getLoggerClass()`` instead of direct class references
            (e.g., ``mod_alogs.Logger``). This works reliably in both installed
            and singlefile runtime modes because it uses the actual class object
            that was set via ``logging.setLoggerClass()``, rather than a class
            reference from the import shim which may have different object identity
            in singlefile mode.

        Example:
                # ✅ Good: Works in both installed and singlefile modes
                assert isinstance(logger, logging.getLoggerClass())

                # ❌ May fail in singlefile mode due to class identity differences
                assert isinstance(logger, mod_alogs.Logger)
        """
        _constants = ApatheticLogging_Internal_Constants
        # Check if this specific class has already extended the module
        # (not inherited from base class)
        already_extended = getattr(cls, "_logging_module_extended", False)

        # Always set the logger class to cls, even if already extended.
        # This allows subclasses to override the logger class.
        # stdlib unwrapped
        logging.setLoggerClass(cls)

        # If already extended, skip the rest (level registration, etc.)
        if already_extended:
            return False
        cls._logging_module_extended = True

        # Sanity check: validate TAG_STYLES keys are in LEVEL_ORDER
        if __debug__:
            _tag_levels = set(_constants.TAG_STYLES.keys())
            _known_levels = {lvl.upper() for lvl in _constants.LEVEL_ORDER}
            if not _tag_levels <= _known_levels:
                _msg = "TAG_STYLES contains unknown levels"
                raise AssertionError(_msg)

        # Register custom levels with validation
        # addLevelName() also sets logging.TEST, logging.TRACE, etc. attributes
        cls.addLevelName(_constants.TEST_LEVEL, "TEST")
        cls.addLevelName(_constants.TRACE_LEVEL, "TRACE")
        cls.addLevelName(_constants.DETAIL_LEVEL, "DETAIL")
        cls.addLevelName(_constants.MINIMAL_LEVEL, "MINIMAL")
        cls.addLevelName(_constants.SILENT_LEVEL, "SILENT")

        return True

    def determineLogLevel(
        self,
        *,
        args: argparse.Namespace | None = None,
        root_log_level: str | None = None,
    ) -> str:
        """Resolve log level from CLI → env → root config → default."""
        _registry = ApatheticLogging_Internal_RegistryData
        _constants = ApatheticLogging_Internal_Constants
        args_level = getattr(args, "log_level", None)
        if args_level is not None:
            # cast_hint would cause circular dependency
            return cast("str", args_level).upper()

        # Check registered environment variables, or fall back to "LOG_LEVEL"
        # Access registry via namespace class MRO to ensure correct resolution
        # in both installed and stitched builds
        namespace_module = sys.modules.get("apathetic_logging")
        if namespace_module is not None:
            namespace_class = getattr(namespace_module, "apathetic_logging", None)
            if namespace_class is not None:
                # Use namespace class MRO to access registry
                # (handles shadowed attributes correctly)
                registered_env_vars = getattr(
                    namespace_class,
                    "registered_internal_log_level_env_vars",
                    None,
                )
                registered_default = getattr(
                    namespace_class,
                    "registered_internal_default_log_level",
                    None,
                )
            else:
                # Fallback to direct registry access
                registry_cls = _registry
                registered_env_vars = (
                    registry_cls.registered_internal_log_level_env_vars
                )
                registered_default = registry_cls.registered_internal_default_log_level
        else:
            # Fallback to direct registry access
            registered_env_vars = _registry.registered_internal_log_level_env_vars
            registered_default = _registry.registered_internal_default_log_level

        env_vars_to_check = (
            registered_env_vars or _constants.DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS
        )
        for env_var in env_vars_to_check:
            env_log_level = os.getenv(env_var)
            if env_log_level:
                return env_log_level.upper()

        if root_log_level:
            return root_log_level.upper()

        # Use registered default, or fall back to module default
        default_level: str = (
            registered_default or _constants.DEFAULT_APATHETIC_LOG_LEVEL
        )
        return default_level.upper()

    @property
    def levelName(self) -> str:
        """Return the explicit level name set on this logger.

        This property returns the name of the level explicitly set on this logger
        (via self.level). For the effective level name (what's actually used,
        considering inheritance), use effectiveLevelName instead.

        See also: logging.getLevelName, effectiveLevelName
        """
        return self.getLevelName()

    @property
    def effectiveLevel(self) -> int:
        """Return the effective level (what's actually used).

        This property returns the effective logging level for this logger,
        considering inheritance from parent loggers. This is the preferred
        way to get the effective level. Also available via getEffectiveLevel()
        for stdlib compatibility.

        See also: logging.Logger.getEffectiveLevel, effectiveLevelName
        """
        return self.getEffectiveLevel()

    @property
    def effectiveLevelName(self) -> str:
        """Return the effective level name (what's actually used).

        This property returns the name of the effective logging level for this
        logger, considering inheritance from parent loggers. This is the
        preferred way to get the effective level name. Also available via
        getEffectiveLevelName() for consistency.

        See also: logging.getLevelName, effectiveLevel
        """
        return self.getEffectiveLevelName()

    def getLevel(self) -> int:
        """Return the explicit level set on this logger.

        This method returns the level explicitly set on this logger (via
        self.level). For the effective level (what's actually used, considering
        inheritance), use getEffectiveLevel() or the effectiveLevel property.

        Returns:
            The explicit level value (int) set on this logger.

        See also: level property, getEffectiveLevel
        """
        return self.level

    def getLevelName(self) -> str:
        """Return the explicit level name set on this logger.

        This method returns the name of the level explicitly set on this logger
        (via self.level). For the effective level name (what's actually used,
        considering inheritance), use getEffectiveLevelName() or the
        effectiveLevelName property.

        Returns:
            The explicit level name (str) set on this logger.

        See also: levelName property, getEffectiveLevelName
        """
        return ApatheticLogging_Internal_LoggingUtils.getLevelNameStr(self.level)

    def getEffectiveLevelName(self) -> str:
        """Return the effective level name (what's actually used).

        This method returns the name of the effective logging level for this
        logger, considering inheritance from parent loggers. Prefer the
        effectiveLevelName property for convenience, or use this method for
        consistency with getEffectiveLevel().

        Returns:
            The effective level name (str) for this logger.

        See also: effectiveLevelName property, getEffectiveLevel
        """
        return ApatheticLogging_Internal_LoggingUtils.getLevelNameStr(
            self.getEffectiveLevel()
        )

    def errorIfNotDebug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Logs an exception with the real traceback starting from the caller.
        Only shows full traceback if debug/trace is enabled."""
        exc_info = kwargs.pop("exc_info", True)
        stacklevel = kwargs.pop("stacklevel", self.DEFAULT_STACKLEVEL)
        if self.isEnabledFor(logging.DEBUG):
            self.exception(
                msg, *args, exc_info=exc_info, stacklevel=stacklevel, **kwargs
            )
        else:
            self.error(msg, *args, **kwargs)

    def criticalIfNotDebug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Logs an exception with the real traceback starting from the caller.
        Only shows full traceback if debug/trace is enabled."""
        exc_info = kwargs.pop("exc_info", True)
        stacklevel = kwargs.pop("stacklevel", self.DEFAULT_STACKLEVEL)
        if self.isEnabledFor(logging.DEBUG):
            self.exception(
                msg, *args, exc_info=exc_info, stacklevel=stacklevel, **kwargs
            )
        else:
            self.critical(msg, *args, **kwargs)

    def colorize(
        self, text: str, color: str, *, enable_color: bool | None = None
    ) -> str:
        """Apply ANSI color codes to text.

        Defaults to using the instance's enable_color setting.

        Args:
            text: Text to colorize
            color: ANSI color code
            enable_color: Override color setting, or None to use instance default

        Returns:
            Colorized text if enabled, otherwise original text
        """
        _constants = ApatheticLogging_Internal_Constants
        if enable_color is None:
            enable_color = self.enable_color
        return f"{color}{text}{_constants.ANSIColors.RESET}" if enable_color else text

    def trace(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a trace-level message (more verbose than DEBUG)."""
        _constants = ApatheticLogging_Internal_Constants
        if self.isEnabledFor(_constants.TRACE_LEVEL):
            self._log(_constants.TRACE_LEVEL, msg, args, **kwargs)

    def detail(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a detail-level message (more detailed than INFO)."""
        _constants = ApatheticLogging_Internal_Constants
        if self.isEnabledFor(_constants.DETAIL_LEVEL):
            self._log(
                _constants.DETAIL_LEVEL,
                msg,
                args,
                **kwargs,
            )

    def minimal(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a minimal-level message (less detailed than INFO)."""
        _constants = ApatheticLogging_Internal_Constants
        if self.isEnabledFor(_constants.MINIMAL_LEVEL):
            self._log(
                _constants.MINIMAL_LEVEL,
                msg,
                args,
                **kwargs,
            )

    def test(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a test-level message (most verbose, bypasses capture)."""
        _constants = ApatheticLogging_Internal_Constants
        if self.isEnabledFor(_constants.TEST_LEVEL):
            self._log(_constants.TEST_LEVEL, msg, args, **kwargs)

    def logDynamic(self, level: str | int, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message with a dynamically provided log level
           (unlike .info(), .error(), etc.).

        Useful when you have a log level (string or numeric) and don't want to resolve
        either the string to int, or the int to a log method.

        Args:
            level: Log level as string name or integer
            msg: Message format string
            *args: Arguments for message formatting
            **kwargs: Additional keyword arguments
        """
        # Resolve level
        if isinstance(level, str):
            try:
                level_no = ApatheticLogging_Internal_LoggingUtils.getLevelNumber(level)
            except ValueError:
                self.error("Unknown log level: %r", level)
                return
        elif isinstance(level, int):  # pyright: ignore[reportUnnecessaryIsInstance]
            level_no = level
        else:
            self.error("Invalid log level type: %r", type(level))
            return

        self._log(level_no, msg, args, **kwargs)

    @contextmanager
    def useLevel(
        self, level: str | int, *, minimum: bool = False
    ) -> Generator[None, None, None]:
        """Use a context to temporarily log with a different log-level.

        Args:
            level: Log level to use (string name or numeric value)
            minimum: If True, only set the level if it's more verbose (lower
                numeric value) than the current effective level. This prevents
                downgrading from a more verbose level (e.g., TRACE) to a less
                verbose one (e.g., DEBUG). Compares against effective level
                (considering parent inheritance), matching setLevel(minimum=True)
                behavior. Defaults to False.

        Yields:
            None: Context manager yields control to the with block
        """
        # Save explicit level for restoration (not effective level)
        prev_level = self.level

        # Resolve level
        if isinstance(level, str):
            try:
                level_no = ApatheticLogging_Internal_LoggingUtils.getLevelNumber(level)
            except ValueError:
                self.error("Unknown log level: %r", level)
                # Yield control anyway so the 'with' block doesn't explode
                yield
                return
        elif isinstance(level, int):  # pyright: ignore[reportUnnecessaryIsInstance]
            level_no = level
        else:
            self.error("Invalid log level type: %r", type(level))
            yield
            return

        # Apply new level (only if more verbose when minimum=True)
        if minimum:
            # Compare against effective level (not explicit level) to match
            # setLevel(minimum=True) behavior. This ensures consistent behavior
            # when logger inherits level from parent.
            current_effective_level = self.getEffectiveLevel()
            # Lower number = more verbose, so only set if new level is more verbose
            if level_no < current_effective_level:
                self.setLevel(level_no)
            # Otherwise keep current level (don't downgrade)
        else:
            self.setLevel(level_no)

        try:
            yield
        finally:
            self.setLevel(prev_level)


# === apathetic_logging.logger_namespace ===
# src/apathetic_logging/logger_namespace.py
"""Logger namespace mixin that provides the Logger nested class.

See https://docs.python.org/3/library/logging.html#logging.Logger for the
complete list of standard library Logger methods.

Docstrings are adapted from the standard library logging.Logger documentation
licensed under the Python Software Foundation License Version 2.
"""


class ApatheticLogging_Internal_Logger:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the Logger nested class.

    This class contains the Logger implementation as a nested class, using
    the core Logger implementation.

    When mixed into apathetic_logging, it provides apathetic_logging.Logger.
    """

    class Logger(
        ApatheticLogging_Internal_LoggerCore,
    ):
        """Logger for all Apathetic tools.

        This Logger class is composed from:
        - Core Logger implementation
          (ApatheticLogging_Internal_LoggerCore, which inherits from logging.Logger)
        """


# === apathetic_logging.get_logger ===
# src/apathetic_logging/get_logger.py
"""GetLogger functionality for Apathetic Logging.

Docstrings are adapted from the standard library logging module documentation
licensed under the Python Software Foundation License Version 2.
"""


class ApatheticLogging_Internal_GetLogger:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the getLogger static method.

    This class contains the getLogger implementation as a static method.
    When mixed into apathetic_logging, it provides apathetic_logging.getLogger.
    """

    _LoggerType = TypeVar("_LoggerType", bound=logging.Logger)

    @staticmethod
    def _setLoggerClassTemporarily(
        klass: type[ApatheticLogging_Internal_GetLogger._LoggerType],
        name: str,
    ) -> ApatheticLogging_Internal_GetLogger._LoggerType:
        """Temporarily set the logger class, get/create a logger, then restore.

        This is an internal helper function used by getLoggerOfType to create
        a logger of a specific type when one doesn't already exist. It temporarily
        sets the logger class to the desired type, gets or creates the logger,
        then restores the original logger class.

        This function is mostly for internal use by the library. If you need
        a logger of a specific type, use getLoggerOfType instead, which provides
        all the conveniences (name inference, registry checking, etc.).

        Args:
            klass (logger class): The desired logger class type.
            name: The name of the logger to get.

        Returns:
            A logger instance of the specified type.
        """
        # stdlib unwrapped
        original_class = logging.getLoggerClass()
        logging.setLoggerClass(klass)
        # avoid circular dependency by using logging.getLogger directly
        logger = logging.getLogger(name)
        logging.setLoggerClass(original_class)
        typed_logger = cast("ApatheticLogging_Internal_GetLogger._LoggerType", logger)
        return typed_logger

    @staticmethod
    def _getOrCreateLoggerOfType(
        register_name: str,
        class_type: type[ApatheticLogging_Internal_GetLogger._LoggerType],
        *args: Any,
        **kwargs: Any,
    ) -> ApatheticLogging_Internal_GetLogger._LoggerType:
        """Get or create a logger of the specified type.

        Checks if a logger with the given name exists. If it exists but is not
        of the correct type, removes it and creates a new one. If it doesn't
        exist, creates a new logger of the specified type.

        Args:
            register_name: The name of the logger to get or create.
            class_type: The logger class type to use.
            *args: Additional positional arguments to pass to logging.getLogger.
            **kwargs: Additional keyword arguments to pass to logging.getLogger.

        Returns:
            A logger instance of the specified type.
        """
        _logging_utils = ApatheticLogging_Internal_LoggingUtils

        logger: logging.Logger | None = None
        registered = _logging_utils.hasLogger(register_name)
        if registered:
            logger = logging.getLogger(register_name, *args, **kwargs)
            if not isinstance(logger, class_type):
                _logging_utils.removeLogger(register_name)
                registered = False
        if not registered:  # may have changed above
            logger = ApatheticLogging_Internal_GetLogger._setLoggerClassTemporarily(
                class_type, register_name
            )
        typed_logger = cast("ApatheticLogging_Internal_GetLogger._LoggerType", logger)
        return typed_logger

    @staticmethod
    def _applyPropagateSetting(logger: logging.Logger) -> None:
        """Apply propagate setting to a logger from registry or default.

        Determines the propagate value from the registry (if set) or falls back
        to the default from constants, then applies it to the logger.

        Args:
            logger: The logger instance to apply the propagate setting to.
        """
        _constants = ApatheticLogging_Internal_Constants
        _registry_data = ApatheticLogging_Internal_RegistryData

        if _registry_data.registered_internal_propagate is not None:
            # Use registered value
            logger.propagate = _registry_data.registered_internal_propagate
        else:
            # Use default from constants
            logger.propagate = _constants.DEFAULT_PROPAGATE

    @staticmethod
    def getLogger(
        name: str | None = None,
        *args: Any,
        level: str | int | None = None,
        minimum: bool | None = None,
        extend: bool | None = None,
        **kwargs: Any,
    ) -> ApatheticLogging_Internal_Logger.Logger:
        """Return a logger with the specified name, creating it if necessary.

        Changes:
        - When name is None, infers the name automatically from
          the calling module's __package__ attribute by examining the call stack
          (using skip_frames=2 to correctly identify the caller)
          instead of returning the root logger.
        - When name is an empty string (""), returns the root logger
          as usual, matching standard library behavior.
        - Returns an apathetic_logging.Logger instance instead of
          the standard logging.Logger.

        Args:
            name: The name of the logger to get. If None, the logger name
                will be auto-inferred from the calling module's __package__.
                If an empty string (""), returns the root logger.
            *args: Additional positional arguments (for future-proofing)
            level: Exact log level to set on the logger. Accepts both string
                names (case-insensitive) and numeric values. If provided,
                sets the logger's level to this value. Defaults to None.
            minimum: If True, only set the level if it's more verbose (lower
                numeric value) than the current level. This prevents downgrading
                from a more verbose level (e.g., TRACE) to a less verbose one
                (e.g., DEBUG). If None, defaults to False. Only used when
                `level` is provided.
            extend: If True (default), extend the logging module.
            **kwargs: Additional keyword arguments (for future-proofing)

        Returns:
            A logger of type ApatheticLogging_Internal_Logger.Logger.

        Wrapper for logging.getLogger.

        https://docs.python.org/3.10/library/logging.html#logging.getLogger
        """
        _get_logger = ApatheticLogging_Internal_GetLogger
        _logger = ApatheticLogging_Internal_Logger
        skip_frames = 2
        result = _get_logger.getLoggerOfType(
            name,
            _logger.Logger,
            skip_frames,
            *args,
            level=level,
            minimum=minimum,
            extend=extend,
            **kwargs,
        )
        return cast("ApatheticLogging_Internal_Logger.Logger", result)  # type: ignore[redundant-cast]

    @staticmethod
    def getLoggerOfType(
        name: str | None,
        class_type: type[ApatheticLogging_Internal_GetLogger._LoggerType],
        skip_frames: int = 1,
        *args: Any,
        level: str | int | None = None,
        minimum: bool | None = None,
        extend: bool | None = True,
        **kwargs: Any,
    ) -> ApatheticLogging_Internal_GetLogger._LoggerType:
        """Get a logger of the specified type, creating it if necessary.

        Changes:
        - When name is None, infers the name automatically from
          the calling module's __package__ attribute by examining the call stack
          (using skip_frames to correctly identify the caller)
          instead of returning the root logger.
        - When name is an empty string (""), returns the root logger
          as usual, matching standard library behavior.
        - Returns a class_type instance instead of
          the standard logging.Logger.

        Args:
            name: The name of the logger to get. If None, the logger name
                will be auto-inferred from the calling module's __package__.
                If an empty string (""), returns the root logger.
            class_type: The logger class type to use.
            skip_frames: Number of frames to skip when inferring logger name.
                Prefer using as a keyword argument (e.g., skip_frames=2) for clarity.
            *args: Additional positional arguments (for future-proofing)
            level: Exact log level to set on the logger. Accepts both string
                names (case-insensitive) and numeric values. If provided,
                sets the logger's level to this value. Defaults to None.
            minimum: If True, only set the level if it's more verbose (lower
                numeric value) than the current level. This prevents downgrading
                from a more verbose level (e.g., TRACE) to a less verbose one
                (e.g., DEBUG). If None, defaults to False. Only used when
                `level` is provided.
            extend: If True (default), extend the logging module.
            **kwargs: Additional keyword arguments (for future-proofing)

        Returns:
            A logger instance of the specified type.

        Wrapper for logging.getLogger.

        https://docs.python.org/3.10/library/logging.html#logging.getLogger
        """
        _logging_utils = ApatheticLogging_Internal_LoggingUtils

        # Check compatibility mode for getLogger(None) behavior

        _registry_data = ApatheticLogging_Internal_RegistryData
        compatibility_mode = (
            _registry_data.registered_internal_compatibility_mode
            if _registry_data.registered_internal_compatibility_mode is not None
            else False
        )

        # In compatibility mode, getLogger(None) returns root logger (stdlib behavior)
        if name is None and compatibility_mode:
            register_name: str = ""
        else:
            # Resolve logger name (with inference if needed)
            # Note: Empty string ("") is a special case - getDefaultLoggerName
            # returns it as-is (root logger, matching stdlib behavior). This is
            # handled by the
            # early return in getDefaultLoggerName when logger_name is not None.
            # skip_frames+1 because: getLoggerOfType -> getDefaultLoggerName -> caller
            # check_registry=True because getLogger() should use a previously registered
            # name if available, which is the expected behavior for "get" operations.
            # raise_on_error=True because getLogger() requires a logger name.
            # infer=True and register=True - getLogger() infers and stores (matches old
            # resolveLoggerName behavior where inferred names were automatically stored)
            register_name_raw = _logging_utils.getDefaultLoggerName(
                name,
                check_registry=True,
                skip_frames=skip_frames + 1,
                raise_on_error=True,
                infer=True,
                register=True,
            )
            # With raise_on_error=True, register_name is guaranteed to be str, not None
            register_name = register_name_raw  # type: ignore[assignment]

        # extend logging module
        if extend and hasattr(class_type, "extendLoggingModule"):
            class_type.extendLoggingModule()  # type: ignore[attr-defined]

        # Get or create logger of the correct type
        logger = ApatheticLogging_Internal_GetLogger._getOrCreateLoggerOfType(
            register_name, class_type, *args, **kwargs
        )

        # Apply log level settings if provided
        if level is not None:
            logger.setLevel(level, minimum=minimum)  # type: ignore[call-arg]

        # Apply propagate setting from registry or default
        ApatheticLogging_Internal_GetLogger._applyPropagateSetting(logger)

        return logger


# === apathetic_logging.logging_std_camel ===
# src/apathetic_logging/logging_std_camel.py
"""Camel case convenience functions for standard logging module.

Docstrings are adapted from the standard library logging module documentation
licensed under the Python Software Foundation License Version 2.
"""


class ApatheticLogging_Internal_StdCamelCase:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides camelCase convenience functions for logging.*.

    This class contains camelCase wrapper functions for standard library
    `logging.*` functions that use camelCase naming. These wrappers provide
    direct compatibility with the standard logging module interface while
    maintaining full compatibility with the underlying logging module functions.

    When mixed into apathetic_logging, it provides camelCase functions
    that match the standard logging module functions (e.g., `basicConfig`,
    `addLevelName`, `setLoggerClass`, `getLogger`).
    """

    # --- Configuration Functions ---

    @staticmethod
    def basicConfig(*args: Any, **kwargs: Any) -> None:
        """Do basic configuration for the logging system.

        This function does nothing if the root logger already has handlers
        configured, unless the keyword argument *force* is set to ``True``.
        It is a convenience method intended for use by simple scripts
        to do one-shot configuration of the logging package.

        The default behaviour is to create a StreamHandler which writes to
        sys.stderr, set a formatter using the BASIC_FORMAT format string, and
        add the handler to the root logger.

        A number of optional keyword arguments may be specified, which can alter
        the default behaviour.

        Wrapper for logging.basicConfig with camelCase naming.

        https://docs.python.org/3.10/library/logging.html#logging.basicConfig
        """
        logging.basicConfig(*args, **kwargs)

    @staticmethod
    def captureWarnings(
        capture: bool,  # noqa: FBT001
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Redirect warnings to the logging package.

        If capture is true, redirect all warnings to the logging package.
        If capture is False, ensure that warnings are not redirected to logging
        but to their original destinations.

        Wrapper for logging.captureWarnings with camelCase naming.

        https://docs.python.org/3.10/library/logging.html#logging.captureWarnings
        """
        logging.captureWarnings(capture, *args, **kwargs)

    @staticmethod
    def shutdown(*args: Any, **kwargs: Any) -> None:
        """Perform any cleanup actions in the logging system.

        Perform any cleanup actions in the logging system (e.g. flushing
        buffers). Should be called at application exit.

        Wrapper for logging.shutdown with camelCase naming.

        https://docs.python.org/3.10/library/logging.html#logging.shutdown
        """
        logging.shutdown(*args, **kwargs)

    # --- Level Management Functions ---

    @staticmethod
    def addLevelName(level: int, level_name: str, *args: Any, **kwargs: Any) -> None:
        """Associate a level name with a numeric level.

        Associate 'level_name' with 'level'. This is used when converting
        levels to text during message formatting.

        Wrapper for logging.addLevelName with camelCase naming.

        https://docs.python.org/3.10/library/logging.html#logging.addLevelName
        """
        logging.addLevelName(level, level_name, *args, **kwargs)

    @staticmethod
    def getLevelName(level: int, *args: Any, **kwargs: Any) -> str | int:
        """Return the textual or numeric representation of a logging level.

        If the level is one of the predefined levels (CRITICAL, ERROR, WARNING,
        INFO, DEBUG) then you get the corresponding string. If you have
        associated levels with names using addLevelName then the name you have
        associated with 'level' is returned.

        If a numeric value corresponding to one of the defined levels is passed
        in, the corresponding string representation is returned.

        If a string representation of the level is passed in, the corresponding
        numeric value is returned.

        If no matching numeric or string value is passed in, the string
        'Level %s' % level is returned.

        Wrapper for logging.getLevelName with camelCase naming.

        https://docs.python.org/3.10/library/logging.html#logging.getLevelName
        """
        return logging.getLevelName(level, *args, **kwargs)

    @staticmethod
    def getLevelNamesMapping(*args: Any, **kwargs: Any) -> dict[int, str]:
        """Return a mapping of all level names to their numeric values.

        **Requires Python 3.11+**

        Wrapper for logging.getLevelNamesMapping with camelCase naming.

        https://docs.python.org/3.11/library/logging.html#logging.getLevelNamesMapping
        """
        _logging_utils = ApatheticLogging_Internal_LoggingUtils
        _logging_utils.checkPythonVersionRequirement((3, 11), "getLevelNamesMapping")
        return logging.getLevelNamesMapping(*args, **kwargs)  # type: ignore[attr-defined,no-any-return]

    @staticmethod
    def disable(level: int = 50, *args: Any, **kwargs: Any) -> None:
        """Disable all logging calls of severity 'level' and below.

        Wrapper for logging.disable with camelCase naming.

        https://docs.python.org/3.10/library/logging.html#logging.disable
        """
        logging.disable(level, *args, **kwargs)

    # --- Logger Management Functions ---

    @staticmethod
    def getLogger(
        name: str | None = None, *_args: Any, **_kwargs: Any
    ) -> logging.Logger:
        """Return a logger with the specified name, creating it if necessary.

        If no name is specified, return the root logger.

        Returns an logging.Logger instance.

        Wrapper for logging.getLogger with camelCase naming.

        https://docs.python.org/3.10/library/logging.html#logging.getLogger
        """
        return logging.getLogger(name)

    @staticmethod
    def getLoggerClass(*args: Any, **kwargs: Any) -> type[logging.Logger]:
        """Return the class to be used when instantiating a logger.

        Wrapper for logging.getLoggerClass with camelCase naming.

        https://docs.python.org/3.10/library/logging.html#logging.getLoggerClass
        """
        return logging.getLoggerClass(*args, **kwargs)

    @staticmethod
    def setLoggerClass(klass: type[logging.Logger], *args: Any, **kwargs: Any) -> None:
        """Set the class to be used when instantiating a logger.

        The class should define __init__() such that only a name argument is
        required, and the __init__() should call Logger.__init__().

        Args:
            klass (logger class): The logger class to use.
            *args: Additional positional arguments (for future-proofing).
            **kwargs: Additional keyword arguments (for future-proofing).

        Wrapper for logging.setLoggerClass with camelCase naming.

        https://docs.python.org/3.10/library/logging.html#logging.setLoggerClass
        """
        logging.setLoggerClass(klass, *args, **kwargs)

    # --- Handler Management Functions ---

    @staticmethod
    def getHandlerByName(
        name: str, *args: Any, **kwargs: Any
    ) -> logging.Handler | None:
        """Get a handler with the specified name, or None if there isn't one.

        **Requires Python 3.12+**

        Wrapper for logging.getHandlerByName with camelCase naming.

        https://docs.python.org/3.12/library/logging.html#logging.getHandlerByName
        """
        _logging_utils = ApatheticLogging_Internal_LoggingUtils
        _logging_utils.checkPythonVersionRequirement((3, 12), "getHandlerByName")
        return logging.getHandlerByName(name, *args, **kwargs)  # type: ignore[attr-defined,no-any-return]

    @staticmethod
    def getHandlerNames(*args: Any, **kwargs: Any) -> list[str]:
        """Return all known handler names as an immutable set.

        **Requires Python 3.12+**

        Wrapper for logging.getHandlerNames with camelCase naming.

        https://docs.python.org/3.12/library/logging.html#logging.getHandlerNames
        """
        _logging_utils = ApatheticLogging_Internal_LoggingUtils
        _logging_utils.checkPythonVersionRequirement((3, 12), "getHandlerNames")
        return logging.getHandlerNames(*args, **kwargs)  # type: ignore[attr-defined,no-any-return]

    # --- Factory Functions ---

    @staticmethod
    def getLogRecordFactory(
        *args: Any, **kwargs: Any
    ) -> Callable[..., logging.LogRecord]:
        """Return the factory to be used when instantiating a log record.

        Wrapper for logging.getLogRecordFactory with camelCase naming.

        https://docs.python.org/3.10/library/logging.html#logging.getLogRecordFactory
        """
        return logging.getLogRecordFactory(*args, **kwargs)

    @staticmethod
    def setLogRecordFactory(
        factory: Callable[..., logging.LogRecord], *args: Any, **kwargs: Any
    ) -> None:
        """Set the factory to be used when instantiating a log record.

        :param factory: A callable which will be called to instantiate
        a log record.

        Wrapper for logging.setLogRecordFactory with camelCase naming.

        https://docs.python.org/3.10/library/logging.html#logging.setLogRecordFactory
        """
        logging.setLogRecordFactory(factory, *args, **kwargs)

    @staticmethod
    def makeLogRecord(
        dict: dict[str, Any],  # noqa: A002  # Required to match stdlib logging.makeLogRecord signature
        *args: Any,
        **kwargs: Any,
    ) -> logging.LogRecord:
        """Make a LogRecord whose attributes are defined by a dictionary.

        This function is useful for converting a logging event received over
        a socket connection (which is sent as a dictionary) into a LogRecord
        instance.

        Wrapper for logging.makeLogRecord with camelCase naming.

        https://docs.python.org/3.10/library/logging.html#logging.makeLogRecord
        """
        return logging.makeLogRecord(dict, *args, **kwargs)

    # --- Logging Functions ---

    @staticmethod
    def critical(msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message with severity 'CRITICAL' on the root logger.

        If the logger has no handlers, call basicConfig() to add a console
        handler with a pre-defined format.

        Wrapper for logging.critical with camelCase naming.

        https://docs.python.org/3.10/library/logging.html#logging.critical
        """
        logging.critical(msg, *args, **kwargs)  # noqa: LOG015

    @staticmethod
    def debug(msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message with severity 'DEBUG' on the root logger.

        If the logger has no handlers, call basicConfig() to add a console
        handler with a pre-defined format.

        Wrapper for logging.debug with camelCase naming.

        https://docs.python.org/3.10/library/logging.html#logging.debug
        """
        logging.debug(msg, *args, **kwargs)  # noqa: LOG015

    @staticmethod
    def error(msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message with severity 'ERROR' on the root logger.

        If the logger has no handlers, call basicConfig() to add a console
        handler with a pre-defined format.

        Wrapper for logging.error with camelCase naming.

        https://docs.python.org/3.10/library/logging.html#logging.error
        """
        logging.error(msg, *args, **kwargs)  # noqa: LOG015

    @staticmethod
    def exception(msg: str, *args: Any, exc_info: bool = True, **kwargs: Any) -> None:
        """Log a message with severity 'ERROR' on the root logger, with exception info.

        If the logger has no handlers, basicConfig() is called to add a console
        handler with a pre-defined format.

        Wrapper for logging.exception with camelCase naming.

        https://docs.python.org/3.10/library/logging.html#logging.exception
        """
        logging.exception(msg, *args, exc_info=exc_info, **kwargs)  # noqa: LOG015

    @staticmethod
    def fatal(msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message with severity 'CRITICAL' on the root logger.

        Don't use this function, use critical() instead.

        Wrapper for logging.fatal with camelCase naming.

        https://docs.python.org/3.10/library/logging.html#logging.fatal
        """
        logging.fatal(msg, *args, **kwargs)

    @staticmethod
    def info(msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message with severity 'INFO' on the root logger.

        If the logger has no handlers, call basicConfig() to add a console
        handler with a pre-defined format.

        Wrapper for logging.info with camelCase naming.

        https://docs.python.org/3.10/library/logging.html#logging.info
        """
        logging.info(msg, *args, **kwargs)  # noqa: LOG015

    @staticmethod
    def log(level: int, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log 'msg % args' with the integer severity 'level' on the root logger.

        If the logger has no handlers, call basicConfig() to add a console
        handler with a pre-defined format.

        Wrapper for logging.log with camelCase naming.

        https://docs.python.org/3.10/library/logging.html#logging.log
        """
        logging.log(level, msg, *args, **kwargs)  # noqa: LOG015

    @staticmethod
    def warn(msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message with severity 'WARNING' on the root logger.

        If the logger has no handlers, call basicConfig() to add a console
        handler with a pre-defined format.

        Wrapper for logging.warn with camelCase naming.

        https://docs.python.org/3.10/library/logging.html#logging.warn
        """
        logging.warning(msg, *args, **kwargs)  # noqa: LOG015

    @staticmethod
    def warning(msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message with severity 'WARNING' on the root logger.

        If the logger has no handlers, call basicConfig() to add a console
        handler with a pre-defined format.

        Wrapper for logging.warning with camelCase naming.

        https://docs.python.org/3.10/library/logging.html#logging.warning
        """
        logging.warning(msg, *args, **kwargs)  # noqa: LOG015

    # --- Custom Level Functions ---

    @staticmethod
    def trace(msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message with severity 'TRACE' on the root logger.

        TRACE is more verbose than DEBUG. If the logger has no handlers,
        call basicConfig() to add a console handler with a pre-defined format.

        This function gets an apathetic_logging.Logger instance (ensuring
        the root logger is an apathetic logger) and calls its trace() method.
        """
        _get_logger = ApatheticLogging_Internal_GetLogger
        _logger = ApatheticLogging_Internal_Logger
        _constants = ApatheticLogging_Internal_Constants
        # Ensure logging module is extended
        _logger.Logger.extendLoggingModule()
        # Get root logger - it should be an apathetic logger now
        logger = _get_logger.getLogger("", extend=True)
        # Check if logger has trace method (it should if it's an apathetic logger)
        if hasattr(logger, "trace"):
            logger.trace(msg, *args, **kwargs)
        # Fallback: if root logger is still a standard logger, use _log directly
        # This can happen if root logger was created before extendLoggingModule
        elif logger.isEnabledFor(_constants.TRACE_LEVEL):
            logger._log(_constants.TRACE_LEVEL, msg, args, **kwargs)  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]

    @staticmethod
    def detail(msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message with severity 'DETAIL' on the root logger.

        DETAIL is more detailed than INFO. If the logger has no handlers,
        call basicConfig() to add a console handler with a pre-defined format.

        This function gets an apathetic_logging.Logger instance (ensuring
        the root logger is an apathetic logger) and calls its detail() method.
        """
        _get_logger = ApatheticLogging_Internal_GetLogger
        _logger = ApatheticLogging_Internal_Logger
        _constants = ApatheticLogging_Internal_Constants
        # Ensure logging module is extended
        _logger.Logger.extendLoggingModule()
        # Get root logger - it should be an apathetic logger now
        logger = _get_logger.getLogger("", extend=True)
        # Check if logger has detail method (it should if it's an apathetic logger)
        if hasattr(logger, "detail"):
            logger.detail(msg, *args, **kwargs)
        # Fallback: if root logger is still a standard logger, use _log directly
        elif logger.isEnabledFor(_constants.DETAIL_LEVEL):
            logger._log(_constants.DETAIL_LEVEL, msg, args, **kwargs)  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]

    @staticmethod
    def minimal(msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message with severity 'MINIMAL' on the root logger.

        MINIMAL is less detailed than INFO. If the logger has no handlers,
        call basicConfig() to add a console handler with a pre-defined format.

        This function gets an apathetic_logging.Logger instance (ensuring
        the root logger is an apathetic logger) and calls its minimal() method.
        """
        _get_logger = ApatheticLogging_Internal_GetLogger
        _logger = ApatheticLogging_Internal_Logger
        _constants = ApatheticLogging_Internal_Constants
        # Ensure logging module is extended
        _logger.Logger.extendLoggingModule()
        # Get root logger - it should be an apathetic logger now
        logger = _get_logger.getLogger("", extend=True)
        # Check if logger has minimal method (it should if it's an apathetic logger)
        if hasattr(logger, "minimal"):
            logger.minimal(msg, *args, **kwargs)
        # Fallback: if root logger is still a standard logger, use _log directly
        elif logger.isEnabledFor(_constants.MINIMAL_LEVEL):
            logger._log(_constants.MINIMAL_LEVEL, msg, args, **kwargs)  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]

    # --- Utility Functions ---

    @staticmethod
    def currentframe(*args: Any, **kwargs: Any) -> FrameType | None:
        """Return the frame object for the caller's stack frame.

        Wrapper for logging.currentframe with camelCase naming.

        https://docs.python.org/3.10/library/logging.html#logging.currentframe
        """
        return logging.currentframe(*args, **kwargs)


# === apathetic_logging.namespace ===
# src/apathetic_logging/namespace.py
"""Shared Apathetic CLI logger implementation.

See https://docs.python.org/3/library/logging.html for the complete list of
standard library logging functions that are wrapped by this namespace.

Docstrings are adapted from the standard library logging module documentation
licensed under the Python Software Foundation License Version 2.
"""


# --- Apathetic Logging Namespace -------------------------------------------


class apathetic_logging(  # noqa: N801
    ApatheticLogging_Internal_Constants,
    ApatheticLogging_Internal_DualStreamHandler,
    ApatheticLogging_Internal_GetLogger,
    ApatheticLogging_Internal_Logger,
    ApatheticLogging_Internal_LoggingUtils,
    ApatheticLogging_Internal_Registry,
    ApatheticLogging_Internal_RegistryData,
    ApatheticLogging_Internal_SafeLogging,
    ApatheticLogging_Internal_TagFormatter,
    ApatheticLogging_Internal_StdCamelCase,  # keep last
):
    """Namespace for apathetic logging functionality.

    All logger functionality is accessed via this namespace class to minimize
    global namespace pollution when the library is embedded in a stitched script.

    **Classes:**
    - ``Logger`` → ``ApatheticLogging_Internal_Logger``
    - ``TagFormatter`` → ``ApatheticLogging_Internal_TagFormatter``
    - ``DualStreamHandler`` → ``ApatheticLogging_Internal_DualStreamHandler``

    **Static Methods:**
    - ``getLogger()`` → ``ApatheticLogging_Internal_GetLogger``
    - ``registerDefaultLogLevel()`` → ``ApatheticLogging_Internal_Registry``
    - ``registerLogLevelEnvVars()`` → ``ApatheticLogging_Internal_Registry``
    - ``registerLogger()`` → ``ApatheticLogging_Internal_Registry``
    - ``safeLog()`` → ``ApatheticLogging_Internal_SafeLogging``
    - ``safeTrace()`` → ``ApatheticLogging_Internal_SafeLogging``
    - ``makeSafeTrace()`` → ``ApatheticLogging_Internal_SafeLogging``

    **Constants:**
    - ``DEFAULT_APATHETIC_LOG_LEVEL`` → ``ApatheticLogging_Internal_Constants``
    - ``DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS`` → ``ApatheticLogging_Internal_Constants``
    - ``SAFE_TRACE_ENABLED`` → ``ApatheticLogging_Internal_Constants``
    - ``TEST_LEVEL`` → ``ApatheticLogging_Internal_Constants``
    - ``TRACE_LEVEL`` → ``ApatheticLogging_Internal_Constants``
    - ``MINIMAL_LEVEL`` → ``ApatheticLogging_Internal_Constants``
    - ``DETAIL_LEVEL`` → ``ApatheticLogging_Internal_Constants``
    - ``SILENT_LEVEL`` → ``ApatheticLogging_Internal_Constants``
    - ``LEVEL_ORDER`` → ``ApatheticLogging_Internal_Constants``
    - ``ANSIColors`` → ``ApatheticLogging_Internal_Constants``
    - ``TAG_STYLES`` → ``ApatheticLogging_Internal_Constants``
    """


# Ensure logging module is extended with TEST, TRACE, MINIMAL, DETAIL, and SILENT
# levels
# This must be called before any loggers are created
# This runs when namespace.py is executed (both installed and stitched modes)
# The method is idempotent, so safe to call multiple times if needed
apathetic_logging.Logger.extendLoggingModule()

# Note: All exports are handled in __init__.py
# - For library builds (installed/singlefile): __init__.py is included, exports happen
# - For embedded builds: __init__.py is excluded, no exports (only class available)


# === apathetic_logging.__init__ ===
# src/apathetic_logging/__init__.py
"""Apathetic Logging implementation."""


# Get reference to the namespace class
# In stitched mode: class is already defined in namespace.py (executed before this)
# In installed mode: import from namespace module
_is_standalone = globals().get("__STANDALONE__", False)

if _is_standalone:
    # Stitched mode: class already defined in namespace.py
    # Get reference to the class (it's already in globals from namespace.py)
    _apathetic_logging_raw = globals().get("apathetic_logging")
    if _apathetic_logging_raw is None:
        # Fallback: should not happen, but handle gracefully
        msg = "apathetic_logging class not found in standalone mode"
        raise RuntimeError(msg)
    # Type cast to help mypy understand this is the apathetic_logging class
    # The import gives us type[apathetic_logging], so cast to
    # type[_apathetic_logging_class]
    apathetic_logging = cast("type[_apathetic_logging_class]", _apathetic_logging_raw)
else:
    # Installed mode: import from namespace module
    # This block is only executed in installed mode, not in standalone builds

    # Ensure the else block is not empty (build script may remove import)
    _ = apathetic_logging

# Export all namespace items for convenience
# These are aliases to apathetic_logging.*
#
# Note: In embedded builds, __init__.py is excluded from the stitch,
# so this code never runs and no exports happen (only the class is available).
# In singlefile/installed builds, __init__.py is included, so exports happen.
DEFAULT_APATHETIC_LOG_LEVEL = apathetic_logging.DEFAULT_APATHETIC_LOG_LEVEL
DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS = (
    apathetic_logging.DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS
)
LEVEL_ORDER = apathetic_logging.LEVEL_ORDER
SILENT_LEVEL = apathetic_logging.SILENT_LEVEL
TAG_STYLES = apathetic_logging.TAG_STYLES
TEST_LEVEL = apathetic_logging.TEST_LEVEL
safeTrace = apathetic_logging.safeTrace
SAFE_TRACE_ENABLED = apathetic_logging.SAFE_TRACE_ENABLED
TRACE_LEVEL = apathetic_logging.TRACE_LEVEL
MINIMAL_LEVEL = apathetic_logging.MINIMAL_LEVEL
DETAIL_LEVEL = apathetic_logging.DETAIL_LEVEL
NOTSET_LEVEL = apathetic_logging.NOTSET_LEVEL

# ANSI Colors
ANSIColors = apathetic_logging.ANSIColors

# Classes
DualStreamHandler = apathetic_logging.DualStreamHandler
TagFormatter = apathetic_logging.TagFormatter
# Logger is a nested class in ApatheticLogging_Internal_Logger that
# inherits from logging.Logger.
# Use TypeAlias to help mypy understand this is a class type.
if TYPE_CHECKING:
    Logger: TypeAlias = ApatheticLogging_Internal_Logger.Logger
else:
    Logger = apathetic_logging.Logger

# Functions (camelCase - stdlib wrappers)
addLevelName = apathetic_logging.addLevelName
basicConfig = apathetic_logging.basicConfig
captureWarnings = apathetic_logging.captureWarnings
critical = apathetic_logging.critical
currentframe = apathetic_logging.currentframe
debug = apathetic_logging.debug
detail = apathetic_logging.detail
disable = apathetic_logging.disable
error = apathetic_logging.error
exception = apathetic_logging.exception
fatal = apathetic_logging.fatal
getHandlerByName = apathetic_logging.getHandlerByName
getHandlerNames = apathetic_logging.getHandlerNames
getLevelName = apathetic_logging.getLevelName
getLevelNamesMapping = apathetic_logging.getLevelNamesMapping
getLogRecordFactory = apathetic_logging.getLogRecordFactory
getLogger = apathetic_logging.getLogger
getLoggerClass = apathetic_logging.getLoggerClass
info = apathetic_logging.info
log = apathetic_logging.log
makeLogRecord = apathetic_logging.makeLogRecord
minimal = apathetic_logging.minimal
setLogRecordFactory = apathetic_logging.setLogRecordFactory
setLoggerClass = apathetic_logging.setLoggerClass
shutdown = apathetic_logging.shutdown
trace = apathetic_logging.trace
warn = apathetic_logging.warn
warning = apathetic_logging.warning

# Functions (camelCase - library functions)
getDefaultLogLevel = apathetic_logging.getDefaultLogLevel
getCompatibilityMode = apathetic_logging.getCompatibilityMode
getDefaultLoggerName = apathetic_logging.getDefaultLoggerName
getDefaultPropagate = apathetic_logging.getDefaultPropagate
getLevelNumber = apathetic_logging.getLevelNumber
getLevelNameStr = apathetic_logging.getLevelNameStr
getLogLevelEnvVars = apathetic_logging.getLogLevelEnvVars
getLoggerOfType = apathetic_logging.getLoggerOfType
getRegisteredLoggerName = apathetic_logging.getRegisteredLoggerName
getTargetPythonVersion = apathetic_logging.getTargetPythonVersion
hasLogger = apathetic_logging.hasLogger
makeSafeTrace = apathetic_logging.makeSafeTrace
registerDefaultLogLevel = apathetic_logging.registerDefaultLogLevel
registerLogLevelEnvVars = apathetic_logging.registerLogLevelEnvVars
registerLogger = apathetic_logging.registerLogger
registerCompatibilityMode = apathetic_logging.registerCompatibilityMode
registerPropagate = apathetic_logging.registerPropagate
registerTargetPythonVersion = apathetic_logging.registerTargetPythonVersion
removeLogger = apathetic_logging.removeLogger
safeLog = apathetic_logging.safeLog


__all__ = [
    "DEFAULT_APATHETIC_LOG_LEVEL",
    "DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS",
    "DETAIL_LEVEL",
    "LEVEL_ORDER",
    "MINIMAL_LEVEL",
    "NOTSET_LEVEL",
    "SAFE_TRACE_ENABLED",
    "SILENT_LEVEL",
    "TAG_STYLES",
    "TEST_LEVEL",
    "TRACE_LEVEL",
    "ANSIColors",
    "DualStreamHandler",
    "Logger",
    "TagFormatter",
    "addLevelName",
    "apathetic_logging",
    "basicConfig",
    "captureWarnings",
    "critical",
    "currentframe",
    "debug",
    "detail",
    "disable",
    "error",
    "exception",
    "fatal",
    "getCompatibilityMode",
    "getDefaultLogLevel",
    "getDefaultLoggerName",
    "getDefaultPropagate",
    "getHandlerByName",
    "getHandlerNames",
    "getLevelName",
    "getLevelNameStr",
    "getLevelNamesMapping",
    "getLevelNumber",
    "getLogLevelEnvVars",
    "getLogRecordFactory",
    "getLogger",
    "getLoggerClass",
    "getLoggerOfType",
    "getRegisteredLoggerName",
    "getTargetPythonVersion",
    "hasLogger",
    "info",
    "log",
    "makeLogRecord",
    "makeSafeTrace",
    "minimal",
    "registerCompatibilityMode",
    "registerDefaultLogLevel",
    "registerLogLevelEnvVars",
    "registerLogger",
    "registerPropagate",
    "registerTargetPythonVersion",
    "removeLogger",
    "safeLog",
    "safeTrace",
    "setLogRecordFactory",
    "setLoggerClass",
    "shutdown",
    "trace",
    "warn",
    "warning",
]


# === apathetic_utils.ci ===
# src/apathetic_utils/ci.py
"""CI environment detection utilities."""


# CI environment variable names that indicate CI environment
CI_ENV_VARS = ("CI", "GITHUB_ACTIONS", "GIT_TAG", "GITHUB_REF")


def is_ci() -> bool:
    """Check if running in a CI environment.

    Returns True if any of the following environment variables are set:
    - CI: Generic CI indicator (set by most CI systems)
    - GITHUB_ACTIONS: GitHub Actions specific
    - GIT_TAG: Indicates a tagged build
    - GITHUB_REF: GitHub Actions ref (branch/tag)

    Returns:
        True if running in CI, False otherwise
    """
    return bool(any(os.getenv(var) for var in CI_ENV_VARS))


# === apathetic_utils.files ===
# src/serger/utils/utils_files.py


def _strip_jsonc_comments(text: str) -> str:  # noqa: PLR0912
    """Strip comments from JSONC while preserving string contents.

    Handles //, #, and /* */ comments without modifying content inside strings.
    """
    result: list[str] = []
    in_string = False
    in_escape = False
    i = 0
    while i < len(text):
        ch = text[i]

        # Handle escape sequences in strings
        if in_escape:
            result.append(ch)
            in_escape = False
            i += 1
            continue

        if ch == "\\" and in_string:
            result.append(ch)
            in_escape = True
            i += 1
            continue

        # Toggle string state
        if ch in ('"', "'") and (not in_string or text[i - 1 : i] != "\\"):
            in_string = not in_string
            result.append(ch)
            i += 1
            continue

        # If in a string, keep everything
        if in_string:
            result.append(ch)
            i += 1
            continue

        # Outside strings: handle comments
        # Check for // comment (but skip URLs like http://)
        if (
            ch == "/"
            and i + 1 < len(text)
            and text[i + 1] == "/"
            and not (i > 0 and text[i - 1] == ":")
        ):
            # Skip to end of line
            while i < len(text) and text[i] != "\n":
                i += 1
            if i < len(text):
                result.append("\n")
                i += 1
            continue

        # Check for # comment
        if ch == "#":
            # Skip to end of line
            while i < len(text) and text[i] != "\n":
                i += 1
            if i < len(text):
                result.append("\n")
                i += 1
            continue

        # Check for block comments /* ... */
        if ch == "/" and i + 1 < len(text) and text[i + 1] == "*":
            # Skip to end of block comment
            i += 2
            while i + 1 < len(text):
                if text[i] == "*" and text[i + 1] == "/":
                    i += 2
                    break
                i += 1
            continue

        # Regular character
        result.append(ch)
        i += 1

    return "".join(result)


def load_toml(path: Path, *, required: bool = False) -> dict[str, Any] | None:
    """Load and parse a TOML file, supporting Python 3.10 and 3.11+.

    Uses:
    - `tomllib` (Python 3.11+ standard library)
    - `tomli` (required for Python 3.10 - must be installed separately)

    Args:
        path: Path to TOML file
        required: If True, raise RuntimeError when tomli is missing on Python 3.10.
                  If False, return None when unavailable (caller handles gracefully).

    Returns:
        Parsed TOML data as a dictionary, or None if unavailable and not required

    Raises:
        FileNotFoundError: If the file doesn't exist
        RuntimeError: If required=True and neither tomllib nor tomli is available
        ValueError: If the file cannot be parsed
    """
    if not path.exists():
        xmsg = f"TOML file not found: {path}"
        raise FileNotFoundError(xmsg)

    # Try tomllib (Python 3.11+)
    try:
        import tomllib  # type: ignore[import-not-found] # noqa: PLC0415

        with path.open("rb") as f:
            return tomllib.load(f)  # type: ignore[no-any-return]
    except ImportError:
        pass

    # Try tomli (required for Python 3.10)
    try:
        import tomli  # type: ignore[import-not-found,unused-ignore] # noqa: PLC0415  # pyright: ignore[reportMissingImports]

        with path.open("rb") as f:
            return tomli.load(f)  # type: ignore[no-any-return,unused-ignore]  # pyright: ignore[reportUnknownReturnType]
    except ImportError:
        if required:
            xmsg = (
                "TOML parsing requires 'tomli' package on Python 3.10. "
                "Install it with: pip install tomli, or disable pyproject.toml support "
                "by setting 'use_pyproject_metadata: false' in your config."
            )
            raise RuntimeError(xmsg) from None
        return None


def load_jsonc(path: Path) -> dict[str, Any] | list[Any] | None:
    """Load JSONC (JSON with comments and trailing commas)."""
    logger = getLogger()
    logger.trace(f"[load_jsonc] Loading from {path}")

    if not path.exists():
        xmsg = f"JSONC file not found: {path}"
        raise FileNotFoundError(xmsg)

    if not path.is_file():
        xmsg = f"Expected a file: {path}"
        raise ValueError(xmsg)

    text = path.read_text(encoding="utf-8")
    text = _strip_jsonc_comments(text)

    # Remove trailing commas before } or ]
    text = re.sub(r",(?=\s*[}\]])", "", text)

    # Trim whitespace
    text = text.strip()

    if not text:
        # Empty or only comments → interpret as "no config"
        return None

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        xmsg = (
            f"Invalid JSONC syntax in {path}:"
            f" {e.msg} (line {e.lineno}, column {e.colno})"
        )
        raise ValueError(xmsg) from e

    # Guard against scalar roots (invalid config structure)
    if not isinstance(data, (dict, list)):
        xmsg = f"Invalid JSONC root type: {type(data).__name__}"
        raise ValueError(xmsg)  # noqa: TRY004

    # narrow type
    result = cast("dict[str, Any] | list[Any]", data)
    logger.trace(
        f"[load_jsonc] Loaded {type(result).__name__} with"
        f" {len(result) if hasattr(result, '__len__') else 'N/A'} items"
    )
    return result


# === apathetic_utils.paths ===
# src/serger/utils/utils_paths.py


def normalize_path_string(raw: str) -> str:
    r"""Normalize a user-supplied path string for cross-platform use.

    Industry-standard (Git/Node/Python) rules:
      - Treat both '/' and '\\' as valid separators and normalize all to '/'.
      - Replace escaped spaces ('\\ ') with real spaces.
      - Collapse redundant slashes (preserve protocol prefixes like 'file://').
      - Never resolve '.' or '..' or touch the filesystem.
      - Never raise for syntax; normalization is always possible.

    This is the pragmatic cross-platform normalization strategy used by
    Git, Node.js, and Python build tools.
    This function is purely lexical — it normalizes syntax, not filesystem state.
    """
    logger = getLogger()
    if not raw:
        return ""

    path = raw.strip()

    # Handle escaped spaces (common shell copy-paste)
    if "\\ " in path:
        fixed = path.replace("\\ ", " ")
        logger.warning("Normalizing escaped spaces in path: %r → %s", path, fixed)
        path = fixed

    # Normalize all backslashes to forward slashes
    path = path.replace("\\", "/")

    # Collapse redundant slashes (keep protocol //)
    collapsed_slashes = re.sub(r"(?<!:)//+", "/", path)
    if collapsed_slashes != path:
        logger.trace("Collapsed redundant slashes: %r → %r", path, collapsed_slashes)
        path = collapsed_slashes

    return path


def has_glob_chars(s: str) -> bool:
    return any(c in s for c in "*?[]")


def get_glob_root(pattern: str) -> Path:
    """Return the non-glob portion of a path like 'src/**/*.txt'.

    Normalizes paths to cross-platform.
    """
    if not pattern:
        return Path()

    # Normalize backslashes to forward slashes
    normalized = normalize_path_string(pattern)

    parts: list[str] = []
    for part in Path(normalized).parts:
        if re.search(r"[*?\[\]]", part):
            break
        parts.append(part)
    return Path(*parts) if parts else Path()


# === apathetic_utils.system ===
# src/serger/utils/utils_system.py


# --- types --------------------------------------------------------------------


@dataclass
class CapturedOutput:
    """Captured stdout, stderr, and merged streams."""

    stdout: StringIO
    stderr: StringIO
    merged: StringIO

    def __str__(self) -> str:
        """Human-friendly representation (merged output)."""
        return self.merged.getvalue()

    def as_dict(self) -> dict[str, str]:
        """Return contents as plain strings for serialization."""
        return {
            "stdout": self.stdout.getvalue(),
            "stderr": self.stderr.getvalue(),
            "merged": self.merged.getvalue(),
        }


# --- system utilities --------------------------------------------------------


def get_sys_version_info() -> tuple[int, int, int] | tuple[int, int, int, str, int]:
    return sys.version_info


def is_running_under_pytest() -> bool:
    """Detect if code is running under pytest.

    Checks multiple indicators:
    - Environment variables set by pytest
    - Command-line arguments containing 'pytest'

    Returns:
        True if running under pytest, False otherwise
    """
    return (
        "pytest" in os.environ.get("_", "")
        or "PYTEST_CURRENT_TEST" in os.environ
        or any(
            "pytest" in arg
            for arg in sys.argv
            if isinstance(arg, str)  # pyright: ignore[reportUnnecessaryIsInstance]
        )
    )


def detect_runtime_mode() -> str:  # noqa: PLR0911
    if getattr(sys, "frozen", False):
        return "frozen"
    if "__main__" in sys.modules and getattr(
        sys.modules["__main__"],
        __file__,
        "",
    ).endswith(".pyz"):
        return "zipapp"
    # Check for standalone mode in multiple locations
    # 1. Current module's globals (for when called from within standalone script)
    if "__STANDALONE__" in globals():
        return "standalone"
    # 2. Check package module's globals (when loaded via importlib)
    # The standalone script is loaded as the "serger" package
    pkg_mod = sys.modules.get("serger")
    if pkg_mod is not None and hasattr(pkg_mod, "__STANDALONE__"):
        return "standalone"
    # 3. Check __main__ module's globals (for script execution)
    if "__main__" in sys.modules:
        main_mod = sys.modules["__main__"]
        if hasattr(main_mod, "__STANDALONE__"):
            return "standalone"
    return "installed"


@contextmanager
def capture_output() -> Iterator[CapturedOutput]:
    """Temporarily capture stdout and stderr.

    Any exception raised inside the block is re-raised with
    the captured output attached as `exc.captured_output`.

    Example:
    from serger.utils import capture_output
    from serger.cli import main

    with capture_output() as cap:
        exit_code = main(["--config", "my.cfg", "--dry-run"])

    result = {
        "exit_code": exit_code,
        "stdout": cap.stdout.getvalue(),
        "stderr": cap.stderr.getvalue(),
        "merged": cap.merged.getvalue(),
    }

    """
    merged = StringIO()

    class TeeStream(StringIO):
        def write(self, s: str) -> int:
            merged.write(s)
            return super().write(s)

    buf_out, buf_err = TeeStream(), TeeStream()
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = buf_out, buf_err

    cap = CapturedOutput(stdout=buf_out, stderr=buf_err, merged=merged)
    try:
        yield cap
    except Exception as e:
        # Attach captured output to the raised exception for API introspection
        e.captured_output = cap  # type: ignore[attr-defined]
        raise
    finally:
        sys.stdout, sys.stderr = old_out, old_err


# === apathetic_utils.matching ===
# src/serger/utils/utils_matching.py


@lru_cache(maxsize=512)
def _compile_glob_recursive(pattern: str) -> re.Pattern[str]:
    """
    Compile a glob pattern to regex, backporting recursive '**' on Python < 3.11.
    This translator handles literals, ?, *, **, and [] classes without relying on
    slicing fnmatch.translate() output, avoiding unbalanced parentheses.
    Always case-sensitive.
    """

    def _escape_lit(ch: str) -> str:
        # Escape regex metacharacters
        if ch in ".^$+{}[]|()\\":
            return "\\" + ch
        return ch

    i = 0
    n = len(pattern)
    pieces: list[str] = []
    while i < n:
        ch = pattern[i]

        # Character class: copy through closing ']'
        if ch == "[":
            j = i + 1
            if j < n and pattern[j] in "!^":
                j += 1
            # allow leading ']' inside class as a literal
            if j < n and pattern[j] == "]":
                j += 1
            while j < n and pattern[j] != "]":
                j += 1
            if j < n and pattern[j] == "]":
                # whole class, keep as-is (regex already)
                pieces.append(pattern[i : j + 1])
                i = j + 1
            else:
                # unmatched '[', treat literally
                pieces.append("\\[")
                i += 1
            continue

        # Recursive glob
        if ch == "*" and i + 1 < n and pattern[i + 1] == "*":
            # Collapse a run of consecutive '*' to detect '**'
            k = i + 2
            while k < n and pattern[k] == "*":
                k += 1
            # Treat any run >= 2 as recursive
            pieces.append(".*")
            i = k
            continue

        # Single-segment glob
        if ch == "*":
            pieces.append("[^/]*")
            i += 1
            continue

        # Single character
        if ch == "?":
            pieces.append("[^/]")
            i += 1
            continue

        # Path separator or literal
        pieces.append(_escape_lit(ch))
        i += 1

    inner = "".join(pieces)
    return re.compile(f"(?s:{inner})\\Z")


def fnmatchcase_portable(path: str, pattern: str) -> bool:
    """
    Case-sensitive glob pattern matching with Python 3.10 '**' backport.

    Uses fnmatchcase (case-sensitive) as the base, with backported support
    for recursive '**' patterns on Python 3.10.

    Args:
        path: The path to match against the pattern
        pattern: The glob pattern to match

    Returns:
        True if the path matches the pattern, False otherwise.
    """
    if get_sys_version_info() >= (3, 11) or "**" not in pattern:
        return fnmatchcase(path, pattern)
    return bool(_compile_glob_recursive(pattern).match(path))


def is_excluded_raw(  # noqa: PLR0911, PLR0912, PLR0915, C901
    path: Path | str,
    exclude_patterns: list[str],
    root: Path | str,
) -> bool:
    """Smart matcher for normalized inputs.

    - Treats 'path' as relative to 'root' unless already absolute.
    - If 'root' is a file, match directly.
    - Handles absolute or relative glob patterns.

    Special behavior for patterns with '../':
    Unlike rsync/ruff (which don't support '../' in exclude patterns),
    serger allows patterns with '../' to explicitly match files outside
    the exclude root. This enables config files in subdirectories to
    exclude files elsewhere in the project. Patterns containing '../'
    are resolved relative to the exclude root, then matched against
    the absolute file path.

    Note:
    The function does not require `root` to exist; if it does not,
    a debug message is logged and matching is purely path-based.
    """
    logger = getLogger()
    root = Path(root).resolve()
    path = Path(path)

    logger.trace(
        f"[is_excluded_raw] Checking path={path} against"
        f" {len(exclude_patterns)} patterns"
    )

    # the callee really should deal with this, otherwise we might spam
    if not Path(root).exists():
        logger.debug("Exclusion root does not exist: %s", root)

    # If the root itself is a file, treat that as a direct exclusion target.
    if root.is_file():
        # If the given path resolves exactly to that file, exclude it.
        full_path = path if path.is_absolute() else (root.parent / path)
        return full_path.resolve() == root.resolve()

    # If no exclude patterns, nothing else to exclude
    if not exclude_patterns:
        return False

    # Otherwise, treat as directory root.
    full_path = path if path.is_absolute() else (root / path)
    full_path = full_path.resolve()

    # Try to get relative path for standard matching
    try:
        rel = str(full_path.relative_to(root)).replace("\\", "/")
        path_outside_root = False
    except ValueError:
        # Path lies outside the root
        path_outside_root = True
        # For patterns starting with **/, we can still match against filename
        # or absolute path. For other patterns, we need rel, so use empty string
        # as fallback (won't match non-**/ patterns)
        rel = ""

    for pattern in exclude_patterns:
        pat = pattern.replace("\\", "/")

        # Handle patterns starting with **/ - these should match even for files
        # outside the exclude root (matching rsync/ruff behavior)
        if pat.startswith("**/"):
            # For **/ patterns, match against:
            # 1. The file's name (e.g., **/__init__.py matches any __init__.py)
            # 2. The absolute path (for more complex patterns with subdirectories)
            file_name = full_path.name
            abs_path_str = str(full_path).replace("\\", "/")

            # Remove **/ prefix and match against filename
            pattern_suffix = pat[3:]  # Remove "**/" prefix
            if fnmatchcase_portable(file_name, pattern_suffix):
                logger.trace(
                    f"[is_excluded_raw] MATCHED **/ pattern {pattern!r} "
                    f"against filename {file_name}"
                )
                return True

            # Also try matching against absolute path, but only if the pattern
            # suffix contains directory separators (for patterns like **/subdir/file.py)
            # If the suffix has no directory separators, we've already checked
            # the filename above, so skip absolute path matching to avoid false
            # positives (e.g., **/test_*.py shouldn't match paths containing "test")
            has_dir_sep = "/" in pattern_suffix or "\\" in pattern_suffix
            if has_dir_sep and fnmatchcase_portable(abs_path_str, pat):
                logger.trace(
                    f"[is_excluded_raw] MATCHED **/ pattern {pattern!r} "
                    f"against absolute path"
                )
                return True

            # Continue to next pattern if we're outside root and **/ didn't match
            if path_outside_root:
                continue

        # Handle patterns with ../ - serger-specific behavior to allow
        # patterns that explicitly navigate outside the exclude root
        if "../" in pat or pat.startswith("../"):
            # Resolve the pattern relative to the exclude root
            # We need to handle glob patterns (with **) by resolving the base
            # path and preserving the glob part
            try:
                abs_path_str = str(full_path).replace("\\", "/")

                # If pattern contains glob chars, split and resolve carefully
                if "*" in pat or "?" in pat or "[" in pat:
                    # Find the first glob character to split base from pattern
                    glob_chars = ["*", "?", "["]
                    first_glob_pos = min(
                        (pat.find(c) for c in glob_chars if c in pat),
                        default=len(pat),
                    )

                    # Split into base path (before glob) and pattern part
                    base_part = pat[:first_glob_pos].rstrip("/")
                    pattern_part = pat[first_glob_pos:]

                    # Resolve the base part relative to root
                    if base_part:
                        resolved_base = (root / base_part).resolve()
                        resolved_pattern_str = (
                            str(resolved_base).replace("\\", "/") + "/" + pattern_part
                        )
                    else:
                        # Pattern starts with glob, resolve root and prepend pattern
                        resolved_pattern_str = (
                            str(root).replace("\\", "/") + "/" + pattern_part
                        )
                else:
                    # No glob chars, resolve normally
                    resolved_pattern = (root / pat).resolve()
                    resolved_pattern_str = str(resolved_pattern).replace("\\", "/")

                # Match the resolved pattern against the absolute file path
                if fnmatchcase_portable(abs_path_str, resolved_pattern_str):
                    logger.trace(
                        f"[is_excluded_raw] MATCHED ../ pattern {pattern!r} "
                        f"(resolved to {resolved_pattern_str})"
                    )
                    return True
            except (ValueError, RuntimeError):
                # Pattern resolves outside filesystem or invalid, skip
                logger.trace(
                    f"[is_excluded_raw] Could not resolve ../ pattern {pattern!r}"
                )

        # If path is outside root and pattern doesn't start with **/ or
        # contain ../, skip
        if path_outside_root:
            continue

        logger.trace(f"[is_excluded_raw] Testing pattern {pattern!r} against {rel}")

        # If pattern is absolute and under root, adjust to relative form
        if pat.startswith(str(root)):
            try:
                pat_rel = str(Path(pat).relative_to(root)).replace("\\", "/")
            except ValueError:
                pat_rel = pat  # not under root; treat as-is
            if fnmatchcase_portable(rel, pat_rel):
                logger.trace(f"[is_excluded_raw] MATCHED pattern {pattern!r}")
                return True

        # Otherwise treat pattern as relative glob
        if fnmatchcase_portable(rel, pat):
            logger.trace(f"[is_excluded_raw] MATCHED pattern {pattern!r}")
            return True

        # Optional directory-only semantics
        if pat.endswith("/") and rel.startswith(pat.rstrip("/") + "/"):
            logger.trace(f"[is_excluded_raw] MATCHED pattern {pattern!r}")
            return True

    return False


# === apathetic_utils.text ===
# src/serger/utils/utils_text.py


def plural(obj: Any) -> str:
    """Return 's' if obj represents a plural count.

    Accepts ints, floats, and any object implementing __len__().
    Returns '' for singular or zero.
    """
    count: int | float
    try:
        count = len(obj)
    except TypeError:
        # fallback for numbers or uncountable types
        count = obj if isinstance(obj, (int, float)) else 0
    return "s" if count != 1 else ""


def remove_path_in_error_message(inner_msg: str, path: Path) -> str:
    """Remove redundant file path mentions (and nearby filler)
    from error messages.

    Useful when wrapping a lower-level exception that already
    embeds its own file reference, so the higher-level message
    can use its own path without duplication.

    Example:
        "Invalid JSONC syntax in /abs/path/config.jsonc: Expecting value"
        → "Invalid JSONC syntax: Expecting value"

    """
    # Normalize both path and name for flexible matching
    full_path = str(path)
    filename = path.name

    # Common redundant phrases we might need to remove
    candidates = [
        f"in {full_path}",
        f"in '{full_path}'",
        f'in "{full_path}"',
        f"in {filename}",
        f"in '{filename}'",
        f'in "{filename}"',
        full_path,
        filename,
    ]

    clean_msg = inner_msg
    for pattern in candidates:
        clean_msg = clean_msg.replace(pattern, "").strip(": ").strip()

    # Normalize leftover spaces and colons
    clean_msg = re.sub(r"\s{2,}", " ", clean_msg)
    clean_msg = re.sub(r"\s*:\s*", ": ", clean_msg)

    return clean_msg


# === apathetic_utils.types ===
# src/serger/utils/utils_types.py


T = TypeVar("T")


def cast_hint(typ: type[T], value: Any) -> T:  # noqa: ARG001
    """Explicit cast that documents intent but is purely for type hinting.

    A drop-in replacement for `typing.cast`, meant for places where:
      - You want to silence mypy's redundant-cast warnings.
      - You want to signal "this narrowing is intentional."
      - You need IDEs (like Pylance) to retain strong inference on a value.

    Does not handle Union, Optional, or nested generics: stick to cast(),
      because unions almost always represent a meaningful type narrowing.

    This function performs *no runtime checks*.
    """
    return cast("T", value)


def schema_from_typeddict(td: type[Any]) -> dict[str, Any]:
    """Extract field names and their annotated types from a TypedDict."""
    return get_type_hints(td, include_extras=True)


def literal_to_set(literal_type: Any) -> set[Any]:
    """Extract values from a Literal type as a set.

    Example:
        StitchMode = Literal["raw", "package"]
        valid_modes = literal_to_set(StitchMode)  # Returns set with literal values

    Args:
        literal_type: A Literal type (e.g., Literal["a", "b"])

    Returns:
        A set containing all values from the Literal type.
        Returns set[Any] to allow flexible operations without requiring
        casts. The actual values are constrained by the Literal type at
        runtime validation.

    Type Safety Tradeoffs:
        This function returns set[Any] after considering three approaches:

        1. set[Any] (current): Allows flexible operations (e.g., sorted(),
           membership checks) without requiring casts. Less type-safe but
           more ergonomic for common use cases.

        2. set[str | int | float | bool | None]: More type-safe, but requires
           casts for operations like sorted() that expect specific types,
           creating noise and potential for errors.

        3. TypeVar (like cast_hint): Would provide perfect type inference,
           but Python's type system cannot extract the union of literal
           values from a Literal type at the type level.

        The current approach prioritizes ergonomics while still providing
        runtime validation that the input is a Literal type.

    Raises:
        TypeError: If the input is not a Literal type
    """
    origin = get_origin(literal_type)
    if origin is not Literal:
        msg = f"Expected Literal type, got {literal_type}"
        raise TypeError(msg)
    return set(get_args(literal_type))


def _isinstance_generics(  # noqa: PLR0911
    value: Any,
    origin: Any,
    args: tuple[Any, ...],
) -> bool:
    # Outer container check
    if not isinstance(value, origin):
        return False

    # Recursively check elements for known homogeneous containers
    if not args:
        return True

    # list[str]
    if origin is list and isinstance(value, list):
        subtype = args[0]
        items = cast_hint(list[Any], value)
        return all(safe_isinstance(v, subtype) for v in items)

    # dict[str, int]
    if origin is dict and isinstance(value, dict):
        key_t, val_t = args if len(args) == 2 else (Any, Any)  # noqa: PLR2004
        dct = cast_hint(dict[Any, Any], value)
        return all(
            safe_isinstance(k, key_t) and safe_isinstance(v, val_t)
            for k, v in dct.items()
        )

    # Tuple[str, int] etc.
    if origin is tuple and isinstance(value, tuple):
        subtypes = args
        tup = cast_hint(tuple[Any, ...], value)
        if len(subtypes) == len(tup):
            return all(
                safe_isinstance(v, t) for v, t in zip(tup, subtypes, strict=False)
            )
        if len(subtypes) == 2 and subtypes[1] is Ellipsis:  # noqa: PLR2004
            return all(safe_isinstance(v, subtypes[0]) for v in tup)
        return False

    return True  # e.g., other typing origins like set[], Iterable[]


def safe_isinstance(value: Any, expected_type: Any) -> bool:  # noqa: PLR0911
    """Like isinstance(), but safe for TypedDicts and typing generics.

    Handles:
      - typing.Union, Optional, Any
      - typing.NotRequired
      - TypedDict subclasses
      - list[...] with inner types
      - Defensive fallback for exotic typing constructs
    """
    # --- Always allow Any ---
    if expected_type is Any:
        return True

    origin = get_origin(expected_type)
    args = get_args(expected_type)

    # --- Handle NotRequired (extract inner type) ---
    if origin is NotRequired:
        # NotRequired[str] → validate as str
        if args:
            return safe_isinstance(value, args[0])
        return True

    # --- Handle Literals explicitly ---
    if origin is Literal:
        # Literal["x", "y"] → True if value equals any of the allowed literals
        return value in args

    # --- Handle Unions (includes Optional) ---
    if origin in {Union, UnionType}:
        # e.g. Union[str, int]
        return any(safe_isinstance(value, t) for t in args)

    # --- Handle special case: TypedDicts ---
    try:
        if (
            isinstance(expected_type, type)
            and hasattr(expected_type, "__annotations__")
            and hasattr(expected_type, "__total__")
        ):
            # Treat TypedDict-like as dict
            return isinstance(value, dict)
    except TypeError:
        # Not a class — skip
        pass

    # --- Handle generics like list[str], dict[str, int] ---
    if origin:
        return _isinstance_generics(value, origin, args)

    # --- Fallback for simple types ---
    try:
        return isinstance(value, expected_type)
    except TypeError:
        # Non-type or strange typing construct
        return False


# === apathetic_utils.__init__ ===
"""Apathetic utilities package."""


__all__ = [  # noqa: RUF022
    # ci
    "CI_ENV_VARS",
    "is_ci",
    # files
    "load_jsonc",
    "load_toml",
    # matching
    "fnmatchcase_portable",
    "is_excluded_raw",
    # paths
    "get_glob_root",
    "has_glob_chars",
    "normalize_path_string",
    # system
    "CapturedOutput",
    "capture_output",
    "detect_runtime_mode",
    "get_sys_version_info",
    "is_running_under_pytest",
    # text
    "plural",
    "remove_path_in_error_message",
    # types
    "cast_hint",
    "literal_to_set",
    "safe_isinstance",
    "schema_from_typeddict",
]


# === apathetic_schema.schema ===
# src/serger/utils/utils_schema.py


# --- constants ----------------------------------------------------------


DEFAULT_HINT_CUTOFF: float = 0.75


# --- types ----------------------------------------------------------


class _SchErrAggEntry(TypedDict):
    msg: str
    contexts: list[str]


"""
severity, tag

Aggregator structure example:
{
  "strict_warnings": {
      "dry-run": {"msg": DRYRUN_MSG, "contexts": ["in build #0", "in build #2"]},
      ...
  },
  "warnings": { ... }
}
"""
SchemaErrorAggregator = dict[str, dict[str, dict[str, _SchErrAggEntry]]]


# --- dataclasses ------------------------------------------------------


@dataclass
class ValidationSummary:
    valid: bool
    errors: list[str]
    strict_warnings: list[str]
    warnings: list[str]
    strict: bool  # strictness somewhere in our config?


# --- constants ------------------------------------------------------

AGG_STRICT_WARN = "strict_warnings"
AGG_WARN = "warnings"

# --- helpers --------------------------------------------------------


def collect_msg(
    msg: str,
    *,
    strict: bool,
    summary: ValidationSummary,  # modified in function, not returned
    is_error: bool = False,
) -> None:
    """Route a message to the appropriate bucket.
    Errors are always fatal.
    Warnings may escalate to strict_warnings in strict mode.
    """
    if is_error:
        summary.errors.append(msg)
    elif strict:
        summary.strict_warnings.append(msg)
    else:
        summary.warnings.append(msg)


def flush_schema_aggregators(
    *,
    summary: ValidationSummary,
    agg: SchemaErrorAggregator,
) -> None:
    def _clean_context(ctx: str) -> str:
        """Normalize context strings by removing leading 'in' or 'on'."""
        ctx = ctx.strip()
        for prefix in ("in ", "on "):
            if ctx.lower().startswith(prefix):
                return ctx[len(prefix) :].strip()
        return ctx

    def _flush_one(
        bucket: dict[str, dict[str, Any]],
        *,
        strict: bool,
    ) -> None:
        for tag, entry in bucket.items():
            msg_tmpl = entry["msg"]
            contexts = [_clean_context(c) for c in entry["contexts"]]
            joined_ctx = ", ".join(contexts)
            rendered = msg_tmpl.format(keys=tag, ctx=f"in {joined_ctx}")
            collect_msg(rendered, strict=strict, summary=summary)
        bucket.clear()

    strict_bucket = agg.get(AGG_STRICT_WARN, {})
    warn_bucket = agg.get(AGG_WARN, {})

    if strict_bucket:
        summary.valid = False
        _flush_one(strict_bucket, strict=True)
    if warn_bucket:
        _flush_one(warn_bucket, strict=False)


# ---------------------------------------------------------------------------
# granular schema validator helpers (private and testable)
# ---------------------------------------------------------------------------


def _get_example_for_field(
    field_path: str,
    field_examples: dict[str, str] | None = None,
) -> str | None:
    """Get example for field if available in field_examples.

    Args:
        field_path: The full field path
            (e.g. "root.include" or "root.watch_interval")
        field_examples: Optional dict mapping field patterns to example values.
        If None, returns None (no examples available).
    """
    if field_examples is None:
        return None

    # First, try exact match (O(1) lookup)
    if field_path in field_examples:
        return field_examples[field_path]

    # Then try wildcard matches
    for pattern, example in field_examples.items():
        if "*" in pattern and fnmatchcase_portable(field_path, pattern):
            return example

    return None


def _infer_type_label(
    expected_type: Any,
) -> str:
    """Return a readable label for logging (e.g. 'list[str]', 'BuildConfig')."""
    try:
        origin = get_origin(expected_type)
        args = get_args(expected_type)

        # Unwrap NotRequired to get the actual type
        if origin is NotRequired and args:
            return _infer_type_label(args[0])

        if origin is list and args:
            return f"list[{getattr(args[0], '__name__', repr(args[0]))}]"
        if isinstance(expected_type, type):
            return expected_type.__name__
        return str(expected_type)
    except Exception:  # noqa: BLE001
        return repr(expected_type)


def _validate_scalar_value(
    context: str,
    key: str,
    val: Any,
    expected_type: Any,
    *,
    strict: bool,
    summary: ValidationSummary,  # modified in function, not returned
    field_path: str,
    field_examples: dict[str, str] | None = None,
) -> bool:
    """Validate a single non-container value against its expected type."""
    try:
        if safe_isinstance(val, expected_type):  # self-ref guard
            return True
    except Exception:  # noqa: BLE001
        # Defensive fallback — e.g. weird typing generics
        fallback_type = (
            expected_type if isinstance(expected_type, type) else type(expected_type)
        )
        if isinstance(val, fallback_type):
            return True

    exp_label = _infer_type_label(expected_type)
    example = _get_example_for_field(field_path, field_examples)
    exmsg = ""
    if example:
        exmsg = f" (e.g. {example})"

    msg = (
        f"{context}: key `{key}` expected {exp_label}{exmsg}, got {type(val).__name__}"
    )
    collect_msg(msg, summary=summary, strict=strict, is_error=True)
    return False


def _validate_list_value(
    context: str,
    key: str,
    val: Any,
    subtype: Any,
    *,
    strict: bool,
    summary: ValidationSummary,  # modified in function, not returned
    prewarn: set[str],
    field_path: str,
    field_examples: dict[str, str] | None = None,
) -> bool:
    """Validate a homogeneous list value, delegating to scalar/TypedDict validators."""
    if not isinstance(val, list):
        exp_label = f"list[{_infer_type_label(subtype)}]"
        example = _get_example_for_field(field_path, field_examples)
        exmsg = ""
        if example:
            exmsg = f" (e.g. {example})"
        msg = (
            f"{context}: key `{key}` expected {exp_label}{exmsg},"
            f" got {type(val).__name__}"
        )
        collect_msg(
            msg,
            strict=strict,
            summary=summary,
            is_error=True,
        )
        return False

    # Treat val as a real list for static type checkers
    items = cast_hint(list[Any], val)

    # Empty list → fine, nothing to check
    if not items:
        return True

    valid = True
    for i, item in enumerate(items):
        # Detect TypedDict-like subtypes
        if (
            isinstance(subtype, type)
            and hasattr(subtype, "__annotations__")
            and hasattr(subtype, "__total__")
        ):
            if not isinstance(item, dict):
                collect_msg(
                    f"{context}: key `{key}` #{i + 1} expected an "
                    " object with named keys for "
                    f"{subtype.__name__}, got {type(item).__name__}",
                    strict=strict,
                    summary=summary,
                    is_error=True,
                )
                valid = False
                continue
            valid &= _validate_typed_dict(
                f"{context}.{key}[{i}]",
                item,
                subtype,
                strict=strict,
                summary=summary,
                prewarn=prewarn,
                field_path=f"{field_path}[{i}]",
                field_examples=field_examples,
            )
        else:
            valid &= _validate_scalar_value(
                context,
                f"{key}[{i}]",
                item,
                subtype,
                strict=strict,
                summary=summary,
                field_path=f"{field_path}[{i}]",
                field_examples=field_examples,
            )
    return valid


def _dict_unknown_keys(
    context: str,
    val: Any,
    schema: dict[str, Any],
    *,
    strict: bool,
    summary: ValidationSummary,  # modified in function, not returned
    prewarn: set[str],
) -> bool:
    # --- Unknown keys ---
    val_dict = cast("dict[str, Any]", val)
    unknown: list[str] = [k for k in val_dict if k not in schema and k not in prewarn]
    if unknown:
        joined = ", ".join(f"`{u}`" for u in unknown)

        location = context
        if "in top-level configuration." in location:
            location = "in " + location.split("in top-level configuration.")[-1]

        msg = f"Unknown key{plural(unknown)} {joined} {location}."

        hints: list[str] = []
        for k in unknown:
            close = get_close_matches(k, schema.keys(), n=1, cutoff=DEFAULT_HINT_CUTOFF)
            if close:
                hints.append(f"'{k}' → '{close[0]}'")
        if hints:
            msg += "\nHint: did you mean " + ", ".join(hints) + "?"

        collect_msg(msg.strip(), strict=strict, summary=summary)
        if strict:
            return False

    return True


def _dict_fields(
    context: str,
    val: Any,
    schema: dict[str, Any],
    *,
    strict: bool,
    summary: ValidationSummary,  # modified in function, not returned
    prewarn: set[str],
    ignore_keys: set[str],
    field_path: str,
    field_examples: dict[str, str] | None = None,
) -> bool:
    valid = True

    for field, expected_type in schema.items():
        if field not in val or field in prewarn or field in ignore_keys:
            # Optional or missing field → not a failure
            continue

        inner_val = val[field]
        origin = get_origin(expected_type)
        args = get_args(expected_type)
        exp_label = _infer_type_label(expected_type)
        current_field_path = f"{field_path}.{field}" if field_path else field

        if origin is list:
            subtype = args[0] if args else Any
            valid &= _validate_list_value(
                context,
                field,
                inner_val,
                subtype,
                strict=strict,
                summary=summary,
                prewarn=prewarn,
                field_path=current_field_path,
                field_examples=field_examples,
            )
        elif (
            isinstance(expected_type, type)
            and hasattr(expected_type, "__annotations__")
            and hasattr(expected_type, "__total__")
        ):
            # we don't pass ignore_keys down because
            # we don't recursively ignore these keys
            # and they have no depth syntax. Instead you
            # need to ignore the current level, then take ownership
            # and only validate what you want manually. calling validation
            # on anything that you aren't ignoring downstream.
            # rare case that is a lot of work, but keeps the rest
            # simple for now.
            if "in top-level configuration." in context:
                location = field
            else:
                location = f"{context}.{field}"
            valid &= _validate_typed_dict(
                location,
                inner_val,
                expected_type,
                strict=strict,
                summary=summary,
                prewarn=prewarn,
                field_path=current_field_path,
                field_examples=field_examples,
            )
        else:
            val_scalar = _validate_scalar_value(
                context,
                field,
                inner_val,
                expected_type,
                strict=strict,
                summary=summary,
                field_path=current_field_path,
                field_examples=field_examples,
            )
            if not val_scalar:
                collect_msg(
                    f"{context}: key `{field}` expected {exp_label}, "
                    f"got {type(inner_val).__name__}",
                    strict=strict,
                    summary=summary,
                    is_error=True,
                )
                valid = False

    return valid


def _validate_typed_dict(
    context: str,
    val: Any,
    typedict_cls: type[Any],
    *,
    strict: bool,
    summary: ValidationSummary,  # modified in function, not returned
    prewarn: set[str],
    ignore_keys: set[str] | None = None,
    field_path: str = "",
    field_examples: dict[str, str] | None = None,
) -> bool:
    """Validate a dict against a TypedDict schema recursively.

    - Return False if val is not a dict
    - Recurse into its fields using _validate_scalar_value or _validate_list_value
    - Warn about unknown keys under strict=True
    """
    if ignore_keys is None:
        ignore_keys = set()

    if not isinstance(val, dict):
        collect_msg(
            f"{context}: expected an object with named keys for"
            f" {typedict_cls.__name__}, got {type(val).__name__}",
            strict=strict,
            summary=summary,
            is_error=True,
        )
        return False

    if not hasattr(typedict_cls, "__annotations__"):
        xmsg = (
            "Internal schema invariant violated: "
            f"{typedict_cls!r} has no __annotations__."
        )
        raise AssertionError(xmsg)

    schema = schema_from_typeddict(typedict_cls)
    valid = True

    # --- walk through all the fields recursively ---
    if not _dict_fields(
        context,
        val,
        schema,
        strict=strict,
        summary=summary,
        prewarn=prewarn,
        ignore_keys=ignore_keys,
        field_path=field_path,
        field_examples=field_examples,
    ):
        valid = False

    # --- Unknown keys ---
    if not _dict_unknown_keys(
        context,
        val,
        schema,
        strict=strict,
        summary=summary,
        prewarn=prewarn,
    ):
        valid = False

    return valid


# ---------------------------------------------------------------------------
# granular schema validator
# ---------------------------------------------------------------------------


# --- warn_keys_once -------------------------------------------


def warn_keys_once(
    tag: str,
    bad_keys: set[str],
    cfg: dict[str, Any],
    context: str,
    msg: str,
    *,
    strict_config: bool,
    summary: ValidationSummary,  # modified in function, not returned
    agg: SchemaErrorAggregator | None,
) -> tuple[bool, set[str]]:
    """Warn once for known bad keys (e.g. dry-run, root-only).

    agg indexes are: severity, tag, msg, context (list[str])

    Returns (valid, found_keys).
    """
    valid = True

    # Normalize keys to lowercase for case-insensitive matching
    bad_keys_lower = {k.lower(): k for k in bad_keys}
    cfg_keys_lower = {k.lower(): k for k in cfg}
    found_lower = bad_keys_lower & cfg_keys_lower.keys()

    if not found_lower:
        return True, set()

    # Recover original-case keys for display
    found = {cfg_keys_lower[k] for k in found_lower}

    if agg is not None:
        # record context for later aggregation
        severity = AGG_STRICT_WARN if strict_config else AGG_WARN
        bucket = cast_hint(dict[str, _SchErrAggEntry], agg.setdefault(severity, {}))

        default_entry: _SchErrAggEntry = {"msg": msg, "contexts": []}
        entry = bucket.setdefault(tag, default_entry)
        entry["contexts"].append(context)
    else:
        # immediate fallback
        collect_msg(
            f"{msg.format(keys=', '.join(sorted(found)), ctx=context)}",
            strict=strict_config,
            summary=summary,
        )

    if strict_config:
        valid = False

    return valid, found


# --- check_schema_conformance --------------------


def check_schema_conformance(
    cfg: dict[str, Any],
    schema: dict[str, Any],
    context: str,
    *,
    strict_config: bool,
    summary: ValidationSummary,  # modified in function, not returned
    prewarn: set[str] | None = None,
    ignore_keys: set[str] | None = None,
    base_path: str = "root",
    field_examples: dict[str, str] | None = None,
) -> bool:
    """Thin wrapper around _validate_typed_dict for root-level schema checks."""
    if prewarn is None:
        prewarn = set()
    if ignore_keys is None:
        ignore_keys = set()

    # Pretend schema is a TypedDict for uniformity
    class _AnonTypedDict(TypedDict):
        pass

    # Attach the schema dynamically to mimic schema_from_typeddict output
    _AnonTypedDict.__annotations__ = schema

    return _validate_typed_dict(
        context,
        cfg,
        _AnonTypedDict,
        strict=strict_config,
        summary=summary,
        prewarn=prewarn,
        ignore_keys=ignore_keys,
        field_path=base_path,
        field_examples=field_examples,
    )


# === apathetic_schema.__init__ ===
"""Apathetic schema package."""


__all__ = [
    # schema
    "SchemaErrorAggregator",
    "ValidationSummary",
    "check_schema_conformance",
    "collect_msg",
    "flush_schema_aggregators",
    "warn_keys_once",
]


# === serger.config.config_types ===
# src/serger/config/config_types.py


OriginType = Literal["cli", "config", "plugin", "default", "code", "gitignore", "test"]


InternalImportMode = Literal["force_strip", "strip", "keep", "assign"]
ExternalImportMode = Literal["force_top", "top", "keep", "force_strip", "strip"]
StitchMode = Literal["raw", "class", "exec"]
ModuleMode = Literal[
    "none", "multi", "force", "force_flat", "unify", "unify_preserve", "flat"
]
ShimSetting = Literal["all", "public", "none"]
MainMode = Literal["none", "auto"]
# Module actions configuration types
ModuleActionType = Literal["move", "copy", "delete", "rename", "none"]
ModuleActionMode = Literal["preserve", "flatten"]
ModuleActionScope = Literal["original", "shim"]
ModuleActionAffects = Literal["shims", "stitching", "both"]
ModuleActionCleanup = Literal["auto", "error", "ignore"]


class ModuleActionFull(TypedDict, total=False):
    source: str  # required
    source_path: NotRequired[str]  # optional filesystem path
    dest: NotRequired[str]  # required for move/copy
    action: NotRequired[ModuleActionType]  # default: "move"
    mode: NotRequired[ModuleActionMode]  # default: "preserve"
    # default: "shim" for user, "original" for mode-generated
    scope: NotRequired[ModuleActionScope]
    affects: NotRequired[ModuleActionAffects]  # default: "shims"
    cleanup: NotRequired[ModuleActionCleanup]  # default: "auto"


# Simple format: dict[str, str | None]
ModuleActionSimple = dict[str, str | None]

# Union type for config
ModuleActions = ModuleActionSimple | list[ModuleActionFull]

CommentsMode = Literal["keep", "ignores", "inline", "strip"]
# DocstringMode can be a simple string mode or a dict for per-location control
DocstringModeSimple = Literal["keep", "strip", "public"]
DocstringModeLocation = Literal["module", "class", "function", "method"]
DocstringMode = DocstringModeSimple | dict[DocstringModeLocation, DocstringModeSimple]


# Post-processing configuration types
class ToolConfig(TypedDict, total=False):
    command: str  # executable name (optional - defaults to key if missing)
    args: list[str]  # command arguments (optional, replaces defaults)
    path: str  # custom executable path
    options: list[str]  # additional CLI arguments (appends to args)


class PostCategoryConfig(TypedDict, total=False):
    enabled: bool  # default: True
    priority: list[str]  # tool names in priority order
    tools: NotRequired[dict[str, ToolConfig]]  # per-tool overrides


class PostProcessingConfig(TypedDict, total=False):
    enabled: bool  # master switch, default: True
    category_order: list[str]  # order to run categories
    categories: NotRequired[dict[str, PostCategoryConfig]]  # category definitions


# Resolved types - all fields are guaranteed to be present with final values
class ToolConfigResolved(TypedDict):
    command: str  # executable name (defaults to tool_label if not specified)
    args: list[str]  # command arguments (always present)
    path: str | None  # custom executable path (None if not specified)
    options: list[str]  # additional CLI arguments (empty list if not specified)


class PostCategoryConfigResolved(TypedDict):
    enabled: bool  # always present
    priority: list[str]  # always present (may be empty)
    tools: dict[str, ToolConfigResolved]  # always present (may be empty dict)


class PostProcessingConfigResolved(TypedDict):
    enabled: bool
    category_order: list[str]
    categories: dict[str, PostCategoryConfigResolved]


class PathResolved(TypedDict):
    path: Path | str  # absolute or relative to `root`, or a pattern
    root: Path  # canonical origin directory for resolution
    pattern: NotRequired[str]  # the original pattern matching this path

    # meta only
    origin: OriginType  # provenance


class IncludeResolved(PathResolved):
    dest: NotRequired[Path]  # optional override for target name


class MetaBuildConfigResolved(TypedDict):
    # sources of parameters
    cli_root: Path
    config_root: Path


class IncludeConfig(TypedDict):
    path: str
    dest: NotRequired[str]


class RootConfig(TypedDict, total=False):
    include: list[str | IncludeConfig]
    exclude: list[str]

    # Optional per-build overrides
    strict_config: bool
    out: str
    respect_gitignore: bool
    log_level: str

    # Runtime behavior
    watch_interval: float
    post_processing: PostProcessingConfig  # Post-processing configuration

    # Pyproject.toml integration
    use_pyproject_metadata: bool  # Whether to pull metadata from pyproject.toml
    pyproject_path: str  # Path to pyproject.toml (overrides root default)

    # Version (overrides pyproject version)
    version: str  # Version string (optional, falls back to pyproject.toml if not set)

    # Stitching configuration
    package: str  # Package name for imports (e.g., "serger")
    # Explicit module order for stitching (optional; auto-discovered if not provided)
    order: list[str]
    # License text or dict with file/text/expression
    license: str | dict[str, str | list[str]]
    license_files: list[str]  # Additional license files (glob patterns)
    display_name: str  # Display name for header (defaults to package)
    description: str  # Description for header (defaults to blank)
    authors: str  # Authors for header (optional, can fallback to pyproject.toml)
    repo: str  # Repository URL for header (optional)
    custom_header: str  # Custom header text (overrides display_name/description)
    file_docstring: str  # Custom file docstring (overrides auto-generated docstring)
    # Import handling configuration
    internal_imports: InternalImportMode  # How to handle internal package imports
    external_imports: ExternalImportMode  # How to handle external imports
    # Stitching mode: how to combine modules into a single file
    # - "raw": Concatenate all files together (default)
    # - "class": Namespace files within classes (not yet implemented)
    # - "exec": Namespace files within module shims using exec() (not yet implemented)
    stitch_mode: StitchMode
    # Module mode: how to generate import shims for single-file runtime
    # - "none": No shims generated
    # - "multi": Generate shims for all detected packages (default)
    # - "force": Replace root package but keep subpackages (e.g., pkg1.sub -> mypkg.sub)
    # - "force_flat": Flatten everything to configured package (e.g., pkg1.sub -> mypkg)
    # - "unify": Place all detected packages under package, combine if package matches
    # - "unify_preserve": Like unify but preserves structure when package matches
    # - "flat": Treat loose files as top-level modules (not under package)
    module_mode: ModuleMode
    # Shim setting: controls whether shims are generated and which modules get shims
    # - "all": Generate shims for all modules (default)
    # - "public": Only generate shims for public modules
    #   (future: based on _ prefix or __all__)
    # - "none": Don't generate shims at all
    shim: ShimSetting
    # Module actions: custom module transformations (move, copy, delete)
    # - dict[str, str | None]: Simple format mapping source -> dest
    # - list[ModuleActionFull]: Full format with detailed options
    module_actions: NotRequired[ModuleActions]
    # Comments mode: how to handle comments in stitched output
    # - "keep": Keep all comments (default)
    # - "ignores": Only keep comments that specify ignore rules
    #   (e.g., "noqa:", "type: ignore")
    # - "inline": Only keep inline comments (comments on the same line as code)
    # - "strip": Remove all comments
    comments_mode: CommentsMode
    # Docstring mode: how to handle docstrings in stitched output
    # - "keep": Keep all docstrings (default)
    # - "strip": Remove all docstrings
    # - "public": Keep only public docstrings (not prefixed with underscore)
    # - dict: Per-location control, e.g., {"module": "keep", "class": "strip"}
    #   Valid locations: "module", "class", "function", "method"
    #   Each location value can be "keep", "strip", or "public"
    #   Omitted locations default to "keep"
    docstring_mode: DocstringMode
    # Source bases: ordered list of directories where packages can be found
    # - str: Single directory (convenience, converted to list[str] on resolve)
    # - list[str]: Ordered list of directories (default: ["src", "lib", "packages"])
    source_bases: str | list[str]
    # Installed packages bases: ordered list of directories where installed packages
    # can be found (for "follow the imports" stitching)
    # - str: Single directory (convenience, converted to list[str] on resolve)
    # - list[str]: Ordered list of directories (default: auto-discovered if enabled)
    installed_bases: NotRequired[str | list[str]]
    # Auto-discover installed packages: whether to automatically discover
    # installed package roots (default: True)
    auto_discover_installed_packages: NotRequired[bool]
    # Include installed dependencies: whether to include installed dependencies
    # in "follow the imports" stitching (default: False)
    include_installed_dependencies: NotRequired[bool]
    # Main function configuration
    # - "none": Don't generate __main__ block
    # - "auto": Automatically detect and generate __main__ block (default)
    main_mode: NotRequired[MainMode]
    # Main function name specification
    # - None: Auto-detect main function (default)
    # - str: Explicit main function specification (see docs for syntax)
    main_name: NotRequired[str | None]
    # Build timestamp control
    # - False: Use real timestamps (default)
    # - True: Use placeholder for deterministic builds
    disable_build_timestamp: NotRequired[bool]


class RootConfigResolved(TypedDict):
    include: list[IncludeResolved]
    exclude: list[PathResolved]

    # Optional per-build overrides
    strict_config: bool
    out: PathResolved
    respect_gitignore: bool
    log_level: str

    # Runtime behavior
    watch_interval: float

    # Runtime flags (CLI only, not persisted in normal configs)
    dry_run: bool
    validate_config: bool

    # Global provenance (optional, for audit/debug)
    __meta__: MetaBuildConfigResolved

    # Internal metadata fields (not user-configurable)
    version: NotRequired[str]  # Version (user -> pyproject, resolved in config)

    # Stitching fields (optional - present if this is a stitch build)
    package: NotRequired[str]
    order: NotRequired[list[str]]
    # Metadata fields (optional, resolved to user -> pyproject -> None)
    license: str  # License text (mandatory, always present with fallback)
    display_name: NotRequired[str]
    description: NotRequired[str]
    authors: NotRequired[str]
    repo: NotRequired[str]
    custom_header: NotRequired[str]  # Custom header (overrides display_name)
    file_docstring: NotRequired[str]  # Custom docstring (overrides auto-generated)
    post_processing: PostProcessingConfigResolved  # Post-processing configuration
    internal_imports: InternalImportMode  # How to handle internal imports
    external_imports: ExternalImportMode  # How to handle external imports
    stitch_mode: StitchMode  # How to combine modules into a single file
    module_mode: ModuleMode  # How to generate import shims for single-file runtime
    shim: ShimSetting  # Controls shim generation and which modules get shims
    # Module transformations (normalized to list format, always present)
    module_actions: list[ModuleActionFull]
    comments_mode: CommentsMode  # How to handle comments in stitched output
    docstring_mode: DocstringMode  # How to handle docstrings in stitched output
    # Source bases: ordered list of directories where packages can be found
    # (always present, resolved to list[str])
    source_bases: list[str]
    # Installed packages bases: ordered list of directories where installed packages
    # can be found (always present, resolved to list[str])
    installed_bases: list[str]
    # Auto-discover installed packages (always present, resolved with defaults)
    auto_discover_installed_packages: bool
    # Include installed dependencies (always present, resolved with defaults)
    include_installed_dependencies: bool
    # Main function configuration (always present, resolved with defaults)
    main_mode: MainMode
    # Main function name specification (always present, resolved with defaults)
    main_name: str | None
    # Build timestamp control (always present, resolved with defaults)
    disable_build_timestamp: bool


# === serger.constants ===
# src/serger/constants.py
"""Central constants used across the project."""


RUNTIME_MODES = {
    "standalone",  # single stitched file
    "installed",  # poetry-installed / pip-installed / importable
    "zipapp",  # .pyz bundle
}

# --- env keys ---
DEFAULT_ENV_LOG_LEVEL: str = "LOG_LEVEL"
DEFAULT_ENV_RESPECT_GITIGNORE: str = "RESPECT_GITIGNORE"
DEFAULT_ENV_WATCH_INTERVAL: str = "WATCH_INTERVAL"
DEFAULT_ENV_DISABLE_BUILD_TIMESTAMP: str = "DISABLE_BUILD_TIMESTAMP"

# --- program defaults ---
DEFAULT_LOG_LEVEL: str = "info"
DEFAULT_WATCH_INTERVAL: float = 1.0  # seconds
DEFAULT_RESPECT_GITIGNORE: bool = True

# --- config defaults ---
DEFAULT_STRICT_CONFIG: bool = True
DEFAULT_OUT_DIR: str = "dist"
DEFAULT_DRY_RUN: bool = False
DEFAULT_USE_PYPROJECT_METADATA: bool = True

# Import handling defaults keyed by stitch mode
# These defaults are chosen based on how each stitching mode works:

# INTERNAL_IMPORTS:
#   - "raw": "force_strip" - Raw mode concatenates all files into a single namespace.
#     Internal imports (e.g., "from .utils import helper") are stripped because all
#     code is in the same namespace and can reference each other directly.
#   - "class": "assign" - Class mode wraps each module in a class namespace.
#     Internal imports must be transformed to class attribute access (e.g.,
#     "from .utils import helper" becomes "helper = _Module_utils.helper").
#     The "assign" mode handles this transformation automatically.
#   - "exec": "keep" - Exec mode uses exec() with separate module objects in
#     sys.modules, each with proper __package__ attributes. Relative imports work
#     correctly in this setup, so they should be kept as-is.
DEFAULT_INTERNAL_IMPORTS: dict[str, str] = {
    "raw": "force_strip",
    "class": "assign",
    "exec": "keep",
}

# EXTERNAL_IMPORTS:
#   - All modes use "top" - External imports (e.g., "import os", "from pathlib
#     import Path") must be available at module level for all stitching modes.
#     Hoisting them to the top ensures they're accessible throughout the stitched
#     file, whether code is concatenated (raw), wrapped in classes (class), or
#     executed in separate namespaces (exec).
DEFAULT_EXTERNAL_IMPORTS: dict[str, str] = {
    "raw": "top",
    "class": "top",
    "exec": "top",
}
DEFAULT_STITCH_MODE: str = "raw"  # Raw concatenation (default stitching mode)
DEFAULT_MODULE_MODE: str = "multi"  # Generate shims for all detected packages
DEFAULT_SHIM: str = "all"  # Generate shims for all modules (default shim setting)
DEFAULT_COMMENTS_MODE: str = "keep"  # Keep all comments (default comments mode)
DEFAULT_DOCSTRING_MODE: str = "keep"  # Keep all docstrings (default docstring mode)
DEFAULT_SOURCE_BASES: list[str] = [
    "src",
    "lib",
    "packages",
]  # Default directories to search for packages
DEFAULT_MAIN_MODE: str = "auto"  # Automatically detect and generate __main__ block
DEFAULT_MAIN_NAME: str | None = None  # Auto-detect main function (default)
DEFAULT_DISABLE_BUILD_TIMESTAMP: bool = False  # Use real timestamps by default
BUILD_TIMESTAMP_PLACEHOLDER: str = "<build-timestamp>"  # Placeholder
DEFAULT_LICENSE_FALLBACK: str = (
    "All rights reserved. See additional license files if distributed "
    "alongside this file for additional terms."
)

# --- post-processing defaults ---
DEFAULT_CATEGORY_ORDER: list[str] = ["static_checker", "formatter", "import_sorter"]

# Type: dict[str, dict[str, Any]] - matches PostCategoryConfig structure
# All tool commands are defined in tools dict for consistency (supports custom labels)
# Note: This is the raw default structure; it gets resolved to
# PostCategoryConfigResolved
DEFAULT_CATEGORIES: dict[str, dict[str, Any]] = {
    "static_checker": {
        "enabled": True,
        "priority": ["ruff"],
        "tools": {
            "ruff": {
                "args": ["check", "--fix"],
            },
        },
    },
    "formatter": {
        "enabled": True,
        "priority": ["ruff", "black"],
        "tools": {
            "ruff": {
                "args": ["format"],
            },
            "black": {
                "args": ["format"],
            },
        },
    },
    "import_sorter": {
        "enabled": True,
        "priority": ["ruff", "isort"],
        "tools": {
            "ruff": {
                "args": ["check", "--select", "I", "--fix"],
            },
            "isort": {
                "args": ["--fix"],
            },
        },
    },
}


# === serger.meta ===
# src/serger/meta.py

"""Centralized program identity constants for Serger."""


_BASE = "serger"

# CLI script name (the executable or `poetry run` entrypoint)
PROGRAM_SCRIPT = _BASE

# config file name
PROGRAM_CONFIG = _BASE

# Human-readable name for banners, help text, etc.
PROGRAM_DISPLAY = _BASE.replace("-", " ").title()

# Python package / import name
PROGRAM_PACKAGE = _BASE.replace("-", "_")

# Environment variable prefix (used for <APP>_BUILD_LOG_LEVEL, etc.)
PROGRAM_ENV = _BASE.replace("-", "_").upper()

# Short tagline or __DESCRIPTION for help screens and metadata
DESCRIPTION = "Stitch your module into a single file."


@dataclass(frozen=True)
class Metadata:
    """Lightweight result from get_metadata(), containing version and commit info."""

    version: str
    commit: str

    def __str__(self) -> str:
        return f"{self.version} ({self.commit})"


# === serger.logs ===
# src/serger/logs.py


# --- Our application logger -----------------------------------------------------


class AppLogger(Logger):
    def determineLogLevel(  # noqa: N802
        self,
        *,
        args: argparse.Namespace | None = None,
        root_log_level: str | None = None,
        build_log_level: str | None = None,
    ) -> str:
        """Resolve log level from CLI → env → root config → default."""
        args_level = getattr(args, "log_level", None)
        if args_level is not None and args_level:
            # cast_hint would cause circular dependency
            return cast("str", args_level).upper()

        env_log_level = os.getenv(
            f"{PROGRAM_ENV}_{DEFAULT_ENV_LOG_LEVEL}"
        ) or os.getenv(DEFAULT_ENV_LOG_LEVEL)
        if env_log_level:
            return env_log_level.upper()

        if build_log_level:
            return build_log_level.upper()

        if root_log_level:
            return root_log_level.upper()

        return DEFAULT_LOG_LEVEL.upper()


# --- Logger initialization ---------------------------------------------------

# Force the logging module to use our subclass globally.
# This must happen *before* any loggers are created.
logging.setLoggerClass(AppLogger)

# Force registration of TRACE and SILENT levels
AppLogger.extendLoggingModule()

# Register log level environment variables and default
# This must happen before any loggers are created so they use the registered values
registerLogLevelEnvVars(
    [f"{PROGRAM_ENV}_{DEFAULT_ENV_LOG_LEVEL}", DEFAULT_ENV_LOG_LEVEL]
)
registerDefaultLogLevel(DEFAULT_LOG_LEVEL)

# Register the logger name so getLogger() can find it
registerLogger(PROGRAM_PACKAGE)

# Create the app logger instance via logging.getLogger()
# This ensures it's registered with the logging module and can be retrieved
# by other code that uses logging.getLogger()
_APP_LOGGER = cast("AppLogger", logging.getLogger(PROGRAM_PACKAGE))


# --- Convenience utils ---------------------------------------------------------


def getAppLogger() -> AppLogger:  # noqa: N802
    """Return the configured app logger.

    This is the app-specific logger getter that returns AppLogger type.
    Use this in application code instead of utils_logs.get_logger() for
    better type hints.
    """
    trace = makeSafeTrace()
    trace(
        "getAppLogger() called",
        f"id={id(_APP_LOGGER)}",
        f"name={_APP_LOGGER.name}",
        f"level={_APP_LOGGER.levelName}",
        f"handlers={[type(h).__name__ for h in _APP_LOGGER.handlers]}",
    )
    return _APP_LOGGER


# === serger.config.config_validate ===
# src/serger/config/config_validate.py


# --- constants ------------------------------------------------------

DRYRUN_KEYS = {"dry-run", "dry_run", "dryrun", "no-op", "no_op", "noop"}
DRYRUN_MSG = (
    "Ignored config key(s) {keys} {ctx}: this tool has no config option for it. "
    "Use the CLI flag '--dry-run' instead."
)

ROOT_ONLY_KEYS = {"watch_interval"}
ROOT_ONLY_MSG = "Ignored {keys} {ctx}: these options only apply at the root level."

# Field-specific type examples for better error messages
# Dict format: {field_pattern: example_value}
# Wildcard patterns (with *) are supported for matching multiple fields
FIELD_EXAMPLES: dict[str, str] = {
    "root.include": '["src/", "lib/"]',
    "root.out": '"dist/script.py"',
    "root.display_name": '"MyProject"',
    "root.description": '"A description of the project"',
    "root.repo": '"https://github.com/user/project"',
    "root.internal_imports": '"force_strip"',
    "root.external_imports": '"top"',
    "root.watch_interval": "1.5",
    "root.log_level": '"debug"',
    "root.strict_config": "true",
}


# ---------------------------------------------------------------------------
# main validator
# ---------------------------------------------------------------------------


def _set_valid_and_return(
    *,
    flush: bool = True,
    summary: ValidationSummary,  # could be modified
    agg: SchemaErrorAggregator,  # could be modified
) -> ValidationSummary:
    if flush:
        flush_schema_aggregators(summary=summary, agg=agg)
    summary.valid = not summary.errors and not summary.strict_warnings
    return summary


def _validate_root(
    parsed_cfg: dict[str, Any],
    *,
    strict_arg: bool | None,
    summary: ValidationSummary,  # modified
    agg: SchemaErrorAggregator,  # modified
) -> ValidationSummary | None:
    logger = getAppLogger()
    logger.trace(f"[validate_root] Validating root with {len(parsed_cfg)} keys")

    strict_config: bool = summary.strict
    # --- Determine strictness from arg or root config or default ---
    strict_from_root: Any = parsed_cfg.get("strict_config")
    if strict_arg is not None and strict_arg:
        strict_config = strict_arg
    elif strict_arg is None and isinstance(strict_from_root, bool):
        strict_config = strict_from_root

    if strict_config:
        summary.strict = True

    # --- Validate root-level keys ---
    root_schema = schema_from_typeddict(RootConfig)
    prewarn_root: set[str] = set()
    ok, found = warn_keys_once(
        "dry-run",
        DRYRUN_KEYS,
        parsed_cfg,
        "in top-level configuration",
        DRYRUN_MSG,
        strict_config=strict_config,
        summary=summary,
        agg=agg,
    )
    prewarn_root |= found

    ok = check_schema_conformance(
        parsed_cfg,
        root_schema,
        "in top-level configuration",
        strict_config=strict_config,
        summary=summary,
        prewarn=prewarn_root,
        ignore_keys={"builds"},
        base_path="root",
        field_examples=FIELD_EXAMPLES,
    )
    if not ok and not (summary.errors or summary.strict_warnings):
        collect_msg(
            "Top-level configuration invalid.",
            strict=True,
            summary=summary,
            is_error=True,
        )

    return None


def _validate_builds(
    parsed_cfg: dict[str, Any],
    *,
    strict_arg: bool | None,  # noqa: ARG001
    summary: ValidationSummary,  # modified
    agg: SchemaErrorAggregator,  # modified
) -> ValidationSummary | None:
    """Validate that 'builds' key is not present (multi-build not supported)."""
    logger = getAppLogger()
    logger.trace("[validate_builds] Checking for unsupported 'builds' key")

    if "builds" in parsed_cfg:
        collect_msg(
            "The 'builds' key is not supported. "
            "Please use a single flat configuration object with all options "
            "at the root level.",
            strict=True,
            summary=summary,
            is_error=True,
        )
        return _set_valid_and_return(summary=summary, agg=agg)

    return None


def validate_config(
    parsed_cfg: dict[str, Any],
    *,
    strict: bool | None = None,
) -> ValidationSummary:
    """Validate normalized config. Returns True if valid.

    strict=True  →  warnings become fatal, but still listed separately
    strict=False →  warnings remain non-fatal

    The `strict_config` key in the root config (and optionally in each build)
    controls strictness. CLI flags are not considered.

    Returns a ValidationSummary object.
    """
    logger = getAppLogger()
    logger.trace(f"[validate_config] Starting validation (strict={strict})")

    summary = ValidationSummary(
        valid=True,
        errors=[],
        strict_warnings=[],
        warnings=[],
        strict=DEFAULT_STRICT_CONFIG,
    )
    agg: SchemaErrorAggregator = {}

    # --- Validate root structure ---
    ret = _validate_root(
        parsed_cfg,
        strict_arg=strict,
        summary=summary,
        agg=agg,
    )
    if ret is not None:
        return ret

    # --- Validate builds structure ---
    ret = _validate_builds(parsed_cfg, strict_arg=strict, summary=summary, agg=agg)
    if ret is not None:
        return ret

    # --- finalize result ---
    return _set_valid_and_return(
        summary=summary,
        agg=agg,
    )


# === serger.config.config_loader ===
# src/serger/config/config_loader.py


def can_run_configless(args: argparse.Namespace) -> bool:
    """To run without config we need at least --include
    or --add-include or a positional include.

    Since this is pre-args normalization we need to still check
    positionals and not assume the positional out doesn't improperly
    greed grab the include.
    """
    return bool(
        getattr(args, "include", None)
        or getattr(args, "add_include", None)
        or getattr(args, "positional_include", None)
        or getattr(args, "positional_out", None),
    )


def find_config(
    args: argparse.Namespace,
    cwd: Path,
    *,
    missing_level: str = "error",
) -> Path | None:
    """Locate a configuration file.

    missing_level: log-level for failing to find a configuration file.

    Search order:
      1. Explicit path from CLI (--config)
      2. Default candidates in the current working directory:
         .{PROGRAM_CONFIG}.py, .{PROGRAM_CONFIG}.jsonc, .{PROGRAM_CONFIG}.json

    Returns the first matching path, or None if no config was found.
    """
    # NOTE: We only have early no-config Log-Level
    logger = getAppLogger()

    try:
        getLevelNumber(missing_level)
    except ValueError:
        logger.error(  # noqa: TRY400
            "Invalid log level name in find_config(): %s", missing_level
        )
        missing_level = "error"

    # --- 1. Explicit config path ---
    if getattr(args, "config", None):
        config = Path(args.config).expanduser().resolve()
        logger.trace(f"[find_config] Checking explicit path: {config}")
        if not config.exists():
            # Explicit path → hard failure
            xmsg = f"Specified config file not found: {config}"
            raise FileNotFoundError(xmsg)
        if config.is_dir():
            xmsg = f"Specified config path is a directory, not a file: {config}"
            raise ValueError(xmsg)
        return config

    # --- 2. Default candidate files (search current dir and parents) ---
    # Search from cwd up to filesystem root, returning first match (closest to cwd)
    current = cwd
    candidate_names = [
        f".{PROGRAM_CONFIG}.py",
        f".{PROGRAM_CONFIG}.jsonc",
        f".{PROGRAM_CONFIG}.json",
    ]
    found: list[Path] = []
    while True:
        for name in candidate_names:
            candidate = current / name
            if candidate.exists():
                found.append(candidate)
        if found:
            # Found at least one config file at this level
            break
        parent = current.parent
        if parent == current:  # Reached filesystem root
            break
        current = parent

    if not found:
        # Expected absence — soft failure (continue)
        logger.logDynamic(missing_level, f"No config file found in {cwd} or parents")
        return None

    # --- 3. Handle multiple matches at same level (prefer .py > .jsonc > .json) ---
    if len(found) > 1:
        # Prefer .py, then .jsonc, then .json
        priority = {".py": 0, ".jsonc": 1, ".json": 2}
        found_sorted = sorted(found, key=lambda p: priority.get(p.suffix, 99))
        names = ", ".join(p.name for p in found_sorted)
        logger.warning(
            "Multiple config files detected (%s); using %s.",
            names,
            found_sorted[0].name,
        )
        return found_sorted[0]
    return found[0]


def load_config(config_path: Path) -> dict[str, Any] | list[Any] | None:
    """Load configuration data from a file.

    Supports:
      - Python configs: .py files exporting either `config` or `includes`
      - JSON/JSONC configs: .json, .jsonc files

    Returns:
        The raw object defined in the config (dict, list, or None).
        Returns None for intentionally empty configs
          (e.g. empty files or `config = None`).

    Raises:
        ValueError if a .py config defines none of the expected variables.

    """
    # NOTE: We only have early no-config Log-Level
    logger = getAppLogger()
    logger.trace(f"[load_config] Loading from {config_path} ({config_path.suffix})")

    # --- Python config ---
    if config_path.suffix == ".py":
        config_globals: dict[str, Any] = {}

        # Allow local imports in Python configs (e.g. from ./helpers import foo)
        # This is safe because configs are trusted user code.
        parent_dir = str(config_path.parent)
        added_to_sys_path = parent_dir not in sys.path
        if added_to_sys_path:
            sys.path.insert(0, parent_dir)

        # Execute the python config file
        try:
            source = config_path.read_text(encoding="utf-8")
            exec(compile(source, str(config_path), "exec"), config_globals)  # noqa: S102
            logger.trace(
                f"[EXEC] globals after exec: {list(config_globals.keys())}",
            )
        except Exception as e:
            tb = traceback.format_exc()
            xmsg = (
                f"Error while executing Python config: {config_path.name}\n"
                f"{type(e).__name__}: {e}\n{tb}"
            )
            # Raise a generic runtime error for main() to catch and print cleanly
            raise RuntimeError(xmsg) from e
        finally:
            # Only remove if we actually inserted it
            if added_to_sys_path and sys.path[0] == parent_dir:
                sys.path.pop(0)

        for key in ("config", "includes"):
            if key in config_globals:
                result = config_globals[key]
                if not isinstance(result, (dict, list, type(None))):
                    xmsg = (
                        f"{key} in {config_path.name} must be a dict, list, or None"
                        f", not {type(result).__name__}"
                    )
                    raise TypeError(xmsg)

                # Explicitly narrow the loaded config to its expected union type.
                return cast("dict[str, Any] | list[Any] | None", result)

        xmsg = f"{config_path.name} did not define `config` or `includes`"
        raise ValueError(xmsg)

    # JSONC / JSON fallback
    try:
        return load_jsonc(config_path)
    except ValueError as e:
        clean_msg = remove_path_in_error_message(str(e), config_path)
        xmsg = (
            f"Error while loading configuration file '{config_path.name}': {clean_msg}"
        )
        raise ValueError(xmsg) from e


def _parse_case_2_list_of_strings(
    raw_config: list[str],
) -> dict[str, Any]:
    # --- Case 2: naked list of strings → flat config with include ---
    return {"include": list(raw_config)}


def _parse_case_flat_config(
    raw_config: dict[str, Any],
) -> dict[str, Any]:
    # --- Flat config: all fields at root level ---
    # The user gave a flat single-build config.
    # No hoisting needed - all fields are already at the root level.
    return dict(raw_config)


def parse_config(
    raw_config: dict[str, Any] | list[Any] | None,
) -> dict[str, Any] | None:
    """Normalize user config into canonical RootConfig shape (no filesystem work).

    Accepted forms:
      - None / [] / {}                → None (empty config)
      - ["src/**", "assets/**"]       → flat config with those includes
      - {...}                         → flat config (all fields at root level)

     After normalization:
      - Returns flat dict with all fields at root level, or None for empty config.
      - Preserves all unknown keys for later validation.
    """
    # NOTE: This function only normalizes shape — it does NOT validate or restrict keys.
    #       Unknown keys are preserved for the validation phase.

    logger = getAppLogger()
    logger.trace(f"[parse_config] Parsing {type(raw_config).__name__}")

    # --- Case 1: empty config → None ---
    # Includes None (empty file / config = None), [] (no builds), and {} (empty object)
    if not raw_config or raw_config == {}:  # handles None, [], {}
        return None

    # --- Case 2: naked list of strings → flat config with include ---
    if isinstance(raw_config, list) and all(isinstance(x, str) for x in raw_config):
        logger.trace("[parse_config] Detected case: list of strings")
        return _parse_case_2_list_of_strings(raw_config)

    # --- Invalid list types (not all strings) ---
    if isinstance(raw_config, list):
        xmsg = (
            "Invalid list configuration: "
            "all elements must be strings (for include patterns)."
        )
        raise TypeError(xmsg)

    # --- From here on, must be a dict ---
    # Defensive check: should be unreachable after list cases above,
    # but kept to guard against future changes or malformed input.
    if not isinstance(raw_config, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
        xmsg = (
            f"Invalid top-level value: {type(raw_config).__name__} "
            "(expected object or list of strings)",
        )
        raise TypeError(xmsg)

    # --- Flat config: all fields at root level ---
    # Note: build/builds keys will be rejected as unknown keys by validation
    return _parse_case_flat_config(raw_config)


def _validation_summary(
    summary: ValidationSummary,
    config_path: Path,
) -> None:
    """Pretty-print a validation summary using the standard log() interface."""
    logger = getAppLogger()
    mode = "strict mode" if summary.strict else "lenient mode"

    # --- Build concise counts line ---
    counts: list[str] = []
    if summary.errors:
        counts.append(f"{len(summary.errors)} error{plural(summary.errors)}")
    if summary.strict_warnings:
        counts.append(
            f"{len(summary.strict_warnings)} strict warning"
            f"{plural(summary.strict_warnings)}",
        )
    if summary.warnings:
        counts.append(
            f"{len(summary.warnings)} normal warning{plural(summary.warnings)}",
        )
    counts_msg = f"\nFound {', '.join(counts)}." if counts else ""

    # --- Header (single icon) ---
    if not summary.valid:
        logger.error(
            "Failed to validate configuration file %s (%s).%s",
            config_path.name,
            mode,
            counts_msg,
        )
    elif counts:
        logger.warning(
            "Validated configuration file  %s (%s) with warnings.%s",
            config_path.name,
            mode,
            counts_msg,
        )
    else:
        logger.debug("Validated  %s (%s) successfully.", config_path.name, mode)

    # --- Detailed sections ---
    if summary.errors:
        msg_summary = "\n  • ".join(summary.errors)
        logger.error("\nErrors:\n  • %s", msg_summary)
    if summary.strict_warnings:
        msg_summary = "\n  • ".join(summary.strict_warnings)
        logger.error("\nStrict warnings (treated as errors):\n  • %s", msg_summary)
    if summary.warnings:
        msg_summary = "\n  • ".join(summary.warnings)
        logger.warning("\nWarnings (non-fatal):\n  • %s", msg_summary)


def load_and_validate_config(
    args: argparse.Namespace,
) -> tuple[Path, RootConfig, ValidationSummary] | None:
    """Find, load, parse, and validate the user's configuration.

    Also determines the effective log level (from CLI/env/config/default)
    early, so logging can initialize as soon as possible.

    Returns:
        (config_path, root_cfg, validation_summary)
        if a config file was found and valid, or None if no config was found.

    """
    logger = getAppLogger()
    # warn if cwd doesn't exist, edge case. We might still be able to run
    cwd = Path.cwd().resolve()
    if not cwd.exists():
        logger.warning("Working directory does not exist: %s", cwd)

    # --- Find config file ---
    cwd = Path.cwd().resolve()
    missing_level = "warning" if can_run_configless(args) else "error"
    config_path = find_config(args, cwd, missing_level=missing_level)
    if config_path is None:
        return None

    # --- Load the raw config (dict or list) ---
    raw_config = load_config(config_path)
    if raw_config is None:
        return None

    # --- Early peek for log_level before parsing ---
    # Handles:
    #   - Root configs with "log_level"
    #   - Single-build dicts with "log_level"
    # Skips empty or list configs.
    if isinstance(raw_config, dict):
        raw_log_level = raw_config.get("log_level")
        if isinstance(raw_log_level, str) and raw_log_level:
            logger.setLevel(
                logger.determineLogLevel(args=args, root_log_level=raw_log_level)
            )

    # --- Parse structure into final form without types ---
    try:
        parsed_cfg = parse_config(raw_config)
    except TypeError as e:
        xmsg = f"Could not parse config {config_path.name}: {e}"
        raise TypeError(xmsg) from e
    if parsed_cfg is None:
        return None

    # --- Validate schema ---
    validation_result = validate_config(parsed_cfg)
    if not validation_result.valid:
        # Build comprehensive error message with all details
        mode = "strict mode" if validation_result.strict else "lenient mode"
        counts: list[str] = []
        if validation_result.errors:
            error_count = len(validation_result.errors)
            counts.append(f"{error_count} error{plural(validation_result.errors)}")
        if validation_result.strict_warnings:
            warning_count = len(validation_result.strict_warnings)
            counts.append(
                f"{warning_count} strict warning"
                f"{plural(validation_result.strict_warnings)}"
            )
        counts_msg = f"\nFound {', '.join(counts)}." if counts else ""

        # Build detailed error message with newlines
        error_parts: list[str] = []
        error_parts.append(
            f"Failed to validate configuration file {config_path.name} "
            f"({mode}).{counts_msg}"
        )

        if validation_result.errors:
            msg_summary = "\n  • ".join(validation_result.errors)
            error_parts.append(f"\nErrors:\n  • {msg_summary}")

        if validation_result.strict_warnings:
            msg_summary = "\n  • ".join(validation_result.strict_warnings)
            error_parts.append(
                f"\nStrict warnings (treated as errors):\n  • {msg_summary}"
            )

        xmsg = "".join(error_parts)
        exception = ValueError(xmsg)
        exception.data = validation_result  # type: ignore[attr-defined]
        raise exception

    # Log validation summary (only if valid or has warnings)
    _validation_summary(validation_result, config_path)

    # --- Upgrade to RootConfig type ---
    root_cfg: RootConfig = cast_hint(RootConfig, parsed_cfg)
    return config_path, root_cfg, validation_result


# === serger.utils.utils_installed_packages ===
# src/serger/utils/utils_installed_packages.py


def discover_installed_packages_roots() -> list[str]:
    """Discover installed packages root directories.

    Searches for site-packages directories in priority order:
    1. Poetry environment: `poetry env info --path` →
       `{path}/lib/python*/site-packages`
    2. Virtualenv/pip: Check `sys.path` for `site-packages` or
       `dist-packages` in virtualenv paths
    3. User site-packages: `~/.local/lib/python*/site-packages`
       (or platform-specific)
    4. System site-packages: Check `sys.path` for system
       `site-packages` or `dist-packages`

    Handles both `site-packages` and `dist-packages` (Debian/Ubuntu).

    Returns:
        List of absolute paths to site-packages directories in priority order.
        Returns empty list if nothing found (does not error).

    Note:
        Paths are deduplicated and returned in priority order.
    """
    discovered: list[str] = []
    seen: set[str] = set()

    # 1. Poetry environment (highest priority)
    poetry_paths = _discover_poetry_site_packages()
    for path in poetry_paths:
        if path not in seen:
            discovered.append(path)
            seen.add(path)

    # 2. Virtualenv/pip from sys.path
    venv_paths = _discover_venv_site_packages()
    for path in venv_paths:
        if path not in seen:
            discovered.append(path)
            seen.add(path)

    # 3. User site-packages
    user_paths = _discover_user_site_packages()
    for path in user_paths:
        if path not in seen:
            discovered.append(path)
            seen.add(path)

    # 4. System site-packages from sys.path
    system_paths = _discover_system_site_packages()
    for path in system_paths:
        if path not in seen:
            discovered.append(path)
            seen.add(path)

    return discovered


def _discover_poetry_site_packages() -> list[str]:
    """Discover Poetry environment site-packages directories.

    Returns:
        List of absolute paths to Poetry site-packages directories.
        Returns empty list if Poetry is not available or not in use.
    """
    poetry_cmd = shutil.which("poetry")
    if not poetry_cmd:
        return []

    try:
        result = subprocess.run(  # noqa: S603
            [poetry_cmd, "env", "info", "--path"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        venv_path = Path(result.stdout.strip())
        if not venv_path.exists():
            return []

        # Look for lib/python*/site-packages or lib/python*/dist-packages
        site_packages_paths: list[str] = []
        lib_dir = venv_path / "lib"
        if lib_dir.exists():
            for python_dir in lib_dir.iterdir():
                if python_dir.is_dir() and python_dir.name.startswith("python"):
                    for pkg_dir_name in ("site-packages", "dist-packages"):
                        pkg_dir = python_dir / pkg_dir_name
                        if pkg_dir.exists() and pkg_dir.is_dir():
                            site_packages_paths.append(str(pkg_dir.resolve()))

        return sorted(site_packages_paths)
    except Exception:  # noqa: BLE001
        # Poetry command failed or venv path invalid - return empty
        return []


def _discover_venv_site_packages() -> list[str]:
    """Discover virtualenv/pip site-packages from sys.path.

    Returns:
        List of absolute paths to virtualenv site-packages directories.
        Returns empty list if no virtualenv is detected.
    """
    discovered: list[str] = []
    seen: set[str] = set()

    # Check if we're in a virtualenv
    if not (
        hasattr(sys, "real_prefix")
        or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
    ):
        # Not in a virtualenv
        return []

    # Check sys.path for site-packages or dist-packages in virtualenv
    for path_str in sys.path:
        path = Path(path_str).resolve()
        if not path.exists():
            continue

        # Check if this path is a site-packages or dist-packages directory
        if path.name in ("site-packages", "dist-packages"):
            path_str_abs = str(path)
            if path_str_abs not in seen:
                discovered.append(path_str_abs)
                seen.add(path_str_abs)
        # Also check if path is inside a site-packages or dist-packages directory
        elif "site-packages" in path.parts or "dist-packages" in path.parts:
            # Find the site-packages or dist-packages parent
            for parent in path.parents:
                if parent.name in ("site-packages", "dist-packages"):
                    parent_str = str(parent.resolve())
                    if parent_str not in seen:
                        discovered.append(parent_str)
                        seen.add(parent_str)
                    break

    return sorted(discovered)


def _discover_user_site_packages() -> list[str]:
    """Discover user site-packages directories.

    Returns:
        List of absolute paths to user site-packages directories.
        Returns empty list if none found.
    """
    discovered: list[str] = []

    # Use site.getusersitepackages() if available (Python 3.11+)
    # For Python 3.10, we'll construct it manually
    try:
        user_site = site.getusersitepackages()
        if user_site:
            user_path = Path(user_site).resolve()
            if user_path.exists() and user_path.is_dir():
                discovered.append(str(user_path))
    except AttributeError:
        # Python 3.10 doesn't have getusersitepackages()
        # Construct it manually: ~/.local/lib/python*/site-packages
        home = Path.home()
        local_lib = home / ".local" / "lib"
        if local_lib.exists():
            for python_dir in local_lib.iterdir():
                if python_dir.is_dir() and python_dir.name.startswith("python"):
                    for pkg_dir_name in ("site-packages", "dist-packages"):
                        pkg_dir = python_dir / pkg_dir_name
                        if pkg_dir.exists() and pkg_dir.is_dir():
                            discovered.append(str(pkg_dir.resolve()))

    return sorted(discovered)


def _discover_system_site_packages() -> list[str]:
    """Discover system site-packages directories from sys.path.

    Returns:
        List of absolute paths to system site-packages directories.
        Returns empty list if none found.
    """
    discovered: list[str] = []
    seen: set[str] = set()

    # Get system site-packages
    system_sites: Sequence[str] = []
    with contextlib.suppress(AttributeError):
        # Python 3.10 doesn't have getsitepackages()
        # Fall back to checking sys.path for system paths
        system_sites = site.getsitepackages()

    # Add from getsitepackages() if available
    for site_path_str in system_sites:
        site_path = Path(site_path_str).resolve()
        if site_path.exists() and site_path.is_dir():
            site_str = str(site_path)
            if site_str not in seen:
                discovered.append(site_str)
                seen.add(site_str)

    # Also check sys.path for system site-packages/dist-packages
    # (not in virtualenv, not user site)
    for path_str in sys.path:
        path = Path(path_str).resolve()
        if not path.exists():
            continue

        # Skip if this looks like a virtualenv path
        if "site-packages" in path.parts or "dist-packages" in path.parts:
            # Check if it's a system path (not in home, not in venv)
            path_str_abs = str(path)
            if (
                path_str_abs not in seen
                and not path_str_abs.startswith(str(Path.home()))
                and not (
                    hasattr(sys, "real_prefix")
                    or (
                        hasattr(sys, "base_prefix")
                        and sys.base_prefix != sys.prefix
                        and path_str_abs.startswith(sys.prefix)
                    )
                )
            ):
                # Find the site-packages or dist-packages parent
                for parent in path.parents:
                    if parent.name in ("site-packages", "dist-packages"):
                        parent_str = str(parent.resolve())
                        if parent_str not in seen:
                            discovered.append(parent_str)
                            seen.add(parent_str)
                        break

    return sorted(discovered)


# === serger.utils.utils_paths ===
# src/serger/utils/utils_paths.py


def shorten_path_for_display(
    path: Path | str | PathResolved | IncludeResolved,
    *,
    cwd: Path | None = None,
    config_dir: Path | None = None,
) -> str:
    """Shorten an absolute path for display purposes.

    Tries to make the path relative to cwd first, then config_dir, and picks
    the shortest result. If neither works, returns the absolute path as a string.

    If path is a PathResolved or IncludeResolved, resolves exclusively against
    its built-in `root` field (ignoring cwd and config_dir).

    Args:
        path: Path to shorten (can be Path, str, PathResolved, or IncludeResolved)
        cwd: Current working directory (optional, ignored for PathResolved/
            IncludeResolved)
        config_dir: Config directory (optional, ignored for PathResolved/
            IncludeResolved)

    Returns:
        Shortened path string (relative when possible, absolute otherwise)
    """
    # Handle PathResolved or IncludeResolved types
    if isinstance(path, dict) and "root" in path:
        # PathResolved or IncludeResolved - resolve against its root exclusively
        root = Path(path["root"]).resolve()
        path_val = path["path"]
        # Resolve path relative to root
        path_obj = (root / path_val).resolve()
        # Try to make relative to root
        try:
            rel_to_root = str(path_obj.relative_to(root))
        except ValueError:
            # Not relative to root, return absolute
            return str(path_obj)
        else:
            if rel_to_root:
                return rel_to_root
            return "."

    # Handle regular Path or str
    path_obj = Path(path).resolve()

    candidates: list[str] = []

    # Try relative to cwd
    if cwd:
        cwd_resolved = Path(cwd).resolve()
        try:
            rel_to_cwd = str(path_obj.relative_to(cwd_resolved))
            candidates.append(rel_to_cwd)
        except ValueError:
            pass

    # Try relative to config_dir
    if config_dir:
        config_dir_resolved = Path(config_dir).resolve()
        try:
            rel_to_config = str(path_obj.relative_to(config_dir_resolved))
            candidates.append(rel_to_config)
        except ValueError:
            pass

    # If we have candidates, pick the shortest one
    if candidates:
        return min(candidates, key=len)

    # Fall back to absolute path
    return str(path_obj)


def shorten_paths_for_display(
    paths: (
        list[Path]
        | list[str]
        | list[PathResolved]
        | list[IncludeResolved]
        | list[Path | str | PathResolved | IncludeResolved]
    ),
    *,
    cwd: Path | None = None,
    config_dir: Path | None = None,
) -> list[str]:
    """Shorten a list of paths for display purposes.

    Applies shorten_path_for_display to each path in the list. Can handle
    mixed types (Path, str, PathResolved, IncludeResolved).

    Args:
        paths: List of paths to shorten (can be Path, str, PathResolved, or
            IncludeResolved, or a mix)
        cwd: Current working directory (optional, ignored for PathResolved/
            IncludeResolved)
        config_dir: Config directory (optional, ignored for PathResolved/
            IncludeResolved)

    Returns:
        List of shortened path strings
    """
    return [
        shorten_path_for_display(path, cwd=cwd, config_dir=config_dir) for path in paths
    ]


# === serger.utils.utils_types ===
# src/serger/utils/utils_types.py


def _root_resolved(
    path: Path | str,
    root: Path | str,
    pattern: str | None,
    origin: OriginType,
) -> dict[str, object]:
    # Preserve raw string if available (to keep trailing slashes)
    raw_path = path if isinstance(path, str) else str(path)
    result: dict[str, object] = {
        "path": raw_path,
        "root": Path(root).resolve(),
        "origin": origin,
    }
    if pattern is not None:
        result["pattern"] = pattern
    return result


def make_pathresolved(
    path: Path | str,
    root: Path | str = ".",
    origin: OriginType = "code",
    *,
    pattern: str | None = None,
) -> PathResolved:
    """Quick helper to build a PathResolved entry."""
    # mutate class type
    return cast("PathResolved", _root_resolved(path, root, pattern, origin))


def make_includeresolved(
    path: Path | str,
    root: Path | str = ".",
    origin: OriginType = "code",
    *,
    pattern: str | None = None,
    dest: Path | str | None = None,
) -> IncludeResolved:
    """Create an IncludeResolved entry with optional dest override."""
    entry = _root_resolved(path, root, pattern, origin)
    if dest is not None:
        entry["dest"] = Path(dest)
    # mutate class type
    return cast("IncludeResolved", entry)


# === serger.utils.utils_validation ===
# src/serger/utils/utils_validation.py


def validate_required_keys(
    config: dict[str, Any] | Any,
    required_keys: set[str],
    param_name: str,
) -> None:
    """Validate that a config dict contains all required keys.

    Args:
        config: The config dict to validate (TypedDict or dict)
        required_keys: Set of required key names
        param_name: Name of the parameter (for error messages)

    Raises:
        TypeError: If any required keys are missing
    """
    if not required_keys:
        return

    # TypedDict is a dict at runtime, but type checkers need help
    config_dict = cast("dict[str, Any]", config)
    missing = required_keys - config_dict.keys()
    if missing:
        missing_str = ", ".join(sorted(missing))
        xmsg = (
            f"Missing required keys in {param_name}: {missing_str}. "
            f"Required keys: {', '.join(sorted(required_keys))}"
        )
        raise TypeError(xmsg)


# === serger.utils.utils_matching ===
# src/serger/utils/utils_matching.py


def is_excluded(path_entry: PathResolved, exclude_patterns: list[PathResolved]) -> bool:
    """High-level helper for internal use.
    Accepts PathResolved entries and delegates to the smart matcher.
    """
    validate_required_keys(path_entry, {"path", "root"}, "path_entry")
    for exc in exclude_patterns:
        validate_required_keys(exc, {"path", "root"}, "exclude_patterns item")
    logger = getAppLogger()
    path = path_entry["path"]
    root = path_entry["root"]
    # Patterns are always normalized to PathResolved["path"] under config_resolve
    patterns = [str(e["path"]) for e in exclude_patterns]
    result = is_excluded_raw(path, patterns, root)
    logger.trace(
        f"[is_excluded] path={path}, root={root},"
        f" patterns={len(patterns)}, excluded={result}"
    )
    return result


# === serger.utils.utils_modules ===
# src/serger/utils/utils_modules.py


def _non_glob_prefix(pattern: str) -> Path:
    """Return the non-glob leading portion of a pattern, as a Path."""
    parts: list[str] = []
    for part in Path(pattern).parts:
        if re.search(r"[*?\[\]]", part):
            break
        parts.append(part)
    return Path(*parts)


def _interpret_dest_for_module_name(  # noqa: PLR0911
    file_path: Path,
    include_root: Path,
    include_pattern: str,
    dest: Path | str,
) -> Path:
    """Interpret dest parameter to compute virtual destination path for module name.

    This adapts logic from _compute_dest() but returns a path that can be used
    for module name derivation, not an actual file system destination.

    Args:
        file_path: The actual source file path
        include_root: Root directory for the include pattern
        include_pattern: Original include pattern string
        dest: Dest parameter (can be pattern, relative path, or explicit override)

    Returns:
        Virtual destination path that should be used for module name derivation
    """
    logger = getAppLogger()
    dest_path = Path(dest)
    include_root_resolved = Path(include_root).resolve()
    file_path_resolved = file_path.resolve()

    logger.trace(
        f"[DEST_INTERPRET] file={file_path}, root={include_root}, "
        f"pattern={include_pattern!r}, dest={dest}",
    )

    # If dest is absolute, use it directly
    if dest_path.is_absolute():
        result = dest_path.resolve()
        logger.trace(f"[DEST_INTERPRET] absolute dest → {result}")
        return result

    # Treat trailing slashes as if they implied recursive includes
    if include_pattern.endswith("/"):
        include_pattern = include_pattern.rstrip("/")
        try:
            rel = file_path_resolved.relative_to(
                include_root_resolved / include_pattern,
            )
            result = dest_path / rel
            logger.trace(
                f"[DEST_INTERPRET] trailing-slash include → rel={rel}, result={result}",
            )
            return result  # noqa: TRY300
        except ValueError:
            logger.trace("[DEST_INTERPRET] trailing-slash fallback (ValueError)")
            return dest_path / file_path.name

    # Handle glob patterns
    if has_glob_chars(include_pattern):
        # Special case: if dest is just a simple name (no path parts) and pattern
        # is a single-level file glob like "a/*.py" (one directory part, then /*.py),
        # use dest directly (explicit override)
        # This handles the case where dest is meant to override the entire module name
        dest_parts = list(dest_path.parts)
        # Count directory parts before the glob (split by / and count non-glob parts)
        pattern_dir_parts = include_pattern.split("/")
        # Remove the glob part (last part containing *)
        non_glob_parts = [
            p
            for p in pattern_dir_parts
            if "*" not in p and "?" not in p and "[" not in p
        ]
        is_single_level_glob = (
            len(dest_parts) == 1
            and len(non_glob_parts) == 1
            and include_pattern.endswith("/*.py")
            and not include_pattern.endswith("/*")
        )
        if is_single_level_glob:
            logger.trace(
                f"[DEST_INTERPRET] explicit dest override → {dest_path}",
            )
            return dest_path

        # For glob patterns, strip non-glob prefix
        prefix = _non_glob_prefix(include_pattern)
        try:
            rel = file_path_resolved.relative_to(include_root_resolved / prefix)
            result = dest_path / rel
            logger.trace(
                f"[DEST_INTERPRET] glob include → prefix={prefix}, "
                f"rel={rel}, result={result}",
            )
            return result  # noqa: TRY300
        except ValueError:
            logger.trace("[DEST_INTERPRET] glob fallback (ValueError)")
            return dest_path / file_path.name

    # For literal includes, check if dest is a full path (ends with .py)
    # If so, use it directly; otherwise preserve structure relative to dest
    dest_str = str(dest_path)
    if dest_str.endswith(".py"):
        # Dest is a full path - use it directly
        logger.trace(
            f"[DEST_INTERPRET] literal include with full dest path → {dest_path}",
        )
        return dest_path

    # Dest is a directory prefix - preserve structure relative to dest
    try:
        rel = file_path_resolved.relative_to(include_root_resolved)
        result = dest_path / rel
        logger.trace(f"[DEST_INTERPRET] literal include → rel={rel}, result={result}")
        return result  # noqa: TRY300
    except ValueError:
        # Fallback when file_path isn't under include_root
        logger.trace(
            f"[DEST_INTERPRET] fallback (file not under root) → "
            f"using name={file_path.name}",
        )
        return dest_path / file_path.name


def derive_module_name(  # noqa: PLR0912, PLR0915, C901
    file_path: Path,
    package_root: Path,
    include: IncludeResolved | None = None,
    source_bases: list[str] | None = None,
    user_provided_source_bases: list[str] | None = None,
    detected_packages: set[str] | None = None,
) -> str:
    """Derive module name from file path for shim generation.

    Default behavior: Preserve directory structure from file path relative to
    package root. With dest: Preserve structure from dest path instead.
    With source_bases: For external files, derive relative to matching module_base.

    Args:
        file_path: The file path to derive module name from
        package_root: Common root of all included files
        include: Optional include that produced this file (for dest access)
        source_bases: Optional list of module base directories for external files
        user_provided_source_bases: Optional list of user-provided module bases
            (from config, excludes auto-discovered package directories)
        detected_packages: Optional set of detected package names for preserving
            package structure when module_base is a detected package

    Returns:
        Derived module name (e.g., "core.base" from "src/core/base.py")

    Raises:
        ValueError: If module name would be empty or invalid
    """
    logger = getAppLogger()
    file_path_resolved = file_path.resolve()
    package_root_resolved = package_root.resolve()

    # Check if include has dest override
    if include:
        validate_required_keys(include, {"path", "root"}, "include")
    if include and include.get("dest"):
        dest_raw = include.get("dest")
        # dest is Path | None, but we know it's truthy from the if check
        if dest_raw is None:
            # This shouldn't happen due to the if check, but satisfy type checker
            dest: Path | str = Path()
        else:
            dest = dest_raw  # dest_raw is Path here
        include_root = Path(include["root"]).resolve()
        include_pattern = str(include["path"])

        # Use _interpret_dest_for_module_name to get virtual destination path
        dest_path = _interpret_dest_for_module_name(
            file_path_resolved,
            include_root,
            include_pattern,
            dest,
        )

        # Convert dest path to module name, preserving directory structure
        # custom/sub/foo.py → custom.sub.foo
        parts = list(dest_path.parts)
        if parts and parts[-1].endswith(".py"):
            parts[-1] = parts[-1][:-3]  # Remove .py extension
        elif parts and parts[-1].endswith("/"):
            # Trailing slash means directory - use as-is but might need adjustment
            parts[-1] = parts[-1].rstrip("/")

        # Filter out empty parts and join
        parts = [p for p in parts if p]
        if not parts:
            xmsg = f"Cannot derive module name from dest path: {dest_path}"
            raise ValueError(xmsg)

        module_name = ".".join(parts)
        logger.trace(
            f"[DERIVE] file={file_path}, dest={dest} → module={module_name}",
        )
        return module_name

    # Check if file is under package_root
    package_root_rel: Path | None = None
    try:
        package_root_rel = file_path_resolved.relative_to(package_root_resolved)
        is_under_package_root = True
    except ValueError:
        is_under_package_root = False

    # Check source_bases if provided
    # If file is under both package_root and a module_base, prefer module_base
    # when it's more specific (deeper in the tree than package_root)
    # BUT: Don't use module_base if it's the file's parent directory
    # (would lose package name)
    # Use user_provided_source_bases for the fix (external files),
    # fall back to all source_bases for backward compatibility
    rel_path = None
    # Prefer user-provided source_bases (from config) over auto-discovered ones
    bases_to_use = (
        user_provided_source_bases if user_provided_source_bases else source_bases
    )
    if bases_to_use:
        file_parent = file_path_resolved.parent
        # Try each module_base in order (first match wins)
        for module_base_str in bases_to_use:
            module_base = Path(module_base_str).resolve()
            # Skip if module_base is the file's parent directory
            # (this would cause files in package dirs to lose their package name)
            if module_base == file_parent:
                logger.trace(
                    f"[DERIVE] file={file_path} parent={file_parent} equals "
                    f"module_base={module_base}, skipping (would lose package name)",
                )
                continue
            try:
                module_base_rel = file_path_resolved.relative_to(module_base)
                # Use module_base if:
                # 1. File is not under package_root, OR
                # 2. File is under both, but module_base is more specific (deeper)
                if not is_under_package_root:
                    rel_path = module_base_rel
                    logger.trace(
                        f"[DERIVE] file={file_path} not under root={package_root}, "
                        f"but under module_base={module_base}, using relative path",
                    )
                    break
                # Check if module_base is more specific (deeper) than package_root
                try:
                    module_base.relative_to(package_root_resolved)
                    # module_base is under package_root
                    # For files from installed_bases or external sources, prefer
                    # module_base even if not deeper (to get correct module names)
                    # Check if file is actually under this module_base
                    try:
                        file_path_resolved.relative_to(module_base)
                        # File is under module_base - use it for correct module name
                        rel_path = module_base_rel
                        # If module_base.name is a detected package AND it's not the
                        # package_root name, prepend it to preserve package structure
                        # (e.g., pkg1/sub/mod1.py -> pkg1.sub.mod1)
                        # But don't prepend if:
                        # 1. module_base is the package_root itself (double prefix)
                        # 2. module_base.name is a common directory name
                        #    (src, lib, site-packages)
                        # 3. The relative path already starts with module_base.name
                        should_prepend = False
                        if (
                            detected_packages
                            and module_base.name in detected_packages
                            and module_base.name != package_root_resolved.name
                        ):
                            # Don't prepend common directory names
                            common_dirs = {
                                "src",
                                "lib",
                                "site-packages",
                                "dist-packages",
                            }
                            if module_base.name not in common_dirs:
                                # Check if rel_path already starts with module_base.name
                                # (avoid double prefix like pkg1.pkg1.sub.mod1)
                                rel_parts = list(rel_path.parts)
                                if rel_parts:
                                    first_part = rel_parts[0]
                                    # Only prepend if first part is not module_base.name
                                    if first_part != module_base.name:
                                        should_prepend = True
                        if should_prepend:
                            # Prepend module_base.name to preserve package structure
                            rel_path = Path(module_base.name) / rel_path
                            logger.trace(
                                f"[DERIVE] file={file_path} under both "
                                f"root={package_root} and module_base={module_base}, "
                                f"using module_base (file is under module_base, "
                                f"prepending package {module_base.name})",
                            )
                        else:
                            logger.trace(
                                f"[DERIVE] file={file_path} under both "
                                f"root={package_root} and module_base={module_base}, "
                                f"using module_base (file is under module_base)",
                            )
                        break
                    except ValueError:
                        # File is not under this module_base, continue
                        pass
                    # module_base is at same level or higher, don't use it
                    # (preserve original behavior for files under package_root)
                except ValueError:
                    # module_base is not under package_root
                    # Only use it if file is also not under package_root
                    # (if file is under package_root, preserve original behavior)
                    if not is_under_package_root:
                        rel_path = module_base_rel
                        logger.trace(
                            f"[DERIVE] file={file_path} not under root={package_root}, "
                            f"but under module_base={module_base}, using module_base",
                        )
                        break
                    # File is under package_root but module_base is not
                    # Don't use module_base (preserve original behavior)
            except ValueError:
                # Not under this module_base, try next
                continue

    # If not using module_base, derive from file path relative to package root
    if rel_path is None:
        if is_under_package_root and package_root_rel is not None:
            rel_path = package_root_rel
            logger.trace(
                f"[DERIVE] file={file_path} under package_root={package_root}, "
                f"using relative path",
            )
        else:
            # File not under package root or any module_base - use just filename
            logger.trace(
                f"[DERIVE] file={file_path} not under root={package_root} "
                f"or any module_base, using filename",
            )
            rel_path = Path(file_path.name)

    # Convert path to module name, preserving directory structure
    # path/to/file.py → path.to.file
    parts = list(rel_path.parts)
    if parts and parts[-1].endswith(".py"):
        parts[-1] = parts[-1][:-3]  # Remove .py extension

    # Filter out empty parts
    parts = [p for p in parts if p]
    if not parts:
        xmsg = f"Cannot derive module name from file path: {file_path}"
        raise ValueError(xmsg)

    module_name = ".".join(parts)
    logger.trace(f"[DERIVE] file={file_path} → module={module_name}")
    return module_name


# === serger.module_actions ===
"""Module actions processing for renaming, moving, copying, and deleting modules."""


def extract_module_name_from_source_path(
    source_path: Path,
    package_root: Path,
    expected_source: str,
) -> str:
    """Extract module name from source_path and verify it matches expected_source.

    Args:
        source_path: Path to Python file
        package_root: Root directory for module name derivation
        expected_source: Expected module name from action source field

    Returns:
        Extracted module name

    Raises:
        ValueError: If module name doesn't match expected_source or file is invalid
    """
    logger = getAppLogger()

    # Validate file exists
    if not source_path.exists():
        msg = f"source_path file does not exist: {source_path}"
        raise ValueError(msg)

    # Validate is Python file
    if source_path.suffix != ".py":
        msg = f"source_path must be a Python file (.py extension), got: {source_path}"
        raise ValueError(msg)

    # Extract module name using derive_module_name
    # Use None for include since source_path files don't have include metadata
    extracted_module_name = derive_module_name(source_path, package_root, include=None)

    # Verify extracted module name matches expected_source
    # Allow exact match or derivable (e.g., if package is "internal" and file
    # has module "internal.utils", source can be "internal.utils" or just "utils")
    if extracted_module_name == expected_source:
        # Exact match
        logger.trace(
            f"[source_path] Module name matches: "
            f"{extracted_module_name} == {expected_source}"
        )
        return extracted_module_name

    # Check if expected_source is a suffix of extracted_module_name
    # (e.g., extracted="internal.utils", expected="utils")
    # Also check if extracted_module_name ends with expected_source
    # (e.g., extracted="other.utils", expected="utils")
    if extracted_module_name.endswith((f".{expected_source}", expected_source)):
        # Suffix match - this is allowed
        logger.trace(
            f"[source_path] Module name suffix matches: "
            f"{extracted_module_name} ends with {expected_source}"
        )
        return extracted_module_name

    # Check if extracted_module_name is a prefix of expected_source
    # (e.g., extracted="utils", expected="internal.utils")
    # This means the file has a shorter module name than expected
    # We don't allow this - the file's module name should match or be longer
    # (e.g., file has "internal.utils", source can be "internal.utils" or "utils")

    # No match - raise error
    msg = (
        f"Module name extracted from source_path ({extracted_module_name}) "
        f"does not match expected source ({expected_source}). "
        f"File: {source_path}, package_root: {package_root}"
    )
    raise ValueError(msg)


def set_mode_generated_action_defaults(
    action: ModuleActionFull,
) -> ModuleActionFull:
    """Set default values for mode-generated actions.

    Mode-generated actions are created fresh (not from config), so they need
    defaults applied. All mode-generated actions have:
    - action: "move" (if not specified)
    - mode: "preserve" (if not specified)
    - scope: "original" (always set for mode-generated)
    - affects: "shims" (if not specified)
    - cleanup: "auto" (if not specified)

    Note: User actions from RootConfigResolved already have all defaults
    applied (including scope: "shim") from config resolution (iteration 04).

    Args:
        action: Action dict that may be missing some fields

    Returns:
        Action dict with all fields present (defaults applied)
    """
    # Create a copy to avoid mutating the input
    result: ModuleActionFull = dict(action)  # type: ignore[assignment]

    # Set defaults for fields that may be missing
    if "action" not in result:
        result["action"] = "move"
    if "mode" not in result:
        result["mode"] = "preserve"
    # Always set scope to "original" for mode-generated actions
    result["scope"] = "original"
    if "affects" not in result:
        result["affects"] = "shims"
    if "cleanup" not in result:
        result["cleanup"] = "auto"

    return result


def validate_action_source_exists(
    action: ModuleActionFull,
    available_modules: set[str],
    *,
    scope: ModuleActionScope | None = None,
) -> None:
    """Validate that action source exists in available modules.

    Args:
        action: Action to validate
        available_modules: Set of available module names
        scope: Optional scope for error message context

    Raises:
        ValueError: If source does not exist in available modules
    """
    source = action["source"]  # pyright: ignore[reportTypedDictNotRequiredAccess]
    if source not in available_modules:
        scope_str = f" (scope: '{scope}')" if scope else ""
        msg = (
            f"Module action source '{source}' does not exist in available modules"
            f"{scope_str}"
        )
        raise ValueError(msg)


def validate_rename_action(
    action: ModuleActionFull,
    *,
    scope: ModuleActionScope | None = None,
) -> None:
    """Validate rename action constraints.

    Rename actions can only rename the last node in the dot sequence.
    The dest must be just the new name (no dots allowed).

    Args:
        action: Rename action to validate
        scope: Optional scope for error message context

    Raises:
        ValueError: If rename action is invalid
    """
    dest = action.get("dest")
    scope_str = f" (scope: '{scope}')" if scope else ""

    if dest is None:
        msg = (
            f"Module action 'rename' requires 'dest' field, "
            f"but it is missing{scope_str}"
        )
        raise ValueError(msg)

    # Dest must not contain dots (only the new name for the last node)
    if "." in dest:
        msg = (
            f"Module action 'rename' dest must not contain dots. "
            f"Got dest='{dest}'. Use 'move' action to move modules down the tree"
            f"{scope_str}"
        )
        raise ValueError(msg)


def validate_action_dest(
    action: ModuleActionFull,
    existing_modules: set[str],
    *,
    allowed_destinations: set[str] | None = None,
    scope: ModuleActionScope | None = None,
) -> None:
    """Validate action destination (conflicts, required for move/copy, etc.).

    Args:
        action: Action to validate
        existing_modules: Set of existing module names (for conflict checking)
        allowed_destinations: Optional set of destinations that are allowed
            even if they exist in existing_modules (e.g., target package for
            mode-generated actions). If None, no special exceptions.
        scope: Optional scope for error message context

    Raises:
        ValueError: If destination is invalid
    """
    action_type = action.get("action", "move")
    dest = action.get("dest")
    scope_str = f" (scope: '{scope}')" if scope else ""

    # Delete actions must not have dest
    if action_type == "delete" and dest is not None:
        msg = (
            f"Module action 'delete' must not have 'dest' field, but got dest='{dest}'"
            f"{scope_str}"
        )
        raise ValueError(msg)
    if action_type == "delete":
        return

    # Rename actions have special validation
    if action_type == "rename":
        validate_rename_action(action, scope=scope)
        # After validating rename constraints, check if the constructed
        # destination conflicts with existing modules
        source = action["source"]  # pyright: ignore[reportTypedDictNotRequiredAccess]
        if dest is not None:
            # Construct full destination path: replace last component of source
            if "." in source:
                parent = ".".join(source.split(".")[:-1])
                full_dest = f"{parent}.{dest}"
            else:
                # Top-level module: just use dest
                full_dest = dest

            # Check for conflicts (rename acts like move - can't conflict)
            if full_dest in existing_modules and (
                allowed_destinations is None or full_dest not in allowed_destinations
            ):
                msg = (
                    f"Module action 'rename' destination '{full_dest}' "
                    f"(from source '{source}' + dest '{dest}') "
                    f"conflicts with existing module{scope_str}"
                )
                raise ValueError(msg)
        return

    # Move and copy actions require dest
    if action_type in ("move", "copy"):
        if dest is None:
            msg = (
                f"Module action '{action_type}' requires 'dest' field, "
                f"but it is missing{scope_str}"
            )
            raise ValueError(msg)

        # For move, dest must not conflict with existing modules
        # Exception: if dest is in allowed_destinations, it's allowed
        # (e.g., target package for mode-generated actions)
        # For copy, dest can conflict (it's allowed to overwrite)
        if (
            action_type == "move"
            and dest in existing_modules
            and (allowed_destinations is None or dest not in allowed_destinations)
        ):
            msg = (
                f"Module action 'move' destination '{dest}' "
                f"conflicts with existing module{scope_str}"
            )
            raise ValueError(msg)


def validate_no_circular_moves(  # noqa: C901, PLR0912
    actions: list[ModuleActionFull],
) -> None:
    """Validate no circular move operations.

    Detects direct and indirect circular move chains (e.g., A -> B, B -> A
    or A -> B, B -> C, C -> A). Includes rename actions (which act like moves).

    Args:
        actions: List of actions to validate

    Raises:
        ValueError: If circular move chain is detected
    """
    # Build a mapping of source -> dest for move and rename operations
    move_map: dict[str, str] = {}
    for action in actions:
        action_type = action.get("action", "move")
        if action_type in ("move", "rename"):
            source = action["source"]  # pyright: ignore[reportTypedDictNotRequiredAccess]
            dest = action.get("dest")
            if dest is not None:
                # For rename, construct full destination path
                if action_type == "rename":
                    if "." in source:
                        parent = ".".join(source.split(".")[:-1])
                        full_dest = f"{parent}.{dest}"
                    else:
                        full_dest = dest
                    move_map[source] = full_dest
                else:
                    move_map[source] = dest

    # Check for circular chains using DFS
    visited: set[str] = set()
    path: set[str] = set()

    def has_cycle(node: str) -> bool:
        """Check if there's a cycle starting from node."""
        if node in path:
            return True  # Found a cycle
        if node in visited:
            return False  # Already checked, no cycle from here

        visited.add(node)
        path.add(node)

        # Follow the move chain
        if node in move_map:
            next_node = move_map[node]
            if has_cycle(next_node):
                return True

        path.remove(node)
        return False

    # Check each node for cycles
    for source in move_map:
        if source not in visited and has_cycle(source):
            # Find the cycle path for error message
            cycle_path: list[str] = []
            current = source
            seen_in_cycle: set[str] = set()
            while current not in seen_in_cycle:
                seen_in_cycle.add(current)
                cycle_path.append(current)
                if current in move_map:
                    current = move_map[current]
                else:
                    break
            # Add the closing link
            if cycle_path:
                cycle_path.append(cycle_path[0])
            cycle_str = " -> ".join(cycle_path)
            msg = f"Circular move chain detected: {cycle_str}"
            raise ValueError(msg)


def validate_no_conflicting_operations(  # noqa: C901, PLR0912, PLR0915
    actions: list[ModuleActionFull],
) -> None:
    """Validate no conflicting operations (delete then move, etc.).

    Checks for conflicts like:
    - Can't delete something that's being moved/copied
    - Can't move/copy to something that's being deleted
    - Can't move/copy to something that's being moved/copied from
      (unless it's a copy, which allows overwriting)

    Args:
        actions: List of actions to validate

    Raises:
        ValueError: If conflicting operations are detected
    """
    # Collect all sources and destinations
    sources: set[str] = set()
    dests: set[str] = set()
    deleted: set[str] = set()
    moved_from: set[str] = set()
    copied_from: set[str] = set()

    for action in actions:
        source = action["source"]  # pyright: ignore[reportTypedDictNotRequiredAccess]
        action_type = action.get("action", "move")
        dest = action.get("dest")

        sources.add(source)

        if action_type == "delete":
            deleted.add(source)
        elif action_type in ("move", "rename"):
            moved_from.add(source)
            if dest is not None:
                # For rename, construct full destination path
                if action_type == "rename":
                    if "." in source:
                        parent = ".".join(source.split(".")[:-1])
                        full_dest = f"{parent}.{dest}"
                    else:
                        full_dest = dest
                    dests.add(full_dest)
                else:
                    dests.add(dest)
        elif action_type == "copy":
            copied_from.add(source)
            if dest is not None:
                dests.add(dest)

    # Check: Can't delete something that's being moved/copied
    for action in actions:
        source = action["source"]  # pyright: ignore[reportTypedDictNotRequiredAccess]
        action_type = action.get("action", "move")
        if action_type == "delete" and (source in moved_from or source in copied_from):
            msg = (
                f"Cannot delete module '{source}' because it is "
                f"being moved or copied in another action"
            )
            raise ValueError(msg)

    # Check: Can't move/copy to something that's being deleted
    for action in actions:
        action_type = action.get("action", "move")
        dest = action.get("dest")
        if dest is not None and dest in deleted:
            msg = (
                f"Cannot {action_type} to '{dest}' because it is "
                f"being deleted in another action"
            )
            raise ValueError(msg)

    # Check: Can't move to something that's being moved/copied from
    # (copy is allowed to overwrite, but move is not)
    # Exception: If a module is only a destination (not a source) in other
    # actions, it's allowed to move it (e.g., moving target package after
    # mode actions have moved things into it)
    for action in actions:
        action_type = action.get("action", "move")
        dest = action.get("dest")
        # For rename, construct full destination path
        computed_dest: str | None
        if action_type == "rename" and dest is not None:
            source = action["source"]  # pyright: ignore[reportTypedDictNotRequiredAccess]
            if "." in source:
                parent = ".".join(source.split(".")[:-1])
                computed_dest = f"{parent}.{dest}"
            else:
                computed_dest = dest
        else:
            computed_dest = dest
        # Check if dest is being moved/copied FROM (not just TO)
        # Only error if dest is a source of another action
        if (
            action_type in ("move", "rename")
            and computed_dest is not None
            and (computed_dest in moved_from or computed_dest in copied_from)
        ):
            # But allow if dest is also a destination in other actions
            # (it's being moved into, then moved from - this is valid)
            # Only error if dest is ONLY a source (not also a destination)
            # Check if dest appears as a destination in any other action
            dest_is_also_destination = False
            for other_action in actions:
                if other_action is action:
                    continue
                other_dest = other_action.get("dest")
                if other_dest is not None:
                    # For rename actions, construct full destination path
                    other_action_type = other_action.get("action", "move")
                    if other_action_type == "rename":
                        other_source = other_action["source"]  # pyright: ignore[reportTypedDictNotRequiredAccess]
                        if "." in other_source:
                            other_parent = ".".join(other_source.split(".")[:-1])
                            other_computed_dest = f"{other_parent}.{other_dest}"
                        else:
                            other_computed_dest = other_dest
                        if other_computed_dest == computed_dest:
                            dest_is_also_destination = True
                            break
                    elif other_dest == computed_dest:
                        dest_is_also_destination = True
                        break
            if not dest_is_also_destination:
                msg = (
                    f"Cannot {action_type} to '{computed_dest}' because it is being "
                    f"moved or copied from in another action"
                )
                raise ValueError(msg)


def validate_module_actions(
    actions: list[ModuleActionFull],
    original_modules: set[str],
    detected_packages: set[str],  # noqa: ARG001
    *,
    scope: ModuleActionScope | None = None,
) -> None:
    """Validate module actions upfront.

    For scope: "original" actions, validates against original module tree.
    For scope: "shim" actions, validates incrementally (call after each action).

    Args:
        actions: List of actions to validate
        original_modules: Set of original module names (for upfront validation)
        detected_packages: Set of detected package names (for context)
        scope: Optional scope filter - if provided, only validate actions
            with this scope. If None, validate all actions.

    Raises:
        ValueError: For invalid operations
    """
    # Filter by scope if provided
    filtered_actions = actions
    if scope is not None:
        filtered_actions = [
            action for action in actions if action.get("scope") == scope
        ]

    if not filtered_actions:
        return

    # Determine available modules based on scope
    # For "original" scope, use original_modules
    # For "shim" scope, this will be called incrementally with current state
    # For incremental validation, available_modules should be passed
    # as the current state. For now, we'll use original_modules as
    # a fallback, but this should be called with current state.
    # This is a design note: incremental validation should be called
    # with the current transformed module set.
    available_modules = original_modules

    # Validate each action's source exists
    for action in filtered_actions:
        action_scope = action.get("scope") or scope
        validate_action_source_exists(action, available_modules, scope=action_scope)

    # Validate no circular moves first (before dest conflicts)
    # Circular moves can cause false dest conflicts
    validate_no_circular_moves(filtered_actions)

    # Validate each action's destination
    # For mode-generated actions (scope: "original"), allow moving into
    # the target package even if it exists. Extract target packages from
    # actions that have scope: "original" and dest in existing_modules.
    allowed_destinations: set[str] | None = None
    if scope == "original" or scope is None:
        # Check if any action is moving into an existing module
        # This is allowed for mode-generated actions (target package)
        for action in filtered_actions:
            if action.get("scope") == "original":
                dest = action.get("dest")
                if dest is not None and dest in available_modules:
                    if allowed_destinations is None:
                        allowed_destinations = set()
                    allowed_destinations.add(dest)

    for action in filtered_actions:
        action_scope = action.get("scope") or scope
        validate_action_dest(
            action,
            available_modules,
            allowed_destinations=allowed_destinations,
            scope=action_scope,
        )

    # Validate no conflicting operations
    validate_no_conflicting_operations(filtered_actions)


def _transform_module_name(  # noqa: PLR0911
    module_name: str,
    source: str,
    dest: str,
    mode: ModuleActionMode,
) -> str | None:
    """Transform a single module name based on action.

    Handles preserve vs flatten modes:
    - preserve: Keep structure (apathetic_logs.utils -> grinch.utils)
    - flatten: Remove intermediate levels (apathetic_logs.utils -> grinch)

    Args:
        module_name: The module name to transform
        source: Source module path (e.g., "apathetic_logs")
        dest: Destination module path (e.g., "grinch")
        mode: Transformation mode ("preserve" or "flatten")

    Returns:
        Transformed module name, or None if module doesn't match source
    """
    # Check if module_name starts with source
    if not module_name.startswith(source):
        # Try component matching: check if all source components appear in module_name
        # (e.g., "mypkg.module" should match "mypkg.pkg1.module")
        source_parts = source.split(".")
        module_parts = module_name.split(".")
        # Check if first and last components of source match first and last of module
        min_components_for_match = 2
        if (
            len(source_parts) >= min_components_for_match
            and len(module_parts) >= min_components_for_match
            and source_parts[0] == module_parts[0]
            and source_parts[-1] == module_parts[-1]
        ):
            # Component matching: extract middle part(s) from module_name
            # For "mypkg.module" matching "mypkg.pkg1.module":
            # - source_parts = ["mypkg", "module"]
            # - module_parts = ["mypkg", "pkg1", "module"]
            # - middle_parts = ["pkg1"]
            middle_parts = module_parts[1:-1]
            if mode == "preserve":
                # Preserve structure: dest + middle + last component
                if middle_parts:
                    return f"{dest}.{'.'.join(middle_parts)}.{source_parts[-1]}"
                return f"{dest}.{source_parts[-1]}"
            # mode == "flatten"
            # Flatten: just dest (remove middle parts and last component)
            return dest
        return None

    # Exact match: source -> dest
    if module_name == source:
        return dest

    # Check if it's a submodule (must have a dot after source)
    if not module_name.startswith(f"{source}."):
        return None

    # Extract the suffix (everything after source.)
    suffix = module_name[len(source) + 1 :]

    if mode == "preserve":
        # Preserve structure: dest + suffix
        return f"{dest}.{suffix}"

    # mode == "flatten"
    # Flatten: dest + last component only
    # e.g., "apathetic_logs.utils.text" -> "grinch.text"
    # e.g., "apathetic_logs.utils.schema.validator" -> "grinch.validator"
    if "." in suffix:
        # Multiple levels: take only the last component
        last_component = suffix.split(".")[-1]
        return f"{dest}.{last_component}"

    # Single level: dest + suffix
    return f"{dest}.{suffix}"


def _apply_move_action(
    module_names: list[str],
    action: ModuleActionFull,
) -> list[str]:
    """Apply move action with preserve or flatten mode.

    Moves modules from source to dest, removing source modules.
    Handles preserve vs flatten modes.

    Args:
        module_names: List of module names to transform
        action: Move action with source, dest, and mode

    Returns:
        Transformed list of module names
    """
    source = action["source"]  # pyright: ignore[reportTypedDictNotRequiredAccess]
    dest = action.get("dest")
    if dest is None:
        msg = "Move action requires 'dest' field"
        raise ValueError(msg)

    mode = action.get("mode", "preserve")
    if mode not in ("preserve", "flatten"):
        msg = f"Invalid mode '{mode}', must be 'preserve' or 'flatten'"
        raise ValueError(msg)

    result: list[str] = []
    for module_name in module_names:
        transformed = _transform_module_name(module_name, source, dest, mode)
        if transformed is not None:
            # Replace source module with transformed name
            result.append(transformed)
        else:
            # Keep modules that don't match source
            result.append(module_name)

    return result


def _apply_copy_action(
    module_names: list[str],
    action: ModuleActionFull,
) -> list[str]:
    """Apply copy action (source remains, also appears at dest).

    Copies modules from source to dest, keeping source modules.
    Handles preserve vs flatten modes.

    Args:
        module_names: List of module names to transform
        action: Copy action with source, dest, and mode

    Returns:
        Transformed list of module names (includes both original and copied)
    """
    source = action["source"]  # pyright: ignore[reportTypedDictNotRequiredAccess]
    dest = action.get("dest")
    if dest is None:
        msg = "Copy action requires 'dest' field"
        raise ValueError(msg)

    mode = action.get("mode", "preserve")
    if mode not in ("preserve", "flatten"):
        msg = f"Invalid mode '{mode}', must be 'preserve' or 'flatten'"
        raise ValueError(msg)

    result: list[str] = []
    for module_name in module_names:
        # Always keep the original
        result.append(module_name)

        # Also add transformed version if it matches source
        transformed = _transform_module_name(module_name, source, dest, mode)
        if transformed is not None:
            result.append(transformed)

    return result


def _apply_rename_action(
    module_names: list[str],
    action: ModuleActionFull,
) -> list[str]:
    """Apply rename action (rename only the last node in the dot sequence).

    Renames the last component of the source module path. The dest field
    contains only the new name (no dots). For example:
    - source: "foo.bar.baz", dest: "new_name" -> "foo.bar.new_name"
    - source: "foo", dest: "new_name" -> "new_name"

    This is essentially a move action with validation that only allows
    renaming the last node.

    Args:
        module_names: List of module names to transform
        action: Rename action with source and dest (new name only)

    Returns:
        Transformed list of module names
    """
    source = action["source"]  # pyright: ignore[reportTypedDictNotRequiredAccess]
    dest = action.get("dest")
    if dest is None:
        msg = "Rename action requires 'dest' field"
        raise ValueError(msg)

    # Construct full destination path: replace last component of source
    if "." in source:
        parent = ".".join(source.split(".")[:-1])
        full_dest = f"{parent}.{dest}"
    else:
        # Top-level module: just use dest
        full_dest = dest

    # Rename acts like a move with preserve mode (keep structure)
    # We use _transform_module_name with preserve mode to handle submodules
    result: list[str] = []
    for module_name in module_names:
        transformed = _transform_module_name(module_name, source, full_dest, "preserve")
        if transformed is not None:
            # Replace source module with transformed name
            result.append(transformed)
        else:
            # Keep modules that don't match source
            result.append(module_name)

    return result


def _apply_delete_action(
    module_names: list[str],
    action: ModuleActionFull,
) -> list[str]:
    """Apply delete action (remove module and all submodules).

    Removes the source module and all modules that start with source.

    Args:
        module_names: List of module names to transform
        action: Delete action with source

    Returns:
        Filtered list of module names (deleted modules removed)
    """
    source = action["source"]  # pyright: ignore[reportTypedDictNotRequiredAccess]

    result: list[str] = []
    for module_name in module_names:
        # Keep modules that don't match source
        # Check exact match, starts with source., or source appears as component
        if module_name == source:
            # Exact match: delete it
            continue
        if module_name.startswith(f"{source}."):
            # Submodule: delete it
            continue
        # Check if source appears as a component in module_name
        # (e.g., "mypkg.pkg1" contains "pkg1" as a component)
        if source in module_name.split("."):
            # Source is a component: delete it
            continue
        # Keep this module
        result.append(module_name)

    return result


def apply_single_action(
    module_names: list[str],
    action: ModuleActionFull,
    detected_packages: set[str],  # noqa: ARG001
) -> list[str]:
    """Apply a single action to module names.

    Routes to the appropriate action handler based on action type.

    Args:
        module_names: List of module names to transform
        action: Action to apply
        detected_packages: Set of detected package names (for context)

    Returns:
        Transformed list of module names

    Raises:
        ValueError: If action type is invalid or missing required fields
    """
    action_type = action.get("action", "move")

    if action_type == "move":
        return _apply_move_action(module_names, action)
    if action_type == "copy":
        return _apply_copy_action(module_names, action)
    if action_type == "rename":
        return _apply_rename_action(module_names, action)
    if action_type == "delete":
        return _apply_delete_action(module_names, action)
    if action_type == "none":
        # No-op action
        return module_names

    msg = (
        f"Invalid action type '{action_type}', must be "
        "'move', 'copy', 'delete', 'rename', or 'none'"
    )
    raise ValueError(msg)


def apply_module_actions(
    module_names: list[str],
    actions: list[ModuleActionFull],
    detected_packages: set[str],
) -> list[str]:
    """Apply module actions to transform module names.

    Applies all actions in sequence to transform the module names list.
    Each action is applied to the result of the previous action.

    Args:
        module_names: Initial list of module names
        actions: List of actions to apply in order
        detected_packages: Set of detected package names (for context)

    Returns:
        Transformed list of module names

    Raises:
        ValueError: For invalid operations
    """
    result = list(module_names)

    # Apply each action in sequence
    for action in actions:
        result = apply_single_action(result, action, detected_packages)

    return result


def _generate_force_actions(  # noqa: PLR0912, C901
    detected_packages: set[str],
    package_name: str,
    mode: ModuleActionMode,
    *,
    module_names: list[str] | None = None,
    source_bases: list[str] | None = None,
) -> list[ModuleActionFull]:
    """Generate actions for force/force_flat modes.

    For "preserve" mode: Only generates actions for top-level root packages.
    For "flatten" mode: Generates actions for all first components of multi-level
    module names to flatten all intermediate levels.

    Args:
        detected_packages: Set of all detected package names
        package_name: Target package name (excluded from actions)
        mode: "preserve" or "flatten"
        module_names: Optional list of module names (required for flatten mode
            to identify all first components that need flattening)
        source_bases: Optional list of source base directories for detecting
            nested packages

    Returns:
        List of actions for packages/modules to transform
    """
    actions: list[ModuleActionFull] = []

    if mode == "flatten" and module_names is not None:
        # For flatten mode, generate actions for all first components of
        # multi-level module names to flatten all intermediate levels
        first_components: set[str] = set()
        for mod_name in module_names:
            if "." in mod_name:
                first_part = mod_name.split(".", 1)[0]
                if first_part != package_name:
                    first_components.add(first_part)

        # Also include detected root packages that aren't package_name
        root_packages = {pkg for pkg in detected_packages if "." not in pkg}
        for pkg in root_packages:
            if pkg != package_name:
                first_components.add(pkg)

        for component in sorted(first_components):
            component_action: ModuleActionFull = {
                "source": component,
                "dest": package_name,
                "mode": "flatten",
            }
            actions.append(set_mode_generated_action_defaults(component_action))
    else:
        # For preserve mode, only generate actions for top-level root packages
        root_packages = {pkg for pkg in detected_packages if "." not in pkg}
        # Filter to only top-level root packages (not nested under other packages)
        top_level_packages: set[str] = set()
        logger = getAppLogger()
        logger.trace(
            "[FORCE_ACTIONS] preserve mode: detected_packages=%s, "
            "root_packages=%s, source_bases=%s, module_names=%s",
            sorted(detected_packages),
            sorted(root_packages),
            source_bases,
            module_names[:5] if module_names else None,  # First 5 for brevity
        )
        for pkg in root_packages:
            if pkg == package_name:
                continue
            # Check if this package is nested under any other detected package
            is_nested = False
            for other_pkg in detected_packages:
                # Check if pkg is nested under other_pkg
                # e.g., if other_pkg="pkg1" and pkg="sub", check if "pkg1.sub"
                # exists
                if other_pkg not in (pkg, package_name):
                    # Check if "other_pkg.pkg" is in detected_packages
                    if f"{other_pkg}.{pkg}" in detected_packages:
                        is_nested = True
                        break
                    # Check if any module name starts with "other_pkg.pkg."
                    if any(
                        mod.startswith(f"{other_pkg}.{pkg}.")
                        for mod in detected_packages
                    ):
                        is_nested = True
                        break
                    # Check if other_pkg is in source_bases and pkg appears in
                    # module_names, suggesting pkg is nested under other_pkg
                    # This handles cases where pkg1 is in source_bases and contains
                    # sub, but module names are "sub.mod1" not "pkg1.sub.mod1"
                    if source_bases and module_names:
                        # Check if other_pkg appears as a directory name in source_bases
                        other_pkg_in_bases = any(
                            Path(base).name == other_pkg
                            or base.endswith((f"/{other_pkg}", f"\\{other_pkg}"))
                            for base in source_bases
                        )
                        if other_pkg_in_bases:
                            # Check if pkg appears in module_names as a component
                            # under other_pkg (e.g., other_pkg.pkg.X or other_pkg.pkg)
                            # This indicates pkg is nested under other_pkg
                            pkg_nested_under_other = any(
                                mod_name.startswith(f"{other_pkg}.{pkg}.")
                                or mod_name == f"{other_pkg}.{pkg}"
                                for mod_name in module_names
                            )
                            if pkg_nested_under_other:
                                # other_pkg is in source_bases and pkg appears nested
                                # under other_pkg in module_names
                                logger.trace(
                                    "[FORCE_ACTIONS] Detected %s as nested under %s "
                                    "(found %s.%s in module_names)",
                                    pkg,
                                    other_pkg,
                                    other_pkg,
                                    pkg,
                                )
                                is_nested = True
                                break
                            # Also check if pkg appears as standalone in module_names
                            # AND other_pkg is a parent directory in source_bases
                            # (this handles cases where module names are "pkg.X" not
                            # "other_pkg.pkg.X" because derive_module_name used
                            # other_pkg as module_base)
                            # BUT: Only if other_pkg doesn't also appear standalone
                            # (to avoid false positives when both are top-level)
                            pkg_standalone_in_names = any(
                                mod_name == pkg or mod_name.startswith(f"{pkg}.")
                                for mod_name in module_names
                            )
                            other_pkg_standalone_in_names = any(
                                mod_name == other_pkg
                                or mod_name.startswith(f"{other_pkg}.")
                                for mod_name in module_names
                            )
                            # Only consider pkg nested if:
                            # 1. pkg appears standalone in module_names
                            # 2. other_pkg is in source_bases
                            # 3. other_pkg does NOT also appear standalone
                            #    (if both appear standalone, they're siblings)
                            if (
                                pkg_standalone_in_names
                                and not other_pkg_standalone_in_names
                            ):
                                logger.trace(
                                    "[FORCE_ACTIONS] Detected %s as nested under %s "
                                    "(other_pkg in source_bases, pkg standalone "
                                    "but other_pkg isn't)",
                                    pkg,
                                    other_pkg,
                                )
                                is_nested = True
                                break
            if not is_nested:
                top_level_packages.add(pkg)

        for pkg in sorted(top_level_packages):
            action: ModuleActionFull = {
                "source": pkg,
                "dest": package_name,
                "mode": mode,
            }
            actions.append(set_mode_generated_action_defaults(action))

    return actions


def _generate_unify_actions(
    detected_packages: set[str],
    package_name: str,
) -> list[ModuleActionFull]:
    """Generate actions for unify/unify_preserve modes.

    Args:
        detected_packages: Set of all detected package names
        package_name: Target package name (excluded from actions)

    Returns:
        List of actions for all packages
    """
    actions: list[ModuleActionFull] = []
    for pkg in sorted(detected_packages):
        if pkg != package_name:
            action: ModuleActionFull = {
                "source": pkg,
                "dest": f"{package_name}.{pkg}",
                "mode": "preserve",
            }
            actions.append(set_mode_generated_action_defaults(action))
    return actions


def generate_actions_from_mode(
    module_mode: str,
    detected_packages: set[str],
    package_name: str,
    *,
    module_names: list[str] | None = None,
    source_bases: list[str] | None = None,
) -> list[ModuleActionFull]:
    """Generate module_actions equivalent to a module_mode.

    Converts module_mode presets into explicit actions that are prepended to
    user-specified actions. Returns list of actions that would produce the
    same result as the mode.

    All generated actions have scope: "original".

    Args:
        module_mode: Mode value ("force", "force_flat", "unify", "multi", etc.)
        detected_packages: Set of all detected package names
        package_name: Target package name (excluded from actions)
        module_names: Optional list of module names (required for flatten mode
            to identify all first components that need flattening)
        source_bases: Optional list of source base directories for detecting
            nested packages

    Returns:
        List of actions equivalent to the mode

    Raises:
        ValueError: For invalid mode values
    """
    if module_mode == "force":
        return _generate_force_actions(
            detected_packages,
            package_name,
            "preserve",
            module_names=module_names,
            source_bases=source_bases,
        )

    if module_mode == "force_flat":
        return _generate_force_actions(
            detected_packages,
            package_name,
            "flatten",
            module_names=module_names,
            source_bases=source_bases,
        )

    if module_mode in ("unify", "unify_preserve"):
        return _generate_unify_actions(detected_packages, package_name)

    if module_mode in ("multi", "none", "flat"):
        # multi: no actions needed (default behavior)
        # none: no shims (handled separately via shim setting)
        # flat: cannot be expressed as actions (requires file-level detection)
        return []

    msg = (
        f"Invalid module_mode: {module_mode!r}. "
        f"Must be one of: 'none', 'multi', 'force', 'force_flat', "
        f"'unify', 'unify_preserve', 'flat'"
    )
    raise ValueError(msg)


def separate_actions_by_affects(
    actions: list[ModuleActionFull],
) -> tuple[list[ModuleActionFull], list[ModuleActionFull], list[ModuleActionFull]]:
    """Separate actions by affects value.

    Args:
        actions: List of actions to separate

    Returns:
        Tuple of (shims_only_actions, stitching_only_actions, both_actions)
    """
    shims_only: list[ModuleActionFull] = []
    stitching_only: list[ModuleActionFull] = []
    both: list[ModuleActionFull] = []

    for action in actions:
        affects = action.get("affects", "shims")
        if affects == "shims":
            shims_only.append(action)
        elif affects == "stitching":
            stitching_only.append(action)
        elif affects == "both":
            both.append(action)
        else:
            # Default to shims for backward compatibility
            shims_only.append(action)

    return shims_only, stitching_only, both


def get_deleted_modules_from_actions(
    actions: list[ModuleActionFull],
    initial_modules: list[str],
    detected_packages: set[str],  # noqa: ARG001
) -> set[str]:
    """Get set of modules that are deleted by actions.

    Applies delete actions to determine which modules are removed.

    Args:
        actions: List of actions to apply
        initial_modules: Initial list of module names
        detected_packages: Set of detected package names (for context)

    Returns:
        Set of module names that are deleted
    """
    # Start with all initial modules
    current_modules = set(initial_modules)

    # Apply delete actions to track what gets deleted
    for action in actions:
        action_type = action.get("action", "move")
        if action_type == "delete":
            source = action["source"]  # pyright: ignore[reportTypedDictNotRequiredAccess]
            # Remove source and all submodules
            to_remove: set[str] = set()
            for mod in current_modules:
                if mod == source or mod.startswith(f"{source}."):
                    to_remove.add(mod)
            current_modules -= to_remove

    # Return the difference (what was deleted)
    initial_set = set(initial_modules)
    return initial_set - current_modules


def check_shim_stitching_mismatches(
    shim_modules: set[str],
    stitched_modules: set[str],
    actions: list[ModuleActionFull],
) -> list[tuple[ModuleActionFull, set[str]]]:
    """Check for shims pointing to modules deleted from stitching.

    Args:
        shim_modules: Set of module names that have shims
        stitched_modules: Set of module names that are in stitched code
        actions: List of actions that were applied

    Returns:
        List of tuples (action, broken_shims) where broken_shims is the set
        of shim module names that point to deleted modules
    """
    mismatches: list[tuple[ModuleActionFull, set[str]]] = []

    # Find modules that have shims but are not in stitched code
    broken_shims = shim_modules - stitched_modules

    if not broken_shims:
        return mismatches

    # For each action, check if it could have caused the mismatch
    # (i.e., if it deleted from stitching but not from shims)
    for action in actions:
        affects = action.get("affects", "shims")
        action_type = action.get("action", "move")

        # Only actions that affect stitching (but not shims) can cause mismatches
        if affects in ("stitching", "both") and action_type == "delete":
            source = action["source"]  # pyright: ignore[reportTypedDictNotRequiredAccess]
            # Check if any broken shims match this action's source
            # broken_shim is a full module path (e.g., "mypkg.pkg1.module"),
            # source is a package/module name (e.g., "pkg1")
            # We need to check if the broken shim belongs to the deleted package
            action_broken_shims: set[str] = set()
            for broken_shim in broken_shims:
                # Check if broken shim matches source exactly
                # Also check if source appears as a path component in broken_shim
                # (e.g., "mypkg.pkg1.module" contains "pkg1" as a component)
                if (
                    broken_shim == source
                    or broken_shim.endswith(f".{source}")
                    or f".{source}." in broken_shim
                    or broken_shim.startswith(f"{source}.")
                    or source in broken_shim.split(".")
                ):
                    action_broken_shims.add(broken_shim)

            if action_broken_shims:
                mismatches.append((action, action_broken_shims))

    return mismatches


def apply_cleanup_behavior(
    mismatches: list[tuple[ModuleActionFull, set[str]]],
    shim_modules: set[str],
) -> tuple[set[str], list[str]]:
    """Apply cleanup behavior for shim-stitching mismatches.

    Args:
        mismatches: List of tuples (action, broken_shims) from
            check_shim_stitching_mismatches
        shim_modules: Set of all shim module names (will be modified)

    Returns:
        Tuple of (updated_shim_modules, warnings) where warnings is a list
        of warning messages

    Raises:
        ValueError: If cleanup: "error" and mismatches exist
    """
    logger = getAppLogger()
    warnings: list[str] = []
    shims_to_remove: set[str] = set()

    for action, broken_shims in mismatches:
        cleanup = action.get("cleanup", "auto")
        source = action["source"]  # pyright: ignore[reportTypedDictNotRequiredAccess]

        if cleanup == "error":
            # Raise error with clear message
            broken_list = sorted(broken_shims)
            affects_val = action.get("affects", "shims")
            msg = (
                f"Module action on '{source}' with affects='{affects_val}' "
                f"and cleanup='error' created broken shims pointing to "
                f"deleted modules: {', '.join(broken_list)}"
            )
            raise ValueError(msg)

        if cleanup == "auto":
            # Auto-delete broken shims
            shims_to_remove.update(broken_shims)
            if broken_shims:
                broken_list = sorted(broken_shims)
                warning_msg = (
                    f"Auto-deleting broken shims for action on '{source}': "
                    f"{', '.join(broken_list)}"
                )
                warnings.append(warning_msg)
                logger.warning(warning_msg)

        elif cleanup == "ignore":
            # Keep broken shims (no action)
            pass

    # Remove broken shims
    updated_shims = shim_modules - shims_to_remove

    return updated_shims, warnings


# === serger.utils.__init__ ===
# src/serger/utils/__init__.py


__all__ = [  # noqa: RUF022
    # utils_installed_packages
    "discover_installed_packages_roots",
    # utils_matching
    "is_excluded",
    # utils_modules
    "derive_module_name",
    # utils_paths
    "shorten_path_for_display",
    "shorten_paths_for_display",
    # utils_types
    "make_includeresolved",
    "make_pathresolved",
]


# === serger.config.config_resolve ===
# src/serger/config/config_resolve.py


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #


@dataclass
class PyprojectMetadata:
    """Metadata extracted from pyproject.toml."""

    name: str = ""
    version: str = ""
    description: str = ""
    license_text: str = ""  # Combined license text
    license_files: list[str] | None = None  # Additional license files (glob patterns)
    authors: str = ""

    def has_any(self) -> bool:
        """Check if any metadata was found."""
        return bool(
            self.name
            or self.version
            or self.description
            or self.license_text
            or self.authors
        )


def _extract_authors_from_project(project: dict[str, Any]) -> str:
    """Extract authors from project dict and format as string.

    Args:
        project: Project section from pyproject.toml

    Returns:
        Formatted authors string (empty if no authors found)
    """
    authors_text = ""
    authors_val = project.get("authors", [])
    if isinstance(authors_val, list) and authors_val:
        author_parts: list[str] = []
        for author in authors_val:  # pyright: ignore[reportUnknownVariableType]
            if isinstance(author, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
                author_name = author.get("name", "")  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]
                author_email = author.get("email", "")  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]
                if isinstance(author_name, str) and author_name:
                    if isinstance(author_email, str) and author_email:
                        author_parts.append(f"{author_name} <{author_email}>")
                    else:
                        author_parts.append(author_name)
        if author_parts:
            authors_text = ", ".join(author_parts)
    return authors_text


def _resolve_single_license_pattern(
    pattern_str: str,
    base_dir: Path,
) -> list[Path]:
    """Resolve a single license pattern to list of file paths.

    Args:
        pattern_str: Single file/glob pattern
        base_dir: Base directory for resolving relative paths and globs

    Returns:
        List of resolved file paths (empty if no matches)
    """
    logger = getAppLogger()
    if Path(pattern_str).is_absolute():
        # Absolute path - use as-is but resolve
        pattern_path = Path(pattern_str).resolve()
        if pattern_path.is_file():
            return [pattern_path]
        if pattern_path.is_dir():
            # Directory - skip (only files)
            logger.warning(
                "License pattern %r resolved to directory, skipping",
                pattern_str,
            )
        return []
    if has_glob_chars(pattern_str):
        # Glob pattern - resolve relative to base_dir
        all_matches = list(base_dir.glob(pattern_str))
        return [p.resolve() for p in all_matches if p.is_file()]
    # Literal file path - resolve relative to base_dir
    file_path = (base_dir / pattern_str).resolve()
    if file_path.exists() and file_path.is_file():
        return [file_path]
    return []


def _check_duplicate_license_files(
    pattern_to_files: dict[str, list[Path]],
) -> None:
    """Check for and log duplicate license files matched by multiple patterns.

    Args:
        pattern_to_files: Mapping of patterns to their matched files
    """
    logger = getAppLogger()
    # Build reverse mapping: file -> patterns that matched it
    file_to_patterns: dict[Path, list[str]] = {}
    for pattern_str, files in pattern_to_files.items():
        for file_path in files:
            if file_path not in file_to_patterns:
                file_to_patterns[file_path] = []
            file_to_patterns[file_path].append(pattern_str)

    # Find duplicates
    duplicates = {
        file_path: pattern_list
        for file_path, pattern_list in file_to_patterns.items()
        if len(pattern_list) > 1
    }
    if duplicates:
        for file_path, pattern_list in sorted(duplicates.items()):
            logger.warning(
                "License file %s matched by multiple patterns: %s. Using file once.",
                file_path,
                ", ".join(sorted(pattern_list)),
            )


def _read_license_files(matched_files: set[Path]) -> list[str]:
    """Read contents of all matched license files.

    Args:
        matched_files: Set of file paths to read

    Returns:
        List of file contents (empty strings for failed reads)
    """
    logger = getAppLogger()
    text_parts: list[str] = []
    for file_path in sorted(matched_files):
        try:
            content = file_path.read_text(encoding="utf-8")
            text_parts.append(content)
        except (OSError, UnicodeDecodeError) as e:  # noqa: PERF203
            # PERF203: try/except in loop is intentional - we need to handle
            # errors per file and continue processing other files
            logger.warning(
                "Failed to read license file %s: %s. Skipping file.",
                file_path,
                e,
            )
    return text_parts


def _handle_missing_license_patterns(
    patterns: list[str],
    pattern_to_files: dict[str, list[Path]],
    base_dir: Path,
) -> list[str]:
    """Handle missing license patterns and return warning messages.

    Args:
        patterns: Original list of patterns
        pattern_to_files: Mapping of patterns to their matched files
        base_dir: Base directory for logging

    Returns:
        List of warning messages for missing patterns
    """
    logger = getAppLogger()
    missing_patterns = [
        pattern_str
        for pattern_str in patterns
        if pattern_str not in pattern_to_files or not pattern_to_files[pattern_str]
    ]

    if not missing_patterns:
        return []

    warning_messages: list[str] = []
    for pattern_str in sorted(missing_patterns):
        logger.warning(
            "License file/pattern not found: %s (resolved from %s)",
            pattern_str,
            base_dir,
        )
        warning_messages.append(
            f"See {pattern_str} if distributed alongside this file "
            "for additional terms."
        )
    return warning_messages


def _resolve_license_file_or_pattern(
    pattern: str | list[str],
    base_dir: Path,
) -> str:
    """Resolve license file(s) or glob pattern(s) to combined text.

    Resolves glob patterns to actual files (only files, not directories),
    deduplicates if same file matched multiple times, follows symlinks,
    and reads file contents (UTF-8 encoding).

    Args:
        pattern: Single file/glob pattern or list of file/glob patterns
        base_dir: Base directory for resolving relative paths and globs

    Returns:
        Combined text from all matched files, or warning message for missing
        files/patterns
    """
    patterns: list[str] = [pattern] if isinstance(pattern, str) else pattern

    if not patterns:
        return ""

    # Collect all matched files (deduplicated)
    matched_files: set[Path] = set()
    pattern_to_files: dict[str, list[Path]] = {}

    for pattern_str in patterns:
        files = _resolve_single_license_pattern(pattern_str, base_dir)
        matched_files.update(files)
        pattern_to_files[pattern_str] = files

    # Check for duplicates
    _check_duplicate_license_files(pattern_to_files)

    # Read all matched files
    text_parts = _read_license_files(matched_files)

    # Handle missing patterns/files
    warning_messages = _handle_missing_license_patterns(
        patterns, pattern_to_files, base_dir
    )
    text_parts.extend(warning_messages)

    return "\n\n".join(text_parts) if text_parts else ""


def _resolve_license_files_patterns(  # pyright: ignore[reportUnusedFunction]
    patterns: list[str],
    base_dir: Path,
) -> str:
    """Resolve list of license file glob patterns to combined text.

    Resolves glob patterns to actual files (only files, not directories),
    deduplicates if same file matched multiple times, follows symlinks,
    and reads file contents (UTF-8 encoding).

    Args:
        patterns: List of glob patterns for license files
        base_dir: Base directory for resolving relative paths and globs

    Returns:
        Combined text from all matched files (to be appended to license text)

    Note: This function will be used in Phase 3 and Phase 4 of license
    support implementation.
    """
    return _resolve_license_file_or_pattern(patterns, base_dir)


def _resolve_license_file_value(file_val: Any, base_dir: Path) -> str:
    """Resolve license file value (str or list[str]) to text.

    Args:
        file_val: File value from license dict (str or list[str])
        base_dir: Base directory for resolving relative paths and globs

    Returns:
        Combined text from resolved files (empty string if none found)
    """
    if file_val is None:
        return ""

    if isinstance(file_val, str):
        return _resolve_license_file_or_pattern(file_val, base_dir)

    if isinstance(file_val, list):
        # Convert to list of strings
        pattern_list: list[str] = []
        for item in file_val:  # pyright: ignore[reportUnknownVariableType]
            if isinstance(item, str):
                pattern_list.append(item)
            elif item is not None:
                pattern_list.append(str(item))  # pyright: ignore[reportUnknownArgumentType]
        if pattern_list:
            return _resolve_license_file_or_pattern(pattern_list, base_dir)

    return ""


def _extract_license_from_project(license_val: Any, base_dir: Path) -> str:
    """Extract license text from project license field.

    Handles string format and dict format with file/text/expression keys.
    Priority: text > expression > file.

    Args:
        license_val: License value from project dict (str or dict)
        base_dir: Base directory for resolving relative paths and globs

    Returns:
        Combined license text (empty string if no license found)
    """
    if isinstance(license_val, str):
        # String format: Store as-is
        return license_val

    if not isinstance(license_val, dict):
        return ""

    # Dict format: Handle text, expression, and file keys
    # Priority: text > expression > file
    text_parts: list[str] = []

    # Check for text key (highest priority)
    if "text" in license_val:
        text_val = license_val.get("text")  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]
        if isinstance(text_val, str) and text_val:
            text_parts.append(text_val)
    # Check for expression key (alias for text, second priority)
    elif "expression" in license_val:
        expr_val = license_val.get("expression")  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]
        if isinstance(expr_val, str) and expr_val:
            text_parts.append(expr_val)

    # Check for file key (lowest priority, only if text/expression not present)
    if not text_parts and "file" in license_val:
        file_val = license_val.get("file")  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]
        resolved_text = _resolve_license_file_value(file_val, base_dir)
        if resolved_text:
            text_parts.append(resolved_text)

    # Combine all text parts
    if text_parts:
        return "\n\n".join(text_parts)

    return ""


def _extract_license_files_from_project(
    license_files_val: Any,
) -> list[str] | None:
    """Extract license-files field from project dict.

    Args:
        license_files_val: License-files value from project dict

    Returns:
        List of license file patterns, or None if not present
    """
    if license_files_val is None:
        return None

    if isinstance(license_files_val, list):
        # Convert to list of strings
        license_files: list[str] = []
        for item in license_files_val:  # pyright: ignore[reportUnknownVariableType]
            if isinstance(item, str):
                license_files.append(item)
            elif item is not None:
                license_files.append(str(item))  # pyright: ignore[reportUnknownArgumentType]
        return license_files if license_files else None

    if isinstance(license_files_val, str):
        # Single string pattern
        return [license_files_val]

    return None


def _resolve_license_dict_value(
    license_dict: dict[str, str | list[str]], base_dir: Path
) -> str:
    """Resolve license dict to text using priority: text > expression > file.

    Args:
        license_dict: License dict with text/expression/file keys
        base_dir: Base directory for resolving relative paths and globs

    Returns:
        Resolved license text (empty string if none found)
    """
    # Check for text key (highest priority)
    if "text" in license_dict:
        text_val = license_dict.get("text")  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]
        if isinstance(text_val, str) and text_val:
            return text_val
    # Check for expression key (alias for text, second priority)
    if "expression" in license_dict:
        expr_val = license_dict.get("expression")  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]
        if isinstance(expr_val, str) and expr_val:
            return expr_val
    # Check for file key (lowest priority, only if text/expression not present)
    if "file" in license_dict:
        file_val = license_dict.get("file")  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]
        return _resolve_license_file_value(file_val, base_dir)
    return ""


def _resolve_license_field(
    license_val: str | dict[str, str | list[str]] | None,
    license_files_val: list[str] | None,
    base_dir: Path,
) -> str:
    """Resolve license field (string or dict) and license_files to combined text.

    Processing order: license field first, then license_files.

    Args:
        license_val: License value from config (str or dict)
        license_files_val: License files patterns from config (list of glob patterns)
        base_dir: Base directory for resolving relative paths and globs

    Returns:
        Combined license text (always non-empty, uses fallback if needed)
    """
    text_parts: list[str] = []

    # Process license field first
    if license_val is not None:
        if isinstance(license_val, str):
            # String format: Store as-is
            if license_val:
                text_parts.append(license_val)
        else:
            # Dict format: Resolve using priority
            # pyright: ignore[reportUnnecessaryIsInstance] - needed for type narrowing
            resolved_text = _resolve_license_dict_value(license_val, base_dir)
            if resolved_text:
                text_parts.append(resolved_text)

    # Then process license_files field (append to license result)
    if license_files_val:
        resolved_files_text = _resolve_license_files_patterns(
            license_files_val, base_dir
        )
        if resolved_files_text:
            text_parts.append(resolved_files_text)

    # Combine all text parts
    combined_text = "\n\n".join(text_parts) if text_parts else ""

    # Final fallback: If empty, use DEFAULT_LICENSE_FALLBACK
    if not combined_text:
        combined_text = DEFAULT_LICENSE_FALLBACK

    return combined_text


def extract_pyproject_metadata(
    pyproject_path: Path, *, required: bool = False
) -> PyprojectMetadata | None:
    """Extract metadata from pyproject.toml file.

    Extracts name, version, description, license, and authors from the
    [project] section. Uses load_toml() utility which supports Python 3.10
    and 3.11+.

    Args:
        pyproject_path: Path to pyproject.toml file
        required: If True, raise RuntimeError when tomli is missing on
                  Python 3.10. If False, return None when unavailable.

    Returns:
        PyprojectMetadata with extracted fields (empty strings if not found),
        or None if unavailable

    Raises:
        RuntimeError: If required=True and TOML parsing is unavailable
    """
    if not pyproject_path.exists():
        return PyprojectMetadata()

    try:
        data = load_toml(pyproject_path, required=required)
        if data is None:
            # TOML parsing unavailable and not required
            return None
        project = data.get("project", {})
    except (FileNotFoundError, ValueError):
        # If parsing fails, return empty metadata
        return PyprojectMetadata()

    # Extract fields from parsed TOML
    name = project.get("name", "")
    version = project.get("version", "")
    description = project.get("description", "")

    # Handle license (can be string or dict with file/text/expression keys)
    license_val = project.get("license")
    license_text = _extract_license_from_project(license_val, pyproject_path.parent)

    # Extract license-files field (list of glob patterns)
    license_files_val = project.get("license-files")
    license_files = _extract_license_files_from_project(license_files_val)

    # Extract authors
    authors_text = _extract_authors_from_project(project)

    return PyprojectMetadata(
        name=name if isinstance(name, str) else "",
        version=version if isinstance(version, str) else "",
        description=description if isinstance(description, str) else "",
        license_text=license_text,
        license_files=license_files,
        authors=authors_text,
    )


def _is_configless_build(root_cfg: RootConfig | None) -> bool:
    """Check if this is a configless build (no config file).

    Configless builds are detected by checking if root_cfg is minimal:
    has no include/exclude/out/package/order fields (set via CLI).

    Args:
        root_cfg: Root config (may be None)

    Returns:
        True if this is a configless build, False otherwise
    """
    if root_cfg is None:
        return True
    # Check if root_cfg is minimal (empty or only has minimal fields)
    # This indicates a configless build created in cli.py
    root_keys = set(root_cfg.keys())
    # Configless builds have no include/exclude/out fields (set via CLI)
    has_build_fields = any(
        key in root_keys for key in ("include", "exclude", "out", "package", "order")
    )
    return not has_build_fields


def _should_use_pyproject_metadata(
    build_cfg: RootConfig,
    root_cfg: RootConfig | None,
) -> bool:
    """Determine if pyproject.toml metadata should be extracted for this build.

    Pyproject.toml metadata is used by default (DEFAULT_USE_PYPROJECT_METADATA) unless
    explicitly disabled. Explicit enablement (use_pyproject_metadata=True or
    pyproject_path set) always takes precedence and enables it even if it would
    otherwise be disabled.

    Note: Package name is always extracted from pyproject.toml (if available) for
    resolution purposes, regardless of this setting. This setting only controls
    extraction of other metadata (display_name, description, authors, license, version).

    Args:
        build_cfg: Build config
        root_cfg: Root config (may be None)

    Returns:
        True if pyproject.toml should be used, False otherwise
    """
    root_use_pyproject_metadata = (root_cfg or {}).get("use_pyproject_metadata")
    root_pyproject_path = (root_cfg or {}).get("pyproject_path")
    build_use_pyproject_metadata = build_cfg.get("use_pyproject_metadata")
    build_pyproject_path = build_cfg.get("pyproject_path")

    # Check if this is a configless build
    is_configless = _is_configless_build(root_cfg)

    # Build-level explicit disablement always takes precedence
    if build_use_pyproject_metadata is False:
        return False

    # Root-level explicit disablement takes precedence unless build overrides
    # (build-level pyproject_path is considered an override)
    if root_use_pyproject_metadata is False and build_pyproject_path is None:
        return False

    # For configless builds, use DEFAULT_USE_PYPROJECT_METADATA (unless disabled above)
    if is_configless:
        return DEFAULT_USE_PYPROJECT_METADATA

    # For non-configless builds, also use DEFAULT_USE_PYPROJECT_METADATA unless
    # explicitly disabled (but allow explicit enablement to override)
    if (
        root_use_pyproject_metadata is True
        or root_pyproject_path is not None
        or build_use_pyproject_metadata is True
        or build_pyproject_path is not None
    ):
        return True

    # Default to DEFAULT_USE_PYPROJECT_METADATA for non-configless builds too
    return DEFAULT_USE_PYPROJECT_METADATA


def _resolve_pyproject_path(
    build_cfg: RootConfig,
    root_cfg: RootConfig | None,
    config_dir: Path,
) -> Path:
    """Resolve the path to pyproject.toml file.

    Args:
        build_cfg: Build config
        root_cfg: Root config (may be None)
        config_dir: Config directory for path resolution

    Returns:
        Resolved path to pyproject.toml
    """
    build_pyproject_path = build_cfg.get("pyproject_path")
    root_pyproject_path = (root_cfg or {}).get("pyproject_path")

    if build_pyproject_path:
        # Build-level path takes precedence
        return (config_dir / build_pyproject_path).resolve()
    if root_pyproject_path:
        # Root-level path
        return (config_dir / root_pyproject_path).resolve()
    # Default: config_dir / "pyproject.toml" (project root)
    return config_dir / "pyproject.toml"


def validate_and_normalize_module_actions(  # noqa: C901, PLR0912, PLR0915
    module_actions: ModuleActions,
    config_dir: Path | None = None,
) -> list[ModuleActionFull]:
    """Validate and normalize module_actions to list format.

    Applies all default values and validates all fields. Returns fully resolved
    actions with all fields present (defaults applied).

    Args:
        module_actions: Either dict format (simple) or list format (full)
        config_dir: Optional config directory for resolving relative source_path
            paths. If None, paths are resolved relative to current working directory.

    Returns:
        Normalized list of ModuleActionFull with all fields present

    Raises:
        ValueError: If validation fails
        TypeError: If types are invalid
    """
    valid_action_types = literal_to_set(ModuleActionType)
    valid_action_modes = literal_to_set(ModuleActionMode)
    valid_action_scopes = literal_to_set(ModuleActionScope)
    valid_action_affects = literal_to_set(ModuleActionAffects)
    valid_action_cleanups = literal_to_set(ModuleActionCleanup)

    if isinstance(module_actions, dict):
        # Simple format: dict[str, str | None]
        # Convert to list format with defaults applied
        # {"old": "new"} -> move action
        # {"old": None} -> delete action
        result: list[ModuleActionFull] = []
        for key, value in sorted(module_actions.items()):
            if not isinstance(key, str):  # pyright: ignore[reportUnnecessaryIsInstance]
                msg = (
                    f"module_actions dict keys must be strings, "
                    f"got {type(key).__name__}"
                )
                raise TypeError(msg)
            if value is not None and not isinstance(value, str):  # pyright: ignore[reportUnnecessaryIsInstance]
                msg = (
                    f"module_actions dict values must be strings or None, "
                    f"got {type(value).__name__}"
                )
                raise ValueError(msg)

            # Validate source is non-empty
            if not key:
                msg = "module_actions dict keys (source) must be non-empty strings"
                raise ValueError(msg)

            # Build normalized action with defaults
            # Dict format: {"old": "new"} -> move, {"old": None} -> delete
            if value is not None:
                # Move action: {"old": "new"}
                normalized: ModuleActionFull = {
                    "source": key,
                    "dest": value,
                    "action": "move",
                    "mode": "preserve",
                    "scope": "shim",  # Explicitly set for dict format (per Q4)
                    "affects": "shims",
                    "cleanup": "auto",
                }
            else:
                # Delete action: {"old": None}
                normalized = {
                    "source": key,
                    "action": "delete",
                    "mode": "preserve",
                    "scope": "shim",  # Explicitly set for dict format (per Q4)
                    "affects": "shims",
                    "cleanup": "auto",
                }
            result.append(normalized)
        return result

    if isinstance(module_actions, list):  # pyright: ignore[reportUnnecessaryIsInstance]
        # Full format: list[ModuleActionFull]
        # Validate each item, then apply defaults
        result_list: list[ModuleActionFull] = []
        for idx, action in enumerate(module_actions):
            if not isinstance(action, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
                msg = (
                    f"module_actions list items must be dicts, "
                    f"got {type(action).__name__} at index {idx}"
                )
                raise TypeError(msg)

            # Validate required 'source' key
            if "source" not in action:
                msg = f"module_actions[{idx}] missing required 'source' key"
                raise ValueError(msg)
            source_val = action["source"]
            if not isinstance(source_val, str):  # pyright: ignore[reportUnnecessaryIsInstance]
                msg = (
                    f"module_actions[{idx}]['source'] must be a string, "
                    f"got {type(source_val).__name__}"
                )
                raise TypeError(msg)
            # Validate source is non-empty
            if not source_val:
                msg = f"module_actions[{idx}]['source'] must be a non-empty string"
                raise ValueError(msg)

            # Validate and normalize action type
            action_val = action.get("action", "move")
            # Normalize "none" to "delete" (alias)
            if action_val == "none":
                action_val = "delete"
            if action_val not in valid_action_types:
                valid_str = ", ".join(repr(v) for v in sorted(valid_action_types))
                msg = (
                    f"module_actions[{idx}]['action'] invalid: {action_val!r}. "
                    f"Must be one of: {valid_str}"
                )
                raise ValueError(msg)

            # Validate mode if present
            if "mode" in action:
                mode_val = action["mode"]
                if mode_val not in valid_action_modes:
                    valid_str = ", ".join(repr(v) for v in sorted(valid_action_modes))
                    msg = (
                        f"module_actions[{idx}]['mode'] invalid: {mode_val!r}. "
                        f"Must be one of: {valid_str}"
                    )
                    raise ValueError(msg)

            # Validate scope if present
            if "scope" in action:
                scope_val = action["scope"]
                if scope_val not in valid_action_scopes:
                    valid_str = ", ".join(repr(v) for v in sorted(valid_action_scopes))
                    msg = (
                        f"module_actions[{idx}]['scope'] invalid: {scope_val!r}. "
                        f"Must be one of: {valid_str}"
                    )
                    raise ValueError(msg)

            # Validate affects if present
            if "affects" in action:
                affects_val = action["affects"]
                if affects_val not in valid_action_affects:
                    valid_str = ", ".join(repr(v) for v in sorted(valid_action_affects))
                    msg = (
                        f"module_actions[{idx}]['affects'] invalid: {affects_val!r}. "
                        f"Must be one of: {valid_str}"
                    )
                    raise ValueError(msg)

            # Validate cleanup if present
            if "cleanup" in action:
                cleanup_val = action["cleanup"]
                if cleanup_val not in valid_action_cleanups:
                    valid_str = ", ".join(
                        repr(v) for v in sorted(valid_action_cleanups)
                    )
                    msg = (
                        f"module_actions[{idx}]['cleanup'] invalid: {cleanup_val!r}. "
                        f"Must be one of: {valid_str}"
                    )
                    raise ValueError(msg)

            # Validate source_path if present
            source_path_resolved_str: str | None = None
            if "source_path" in action:
                source_path_val = action["source_path"]
                if not isinstance(source_path_val, str):  # pyright: ignore[reportUnnecessaryIsInstance]
                    msg = (
                        f"module_actions[{idx}]['source_path'] must be a string, "
                        f"got {type(source_path_val).__name__}"
                    )
                    raise TypeError(msg)
                if not source_path_val:
                    msg = (
                        f"module_actions[{idx}]['source_path'] must be a "
                        f"non-empty string if present"
                    )
                    raise ValueError(msg)

                # Resolve to absolute path (relative to config_dir if provided)
                if config_dir is not None:
                    if Path(source_path_val).is_absolute():
                        source_path_resolved = Path(source_path_val).resolve()
                    else:
                        source_path_resolved = (config_dir / source_path_val).resolve()
                else:
                    source_path_resolved = Path(source_path_val).resolve()

                # Get affects value to determine if we need to validate file existence
                affects_val = action.get("affects", "shims")
                # Always validate module name matching (even for shims-only actions)
                # but only validate file existence if affects includes "stitching"
                if "stitching" in affects_val or affects_val == "both":
                    # Validate file exists (if affects includes "stitching")
                    if not source_path_resolved.exists():
                        msg = (
                            f"module_actions[{idx}]['source_path'] file "
                            f"does not exist: {source_path_resolved}"
                        )
                        raise ValueError(msg)

                    # Validate is Python file
                    if source_path_resolved.suffix != ".py":
                        msg = (
                            f"module_actions[{idx}]['source_path'] must be a "
                            f"Python file (.py extension), got: {source_path_resolved}"
                        )
                        raise ValueError(msg)

                # Extract module name from file and verify it matches source
                # Use file's parent directory as package root for validation
                # (since source_path files may not be in normal include set)
                # This validation happens for all affects values to ensure
                # source matches
                if (
                    source_path_resolved.exists()
                    and source_path_resolved.suffix == ".py"
                ):
                    package_root_for_validation = source_path_resolved.parent
                    try:
                        extract_module_name_from_source_path(
                            source_path_resolved,
                            package_root_for_validation,
                            source_val,
                        )
                    except ValueError as e:
                        msg = (
                            f"module_actions[{idx}]['source_path'] "
                            f"validation failed: {e!s}"
                        )
                        raise ValueError(msg) from e

                # Store resolved absolute path for later use
                source_path_resolved_str = str(source_path_resolved)

            # Validate dest based on action type (per Q5)
            dest_val = action.get("dest")
            if action_val in ("move", "copy", "rename"):
                # dest is required for move/copy/rename
                if dest_val is None:
                    msg = (
                        f"module_actions[{idx}]: 'dest' is required for "
                        f"'{action_val}' action"
                    )
                    raise ValueError(msg)
                if not isinstance(dest_val, str):  # pyright: ignore[reportUnnecessaryIsInstance]
                    msg = (
                        f"module_actions[{idx}]['dest'] must be a string, "
                        f"got {type(dest_val).__name__}"
                    )
                    raise TypeError(msg)
                # For rename, validate that dest doesn't contain dots
                if action_val == "rename" and "." in dest_val:
                    msg = (
                        f"module_actions[{idx}]['dest'] for 'rename' action "
                        f"must not contain dots. Got dest='{dest_val}'. "
                        f"Use 'move' action to move modules down the tree"
                    )
                    raise ValueError(msg)
            elif action_val == "delete":
                # dest must NOT be present for delete
                if dest_val is not None:
                    msg = (
                        f"module_actions[{idx}]: 'dest' must not be present "
                        f"for 'delete' action"
                    )
                    raise ValueError(msg)

            # Build normalized action with all defaults applied (per Q1/Q2)
            normalized_action: ModuleActionFull = {
                "source": source_val,
                "action": action_val,  # Already normalized ("none" -> "delete")
                "mode": action.get("mode", "preserve"),
                # Default for user actions (per Q3)
                "scope": action.get("scope", "shim"),
                "affects": action.get("affects", "shims"),
                "cleanup": action.get("cleanup", "auto"),
            }
            # Add dest only if present (required for move/copy, not for delete)
            if dest_val is not None:
                normalized_action["dest"] = dest_val
            # Add source_path only if present (store resolved absolute path)
            if "source_path" in action:
                if source_path_resolved_str is not None:
                    normalized_action["source_path"] = source_path_resolved_str
                else:
                    # This shouldn't happen, but handle it just in case
                    source_path_val = action["source_path"]
                    if config_dir is not None:
                        if Path(source_path_val).is_absolute():
                            source_path_resolved = Path(source_path_val).resolve()
                        else:
                            source_path_resolved = (
                                config_dir / source_path_val
                            ).resolve()
                    else:
                        source_path_resolved = Path(source_path_val).resolve()
                    normalized_action["source_path"] = str(source_path_resolved)

            result_list.append(normalized_action)

        return result_list

    msg = f"module_actions must be dict or list, got {type(module_actions).__name__}"
    raise ValueError(msg)


def _apply_metadata_fields(
    resolved_cfg: dict[str, Any],
    metadata: PyprojectMetadata,
    pyproject_path: Path,
    *,
    explicitly_requested: bool,
) -> None:
    """Apply extracted metadata fields to resolved config.

    Pyproject.toml metadata is always a fallback - it only fills missing fields.
    User-set values (empty strings or non-empty strings) always take precedence
    and are never overwritten.

    Note: Empty strings ("") in config are preserved as they represent an
    intentional choice. None or missing fields can be filled by pyproject.

    Note: Package name is NOT set here - it's handled in _apply_pyproject_metadata()
    and is always extracted if available, regardless of use_pyproject_metadata.

    Note: description, authors, and license are only applied when
    explicitly_requested is True (use_pyproject_metadata=True or pyproject_path set).

    Args:
        resolved_cfg: Mutable resolved config dict (modified in place)
        metadata: Extracted metadata
        pyproject_path: Path to pyproject.toml (for logging)
        explicitly_requested: True if pyproject metadata should be used
            (use_pyproject_metadata=True, pyproject_path set, or default for
            configless builds). Controls whether description, authors, and
            license are applied.
    """
    logger = getAppLogger()

    # Apply fields from pyproject.toml
    # Version is resolved immediately (user -> pyproject) rather than storing
    # _pyproject_version separately
    if (
        explicitly_requested
        and metadata.version
        and ("version" not in resolved_cfg or not resolved_cfg.get("version"))
    ):
        resolved_cfg["version"] = metadata.version

    # For description, authors, license:
    # - Only applied when explicitly_requested is True (use_pyproject_metadata=True
    #   or pyproject_path set)
    # - None or missing = not set, can be filled by pyproject (fallback)
    # - "" = explicitly set to empty, should NOT be overwritten
    # - non-empty string = explicitly set by user, should NEVER be overwritten
    # Note: display_name is NOT set here - it uses package as fallback
    # (handled after package resolution, since package may come from pyproject)

    if explicitly_requested:
        if metadata.description:
            current = resolved_cfg.get("description")
            if current is None:
                resolved_cfg["description"] = metadata.description

        if metadata.authors:
            current = resolved_cfg.get("authors")
            if current is None:
                resolved_cfg["authors"] = metadata.authors

        # Apply license from pyproject (only if not already set in config)
        # Note: This only runs when explicitly_requested=True
        # (use_pyproject_metadata=True or pyproject_path set),
        # same as description and authors fields.
        # Process license_text first, then license_files
        if metadata.license_text or metadata.license_files:
            current_license = resolved_cfg.get("license")
            if current_license is None:
                # Combine pyproject license_text (already resolved) with license_files
                text_parts: list[str] = []
                if metadata.license_text:
                    text_parts.append(metadata.license_text)
                if metadata.license_files:
                    resolved_files_text = _resolve_license_files_patterns(
                        metadata.license_files, pyproject_path.parent
                    )
                    if resolved_files_text:
                        text_parts.append(resolved_files_text)
                # Combine and use fallback if empty
                pyproject_license_text = (
                    "\n\n".join(text_parts) if text_parts else DEFAULT_LICENSE_FALLBACK
                )
                resolved_cfg["license"] = pyproject_license_text

    if metadata.has_any():
        logger.trace(f"[resolve_build_config] Extracted metadata from {pyproject_path}")


def _apply_pyproject_metadata(
    resolved_cfg: dict[str, Any],
    *,
    build_cfg: RootConfig,
    root_cfg: RootConfig | None,
    config_dir: Path,
) -> None:
    """Extract and apply pyproject.toml metadata to resolved config.

    Extracts all metadata from pyproject.toml once, then:
    - Always uses package name for resolution (if not already set)
    - Uses other metadata (display_name, description, authors, license, version)
      only if use_pyproject_metadata is enabled

    Args:
        resolved_cfg: Mutable resolved config dict (modified in place)
        build_cfg: Original build config
        root_cfg: Root config (may be None)
        config_dir: Config directory for path resolution
    """
    logger = getAppLogger()

    # Try to find pyproject.toml
    pyproject_path = _resolve_pyproject_path(build_cfg, root_cfg, config_dir)
    if not pyproject_path or not pyproject_path.exists():
        return

    # Extract all metadata once (if available)
    # Use required=False since we handle errors gracefully below
    try:
        metadata = extract_pyproject_metadata(pyproject_path, required=False)
        if metadata is None:
            return
    except (RuntimeError, ValueError, FileNotFoundError) as e:
        # If extraction fails, silently continue (package will be resolved via
        # other means)
        logger.trace(
            "[_apply_pyproject_metadata] Failed to extract metadata from %s: %s",
            pyproject_path,
            e,
        )
        return

    # Always extract package name for resolution purposes (if not already set)
    if metadata.name and not resolved_cfg.get("package"):
        resolved_cfg["package"] = metadata.name
        logger.info(
            "Package name '%s' extracted from pyproject.toml for resolution",
            metadata.name,
        )

    # Apply other metadata only if use_pyproject_metadata is enabled
    # (This includes configless builds which use pyproject by default)
    should_use = _should_use_pyproject_metadata(build_cfg, root_cfg)
    if not should_use:
        return

    _apply_metadata_fields(
        resolved_cfg,
        metadata,
        pyproject_path,
        explicitly_requested=should_use,
    )


def _load_gitignore_patterns(path: Path) -> list[str]:
    """Read .gitignore and return non-comment patterns."""
    patterns: list[str] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            clean_line = line.strip()
            if clean_line and not clean_line.startswith("#"):
                patterns.append(clean_line)
    return patterns


def _merge_post_processing(  # noqa: C901, PLR0912, PLR0915
    build_cfg: PostProcessingConfig | None,
    root_cfg: PostProcessingConfig | None,
) -> PostProcessingConfig:
    """Deep merge post-processing configs: build-level → root-level → default.

    Args:
        build_cfg: Build-level post-processing config (may be None)
        root_cfg: Root-level post-processing config (may be None)

    Returns:
        Merged post-processing config
    """
    # Start with defaults
    merged: PostProcessingConfig = {
        "enabled": True,
        "category_order": list(DEFAULT_CATEGORY_ORDER),
        "categories": {
            cat: {
                "enabled": bool(cfg.get("enabled", True)),
                "priority": (
                    list(cast("list[str]", cfg["priority"]))
                    if isinstance(cfg.get("priority"), list)
                    else []
                ),
            }
            for cat, cfg in DEFAULT_CATEGORIES.items()
        },
    }

    # Merge root-level config
    if root_cfg:
        if "enabled" in root_cfg:
            merged["enabled"] = root_cfg["enabled"]
        if "category_order" in root_cfg:
            merged["category_order"] = list(root_cfg["category_order"])

        if "categories" in root_cfg:
            if "categories" not in merged:
                merged["categories"] = {}
            for cat_name, cat_cfg in root_cfg["categories"].items():
                if cat_name not in merged["categories"]:
                    merged["categories"][cat_name] = {}
                # Merge category config
                merged_cat = merged["categories"][cat_name]
                if "enabled" in cat_cfg:
                    merged_cat["enabled"] = cat_cfg["enabled"]
                if "priority" in cat_cfg:
                    merged_cat["priority"] = list(cat_cfg["priority"])
                if "tools" in cat_cfg:
                    if "tools" not in merged_cat:
                        merged_cat["tools"] = {}
                    # Tool options replace (don't merge)
                    for tool_name, tool_override in cat_cfg["tools"].items():
                        root_override_dict: dict[str, object] = {}
                        if "command" in tool_override:
                            root_override_dict["command"] = tool_override["command"]
                        if "args" in tool_override:
                            root_override_dict["args"] = list(tool_override["args"])
                        if "path" in tool_override:
                            root_override_dict["path"] = tool_override["path"]
                        if "options" in tool_override:
                            root_override_dict["options"] = list(
                                tool_override["options"]
                            )
                        merged_cat["tools"][tool_name] = cast_hint(
                            ToolConfig, root_override_dict
                        )

    # Merge build-level config (overrides root)
    if build_cfg:
        if "enabled" in build_cfg:
            merged["enabled"] = build_cfg["enabled"]
        if "category_order" in build_cfg:
            merged["category_order"] = list(build_cfg["category_order"])

        if "categories" in build_cfg:
            if "categories" not in merged:
                merged["categories"] = {}
            for cat_name, cat_cfg in build_cfg["categories"].items():
                if cat_name not in merged["categories"]:
                    merged["categories"][cat_name] = {}
                # Merge category config
                merged_cat = merged["categories"][cat_name]
                if "enabled" in cat_cfg:
                    merged_cat["enabled"] = cat_cfg["enabled"]
                if "priority" in cat_cfg:
                    merged_cat["priority"] = list(cat_cfg["priority"])
                if "tools" in cat_cfg:
                    if "tools" not in merged_cat:
                        merged_cat["tools"] = {}
                    # Tool options replace (don't merge)
                    for tool_name, tool_override in cat_cfg["tools"].items():
                        build_override_dict: dict[str, object] = {}
                        if "command" in tool_override:
                            build_override_dict["command"] = tool_override["command"]
                        if "args" in tool_override:
                            build_override_dict["args"] = list(tool_override["args"])
                        if "path" in tool_override:
                            build_override_dict["path"] = tool_override["path"]
                        if "options" in tool_override:
                            build_override_dict["options"] = list(
                                tool_override["options"]
                            )
                        merged_cat["tools"][tool_name] = cast_hint(
                            ToolConfig, build_override_dict
                        )

    return merged


def resolve_post_processing(  # noqa: PLR0912
    build_cfg: RootConfig,
    root_cfg: RootConfig | None,
) -> PostProcessingConfigResolved:
    """Resolve post-processing configuration with cascade and validation.

    Args:
        build_cfg: Build config
        root_cfg: Root config (may be None)

    Returns:
        Resolved post-processing configuration
    """
    logger = getAppLogger()

    # Extract configs
    build_post = build_cfg.get("post_processing")
    root_post = (root_cfg or {}).get("post_processing")

    # Merge configs
    merged = _merge_post_processing(
        build_post if isinstance(build_post, dict) else None,
        root_post if isinstance(root_post, dict) else None,
    )

    # Validate category_order - warn on invalid category names
    valid_categories = set(DEFAULT_CATEGORIES.keys())
    category_order = merged.get("category_order", DEFAULT_CATEGORY_ORDER)
    invalid_categories = [cat for cat in category_order if cat not in valid_categories]
    if invalid_categories:
        logger.warning(
            "Invalid category names in post_processing.category_order: %s. "
            "Valid categories are: %s",
            invalid_categories,
            sorted(valid_categories),
        )

    # Helper function to resolve a ToolConfig to ToolConfigResolved with all fields
    def _resolve_tool_config(
        tool_label: str, tool_config: ToolConfig | dict[str, Any]
    ) -> ToolConfigResolved:
        """Resolve a ToolConfig to ToolConfigResolved with all fields populated."""
        # Ensure we have a dict (ToolConfig is a TypedDict, which is a dict)
        tool_dict = cast("dict[str, Any]", tool_config)

        # Args is required - if not present, this is an error
        validate_required_keys(tool_dict, {"args"}, f"tool_config for {tool_label}")

        resolved: ToolConfigResolved = {
            "command": tool_dict.get("command", tool_label),
            "args": list(tool_dict["args"]),
            "path": tool_dict.get("path"),
            "options": list(tool_dict.get("options", [])),
        }
        return resolved

    # Build resolved config with all categories (even if not in category_order)
    resolved_categories: dict[str, PostCategoryConfigResolved] = {}
    for cat_name, default_cat in DEFAULT_CATEGORIES.items():
        # Start with defaults
        enabled_val = default_cat.get("enabled", True)
        priority_val = default_cat.get("priority", [])
        priority_list = (
            list(cast("list[str]", priority_val))
            if isinstance(priority_val, list)
            else []
        )

        # Build tools dict from defaults
        tools_dict: dict[str, ToolConfigResolved] = {}
        if "tools" in default_cat:
            for tool_name, tool_override in default_cat["tools"].items():
                tools_dict[tool_name] = _resolve_tool_config(tool_name, tool_override)

        # Apply merged config if present
        if "categories" in merged and cat_name in merged["categories"]:
            merged_cat = merged["categories"][cat_name]
            if "enabled" in merged_cat:
                enabled_val = merged_cat["enabled"]
            if "priority" in merged_cat:
                priority_list = list(merged_cat["priority"])
            if "tools" in merged_cat:
                # Merge tools: user config overrides defaults
                for tool_name, tool_override in merged_cat["tools"].items():
                    # Merge with existing tool config if present, otherwise use override
                    existing_tool_raw: ToolConfigResolved | dict[str, Any] = (
                        tools_dict.get(tool_name, {})
                    )
                    existing_tool: dict[str, Any] = cast(
                        "dict[str, Any]", existing_tool_raw
                    )
                    merged_tool: dict[str, Any] = dict(existing_tool)
                    # Update with user override (may be partial)
                    if isinstance(tool_override, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
                        merged_tool.update(tool_override)
                    tools_dict[tool_name] = _resolve_tool_config(tool_name, merged_tool)

        # Fallback: ensure all tools in priority are in tools dict
        # If a tool is in priority but not in tools, look it up from DEFAULT_CATEGORIES
        default_tools = default_cat.get("tools", {})
        for tool_label in priority_list:
            if tool_label not in tools_dict and tool_label in default_tools:
                # Copy from defaults as fallback
                default_override = default_tools[tool_label]
                tools_dict[tool_label] = _resolve_tool_config(
                    tool_label, default_override
                )

        # Empty priority = disabled
        if not priority_list:
            enabled_val = False

        resolved_cat: PostCategoryConfigResolved = {
            "enabled": bool(enabled_val) if isinstance(enabled_val, bool) else True,
            "priority": priority_list,
            "tools": tools_dict,
        }

        resolved_categories[cat_name] = resolved_cat

    resolved: PostProcessingConfigResolved = {
        "enabled": merged.get("enabled", True),
        "category_order": list(category_order),
        "categories": resolved_categories,
    }

    return resolved


def _parse_include_with_dest(
    raw: str, context_root: Path
) -> tuple[IncludeResolved, bool]:
    """Parse include string with optional :dest suffix.

    Returns:
        (IncludeResolved, has_dest) tuple
    """
    has_dest = False
    path_str = raw
    dest_str = None

    # Handle "path:dest" format - split on last colon
    if ":" in raw:
        parts = raw.rsplit(":", 1)
        path_part, dest_part = parts[0], parts[1]

        # Check if this is a Windows drive letter (C:, D:, etc.)
        # Drive letters are 1-2 chars, possibly with backslash
        is_drive_letter = len(path_part) <= 2 and (  # noqa: PLR2004
            len(path_part) == 1 or path_part.endswith("\\")
        )

        if not is_drive_letter:
            # Valid dest separator found
            path_str = path_part
            dest_str = dest_part
            has_dest = True

    # Normalize the path
    root, rel = _normalize_path_with_root(path_str, context_root)
    inc = make_includeresolved(rel, root, "cli")

    if has_dest and dest_str:
        inc["dest"] = Path(dest_str)

    return inc, has_dest


def _try_resolve_path_in_bases(
    raw: Path | str,
    source_bases: list[str] | None = None,
    installed_bases: list[str] | None = None,
) -> tuple[Path, Path | str] | None:
    """Try to resolve a relative path in source_bases or installed_bases.

    Checks if a relative path exists in the provided bases (source_bases first,
    then installed_bases as fallback). Returns the resolved root and relative
    path if found, None otherwise.

    For glob patterns (e.g., "mypkg/**"), extracts the base path (e.g., "mypkg")
    and checks if that exists in the bases.

    Args:
        raw: Relative path to resolve
        source_bases: Optional list of source base directories (absolute paths)
        installed_bases: Optional list of installed base directories
            (absolute paths)

    Returns:
        Tuple of (root, rel) if path found in bases, None otherwise
    """
    logger = getAppLogger()
    raw_str = str(raw)

    # For glob patterns, extract the base path (part before glob)
    if has_glob_chars(raw_str):
        # Extract base path before first glob character
        glob_chars = ["*", "?", "[", "{"]
        glob_pos = min(
            (raw_str.find(c) for c in glob_chars if c in raw_str),
            default=len(raw_str),
        )
        # Find the last / before the glob (or use entire path if no /)
        path_before_glob = raw_str[:glob_pos]
        last_slash = path_before_glob.rfind("/")
        if last_slash >= 0:
            base_path_str = path_before_glob[:last_slash]
        else:
            # No slash found, entire path before glob is the base
            base_path_str = path_before_glob
    else:
        # No glob, use entire path as base
        base_path_str = raw_str

    # Try source_bases first (higher priority)
    if source_bases:
        for base_str in source_bases:
            base_path = Path(base_str).resolve()
            candidate_path = base_path / base_path_str
            if candidate_path.exists():
                logger.trace(
                    f"Found path in source_bases: {raw_str!r} "
                    f"(base: {base_path_str!r}) in {base_str}"
                )
                return base_path, raw_str

    # Try installed_bases as fallback
    if installed_bases:
        for base_str in installed_bases:
            base_path = Path(base_str).resolve()
            candidate_path = base_path / base_path_str
            if candidate_path.exists():
                logger.trace(
                    f"Found path in installed_bases: {raw_str!r} "
                    f"(base: {base_path_str!r}) in {base_str}"
                )
                return base_path, raw_str

    return None


def _normalize_path_with_root(
    raw: Path | str,
    context_root: Path | str,
    *,
    source_bases: list[str] | None = None,
    installed_bases: list[str] | None = None,
) -> tuple[Path, Path | str]:
    """Normalize a user-provided path (from CLI or config).

    - If absolute → treat that path as its own root.
      * `/abs/path/**` → root=/abs/path, rel="**"
      * `/abs/path/`   → root=/abs/path, rel="**"  (treat as contents)
      * `/abs/path`    → root=/abs/path, rel="."   (treat as literal)
    - If relative → try context_root first, then source_bases, then installed_bases
      * If found in bases, use that base as root
      * Otherwise, use context_root as root

    Args:
        raw: Path to normalize
        context_root: Default context root (config_dir or cwd)
        source_bases: Optional list of source base directories
            (for fallback lookup)
        installed_bases: Optional list of installed base directories
            (for fallback lookup)
    """
    logger = getAppLogger()
    raw_path = Path(raw)
    rel: Path | str

    # --- absolute path case ---
    if raw_path.is_absolute():
        # Split out glob or trailing slash intent
        raw_str = str(raw)
        if raw_str.endswith("/**"):
            root = Path(raw_str[:-3]).resolve()
            rel = "**"
        elif raw_str.endswith("/"):
            root = Path(raw_str[:-1]).resolve()
            rel = "**"  # treat directory as contents
        elif has_glob_chars(raw_str):
            # Extract root directory (part before first glob char)
            # Find the last path separator before any glob character
            glob_chars = ["*", "?", "[", "{"]
            glob_pos = min(
                (raw_str.find(c) for c in glob_chars if c in raw_str),
                default=len(raw_str),
            )
            # Find the last / before the glob
            path_before_glob = raw_str[:glob_pos]
            last_slash = path_before_glob.rfind("/")
            if last_slash >= 0:
                root = Path(path_before_glob[:last_slash] or "/").resolve()
                rel = raw_str[last_slash + 1 :]  # Pattern part after root
            else:
                # No slash found, treat entire path as root
                root = Path("/").resolve()
                rel = raw_str.removeprefix("/")
        else:
            root = raw_path.resolve()
            rel = "."
    else:
        # --- relative path case ---
        # Try to resolve in bases first (source_bases > installed_bases)
        resolved = _try_resolve_path_in_bases(
            raw,
            source_bases=source_bases,
            installed_bases=installed_bases,
        )
        if resolved is not None:
            root, rel = resolved
        else:
            # Not found in bases, use context_root
            root = Path(context_root).resolve()
            # preserve literal string if user provided one
            rel = raw if isinstance(raw, str) else Path(raw)

    logger.trace(f"Normalized: raw={raw!r} → root={root}, rel={rel}")
    return root, rel


def _extract_source_bases_from_includes(  # noqa: PLR0912
    includes: list[IncludeResolved],
    config_dir: Path,
) -> list[str]:
    """Extract parent directories from includes to use as source_bases.

    For each include, extracts the first directory component that contains
    packages (e.g., "src/" from "src/mypkg/main.py" or "src/mypkg/**/*.py").
    Returns absolute paths. Skips filesystem root and config_dir itself.
    Returns a deduplicated list preserving order.

    Args:
        includes: List of resolved includes
        config_dir: Config directory for resolving paths

    Returns:
        List of module base directories as absolute paths
    """
    logger = getAppLogger()
    config_dir_resolved = config_dir.resolve()
    bases: list[str] = []
    seen_bases: set[str] = set()

    for inc in includes:
        # Get the root directory for this include
        include_root = Path(inc["root"]).resolve()
        include_path = inc["path"]

        # Extract the first directory component from the path
        if isinstance(include_path, Path):
            # Resolved Path object: get first component
            path_parts = include_path.parts
            if path_parts:
                # Get first directory component
                first_dir = path_parts[0]
                parent_dir = (include_root / first_dir).resolve()
            else:
                parent_dir = include_root
        else:
            # String pattern: extract first directory component
            path_str = str(include_path)
            # Remove glob patterns and trailing slashes
            if path_str.endswith("/**"):
                # Recursive pattern: remove "/**"
                path_str = path_str.removesuffix("/**")
            elif path_str.endswith("/"):
                # Directory: remove trailing slash
                path_str = path_str.rstrip("/")

            # Extract first directory component
            # For "src/mypkg/main.py" → "src"
            # For "src/mypkg/**/*.py" → "src"
            # For "lib/otherpkg/" → "lib"
            if "/" in path_str:
                # Get first component (before first /)
                first_component = path_str.split("/", 1)[0]
                # Remove any glob chars from first component
                if has_glob_chars(first_component):
                    # If first component has glob, use include_root
                    parent_dir = include_root
                else:
                    parent_dir = (include_root / first_component).resolve()
            else:
                # Single filename or pattern: use root
                parent_dir = include_root

        # Skip if parent is filesystem root or config_dir itself
        if parent_dir in {parent_dir.anchor, config_dir_resolved}:
            continue

        # Store as absolute path
        base_str = str(parent_dir)

        # Deduplicate while preserving order
        if base_str not in seen_bases:
            seen_bases.add(base_str)
            bases.append(base_str)
            logger.trace(
                "[MODULE_BASES] Extracted base from include: %s → %s",
                inc["path"],
                base_str,
            )

    return bases


# --------------------------------------------------------------------------- #
# main per-build resolver
# --------------------------------------------------------------------------- #


def _get_first_level_modules_from_base(
    base_str: str,
    _config_dir: Path,
) -> list[str]:
    """Get first-level module/package names from a single module_base directory.

    Scans only the immediate children of the module_base directory (not
    recursive). Returns a sorted list of package/module names.

    Package detection logic:
    - Directories with __init__.py are definitely packages (standard Python)
    - Directories in source_bases are also considered packages (namespace
      packages, mimics modern Python behavior)
    - .py files at first level are modules

    Args:
        base_str: Module base directory path (absolute)
        _config_dir: Config directory (unused, kept for compatibility)

    Returns:
        Sorted list of first-level module/package names found in the base
    """
    logger = getAppLogger()
    modules: list[str] = []

    # base_str is already an absolute path
    base_path = Path(base_str).resolve()

    if not base_path.exists() or not base_path.is_dir():
        logger.trace(
            "[get_first_level_modules] Skipping non-existent base: %s", base_path
        )
        return modules

    # Get immediate children (first level only, not recursive)
    try:
        for item in sorted(base_path.iterdir()):
            if item.is_dir():
                # Check if directory has __init__.py (definitive package marker)
                has_init = (item / "__init__.py").exists()
                if has_init:
                    # Standard Python package (has __init__.py)
                    modules.append(item.name)
                    logger.trace(
                        "[get_first_level_modules] Found package (with __init__.py): "
                        "%s in %s",
                        item.name,
                        base_path,
                    )
                else:
                    # Directory in source_bases is considered a package
                    # (namespace package, mimics modern Python)
                    modules.append(item.name)
                    logger.trace(
                        "[get_first_level_modules] Found package (namespace): %s in %s",
                        item.name,
                        base_path,
                    )
            elif item.is_file() and item.suffix == ".py":
                # Python file at first level is a module
                module_name = item.stem
                if module_name not in modules:
                    modules.append(module_name)
                    logger.trace(
                        "[get_first_level_modules] Found module file: %s in %s",
                        module_name,
                        base_path,
                    )
    except PermissionError:
        logger.trace("[get_first_level_modules] Permission denied for: %s", base_path)

    return sorted(modules)


def _get_first_level_modules_from_bases(
    source_bases: list[str],
    config_dir: Path,
) -> list[str]:
    """Get first-level module/package names from source_bases directories.

    Scans only the immediate children of each source_base directory (not
    recursive). Returns a list preserving the order of source_bases, with
    modules from each base sorted but not deduplicated across bases.

    Args:
        source_bases: List of source base directory paths (absolute)
        config_dir: Config directory (unused, kept for compatibility)

    Returns:
        List of first-level module/package names found in source_bases,
        preserving source_bases order
    """
    modules: list[str] = []

    for base_str in source_bases:
        base_modules = _get_first_level_modules_from_base(base_str, config_dir)
        modules.extend(base_modules)

    return modules


def _has_main_function(module_path: Path) -> bool:
    """Check if a module path contains a main function.

    Looks for:
    - `def main(` in any Python file
    - `if __name__ == "__main__":` in any Python file

    Args:
        module_path: Path to module (directory or file)

    Returns:
        True if main function or __main__ block found
    """
    import ast  # noqa: PLC0415

    if module_path.is_file() and module_path.suffix == ".py":
        files_to_check = [module_path]
    elif module_path.is_dir():
        # Check all Python files in directory (non-recursive)
        files_to_check = list(module_path.glob("*.py"))
    else:
        return False

    for file_path in files_to_check:
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
            for node in ast.walk(tree):
                # Check for def main(
                if isinstance(node, ast.FunctionDef) and node.name == "main":
                    return True
                # Check for if __name__ == '__main__' block
                if isinstance(node, ast.If):
                    test = node.test
                    if (
                        isinstance(test, ast.Compare)
                        and isinstance(test.left, ast.Name)
                        and test.left.id == "__name__"
                        and len(test.ops) == 1
                        and isinstance(test.ops[0], ast.Eq)
                        and len(test.comparators) == 1
                        and isinstance(test.comparators[0], ast.Constant)
                        and test.comparators[0].value == "__main__"
                    ):
                        return True
        except (SyntaxError, UnicodeDecodeError, OSError):  # noqa: PERF203
            # Skip files that can't be parsed
            continue

    return False


def _infer_packages_from_includes(  # noqa: C901, PLR0912, PLR0915
    includes: list[IncludeResolved],
    source_bases: list[str],
    config_dir: Path,
) -> list[str]:
    """Infer package names from include paths using multiple strategies.

    Uses strategies in priority order:
    1. Filter by source_bases (if configured)
    2. Check __init__.py (definitive package markers)
    3. Check __main__.py (executable package markers)
    4. Extract from common prefix
    5. Validate against source_bases (ensure exists)
    6. Use most common first-level directory (when multiple candidates)

    Args:
        includes: List of resolved include patterns
        source_bases: List of source base directory paths
        config_dir: Config directory for resolving relative paths

    Returns:
        List of inferred package names (may be empty or contain multiple candidates)
    """
    if not includes:
        return []

    logger = getAppLogger()
    candidates: set[str] = set()
    path_strings: list[str] = []

    # Extract path strings from includes
    for inc in includes:
        path_val = inc.get("path")
        if isinstance(path_val, (Path, str)):  # pyright: ignore[reportUnnecessaryIsInstance]
            path_str = str(path_val)
            # Remove trailing slashes and normalize
            path_str = path_str.rstrip("/")
            if path_str:
                path_strings.append(path_str)

    if not path_strings:
        return []

    # Strategy 1: Filter by source_bases (if configured)
    filtered_paths: list[str] = []
    if source_bases:
        for path_str in path_strings:
            # Check if path is within any module_base
            for base_str in source_bases:
                # base_str is already an absolute path
                base_path = Path(base_str).resolve()
                # Try to resolve path relative to config_dir
                try:
                    path_obj = (config_dir / path_str).resolve()
                    # Check if path is within base_path
                    try:
                        path_obj.relative_to(base_path)
                        filtered_paths.append(path_str)
                        break
                    except ValueError:
                        # Not within this base, try next
                        continue
                except (OSError, ValueError):
                    # Path resolution failed, skip
                    continue
    else:
        # No source_bases, use all paths
        filtered_paths = path_strings

    if not filtered_paths:
        return []

    # Strategy 2 & 3: Check for __init__.py and __main__.py
    for path_str in filtered_paths:
        path_obj = (config_dir / path_str).resolve()
        if not path_obj.exists():
            continue

        # Check if it's a file or directory
        if path_obj.is_file():
            # Check if parent has __init__.py or __main__.py
            parent = path_obj.parent
            if (parent / "__init__.py").exists() or (parent / "__main__.py").exists():
                candidates.add(parent.name)
            # Also check if file itself is __init__.py or __main__.py
            if path_obj.name in {"__init__.py", "__main__.py"}:
                candidates.add(parent.name)
        elif path_obj.is_dir():
            # Check if directory has __init__.py or __main__.py
            if (path_obj / "__init__.py").exists() or (
                path_obj / "__main__.py"
            ).exists():
                candidates.add(path_obj.name)

    # Strategy 4: Extract from common prefix
    if not candidates:
        # Find common prefix of all paths
        common_prefix = _find_common_path_prefix(filtered_paths, config_dir)
        if common_prefix:
            # Get first directory after common prefix for each path
            common_path = (config_dir / common_prefix).resolve()
            for path_str in filtered_paths:
                try:
                    path_obj = (config_dir / path_str).resolve()
                    try:
                        rel_path = path_obj.relative_to(common_path)
                        # Get first component
                        parts = list(rel_path.parts)
                        if parts:
                            first_part = parts[0]
                            if first_part and first_part != ".":
                                candidates.add(first_part)
                    except ValueError:
                        # Not relative to common prefix, skip
                        continue
                except (OSError, ValueError):
                    continue

    # Strategy 5: Validate against source_bases (ensure exists)
    if source_bases and candidates:
        valid_modules = _get_first_level_modules_from_bases(source_bases, config_dir)
        candidates = {c for c in candidates if c in valid_modules}

    # Strategy 6: If multiple candidates, use most common first-level directory
    if len(candidates) > 1:
        # Count occurrences in original paths
        first_level_counts: dict[str, int] = {}
        for path_str in filtered_paths:
            try:
                path_obj = (config_dir / path_str).resolve()
                # Try to find first-level directory relative to source_bases
                for base_str in source_bases:
                    # base_str is already an absolute path
                    base_path = Path(base_str).resolve()
                    try:
                        rel_path = path_obj.relative_to(base_path)
                        parts = list(rel_path.parts)
                        if parts:
                            first_part = parts[0]
                            if first_part in candidates:
                                first_level_counts[first_part] = (
                                    first_level_counts.get(first_part, 0) + 1
                                )
                        break
                    except ValueError:
                        continue
            except (OSError, ValueError):
                continue

        # Return most common, or all if tied
        if first_level_counts:
            max_count = max(first_level_counts.values())
            most_common = [
                pkg for pkg, count in first_level_counts.items() if count == max_count
            ]
            if len(most_common) == 1:
                logger.trace(
                    "[_infer_packages_from_includes] Using most common package: %s",
                    most_common[0],
                )
                return most_common

    result = sorted(candidates)
    if result:
        logger.trace("[_infer_packages_from_includes] Inferred packages: %s", result)
    return result


def _find_common_path_prefix(paths: list[str], config_dir: Path) -> str | None:
    """Find the longest common path prefix of a list of paths.

    Args:
        paths: List of path strings (relative to config_dir)
        config_dir: Config directory for resolving paths

    Returns:
        Common prefix path string (relative to config_dir), or None if no common prefix
    """
    if not paths:
        return None

    # Resolve all paths and find common prefix
    resolved_paths: list[Path] = []
    for path_str in paths:
        try:
            resolved = (config_dir / path_str).resolve()
            if resolved.exists():
                resolved_paths.append(resolved)
        except (OSError, ValueError):  # noqa: PERF203
            continue

    if not resolved_paths:
        return None

    # Find common prefix by comparing path parts
    common_parts: list[str] = []
    first_path = resolved_paths[0]
    max_parts = len(first_path.parts)

    for i in range(max_parts):
        part = first_path.parts[i]
        # Check if all paths have this part at this position
        if all(i < len(p.parts) and p.parts[i] == part for p in resolved_paths[1:]):
            common_parts.append(part)
        else:
            break

    if not common_parts:
        return None

    # Reconstruct path and make relative to config_dir
    common_path = Path(*common_parts)
    try:
        rel_path = common_path.relative_to(config_dir.resolve())
        return str(rel_path)
    except ValueError:
        # Not relative to config_dir, return as-is
        return str(common_path)


def _resolve_includes(  # noqa: PLR0912
    resolved_cfg: dict[str, Any],
    *,
    args: argparse.Namespace,
    config_dir: Path,
    cwd: Path,
    source_bases: list[str] | None = None,
    installed_bases: list[str] | None = None,
) -> list[IncludeResolved]:
    logger = getAppLogger()
    logger.trace(
        f"[resolve_includes] Starting with"
        f" {len(resolved_cfg.get('include', []))} config includes"
    )

    includes: list[IncludeResolved] = []

    if getattr(args, "include", None):
        # Full override → relative to cwd
        for raw in args.include:
            inc, _ = _parse_include_with_dest(raw, cwd)
            includes.append(inc)

    elif "include" in resolved_cfg:
        # From config → relative to config_dir
        # Type narrowing: resolved_cfg is dict[str, Any], narrow the include list
        include_list: list[str | dict[str, str]] = cast(
            "list[str | dict[str, str]]", resolved_cfg["include"]
        )
        for raw in include_list:
            # Handle both string and object formats
            if isinstance(raw, dict):
                # Object format: {"path": "...", "dest": "..."}
                path_str = raw.get("path", "")
                dest_str = raw.get("dest")
                root, rel = _normalize_path_with_root(
                    path_str,
                    config_dir,
                    source_bases=source_bases,
                    installed_bases=installed_bases,
                )
                inc = make_includeresolved(rel, root, "config")
                if dest_str:
                    # dest is relative to output dir, no normalization
                    inc["dest"] = Path(dest_str)
                includes.append(inc)
            else:
                # String format: "path/to/files"
                root, rel = _normalize_path_with_root(
                    raw,
                    config_dir,
                    source_bases=source_bases,
                    installed_bases=installed_bases,
                )
                includes.append(make_includeresolved(rel, root, "config"))

    # Add-on includes (extend, not override)
    if getattr(args, "add_include", None):
        for raw in args.add_include:
            inc, _ = _parse_include_with_dest(raw, cwd)
            includes.append(inc)

    # unique path+root
    seen_inc: set[tuple[Path | str, Path]] = set()
    unique_inc: list[IncludeResolved] = []
    for i in includes:
        key = (i["path"], i["root"])
        if key not in seen_inc:
            seen_inc.add(key)
            unique_inc.append(i)

            # Check root existence
            if not i["root"].exists():
                logger.warning(
                    "Include root does not exist: %s (origin: %s)",
                    i["root"],
                    i["origin"],
                )

            # Check path existence
            if not has_glob_chars(str(i["path"])):
                full_path = i["root"] / i["path"]  # absolute paths override root
                if not full_path.exists():
                    logger.warning(
                        "Include path does not exist: %s (origin: %s)",
                        full_path,
                        i["origin"],
                    )

    return unique_inc


def _resolve_excludes(
    resolved_cfg: dict[str, Any],
    *,
    args: argparse.Namespace,
    config_dir: Path,
    cwd: Path,
    root_cfg: RootConfig | None,
) -> list[PathResolved]:
    logger = getAppLogger()
    logger.trace(
        f"[resolve_excludes] Starting with"
        f" {len(resolved_cfg.get('exclude', []))} config excludes"
    )

    excludes: list[PathResolved] = []

    def _add_excludes(paths: list[str], context: Path, origin: OriginType) -> None:
        # Exclude patterns (from CLI, config, or gitignore) should stay literal
        excludes.extend(make_pathresolved(raw, context, origin) for raw in paths)

    if getattr(args, "exclude", None):
        # Full override → relative to cwd
        # Keep CLI-provided exclude patterns as-is (do not resolve),
        # since glob patterns like "*.tmp" should match relative paths
        # beneath the include root, not absolute paths.
        _add_excludes(args.exclude, cwd, "cli")
    elif "exclude" in resolved_cfg:
        # From config → relative to config_dir
        _add_excludes(resolved_cfg["exclude"], config_dir, "config")

    # Add-on excludes (extend, not override)
    if getattr(args, "add_exclude", None):
        _add_excludes(args.add_exclude, cwd, "cli")

    # --- Merge .gitignore patterns into excludes if enabled ---
    # Determine whether to respect .gitignore
    if getattr(args, "respect_gitignore", None) is not None:
        respect_gitignore = args.respect_gitignore
    else:
        # Check ENV (SERGER_RESPECT_GITIGNORE or RESPECT_GITIGNORE)
        env_respect = os.getenv(
            f"{PROGRAM_ENV}_{DEFAULT_ENV_RESPECT_GITIGNORE}"
        ) or os.getenv(DEFAULT_ENV_RESPECT_GITIGNORE)
        if env_respect is not None:
            # Parse boolean from string (accept "true", "1", "yes", etc.)
            env_respect_lower = env_respect.lower()
            respect_gitignore = env_respect_lower in ("true", "1", "yes", "on")
        elif "respect_gitignore" in resolved_cfg:
            respect_gitignore = resolved_cfg["respect_gitignore"]
        else:
            # fallback — true by default, overridden by root config if needed
            respect_gitignore = (root_cfg or {}).get(
                "respect_gitignore",
                DEFAULT_RESPECT_GITIGNORE,
            )

    if respect_gitignore:
        gitignore_path = config_dir / ".gitignore"
        patterns = _load_gitignore_patterns(gitignore_path)
        if patterns:
            logger.trace(
                f"Adding {len(patterns)} .gitignore patterns from {gitignore_path}",
            )
        _add_excludes(patterns, config_dir, "gitignore")

    resolved_cfg["respect_gitignore"] = respect_gitignore

    # unique path+root
    seen_exc: set[tuple[Path | str, Path]] = set()
    unique_exc: list[PathResolved] = []
    for ex in excludes:
        key = (ex["path"], ex["root"])
        if key not in seen_exc:
            seen_exc.add(key)
            unique_exc.append(ex)

    return unique_exc


def _resolve_output(
    resolved_cfg: dict[str, Any],
    *,
    args: argparse.Namespace,
    config_dir: Path,
    cwd: Path,
) -> PathResolved:
    logger = getAppLogger()
    logger.trace("[resolve_output] Resolving output directory")

    if getattr(args, "out", None):
        # Full override → relative to cwd
        root, rel = _normalize_path_with_root(args.out, cwd)
        out_wrapped = make_pathresolved(rel, root, "cli")
    elif "out" in resolved_cfg:
        # From config → relative to config_dir
        root, rel = _normalize_path_with_root(resolved_cfg["out"], config_dir)
        out_wrapped = make_pathresolved(rel, root, "config")
    else:
        root, rel = _normalize_path_with_root(DEFAULT_OUT_DIR, cwd)
        out_wrapped = make_pathresolved(rel, root, "default")

    return out_wrapped


def resolve_build_config(  # noqa: C901, PLR0912, PLR0915
    build_cfg: RootConfig,
    args: argparse.Namespace,
    config_dir: Path,
    cwd: Path,
) -> RootConfigResolved:
    """Resolve a flat RootConfig into a RootConfigResolved.

    Applies CLI overrides, normalizes paths, merges gitignore behavior,
    and attaches provenance metadata.
    """
    logger = getAppLogger()
    logger.trace("[resolve_build_config] Starting resolution for config")

    # Make a mutable copy
    resolved_cfg: dict[str, Any] = dict(build_cfg)

    # Log package source if provided in config
    if "package" in build_cfg and build_cfg.get("package"):
        logger.info(
            "Package name '%s' provided in config",
            build_cfg.get("package"),
        )

    # Set log_level if not present (for tests that call resolve_build_config directly)
    if "log_level" not in resolved_cfg:
        root_log = None
        log_level = logger.determineLogLevel(args=args, root_log_level=root_log)
        resolved_cfg["log_level"] = log_level

    # root provenance for all resolutions
    meta: MetaBuildConfigResolved = {
        "cli_root": cwd,
        "config_root": config_dir,
    }

    # ------------------------------
    # Auto-discover installed packages (resolved early for use in includes)
    # ------------------------------
    if "auto_discover_installed_packages" not in resolved_cfg:
        resolved_cfg["auto_discover_installed_packages"] = True

    # ------------------------------
    # Installed packages bases (resolved early for use in includes)
    # ------------------------------
    # Convert str to list[str] if needed, then resolve relative paths to absolute
    # Priority: user-specified > auto-discovery > empty list
    if "installed_bases" in resolved_cfg:
        installed_bases = resolved_cfg["installed_bases"]
        config_installed_bases = (
            [installed_bases] if isinstance(installed_bases, str) else installed_bases
        )
        # Resolve relative paths to absolute
        resolved_installed_bases: list[str] = []
        for base in config_installed_bases:
            base_path = (config_dir / base).resolve()
            resolved_installed_bases.append(str(base_path))
        resolved_cfg["installed_bases"] = resolved_installed_bases
    # Not specified - use auto-discovery if enabled
    elif resolved_cfg["auto_discover_installed_packages"]:
        discovered_bases = discover_installed_packages_roots()
        resolved_cfg["installed_bases"] = discovered_bases
        if discovered_bases:
            logger.debug(
                "[INSTALLED_BASES] Auto-discovered %d installed package root(s): %s",
                len(discovered_bases),
                shorten_paths_for_display(
                    discovered_bases, cwd=cwd, config_dir=config_dir
                ),
            )
    else:
        # Auto-discovery disabled and not specified - use empty list
        resolved_cfg["installed_bases"] = []

    # --- Includes ---------------------------
    # Resolve source_bases to absolute paths for include resolution
    # (they may be relative paths from config)
    resolved_source_bases: list[str] | None = None
    if "source_bases" in resolved_cfg:
        source_bases_raw = resolved_cfg["source_bases"]
        source_bases_list = (
            [source_bases_raw]
            if isinstance(source_bases_raw, str)
            else source_bases_raw
        )
        resolved_source_bases = [
            str((config_dir / base).resolve()) for base in source_bases_list
        ]
    resolved_cfg["include"] = _resolve_includes(
        resolved_cfg,
        args=args,
        config_dir=config_dir,
        cwd=cwd,
        source_bases=resolved_source_bases,
        installed_bases=resolved_cfg.get("installed_bases"),
    )
    logger.trace(
        f"[resolve_build_config] Resolved {len(resolved_cfg['include'])} include(s)"
    )

    # --- Extract source_bases from includes (before resolving source_bases) ---
    # Separate CLI and config includes for priority ordering
    cli_includes: list[IncludeResolved] = [
        inc for inc in resolved_cfg["include"] if inc["origin"] == "cli"
    ]
    config_includes: list[IncludeResolved] = [
        inc for inc in resolved_cfg["include"] if inc["origin"] == "config"
    ]

    # Extract bases from includes (CLI first, then config)
    cli_bases = _extract_source_bases_from_includes(cli_includes, config_dir)
    config_bases = _extract_source_bases_from_includes(config_includes, config_dir)

    # --- Excludes ---------------------------
    resolved_cfg["exclude"] = _resolve_excludes(
        resolved_cfg,
        args=args,
        config_dir=config_dir,
        cwd=cwd,
        root_cfg=None,
    )
    logger.trace(
        f"[resolve_build_config] Resolved {len(resolved_cfg['exclude'])} exclude(s)"
    )

    # --- Output ---------------------------
    resolved_cfg["out"] = _resolve_output(
        resolved_cfg,
        args=args,
        config_dir=config_dir,
        cwd=cwd,
    )

    # ------------------------------
    # Log level
    # ------------------------------
    # Log level is resolved in resolve_config() before calling this function
    # This is a no-op placeholder - the value should already be set
    # (resolve_config sets it and then calls this function)

    # ------------------------------
    # Strict config
    # ------------------------------
    if "strict_config" not in resolved_cfg:
        resolved_cfg["strict_config"] = DEFAULT_STRICT_CONFIG

    # ------------------------------
    # Stitch mode (resolved first, used for import defaults)
    # ------------------------------
    if "stitch_mode" not in resolved_cfg:
        resolved_cfg["stitch_mode"] = DEFAULT_STITCH_MODE

    # Get the resolved stitch_mode for use in import defaults
    stitch_mode = resolved_cfg["stitch_mode"]
    if not isinstance(stitch_mode, str):
        msg = "stitch_mode must be a string"
        raise TypeError(msg)

    # ------------------------------
    # Module mode
    # ------------------------------
    if "module_mode" not in resolved_cfg:
        resolved_cfg["module_mode"] = DEFAULT_MODULE_MODE

    # ------------------------------
    # Shim setting
    # ------------------------------
    valid_shim_values = literal_to_set(ShimSetting)
    if "shim" in resolved_cfg:
        shim_val = resolved_cfg["shim"]
        # Validate value
        if shim_val not in valid_shim_values:
            valid_str = ", ".join(repr(v) for v in sorted(valid_shim_values))
            msg = f"Invalid shim value: {shim_val!r}. Must be one of: {valid_str}"
            raise ValueError(msg)
    else:
        resolved_cfg["shim"] = DEFAULT_SHIM

    # ------------------------------
    # Module actions
    # ------------------------------
    if "module_actions" in resolved_cfg:
        # Validate and normalize to list format
        resolved_cfg["module_actions"] = validate_and_normalize_module_actions(
            resolved_cfg["module_actions"], config_dir=config_dir
        )
    else:
        # Always set to empty list in resolved config (fully resolved)
        resolved_cfg["module_actions"] = []

    # ------------------------------
    # Import handling
    # ------------------------------
    if "internal_imports" not in resolved_cfg:
        resolved_cfg["internal_imports"] = DEFAULT_INTERNAL_IMPORTS[stitch_mode]

    if "external_imports" not in resolved_cfg:
        resolved_cfg["external_imports"] = DEFAULT_EXTERNAL_IMPORTS[stitch_mode]

    # ------------------------------
    # Comments mode
    # ------------------------------
    if "comments_mode" not in resolved_cfg:
        resolved_cfg["comments_mode"] = DEFAULT_COMMENTS_MODE

    # ------------------------------
    # Docstring mode
    # ------------------------------
    if "docstring_mode" not in resolved_cfg:
        resolved_cfg["docstring_mode"] = DEFAULT_DOCSTRING_MODE

    # ------------------------------
    # Module bases
    # ------------------------------
    # Convert str to list[str] if needed, then merge with bases from includes
    if "source_bases" in resolved_cfg:
        source_bases = resolved_cfg["source_bases"]
        config_source_bases = (
            [source_bases] if isinstance(source_bases, str) else source_bases
        )
    else:
        config_source_bases = DEFAULT_SOURCE_BASES

    # Merge with priority: CLI includes > config includes > config source_bases >
    # defaults
    # Deduplicate while preserving priority order
    merged_bases: list[str] = []
    seen_bases: set[str] = set()

    # Add CLI bases first (highest priority)
    # (already absolute from _extract_source_bases_from_includes)
    for base in cli_bases:
        if base not in seen_bases:
            seen_bases.add(base)
            merged_bases.append(base)

    # Add config bases (second priority)
    # (already absolute from _extract_source_bases_from_includes)
    for base in config_bases:
        if base not in seen_bases:
            seen_bases.add(base)
            merged_bases.append(base)

    # Add config source_bases (third priority) - resolve relative paths to absolute
    for base in config_source_bases:
        # Resolve relative paths to absolute
        base_path = (config_dir / base).resolve()
        base_abs = str(base_path)
        if base_abs not in seen_bases:
            seen_bases.add(base_abs)
            merged_bases.append(base_abs)

    # Add defaults last (lowest priority, but should already be in config_source_bases)
    # Resolve relative paths to absolute
    for base in DEFAULT_SOURCE_BASES:
        base_path = (config_dir / base).resolve()
        base_abs = str(base_path)
        if base_abs not in seen_bases:
            seen_bases.add(base_abs)
            merged_bases.append(base_abs)

    resolved_cfg["source_bases"] = merged_bases
    if cli_bases or config_bases:
        # Use display helpers for logging
        display_bases = shorten_paths_for_display(
            merged_bases, cwd=cwd, config_dir=config_dir
        )
        display_cli = shorten_paths_for_display(
            cli_bases, cwd=cwd, config_dir=config_dir
        )
        display_config = shorten_paths_for_display(
            config_bases, cwd=cwd, config_dir=config_dir
        )
        logger.debug(
            "[MODULE_BASES] Extracted bases from includes: CLI=%s, config=%s, "
            "merged=%s",
            display_cli,
            display_config,
            display_bases,
        )

    # ------------------------------
    # Include installed dependencies
    # ------------------------------
    if "include_installed_dependencies" not in resolved_cfg:
        resolved_cfg["include_installed_dependencies"] = False

    # ------------------------------
    # Main mode
    # ------------------------------
    valid_main_mode_values = literal_to_set(MainMode)
    if "main_mode" in resolved_cfg:
        main_mode_val = resolved_cfg["main_mode"]
        # Validate value
        if main_mode_val not in valid_main_mode_values:
            valid_str = ", ".join(repr(v) for v in sorted(valid_main_mode_values))
            msg = (
                f"Invalid main_mode value: {main_mode_val!r}. "
                f"Must be one of: {valid_str}"
            )
            raise ValueError(msg)
    else:
        resolved_cfg["main_mode"] = DEFAULT_MAIN_MODE

    # ------------------------------
    # Main name
    # ------------------------------
    if "main_name" not in resolved_cfg:
        resolved_cfg["main_name"] = DEFAULT_MAIN_NAME
    # Note: main_name can be None or a string, no validation needed here
    # (validation happens during parsing in later phases)

    # ------------------------------
    # Disable build timestamp
    # ------------------------------
    if getattr(args, "disable_build_timestamp", None):
        # CLI argument takes precedence
        resolved_cfg["disable_build_timestamp"] = True
    else:
        # Check ENV (SERGER_DISABLE_BUILD_TIMESTAMP or DISABLE_BUILD_TIMESTAMP)
        env_disable = os.getenv(
            f"{PROGRAM_ENV}_{DEFAULT_ENV_DISABLE_BUILD_TIMESTAMP}"
        ) or os.getenv(DEFAULT_ENV_DISABLE_BUILD_TIMESTAMP)
        if env_disable is not None:
            # Parse boolean from string (accept "true", "1", "yes", etc.)
            env_disable_lower = env_disable.lower()
            resolved_cfg["disable_build_timestamp"] = env_disable_lower in (
                "true",
                "1",
                "yes",
                "on",
            )
        elif "disable_build_timestamp" not in resolved_cfg:
            resolved_cfg["disable_build_timestamp"] = DEFAULT_DISABLE_BUILD_TIMESTAMP

    # ------------------------------
    # Post-processing
    # ------------------------------
    resolved_cfg["post_processing"] = resolve_post_processing(build_cfg, None)

    # ------------------------------
    # Pyproject.toml metadata extraction
    # ------------------------------
    # Extracts all metadata once, then:
    # - Always uses package name for resolution (if not already set)
    # - Uses other metadata only if use_pyproject_metadata is enabled
    # - Version is resolved here: user version -> pyproject version
    _apply_pyproject_metadata(
        resolved_cfg,
        build_cfg=build_cfg,
        root_cfg=None,
        config_dir=config_dir,
    )

    # ------------------------------
    # Version resolution
    # ------------------------------
    # Version is optional - resolved during pyproject metadata extraction above.
    # If not set, will fall back to timestamp in _extract_build_metadata()
    # No action needed here - value is already resolved if available

    # ------------------------------
    # License resolution
    # ------------------------------
    # License is mandatory in resolved config (always present with fallback).
    # Processing order: license field first, then license_files.
    # Resolution order: config license -> pyproject license (if enabled) -> fallback
    # Note: pyproject license is already applied in _apply_pyproject_metadata()
    # above (only when use_pyproject_metadata=True or pyproject_path set),
    # so we only need to handle config-provided license here.
    license_val = build_cfg.get("license")
    license_files_val = build_cfg.get("license_files")
    if license_val is not None or license_files_val is not None:
        # Resolve config-provided license (overrides pyproject if set)
        resolved_license = _resolve_license_field(
            license_val, license_files_val, config_dir
        )
        resolved_cfg["license"] = resolved_license
    elif "license" not in resolved_cfg:
        # No license in config or pyproject - use fallback
        resolved_cfg["license"] = DEFAULT_LICENSE_FALLBACK

    # ------------------------------
    # Stitching metadata fields (ensure all are present)
    # ------------------------------
    # Metadata fields are optional in resolved config.
    # Resolution order for most fields: user value -> pyproject value -> None (default)
    # Note: display_name has different priority (handled after package resolution)
    # Note: license is handled above (always present with fallback)
    # Fields are only set if they have a value; otherwise they remain None/absent
    for field in ("description", "authors", "repo"):
        if field not in resolved_cfg or resolved_cfg.get(field) is None:
            # Don't set to empty string - leave as None/absent
            pass

    # ------------------------------
    # Custom header and file docstring (pass through if present)
    # ------------------------------
    # These fields are truly optional and pass through as-is if provided
    if "custom_header" in build_cfg:
        resolved_cfg["custom_header"] = build_cfg["custom_header"]
    if "file_docstring" in build_cfg:
        resolved_cfg["file_docstring"] = build_cfg["file_docstring"]

    # ------------------------------
    # Package resolution (steps 3-7)
    # ------------------------------
    # Order of operations:
    # 1. ✅ User-provided in config (already set, logged above)
    # 2. ✅ pyproject.toml (just completed above)
    # 3. ✅ Infer from include paths
    # 4. ✅ Main function detection
    # 5. ✅ Most common package in includes (handled in step 3)
    # 6. ✅ Single module auto-detection
    # 7. ✅ First package in source_bases order
    package = resolved_cfg.get("package")
    source_bases_list = resolved_cfg.get("source_bases", [])
    config_includes = resolved_cfg.get("include", [])

    # Step 3: Infer from include paths (if package not set and includes exist)
    if not package and config_includes:
        inferred_packages = _infer_packages_from_includes(
            config_includes, source_bases_list, config_dir
        )
        if inferred_packages:
            # Use first package if single, or most common if multiple (already handled)
            resolved_cfg["package"] = inferred_packages[0]
            logger.info(
                "Package name '%s' inferred from include paths. "
                "Set 'package' in config to override.",
                inferred_packages[0],
            )

    # Step 4: Main function detection (if package not set and multiple modules exist)
    package = resolved_cfg.get("package")
    if not package and source_bases_list:
        # Check if multiple modules exist
        all_modules = _get_first_level_modules_from_bases(source_bases_list, config_dir)
        if len(all_modules) > 1:
            # Try to find main function in modules
            for module_name in all_modules:
                # Find module path
                module_path: Path | None = None
                for base_str in source_bases_list:
                    base_path = (config_dir / base_str).resolve()
                    module_dir = base_path / module_name
                    module_file = base_path / f"{module_name}.py"
                    if module_dir.exists() and module_dir.is_dir():
                        module_path = module_dir
                        break
                    if module_file.exists() and module_file.is_file():
                        module_path = module_file.parent
                        break
                if module_path and _has_main_function(module_path):
                    # Simple check for main function (def main( or if __name__ == "__main__")  # noqa: E501
                    resolved_cfg["package"] = module_name
                    logger.info(
                        "Package name '%s' detected via main() function. "
                        "Set 'package' in config to override.",
                        module_name,
                    )
                    break

    # Step 6: Single module auto-detection (if package not set)
    package = resolved_cfg.get("package")
    if not package and source_bases_list:
        # Find the first module_base with exactly 1 module
        detected_module: str | None = None
        detected_base: str | None = None
        for base_str in source_bases_list:
            base_modules = _get_first_level_modules_from_base(base_str, config_dir)
            if len(base_modules) == 1:
                # Found a base with exactly 1 module
                detected_module = base_modules[0]
                detected_base = base_str
                break

        if detected_module and detected_base:
            # Set package to the detected module
            resolved_cfg["package"] = detected_module
            logger.info(
                "Package name '%s' auto-detected from single module in "
                "module_base '%s'. Set 'package' in config to override.",
                detected_module,
                detected_base,
            )

    # Step 7: First package in source_bases order (if package not set)
    package = resolved_cfg.get("package")
    if not package and source_bases_list:
        all_modules = _get_first_level_modules_from_bases(source_bases_list, config_dir)
        if len(all_modules) > 0:
            # Use first module found (preserves source_bases order)
            resolved_cfg["package"] = all_modules[0]
            logger.info(
                "Package name '%s' selected from source_bases (first found). "
                "Set 'package' in config to override.",
                all_modules[0],
            )

    # ------------------------------
    # Auto-set includes from package and source_bases
    # ------------------------------
    # If no includes were provided (configless or config has no includes),
    # automatically set includes based on package and source_bases.
    # This must run AFTER pyproject metadata extraction so package from
    # pyproject.toml is available.
    has_cli_includes = bool(
        getattr(args, "include", None) or getattr(args, "add_include", None)
    )
    # Check if config has includes (empty list means no includes)
    config_includes = resolved_cfg.get("include", [])
    has_config_includes = len(config_includes) > 0
    # Check if includes were explicitly set in original config
    # (even if empty, explicit setting means don't auto-set)
    has_explicit_config_includes = "include" in build_cfg
    package = resolved_cfg.get("package")
    source_bases_list = resolved_cfg.get("source_bases", [])

    # Auto-set includes based on package (if package exists and no includes provided)
    if (
        package
        and not has_cli_includes
        and not has_config_includes
        and not has_explicit_config_includes
        and source_bases_list
    ):
        # Package exists and is found in source_bases
        # Get first-level modules from source_bases for this check
        first_level_modules = _get_first_level_modules_from_bases(
            source_bases_list, config_dir
        )
        if package in first_level_modules:
            logger.debug(
                "Auto-setting includes to package '%s' found in source_bases: %s",
                package,
                source_bases_list,
            )

            # Find which module_base contains the package
            # Can be either a directory (package) or a .py file (module)
            package_path: str | None = None
            for base_str in source_bases_list:
                # base_str is already an absolute path
                base_path = Path(base_str).resolve()
                package_dir = base_path / package
                package_file = base_path / f"{package}.py"

                if package_dir.exists() and package_dir.is_dir():
                    # Found the package directory
                    # Create include path relative to config_dir
                    rel_path = package_dir.relative_to(config_dir)
                    package_path = str(rel_path)
                    break
                if package_file.exists() and package_file.is_file():
                    # Found the package as a single-file module
                    # Create include path relative to config_dir
                    rel_path = package_file.relative_to(config_dir)
                    package_path = str(rel_path)
                    break

            if package_path:
                # Set includes to the package found in source_bases
                # For directories, add trailing slash to ensure recursive matching
                # (build.py handles directories with trailing slash as recursive)
                package_path_str = str(package_path)
                # Check if it's a directory (not a .py file) and add trailing slash
                if (
                    (config_dir / package_path_str).exists()
                    and (config_dir / package_path_str).is_dir()
                    and not package_path_str.endswith(".py")
                    and not package_path_str.endswith("/")
                ):
                    # Add trailing slash for recursive directory matching
                    package_path_str = f"{package_path_str}/"

                root, rel = _normalize_path_with_root(package_path_str, config_dir)
                auto_include = make_includeresolved(rel, root, "config")
                resolved_cfg["include"] = [auto_include]
                logger.trace(
                    "[resolve_build_config] Auto-set include: %s (root: %s)",
                    rel,
                    root,
                )

    # ------------------------------
    # Display name resolution (after package is fully resolved)
    # ------------------------------
    # display_name priority: user -> package -> None (default)
    # Package is now fully resolved, so we can use it as fallback
    if "display_name" not in resolved_cfg or resolved_cfg.get("display_name") is None:
        package = resolved_cfg.get("package")
        if package:
            resolved_cfg["display_name"] = package
        # If no package, leave display_name as None/absent

    # ------------------------------
    # Attach provenance
    # ------------------------------
    resolved_cfg["__meta__"] = meta
    return cast_hint(RootConfigResolved, resolved_cfg)


# --------------------------------------------------------------------------- #
# root-level resolver
# --------------------------------------------------------------------------- #


def resolve_config(
    root_input: RootConfig,
    args: argparse.Namespace,
    config_dir: Path,
    cwd: Path,
) -> RootConfigResolved:
    """Fully resolve a loaded RootConfig into a ready-to-run RootConfigResolved.

    If invoked standalone, ensures the global logger reflects the resolved log level.
    If called after load_and_validate_config(), this is a harmless no-op re-sync."""
    logger = getAppLogger()
    root_cfg = cast_hint(RootConfig, dict(root_input))

    logger.trace("[resolve_config] Resolving flat config")

    # ------------------------------
    # Watch interval
    # ------------------------------
    env_watch = os.getenv(DEFAULT_ENV_WATCH_INTERVAL)
    if getattr(args, "watch", None) is not None:
        watch_interval = args.watch
    elif env_watch is not None:
        try:
            watch_interval = float(env_watch)
        except ValueError:
            logger.warning(
                "Invalid %s=%r, using default.", DEFAULT_ENV_WATCH_INTERVAL, env_watch
            )
            watch_interval = DEFAULT_WATCH_INTERVAL
    else:
        watch_interval = root_cfg.get("watch_interval", DEFAULT_WATCH_INTERVAL)

    logger.trace(f"[resolve_config] Watch interval resolved to {watch_interval}s")

    # ------------------------------
    # Log level
    # ------------------------------
    root_log = root_cfg.get("log_level")
    log_level = logger.determineLogLevel(args=args, root_log_level=root_log)

    # --- sync runtime ---
    logger.setLevel(log_level)

    # Set log_level in config before resolving (resolve_build_config expects it)
    root_cfg["log_level"] = log_level

    # ------------------------------
    # Resolve single flat config
    # ------------------------------
    resolved = resolve_build_config(root_cfg, args, config_dir, cwd)

    # Add watch_interval to resolved config
    resolved["watch_interval"] = watch_interval

    # Set runtime flags with defaults (will be overridden in _execute_build if set)
    resolved["dry_run"] = False
    resolved["validate_config"] = False

    return resolved


# === serger.config.__init__ ===
# src/serger/config/__init__.py

"""Configuration handling for serger.

This module provides configuration loading, parsing, validation, and resolution.
"""


__all__ = [  # noqa: RUF022
    # config_loader
    "can_run_configless",
    "find_config",
    "load_and_validate_config",
    "load_config",
    "parse_config",
    # config_resolve
    "PyprojectMetadata",
    "extract_pyproject_metadata",
    "resolve_build_config",
    "resolve_config",
    "resolve_post_processing",
    # config_types
    "CommentsMode",
    "DocstringMode",
    "DocstringModeLocation",
    "DocstringModeSimple",
    "ExternalImportMode",
    "IncludeConfig",
    "IncludeResolved",
    "InternalImportMode",
    "MetaBuildConfigResolved",
    "ModuleActionFull",
    "ModuleMode",
    "OriginType",
    "PathResolved",
    "PostCategoryConfig",
    "PostCategoryConfigResolved",
    "PostProcessingConfig",
    "PostProcessingConfigResolved",
    "RootConfig",
    "RootConfigResolved",
    "ShimSetting",
    "StitchMode",
    "ToolConfig",
    "ToolConfigResolved",
    # config_validate
    "validate_config",
]


# === serger.main_config ===
# src/serger/main_config.py
"""Main function configuration and detection logic.

This module handles parsing of main_name configuration, finding main functions,
and managing __main__ block generation.
"""


@dataclass
class MainBlock:
    """Represents a detected __main__ block.

    Attributes:
        content: The full content of the __main__ block (including the if statement)
        file_path: Path to the file containing the block
        module_name: Module name derived from the file path
    """

    content: str
    file_path: Path
    module_name: str


def parse_main_name(main_name: str | None) -> tuple[str | None, str]:
    """Parse main_name syntax to extract module path and function name.

    Syntax rules:
    - With dots (module/package path): `::` is optional
      - `mypkg.subpkg` → module `mypkg.subpkg`, function `main` (default)
      - `mypkg.subpkg::` → module `mypkg.subpkg`, function `main` (explicit)
      - `mypkg.subpkg::entry` → module `mypkg.subpkg`, function `entry`
    - Without dots (single name): `::` is required to indicate package
      - `mypkg::` → package `mypkg`, function `main` (default)
      - `mypkg::entry` → package `mypkg`, function `entry`
      - `mypkg` → function name `mypkg` (search across all packages)
      - `main` → function name `main` (search across all packages)

    Args:
        main_name: The main_name configuration value (can be None)

    Returns:
        Tuple of (module_path, function_name):
        - module_path: Module/package path (None if function name only)
        - function_name: Function name to search for (defaults to "main")
    """
    # If None, return (None, "main") for auto-detection
    if main_name is None:
        return (None, "main")

    # If contains `::`, split on it
    if "::" in main_name:
        parts = main_name.split("::", 1)
        module_path = parts[0] if parts[0] else None
        function_name = parts[1] if parts[1] else "main"
        return (module_path, function_name)

    # If no `::`, check for dots
    if "." in main_name:
        # Contains dots: treat as module path, function defaults to "main"
        return (main_name, "main")

    # No dots and no `::`: treat as function name, module path is None
    return (None, main_name)


def _extract_top_level_function_names(source: str) -> set[str]:
    """Extract all top-level function names from source code.

    This is a "dumb extraction" function that only extracts function names.
    It does not filter by name - that's handled by the usage function.

    Args:
        source: Python source code to analyze

    Returns:
        Set of top-level function names (both sync and async)
    """
    try:
        tree = ast.parse(source)
        function_names: set[str] = set()
        # Only search top-level functions (direct children of module)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_names.add(node.name)
        return function_names  # noqa: TRY300
    except (SyntaxError, ValueError):
        return set()


def _find_function_in_source(
    source: str, function_name: str
) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    """Find a top-level function definition in source code.

    Args:
        source: Python source code
        function_name: Name of function to find

    Returns:
        Function node if found, None otherwise
    """
    try:
        tree = ast.parse(source)
        # Only search top-level functions (direct children of module)
        for node in tree.body:
            if (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name == function_name
            ):
                return node
    except (SyntaxError, ValueError):
        pass
    return None


def _get_file_priority(file_path: Path) -> int:
    """Get priority for file search order.

    Lower numbers = higher priority.
    Priority: __main__.py (0) < __init__.py (1) < other files (2)

    Args:
        file_path: File path to check

    Returns:
        Priority value (lower = higher priority)
    """
    if file_path.name == "__main__.py":
        return 0
    if file_path.name == "__init__.py":
        return 1
    return 2


def detect_function_parameters(
    function_node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> bool:
    """Detect if a function has any parameters.

    Checks for positional parameters, *args, **kwargs, and default values.

    Args:
        function_node: AST node for the function definition

    Returns:
        True if function has any parameters, False otherwise
    """
    args = function_node.args

    # Check for any type of parameter
    return bool(
        args.args  # Positional parameters
        or args.vararg is not None  # *args
        or args.kwarg is not None  # **kwargs
        or args.kwonlyargs  # Keyword-only arguments
        or (
            args.kw_defaults and any(d is not None for d in args.kw_defaults)
        )  # Keyword-only args with defaults
    )


def find_main_function(  # noqa: PLR0912, C901, PLR0915
    *,
    config: RootConfigResolved,
    file_paths: list[Path],
    module_sources: dict[str, str],
    module_names: list[str],  # noqa: ARG001  # Unused: we derive from module_to_file instead
    package_root: Path,
    file_to_include: dict[Path, IncludeResolved],
    detected_packages: set[str],
) -> tuple[str, Path, str] | None:
    """Find the main function based on configuration.

    Search order:
    1. If `main_name` is set, use it (with fallback logic)
    2. If `package` is set, search in that package
    3. Search in first package from include order

    Args:
        config: Resolved configuration with main_mode and main_name
        file_paths: List of file paths being stitched (in order)
        module_sources: Mapping of module name to source code
        module_names: List of module names in order (unused, kept for API)
        package_root: Common root of all included files
        file_to_include: Mapping of file path to its include
        detected_packages: Pre-detected package names

    Returns:
        Tuple of (function_name, source_file, module_path) if found, None otherwise
    """
    main_mode = config.get("main_mode", "auto")
    main_name = config.get("main_name")
    package = config.get("package")

    # If main_mode is "none", don't search
    if main_mode == "none":
        return None

    # Build mapping from module names to file paths
    # Also handle package_root being a package directory itself
    is_package_dir = (package_root / "__init__.py").exists()
    package_name_from_root: str | None = None
    if is_package_dir:
        package_name_from_root = package_root.name
    # Also treat as package directory if package_root.name matches package
    # (even without __init__.py, files in package_root are submodules of package)
    elif package is not None and package_root.name == package:
        package_name_from_root = package_root.name
        is_package_dir = True  # Treat as package directory for module naming

    # Check if any files have imports that reference the package name
    # (indicates files are part of that package structure)
    has_package_imports = False
    if (
        package is not None
        and package_root.name != package
        and package_root.name in ("src", "lib", "app", "package", "packages")
    ):
        # Quick check: see if any file imports from the package
        for file_path in file_paths:
            if not file_path.exists():
                continue
            try:
                content = file_path.read_text(encoding="utf-8")
                # Check for imports that reference the package name
                if f"from {package}" in content or f"import {package}" in content:
                    has_package_imports = True
                    break
            except Exception:  # noqa: BLE001, S110
                # If we can't read the file, skip the check
                pass

    # Extract source_bases from config for external files
    # source_bases is validated and normalized to list[str] in config resolution
    # It's always present in RootConfigResolved, but .get() returns object | None
    source_bases_raw = config.get("source_bases")
    source_bases: list[str] | None = None
    if source_bases_raw is not None:  # pyright: ignore[reportUnnecessaryComparison]
        # Type narrowing: config is RootConfigResolved where source_bases is list[str]
        # Cast is safe because source_bases is validated in config resolution
        # mypy sees cast as redundant, but pyright needs it for type narrowing
        source_bases = [str(mb) for mb in cast("list[str]", source_bases_raw)]  # type: ignore[redundant-cast]  # pyright: ignore[reportUnnecessaryCast]

    module_to_file: dict[str, Path] = {}
    for file_path in file_paths:
        include = file_to_include.get(file_path)
        module_name = derive_module_name(
            file_path, package_root, include, source_bases=source_bases
        )

        # If package_root is a package directory, preserve package structure
        if is_package_dir and package_name_from_root:
            # Handle __init__.py special case: represents the package itself
            if file_path.name == "__init__.py" and file_path.parent == package_root:
                module_name = package_name_from_root
            else:
                # Prepend package name to preserve structure
                module_name = f"{package_name_from_root}.{module_name}"
        # If package name is provided but package_root.name doesn't match,
        # still prepend package name to ensure correct module structure
        # (e.g., files in src/ but package is testpkg -> testpkg.utils)
        # Only do this if package_root is a common project subdirectory
        # (like src, lib, app) AND files have imports that reference the package
        elif (
            package is not None
            and package_root.name != package
            and not module_name.startswith(f"{package}.")
            and has_package_imports
            and module_name != package
        ):
            # Prepend package name to module name
            module_name = f"{package}.{module_name}"

        module_to_file[module_name] = file_path

    # Parse main_name to get module path and function name
    module_path_spec, function_name = parse_main_name(main_name)

    # Use module_to_file.keys() instead of module_names to ensure we use
    # the correct module names (with package prefix if applicable)
    available_module_names = sorted(module_to_file.keys())

    # Search strategy based on what's specified
    search_candidates: list[tuple[str, Path]] = []

    if main_name is not None:
        # main_name is set: use it
        if module_path_spec is not None:
            # Module path specified: search in that module/package
            # Match modules that start with the specified path
            search_candidates.extend(
                (mod_name, module_to_file[mod_name])
                for mod_name in available_module_names
                if (
                    mod_name == module_path_spec
                    or mod_name.startswith(f"{module_path_spec}.")
                )
            )
        else:
            # Function name only: search across all packages
            search_candidates.extend(
                (mod_name, module_to_file[mod_name])
                for mod_name in available_module_names
            )
    elif package is not None:
        # main_name is None, but package is set: search in that package
        search_candidates.extend(
            (mod_name, module_to_file[mod_name])
            for mod_name in available_module_names
            if mod_name == package or mod_name.startswith(f"{package}.")
        )
    # No main_name and no package: search in first package from include order
    elif detected_packages:
        first_package = sorted(detected_packages)[0]
        search_candidates.extend(
            (mod_name, module_to_file[mod_name])
            for mod_name in available_module_names
            if mod_name == first_package or mod_name.startswith(f"{first_package}.")
        )
    else:
        # No packages detected: search all modules
        search_candidates.extend(
            (mod_name, module_to_file[mod_name]) for mod_name in available_module_names
        )

    # Sort candidates by file priority
    # (__main__.py first, then __init__.py, then others)
    # Then by module name for determinism
    search_candidates.sort(key=lambda x: (_get_file_priority(x[1]), x[0]))

    # Extract function names from all candidates (one parse per candidate)
    # Then filter to only candidates that have the function name
    for mod_name, file_path in search_candidates:
        # Get module source (key includes .py suffix)
        module_key = f"{mod_name}.py"
        if module_key not in module_sources:
            continue

        source = module_sources[module_key]
        # Extract function names (parses AST once)
        function_names = _extract_top_level_function_names(source)
        # Filter: only keep candidates that have the function name
        if function_name in function_names:
            # Return first matching candidate (already sorted by priority)
            return (function_name, file_path, mod_name)

    # Not found
    return None


def _is_main_guard(node: ast.If) -> bool:  # noqa: PLR0911
    """Check if an if statement is a __main__ guard.

    Args:
        node: AST If node to check

    Returns:
        True if this is a __main__ guard, False otherwise
    """
    # Check if condition is: __name__ == '__main__'
    if not isinstance(node.test, ast.Compare):
        return False

    compare = node.test
    if len(compare.ops) != 1:
        return False

    if not isinstance(compare.ops[0], ast.Eq):
        return False

    # Check left side is __name__
    if not isinstance(compare.left, ast.Name):
        return False
    if compare.left.id != "__name__":
        return False

    # Check right side is '__main__' or "__main__"
    if len(compare.comparators) != 1:
        return False

    comparator = compare.comparators[0]
    if isinstance(comparator, ast.Constant):
        return comparator.value == "__main__"

    return False


def _extract_main_guards(source: str) -> list[tuple[int, int | None]]:
    """Extract line ranges for __main__ guard blocks.

    This is a "dumb extraction" function that only extracts line ranges.
    It does not extract block content - that's handled by the usage function.

    Args:
        source: Python source code to analyze

    Returns:
        List of (start_line, end_line) tuples where:
        - start_line: 1-indexed line number where the guard starts
        - end_line: 1-indexed line number (exclusive) where the guard ends,
          or None if end_lineno is not available (Python < 3.8)
    """
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return []

    guards: list[tuple[int, int | None]] = []

    # Find all top-level if statements that are __main__ guards
    for node in tree.body:
        if isinstance(node, ast.If) and _is_main_guard(node):
            if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                # Python 3.8+ has end_lineno
                start_line = node.lineno  # 1-indexed
                end_line = node.end_lineno  # 1-indexed (exclusive)
                guards.append((start_line, end_line))
            elif hasattr(node, "lineno"):
                # Python < 3.8 or no end_lineno
                start_line = node.lineno  # 1-indexed
                guards.append((start_line, None))
            # If no lineno, skip (shouldn't happen in valid AST)

    return guards


def detect_main_blocks(  # noqa: PLR0912
    *,
    file_paths: list[Path],
    package_root: Path,
    file_to_include: dict[Path, IncludeResolved],
    detected_packages: set[str],  # noqa: ARG001
) -> list[MainBlock]:
    """Detect all __main__ blocks in the provided file paths.

    Args:
        file_paths: List of file paths to check (in order)
        package_root: Common root of all included files
        file_to_include: Mapping of file path to its include
        detected_packages: Pre-detected package names
            (unused, kept for API consistency)

    Returns:
        List of MainBlock objects, one for each detected __main__ block
    """
    main_blocks: list[MainBlock] = []

    # Build mapping from module names to file paths
    # Also handle package_root being a package directory itself
    is_package_dir = (package_root / "__init__.py").exists()
    package_name_from_root: str | None = None
    if is_package_dir:
        package_name_from_root = package_root.name

    for file_path in file_paths:
        if not file_path.exists():
            continue

        # Read file content
        try:
            source = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        # Extract main guard line ranges (parses AST once)
        guard_ranges = _extract_main_guards(source)

        # Extract block content from line ranges (usage logic)
        for start_line, end_line in guard_ranges:
            # Convert 1-indexed line numbers to 0-indexed for slicing
            start_idx = start_line - 1  # 0-indexed
            block_content: str | None = None

            if end_line is not None:
                # Python 3.8+ has end_lineno
                lines = source.splitlines(keepends=True)
                if start_idx < len(lines) and end_line <= len(lines):
                    block_lines = lines[start_idx:end_line]
                    block_content = "".join(block_lines).rstrip()
                else:
                    # Fallback: use regex to find block
                    block_content = _extract_main_block_regex(source)
            else:
                # Python < 3.8 or no end_lineno: use regex fallback
                block_content = _extract_main_block_regex(source)

            if block_content:
                # Derive module name
                include = file_to_include.get(file_path)
                module_name = derive_module_name(file_path, package_root, include)

                # If package_root is a package directory, preserve package structure
                if is_package_dir and package_name_from_root:
                    # Handle __init__.py special case: represents the package itself
                    if (
                        file_path.name == "__init__.py"
                        and file_path.parent == package_root
                    ):
                        module_name = package_name_from_root
                    else:
                        # Prepend package name to preserve structure
                        module_name = f"{package_name_from_root}.{module_name}"

                main_blocks.append(
                    MainBlock(
                        content=block_content,
                        file_path=file_path,
                        module_name=module_name,
                    )
                )
                # Only take the first __main__ block per file
                break

    return main_blocks


def _extract_main_block_regex(source: str) -> str:
    """Extract __main__ block using regex (fallback method).

    Args:
        source: Source code to search

    Returns:
        Extracted block content, or empty string if not found
    """
    # Pattern matches: if __name__ == '__main__': ... (to end of file)
    # Using (?s) for dotall mode (match newlines)
    pattern = (
        r"(?s)(if\s+__name__\s*==\s*[\"']__main__[\"']\s*:\s*\n.*?)"
        r"(?=\n\n|\n[A-Za-z_#@]|\Z)"
    )
    match = re.search(pattern, source)
    if match:
        return match.group(1).rstrip()
    return ""


def select_main_block(
    *,
    main_blocks: list[MainBlock],
    main_function_result: tuple[str, Path, str] | None,
    file_paths: list[Path],
    module_names: list[str],  # noqa: ARG001
) -> MainBlock | None:
    """Select which __main__ block to keep based on priority.

    Priority order:
    1. Block in same module/file as main function
    2. Block in same package as main function
    3. Block in earliest include (by include order)

    Args:
        main_blocks: List of all detected __main__ blocks
        main_function_result: Result from find_main_function()
            (function_name, file_path, module_path) or None
        file_paths: List of file paths in include order
        module_names: List of module names in include order
            (unused, kept for API consistency)

    Returns:
        Selected MainBlock to keep, or None if no block should be kept
    """
    if not main_blocks:
        return None

    # If we have a main function, use it to determine priority
    if main_function_result is not None:
        _function_name, main_file_path, main_module_path = main_function_result

        # Priority 1: Block in same module/file as main function
        for block in main_blocks:
            if block.file_path == main_file_path:
                return block

        # Priority 2: Block in same package as main function
        # Extract package from main_module_path (everything before last dot)
        if "." in main_module_path:
            main_package = main_module_path.rsplit(".", 1)[0]
            for block in main_blocks:
                if block.module_name == main_package or block.module_name.startswith(
                    f"{main_package}."
                ):
                    return block

    # Priority 3: Block in earliest include (by include order)
    # Build mapping from file paths to their index in include order
    file_to_index = {file_path: i for i, file_path in enumerate(file_paths)}

    # Find block with earliest file index
    earliest_block: MainBlock | None = None
    earliest_index = len(file_paths)  # Start with max index

    for block in main_blocks:
        block_index = file_to_index.get(block.file_path, len(file_paths))
        if block_index < earliest_index:
            earliest_index = block_index
            earliest_block = block

    return earliest_block


@dataclass
class FunctionCollision:
    """Represents a function name collision.

    Attributes:
        module_name: Module name where the collision occurs
        function_name: Name of the colliding function
        is_main: Whether this is the main function (should not be renamed)
    """

    module_name: str
    function_name: str
    is_main: bool


def detect_collisions(
    *,
    main_function_result: tuple[str, Path, str] | None,
    module_sources: dict[str, str],
    module_names: list[str],
) -> list[FunctionCollision]:
    """Detect function name collisions with the main function.

    After module actions are applied, check if multiple functions exist
    with the same name as the main function.

    Args:
        main_function_result: Result from find_main_function()
            (function_name, file_path, module_path) or None
        module_sources: Mapping of module name to source code
        module_names: List of module names in order

    Returns:
        List of FunctionCollision objects for all functions with the same name
        as the main function. The main function itself is marked with is_main=True.
    """
    if main_function_result is None:
        return []

    main_function_name, _main_file_path, main_module_path = main_function_result

    collisions: list[FunctionCollision] = []

    # Search all modules for functions with the same name
    for module_name in sorted(module_names):
        module_key = f"{module_name}.py"
        if module_key not in module_sources:
            continue

        source = module_sources[module_key]
        func_node = _find_function_in_source(source, main_function_name)
        if func_node is not None:
            is_main = module_name == main_module_path
            collisions.append(
                FunctionCollision(
                    module_name=module_name,
                    function_name=main_function_name,
                    is_main=is_main,
                )
            )

    return collisions


def rename_function_in_source(source: str, old_name: str, new_name: str) -> str:
    """Rename a function definition in source code.

    Only renames the function definition, not calls to the function.
    Uses AST to find and rename the function definition.

    Args:
        source: Python source code
        old_name: Current function name
        new_name: New function name

    Returns:
        Modified source code with function renamed
    """
    try:
        tree = ast.parse(source)
        # Find the function definition and rename it
        for node in tree.body:
            if (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name == old_name
            ):
                node.name = new_name
                break

        # Convert back to source code
        # Use ast.unparse if available (Python 3.9+), otherwise use regex fallback
        try:
            unparsed = ast.unparse(tree)
            # ast.unparse removes leading whitespace, so if the original had
            # indentation, we need to preserve it. For module-level functions,
            # this shouldn't be an issue, but we check anyway.
            # If the original source had the function at column 0, unparsed should too
            stripped_source = source.strip()
            if stripped_source.startswith(("def ", "async def ")):
                # Module-level function - unparsed should be correct
                return unparsed
            # Otherwise, try to preserve indentation from original
            # Find the indentation of the function in the original source
            lines = source.splitlines()
            for line in lines:
                stripped = line.lstrip()
                if stripped.startswith(("def ", "async def ")) and old_name in stripped:
                    indent = line[: len(line) - len(stripped)]
                    # Apply same indentation to unparsed result
                    unparsed_lines = unparsed.splitlines()
                    if unparsed_lines:
                        # Find the function definition line in unparsed
                        for i, unparsed_line in enumerate(unparsed_lines):
                            if new_name in unparsed_line and unparsed_line.startswith(
                                ("def ", "async def ")
                            ):
                                unparsed_lines[i] = indent + unparsed_line.lstrip()
                                return "\n".join(unparsed_lines)
                    break
            # If loop completes (with or without break), return unparsed
            return unparsed  # noqa: TRY300
        except AttributeError:
            # Python < 3.9: use regex fallback
            # Match function definition with any indentation
            pattern = rf"^(\s*)(async\s+)?def\s+{re.escape(old_name)}\s*\("
            replacement = rf"\1\2def {new_name}("
            return re.sub(pattern, replacement, source, flags=re.MULTILINE)
    except (SyntaxError, ValueError):
        # If parsing fails, return original source
        return source


def generate_auto_renames(
    *,
    collisions: list[FunctionCollision],
    main_function_result: tuple[str, Path, str],
) -> dict[str, str]:
    """Generate auto-rename mappings for colliding functions.

    Creates rename mappings for all colliding functions except the main one.
    Renames to main_1, main_2, etc.

    Args:
        collisions: List of all function collisions
        main_function_result: Result from find_main_function()
            (function_name, file_path, module_path)

    Returns:
        Dictionary mapping module_name -> new_function_name for functions
        that should be renamed. Only includes non-main functions.
    """
    main_function_name, _main_file_path, _main_module_path = main_function_result

    # Filter out the main function itself
    non_main_collisions = [c for c in collisions if not c.is_main]

    if not non_main_collisions:
        return {}

    # Generate rename mappings: main_1, main_2, etc.
    renames: dict[str, str] = {}
    counter = 1
    for collision in sorted(non_main_collisions, key=lambda c: c.module_name):
        new_name = f"{main_function_name}_{counter}"
        renames[collision.module_name] = new_name
        counter += 1

    return renames


# === serger.verify_script ===
# src/serger/verify_script.py
"""Script verification and post-processing utilities.

This module provides functions for verifying stitched Python scripts,
including compilation checks, ruff formatting, and execution validation.
"""


def verify_compiles_string(source: str, filename: str = "<string>") -> None:
    """Verify that Python source code compiles without syntax errors.

    Args:
        source: Python source code as string
        filename: Filename to use in error messages (for debugging)

    Raises:
        SyntaxError: If compilation fails with syntax error details
    """
    compile(source, filename, "exec")


def verify_compiles(file_path: Path) -> bool:
    """Verify that a Python file compiles without syntax errors.

    Args:
        file_path: Path to Python file to check

    Returns:
        True if file compiles successfully, False otherwise
    """
    logger = getAppLogger()
    try:
        py_compile.compile(str(file_path), doraise=True)
    except py_compile.PyCompileError as e:
        lineno = getattr(e, "lineno", "unknown")
        logger.debug("Compilation error at line %s: %s", lineno, e.msg)
        return False
    except FileNotFoundError:
        logger.debug("File not found: %s", file_path)
        return False
    else:
        logger.debug("File compiles successfully: %s", file_path)
        return True


def find_tool_executable(
    tool_name: str,
    custom_path: str | None = None,
) -> str | None:
    """Find tool executable, checking custom_path first, then PATH.

    Args:
        tool_name: Name of the tool to find
        custom_path: Optional custom path to the executable

    Returns:
        Path to executable if found, None otherwise
    """
    if custom_path:
        path = Path(custom_path)
        if path.exists() and path.is_file():
            return str(path.resolve())
        # If custom path doesn't exist, fall back to PATH

    return shutil.which(tool_name)


def build_tool_command(
    tool_label: str,
    category: str,  # noqa: ARG001
    file_path: Path,
    tool_override: ToolConfigResolved | None = None,  # noqa: ARG001
    tools_dict: dict[str, ToolConfigResolved] | None = None,
) -> list[str] | None:
    """Build the full command to execute a tool.

    Args:
        tool_label: Tool name or custom label (simple tool name or custom instance)
        category: Category name (static_checker, formatter, import_sorter) -
            unused, kept for API compatibility
        file_path: Path to the file to process
        tool_override: Optional tool override config (deprecated, unused)
        tools_dict: Dict of resolved tool configs keyed by label
            (includes defaults from resolved config)

    Returns:
        Command list if tool is available, None otherwise
    """
    # Look up tool in tools_dict (includes defaults from resolved config)
    if tools_dict and tool_label in tools_dict:
        tool_config = tools_dict[tool_label]
        validate_required_keys(
            tool_config, {"command", "args", "path", "options"}, "tool_config"
        )
        actual_tool_name = tool_config["command"]
        base_args = tool_config["args"]
        extra = tool_config["options"]
        custom_path = tool_config["path"]
    else:
        # Tool not found in tools_dict - not supported
        # (All tools should be in tools dict, including defaults)
        return None

    # Find executable
    executable = find_tool_executable(actual_tool_name, custom_path=custom_path)
    if not executable:
        return None

    return [executable, *base_args, *extra, str(file_path)]


def execute_post_processing(
    file_path: Path,
    config: PostProcessingConfigResolved,
) -> None:
    """Execute post-processing tools on a file according to configuration.

    Args:
        file_path: Path to the file to process
        config: Resolved post-processing configuration
    """
    validate_required_keys(
        config, {"enabled", "category_order", "categories"}, "config"
    )
    logger = getAppLogger()

    if not config["enabled"]:
        logger.debug("Post-processing disabled, skipping")
        return

    # Track executed commands for deduplication
    executed_commands: set[tuple[str, ...]] = set()

    # Process categories in order
    for category_name in config["category_order"]:
        if category_name not in config["categories"]:
            continue

        category = config["categories"][category_name]
        validate_required_keys(category, {"enabled", "priority", "tools"}, "category")
        if not category["enabled"]:
            logger.debug("Category %s is disabled, skipping", category_name)
            continue

        priority = category["priority"]
        if not priority:
            logger.debug("Category %s has empty priority, skipping", category_name)
            continue

        # Try tools in priority order
        tool_ran = False
        tools_dict = category["tools"]
        for tool_label in priority:
            # Tool should be in tools dict (guaranteed by resolution)
            tool_config = (
                tools_dict.get(tool_label) if tool_label in tools_dict else None
            )
            command = build_tool_command(
                tool_label, category_name, file_path, tool_config, tools_dict
            )

            if command is None:
                logger.debug(
                    "Tool %s not available or doesn't support category %s",
                    tool_label,
                    category_name,
                )
                continue

            # Deduplicate: skip if we've already run this exact command
            command_tuple = tuple(command)
            if command_tuple in executed_commands:
                logger.debug("Skipping duplicate command: %s", " ".join(command))
                continue

            # Execute command
            logger.debug("Running %s for category %s", tool_label, category_name)
            try:
                result = subprocess.run(  # noqa: S603
                    command,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    logger.debug(
                        "%s completed successfully for category %s",
                        tool_label,
                        category_name,
                    )
                    tool_ran = True
                    executed_commands.add(command_tuple)
                    break  # Success, move to next category
                logger.debug(
                    "%s exited with code %d: %s",
                    tool_label,
                    result.returncode,
                    result.stderr or result.stdout,
                )
            except Exception as e:  # noqa: BLE001
                logger.debug("Error running %s: %s", tool_label, e)

        if not tool_ran:
            logger.debug(
                "No tool succeeded for category %s (tried: %s)",
                category_name,
                priority,
            )


def verify_executes(file_path: Path) -> bool:
    """Verify that a Python script can be executed (basic sanity check).

    First tries to run the script with --help (common CLI flag), then falls back
    to compilation check if that fails. This provides a lightweight execution
    verification without requiring full functionality testing.

    Args:
        file_path: Path to Python script to check

    Returns:
        True if script executes without immediate errors, False otherwise
    """
    logger = getAppLogger()

    # Check if file exists first
    if not file_path.exists():
        logger.debug("File does not exist: %s", file_path)
        return False

    # First, try to actually execute the script with --help
    # This verifies the script can run, not just compile
    try:
        result = subprocess.run(  # noqa: S603
            [sys.executable, str(file_path), "--help"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        # Exit code 0 or 2 (help typically exits with 0 or 2)
        if result.returncode in (0, 2):
            logger.debug("Script executes successfully (--help): %s", file_path)
            return True
        # If --help fails, try --version as fallback
        result = subprocess.run(  # noqa: S603
            [sys.executable, str(file_path), "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode in (0, 2):
            logger.debug("Script executes successfully (--version): %s", file_path)
            return True
    except Exception as e:  # noqa: BLE001
        logger.debug("Error running script with --help/--version: %s", e)

    # Fallback: verify it compiles (lightweight check)
    try:
        result = subprocess.run(  # noqa: S603
            [sys.executable, "-m", "py_compile", str(file_path)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode == 0:
            logger.debug("Script compiles successfully: %s", file_path)
            return True
        logger.debug(
            "Script execution check failed: %s", result.stderr or result.stdout
        )
    except Exception as e:  # noqa: BLE001
        logger.debug("Error during compilation check: %s", e)

    return False


def _get_error_file_pattern(out_path: Path) -> str:
    """Get the glob pattern for error files matching the output path.

    Args:
        out_path: Path to the output file (e.g., dist/package.py)

    Returns:
        Glob pattern string (e.g., "package_ERROR_*.py")
    """
    stem = out_path.stem
    return f"{stem}_ERROR_*.py"


def _cleanup_error_files(out_path: Path) -> None:  # pyright: ignore[reportUnusedFunction]
    """Delete all error files matching the output path pattern.

    Args:
        out_path: Path to the output file (e.g., dist/package.py)
    """
    logger = getAppLogger()
    pattern = _get_error_file_pattern(out_path)
    error_files = list(out_path.parent.glob(pattern))
    if error_files:
        logger.debug(
            "Cleaning up %d error file(s) matching pattern: %s",
            len(error_files),
            pattern,
        )
        for error_file in error_files:
            try:
                error_file.unlink()
                logger.trace("Deleted error file: %s", error_file)
            except OSError as e:  # noqa: PERF203
                logger.debug("Failed to delete error file %s: %s", error_file, e)


def _write_error_file(  # pyright: ignore[reportUnusedFunction]
    out_path: Path,
    source: str,
    error: SyntaxError,
) -> Path:
    """Write source code to an error file with date suffix.

    Args:
        out_path: Path to the output file (e.g., dist/package.py)
        source: Source code that failed to compile
        error: SyntaxError from compilation failure

    Returns:
        Path to the written error file
    """
    logger = getAppLogger()
    now = datetime.now(timezone.utc)
    date_suffix = now.strftime("%Y_%m_%d")
    stem = out_path.stem
    error_filename = f"{stem}_ERROR_{date_suffix}.py"
    error_path = out_path.parent / error_filename

    # Get existing error files before writing (exclude the one we're about to write)
    pattern = _get_error_file_pattern(out_path)
    all_error_files = list(out_path.parent.glob(pattern))
    # Filter out the file we're about to write (in case it already exists)
    existing_error_files = [
        f for f in all_error_files if f.resolve() != error_path.resolve()
    ]

    # Build error header with troubleshooting information
    lineno = error.lineno or "unknown"
    error_msg = error.msg or "unknown error"
    separator = "# " + "=" * 70
    error_header = f"""{separator}
# COMPILATION ERROR - TROUBLESHOOTING FILE
# ============================================================================
# This file was generated because the stitched code failed to compile.
#
# Error Details:
#   - Type: SyntaxError
#   - Line: {lineno}
#   - Message: {error_msg}
#   - Generated: {now.isoformat()}
#
# Original Output Path: {out_path}
#
# Troubleshooting:
#   1. Review the error message above to identify the syntax issue
#   2. Check the source code around line {lineno} in this file
#   3. Fix the syntax error in your source files
#   4. Rebuild with: python -m serger
#   5. This error file can be safely deleted after fixing the issue
#
# If you need to report this error, please include:
#   - This error file (or the error details above)
#   - Your serger configuration
#   - The source files that were being stitched
# ============================================================================

"""

    # Write error file
    error_content = error_header + source
    error_path.write_text(error_content, encoding="utf-8")
    logger.warning("Compilation failed. Error file written to: %s", error_path)

    # Clean up pre-existing error files (excluding the one we just wrote)
    if existing_error_files:
        logger.debug(
            "Deleting %d pre-existing error file(s)", len(existing_error_files)
        )
        for old_error_file in existing_error_files:
            try:
                old_error_file.unlink()
                logger.trace("Deleted pre-existing error file: %s", old_error_file)
            except OSError as e:  # noqa: PERF203
                logger.debug(
                    "Failed to delete pre-existing error file %s: %s",
                    old_error_file,
                    e,
                )

    return error_path


def post_stitch_processing(
    out_path: Path,
    *,
    post_processing: PostProcessingConfigResolved | None = None,
) -> None:
    """Post-process a stitched file with tools, compilation checks, and verification.

    This function:
    1. Compiles the file before post-processing
    2. Runs configured post-processing tools (static checker, formatter, import sorter)
    3. Compiles the file after post-processing
    4. Reverts changes if compilation fails after processing but succeeded before
    5. Runs a basic execution sanity check

    If post-processing breaks compilation, this function logs a warning, reverts
    the file, and continues (does not raise). The build is considered successful
    as long as the original stitched file compiles.

    Args:
        out_path: Path to the stitched Python file
        post_processing: Post-processing configuration (if None, skips post-processing)

    Note:
        This function does not raise on post-processing failures. It only raises
        if the file doesn't compile before post-processing (which should never happen
        if in-memory compilation check was performed first).
    """
    logger = getAppLogger()
    logger.debug("Starting post-stitch processing for %s", out_path)

    # Compile before post-processing
    compiled_before = verify_compiles(out_path)
    if not compiled_before:
        # This should never happen if in-memory compilation check was performed
        # But handle it gracefully just in case
        logger.warning(
            "Stitched file does not compile before post-processing. "
            "Skipping post-processing and continuing."
        )
        # Still try to verify it executes
        verify_executes(out_path)
        return

    # Save original content in case we need to revert
    original_content = out_path.read_text(encoding="utf-8")

    # Run post-processing if configured
    processing_ran = False
    if post_processing:
        try:
            execute_post_processing(out_path, post_processing)
            processing_ran = True
            logger.debug("Post-processing completed")
        except Exception as e:  # noqa: BLE001
            # Post-processing tools can fail - log and continue
            logger.warning("Post-processing failed: %s. Reverting changes.", e)
            out_path.write_text(original_content, encoding="utf-8")
            out_path.chmod(0o755)
            return
    else:
        logger.debug("Post-processing skipped (no configuration)")

    # Compile after post-processing
    compiled_after = verify_compiles(out_path)
    if not compiled_after and compiled_before and processing_ran:
        # Revert if it compiled before but not after processing
        logger.warning(
            "File no longer compiles after post-processing. Reverting changes."
        )
        out_path.write_text(original_content, encoding="utf-8")
        out_path.chmod(0o755)
        # Verify it compiles after revert (should always succeed)
        if not verify_compiles(out_path):
            # This should never happen, but log it if it does
            logger.error(
                "File does not compile after reverting post-processing changes. "
                "This indicates a problem with the original stitched file."
            )
        return
    if not compiled_after:
        # It didn't compile after, but either it didn't compile before
        # or processing didn't run - this shouldn't happen if we checked before
        logger.warning(
            "File does not compile after post-processing. "
            "This should not happen if in-memory compilation check passed."
        )
        return

    # Run execution sanity check
    verify_executes(out_path)

    logger.debug("Post-stitch processing completed successfully")


# === serger.stitch ===
# src/serger/stitch.py
"""Stitching logic for combining multiple Python modules into a single file.

This module handles the core functionality for stitching together modular
Python source files into a single executable script. It includes utilities for
import handling, code analysis, and assembly.
"""


def extract_version(pyproject_path: Path) -> str:
    """Extract version string from pyproject.toml.

    Args:
        pyproject_path: Path to pyproject.toml file

    Returns:
        Version string, or "unknown" if not found
    """
    if not pyproject_path.exists():
        return "unknown"
    text = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'(?m)^\s*version\s*=\s*["\']([^"\']+)["\']', text)
    return match.group(1) if match else "unknown"


def extract_commit(root_path: Path) -> str:  # noqa: PLR0915
    """Extract git commit hash.

    Only embeds commit hash if in CI or release tag context.

    Args:
        root_path: Project root directory

    Returns:
        Short commit hash, or "unknown (local build)" if not in CI
    """
    logger = getAppLogger()
    # Comprehensive logging for troubleshooting
    in_ci = is_ci()
    ci_env = os.getenv("CI")
    github_actions = os.getenv("GITHUB_ACTIONS")
    git_tag = os.getenv("GIT_TAG")
    github_ref = os.getenv("GITHUB_REF")
    logger.trace(
        "extract_commit called: root_path=%s, in_ci=%s, CI=%s, GITHUB_ACTIONS=%s, "
        "GIT_TAG=%s, GITHUB_REF=%s",
        root_path,
        in_ci,
        ci_env,
        github_actions,
        git_tag,
        github_ref,
    )
    logger.trace(
        "extract_commit: root_path=%s, in_ci=%s, CI=%s, GITHUB_ACTIONS=%s, "
        "GIT_TAG=%s, GITHUB_REF=%s",
        root_path,
        in_ci,
        ci_env,
        github_actions,
        git_tag,
        github_ref,
    )

    # Only embed commit hash if in CI or release tag context
    if not in_ci:
        result = "unknown (local build)"
        logger.trace("extract_commit: Not in CI context, returning: %s", result)
        return result

    # Resolve path and verify it exists
    resolved_path = root_path.resolve()
    logger.info("extract_commit: resolved_path=%s", resolved_path)
    logger.trace("extract_commit: resolved_path=%s", resolved_path)

    if not resolved_path.exists():
        logger.warning("Git root path does not exist: %s", resolved_path)
        logger.trace("extract_commit: Path does not exist: %s", resolved_path)
        return "unknown"

    # Check if .git exists (directory or file for worktrees)
    git_dir = resolved_path / ".git"
    parent_git = resolved_path.parent / ".git"
    git_dir_exists = git_dir.exists()
    parent_git_exists = parent_git.exists()
    logger.info(
        "extract_commit: git_dir=%s (exists=%s), parent_git=%s (exists=%s)",
        git_dir,
        git_dir_exists,
        parent_git,
        parent_git_exists,
    )
    logger.trace(
        "extract_commit: git_dir=%s (exists=%s), parent_git=%s (exists=%s)",
        git_dir,
        git_dir_exists,
        parent_git,
        parent_git_exists,
    )

    if not (git_dir_exists or parent_git_exists):
        logger.warning("No .git directory found at %s", resolved_path)
        logger.trace("extract_commit: No .git found, returning 'unknown'")
        return "unknown"

    commit_hash = "unknown"
    try:
        # Convert Path to string for subprocess compatibility
        cwd_str = str(resolved_path)
        logger.info("extract_commit: Running git rev-parse in: %s", cwd_str)
        logger.trace("extract_commit: Running git rev-parse in: %s", cwd_str)

        git_result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],  # noqa: S607
            cwd=cwd_str,
            capture_output=True,
            text=True,
            check=True,
        )
        commit_hash = git_result.stdout.strip()
        logger.info(
            "extract_commit: git rev-parse stdout=%r, stderr=%r",
            git_result.stdout,
            git_result.stderr,
        )
        logger.trace(
            "extract_commit: git rev-parse stdout=%r, stderr=%r",
            git_result.stdout,
            git_result.stderr,
        )

        if not commit_hash:
            logger.warning("git rev-parse returned empty string")
            logger.trace("extract_commit: Empty commit hash, using 'unknown'")
            commit_hash = "unknown"
        else:
            logger.info("extract_commit: Successfully extracted: %s", commit_hash)
            logger.trace("extract_commit: Successfully extracted: %s", commit_hash)

    except subprocess.CalledProcessError as e:
        stderr_msg = e.stderr.strip() or "no error message"
        logger.warning(
            "git rev-parse failed at %s: %s (stderr: %s, returncode: %s)",
            resolved_path,
            stderr_msg,
            stderr_msg,
            e.returncode,
        )
        logger.trace(
            "extract_commit: git rev-parse failed: returncode=%s, stderr=%s",
            e.returncode,
            stderr_msg,
        )
    except FileNotFoundError:
        logger.warning("git not available in environment")
        logger.trace("extract_commit: git not found in PATH")

    # In CI, always log the final commit value for debugging
    if in_ci:
        logger.info(
            "Final commit hash for embedding: %s (from %s)",
            commit_hash,
            resolved_path,
        )
        logger.trace(
            "extract_commit: FINAL RESULT: %s (from %s)",
            commit_hash,
            resolved_path,
        )

    return commit_hash


# Maximum number of lines to read when checking if a file is a serger build
_MAX_LINES_TO_CHECK_FOR_SERGER_BUILD = 100


def is_serger_build(file_path: Path) -> bool:
    """Check if a file is a serger-generated build.

    Reads the first ~100 lines of the file and checks for the
    __STITCH_SOURCE__ variable that serger embeds in all generated files.

    Args:
        file_path: Path to the file to check

    Returns:
        True if the file appears to be a serger build, False otherwise
    """
    if not file_path.exists():
        return False

    try:
        # Read first N lines to catch the constants section
        # where __STITCH_SOURCE__ is defined
        with file_path.open(encoding="utf-8") as f:
            lines: list[str] = []
            for i, line in enumerate(f):
                if i >= _MAX_LINES_TO_CHECK_FOR_SERGER_BUILD:
                    break
                lines.append(line)

        content = "".join(lines)

        # Check for __STITCH_SOURCE__ variable assignment with value "serger"
        # Pattern matches: __STITCH_SOURCE__ = "serger" or __STITCH_SOURCE__ = 'serger'
        # Uses capturing group to ensure opening and closing quotes match
        # Case-insensitive for both variable name and "serger" value
        pattern = r'__STITCH_SOURCE__\s*=\s*(["\'])serger\1'
        return bool(re.search(pattern, content, re.IGNORECASE))

    except (OSError, UnicodeDecodeError):
        # If we can't read the file, assume it's not a serger build
        # (safer to err on the side of caution)
        return False


def split_imports(  # noqa: C901, PLR0912, PLR0915
    text: str,
    package_names: list[str],
    external_imports: ExternalImportMode = "top",
    internal_imports: InternalImportMode = "force_strip",
) -> tuple[list[str], str]:
    """Extract external imports and body text using AST.

    Separates internal package imports from external imports, handling them
    according to the external_imports and internal_imports modes. Recursively
    finds imports at all levels, including inside functions.

    Args:
        text: Python source code
        package_names: List of package names to treat as internal
            (e.g., ["serger", "other"])
        external_imports: How to handle external imports. Supported modes:
            - "top": Hoist module-level external imports to top, but only if
              not inside conditional structures (try/if blocks) (default).
              `if TYPE_CHECKING:` blocks are excluded from this check.
            - "force_top": Hoist module-level external imports to top of file.
              Always moves imports, even inside conditional structures (if, try,
              etc.). Module-level imports are collected and deduplicated at the
              top. Empty structures (if, try, etc.) get a `pass` statement.
              Empty `if TYPE_CHECKING:` blocks (including those with only pass
              statements) are removed entirely.
            - "keep": Leave external imports in their original locations
            - "force_strip": Remove all external imports regardless of location
              (module-level, function-local, in conditionals, etc.). Empty
              structures (if, try, etc.) get a `pass` statement. Empty
              `if TYPE_CHECKING:` blocks (including those with only pass
              statements) are removed entirely.
            - "strip": Remove external imports, but skip imports inside
              conditional structures (if, try, etc.). `if TYPE_CHECKING:` blocks
              are always processed (imports removed). Empty `if TYPE_CHECKING:`
              blocks (including those with only pass statements) are removed
              entirely.
        internal_imports: How to handle internal imports. Supported modes:
            - "force_strip": Remove all internal imports regardless of location
              (default). Internal imports break in stitched mode, so they are
              removed by default.
            - "keep": Keep internal imports in their original locations within
              each module section.
            - "strip": Remove internal imports, but skip imports inside
              conditional structures (if, try, etc.). `if TYPE_CHECKING:` blocks
              are always processed (imports removed). Empty `if TYPE_CHECKING:`
              blocks (including those with only pass statements) are removed
              entirely.
            - "assign": **[EXPERIMENTAL/WIP]** Transform imports into assignments.
              Converts imports like `from module import name` to `name = name`
              (direct reference). In stitched mode, all modules share the same
              global namespace and execute in topological order, so symbols can be
              referenced directly. Preserves original indentation and location of
              imports. Assignments are included in collision detection. Note: `import
              module` statements for internal packages may not work correctly as
              there are no module objects in stitched mode.

    Returns:
        Tuple of (external_imports, body_text) where external_imports is a
        list of import statement strings (empty for "keep" mode), and body_text
        is the source with imports removed according to the mode
    """
    logger = getAppLogger()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        logger.exception("Failed to parse file")
        return [], text

    lines = text.splitlines(keepends=True)
    external_imports_list: list[str] = []
    # Separate list for TYPE_CHECKING imports
    type_checking_imports_list: list[str] = []
    all_import_ranges: list[tuple[int, int]] = []
    # For assign mode: track imports to replace with assignments
    # Maps (start, end) range to assignment code
    import_replacements: dict[tuple[int, int], str] = {}

    def find_parent(
        node: ast.AST,
        tree: ast.AST,
        target_type: type[ast.AST] | tuple[type[ast.AST], ...],
    ) -> ast.AST | None:
        """Find if a node is inside a specific parent type by tracking parent nodes."""
        # Build a mapping of child -> parent
        parent_map: dict[ast.AST, ast.AST] = {}

        def build_parent_map(parent: ast.AST) -> None:
            """Recursively build parent mapping."""
            for child in ast.iter_child_nodes(parent):
                parent_map[child] = parent
                build_parent_map(child)

        build_parent_map(tree)

        # Walk up the parent chain to find target type
        current: ast.AST | None = node
        while current is not None:
            if isinstance(current, target_type):
                # Type checker can't infer the specific type from isinstance check
                # We know it's the target_type due to the isinstance check
                return current  # mypy: ignore[return-value]
            current = parent_map.get(current)
        return None

    def has_no_move_comment(snippet: str) -> bool:
        """Check if import has a # serger: no-move comment."""
        # Look for # serger: no-move or # serger:no-move (with or without space)
        pattern = r"#\s*serger\s*:\s*no-move"
        return bool(re.search(pattern, snippet, re.IGNORECASE))

    def is_in_conditional(node: ast.AST, tree: ast.AST) -> bool:
        """Check if node is inside a conditional structure (try/if).

        Returns True if node is inside a try block or if block (excluding
        `if TYPE_CHECKING:` blocks). Returns False otherwise.

        Args:
            node: AST node to check
            tree: Root AST tree (for building parent map)

        Returns:
            True if node is in a conditional structure, False otherwise
        """
        # Build parent map once
        parent_map: dict[ast.AST, ast.AST] = {}

        def build_parent_map(parent: ast.AST) -> None:
            """Recursively build parent mapping."""
            for child in ast.iter_child_nodes(parent):
                parent_map[child] = parent
                build_parent_map(child)

        build_parent_map(tree)

        # Walk up the parent chain
        current: ast.AST | None = node
        while current is not None:
            # Check for try blocks
            if isinstance(current, ast.Try):
                return True

            # Check for if blocks (but exclude `if TYPE_CHECKING:`)
            if isinstance(current, ast.If):
                # Check if this is `if TYPE_CHECKING:`
                # It must be: test is a Name with id == "TYPE_CHECKING"
                if (
                    isinstance(current.test, ast.Name)
                    and current.test.id == "TYPE_CHECKING"
                ):
                    # This is `if TYPE_CHECKING:` - don't count as conditional
                    # Continue checking parent chain
                    pass
                else:
                    # This is a regular if block - count as conditional
                    return True

            current = parent_map.get(current)

        return False

    def generate_assignments_from_import(
        node: ast.Import | ast.ImportFrom,
        _package_names: list[str],
    ) -> str:
        """Generate assignment statements from an import node.

        In the stitched output, all modules share the same global namespace and
        are executed in topological order. So we can reference symbols directly
        instead of using sys.modules (which isn't set up until after all module
        code runs).

        Converts imports like:
        - `from module import name` → (skipped, no-op: `name = name`)
        - `from module import name as alias` → `alias = name` (direct reference)
        - `import module` → (skipped, no-op: `module = module`)
        - `import module as alias` → `alias = module` (direct reference)

        Note: No-op assignments (where local_name == imported_name) are skipped
        since they're redundant.

        Note: For `import a.b.c`, Python creates variable 'a' in the namespace,
        but in stitched mode, we can't easily reference 'a.b.c' directly.
        This case may need special handling or may not be fully supported.

        Args:
            node: AST Import or ImportFrom node
            package_names: List of package names (unused, kept for API consistency)

        Returns:
            String containing assignment statements, one per line
        """
        assignments: list[str] = []

        if isinstance(node, ast.ImportFrom):
            # Handle: from module import name1, name2, ...
            # In stitched mode, all symbols are in the same global namespace,
            # so we can reference them directly
            for alias in node.names:
                imported_name = alias.name
                local_name = alias.asname if alias.asname else imported_name
                # Skip no-op assignments (name = name)
                if local_name != imported_name:
                    # Direct reference: symbol is already in global namespace
                    assignment = f"{local_name} = {imported_name}"
                    assignments.append(assignment)

        else:
            # Handle: import module [as alias]
            for alias in node.names:
                module_name = alias.name
                if alias.asname:
                    # import module as alias
                    local_name = alias.asname
                    # For simple imports like "import json", we can reference
                    # directly. But this assumes the module was already imported
                    # as an external import (hoisted to top).
                    # For internal imports, this won't work - we'd need the
                    # module object, which doesn't exist in stitched mode.
                    # This is a limitation of assign mode for "import module".
                    # Skip no-op (alias == module_name)
                    if local_name != module_name:
                        assignment = f"{local_name} = {module_name}"
                        assignments.append(assignment)
                else:
                    # import module or import a.b.c
                    # For dotted imports like "import a.b.c", Python creates
                    # variable 'a' pointing to the 'a' module.
                    # In stitched mode, we can't reference 'a.b.c' directly,
                    # so we just reference the first component.
                    # This may not work correctly for all cases.
                    # Skip no-op assignments (module = module would be redundant)
                    # Note: For non-aliased imports, we skip since it would be
                    # a no-op (first_component = first_component)
                    pass

        return "\n".join(assignments)

    def collect_imports(node: ast.AST) -> None:  # noqa: C901, PLR0912, PLR0915
        """Recursively collect all import nodes from the AST."""
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            start = node.lineno - 1
            end = getattr(node, "end_lineno", node.lineno)
            snippet = "".join(lines[start:end])

            # Check for # serger: no-move comment
            if has_no_move_comment(snippet):
                # Keep import in place - don't add to external_imports or ranges
                return

            # --- Determine whether it's internal ---
            is_internal = False
            if isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if node.level > 0:
                    is_internal = True
                else:
                    # Check if module is exactly a package name or starts with one
                    for pkg in package_names:
                        if mod == pkg or mod.startswith(f"{pkg}."):
                            is_internal = True
                            break
            else:
                # Check if any alias starts with any of the package names
                for pkg in package_names:
                    if any(
                        alias.name == pkg or alias.name.startswith(f"{pkg}.")
                        for alias in node.names
                    ):
                        is_internal = True
                        break

            # Check if import is inside if TYPE_CHECKING block
            # Must be exactly 'if TYPE_CHECKING:' (not 'if TYPE_CHECKING and
            # something:')
            type_checking_block = find_parent(node, tree, ast.If)
            is_type_checking = (
                type_checking_block
                and isinstance(type_checking_block, ast.If)
                and isinstance(type_checking_block.test, ast.Name)
                and type_checking_block.test.id == "TYPE_CHECKING"
            )

            # Handle internal imports according to mode
            if is_internal:
                if internal_imports == "keep":
                    # Keep internal imports in place - don't add to ranges
                    pass
                elif internal_imports == "force_strip":
                    # Remove all internal imports regardless of location
                    all_import_ranges.append((start, end))
                elif internal_imports == "strip":
                    # Strip internal imports, but skip imports inside conditional
                    # structures (if, try, etc.). TYPE_CHECKING blocks are always
                    # processed (imports removed).
                    if is_type_checking:
                        # Always process TYPE_CHECKING blocks - remove imports
                        all_import_ranges.append((start, end))
                    elif is_in_conditional(node, tree):
                        # In conditional (but not TYPE_CHECKING) - keep import
                        # Don't add to ranges
                        pass
                    else:
                        # Not in conditional - remove import
                        all_import_ranges.append((start, end))
                elif internal_imports == "assign":
                    # Transform imports into assignments
                    # Get indentation from the original import line
                    import_line = lines[start] if start < len(lines) else ""
                    indent_match = re.match(r"^(\s*)", import_line)
                    indent = indent_match.group(1) if indent_match else ""
                    # Generate assignment code
                    assignment_code = generate_assignments_from_import(
                        node, package_names
                    )
                    # Indent each assignment line to match original import
                    indented_assignments = "\n".join(
                        f"{indent}{line}" for line in assignment_code.split("\n")
                    )
                    # Add newline at end if original had one
                    if end < len(lines) and lines[end - 1].endswith("\n"):
                        indented_assignments += "\n"
                    # Store replacement
                    import_replacements[(start, end)] = indented_assignments
                    # Mark import for removal
                    all_import_ranges.append((start, end))
                else:
                    # Unknown mode
                    msg = (
                        f"internal_imports mode '{internal_imports}' is not "
                        "supported. Only 'force_strip', 'keep', 'strip', and "
                        "'assign' modes are currently supported."
                    )
                    raise ValueError(msg)
            # External: handle according to mode
            elif external_imports == "keep":
                # Keep external imports in place - don't add to ranges or list
                pass
            elif external_imports == "force_top":
                # Hoist module-level to top, keep function-local in place
                is_module_level = not find_parent(
                    node, tree, (ast.FunctionDef, ast.AsyncFunctionDef)
                )
                if is_module_level:
                    # Module-level external import - hoist to top section
                    all_import_ranges.append((start, end))
                    import_text = snippet.strip()
                    if import_text:
                        if not import_text.endswith("\n"):
                            import_text += "\n"
                        # Track TYPE_CHECKING imports separately
                        if is_type_checking:
                            type_checking_imports_list.append(import_text)
                        else:
                            external_imports_list.append(import_text)
                # Function-local external imports stay in place (not added to ranges)
            elif external_imports == "top":
                # Hoist module-level to top, but only if not in conditional
                # Keep function-local and conditional imports in place
                is_module_level = not find_parent(
                    node, tree, (ast.FunctionDef, ast.AsyncFunctionDef)
                )
                if is_module_level and not is_in_conditional(node, tree):
                    # Module-level external import not in conditional - hoist to top
                    all_import_ranges.append((start, end))
                    import_text = snippet.strip()
                    if import_text:
                        if not import_text.endswith("\n"):
                            import_text += "\n"
                        # Track TYPE_CHECKING imports separately
                        if is_type_checking:
                            type_checking_imports_list.append(import_text)
                        else:
                            external_imports_list.append(import_text)
                # Function-local and conditional external imports stay in place
            elif external_imports == "force_strip":
                # Strip all external imports regardless of location
                # (module-level, function-local, in conditionals, etc.)
                all_import_ranges.append((start, end))
                # Don't add to external_imports_list (we're stripping, not hoisting)
            elif external_imports == "strip":
                # Strip external imports, but skip imports inside conditional
                # structures (if, try, etc.). TYPE_CHECKING blocks are always
                # processed (imports removed).
                if is_type_checking:
                    # Always process TYPE_CHECKING blocks - remove imports
                    all_import_ranges.append((start, end))
                elif is_in_conditional(node, tree):
                    # In conditional (but not TYPE_CHECKING) - keep import
                    # Don't add to ranges
                    pass
                else:
                    # Not in conditional - remove import
                    all_import_ranges.append((start, end))
                # Don't add to external_imports_list (we're stripping, not hoisting)
            else:
                # Other modes (assign)
                # not yet implemented
                msg = (
                    f"external_imports mode '{external_imports}' is not yet "
                    "implemented. Only 'force_top', 'top', 'keep', "
                    "'force_strip', and 'strip' modes are currently supported."
                )
                raise ValueError(msg)

        # Recursively visit child nodes
        for child in ast.iter_child_nodes(node):
            collect_imports(child)

    # Collect all imports recursively
    for node in tree.body:
        collect_imports(node)

    # --- Remove *all* import lines from the body and insert assignments ---
    # Build new body with imports replaced by assignments
    new_lines: list[str] = []
    i = 0
    while i < len(lines):
        # Check if this line is part of an import to remove
        in_import_range = False
        replacement_range: tuple[int, int] | None = None
        for start, end in all_import_ranges:
            if start <= i < end:
                in_import_range = True
                replacement_range = (start, end)
                break

        if in_import_range and replacement_range:
            # This is an import to replace
            if replacement_range in import_replacements:
                # Insert assignment code
                assignment_code = import_replacements[replacement_range]
                new_lines.append(assignment_code)
            # Skip all lines in this import range
            i = replacement_range[1]
        else:
            # Keep this line
            new_lines.append(lines[i])
            i += 1

    body = "".join(new_lines)

    # Check if TYPE_CHECKING blocks and other conditional blocks are empty
    # TYPE_CHECKING blocks: remove if empty
    # Other conditionals: add 'pass' if empty (they might have side effects)
    body_lines = body.splitlines(keepends=True)
    lines_to_remove: set[int] = set()
    lines_to_insert: list[tuple[int, str]] = []  # (index, line_to_insert)

    # Find empty conditional blocks
    i = 0
    while i < len(body_lines):
        line = body_lines[i].rstrip()
        # Check if this is a conditional block start (if/try)
        # Match "if condition:" or "try:" (try can have no condition)
        if re.match(r"^\s*(if\s+.*|try)\s*:\s*$", line):
            block_start = i
            is_type_checking = bool(re.match(r"^\s*if\s+TYPE_CHECKING\s*:\s*$", line))
            # Get indentation level
            indent_match = re.match(r"^(\s*)", body_lines[i])
            indent = indent_match.group(1) if indent_match else ""
            i += 1
            # Check if block is empty (only whitespace, pass, or nothing)
            # For TYPE_CHECKING blocks, treat blocks with only pass statements as empty
            has_content = False
            block_end = i
            is_try = line.strip().startswith("try:")
            only_pass_statements = True  # Track if block only has pass statements
            while i < len(body_lines):
                next_line = body_lines[i]
                stripped = next_line.strip()
                # Empty line - continue checking
                if not stripped:
                    i += 1
                    continue
                # For try blocks, check for except/finally/else clauses
                # These are at the same indentation as try:, so they end the try body
                if is_try and stripped.startswith(("except", "finally", "else:")):
                    # We've reached the end of the try body
                    # Check if the try body (before this clause) was empty
                    block_end = i
                    break
                # Check if line is indented (part of the block)
                if re.match(r"^\s+", next_line):
                    # Indented content found
                    if stripped == "pass":
                        # For TYPE_CHECKING blocks, pass statements don't count
                        # as content. For other blocks, pass is content.
                        if not is_type_checking:
                            has_content = True
                        # else: keep only_pass_statements = True
                    else:
                        # Non-pass content found - block has real content
                        has_content = True
                        only_pass_statements = False
                    i += 1
                    continue
                # Non-indented line - end of block
                block_end = i
                break
            # For TYPE_CHECKING blocks, if only pass statements, treat as empty
            if is_type_checking and only_pass_statements and not has_content:
                # TYPE_CHECKING block with only pass statements: remove
                for j in range(block_start, block_end):
                    lines_to_remove.add(j)
            elif not has_content:
                if is_type_checking:
                    # TYPE_CHECKING block: remove if empty
                    for j in range(block_start, block_end):
                        lines_to_remove.add(j)
                else:
                    # Other conditional: add 'pass' to make it valid
                    # Insert pass after the block start line
                    pass_line = f"{indent}    pass\n"
                    lines_to_insert.append((block_start + 1, pass_line))
        i += 1

    # Apply insertions (in reverse order to maintain indices)
    for idx, line in sorted(lines_to_insert, reverse=True):
        body_lines.insert(idx, line)

    # Remove empty TYPE_CHECKING blocks
    if lines_to_remove:
        body = "".join(
            line for i, line in enumerate(body_lines) if i not in lines_to_remove
        )
    else:
        body = "".join(body_lines)

    # Group TYPE_CHECKING imports together in a single block
    if type_checking_imports_list:
        type_checking_block_text = "if TYPE_CHECKING:\n"
        for imp in type_checking_imports_list:
            # Indent the import
            type_checking_block_text += f"    {imp}"
        external_imports_list.append(type_checking_block_text)

    return external_imports_list, body


def strip_redundant_blocks(text: str) -> str:
    """Remove shebangs and __main__ guards from module code.

    Args:
        text: Python source code

    Returns:
        Source code with shebangs and __main__ blocks removed
    """
    text = re.sub(r"^#!.*\n", "", text)
    text = re.sub(
        r"(?s)\n?if\s+__name__\s*==\s*[\"']__main__[\"']\s*:\s*\n.*?$",
        "",
        text,
    )

    return text.strip()


def process_comments(text: str, mode: CommentsMode) -> str:  # noqa: C901, PLR0912, PLR0915
    """Process comments in source code according to the specified mode.

    Args:
        text: Python source code
        mode: Comments processing mode:
            - "keep": Keep all comments
            - "ignores": Only keep comments that specify ignore rules
            - "inline": Only keep inline comments (on same line as code)
            - "strip": Remove all comments

    Returns:
        Source code with comments processed according to mode
    """
    if mode == "keep":
        return text

    if mode == "strip":
        # Remove all comments, but preserve docstrings
        # Use a simple approach: split by # and check if we're in a string
        lines = text.splitlines(keepends=True)
        result: list[str] = []

        for line in lines:
            # Simple check: if line has #, check if it's in a string
            if "#" not in line:
                result.append(line)
                continue

            # Check if # is inside a string literal
            in_string = False
            string_char = None
            escape_next = False
            comment_pos = -1

            for i, char in enumerate(line):
                if escape_next:
                    escape_next = False
                    continue

                if char == "\\":
                    escape_next = True
                    continue

                if not in_string:
                    if char in ('"', "'"):
                        in_string = True
                        string_char = char
                    elif char == "#":
                        comment_pos = i
                        break
                elif char == string_char:
                    in_string = False
                    string_char = None

            if comment_pos >= 0 and not in_string:
                # Found comment outside string - remove it
                code_part = line[:comment_pos].rstrip()
                if code_part:
                    # Has code before comment - keep code part
                    result.append(code_part + ("\n" if line.endswith("\n") else ""))
                # If no code part, this is a standalone comment - remove entirely
            else:
                # No comment found or comment is in string - keep line
                result.append(line)

        return "".join(result)

    # Pattern for ignore comments (case-insensitive)
    # Matches: noqa, type: ignore, pyright: ignore, mypy: ignore,
    # ruff noqa, serger: no-move, etc.
    # Note: This pattern matches the comment part AFTER the #
    ignore_pattern = re.compile(
        r"^\s*(noqa|type:\s*ignore|pyright:\s*ignore|mypy:\s*ignore|ruff:\s*noqa|serger:\s*no-move)",
        re.IGNORECASE,
    )

    lines = text.splitlines(keepends=True)
    output_lines: list[str] = []

    for line in lines:
        # Check if line has code before comment
        if "#" in line:
            # Split at first # to get code and comment parts
            parts = line.split("#", 1)
            code_part = parts[0].rstrip()
            comment_part = parts[1] if len(parts) > 1 else ""
            has_code = bool(code_part)
        else:
            # No comment - keep the line as-is
            output_lines.append(line)
            continue

        if mode == "inline":
            # Keep only inline comments (comments on same line as code)
            if has_code:
                # Has code, so any comment is inline - keep the whole line
                output_lines.append(line)
            # If no code, this is a standalone comment - remove entirely
        elif mode == "ignores":
            # Keep only ignore comments
            if ignore_pattern.match(comment_part):
                # This is an ignore comment - keep it
                output_lines.append(line)
            elif has_code:
                # Has code but comment is not an ignore - keep code, remove comment
                output_lines.append(code_part + ("\n" if line.endswith("\n") else ""))
            # If no code and not an ignore comment, remove entirely
        else:
            # Unknown mode - keep as-is
            output_lines.append(line)

    return "".join(output_lines)


def process_docstrings(text: str, mode: DocstringMode) -> str:  # noqa: C901, PLR0915
    """Process docstrings in source code according to the specified mode.

    Args:
        text: Python source code
        mode: Docstring processing mode:
            - "keep": Keep all docstrings (default)
            - "strip": Remove all docstrings
            - "public": Keep only public docstrings (not prefixed with underscore)
            - dict: Per-location control, e.g., {"module": "keep", "class": "strip"}
              Valid locations: "module", "class", "function", "method"
              Each location value can be "keep", "strip", or "public"
              Omitted locations default to "keep"

    Returns:
        Source code with docstrings processed according to mode
    """
    logger = getAppLogger()

    # Handle simple string modes
    if isinstance(mode, str):
        if mode == "keep":
            return text

        # Normalize to dict format for processing
        mode_dict: dict[DocstringModeLocation, DocstringModeSimple] = {
            "module": mode,
            "class": mode,
            "function": mode,
            "method": mode,
        }
    else:
        # Dict mode - fill in defaults for omitted locations
        mode_dict = {
            "module": mode.get("module", "keep"),
            "class": mode.get("class", "keep"),
            "function": mode.get("function", "keep"),
            "method": mode.get("method", "keep"),
        }

    # Parse AST to find docstrings
    try:
        tree = ast.parse(text)
    except SyntaxError:
        logger.exception("Failed to parse file for docstring processing")
        return text

    # Build parent map to distinguish methods from functions
    parent_map: dict[ast.AST, ast.AST] = {}

    def build_parent_map(parent: ast.AST) -> None:
        """Recursively build parent mapping."""
        for child in ast.iter_child_nodes(parent):
            parent_map[child] = parent
            build_parent_map(child)

    build_parent_map(tree)

    lines = text.splitlines(keepends=True)
    # Track line ranges to remove (start, end) inclusive
    ranges_to_remove: list[tuple[int, int]] = []

    def get_docstring_node(node: ast.AST) -> ast.Expr | None:
        """Get the docstring node if it exists as the first statement."""
        # Type guard: only nodes with body attribute can have docstrings
        if not isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            return None
        if not node.body:
            return None
        first_stmt = node.body[0]
        if (
            isinstance(first_stmt, ast.Expr)
            and isinstance(first_stmt.value, ast.Constant)
            and isinstance(first_stmt.value.value, str)
        ):
            return first_stmt
        return None

    def is_public(name: str) -> bool:
        """Check if a name is public (doesn't start with underscore)."""
        return not name.startswith("_")

    def get_location_type(node: ast.AST) -> DocstringModeLocation | None:
        """Determine the location type of a docstring node.

        Note: "method" covers all functions inside classes, including:
        - Regular methods
        - Properties (@property)
        - Static methods (@staticmethod)
        - Class methods (@classmethod)
        - Async methods (async def)
        """
        if isinstance(node, ast.Module):
            return "module"
        if isinstance(node, ast.ClassDef):
            return "class"
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Check if function is inside a class (method) or top-level (function)
            # This covers all method types: regular, @property, @staticmethod, etc.
            parent = parent_map.get(node)
            if isinstance(parent, ast.ClassDef):
                return "method"
            return "function"
        return None

    def should_remove_docstring(
        location: DocstringModeLocation,
        name: str,
    ) -> bool:
        """Determine if a docstring should be removed based on mode."""
        location_mode = mode_dict[location]

        if location_mode == "keep":
            return False
        if location_mode == "strip":
            return True
        if location_mode == "public":
            # Module docstrings are always considered public
            if location == "module":
                return False
            # Remove if not public
            return not is_public(name)
        # Unknown mode - keep it
        return False

    # Process module-level docstring
    module_docstring = get_docstring_node(tree)
    if module_docstring:
        location: DocstringModeLocation = "module"
        if should_remove_docstring(location, "__module__"):
            # Get line range for docstring
            start_line = module_docstring.lineno - 1  # 0-indexed
            end_line = (
                module_docstring.end_lineno - 1
                if module_docstring.end_lineno
                else start_line
            )
            ranges_to_remove.append((start_line, end_line))

    # Process class and function/method docstrings
    def process_node(node: ast.AST) -> None:
        """Recursively process nodes to find docstrings."""
        # Skip module docstring - it's already processed above
        if isinstance(node, ast.Module):
            # Just recurse into children, don't process module docstring again
            for child in node.body:
                process_node(child)
            return

        docstring = get_docstring_node(node)
        if docstring:
            location = get_location_type(node)
            if location:
                name = ""
                if isinstance(
                    node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                ):
                    name = node.name

                if should_remove_docstring(location, name):
                    # Get line range for docstring
                    start_line = docstring.lineno - 1  # 0-indexed
                    end_line = (
                        docstring.end_lineno - 1 if docstring.end_lineno else start_line
                    )
                    ranges_to_remove.append((start_line, end_line))

        # Recurse into child nodes
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            for child in node.body:
                process_node(child)

    process_node(tree)

    # If no ranges to remove, return original text
    if not ranges_to_remove:
        return text

    # Sort ranges by start line (descending) so we can remove from end to start
    # This preserves line numbers while removing
    ranges_to_remove.sort(reverse=True)

    # Remove docstrings from text
    result_lines = lines[:]
    for start_line, end_line in ranges_to_remove:
        # Remove the range (inclusive)
        del result_lines[start_line : end_line + 1]

    return "".join(result_lines)


@dataclass
class ModuleSymbols:
    """Top-level symbols extracted from a Python module."""

    functions: set[str]
    classes: set[str]
    assignments: set[str]


def _extract_top_level_symbols(code: str) -> ModuleSymbols:
    """Extract top-level symbols from Python source code.

    Parses AST once and extracts functions, classes, and assignments.

    Args:
        code: Python source code to parse

    Returns:
        ModuleSymbols containing sets of function, class, and assignment names
    """
    functions: set[str] = set()
    classes: set[str] = set()
    assignments: set[str] = set()

    try:
        tree = ast.parse(code)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.add(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.add(node.name)
            elif isinstance(node, ast.Assign):
                # only consider simple names like x = ...
                targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
                for target in targets:
                    assignments.add(target)
    except (SyntaxError, ValueError):
        # If code doesn't parse, return empty sets
        pass

    return ModuleSymbols(
        functions=functions,
        classes=classes,
        assignments=assignments,
    )


def detect_name_collisions(
    module_symbols: dict[str, ModuleSymbols],
    *,
    ignore_functions: set[str] | None = None,
) -> None:
    """Detect top-level name collisions across modules.

    Checks for functions, classes, and simple assignments that would
    conflict when stitched together.

    Args:
        module_symbols: Dict mapping module names to their extracted symbols
        ignore_functions: Optional set of function names to ignore when checking
            collisions (e.g., when auto-rename will handle them)

    Raises:
        RuntimeError: If collisions are detected
    """
    # list of harmless globals we don't mind having overwritten
    ignore = {
        "__all__",
        "__version__",
        "__author__",
        "__authors__",
        "__path__",
        "__package__",
        "__commit__",
    }

    symbols: dict[str, str] = {}  # name -> module
    collisions: list[tuple[str, str, str]] = []
    ignore_funcs = ignore_functions or set()

    # Sort module names for deterministic iteration order
    for mod, symbols_data in sorted(module_symbols.items()):
        # Check all symbol types (functions, classes, assignments)
        all_names = (
            symbols_data.functions | symbols_data.classes | symbols_data.assignments
        )

        # Sort for deterministic iteration order
        for name in sorted(all_names):
            # skip known harmless globals
            if name in ignore:
                continue

            # Skip function names that will be auto-renamed
            # (only skip if it's a function collision, not class/assignment)
            if name in ignore_funcs and name in symbols_data.functions:
                continue

            prev = symbols.get(name)
            if prev:
                collisions.append((name, prev, mod))
            else:
                symbols[name] = mod

    if collisions:
        # Sort collisions by name for deterministic error messages
        sorted_collisions = sorted(collisions, key=lambda x: x[0])
        collision_list = ", ".join(f"{name!r}" for name, _, _ in sorted_collisions)
        msg = f"Top-level name collisions detected: {collision_list}"
        raise RuntimeError(msg)


def verify_all_modules_listed(
    file_paths: list[Path], order_paths: list[Path], exclude_paths: list[Path]
) -> None:
    """Ensure all included files are listed in order or exclude paths.

    Args:
        file_paths: List of all included file paths
        order_paths: List of file paths in stitch order
        exclude_paths: List of file paths to exclude

    Raises:
        RuntimeError: If unlisted files are found
    """
    file_set = set(file_paths)
    order_set = set(order_paths)
    exclude_set = set(exclude_paths)
    known = order_set | exclude_set
    unknown = file_set - known

    if unknown:
        unknown_list = ", ".join(str(p) for p in sorted(unknown))
        msg = f"Unlisted source files detected: {unknown_list}"
        raise RuntimeError(msg)


def _resolve_relative_import(node: ast.ImportFrom, current_module: str) -> str | None:
    """Resolve relative import to absolute module name.

    Args:
        node: The ImportFrom AST node
        current_module: The current module name (e.g., "serger.actions")

    Returns:
        Resolved absolute module name, or None if relative import goes
        beyond package root
    """
    if node.level == 0:
        # Not a relative import
        return node.module or ""

    # Resolve relative import to absolute module name
    # e.g., from .constants in serger.actions -> serger.constants
    current_parts = current_module.split(".")
    # Go up 'level' levels from current module
    if node.level > len(current_parts):
        # Relative import goes beyond package root, skip
        return None
    base_parts = current_parts[: -node.level]
    if node.module:
        # Append the module name
        mod_parts = node.module.split(".")
        resolved_mod = ".".join(base_parts + mod_parts)
    else:
        # from . import something - use base only
        resolved_mod = ".".join(base_parts)
    return resolved_mod


def _is_internal_import(module_name: str, detected_packages: set[str]) -> bool:
    """Check if an import is internal (starts with detected package).

    Args:
        module_name: The module name to check
        detected_packages: Set of detected package names

    Returns:
        True if module_name equals or starts with any detected package
    """
    # Sort packages for deterministic iteration order
    for pkg in sorted(detected_packages):
        # Match only if mod equals pkg or starts with pkg + "."
        # This prevents false matches where a module name happens to
        # start with a package name (e.g., "foo_bar" matching "foo")
        if module_name == pkg or module_name.startswith(pkg + "."):
            return True
    return False


def _extract_import_module_info(  # pyright: ignore[reportUnusedFunction]
    node: ast.Import | ast.ImportFrom,
    current_module: str,
    detected_packages: set[str],
) -> tuple[str, bool] | None:
    """Extract module name and whether it's internal from import node.

    Args:
        node: The Import or ImportFrom AST node
        current_module: The current module name
        detected_packages: Set of detected package names

    Returns:
        Tuple of (module_name, is_internal), or None if not relevant
    """
    if isinstance(node, ast.ImportFrom):
        # Handle relative imports (node.level > 0)
        if node.level > 0:
            resolved_mod = _resolve_relative_import(node, current_module)
            if resolved_mod is None:
                # Relative import goes beyond package root
                return None
            mod = resolved_mod
        else:
            # Absolute import
            mod = node.module or ""

        # Check if import is internal
        is_internal = _is_internal_import(mod, detected_packages)
        return (mod, is_internal)

    if isinstance(node, ast.Import):  # pyright: ignore[reportUnnecessaryIsInstance]
        # For Import nodes, we need to check each alias
        # But this function returns a single result, so we'll handle
        # the first alias (caller can iterate if needed)
        if not node.names:
            return None
        mod = node.names[0].name
        # Check if import starts with any detected package
        # Note: Import nodes use startswith(pkg) not startswith(pkg + ".")
        # This is different from ImportFrom matching logic
        is_internal = False
        # Sort packages for deterministic iteration order
        for pkg in sorted(detected_packages):
            if mod.startswith(pkg):
                is_internal = True
                break
        return (mod, is_internal)

    return None


def _extract_internal_imports_for_deps(  # noqa: PLR0912
    source: str,
    module_name: str,
    detected_packages: set[str],
) -> set[str]:
    """Extract internal import module names for dependency graph building.

    This is a "dumb" extraction function that extracts only raw data - the
    set of internal module names that this module imports. The matching logic
    (checking against existing modules) is handled by the caller.

    Args:
        source: Source code of the module
        module_name: The current module name (e.g., "serger.actions")
        detected_packages: Set of detected package names

    Returns:
        Set of internal module names that this module imports (resolved from
        relative imports if needed). Includes relative imports that resolve to
        simple names (no dots) even if not package-prefixed, as they may match
        existing modules.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()

    internal_imports: set[str] = set()

    # Use ast.walk() to find ALL imports, including those inside
    # if/else blocks, functions, etc. This is necessary because
    # imports inside conditionals (like "if not __STANDALONE__: from .x import y")
    # still represent dependencies that affect module ordering.
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            # Handle relative imports (node.level > 0)
            if node.level > 0:
                resolved_mod = _resolve_relative_import(node, module_name)
                if resolved_mod is None:
                    # Relative import goes beyond package root, skip
                    continue
                mod = resolved_mod
                # Check if relative import resolved to a simple name (no dots)
                # These may match existing modules even if not package-prefixed
                is_relative_resolved = mod and "." not in mod
            else:
                # Absolute import
                mod = node.module or ""
                is_relative_resolved = False

            # Check if import is internal (matches a detected package)
            matched_package = None
            # Sort packages for deterministic iteration order
            for pkg in sorted(detected_packages):
                # Match only if mod equals pkg or starts with pkg + "."
                # This prevents false matches where a module name happens to
                # start with a package name (e.g., "foo_bar" matching "foo")
                if mod == pkg or mod.startswith(pkg + "."):
                    matched_package = pkg
                    break

            # If relative import resolved to a simple name (no dots), include it
            # even if not package-prefixed, as it may match existing modules
            if is_relative_resolved and not matched_package:
                internal_imports.add(mod)
            elif matched_package:
                # Include the resolved module name for package-based matching
                internal_imports.add(mod)

        elif isinstance(node, ast.Import):
            # For Import nodes, check each alias
            for alias in node.names:
                mod = alias.name
                # Check if import starts with any detected package
                # Note: Import nodes use startswith(pkg) not startswith(pkg + ".")
                # This is different from ImportFrom matching logic
                # Sort packages for deterministic iteration order
                for pkg in sorted(detected_packages):
                    if mod.startswith(pkg):
                        internal_imports.add(mod)
                        break

    return internal_imports


def _deterministic_topological_sort(
    deps: dict[str, set[str]],
    module_to_file: dict[str, Path],
) -> list[str]:
    """Perform deterministic topological sort using file path as tie-breaker.

    When multiple nodes have zero in-degree, they are sorted by their file path
    to ensure deterministic ordering. This guarantees reproducible builds even
    when multiple valid topological orderings exist.

    Args:
        deps: Dependency graph mapping module names to sets of dependencies
        module_to_file: Mapping from module names to file paths

    Returns:
        Topologically sorted list of module names

    Raises:
        RuntimeError: If circular imports are detected
    """
    # Calculate in-degrees for all nodes
    # In-degree = number of dependencies this node has (how many nodes it depends on)
    in_degree: dict[str, int] = {
        node: len(node_deps) for node, node_deps in deps.items()
    }

    # Build reverse dependency graph for efficient edge removal
    # reverse_deps[dep] = set of nodes that depend on dep
    reverse_deps: dict[str, set[str]] = {node: set() for node in deps}
    for node, node_deps in deps.items():
        for dep in node_deps:
            if dep in reverse_deps:
                reverse_deps[dep].add(node)

    # Start with nodes that have zero in-degree (no dependencies)
    # Sort by file path to ensure deterministic ordering
    zero_in_degree = [node for node, degree in in_degree.items() if degree == 0]
    zero_in_degree.sort(key=lambda node: str(module_to_file.get(node, Path())))

    result: list[str] = []

    while zero_in_degree:
        # Process nodes in sorted order (by file path) for determinism
        # Sort again before processing to maintain determinism
        zero_in_degree.sort(key=lambda node: str(module_to_file.get(node, Path())))
        node = zero_in_degree.pop(0)
        result.append(node)

        # Remove edges from this node and update in-degrees of dependents
        # When we process a node, all nodes that depend on it can have their
        # in-degree decremented (since this dependency is now satisfied)
        for dependent in reverse_deps.get(node, set()):
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                zero_in_degree.append(dependent)

    # Check for circular dependencies
    if len(result) != len(deps):
        # Find nodes that weren't processed (part of a cycle)
        remaining = set(deps) - set(result)
        msg = f"Circular dependency detected involving: {sorted(remaining)}"
        raise RuntimeError(msg)

    return result


def compute_module_order(  # noqa: C901, PLR0912
    file_paths: list[Path],
    package_root: Path,
    _package_name: str,
    file_to_include: dict[Path, IncludeResolved],
    *,
    detected_packages: set[str],
    source_bases: list[str] | None = None,
    user_provided_source_bases: list[str] | None = None,
) -> list[Path]:
    """Compute correct module order based on import dependencies.

    Uses topological sorting of internal imports to determine the correct
    order for stitching.

    Args:
        file_paths: List of file paths in initial order
        package_root: Common root of all included files
        _package_name: Root package name (unused, kept for API consistency)
        file_to_include: Mapping of file path to its include (for dest access)
        detected_packages: Pre-detected package names
        source_bases: Optional list of module base directories for external files
        user_provided_source_bases: Optional list of user-provided module bases
            (from config, excludes auto-discovered package directories)

    Returns:
        Topologically sorted list of file paths

    Raises:
        RuntimeError: If circular imports are detected
    """
    logger = getAppLogger()
    # Map file paths to derived module names
    file_to_module: dict[Path, str] = {}
    module_to_file: dict[str, Path] = {}
    for file_path in file_paths:
        include = file_to_include.get(file_path)
        module_name = derive_module_name(
            file_path,
            package_root,
            include,
            source_bases=source_bases,
            user_provided_source_bases=user_provided_source_bases,
            detected_packages=detected_packages,
        )
        file_to_module[file_path] = module_name
        module_to_file[module_name] = file_path

    # Build dependency graph using derived module names
    # file_paths is already sorted from collect_included_files, so dict insertion
    # order is deterministic
    deps: dict[str, set[str]] = {file_to_module[fp]: set() for fp in file_paths}

    for file_path in file_paths:
        module_name = file_to_module[file_path]
        if not file_path.exists():
            continue

        try:
            source = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        # Extract internal imports using the extraction function
        # This parses the AST once and extracts all internal module names
        internal_imports = _extract_internal_imports_for_deps(
            source, module_name, detected_packages
        )

        # Build dependency graph from extracted imports
        # The matching logic (checking against existing modules) stays here
        for mod in sorted(internal_imports):
            # Check if this is a relative import that resolved to a simple name
            # (no dots) - these may match existing modules directly
            is_relative_resolved = "." not in mod

            # Check if import matches a detected package
            matched_package = None
            # Sort packages for deterministic iteration order
            for pkg in sorted(detected_packages):
                # Match only if mod equals pkg or starts with pkg + "."
                # This prevents false matches where a module name happens to
                # start with a package name (e.g., "foo_bar" matching "foo")
                if mod == pkg or mod.startswith(pkg + "."):
                    matched_package = pkg
                    break

            logger.trace(
                "[DEPS] %s imports %s: matched_package=%s, is_relative_resolved=%s",
                module_name,
                mod,
                matched_package,
                is_relative_resolved,
            )

            # If relative import resolved to a simple name (no dots), check if it
            # matches any module name directly (for same-package imports)
            if not matched_package and is_relative_resolved:
                # Check if the resolved module name matches any module directly
                logger.trace(
                    "[DEPS] Relative import in %s: resolved_mod=%s, checking deps",
                    module_name,
                    mod,
                )
                # Sort for deterministic iteration order
                for dep_module in sorted(deps.keys()):
                    # Match if dep_module equals mod or starts with mod.
                    if (
                        dep_module == mod or dep_module.startswith(mod + ".")
                    ) and dep_module != module_name:
                        logger.trace(
                            "[DEPS] Found dependency: %s -> %s (from %s)",
                            module_name,
                            dep_module,
                            mod,
                        )
                        deps[module_name].add(dep_module)
                continue  # Skip the package-based matching below

            if matched_package:
                # Handle nested imports: package.core.base -> core.base
                # Remove package prefix and check if it matches any module
                mod_suffix = (
                    mod[len(matched_package) + 1 :]
                    if mod.startswith(matched_package + ".")
                    else mod[len(matched_package) :]
                    if mod == matched_package
                    else ""
                )
                if mod_suffix:
                    # Check if this matches any derived module name
                    # Match both the suffix (for same-package imports)
                    # and full module name (for cross-package imports)
                    # Sort for deterministic iteration order
                    for dep_module in sorted(deps.keys()):
                        # Match if: dep_module equals mod_suffix or mod
                        # or dep_module starts with mod_suffix or mod
                        prefix_tuple = (mod_suffix + ".", mod + ".")
                        matches = dep_module in (
                            mod_suffix,
                            mod,
                        ) or dep_module.startswith(prefix_tuple)
                        if matches and dep_module != module_name:
                            deps[module_name].add(dep_module)
                else:
                    # mod == matched_package
                    # (e.g., "from apathetic_logging import Logger")
                    # This is a package-level import, so depend on package.__init__
                    # (package-level imports need package.__init__ loaded first)
                    # Sort for deterministic iteration order
                    for dep_module in sorted(deps.keys()):
                        # Match if dep_module equals the package or starts with
                        # package + "." This ensures package-level imports depend
                        # on package.__init__
                        if (
                            dep_module == matched_package
                            or dep_module.startswith(matched_package + ".")
                        ) and dep_module != module_name:
                            logger.trace(
                                "[DEPS] Package-level import: %s -> %s (from %s)",
                                module_name,
                                dep_module,
                                mod,
                            )
                            deps[module_name].add(dep_module)

    # Perform deterministic topological sort using file path as tie-breaker
    # This ensures reproducible builds even when multiple valid orderings exist
    topo_modules = _deterministic_topological_sort(deps, module_to_file)

    # Convert back to file paths
    topo_paths = [module_to_file[mod] for mod in topo_modules if mod in module_to_file]
    return topo_paths


def suggest_order_mismatch(
    order_paths: list[Path],
    package_root: Path,
    _package_name: str,
    file_to_include: dict[Path, IncludeResolved],
    *,
    detected_packages: set[str],
    topo_paths: list[Path] | None = None,
    source_bases: list[str] | None = None,
    user_provided_source_bases: list[str] | None = None,
) -> None:
    """Warn if module order violates dependencies.

    Args:
        order_paths: List of file paths in intended order
        package_root: Common root of all included files
        _package_name: Root package name (unused, kept for API consistency)
        file_to_include: Mapping of file path to its include (for dest access)
        detected_packages: Pre-detected package names
        topo_paths: Optional pre-computed topological order. If provided,
                    skips recomputing the order. If None, computes it via
                    compute_module_order.
        source_bases: Optional list of module base directories for external files
        user_provided_source_bases: Optional list of user-provided module bases
            (from config, excludes auto-discovered package directories)
    """
    logger = getAppLogger()
    if topo_paths is None:
        topo_paths = compute_module_order(
            order_paths,
            package_root,
            _package_name,
            file_to_include,
            detected_packages=detected_packages,
            source_bases=source_bases,
        )

    # compare order_paths to topological sort
    mismatched = [
        p
        for p in order_paths
        if p in topo_paths and topo_paths.index(p) != order_paths.index(p)
    ]
    if mismatched:
        logger.warning("Possible module misordering detected:")

        for p in mismatched:
            include = file_to_include.get(p)
            module_name = derive_module_name(
                p,
                package_root,
                include,
                source_bases=source_bases,
                user_provided_source_bases=user_provided_source_bases,
                detected_packages=detected_packages,
            )
            logger.warning("  - %s appears before one of its dependencies", module_name)
        topo_modules = [
            derive_module_name(
                p,
                package_root,
                file_to_include.get(p),
                source_bases=source_bases,
                user_provided_source_bases=user_provided_source_bases,
                detected_packages=detected_packages,
            )
            for p in topo_paths
        ]
        logger.warning("Suggested order: %s", ", ".join(topo_modules))


def _is_inside_string_literal(text: str, pos: int) -> bool:
    """Check if a position in text is inside a string literal.

    Args:
        text: Source text to check
        pos: Position to check

    Returns:
        True if position is inside a string literal, False otherwise
    """
    # Track string state by scanning from start
    in_string = False
    string_char = None
    escape_next = False
    triple_quote = False
    i = 0

    while i < pos:
        char = text[i]

        if escape_next:
            escape_next = False
            i += 1
            continue

        if char == "\\":
            escape_next = True
            i += 1
            continue

        if not in_string:
            # Check for triple quotes first
            if i < len(text) - 2:
                triple_start = text[i : i + 3]
                if triple_start in ('"""', "'''"):
                    in_string = True
                    string_char = triple_start[0]
                    triple_quote = True
                    # Skip next two chars
                    i += 3
                    continue
            # Check for single quotes
            if char in ('"', "'"):
                in_string = True
                string_char = char
                triple_quote = False
        # Inside string - check for end
        elif triple_quote:
            if i < len(text) - 2 and string_char is not None:
                triple_end = text[i : i + 3]
                if triple_end == string_char * 3:
                    in_string = False
                    string_char = None
                    triple_quote = False
                    # Skip next two chars
                    i += 3
                    continue
        elif char == string_char:
            in_string = False
            string_char = None

        i += 1

    return in_string


def verify_no_broken_imports(  # noqa: C901, PLR0912
    final_text: str,
    package_names: list[str],
    internal_imports: InternalImportMode | None = None,
) -> None:
    """Verify all internal imports have been resolved in stitched script.

    Args:
        final_text: Final stitched script text
        package_names: List of all package names to check
            (e.g., ["serger", "apathetic_logs"])
        internal_imports: How internal imports are handled. If "keep", validation
            is skipped for kept imports since they are intentionally preserved.

    Raises:
        RuntimeError: If unresolved imports remain
    """
    # When internal_imports is "keep", skip validation for kept imports
    # since they are intentionally preserved and will work at runtime
    if internal_imports == "keep":
        return

    broken: set[str] = set()

    for package_name in package_names:
        # Pattern for nested imports: package.core.base or package.core
        # Matches: import package.module or import package.sub.module
        import_pattern = re.compile(rf"\bimport {re.escape(package_name)}\.([\w.]+)")
        # Pattern for top-level package import: import package
        # Matches: import package (without "from" and without a dot)
        import_package_pattern = re.compile(
            rf"\bimport {re.escape(package_name)}\b(?!\s*\.)"
        )
        # Pattern for from imports: from package.core import base or
        # from package.core.base import something
        from_pattern = re.compile(
            rf"\bfrom {re.escape(package_name)}\.([\w.]+)\s+import"
        )
        # Pattern for top-level package imports: from package import ...
        top_level_pattern = re.compile(rf"\bfrom {re.escape(package_name)}\s+import")

        # Helper to check if a module exists (header or shim)
        def module_exists(full_module_name: str, mod_suffix: str | None = None) -> bool:
            """Check if a module exists via header or shim."""
            # Check for header
            header_pattern_full = re.compile(
                rf"# === {re.escape(full_module_name)} ==="
            )
            if header_pattern_full.search(final_text):
                return True

            # Check for suffix header (backward compat)
            if mod_suffix:
                header_pattern_suffix = re.compile(
                    rf"# === {re.escape(mod_suffix)} ==="
                )
                if header_pattern_suffix.search(final_text):
                    return True

            # Check for shim
            escaped_name = re.escape(full_module_name)
            shim_pattern_old = re.compile(
                rf"_pkg\s*=\s*(?:['\"]){escaped_name}(?:['\"]).*?"
                rf"sys\.modules\[_pkg\]\s*=\s*_mod",
                re.DOTALL,
            )
            shim_pattern_new = re.compile(
                rf"_create_pkg_module\s*\(\s*(?:['\"]){escaped_name}(?:['\"])"
            )
            return (
                shim_pattern_old.search(final_text) is not None
                or shim_pattern_new.search(final_text) is not None
            )

        # Check import statements (nested: import package.module)
        for m in import_pattern.finditer(final_text):
            # Skip if inside string literal (docstring/comment)
            if _is_inside_string_literal(final_text, m.start()):
                continue

            mod_suffix = m.group(1)
            full_module_name = f"{package_name}.{mod_suffix}"
            if not module_exists(full_module_name, mod_suffix):
                broken.add(full_module_name)

        # Check top-level package import: import package
        for m in import_package_pattern.finditer(final_text):
            # Skip if inside string literal (docstring/comment)
            if _is_inside_string_literal(final_text, m.start()):
                continue

            # For top-level package imports, check if the package itself exists
            # This would be in a header like # === package === or
            # # === package.__init__ ===
            # OR it could be created via shims (when __init__.py is excluded)
            header_pattern = re.compile(
                rf"# === {re.escape(package_name)}(?:\.__init__)? ==="
            )
            # Check for shim-created package:
            # Old pattern: _pkg = 'package_name' followed by sys.modules[_pkg] = _mod
            # New pattern: _create_pkg_module('package_name')
            # Handle both single and double quotes (formatter may change them)
            escaped_name = re.escape(package_name)
            shim_pattern_old = re.compile(
                rf"_pkg\s*=\s*(?:['\"]){escaped_name}(?:['\"]).*?"
                rf"sys\.modules\[_pkg\]\s*=\s*_mod",
                re.DOTALL,
            )
            shim_pattern_new = re.compile(
                rf"_create_pkg_module\s*\(\s*(?:['\"]){escaped_name}(?:['\"])"
            )
            if (
                not header_pattern.search(final_text)
                and not shim_pattern_old.search(final_text)
                and not shim_pattern_new.search(final_text)
            ):
                broken.add(package_name)

        # Check from ... import statements
        for m in from_pattern.finditer(final_text):
            # Skip if inside string literal (docstring/comment)
            if _is_inside_string_literal(final_text, m.start()):
                continue

            mod_suffix = m.group(1)
            full_module_name = f"{package_name}.{mod_suffix}"
            if not module_exists(full_module_name, mod_suffix):
                broken.add(full_module_name)

        # Check top-level package imports: from package import ...
        for m in top_level_pattern.finditer(final_text):
            # Skip if inside string literal (docstring/comment)
            if _is_inside_string_literal(final_text, m.start()):
                continue

            # For top-level imports, check if the package itself exists
            # This would be in a header like # === package === or
            # # === package.__init__ ===
            # OR it could be created via shims (when __init__.py is excluded)
            header_pattern = re.compile(
                rf"# === {re.escape(package_name)}(?:\.__init__)? ==="
            )
            # Check for shim-created package:
            # Old pattern: _pkg = 'package_name' followed by sys.modules[_pkg] = _mod
            # New pattern: _create_pkg_module('package_name')
            # Handle both single and double quotes (formatter may change them)
            escaped_name = re.escape(package_name)
            shim_pattern_old = re.compile(
                rf"_pkg\s*=\s*(?:['\"]){escaped_name}(?:['\"]).*?"
                rf"sys\.modules\[_pkg\]\s*=\s*_mod",
                re.DOTALL,
            )
            shim_pattern_new = re.compile(
                rf"_create_pkg_module\s*\(\s*(?:['\"]){escaped_name}(?:['\"])"
            )
            if (
                not header_pattern.search(final_text)
                and not shim_pattern_old.search(final_text)
                and not shim_pattern_new.search(final_text)
            ):
                broken.add(package_name)

    if broken:
        broken_list = ", ".join(sorted(broken))
        msg = f"Unresolved internal imports: {broken_list}"
        raise RuntimeError(msg)


def _find_package_root_for_file(
    file_path: Path,
    *,
    source_bases: list[str] | None = None,
    _config_dir: Path | None = None,
) -> Path | None:
    """Find the package root for a file.

    First checks for __init__.py files (definitive package marker).
    If no __init__.py found and file is under a source_bases directory,
    treats everything after the matching base prefix as a package structure.

    Args:
        file_path: Path to the Python file
        source_bases: Optional list of module base directories (absolute paths)
        _config_dir: Optional config directory (unused, kept for compatibility)

    Returns:
        Path to the package root directory, or None if not found
    """
    logger = getAppLogger()
    file_path_resolved = file_path.resolve()
    current_dir = file_path_resolved.parent
    last_package_dir: Path | None = None

    logger.trace(
        "[PKG_ROOT] Finding package root for %s, starting from %s",
        file_path.name,
        current_dir,
    )

    # First, walk up looking for __init__.py (definitive package marker)
    # __init__.py always takes precedence
    while True:
        # Check if current directory has __init__.py
        init_file = current_dir / "__init__.py"
        if init_file.exists():
            # This directory is part of a package
            last_package_dir = current_dir
            logger.trace(
                "[PKG_ROOT] Found __init__.py at %s (package root so far: %s)",
                current_dir,
                last_package_dir,
            )
        # This directory doesn't have __init__.py
        # If we found a package via __init__.py, return it
        elif last_package_dir is not None:
            logger.trace(
                "[PKG_ROOT] No __init__.py at %s, package root: %s",
                current_dir,
                last_package_dir,
            )
            return last_package_dir
            # No __init__.py found yet, continue walking up
            # (we'll check source_bases after this loop if needed)

        # Move up one level
        parent = current_dir.parent
        if parent == current_dir:
            # Reached filesystem root
            if last_package_dir is not None:
                logger.trace(
                    "[PKG_ROOT] Reached filesystem root, package root: %s",
                    last_package_dir,
                )
                return last_package_dir
            # No __init__.py found, break to check source_bases
            break
        current_dir = parent

    # If no __init__.py found, check if file is under any source_bases directory
    if source_bases and last_package_dir is None:
        for base_str in source_bases:
            # base_str is already an absolute path
            base_path = Path(base_str).resolve()
            try:
                # Check if file is under this base
                rel_path = file_path_resolved.relative_to(base_path)
                # If file is directly in base (e.g., src/mymodule.py), no package
                if len(rel_path.parts) == 1:
                    # Single file in base - not a package
                    continue
                # File is in a subdirectory of base (e.g., src/mypkg/submodule.py)
                # The first part after base is the package
                package_dir = base_path / rel_path.parts[0]
                if package_dir.exists() and package_dir.is_dir():
                    logger.trace(
                        "[PKG_ROOT] Found package via source_bases: %s (base: %s)",
                        package_dir,
                        base_path,
                    )
                    return package_dir
            except ValueError:
                # File is not under this base, continue to next base
                continue

    # Return None if no package found
    return last_package_dir


def detect_packages_from_files(  # noqa: PLR0912, C901, PLR0915
    file_paths: list[Path],
    package_name: str,
    *,
    source_bases: list[str] | None = None,
    _config_dir: Path | None = None,
) -> tuple[set[str], list[str]]:
    """Detect packages from file paths.

    If files are under source_bases directories, treats everything after the
    matching base prefix as a package structure (regardless of __init__.py).
    Otherwise, follows Python's import rules: only detects regular packages
    (with __init__.py files). Falls back to configured package_name if none detected.

    Args:
        file_paths: List of file paths to check
        package_name: Configured package name (used as fallback)
        source_bases: Optional list of module base directories (absolute paths)
        _config_dir: Optional config directory (unused, kept for compatibility)

    Returns:
        Tuple of (set of detected package names, list of parent directories).
        Package names always includes package_name. Parent directories are
        returned as absolute paths, deduplicated.
    """
    logger = getAppLogger()
    detected: set[str] = set()
    parent_dirs: list[Path] = []
    seen_parents: set[Path] = set()

    # Detect packages from files
    for file_path in file_paths:
        pkg_root = _find_package_root_for_file(file_path, source_bases=source_bases)
        if pkg_root:
            # Extract package name from directory name
            pkg_name = pkg_root.name
            detected.add(pkg_name)

            # Extract parent directory (module base)
            parent_dir = pkg_root.parent.resolve()
            # Check if parent is filesystem root (parent of root equals root)
            is_root = parent_dir.parent == parent_dir
            if not is_root and parent_dir not in seen_parents:
                seen_parents.add(parent_dir)
                parent_dirs.append(parent_dir)

            logger.trace(
                "[PKG_DETECT] Detected package %s from %s (root: %s, parent: %s)",
                pkg_name,
                file_path,
                pkg_root,
                parent_dir,
            )

    # Also detect directories in source_bases as packages if they contain
    # subdirectories that are packages (namespace packages)
    # This must happen BEFORE adding package_name to detected, so we can check
    # if base_name == package_name correctly
    # Compute common root of all files to avoid detecting it as a package
    common_root: Path | None = None
    if file_paths:
        common_root = file_paths[0].parent
        for file_path in file_paths[1:]:
            # Find common prefix of paths
            common_parts = [
                p
                for p, q in zip(common_root.parts, file_path.parent.parts, strict=False)
                if p == q
            ]
            if common_parts:
                common_root = Path(*common_parts)
            else:
                # No common root, use first file's parent
                common_root = file_paths[0].parent
                break
    if source_bases:
        for base_str in source_bases:
            base_path = Path(base_str).resolve()
            if not base_path.exists() or not base_path.is_dir():
                continue
            # Check if this base contains any detected packages as direct children
            base_name = base_path.name
            # Skip if base is filesystem root, empty name, already detected,
            # is package_name, or is the common root of all files
            if (
                not base_name
                or base_name in detected
                or base_name == package_name
                or base_path == base_path.parent  # filesystem root
                or (common_root and base_path == common_root.resolve())
            ):
                logger.trace(
                    "[PKG_DETECT] Skipping base %s: name=%s, in_detected=%s, "
                    "is_package_name=%s, is_common_root=%s",
                    base_path,
                    base_name,
                    base_name in detected,
                    base_name == package_name,
                    common_root and base_path == common_root.resolve(),
                )
                continue
            # Check if any detected package has this base as its parent
            for file_path in file_paths:
                pkg_root = _find_package_root_for_file(
                    file_path, source_bases=source_bases
                )
                if pkg_root:
                    pkg_parent = pkg_root.parent.resolve()
                    logger.trace(
                        "[PKG_DETECT] Checking base: %s (base_path=%s), "
                        "pkg_root=%s, pkg_parent=%s, match=%s",
                        base_name,
                        base_path,
                        pkg_root,
                        pkg_parent,
                        pkg_parent == base_path,
                    )
                    if pkg_parent == base_path:
                        # This base contains a detected package, so it's also a package
                        detected.add(base_name)
                        logger.trace(
                            "[PKG_DETECT] Detected base directory as package: %s "
                            "(contains package: %s)",
                            base_name,
                            pkg_root.name,
                        )
                        break

    # Always include configured package (for fallback and multi-package scenarios)
    detected.add(package_name)

    # Return parent directories as absolute paths
    normalized_parents: list[str] = []
    seen_normalized: set[str] = set()

    for parent_dir in parent_dirs:
        base_str = str(parent_dir)
        if base_str not in seen_normalized:
            seen_normalized.add(base_str)
            normalized_parents.append(base_str)

    if len(detected) == 1 and package_name in detected:
        logger.debug(
            "Package detection: No packages found, using configured package '%s'",
            package_name,
        )
    else:
        logger.debug(
            "Package detection: Found %d package(s): %s",
            len(detected),
            sorted(detected),
        )

    return detected, normalized_parents


def force_mtime_advance(path: Path, seconds: float = 1.0, max_tries: int = 50) -> None:
    """Reliably bump a file's mtime, preserving atime and nanosecond precision.

    Ensures the change is visible before returning, even on lazy filesystems.
    We often can't use os.sleep or time.sleep because we monkeypatch it.

    Args:
        path: Path to file whose mtime to advance
        seconds: How many seconds to advance mtime
        max_tries: Maximum number of attempts

    Raises:
        AssertionError: If mtime could not be advanced after max_tries
    """
    real_time = importlib.import_module("time")  # immune to monkeypatch
    old_m = path.stat().st_mtime_ns
    ns_bump = int(seconds * 1_000_000_000)
    new_m: int = old_m

    for _attempt in range(max_tries):
        st = path.stat()
        os.utime(path, ns=(int(st.st_atime_ns), int(st.st_mtime_ns + ns_bump)))
        os.sync()  # flush kernel metadata

        new_m = path.stat().st_mtime_ns
        if new_m > old_m:
            return  # ✅ success
        real_time.sleep(0.00001)  # 10 µs pause before recheck

    xmsg = (
        f"bump_mtime({path}) failed to advance mtime after {max_tries} attempts "
        f"(old={old_m}, new={new_m})",
    )
    raise AssertionError(xmsg)


def _collect_modules(  # noqa: PLR0912, PLR0915, C901
    file_paths: list[Path],
    package_root: Path,
    _package_name: str,
    file_to_include: dict[Path, IncludeResolved],
    detected_packages: set[str],
    external_imports: ExternalImportMode = "top",
    internal_imports: InternalImportMode = "force_strip",
    comments_mode: CommentsMode = "keep",
    docstring_mode: DocstringMode = "keep",
    source_bases: list[str] | None = None,
    user_provided_source_bases: list[str] | None = None,
) -> tuple[dict[str, str], OrderedDict[str, None], list[str], list[str]]:
    """Collect and process module sources from file paths.

    Args:
        file_paths: List of file paths to stitch (in order)
        package_root: Common root of all included files
        _package_name: Root package name (unused, kept for API consistency)
        file_to_include: Mapping of file path to its include (for dest access)
        detected_packages: Pre-detected package names
        external_imports: How to handle external imports
        internal_imports: How to handle internal imports
        comments_mode: How to handle comments in stitched output
        docstring_mode: How to handle docstrings in stitched output
        source_bases: Optional list of module base directories for external files
        user_provided_source_bases: Optional list of user-provided module bases
            (from config, excludes auto-discovered package directories)

    Returns:
        Tuple of (module_sources, all_imports, parts, derived_module_names)
    """
    logger = getAppLogger()
    all_imports: OrderedDict[str, None] = OrderedDict()
    module_sources: dict[str, str] = {}
    parts: list[str] = []
    derived_module_names: list[str] = []

    # Reserve imports for shim system and main entry point
    all_imports.setdefault("import sys\n", None)  # For shim system and main()
    all_imports.setdefault("import types\n", None)  # For shim system (ModuleType)

    # Convert to sorted list for consistent behavior
    package_names_list = sorted(detected_packages)

    # Check if package_root is a package directory itself
    # (when all files are in a single package, package_root is that package)
    is_package_dir = (package_root / "__init__.py").exists()
    package_name_from_root: str | None = None
    if is_package_dir:
        package_name_from_root = package_root.name
    # Also treat as package directory if package_root.name matches package
    # (even without __init__.py, files in package_root are submodules of package)
    elif package_root.name == _package_name:
        package_name_from_root = package_root.name
        is_package_dir = True  # Treat as package directory for module naming

    # Check if any files have imports that reference the package name
    # (indicates files are part of that package structure)
    has_package_imports = False
    if package_root.name != _package_name and package_root.name in (
        "src",
        "lib",
        "app",
        "package",
        "packages",
    ):
        # Quick check: see if any file imports from the package
        for file_path in file_paths:
            if not file_path.exists():
                continue
            try:
                content = file_path.read_text(encoding="utf-8")
                # Check for imports that reference the package name
                if (
                    f"from {_package_name}" in content
                    or f"import {_package_name}" in content
                ):
                    has_package_imports = True
                    break
            except Exception:  # noqa: BLE001, S110
                # If we can't read the file, skip the check
                pass

    for file_path in file_paths:
        if not file_path.exists():
            file_display = shorten_path_for_display(file_path)
            logger.warning("Skipping missing file: %s", file_display)
            continue

        # Derive module name from file path
        include = file_to_include.get(file_path)
        # Debug: log source_bases for external files
        if "site-packages" in str(file_path) or "dist-packages" in str(file_path):
            logger.trace(
                f"[COLLECT] Deriving module name for external file: {file_path}, "
                f"source_bases={source_bases}, "
                f"user_provided_source_bases={user_provided_source_bases}",
            )
        module_name = derive_module_name(
            file_path,
            package_root,
            include,
            source_bases=source_bases,
            user_provided_source_bases=user_provided_source_bases,
            detected_packages=detected_packages,
        )

        # Check if file is from an installed package (site-packages or dist-packages)
        # AND the module name already starts with a detected package that's not the
        # main package. In this case, the module name is already correct and should
        # not have the main package name prepended.
        # However, if the module name doesn't start with a detected package, we
        # should still prepend the main package name (e.g., stitching testpkg into
        # app package should create app.testpkg, not just testpkg).
        file_path_str = str(file_path)
        is_installed_package = (
            "site-packages" in file_path_str or "dist-packages" in file_path_str
        )
        is_external_package = False
        if is_installed_package:
            # Check if module name already starts with a detected package that's
            # not the main package (indicates it's already correctly structured)
            for pkg in sorted(detected_packages):
                if pkg != _package_name and (
                    module_name == pkg or module_name.startswith(f"{pkg}.")
                ):
                    is_external_package = True
                    logger.trace(
                        f"[COLLECT] Skipping package name prepending for installed "
                        f"package: module={module_name}, detected_pkg={pkg}, "
                        f"main_pkg={_package_name}",
                    )
                    break

        # Only apply package name prepending logic for files from the main package
        if not is_external_package:
            # If package_root is a package directory, preserve package structure
            if is_package_dir and package_name_from_root:
                # Handle __init__.py special case: represents the package itself
                if file_path.name == "__init__.py" and file_path.parent == package_root:
                    # Use package name as the module name (represents the package)
                    module_name = package_name_from_root
                else:
                    # Prepend package name to preserve structure
                    # e.g., "core" -> "oldpkg.core"
                    module_name = f"{package_name_from_root}.{module_name}"
            # If package name is provided but package_root.name doesn't match,
            # still prepend package name to ensure correct module structure
            # (e.g., files in src/ but package is testpkg -> testpkg.utils)
            # Only do this if package_root is a common project subdirectory
            # (like src, lib, app) AND files have imports that reference the package
            elif (
                package_root.name != _package_name
                and not module_name.startswith(f"{_package_name}.")
                and has_package_imports
                and module_name != _package_name
            ):
                # Prepend package name to module name
                module_name = f"{_package_name}.{module_name}"

        derived_module_names.append(module_name)

        module_text = file_path.read_text(encoding="utf-8")
        module_text = strip_redundant_blocks(module_text)

        # Process comments according to mode
        # IMPORTANT: This must happen BEFORE split_imports, as split_imports
        # works with the text directly and will preserve any comments that
        # are still in the text at that point
        logger.trace(
            "Processing comments: mode=%s, file=%s, text_length=%d",
            comments_mode,
            file_path,
            len(module_text),
        )
        has_comment_before = "# This comment should be removed" in module_text
        module_text = process_comments(module_text, comments_mode)
        has_comment_after = "# This comment should be removed" in module_text
        logger.trace(
            "After process_comments: text_length=%d, had_comment_before=%s, "
            "has_comment_after=%s",
            len(module_text),
            has_comment_before,
            has_comment_after,
        )

        # Process docstrings according to mode
        # IMPORTANT: This must happen BEFORE split_imports, similar to comments
        logger.trace(
            "Processing docstrings: mode=%s, file=%s, text_length=%d",
            docstring_mode,
            file_path,
            len(module_text),
        )
        module_text = process_docstrings(module_text, docstring_mode)
        logger.trace(
            "After process_docstrings: text_length=%d",
            len(module_text),
        )

        # Extract imports - pass all detected package names and modes
        external_imports_list, module_body = split_imports(
            module_text, package_names_list, external_imports, internal_imports
        )
        # Store transformed body for symbol extraction (collision detection)
        # This ensures assign mode assignments are included in collision checks
        module_sources[f"{module_name}.py"] = module_body
        for imp in external_imports_list:
            all_imports.setdefault(imp, None)

        # Create module section - use derived module name in header
        # Note: serger-generated comments (like headers) are added here and should
        # remain even in strip mode, as they're part of serger's output, not user code
        header = f"# === {module_name} ==="
        parts.append(f"\n{header}\n{module_body.strip()}\n\n")

        file_display = shorten_path_for_display(file_path)
        logger.trace("Processed module: %s (from %s)", module_name, file_display)

    return module_sources, all_imports, parts, derived_module_names


def _format_header_line(
    *,
    display_name: str,
    description: str,
    package_name: str,
) -> str:
    """Format the header text based on config values.

    Rules:
    - Both provided: "DisplayName — Description"
    - Only name: "DisplayName"
    - Nothing: "package_name"
    - Only description: "package_name — Description"

    Args:
        display_name: Optional display name from config
        description: Optional description from config
        package_name: Package name (fallback)

    Returns:
        Formatted header text (without "# " prefix or trailing newline)
    """
    # Use display_name if provided, otherwise fall back to package_name
    name = display_name.strip() if display_name else package_name
    desc = description.strip() if description else ""

    if name and desc:
        return f"{name} — {desc}"
    if name:
        return f"{name}"
    # default to package_name
    return f"{package_name}"


def _format_license(license_text: str) -> str:
    """Format license text for inclusion in generated script.

    Rules:
    - Single line (no linebreaks): Format as "License: <license text>"
    - Multi-line (has linebreaks): Use block format with ====LICENSE==== header

    Args:
        license_text: License text to format

    Returns:
        Formatted license text with "# " prefix on each line, or empty string
    """
    if not license_text:
        return ""

    stripped = license_text.strip()
    if not stripped:
        return ""

    # Check if license text has linebreaks
    has_linebreaks = "\n" in stripped

    if has_linebreaks:
        # Multi-line format: Use block format
        lines = stripped.split("\n")
        prefixed_lines = [f"# {line}" for line in lines]
        return (
            "# ============LICENSE============\n"
            + "\n".join(prefixed_lines)
            + "\n# ================================\n"
        )
    # Single line format: "License: <license text>"
    return f"# License: {stripped}\n"


def _build_final_script(  # noqa: C901, PLR0912, PLR0913, PLR0915
    *,
    package_name: str,
    all_imports: OrderedDict[str, None],
    parts: list[str],
    order_names: list[str],
    all_function_names: set[str],  # noqa: ARG001
    detected_packages: set[str],
    module_mode: str,
    module_actions: list[ModuleActionFull],
    shim: ShimSetting,
    order_paths: list[Path] | None = None,  # noqa: ARG001
    package_root: Path | None = None,  # noqa: ARG001
    file_to_include: dict[Path, IncludeResolved] | None = None,  # noqa: ARG001
    _original_order_names_for_shims: list[str] | None = None,
    license_text: str,
    version: str,
    commit: str,
    build_date: str,
    display_name: str = "",
    description: str = "",
    authors: str = "",
    repo: str = "",
    config: RootConfigResolved | None = None,
    selected_main_block: MainBlock | None = None,
    main_function_result: tuple[str, Path, str] | None = None,
    module_sources: dict[str, str] | None = None,
    source_bases: list[str] | None = None,
) -> tuple[str, list[str]]:
    """Build the final stitched script.

    Args:
        package_name: Root package name
        all_imports: Collected external imports
        parts: Module code sections
        order_names: List of module names (for shim generation)
        all_function_names: Set of all function names from all modules
            (unused, kept for API consistency)
        config: Resolved configuration with main_mode and main_name
        selected_main_block: Selected __main__ block to use (if any)
        main_function_result: Result from find_main_function() if found
        module_sources: Mapping of module name to source code
        detected_packages: Pre-detected package names
        module_mode: How to generate import shims ("none", "multi", "force")
        module_actions: List of module actions (already normalized)
        shim: Shim setting ("all", "public", "none")
        order_paths: Optional list of file paths (unused, kept for API consistency)
        package_root: Optional common root (unused, kept for API consistency)
        file_to_include: Optional mapping (unused, kept for API consistency)
        license_text: License text (will be formatted automatically)
        version: Version string
        commit: Commit hash
        build_date: Build timestamp
        display_name: Optional display name for header
        description: Optional description for header
        authors: Optional authors for header
        repo: Optional repository URL for header
        source_bases: Optional list of source base directories for module name
            derivation and package detection

    Returns:
        Final script text
    """
    logger = getAppLogger()
    logger.debug("Building final script...")

    # Separate __future__ imports
    future_imports: OrderedDict[str, None] = OrderedDict()
    for imp in list(all_imports.keys()):
        if imp.strip().startswith("from __future__"):
            future_imports.setdefault(imp, None)
            del all_imports[imp]

    future_block = "".join(future_imports.keys())
    import_block = "".join(all_imports.keys())

    # Update module section headers in parts to use transformed names
    # This must happen BEFORE shim generation, as headers are part of the stitched code
    # Headers should be updated even when shims aren't generated (module_mode == "none")
    # Process user-specified module_actions to update headers
    # When scope: "original" is set, it affects original module names in stitched code
    # (including headers), regardless of affects value
    transformed_order_names: list[str] | None = None
    if module_actions:
        # Filter for actions with scope: "original"
        # (headers are part of original code structure, so scope: "original" applies)
        original_scope_actions_for_headers = [
            a for a in module_actions if a.get("scope") == "original"
        ]
        if original_scope_actions_for_headers:
            # Apply actions to order_names to get transformed names for headers
            transformed_order_names = apply_module_actions(
                list(order_names), original_scope_actions_for_headers, detected_packages
            )
            logger.debug(
                "Header update: order_names=%s, transformed_order_names=%s",
                order_names,
                transformed_order_names,
            )
            # Build mapping from order_names to transformed_order_names
            # (for updating headers)
            if len(transformed_order_names) != len(order_names):
                logger.warning(
                    "transformed_order_names length (%d) != order_names length (%d). "
                    "Header update may be incomplete.",
                    len(transformed_order_names),
                    len(order_names),
                )
            for i, original_name in enumerate(order_names):
                if i < len(transformed_order_names):
                    transformed_name = transformed_order_names[i]
                    if transformed_name != original_name:
                        # Update header - search and replace in parts
                        # Headers are created as "\n# === {module_name} ===\n"
                        # "{module_body}\n\n"
                        # Use simple string replacement (headers are on their own lines)
                        header_pattern = f"# === {original_name} ==="
                        new_header = f"# === {transformed_name} ==="
                        logger.debug(
                            "Header update: searching for pattern '%s' "
                            "to replace with '%s'",
                            header_pattern,
                            new_header,
                        )
                        # Update all parts that contain this header
                        # Replace all occurrences in each part
                        replaced = False
                        for j, part in enumerate(parts):
                            if header_pattern in part:
                                logger.debug(
                                    "Found header pattern in part %d: %s",
                                    j,
                                    repr(part[:100]),
                                )
                                # Replace the header pattern with new header
                                parts[j] = part.replace(header_pattern, new_header)
                                logger.debug(
                                    "Replaced header in part %d: %s",
                                    j,
                                    repr(parts[j][:100]),
                                )
                                replaced = True
                        if not replaced:
                            logger.debug(
                                "Header pattern '%s' not found in parts for "
                                "transformation to '%s'. Parts sample: %s",
                                header_pattern,
                                new_header,
                                [repr(p[:50]) for p in parts[:5]],
                            )

    # Build name mapping for module structure setup
    # Maps transformed full names -> original full names
    # This is used by _setup_pkg_modules() to find modules by original name
    # when they're registered with transformed names
    name_mapping: dict[str, str] = {}
    if transformed_order_names is not None:
        logger.trace(
            "Building name mapping: transformed_order_names=%s, order_names=%s",
            transformed_order_names,
            order_names,
        )
        # Build mapping from transformed to original names (both as full paths)
        for i, original_name in enumerate(order_names):
            if i < len(transformed_order_names):
                transformed_name = transformed_order_names[i]
                if transformed_name != original_name:
                    # Convert both to full paths for name mapping
                    # Always use full paths with package_name prefix for name mapping
                    # Original name -> full path
                    if original_name == package_name:
                        original_full = package_name
                    elif original_name.startswith(f"{package_name}."):
                        original_full = original_name
                    else:
                        # Always prepend package_name for name mapping
                        # (we need consistent full paths in the mapping)
                        original_full = f"{package_name}.{original_name}"

                    # Transformed name -> full path
                    # Always use full paths with package_name prefix for name mapping
                    if transformed_name == package_name:
                        transformed_full = package_name
                    elif transformed_name.startswith(f"{package_name}."):
                        transformed_full = transformed_name
                    else:
                        # Always prepend package_name for name mapping
                        transformed_full = f"{package_name}.{transformed_name}"

                    # Map transformed -> original
                    name_mapping[transformed_full] = original_full
                    logger.trace(
                        "Name mapping entry: %s -> %s (original: %s, transformed: %s)",
                        transformed_full,
                        original_full,
                        original_name,
                        transformed_name,
                    )

    # Generate import shims based on module_actions and shim setting
    # If shim == "none" or module_mode == "none", skip shim generation
    if shim == "none" or module_mode == "none":
        # No shims generated
        shim_text = ""
    else:
        # IMPORTANT: Module names in order_names are relative to package_root
        # (e.g., "utils.utils_text"), but shims need full paths
        # (e.g., "serger.utils.utils_text").
        # Note: If specific modules should be excluded, use the 'exclude' config option
        # When files are filtered by affects: "stitching", use original module names
        # for shim generation (shims should still be generated even if files are
        # filtered from stitching)
        if _original_order_names_for_shims is not None:
            shim_names_raw = list(_original_order_names_for_shims)
        else:
            shim_names_raw = list(order_names)

        # Generate actions from module_mode if specified (and not "none"/"multi")
        # Actions should be applied to original module names BEFORE prepending
        # package_name
        all_actions: list[ModuleActionFull] = []
        if module_mode and module_mode not in ("none", "multi"):
            logger.trace(
                "[SHIM_GEN] Generating actions: module_mode=%s, "
                "shim_names_raw=%s, order_names=%s",
                module_mode,
                shim_names_raw[:5] if shim_names_raw else None,
                order_names[:5] if order_names else None,
            )
            auto_actions = generate_actions_from_mode(
                module_mode,
                detected_packages,
                package_name,
                module_names=shim_names_raw,
                source_bases=source_bases,
            )
            # Apply defaults to mode-generated actions (scope: "original" set here)
            normalized_actions = [
                set_mode_generated_action_defaults(action) for action in auto_actions
            ]
            logger.trace(
                "[SHIM_GEN] Generated %d actions: %s",
                len(normalized_actions),
                [f"{a.get('source')} -> {a.get('dest')}" for a in normalized_actions],
            )
            all_actions.extend(normalized_actions)

        # Add user-specified module_actions from RootConfigResolved
        # These are already fully normalized with scope: "shim" set (iteration 04)
        if module_actions:  # Already list[ModuleActionFull] with all defaults applied
            all_actions.extend(module_actions)

        # Separate actions by affects value
        (
            shims_only_actions,
            _stitching_only_actions,
            both_actions,
        ) = separate_actions_by_affects(all_actions)

        # Separate shim actions by scope
        # Note: Actions with scope: "original" must be applied BEFORE prepending
        # package_name (they operate on original module names), so we include them
        # from both shims_only_actions and both_actions
        # Actions with scope: "shim" and affects: "shims" are applied after
        # prepending (they operate on full module paths)
        original_scope_actions = [
            a for a in shims_only_actions + both_actions if a.get("scope") == "original"
        ]
        shim_scope_actions = [a for a in both_actions if a.get("scope") == "shim"]

        # Apply scope: "original" actions to original module names (before prepending)
        transformed_names = shim_names_raw
        if original_scope_actions:
            logger.trace(
                "[SHIM_GEN] Applying %d original-scope actions to: %s",
                len(original_scope_actions),
                shim_names_raw[:5] if shim_names_raw else None,
            )
            # Build available_modules set for validation
            available_modules_for_validation = set(shim_names_raw)
            # Add all action sources to available_modules since mode-generated
            # actions only reference root packages that should exist
            for action in original_scope_actions:
                source = action.get("source")
                if source:
                    available_modules_for_validation.add(source)
            # Also add package names from detected_packages that appear anywhere
            # in module names (as a fallback for edge cases)
            for pkg in detected_packages:
                if pkg != package_name and pkg not in available_modules_for_validation:
                    # Check if this package appears anywhere in module names
                    for mod_name in shim_names_raw:
                        if (
                            f".{pkg}." in mod_name
                            or mod_name.startswith(f"{pkg}.")
                            or mod_name == pkg
                            or mod_name.endswith(f".{pkg}")
                        ):
                            available_modules_for_validation.add(pkg)
                            break
            # Validate other constraints (dest conflicts, circular moves, etc.)
            validate_module_actions(
                original_scope_actions,
                available_modules_for_validation,
                detected_packages,
                scope="original",
            )
            transformed_names = apply_module_actions(
                transformed_names, original_scope_actions, detected_packages
            )
            # Note: Header updates are now handled outside the shim generation block
            # (before this conditional) so they work even when module_mode == "none"

        # Now prepend package_name to create full module paths
        # Module names are relative to package_root, so we need to prepend package_name
        # to get the full import path
        # (e.g., "utils.utils_text" -> "serger.utils.utils_text")
        # Note: flat mode has special handling for loose files (keeps them top-level)
        shim_names: list[str] = []
        for name in transformed_names:
            # Flat mode: treat loose files as top-level modules (not under package)
            # Packages still get shims as usual
            if module_mode == "flat":
                if name == package_name:
                    full_name = package_name
                elif name.startswith(f"{package_name}."):
                    full_name = name
                elif "." in name:
                    # Has dots: treat as package structure, use multi mode logic
                    first_part = name.split(".", 1)[0]
                    if first_part in detected_packages and first_part != package_name:
                        full_name = name
                    else:
                        full_name = f"{package_name}.{name}"
                else:
                    # Loose file: keep as top-level module (no package prefix)
                    full_name = name
            # Multi mode logic: use detected packages (default behavior)
            # If name already equals package_name, it's the root module itself
            elif name == package_name:
                full_name = package_name
            # If name already starts with package_name, use it as-is
            elif name.startswith(f"{package_name}."):
                full_name = name
            # If name contains dots and starts with a different detected package,
            # it's from another package (multi-package scenario) - use as-is
            elif "." in name:
                first_part = name.split(".", 1)[0]
                # If first part is a detected package different from package_name,
                # check if it's actually a subpackage of package_name
                # (i.e., if it appears as a top-level module in transformed_names)
                if (
                    first_part in detected_packages
                    and first_part != package_name
                    and first_part not in transformed_names
                ):
                    # First part is a separate package (not in our module list)
                    # - use as-is
                    full_name = name
                else:
                    # Likely a subpackage of package_name - prepend package_name
                    full_name = f"{package_name}.{name}"
            else:
                # Top-level module under package: prepend package_name
                full_name = f"{package_name}.{name}"
            shim_names.append(full_name)

        # Validate and apply scope: "shim" actions (incremental validation)
        if shim_scope_actions:
            for action in shim_scope_actions:
                # Skip source validation for delete actions (they match flexibly)
                action_type = action.get("action", "move")
                if action_type != "delete":
                    # For move/copy actions, validate source exists
                    # After mode transformations, source might need component matching
                    # (e.g., "mypkg.module" might need to match "mypkg.pkg1.module")
                    source = action.get("source")
                    if source:
                        if source not in shim_names:
                            # Check if source matches any component in shim_names
                            # For "mypkg.module", check if it matches
                            # "mypkg.pkg1.module" by checking if all components
                            # of source appear in module name
                            source_parts = source.split(".")
                            matching_modules = [
                                name
                                for name in shim_names
                                if (
                                    name == source
                                    or name.startswith(f"{source}.")
                                    or all(
                                        part in name.split(".") for part in source_parts
                                    )
                                )
                            ]
                            if not matching_modules:
                                available = sorted(shim_names)
                                msg = (
                                    f"Module action source '{source}' "
                                    f"does not exist in available modules "
                                    f"(scope: 'shim'). Available: {available}"
                                )
                                raise ValueError(msg)
                            # Component matching found - skip exact validation
                            # The action handler will use component matching
                        else:
                            # Exact match found - use standard validation
                            validate_action_source_exists(
                                action, set(shim_names), scope="shim"
                            )
                shim_names = apply_single_action(shim_names, action, detected_packages)

        # Apply shims_only_actions after prepending package_name
        # These actions only affect shim generation, so they're applied to
        # the final shim_names list (after prepending package_name)
        # This allows delete actions to match against full module paths like
        # "mypkg.pkg1"
        # Note: Exclude scope: "original" actions from shims_only_actions since
        # they've already been applied in original_scope_actions (before prepending)
        shims_only_actions_filtered = [
            a for a in shims_only_actions if a.get("scope") != "original"
        ]
        if shims_only_actions_filtered:
            for action in shims_only_actions_filtered:
                # Skip source validation for delete actions (they match flexibly)
                action_type = action.get("action", "move")
                if action_type != "delete":
                    # For non-delete actions, validate source exists
                    # Note: source might be relative (scope: "original") or absolute
                    # (scope: "shim"), so we need to handle both cases
                    action_scope = action.get("scope", "shim")
                    if action_scope == "shim":
                        source = action.get("source")
                        if source:
                            if source not in shim_names:
                                # Check if source matches any component in shim_names
                                # For "mypkg.module", check if it matches
                                # "mypkg.pkg1.module" by checking if all components
                                # of source appear in the module name
                                source_parts = source.split(".")
                                matching_modules = [
                                    name
                                    for name in shim_names
                                    if (
                                        name == source
                                        or name.startswith(f"{source}.")
                                        or all(
                                            part in name.split(".")
                                            for part in source_parts
                                        )
                                    )
                                ]
                                if not matching_modules:
                                    available = sorted(shim_names)
                                    msg = (
                                        f"Module action source '{source}' "
                                        f"does not exist in available modules "
                                        f"(scope: 'shim', affects: 'shims'). "
                                        f"Available: {available}"
                                    )
                                    raise ValueError(msg)
                                # Component matching found - skip exact validation
                            else:
                                # Exact match found - use standard validation
                                validate_action_source_exists(
                                    action, set(shim_names), scope="shim"
                                )
                    # For scope: "original", the source is relative, so we need to
                    # check if it matches any component in shim_names
                    # (e.g., source "pkg1" should match "mypkg.pkg1")
                    elif action_scope == "original":
                        source = action.get("source")
                        if source:
                            # Check if source appears as a component in any shim_name
                            source_found = False
                            for shim_name in shim_names:
                                if (
                                    shim_name == source
                                    or shim_name.startswith(f"{source}.")
                                    or source in shim_name.split(".")
                                ):
                                    source_found = True
                                    break
                            if not source_found:
                                available = sorted(shim_names)
                                msg = (
                                    f"Module action source '{source}' does not exist "
                                    f"in available modules (scope: 'original', "
                                    f"affects: 'shims'). Available: {available}"
                                )
                                raise ValueError(msg)
                shim_names = apply_single_action(shim_names, action, detected_packages)

        # Check for shim-stitching mismatches and apply cleanup
        # Build set of modules that are in stitched code
        # (from order_names after filtering)
        # order_names contains the module names that were actually stitched
        # Convert to full module paths (with package_name prefix) for comparison
        # This matches the format of shim_names
        stitched_modules_full: set[str] = set()
        for name in order_names:
            # Apply same logic as shim name generation to get full path
            if module_mode == "flat":
                if name == package_name:
                    full_name = package_name
                elif name.startswith(f"{package_name}."):
                    full_name = name
                elif "." in name:
                    first_part = name.split(".", 1)[0]
                    if first_part in detected_packages and first_part != package_name:
                        full_name = name
                    else:
                        full_name = f"{package_name}.{name}"
                else:
                    full_name = name
            elif name == package_name:
                full_name = package_name
            elif name.startswith(f"{package_name}."):
                full_name = name
            elif "." in name:
                first_part = name.split(".", 1)[0]
                if first_part in detected_packages and first_part != package_name:
                    full_name = name
                else:
                    full_name = f"{package_name}.{name}"
            else:
                full_name = f"{package_name}.{name}"
            stitched_modules_full.add(full_name)

        # Check for mismatches
        shim_modules_set = set(shim_names)
        mismatches = check_shim_stitching_mismatches(
            shim_modules_set, stitched_modules_full, all_actions
        )

        # Apply cleanup behavior
        if mismatches:
            updated_shims, _warnings = apply_cleanup_behavior(
                mismatches, shim_modules_set
            )
            # Update shim_names to reflect cleanup
            shim_names = sorted(updated_shims)

        # Group modules by their parent package
        # parent_package -> list of (module_name, is_direct_child)
        # is_direct_child means the module is directly under this package
        # (not nested deeper)
        packages: dict[str, list[tuple[str, bool]]] = {}
        # parent_pkg -> [(module_name, is_direct)]
        # Track top-level modules for flat mode
        top_level_modules: list[str] = []

        # Use transformed_order_names for module structure if available
        # (for actions with scope: "original", the module structure should use
        # transformed names, not original names)
        # However, if shim transformations have been applied, use final shim_names
        # instead (which includes all transformations)
        # shim_names is used for shim generation, but module structure should
        # use transformed names when scope: "original" actions are applied
        # transformed_order_names is initialized above (line 1829) and set if
        # original_scope_actions_for_headers is not empty
        module_names_for_structure = shim_names
        logger.trace(
            "Module structure setup: shim_names=%s, transformed_order_names=%s",
            shim_names,
            transformed_order_names,
        )
        # Only use transformed_order_names if no shim transformations were applied
        # (shim_names already includes all transformations if shim actions exist)
        has_shim_transformations = any(
            a.get("scope") == "shim"
            for a in (module_actions or [])
            if a.get("affects", "shims") in ("shims", "both")
        )
        if transformed_order_names is not None and not has_shim_transformations:  # pyright: ignore[reportPossiblyUnboundVariable]
            # transformed_order_names contains transformed module names
            # (relative to package_root)
            # We need to convert them to full module paths (with package_name prefix)
            # to match the format of shim_names
            transformed_full_names: list[str] = []
            for name in transformed_order_names:  # pyright: ignore[reportPossiblyUnboundVariable]
                # Apply same logic as shim name generation to get full path
                if module_mode == "flat":
                    if name == package_name:
                        full_name = package_name
                    elif name.startswith(f"{package_name}."):
                        full_name = name
                    elif "." in name:
                        first_part = name.split(".", 1)[0]
                        if (
                            first_part in detected_packages
                            and first_part != package_name
                        ):
                            full_name = name
                        else:
                            full_name = f"{package_name}.{name}"
                    else:
                        full_name = name
                elif name == package_name:
                    full_name = package_name
                elif name.startswith(f"{package_name}."):
                    full_name = name
                elif "." in name:
                    first_part = name.split(".", 1)[0]
                    if first_part in detected_packages and first_part != package_name:
                        full_name = name
                    else:
                        full_name = f"{package_name}.{name}"
                else:
                    full_name = f"{package_name}.{name}"
                transformed_full_names.append(full_name)
            module_names_for_structure = transformed_full_names
            logger.trace(
                "Using transformed names for structure: %s (package_name=%s)",
                transformed_full_names,
                package_name,
            )

        for module_name in module_names_for_structure:
            logger.trace(
                "Processing module for structure: %s (package_name=%s)",
                module_name,
                package_name,
            )
            if "." not in module_name:
                # Top-level module
                if module_mode == "flat":
                    # In flat mode, top-level modules are not under any package
                    top_level_modules.append(module_name)
                else:
                    # In other modes, parent is the root package
                    parent = package_name
                    is_direct = True
                    if parent not in packages:
                        packages[parent] = []
                    packages[parent].append((module_name, is_direct))
                    logger.trace(
                        "Added module %s to package %s (is_direct=%s)",
                        module_name,
                        parent,
                        is_direct,
                    )
            else:
                # Find the parent package (everything except the last component)
                name_parts = module_name.split(".")
                parent = ".".join(name_parts[:-1])
                is_direct = True  # This module is directly under its parent

                if parent not in packages:
                    packages[parent] = []
                packages[parent].append((module_name, is_direct))
                logger.trace(
                    "Added module %s to package %s (is_direct=%s)",
                    module_name,
                    parent,
                    is_direct,
                )

        # Rebuild name mapping using final shim_names (after all transformations)
        # This ensures the mapping reflects the final state after both original and
        # shim transformations
        if transformed_order_names is not None:
            logger.trace(
                "Rebuilding name mapping from final shim_names: shim_names=%s, "
                "order_names=%s",
                shim_names,
                order_names,
            )
            # Build mapping from final transformed names to original names
            # We need to match shim_names (final) back to order_names (original)
            name_mapping.clear()
            # Convert order_names to full paths for matching
            original_full_paths: list[str] = []
            for original_name in order_names:
                if original_name == package_name:
                    original_full = package_name
                elif original_name.startswith(f"{package_name}."):
                    original_full = original_name
                else:
                    original_full = f"{package_name}.{original_name}"
                original_full_paths.append(original_full)

            # Match shim_names to original_full_paths by position
            # (assuming they're in the same order)
            for i, final_name in enumerate(shim_names):
                if i < len(original_full_paths):
                    original_full = original_full_paths[i]
                    if final_name != original_full:
                        name_mapping[final_name] = original_full
                        logger.trace(
                            "Rebuilt name mapping: %s -> %s",
                            final_name,
                            original_full,
                        )

        # Collect all package names (both intermediate and top-level)
        # Use module_names_for_structure to include packages from transformed names
        all_packages: set[str] = set()
        logger.trace(
            "Collecting packages from shim_names=%s and module_names_for_structure=%s",
            shim_names,
            module_names_for_structure,
        )
        # Collect from both shim_names (for shim generation) and
        # module_names_for_structure (for transformed structure)
        for module_name in shim_names:
            # Skip top-level modules in flat mode (they're not in packages)
            if module_mode == "flat" and "." not in module_name:
                continue
            name_parts = module_name.split(".")
            # Add all package prefixes
            # (e.g., for "serger.utils.utils_text" add "serger" and "serger.utils")
            for i in range(1, len(name_parts)):
                pkg = ".".join(name_parts[:i])
                all_packages.add(pkg)
            # Also add the top-level package if module has dots
            if "." in module_name:
                all_packages.add(name_parts[0])
        # Also collect packages from transformed structure
        for module_name in module_names_for_structure:
            # Skip top-level modules in flat mode (they're not in packages)
            if module_mode == "flat" and "." not in module_name:
                continue
            name_parts = module_name.split(".")
            # Add all package prefixes
            for i in range(1, len(name_parts)):
                pkg = ".".join(name_parts[:i])
                all_packages.add(pkg)
            # Also add the top-level package if module has dots
            if "." in module_name:
                all_packages.add(name_parts[0])
        # Add root package if not already present (unless flat mode with no packages)
        if module_mode != "flat" or all_packages:
            all_packages.add(package_name)

        # Add detected packages that have modules in the final output
        # This is important when files from outside the config directory are included
        # and packages are detected via source_bases but not directly referenced
        # in module names (e.g., when __init__.py is excluded)
        # Only add packages that actually have modules (not deleted by actions)
        all_module_names = set(shim_names) | set(module_names_for_structure)
        for detected_pkg in detected_packages:
            # Check if any module belongs to this package
            # Module must start with package name (exact match or package.module)
            # to ensure we only add packages that are actually used as packages,
            # not just components of other package names
            has_modules = any(
                mod == detected_pkg or mod.startswith(f"{detected_pkg}.")
                for mod in all_module_names
            )
            if has_modules:
                all_packages.add(detected_pkg)

        logger.trace(
            "Collected packages: %s (package_name=%s, detected_packages=%s)",
            sorted(all_packages),
            package_name,
            sorted(detected_packages),
        )

        # Sort packages by depth (shallowest first) to create parents before children
        # Use package name as secondary sort key to ensure deterministic ordering
        # when multiple packages have the same depth
        sorted_packages = sorted(all_packages, key=lambda p: (p.count("."), p))
        logger.trace("Sorted packages (by depth, then name): %s", sorted_packages)

        # Generate shims for each package
        # Each package gets its own module object to maintain proper isolation
        shim_blocks: list[str] = []
        shim_blocks.append("# --- import shims for single-file runtime ---")
        # Note: types and sys are imported at the top level (see all_imports)

        # Helper function to create/register package modules
        shim_blocks.append("def _create_pkg_module(pkg_name: str) -> types.ModuleType:")
        shim_blocks.append(
            '    """Create or get a package module and set up parent relationships."""'
        )
        shim_blocks.append("    _mod = sys.modules.get(pkg_name)")
        shim_blocks.append("    if not _mod:")
        shim_blocks.append("        _mod = types.ModuleType(pkg_name)")
        shim_blocks.append("        _mod.__package__ = pkg_name")
        shim_blocks.append("        sys.modules[pkg_name] = _mod")
        shim_blocks.append(
            "    # Set up parent-child relationships for nested packages"
        )
        shim_blocks.append("    if '.' in pkg_name:")
        shim_blocks.append("        _parent_pkg = '.'.join(pkg_name.split('.')[:-1])")
        shim_blocks.append("        _child_name = pkg_name.split('.')[-1]")
        shim_blocks.append("        _parent = sys.modules.get(_parent_pkg)")
        shim_blocks.append("        if _parent:")
        shim_blocks.append("            setattr(_parent, _child_name, _mod)")
        shim_blocks.append("    return _mod")
        shim_blocks.append("")

        # ignores must be on their own line
        # or they may get reformated to the wrong place
        shim_blocks.append("def _setup_pkg_modules(  # noqa: C901, PLR0912")
        shim_blocks.append(
            "pkg_name: str, module_names: list[str], "
            "name_mapping: dict[str, str] | None = None"
        )
        shim_blocks.append(") -> None:")
        shim_blocks.append(
            '    """Set up package module attributes and register submodules."""'
        )
        shim_blocks.append("    _mod = sys.modules.get(pkg_name)")
        shim_blocks.append("    if not _mod:")
        shim_blocks.append("        return")
        shim_blocks.append("    # Copy attributes from all modules under this package")
        shim_blocks.append("    _globals = globals()")
        shim_blocks.append("    # Debug: log what's in globals for this package")
        shim_blocks.append("    # Note: This copies all globals to the package module")
        shim_blocks.append("    for _key, _value in _globals.items():")
        shim_blocks.append("        setattr(_mod, _key, _value)")
        shim_blocks.append(
            "    # Set up package attributes for nested packages BEFORE registering"
        )
        shim_blocks.append(
            "    # modules (so packages are available when modules are registered)"
        )
        shim_blocks.append("    _seen_packages: set[str] = set()")
        shim_blocks.append("    for _name in module_names:")
        shim_blocks.append(
            "        if _name != pkg_name and _name.startswith(pkg_name + '.'):"
        )
        shim_blocks.append(
            "            # Extract parent package (e.g., mypkg.public from"
        )
        shim_blocks.append("            # mypkg.public.utils)")
        shim_blocks.append("            _name_parts = _name.split('.')")
        shim_blocks.append("            if len(_name_parts) > 2:  # noqa: PLR2004")
        shim_blocks.append("                # Has at least one intermediate package")
        shim_blocks.append("                _parent_pkg = '.'.join(_name_parts[:-1])")
        shim_blocks.append(
            "                if _parent_pkg.startswith(pkg_name + '.') and "
            "_parent_pkg not in _seen_packages:"
        )
        shim_blocks.append("                    _seen_packages.add(_parent_pkg)")
        shim_blocks.append(
            "                    _pkg_obj = sys.modules.get(_parent_pkg)"
        )
        shim_blocks.append("                    if _pkg_obj and _pkg_obj != _mod:")
        shim_blocks.append("                        # Set parent package as attribute")
        shim_blocks.append("                        _pkg_attr_name = _name_parts[1]")
        shim_blocks.append(
            "                        if not hasattr(_mod, _pkg_attr_name):"
        )
        shim_blocks.append(
            "                            setattr(_mod, _pkg_attr_name, _pkg_obj)"
        )
        shim_blocks.append("    # Register all modules under this package")
        shim_blocks.append("    for _name in module_names:")
        shim_blocks.append("        # Try to find module by transformed name first")
        shim_blocks.append("        _module_obj = sys.modules.get(_name)")
        shim_blocks.append("        if not _module_obj and name_mapping:")
        shim_blocks.append("            # If not found, try to find by original name")
        shim_blocks.append("            _original_name = name_mapping.get(_name)")
        shim_blocks.append("            if _original_name:")
        shim_blocks.append(
            "                _module_obj = sys.modules.get(_original_name)"
        )
        shim_blocks.append("                if not _module_obj:")
        shim_blocks.append(
            "                    # Also check globals() for module object"
        )
        shim_blocks.append("                    # Module objects might be in globals()")
        shim_blocks.append("                    # with their original names")
        shim_blocks.append(
            "                    _last_part = _original_name.split('.')[-1]"
        )
        shim_blocks.append("                    _module_obj = _globals.get(_last_part)")
        shim_blocks.append("                if _module_obj:")
        shim_blocks.append("                    # Register with transformed name")
        shim_blocks.append("                    sys.modules[_name] = _module_obj")
        shim_blocks.append("        # If still not found, use package module")
        shim_blocks.append("        if not _module_obj:")
        shim_blocks.append("            sys.modules[_name] = _mod")
        shim_blocks.append("    # Set submodules as attributes on parent package")
        shim_blocks.append("    for _name in module_names:")
        shim_blocks.append(
            "        if _name != pkg_name and _name.startswith(pkg_name + '.'):"
        )
        shim_blocks.append("            _submodule_name = _name.split('.')[-1]")
        shim_blocks.append("            # Try to get actual module object")
        shim_blocks.append("            _module_obj = sys.modules.get(_name)")
        shim_blocks.append("            if not _module_obj and name_mapping:")
        shim_blocks.append("                _original_name = name_mapping.get(_name)")
        shim_blocks.append("                if _original_name:")
        shim_blocks.append(
            "                    _module_obj = sys.modules.get(_original_name)"
        )
        shim_blocks.append("                    if not _module_obj:")
        shim_blocks.append("                        # Also check globals()")
        shim_blocks.append(
            "                        _last_part = _original_name.split('.')[-1]"
        )
        shim_blocks.append(
            "                        _module_obj = _globals.get(_last_part)"
        )
        shim_blocks.append(
            "            # Use actual module object if found, otherwise package"
        )
        shim_blocks.append("            _target = _module_obj if _module_obj else _mod")
        shim_blocks.append("            if not hasattr(_mod, _submodule_name):")
        shim_blocks.append("                setattr(_mod, _submodule_name, _target)")
        shim_blocks.append(
            "            elif isinstance(getattr(_mod, _submodule_name, None), "
            "types.ModuleType):"
        )
        shim_blocks.append("                setattr(_mod, _submodule_name, _target)")
        shim_blocks.append("")

        # First pass: Create all package modules and set up parent-child relationships
        shim_blocks.extend(
            f"_create_pkg_module({pkg_name!r})" for pkg_name in sorted_packages
        )

        shim_blocks.append("")

        # Build name mapping dict as string for shim code
        # Maps transformed full names -> original full names
        name_mapping_str = (
            "{"
            + ", ".join(f"{k!r}: {v!r}" for k, v in sorted(name_mapping.items()))
            + "}"
            if name_mapping
            else "None"
        )
        _max_name_mapping_log_length = 200
        logger.trace(
            "Name mapping for shim code: %s (dict size: %d)",
            (
                name_mapping_str[:_max_name_mapping_log_length]
                if len(name_mapping_str) > _max_name_mapping_log_length
                else name_mapping_str
            ),
            len(name_mapping),
        )

        # Second pass: Copy attributes and register modules
        # Process in any order since all modules are now created
        logger.trace("Packages dict: %s", packages)
        for pkg_name in sorted_packages:
            logger.trace(
                "Processing package %s (in packages dict: %s)",
                pkg_name,
                pkg_name in packages,
            )
            if pkg_name not in packages:
                # Package has no direct modules, but might have subpackages
                # We still need to set it up so it's accessible
                logger.trace(
                    "Package %s has no direct modules, but setting up anyway",
                    pkg_name,
                )
                # Set up empty package - just register it
                shim_blocks.append(
                    f"_setup_pkg_modules({pkg_name!r}, [], {name_mapping_str})"
                )
                continue

            # Sort module names for deterministic output
            module_names_for_pkg = sorted([name for name, _ in packages[pkg_name]])
            logger.trace(
                "Setting up package %s with modules: %s",
                pkg_name,
                module_names_for_pkg,
            )
            # Module names already have full paths (with package_name prefix),
            # but ensure they're correctly formatted for registration
            # If name equals pkg_name, it's the root module itself
            full_module_names = [
                (
                    name
                    if (name == pkg_name or name.startswith(f"{pkg_name}."))
                    else f"{pkg_name}.{name}"
                )
                for name in module_names_for_pkg
            ]
            module_names_str = ", ".join(repr(name) for name in full_module_names)
            logger.trace(
                "Calling _setup_pkg_modules for %s with modules: %s",
                pkg_name,
                full_module_names,
            )
            shim_blocks.append(
                f"_setup_pkg_modules({pkg_name!r}, [{module_names_str}], "
                f"{name_mapping_str})"
            )

        # Handle top-level modules for flat mode
        if module_mode == "flat" and top_level_modules:
            # Register top-level modules directly in sys.modules
            shim_blocks.extend(
                f"sys.modules[{module_name!r}] = globals()"
                for module_name in sorted(top_level_modules)
            )

        # Set up root module to have access to top-level packages
        # When transformed packages like mypkg.public exist, make public accessible
        # at root level for convenience (module.public works, not just
        # module.mypkg.public)
        if transformed_order_names is not None and package_name:
            logger.trace(
                "Setting up root module access for transformed packages: "
                "transformed_order_names=%s, package_name=%s, "
                "all_packages=%s",
                transformed_order_names,
                package_name,
                sorted(all_packages),
            )
            # Find top-level transformed packages (e.g., "public" from "mypkg.public")
            for transformed_name in transformed_order_names:
                if "." in transformed_name:
                    # Extract first part (e.g., "public" from "public.utils")
                    first_part = transformed_name.split(".", 1)[0]
                    # Check if this is a package (has submodules)
                    full_pkg_name = f"{package_name}.{first_part}"
                    logger.trace(
                        "Checking transformed package: first_part=%s, "
                        "full_pkg_name=%s, in all_packages=%s",
                        first_part,
                        full_pkg_name,
                        full_pkg_name in all_packages,
                    )
                    if full_pkg_name in all_packages:
                        logger.trace(
                            "Making transformed package %s accessible at root level",
                            first_part,
                        )
                        logger.trace(
                            "Adding shim blocks for root module access (current "
                            "shim_blocks length: %d)",
                            len(shim_blocks),
                        )
                        shim_blocks.append(
                            f"# Make {first_part} accessible at root level"
                        )
                        logger.trace(
                            "After adding comment (shim_blocks length: %d)",
                            len(shim_blocks),
                        )
                        shim_blocks.append(
                            f"_transformed_pkg = sys.modules.get({full_pkg_name!r})"
                        )
                        shim_blocks.append("if _transformed_pkg:")
                        # Set on root package if it exists
                        shim_blocks.append(
                            f"    _root_pkg = sys.modules.get({package_name!r})"
                        )
                        shim_blocks.append(
                            f"    if _root_pkg and not hasattr(_root_pkg, "
                            f"{first_part!r}):"
                        )
                        shim_blocks.append(
                            f"        setattr(_root_pkg, {first_part!r}, "
                            f"_transformed_pkg)"
                        )
                        # Set in globals() for script execution
                        shim_blocks.append(
                            f"    globals()[{first_part!r}] = _transformed_pkg"
                        )
                        # Also set on current module for importlib compatibility
                        # This ensures module.public works when imported via importlib
                        shim_blocks.append("    try:")
                        shim_blocks.append(
                            "        _current_mod = sys.modules.get(__name__)"
                        )
                        shim_blocks.append("        if _current_mod:")
                        shim_blocks.append(
                            f"            setattr(_current_mod, {first_part!r}, "
                            f"_transformed_pkg)"
                        )
                        shim_blocks.append("    except NameError:")
                        shim_blocks.append("        # __name__ not set yet, skip")
                        shim_blocks.append("        pass")

        shim_text = "\n".join(shim_blocks)

    # Auto-rename collision handling (raw mode only)
    # After applying module_mode transformations and user's module_actions,
    # check if multiple functions exist with the same name as the main function.
    # If yes, and in raw mode, auto-rename others to main_1, main_2, etc.
    stitch_mode = config.get("stitch_mode", "raw") if config else "raw"
    if (
        stitch_mode == "raw"
        and main_function_result is not None
        and module_sources is not None
    ):
        # Extract module names from module_sources keys (remove .py suffix)
        # This ensures we use the actual module names after any transformations
        module_names_from_sources = [
            key[:-3] for key in sorted(module_sources.keys()) if key.endswith(".py")
        ]

        # Detect collisions
        collisions = detect_collisions(
            main_function_result=main_function_result,
            module_sources=module_sources,
            module_names=module_names_from_sources,
        )

        # Generate auto-rename mappings (filters out main function automatically)
        renames = generate_auto_renames(
            collisions=collisions,
            main_function_result=main_function_result,
        )

        # If we have renames to apply
        if renames:
            main_function_name, _main_file_path, _main_module_path = (
                main_function_result
            )

            # Apply renames to module_sources and parts
            for module_name, new_function_name in sorted(renames.items()):
                module_key = f"{module_name}.py"
                if module_key in module_sources:
                    old_source = module_sources[module_key]
                    new_source = rename_function_in_source(
                        old_source, main_function_name, new_function_name
                    )
                    module_sources[module_key] = new_source

                    # Update corresponding part in parts list
                    # Find the part that contains this module
                    for i, part in enumerate(parts):
                        # Check if this part contains the module header
                        header_pattern = f"# === {module_name} ==="
                        if header_pattern in part:
                            # Replace the old function definition with new one
                            # Use regex to find and replace function definition
                            pattern = (
                                rf"^(\s*)(async\s+)?def\s+"
                                rf"{re.escape(main_function_name)}\s*\("
                            )
                            replacement = rf"\1\2def {new_function_name}("
                            parts[i] = re.sub(
                                pattern, replacement, part, flags=re.MULTILINE
                            )
                            break

                    # Log the rename
                    logger.info(
                        "Auto-renamed...........%s.%s() → %s()",
                        module_name,
                        main_function_name,
                        new_function_name,
                    )

    # Generate formatted header line
    # Use custom_header if provided, otherwise use formatted header
    if config and config.get("custom_header"):
        header_line = config.get("custom_header", "")
    else:
        header_line = _format_header_line(
            display_name=display_name,
            description=description,
            package_name=package_name,
        )

    # Build license/header section
    # Format license text (single line or multi-line block format)
    license_section = _format_license(license_text)
    repo_line = f"# Repo: {repo}\n" if repo else ""
    authors_line = f"# Authors: {authors}\n" if authors else ""

    # Determine __main__ block to use
    main_block = ""
    main_mode = config.get("main_mode", "auto") if config else "auto"
    main_name = config.get("main_name") if config else None

    if main_mode == "auto":
        # If we have a selected __main__ block, use it
        if selected_main_block is not None:
            logger.info(
                "__main__ block...........selected from %s",
                selected_main_block.file_path,
            )
            # Use the selected block content
            main_block = f"\n{selected_main_block.content}\n"
        elif main_function_result is not None:
            # No existing block found, but we have a main function
            # Generate our own __main__ block
            function_name, _file_path, _module_path = main_function_result

            # Get the function node to detect parameters
            # We need to find it in module_sources
            has_params = True  # Default to True (safe)
            if module_sources is not None:
                # Find the module that contains the function
                module_key = f"{_module_path}.py"
                if module_key in module_sources:
                    source = module_sources[module_key]
                    # Parse and find the function
                    # Note: This is a minor redundant parse (only for one module,
                    # only when main_mode == "auto" and main_function_result is not
                    # None). The complexity of caching ASTs here is not worth it for
                    # this single-use case that only affects one module.
                    try:
                        tree = ast.parse(source)
                        for node in tree.body:
                            if (
                                isinstance(
                                    node, (ast.FunctionDef, ast.AsyncFunctionDef)
                                )
                                and node.name == function_name
                            ):
                                has_params = detect_function_parameters(node)
                                break
                    except (SyntaxError, ValueError):
                        pass

            # Generate block based on parameters
            if has_params:
                main_block = (
                    f"\nif __name__ == '__main__':\n"
                    f"    sys.exit({function_name}(sys.argv[1:]))\n"
                )
            else:
                main_block = (
                    f"\nif __name__ == '__main__':\n    sys.exit({function_name}())\n"
                )
            logger.info("__main__ block...........inserted")
        elif main_name is not None:
            # main_name was specified but not found - this is an error
            msg = (
                f"main_name '{main_name}' was specified but the function "
                "was not found in the stitched code"
            )
            raise ValueError(msg)
        # If no main function found and main_name not specified,
        # this is a non-main build (acceptable)
        # Note: We already logged this in stitch_modules, so we don't log again here
    # If main_mode == "none", don't add any __main__ block

    # Log commit value being written to script (for CI debugging)
    logger = getAppLogger()
    logger.info(
        "_build_final_script: Writing commit to script: %s (version=%s, build_date=%s)",
        commit,
        version,
        build_date,
    )
    logger.trace(
        "_build_final_script: Writing commit=%s, version=%s, build_date=%s",
        commit,
        version,
        build_date,
    )
    if is_ci():
        logger.info("Writing commit to script: %s", commit)
        logger.trace("_build_final_script: CI mode: commit=%s", commit)

    script_text = (
        "#!/usr/bin/env python3\n"
        '"""\n'
        + (
            config.get("file_docstring", "")
            if config and config.get("file_docstring")
            else (
                f"{header_line}\n"
                "This single-file version is auto-generated from modular sources.\n"
                f"Version: {version}\n"
                f"Commit: {commit}\n"
                f"Built: {build_date}\n" + (f"Authors: {authors}\n" if authors else "")
            )
        )
        + '"""\n'
        f"# {header_line}\n"
        f"{license_section}"
        f"# Version: {version}\n"
        f"# Commit: {commit}\n"
        f"# Build Date: {build_date}\n"
        f"{authors_line}"
        f"{repo_line}"
        "\n# noqa: E402\n"
        "\n"
        f"{future_block}\n"
        f"{import_block}\n"
        "\n"
        # constants come *after* imports to avoid breaking __future__ rules
        f"__version__ = {json.dumps(version)}\n"
        f"__commit__ = {json.dumps(commit)}\n"
        f"__build_date__ = {json.dumps(build_date)}\n"
        + (f"__AUTHORS__ = {json.dumps(authors)}\n" if authors else "")
        + f"__STANDALONE__ = True\n"
        f"__STITCH_SOURCE__ = {json.dumps(PROGRAM_PACKAGE)}\n"
        f"__package__ = {json.dumps(package_name)}\n"
        "\n"
        "\n"
        + "\n".join(parts)
        + "\n"
        + (f"{shim_text}\n" if shim_text else "")
        + f"{main_block}"
    )

    # Return script text and detected packages (sorted for consistency)
    return script_text, sorted(detected_packages)


def stitch_modules(  # noqa: PLR0915, PLR0912, PLR0913, C901
    *,
    config: dict[str, object],
    file_paths: list[Path],
    package_root: Path,
    file_to_include: dict[Path, IncludeResolved],
    out_path: Path,
    license_text: str = "",
    version: str = "unknown",
    commit: str = "unknown",
    build_date: str = "unknown",
    post_processing: PostProcessingConfigResolved | None = None,
    is_serger_build: bool,
) -> None:
    """Orchestrate stitching of multiple Python modules into a single file.

    This is the main entry point for the stitching process. It coordinates all
    stitching utilities to produce a single, self-contained Python script from
    modular sources.

    The function:
    1. Validates configuration completeness
    2. Verifies all modules are listed and dependencies are consistent
    3. Collects and deduplicates external imports
    4. Assembles modules in correct order
    5. Detects name collisions
    6. Generates final script with metadata
    7. Verifies the output compiles
    8. Optionally runs post-processing tools (static checker, formatter, import sorter)

    Args:
        config: RootConfigResolved with stitching fields (package, order).
                Must include 'package' field for stitching. 'order' is optional
                and will be auto-discovered via topological sort if not provided.
        file_paths: List of file paths to stitch (in order)
        package_root: Common root of all included files
        file_to_include: Mapping of file path to its include (for dest access)
        out_path: Path where final stitched script should be written
        license_text: Optional license text for generated script
            (will be formatted automatically)
        version: Version string to embed in script metadata
        commit: Commit hash to embed in script metadata
        build_date: Build timestamp to embed in script metadata
        post_processing: Post-processing configuration (if None, skips post-processing)
        is_serger_build: Whether the output file is safe to overwrite.
                True if file doesn't exist or is a serger build, False otherwise.
                Pre-computed in run_build() to avoid recomputation.

    Raises:
        RuntimeError: If any validation or stitching step fails, or if attempting
                to overwrite a non-serger file (is_serger_build=False)
        AssertionError: If mtime advancing fails
    """
    logger = getAppLogger()

    # Bail out early if attempting to overwrite a non-serger file
    # (primary check is in run_build, this is defensive for direct calls)
    if out_path.exists() and not is_serger_build:
        xmsg = (
            f"Refusing to overwrite {out_path} because it does not appear "
            "to be a serger-generated build. If you want to overwrite this "
            "file, please delete it first or rename it."
        )
        raise RuntimeError(xmsg)

    # package is required for stitching
    validate_required_keys(config, {"package"}, "config")
    package_name_raw = config.get("package", "unknown")
    order_paths_raw = config.get("order", [])
    exclude_paths_raw = config.get("exclude_names", [])
    stitch_mode_raw = config.get("stitch_mode", DEFAULT_STITCH_MODE)
    module_mode_raw = config.get("module_mode", DEFAULT_MODULE_MODE)

    # Type guards for mypy/pyright
    if not isinstance(package_name_raw, str):
        msg = "Config 'package' must be a string"
        raise TypeError(msg)
    if not isinstance(order_paths_raw, list):
        msg = "Config 'order' must be a list"
        raise TypeError(msg)
    if not isinstance(exclude_paths_raw, list):
        msg = "Config 'exclude_names' must be a list"
        raise TypeError(msg)
    if not isinstance(stitch_mode_raw, str):
        msg = "Config 'stitch_mode' must be a string"
        raise TypeError(msg)
    if not isinstance(module_mode_raw, str):
        msg = "Config 'module_mode' must be a string"
        raise TypeError(msg)

    # Cast to known types after type guards
    package_name = package_name_raw
    # order and exclude_names are already resolved to Path objects in run_build()
    # Convert to Path objects explicitly

    order_paths: list[Path] = []
    for item in order_paths_raw:  # pyright: ignore[reportUnknownVariableType]
        if isinstance(item, str):
            order_paths.append(Path(item))
        elif isinstance(item, Path):
            order_paths.append(item)

    exclude_paths: list[Path] = []
    for item in exclude_paths_raw:  # pyright: ignore[reportUnknownVariableType]
        if isinstance(item, str):
            exclude_paths.append(Path(item))
        elif isinstance(item, Path):
            exclude_paths.append(item)

    if not package_name or package_name == "unknown":
        msg = "Config must specify 'package' for stitching"
        raise RuntimeError(msg)

    if not order_paths:
        msg = (
            "No modules found for stitching. "
            "Either specify 'order' in config or ensure 'include' patterns match files."
        )
        raise RuntimeError(msg)

    # Validate stitch_mode
    valid_modes = literal_to_set(StitchMode)
    stitch_mode = stitch_mode_raw
    if stitch_mode not in valid_modes:
        msg = (
            f"Invalid stitch_mode: {stitch_mode!r}. "
            f"Must be one of: {', '.join(sorted(valid_modes))}"
        )
        raise ValueError(msg)

    # Validate module_mode
    valid_module_modes = literal_to_set(ModuleMode)
    module_mode = module_mode_raw
    if module_mode not in valid_module_modes:
        msg = (
            f"Invalid module_mode: {module_mode!r}. "
            f"Must be one of: {', '.join(sorted(valid_module_modes))}"
        )
        raise ValueError(msg)

    # Extract shim setting from config
    shim_raw = config.get("shim", DEFAULT_SHIM)
    if not isinstance(shim_raw, str):
        msg = "Config 'shim' must be a string"
        raise TypeError(msg)
    valid_shim_settings = literal_to_set(ShimSetting)
    shim = cast("ShimSetting", shim_raw)
    if shim not in valid_shim_settings:
        msg = (
            f"Invalid shim setting: {shim!r}. "
            f"Must be one of: {', '.join(sorted(valid_shim_settings))}"
        )
        raise ValueError(msg)

    # Extract module_actions from config (already normalized in RootConfigResolved)
    module_actions_raw = config.get("module_actions", [])
    if not isinstance(module_actions_raw, list):
        msg = "Config 'module_actions' must be a list"
        raise TypeError(msg)
    # module_actions is already list[ModuleActionFull] with all defaults applied
    module_actions = cast("list[ModuleActionFull]", module_actions_raw)

    # Check if non-raw modes are implemented
    if stitch_mode != "raw":
        msg = (
            f"stitch_mode '{stitch_mode}' is not yet implemented. "
            "Only 'raw' mode is currently supported."
        )
        raise NotImplementedError(msg)

    logger.debug("Starting stitch process for package: %s", package_name)

    # Extract source_bases from config
    # (needed for package detection and module derivation)
    # source_bases is validated and normalized to list[str] in config resolution
    # It's always present in resolved config, but .get() returns object | None
    source_bases_raw = config.get("source_bases")
    user_provided_source_bases_raw = config.get("_user_provided_source_bases")
    source_bases: list[str] | None = None
    if source_bases_raw is not None:  # pyright: ignore[reportUnnecessaryComparison]
        # Type narrowing: source_bases is list[str] after config resolution
        # Cast is safe because source_bases is validated in config resolution
        source_bases = [str(mb) for mb in cast("list[str]", source_bases_raw)]  # pyright: ignore[reportUnnecessaryCast]
    user_provided_source_bases: list[str] | None = None
    if user_provided_source_bases_raw is not None:  # pyright: ignore[reportUnnecessaryComparison]
        # Type narrowing: _user_provided_source_bases is list[str] after build
        user_provided_source_bases = [
            str(mb) for mb in cast("list[str]", user_provided_source_bases_raw)
        ]  # pyright: ignore[reportUnnecessaryCast]

    # --- Package Detection (once, at the start) ---
    # Use pre-detected packages from run_build (already excludes exclude_paths)
    detected_packages_raw = config.get("detected_packages")
    if detected_packages_raw is not None and isinstance(detected_packages_raw, set):
        # Type narrowing: cast to set[str] after isinstance check
        detected_packages = cast("set[str]", detected_packages_raw)
        logger.debug("Using pre-detected packages: %s", sorted(detected_packages))
    else:
        # Fallback: detect from order_paths (shouldn't happen in normal flow)
        logger.debug("Detecting packages from order_paths (fallback)...")
        detected_packages, _discovered_parent_dirs = detect_packages_from_files(
            order_paths,
            package_name,
            source_bases=source_bases,
        )

    # --- Validation Phase ---
    logger.debug("Validating module listing...")
    verify_all_modules_listed(file_paths, order_paths, exclude_paths)

    logger.debug("Checking module order consistency...")
    # Use pre-computed topological order if available (from auto-discovery)
    topo_paths_raw = config.get("topo_paths")
    topo_paths: list[Path] | None = None
    if topo_paths_raw is not None and isinstance(topo_paths_raw, list):
        topo_paths = []
        # Type narrowing: after isinstance check, cast to help type inference
        for item in cast("list[str | Path]", topo_paths_raw):
            if isinstance(item, str):
                topo_paths.append(Path(item))
            elif isinstance(item, Path):  # pyright: ignore[reportUnnecessaryIsInstance]
                topo_paths.append(item)
    suggest_order_mismatch(
        order_paths,
        package_root,
        package_name,
        file_to_include,
        detected_packages=detected_packages,
        topo_paths=topo_paths,
        source_bases=source_bases,
        user_provided_source_bases=user_provided_source_bases,
    )

    # --- Apply affects: "stitching" actions to filter files ---
    # Before collecting modules, apply actions that affect stitching
    # to determine which files should be excluded
    # IMPORTANT: We need to preserve original module names for shim generation
    # even when files are filtered from stitching
    original_order_names_for_shims: list[str] | None = None
    if module_actions:
        # Build module-to-file mapping from order_paths
        # Check if package_root is a package directory itself
        # (when all files are in a single package, package_root is that package)
        is_package_dir = (package_root / "__init__.py").exists()
        package_name_from_root: str | None = None
        if is_package_dir:
            package_name_from_root = package_root.name

        module_to_file_for_filtering: dict[str, Path] = {}
        for file_path in order_paths:
            include = file_to_include.get(file_path)
            module_name = derive_module_name(
                file_path,
                package_root,
                include,
                source_bases=source_bases,
                user_provided_source_bases=user_provided_source_bases,
                detected_packages=detected_packages,
            )

            # If package_root is a package directory, preserve package structure
            if is_package_dir and package_name_from_root:
                # Handle __init__.py special case: represents the package itself
                if file_path.name == "__init__.py" and file_path.parent == package_root:
                    # Use package name as the module name (represents the package)
                    module_name = package_name_from_root
                else:
                    # Prepend package name to preserve structure
                    # e.g., "core" -> "oldpkg.core"
                    module_name = f"{package_name_from_root}.{module_name}"

            module_to_file_for_filtering[module_name] = file_path

        # Preserve original module names for shim generation
        # (before filtering affects shim generation)
        original_order_names_for_shims = sorted(module_to_file_for_filtering.keys())

        # Separate actions by affects value
        (
            _shims_only_actions,
            stitching_only_actions,
            both_actions,
        ) = separate_actions_by_affects(module_actions)

        # Combine stitching-only and both actions
        stitching_actions = stitching_only_actions + both_actions

        if stitching_actions:
            # Extract deleted package/module names from stitching actions
            # Actions reference package names (e.g., "pkg1"), but we need to
            # check file paths to see if they belong to deleted packages
            deleted_sources: set[str] = set()
            for action in stitching_actions:
                action_type = action.get("action", "move")
                if action_type == "delete":
                    source = action["source"]  # pyright: ignore[reportTypedDictNotRequiredAccess]
                    deleted_sources.add(source)

            # Filter order_paths to exclude files belonging to deleted packages
            if deleted_sources:
                logger.debug(
                    "Filtering files: excluding modules deleted by "
                    "stitching actions: %s",
                    sorted(deleted_sources),
                )
                filtered_order_paths: list[Path] = []
                for file_path in order_paths:
                    # Check if file belongs to a deleted package
                    # package_root might be the package directory itself
                    # (e.g., tmp_path/pkg1), so we need to check if the
                    # package_root's name matches a deleted source, or if
                    # the file path contains the deleted source
                    should_exclude = False
                    excluded_by = None

                    # Check if package_root's name matches deleted_source
                    # (package_root is the package directory, e.g., tmp_path/pkg1)
                    package_root_name = package_root.name
                    for deleted_source in deleted_sources:
                        if package_root_name == deleted_source:
                            # All files under this package_root belong to deleted
                            # package
                            should_exclude = True
                            excluded_by = deleted_source
                            break

                    # Also check file path structure for nested packages
                    # (e.g., if package_root is tmp_path but file is
                    # tmp_path/pkg1/module.py)
                    if not should_exclude:
                        try:
                            file_relative = file_path.relative_to(package_root.parent)
                        except (ValueError, AttributeError):
                            # Fallback: check absolute path
                            file_str = str(file_path).replace("\\", "/")
                            for deleted_source in deleted_sources:
                                if f"/{deleted_source}/" in file_str:
                                    should_exclude = True
                                    excluded_by = deleted_source
                                    break
                        else:
                            file_str = str(file_relative).replace("\\", "/")
                            for deleted_source in deleted_sources:
                                # Check if file path starts with deleted_source/
                                if file_str.startswith(f"{deleted_source}/"):
                                    should_exclude = True
                                    excluded_by = deleted_source
                                    break
                                # Check if file path contains deleted_source as
                                # directory
                                if f"/{deleted_source}/" in file_str:
                                    should_exclude = True
                                    excluded_by = deleted_source
                                    break

                    if not should_exclude:
                        filtered_order_paths.append(file_path)
                    else:
                        logger.debug(
                            "Excluding file %s (deleted by stitching action: %s)",
                            file_path,
                            excluded_by,
                        )
                logger.debug(
                    "File filtering: %d files before, %d files after",
                    len(order_paths),
                    len(filtered_order_paths),
                )
                order_paths = filtered_order_paths

                # Also update derived_module_names if we're tracking it
                # (derived_module_names will be recalculated in _collect_modules)

    # --- Collection Phase ---
    logger.debug("Collecting module sources...")
    # Extract external_imports from config
    external_imports_raw = config.get(
        "external_imports", DEFAULT_EXTERNAL_IMPORTS[stitch_mode]
    )
    if not isinstance(external_imports_raw, str):
        msg = "Config 'external_imports' must be a string"
        raise TypeError(msg)
    external_imports = cast("ExternalImportMode", external_imports_raw)

    # Extract internal_imports from config
    internal_imports_raw = config.get(
        "internal_imports", DEFAULT_INTERNAL_IMPORTS[stitch_mode]
    )
    if not isinstance(internal_imports_raw, str):
        msg = "Config 'internal_imports' must be a string"
        raise TypeError(msg)
    internal_imports = cast("InternalImportMode", internal_imports_raw)

    # Extract comments_mode from config
    comments_mode_raw = config.get("comments_mode", DEFAULT_COMMENTS_MODE)
    if not isinstance(comments_mode_raw, str):
        msg = "Config 'comments_mode' must be a string"
        raise TypeError(msg)
    comments_mode = cast("CommentsMode", comments_mode_raw)

    # Extract docstring_mode from config
    docstring_mode_raw = config.get("docstring_mode", DEFAULT_DOCSTRING_MODE)
    # docstring_mode can be a string or dict
    if not isinstance(docstring_mode_raw, (str, dict)):
        msg = "Config 'docstring_mode' must be a string or dict"
        raise TypeError(msg)
    docstring_mode = cast("DocstringMode", docstring_mode_raw)

    # source_bases already extracted above (before package detection)
    module_sources, all_imports, parts, derived_module_names = _collect_modules(
        order_paths,
        package_root,
        package_name,
        file_to_include,
        detected_packages,
        external_imports,
        internal_imports,
        comments_mode,
        docstring_mode,
        source_bases=source_bases,
        user_provided_source_bases=user_provided_source_bases,
    )

    # --- Parse AST once for all modules ---
    # Extract symbols (functions, classes, assignments) from all modules
    # This avoids parsing AST multiple times
    logger.debug("Extracting symbols from modules...")
    module_symbols: dict[str, ModuleSymbols] = {}
    all_function_names: set[str] = set()
    # Sort for deterministic iteration order
    for mod_name, source in sorted(module_sources.items()):
        symbols = _extract_top_level_symbols(source)
        module_symbols[mod_name] = symbols
        all_function_names.update(symbols.functions)

    # --- Main Function Detection (before collision detection) ---
    # Find main function first, so we can ignore main function collisions
    # in raw mode when auto-rename will handle them
    logger.debug("Finding main function...")
    main_function_result = find_main_function(
        config=cast("RootConfigResolved", config),
        file_paths=order_paths,
        module_sources=module_sources,
        module_names=derived_module_names,
        package_root=package_root,
        file_to_include=file_to_include,
        detected_packages=detected_packages,
    )

    # Determine if we should ignore main function collisions
    # (auto-rename will handle them in raw mode)
    ignore_functions: set[str] = set()
    stitch_mode_raw = config.get("stitch_mode", "raw")
    if stitch_mode_raw == "raw" and main_function_result is not None:
        main_function_name, _main_file_path, _main_module_path = main_function_result
        # Check if there are multiple functions with this name
        module_names_from_sources = [
            key[:-3] for key in sorted(module_sources.keys()) if key.endswith(".py")
        ]
        collisions = detect_collisions(
            main_function_result=main_function_result,
            module_sources=module_sources,
            module_names=module_names_from_sources,
        )
        # If there are collisions, auto-rename will handle them
        if len(collisions) > 1:
            ignore_functions.add(main_function_name)

    # --- Collision Detection ---
    logger.debug("Detecting name collisions...")
    detect_name_collisions(module_symbols, ignore_functions=ignore_functions)

    # --- __main__ Block Detection ---
    # Detect all __main__ blocks from original file paths (before stripping)
    logger.debug("Detecting __main__ blocks...")
    all_main_blocks = detect_main_blocks(
        file_paths=order_paths,
        package_root=package_root,
        file_to_include=file_to_include,
        detected_packages=detected_packages,
    )

    # Log main function status
    if main_function_result is not None:
        function_name, _file_path, module_path = main_function_result
        logger.info("Main function...........%s.%s()", module_path, function_name)
    else:
        # Check if main_mode is "auto" to determine if this is a non-main build
        main_mode = config.get("main_mode", "auto")
        if main_mode == "auto":
            logger.info("Main function...........not found (non-main build)")

    # Select which __main__ block to keep
    selected_main_block = select_main_block(
        main_blocks=all_main_blocks,
        main_function_result=main_function_result,
        file_paths=order_paths,
        module_names=derived_module_names,
    )

    # Log discarded blocks
    if len(all_main_blocks) > 1:
        discarded = [block for block in all_main_blocks if block != selected_main_block]
        for block in discarded:
            logger.info(
                "__main__ block...........discarded from %s",
                block.file_path,
            )

    # --- Final Assembly ---
    # Extract display configuration
    display_name_raw = config.get("display_name", "")
    description_raw = config.get("description", "")
    authors_raw = config.get("authors", "")
    repo_raw = config.get("repo", "")

    # Type guards
    if not isinstance(display_name_raw, str):
        display_name_raw = ""
    if not isinstance(description_raw, str):
        description_raw = ""
    if not isinstance(authors_raw, str):
        authors_raw = ""
    if not isinstance(repo_raw, str):
        repo_raw = ""

    final_script, _detected_packages_returned = _build_final_script(
        package_name=package_name,
        all_imports=all_imports,
        parts=parts,
        order_names=derived_module_names,
        all_function_names=all_function_names,
        detected_packages=detected_packages,
        module_mode=module_mode,
        module_actions=module_actions,
        shim=shim,
        order_paths=order_paths,
        package_root=package_root,
        file_to_include=file_to_include,
        _original_order_names_for_shims=original_order_names_for_shims,
        license_text=license_text,
        version=version,
        commit=commit,
        build_date=build_date,
        display_name=display_name_raw,
        description=description_raw,
        authors=authors_raw,
        repo=repo_raw,
        config=cast("RootConfigResolved", config),
        selected_main_block=selected_main_block,
        main_function_result=main_function_result,
        module_sources=module_sources,
        source_bases=source_bases,
    )

    # --- Verification ---
    logger.debug("Verifying assembled script...")
    verify_no_broken_imports(
        final_script, sorted(detected_packages), internal_imports=internal_imports
    )

    # --- Compile in-memory before writing ---
    logger.debug("Compiling stitched code in-memory...")
    try:
        verify_compiles_string(final_script, filename=str(out_path))
    except SyntaxError as e:
        # Compilation failed - write error file and raise
        logger.exception("Stitched code does not compile")
        error_path = _write_error_file(out_path, final_script, e)
        lineno = e.lineno or "unknown"
        error_msg = e.msg or "unknown error"
        xmsg = (
            f"Stitched code has syntax errors at line {lineno}: {error_msg}. "
            f"Error file written to: {error_path}"
        )
        raise RuntimeError(xmsg) from e

    # --- Output (compilation succeeded) ---
    out_display = shorten_path_for_display(out_path)
    logger.debug("Writing output file: %s", out_display)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(final_script, encoding="utf-8")
    out_path.chmod(0o755)

    # Clean up any existing error files (build succeeded)
    _cleanup_error_files(out_path)

    # Advance mtime to ensure visibility across filesystems
    logger.debug("Advancing mtime...")
    force_mtime_advance(out_path)

    # Post-processing: tools, compilation checks, and verification
    # Note: post_stitch_processing may warn but won't raise on post-processing
    # failures - it will revert and continue
    post_stitch_processing(out_path, post_processing=post_processing)

    logger.info(
        "Successfully stitched %d modules into %s",
        len(parts),
        out_path,
    )


# === serger.build ===
# src/serger/build.py


# --------------------------------------------------------------------------- #
# File collection functions (Phase 1)
# --------------------------------------------------------------------------- #


def expand_include_pattern(include: IncludeResolved) -> list[Path]:
    """Expand a single include pattern to a list of matching Python files.

    Args:
        include: Resolved include pattern with root and path

    Returns:
        List of resolved absolute paths to matching .py files
    """
    validate_required_keys(include, {"path", "root"}, "include")
    logger = getAppLogger()
    src_pattern = str(include["path"])
    root = Path(include["root"]).resolve()
    matches: list[Path] = []

    if src_pattern.endswith("/") and not has_glob_chars(src_pattern):
        logger.trace(
            f"[MATCH] Treating as trailing-slash directory include → {src_pattern!r}",
        )
        root_dir = root / src_pattern.rstrip("/")
        if root_dir.exists():
            all_files = [p for p in root_dir.rglob("*") if p.is_file()]
            matches = [p for p in all_files if p.suffix == ".py"]
        else:
            logger.trace(f"[MATCH] root_dir does not exist: {root_dir}")

    elif src_pattern.endswith("/**"):
        logger.trace(f"[MATCH] Treating as recursive include → {src_pattern!r}")
        root_dir = root / src_pattern.removesuffix("/**")
        if root_dir.exists():
            all_files = [p for p in root_dir.rglob("*") if p.is_file()]
            matches = [p for p in all_files if p.suffix == ".py"]
        else:
            logger.trace(f"[MATCH] root_dir does not exist: {root_dir}")

    elif has_glob_chars(src_pattern):
        logger.trace(f"[MATCH] Using glob() for pattern {src_pattern!r}")
        # Make pattern relative to root if it's absolute
        pattern_path = Path(src_pattern)
        if pattern_path.is_absolute():
            try:
                # Try to make it relative to root
                src_pattern = str(pattern_path.relative_to(root))
            except ValueError:
                # If pattern is not under root, use just the pattern name
                src_pattern = pattern_path.name
        all_matches = list(root.glob(src_pattern))
        matches = [p for p in all_matches if p.is_file() and p.suffix == ".py"]
        logger.trace(f"[MATCH] glob found {len(matches)} .py file(s)")

    else:
        logger.trace(f"[MATCH] Treating as literal include {root / src_pattern}")
        candidate = root / src_pattern
        if candidate.is_file() and candidate.suffix == ".py":
            matches = [candidate]

    # Resolve all paths to absolute
    resolved_matches = [p.resolve() for p in matches]

    for i, m in enumerate(resolved_matches):
        logger.trace(f"[MATCH]   {i + 1:02d}. {m}")

    return resolved_matches


def collect_included_files(
    includes: list[IncludeResolved],
    excludes: list[PathResolved],
) -> tuple[list[Path], dict[Path, IncludeResolved]]:
    """Expand all include patterns and apply excludes.

    Args:
        includes: List of resolved include patterns
        excludes: List of resolved exclude patterns

    Returns:
        Tuple of (filtered file paths, mapping of file to its include)
    """
    for inc in includes:
        validate_required_keys(inc, {"path", "root"}, "include")
    for exc in excludes:
        validate_required_keys(exc, {"path", "root"}, "exclude")
    logger = getAppLogger()
    all_files: set[Path] = set()
    # Track which include produced each file (for dest parameter and exclude checking)
    file_to_include: dict[Path, IncludeResolved] = {}

    # Expand all includes
    for inc in includes:
        matches = expand_include_pattern(inc)
        for match in matches:
            all_files.add(match)
            file_to_include[match] = inc  # Store the include for dest access

    logger.trace(
        f"[COLLECT] Found {len(all_files)} file(s) from {len(includes)} include(s)",
    )

    # Apply excludes - each exclude has its own root!
    filtered: list[Path] = []
    for file_path in all_files:
        # Check file against all excludes, using each exclude's root
        is_excluded = False
        for exc in excludes:
            exclude_root = Path(exc["root"]).resolve()
            exclude_patterns = [str(exc["path"])]
            if is_excluded_raw(file_path, exclude_patterns, exclude_root):
                exc_display = shorten_path_for_display(exc)
                logger.trace(
                    "[COLLECT] Excluded %s by pattern %s",
                    file_path,
                    exc_display,
                )
                is_excluded = True
                break
        if not is_excluded:
            filtered.append(file_path)

    logger.trace(f"[COLLECT] After excludes: {len(filtered)} file(s)")

    return sorted(filtered), file_to_include


def _normalize_order_pattern(entry: str, config_root: Path) -> str:
    """Normalize an order entry pattern relative to config_root.

    Args:
        entry: Order entry (path, relative or absolute)
        config_root: Root directory for resolving relative paths

    Returns:
        Normalized pattern string relative to config_root
    """
    pattern_path = Path(entry)
    if pattern_path.is_absolute():
        try:
            return str(pattern_path.relative_to(config_root))
        except ValueError:
            return pattern_path.name
    return entry


def _collect_recursive_files(
    root_dir: Path,
    included_set: set[Path],
    explicitly_ordered: set[Path],
) -> list[Path]:
    """Collect Python files recursively from a directory.

    Args:
        root_dir: Directory to search recursively
        included_set: Set of included file paths to filter by
        explicitly_ordered: Set of already-ordered paths to exclude

    Returns:
        List of matching file paths
    """
    if not root_dir.exists():
        return []
    all_files = [p for p in root_dir.rglob("*") if p.is_file()]
    return [
        p.resolve()
        for p in all_files
        if p.suffix == ".py"
        and p.resolve() in included_set
        and p.resolve() not in explicitly_ordered
    ]


def _collect_glob_files(
    pattern_str: str,
    config_root: Path,
    included_set: set[Path],
    explicitly_ordered: set[Path],
) -> list[Path]:
    """Collect Python files matching a glob pattern.

    Args:
        pattern_str: Glob pattern string
        config_root: Root directory for glob
        included_set: Set of included file paths to filter by
        explicitly_ordered: Set of already-ordered paths to exclude

    Returns:
        List of matching file paths
    """
    all_matches = list(config_root.glob(pattern_str))
    return [
        p.resolve()
        for p in all_matches
        if p.is_file()
        and p.suffix == ".py"
        and p.resolve() in included_set
        and p.resolve() not in explicitly_ordered
    ]


def _handle_literal_file_path(
    entry: str,
    pattern_str: str,
    config_root: Path,
    included_set: set[Path],
    explicitly_ordered: set[Path],
    resolved: list[Path],
) -> bool:
    """Handle a literal file path entry.

    Args:
        entry: Original order entry string
        pattern_str: Normalized pattern string
        config_root: Root directory for resolving paths
        included_set: Set of included file paths
        explicitly_ordered: Set of already-ordered paths
        resolved: List to append resolved paths to

    Returns:
        True if handled as literal file, False if should continue pattern matching
    """
    logger = getAppLogger()
    candidate = config_root / pattern_str
    if candidate.exists() and candidate.is_dir():
        # Directory without trailing slash - treat as recursive
        return False

    # Treat as literal file path
    if candidate.is_absolute():
        path = candidate.resolve()
    else:
        path = (config_root / pattern_str).resolve()

    if path not in included_set:
        xmsg = (
            f"Order entry {entry!r} resolves to {path}, which is not in included files"
        )
        raise ValueError(xmsg)

    if path in explicitly_ordered:
        logger.warning(
            "Order entry %r (→ %s) appears multiple times in order list",
            entry,
            path,
        )
    else:
        resolved.append(path)
        explicitly_ordered.add(path)
        logger.trace("[ORDER] %r → %s", entry, path)
    return True


def resolve_order_paths(
    order: list[str],
    included_files: list[Path],
    config_root: Path,
) -> list[Path]:
    """Resolve order entries (paths) to actual file paths.

    Supports multiple pattern formats:
    - Explicit file paths: "src/serger/utils.py"
    - Non-recursive glob: "src/serger/*" (matches direct children only)
    - Recursive directory: "src/serger/" (trailing slash = recursive)
    - Recursive pattern: "src/serger/**" (explicit recursive)
    - Directory without slash: "src/serger" (if directory exists, recursive)

    Wildcard patterns are expanded to match all remaining files in included_files
    that haven't been explicitly ordered yet. Matched files are sorted alphabetically.

    Args:
        order: List of order entries (paths, relative or absolute, or glob patterns)
        included_files: List of included file paths to validate against
        config_root: Root directory for resolving relative paths

    Returns:
        Ordered list of resolved file paths

    Raises:
        ValueError: If an order entry resolves to a path not in included files
    """
    logger = getAppLogger()
    included_set = set(included_files)
    resolved: list[Path] = []
    explicitly_ordered: set[Path] = set()

    for entry in order:
        pattern_str = _normalize_order_pattern(entry, config_root)
        matching_files: list[Path] = []

        # Handle different directory pattern formats
        # (matching expand_include_pattern behavior)
        if pattern_str.endswith("/") and not has_glob_chars(pattern_str):
            # Trailing slash directory: "src/serger/" → recursive match
            logger.trace("[ORDER] Treating as trailing-slash directory: %r", entry)
            root_dir = config_root / pattern_str.rstrip("/")
            matching_files = _collect_recursive_files(
                root_dir, included_set, explicitly_ordered
            )
            if not matching_files:
                logger.trace("[ORDER] Directory does not exist: %s", root_dir)

        elif pattern_str.endswith("/**"):
            # Explicit recursive pattern: "src/serger/**" → recursive match
            logger.trace("[ORDER] Treating as recursive pattern: %r", entry)
            root_dir = config_root / pattern_str.removesuffix("/**")
            matching_files = _collect_recursive_files(
                root_dir, included_set, explicitly_ordered
            )
            if not matching_files:
                logger.trace("[ORDER] Directory does not exist: %s", root_dir)

        elif has_glob_chars(pattern_str):
            # Glob pattern: "src/serger/*" → non-recursive glob
            logger.trace("[ORDER] Expanding glob pattern: %r", entry)
            matching_files = _collect_glob_files(
                pattern_str, config_root, included_set, explicitly_ordered
            )

        else:
            # Literal path (no glob chars, no trailing slash)
            candidate = config_root / pattern_str
            if candidate.exists() and candidate.is_dir():
                # Directory without trailing slash: "src/serger" → recursive match
                logger.trace("[ORDER] Treating as directory: %r", entry)
                matching_files = _collect_recursive_files(
                    candidate, included_set, explicitly_ordered
                )
            # Try to handle as literal file path
            elif _handle_literal_file_path(
                entry,
                pattern_str,
                config_root,
                included_set,
                explicitly_ordered,
                resolved,
            ):
                continue  # Skip pattern expansion logic

        # Sort matching files alphabetically for consistent ordering
        matching_files.sort()

        for path in matching_files:
            resolved.append(path)
            explicitly_ordered.add(path)
            logger.trace("[ORDER] %r → %s (pattern match)", entry, path)

        if not matching_files:
            logger.trace("[ORDER] Pattern %r matched no files", entry)

    return resolved


def find_package_root(file_paths: list[Path]) -> Path:
    """Compute common root (lowest common ancestor) of all file paths.

    Args:
        file_paths: List of file paths

    Returns:
        Common root path (lowest common ancestor)

    Raises:
        ValueError: If no common root can be found or list is empty
    """
    if not file_paths:
        xmsg = "Cannot find package root: no file paths provided"
        raise ValueError(xmsg)

    # Resolve all paths to absolute
    resolved_paths = [p.resolve() for p in file_paths]

    # Find common prefix by comparing path parts
    first_parts = list(resolved_paths[0].parts)
    common_parts: list[str] = []

    # For single file, exclude the filename itself (return parent directory)
    if len(resolved_paths) == 1:
        # Remove the last part (filename) for single file case
        common_parts = first_parts[:-1] if len(first_parts) > 1 else first_parts
    else:
        # For multiple files, find common prefix
        for i, part in enumerate(first_parts):
            # Check if all other paths have the same part at this position
            if all(
                i < len(list(p.parts)) and list(p.parts)[i] == part
                for p in resolved_paths[1:]
            ):
                common_parts.append(part)
            else:
                break

    if not common_parts:
        # No common prefix - use filesystem root
        return Path(resolved_paths[0].anchor)

    return Path(*common_parts)


# --------------------------------------------------------------------------- #
# internal helper
# --------------------------------------------------------------------------- #


def _extract_build_metadata(
    *,
    build_cfg: RootConfigResolved,
    project_root: Path,
    git_root: Path | None = None,
    disable_timestamp: bool = False,
) -> tuple[str, str, str]:
    """Extract version, commit, and build date for embedding.

    Args:
        build_cfg: Resolved build config
        project_root: Project root path (for finding pyproject.toml)
        git_root: Git repository root path (for finding .git, defaults to project_root)
        disable_timestamp: If True, use placeholder instead of real timestamp

    Returns:
        Tuple of (version, commit, build_date)
    """
    # Priority order for version:
    # 1. version from resolved config (user version -> pyproject version, resolved
    #    during config resolution if pyproject metadata was enabled)
    # 2. timestamp as last resort
    # Note: Version is fully resolved during config resolution, so we just need
    # to check the resolved config and fall back to timestamp if not set
    version = build_cfg.get("version")
    # Use git_root for commit extraction (project root), fallback to project_root
    commit_path = git_root if git_root is not None else project_root
    logger = getAppLogger()
    logger.trace(
        "_extract_build_metadata: project_root=%s, git_root=%s, commit_path=%s",
        project_root,
        git_root,
        commit_path,
    )
    commit = extract_commit(commit_path)
    logger.trace("_extract_build_metadata: extracted commit=%s", commit)

    if disable_timestamp:
        build_date = BUILD_TIMESTAMP_PLACEHOLDER
        # If still no version found, use placeholder as version
        if not version or version == "unknown":
            version = BUILD_TIMESTAMP_PLACEHOLDER
    else:
        build_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        # If still no version found, use timestamp as version
        if not version or version == "unknown":
            version = build_date

    return version, commit, build_date


def run_build(  # noqa: C901, PLR0915, PLR0912
    build_cfg: RootConfigResolved,
) -> None:
    """Execute a single build task using a fully resolved config.

    Serger handles module stitching builds (combining Python modules into
    a single executable script). File copying is the responsibility of
    pocket-build, not serger.
    """
    validate_required_keys(
        build_cfg,
        {
            "out",
            "__meta__",
            "post_processing",
            "external_imports",
            "stitch_mode",
            "comments_mode",
            "docstring_mode",
        },
        "build_cfg",
    )
    logger = getAppLogger()
    dry_run = build_cfg.get("dry_run", DEFAULT_DRY_RUN)
    validate_config = build_cfg.get("validate_config", False)

    # Extract stitching fields from config
    package = build_cfg.get("package")
    order = build_cfg.get("order")
    license_text = build_cfg.get("license", "")
    out_entry = build_cfg["out"]

    # Collect included files to check if this is a stitch build
    includes = build_cfg.get("include", [])
    excludes = build_cfg.get("exclude", [])
    # Validation happens inside collect_included_files
    included_files, file_to_include = collect_included_files(includes, excludes)

    # Safety net: Defensive check for missing package
    # This is a minimal safety check for:
    #   - Direct calls to run_build() (bypassing CLI validation)
    #   - Edge cases where validation might have been missed
    # Primary validation with detailed error messages happens in _validate_package()
    # in cli.py, which runs early in the CLI flow after config resolution.
    # Note: Package is only required for stitch builds (which need includes).
    # If there are no included files, package is not required.
    if included_files:
        if not package:
            xmsg = (
                "Package name is required for stitch builds. "
                "This should have been caught during validation. "
                "If you're calling run_build() directly, ensure package is set "
                "in the config."
            )
            raise ValueError(xmsg)

        # Type checking - ensure correct types after narrowing
        if not isinstance(package, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            xmsg = f"Invalid package name (expected str, got {type(package).__name__})"
            raise TypeError(xmsg)
    if order is not None and not isinstance(order, list):  # pyright: ignore[reportUnnecessaryIsInstance]
        xmsg = f"Invalid order (expected list, got {type(order).__name__})"
        raise TypeError(xmsg)

    # Determine output file path
    validate_required_keys(out_entry, {"path", "root"}, "build_cfg['out']")
    out_path = (out_entry["root"] / out_entry["path"]).resolve()
    # Check if it's a directory (exists and is dir) or should be treated as one
    # If path doesn't exist and has no .py extension, treat as directory
    # Use the resolved path string to check for .py extension
    # (handles absolute paths correctly)
    out_path_str = str(out_path)
    is_directory = out_path.is_dir() or (
        not out_path.exists() and not out_path_str.endswith(".py")
    )
    # Only use package for output path if we have included files (stitch build)
    if is_directory and included_files and package:
        out_path = out_path / f"{package}.py"

    # --- Validate-config exit point ---
    # Exit after file collection but before expensive stitching work
    if validate_config:
        # Build summary (accounting for output already shown)
        summary_parts: list[str] = []
        if included_files:
            summary_parts.append(f"{len(included_files)} file(s) collected")
            if package:
                summary_parts.append(f"package: {package}")
        else:
            summary_parts.append("no files (not a stitch build)")
        if out_path:
            meta = build_cfg["__meta__"]
            out_display = shorten_path_for_display(
                out_path,
                cwd=meta.get("cli_root"),
                config_dir=meta.get("config_root"),
            )
            summary_parts.append(f"output: {out_display}")
        logger.info("✓ Configuration is valid (%s)", " • ".join(summary_parts))
        return

    if not included_files:
        # No files to stitch - this is not a stitch build
        # Return early (package validation already skipped above)
        return

    # At this point, we have included_files, so package must be set and valid
    # (validated above). Type guard for type checker.
    if not package or not isinstance(package, str):  # pyright: ignore[reportUnnecessaryIsInstance]
        xmsg = (
            "Package must be set when included_files exist. "
            "This should have been caught during validation."
        )
        raise ValueError(xmsg)

    # Safety check: Don't overwrite files that aren't serger builds
    # (fail fast before doing expensive work)
    # Compute once and pass down to avoid recomputation
    is_serger_build_result = not out_path.exists() or is_serger_build(out_path)
    if out_path.exists() and not is_serger_build_result:
        xmsg = (
            f"Refusing to overwrite {out_path} because it does not appear "
            "to be a serger-generated build. If you want to overwrite this "
            "file, please delete it first or rename it."
        )
        raise RuntimeError(xmsg)

    # Get config root for resolving order paths and validating module_actions
    validate_required_keys(
        build_cfg["__meta__"], {"config_root"}, "build_cfg['__meta__']"
    )
    config_root = build_cfg["__meta__"]["config_root"]

    # Validate and normalize module_actions if present
    # (needed when module_actions are set after config resolution, e.g., in tests)
    # Import here to avoid circular dependency

    module_actions_raw = build_cfg.get("module_actions")
    if module_actions_raw:
        module_actions = validate_and_normalize_module_actions(
            module_actions_raw,
            config_dir=config_root,
        )
        # Update build_cfg with validated actions
        build_cfg["module_actions"] = module_actions
    else:
        module_actions = []

    # Collect files from source_path in module_actions
    source_path_files: set[Path] = set()
    for action in module_actions:
        if "source_path" in action:
            affects_val = action.get("affects", "shims")
            if "stitching" in affects_val or affects_val == "both":
                source_path_str = action["source_path"]
                source_path_resolved = Path(source_path_str).resolve()

                # Validate file exists (should have been validated in config resolution)
                if not source_path_resolved.exists():
                    # This should not happen if validation worked, but check anyway
                    msg = (
                        f"source_path file does not exist: {source_path_resolved}. "
                        f"This should have been caught during config validation."
                    )
                    raise ValueError(msg)

                source_path_files.add(source_path_resolved)

                # Add to file_to_include if not already present
                if source_path_resolved not in file_to_include:
                    # Create a synthetic IncludeResolved for this file
                    # Use the file's parent directory as root
                    synthetic_include: IncludeResolved = {
                        "path": str(source_path_resolved),
                        "root": source_path_resolved.parent,
                        "origin": "code",  # Mark as code-generated
                    }
                    file_to_include[source_path_resolved] = synthetic_include

    # Merge source_path files into included_files
    all_included_files = sorted(set(included_files) | source_path_files)

    # Resolve exclude_names to paths (exclude_names is list[str] of paths)
    # Do this early so we can exclude them before package detection
    exclude_names_raw = build_cfg.get("exclude_names", [])
    exclude_paths: list[Path] = []
    if exclude_names_raw:
        included_set = set(all_included_files)
        for exclude_name in cast("list[str]", exclude_names_raw):
            # Resolve path (absolute or relative to config_root)
            if Path(exclude_name).is_absolute():
                exclude_path = Path(exclude_name).resolve()
            else:
                exclude_path = (config_root / exclude_name).resolve()
            if exclude_path in included_set:
                exclude_paths.append(exclude_path)

    # Filter out excluded files to get final set for stitching
    # Note: source_path files override excludes (they're added after initial collection)
    # and should not be filtered out by exclude_paths
    exclude_set = set(exclude_paths)
    # Remove source_path files from exclude_set to ensure they're not filtered out
    exclude_set -= source_path_files
    final_files = [f for f in all_included_files if f not in exclude_set]

    if not final_files:
        xmsg = "No files remaining after exclusions"
        raise ValueError(xmsg)

    # Warn about files outside project directory
    cwd = Path.cwd().resolve()
    config_root_resolved = Path(config_root).resolve()
    # Get source_bases and installed_bases to check if file is in them
    source_bases = build_cfg.get("source_bases", [])
    installed_bases = build_cfg.get("installed_bases", [])
    # Convert to Path objects for comparison
    source_base_paths = [Path(base).resolve() for base in source_bases]
    installed_base_paths = [Path(base).resolve() for base in installed_bases]
    for file_path in final_files:
        file_path_resolved = file_path.resolve()
        # Check if file is inside source_bases or installed_bases
        is_in_source_bases = any(
            file_path_resolved.is_relative_to(base_path)
            for base_path in source_base_paths
        )
        is_in_installed_bases = any(
            file_path_resolved.is_relative_to(base_path)
            for base_path in installed_base_paths
        )
        # Check if file is outside both config_root and CWD
        is_outside_config = not file_path_resolved.is_relative_to(config_root_resolved)
        is_outside_cwd = not file_path_resolved.is_relative_to(cwd)
        # Only warn if outside config/CWD AND not in source_bases or installed_bases
        should_warn = (
            is_outside_config
            and is_outside_cwd
            and not is_in_source_bases
            and not is_in_installed_bases
        )
        if should_warn:
            logger.warning(
                "Including file outside project directory: %s "
                "(config root: %s, CWD: %s)",
                file_path_resolved,
                config_root_resolved,
                cwd,
            )

    # Compute package root for module name derivation (needed for auto-discovery)
    package_root = find_package_root(final_files)

    # Detect packages once from final files (after all exclusions)
    logger.debug("Detecting packages from included files (after exclusions)...")
    source_bases = build_cfg.get("source_bases", [])
    # Save user-provided source_bases (from config, before adding discovered ones)
    # Filter out package directories (those with __init__.py) as they shouldn't be used
    # for module name derivation (would lose package name)
    user_provided_source_bases: list[str] = []
    for base_str in source_bases:
        base_path = Path(base_str)
        # Skip if this is a package directory (has __init__.py)
        # Package directories extracted from includes shouldn't be used for derivation
        if (base_path / "__init__.py").exists():
            logger.trace(
                "[MODULE_BASES] Skipping package directory for user-provided bases: %s",
                base_str,
            )
            continue
        user_provided_source_bases.append(base_str)
    detected_packages, discovered_parent_dirs = detect_packages_from_files(
        final_files, package, source_bases=source_bases
    )

    # Add discovered package parent directories to source_bases (lowest priority)
    if discovered_parent_dirs:
        # Deduplicate while preserving order (add at end)
        seen_bases = set(source_bases)
        for parent_dir in discovered_parent_dirs:
            if parent_dir not in seen_bases:
                seen_bases.add(parent_dir)
                source_bases.append(parent_dir)
                logger.debug(
                    "[MODULE_BASES] Added discovered package parent directory: %s",
                    parent_dir,
                )
                # Also add to user_provided_source_bases if it's not a package directory
                # (discovered parent directories are typically not package directories)
                parent_path = Path(parent_dir)
                if (
                    not (parent_path / "__init__.py").exists()
                    and parent_dir not in user_provided_source_bases
                ):
                    user_provided_source_bases.append(parent_dir)
                    logger.trace(
                        "[MODULE_BASES] Added discovered parent directory to "
                        "user_provided_source_bases: %s",
                        parent_dir,
                    )
        # Update build_cfg with extended source_bases
        build_cfg["source_bases"] = source_bases

    # Now detect base directories in source_bases as packages if they contain
    # detected packages (must happen after source_bases is fully populated)
    # This handles cases where a directory in source_bases contains packages
    # but doesn't have __init__.py itself (namespace packages)
    # Re-detect packages now that source_bases is fully populated
    # This will pick up base directories that are now in source_bases
    detected_packages_updated, _ = detect_packages_from_files(
        final_files, package, source_bases=source_bases
    )
    # Merge any newly detected packages
    if detected_packages_updated != detected_packages:
        newly_detected = detected_packages_updated - detected_packages
        if newly_detected:
            detected_packages = detected_packages_updated
            logger.debug(
                "[MODULE_BASES] Detected additional packages after adding "
                "discovered bases: %s",
                sorted(newly_detected),
            )
    # Store user-provided source_bases (filtered) for use in derive_module_name
    # This excludes package directories extracted from includes
    # Use dict update to avoid TypedDict type error for internal field
    build_cfg_dict: dict[str, object] = build_cfg  # type: ignore[assignment]
    build_cfg_dict["_user_provided_source_bases"] = (
        user_provided_source_bases if user_provided_source_bases else []
    )

    # Resolve order paths (order is list[str] of paths, or None for auto-discovery)
    topo_paths: list[Path] | None = None
    if order is not None:
        # Use explicit order from config (filtered to final_files)
        order_paths = resolve_order_paths(order, final_files, config_root)
        logger.debug("Using explicit order from config (%d entries)", len(order_paths))
        # Add source_path files that aren't already in order_paths
        order_paths_set = set(order_paths)
        for source_path_file in sorted(source_path_files):
            if source_path_file not in order_paths_set:
                order_paths.append(source_path_file)
                logger.debug("Added source_path file to order: %s", source_path_file)
    else:
        # Auto-discover order via topological sort (using final_files)
        logger.info("Auto-discovering module order via topological sort...")
        order_paths = compute_module_order(
            final_files,
            package_root,
            package,
            file_to_include,
            detected_packages=detected_packages,
            source_bases=source_bases,
            user_provided_source_bases=user_provided_source_bases,
        )
        logger.debug("Auto-discovered order (%d modules)", len(order_paths))
        # When auto-discovered, order_paths IS the topological order, so we can reuse it
        topo_paths = order_paths

    # Prepare config dict for stitch_modules
    # post_processing, external_imports, stitch_mode, comments_mode already validated
    display_name_raw = build_cfg.get("display_name", "")
    description_raw = build_cfg.get("description", "")
    repo_raw = build_cfg.get("repo", "")
    post_processing = build_cfg["post_processing"]
    external_imports = build_cfg["external_imports"]
    stitch_mode = build_cfg["stitch_mode"]
    module_mode = build_cfg["module_mode"]
    shim = build_cfg.get("shim", "all")
    comments_mode = build_cfg["comments_mode"]
    docstring_mode = build_cfg["docstring_mode"]
    # module_actions already validated and normalized above

    stitch_config: dict[str, object] = {
        "package": package,
        "order": order_paths,  # Pass resolved paths (already excludes exclude_paths)
        "exclude_names": exclude_paths,  # Pass resolved paths (for validation)
        "display_name": display_name_raw,
        "description": description_raw,
        "repo": repo_raw,
        "topo_paths": topo_paths,  # Pre-computed topological order (if auto-discovered)
        "external_imports": external_imports,
        "stitch_mode": stitch_mode,
        "module_mode": module_mode,
        "shim": shim,
        "module_actions": module_actions,
        "comments_mode": comments_mode,
        "docstring_mode": docstring_mode,
        "main_mode": build_cfg.get("main_mode", "auto"),
        "main_name": build_cfg.get("main_name"),
        "detected_packages": detected_packages,  # Pre-detected packages
        "source_bases": source_bases,  # For package detection fallback
        "_user_provided_source_bases": build_cfg.get(
            "_user_provided_source_bases", []
        ),  # User-provided (filtered) for derive_module_name
        "__meta__": build_cfg["__meta__"],  # For config_dir access in fallback
    }

    # Extract metadata for embedding
    # Use config_root for finding pyproject.toml (project root) and for git
    config_root = build_cfg["__meta__"]["config_root"]
    # Resolve to absolute path for git operations
    git_root = config_root.resolve()
    disable_timestamp = build_cfg.get("disable_build_timestamp", False)
    version, commit, build_date = _extract_build_metadata(
        build_cfg=build_cfg,
        project_root=config_root,
        git_root=git_root,  # Use resolved project root for git operations
        disable_timestamp=disable_timestamp,
    )

    # Create parent directory if needed (skip in dry-run)
    if not dry_run:
        out_path.parent.mkdir(parents=True, exist_ok=True)

    # Dry-run exit: simulate full pre-stitch pipeline, exit before stitching
    if dry_run:
        # Build comprehensive summary
        dry_run_summary_parts: list[str] = []
        dry_run_summary_parts.append(f"Package: {package}")
        dry_run_summary_parts.append(f"Files: {len(final_files)} module(s)")
        dry_run_summary_parts.append(f"Output: {out_path}")

        # Add detected packages (if verbose/debug)
        if detected_packages:
            packages_str = ", ".join(sorted(detected_packages))
            logger.debug("Detected packages: %s", packages_str)

        # Add order resolution method
        order_method = "explicit" if order is not None else "auto-discovered"
        logger.debug("Order: %s (%d modules)", order_method, len(order_paths))

        logger.info("🧪 (dry-run) Would stitch: %s", " • ".join(dry_run_summary_parts))
        return

    meta = build_cfg["__meta__"]
    out_display = shorten_path_for_display(
        out_path,
        cwd=meta.get("cli_root"),
        config_dir=meta.get("config_root"),
    )
    logger.info("🧵 Stitching %s → %s", package, out_display)

    try:
        stitch_modules(
            config=stitch_config,
            file_paths=included_files,
            package_root=package_root,
            file_to_include=file_to_include,
            out_path=out_path,
            license_text=license_text,
            version=version,
            commit=commit,
            build_date=build_date,
            post_processing=post_processing,
            is_serger_build=is_serger_build_result,
        )
        logger.minimal("✅ Stitch completed → %s\n", out_display)
    except RuntimeError as e:
        xmsg = f"Stitch build failed: {e}"
        raise RuntimeError(xmsg) from e


# === serger.actions ===
# src/serger/actions.py


def _collect_included_files(resolved: RootConfigResolved) -> list[Path]:
    """Collect all include globs into a unique list of files.

    Uses collect_included_files() from build.py for consistency.
    Watch mode respects excludes from config.
    """
    # include and exclude are optional, but if present they need validation
    # Validation happens inside collect_included_files
    includes = resolved.get("include", [])
    excludes = resolved.get("exclude", [])
    # Collect files (watch mode respects excludes from config)
    files, _file_to_include = collect_included_files(includes, excludes)

    # Return unique sorted list
    return sorted(set(files))


def watch_for_changes(
    rebuild_func: Callable[[], None],
    resolved: RootConfigResolved,
    interval: float = DEFAULT_WATCH_INTERVAL,
) -> None:
    """Poll file modification times and rebuild when changes are detected.

    Features:
    - Skips files inside the build's output directory.
    - Re-expands include patterns every loop to detect newly created files.
    - Polling interval defaults to 1 second (tune 0.5–2.0 for balance).
    Stops on KeyboardInterrupt.
    """
    logger = getAppLogger()
    logger.info(
        "👀 Watching for changes (interval=%.2fs)... Press Ctrl+C to stop.", interval
    )

    # discover at start
    included_files = _collect_included_files(resolved)

    mtimes: dict[Path, float] = {
        f: f.stat().st_mtime for f in included_files if f.exists()
    }

    # Collect output path to ignore (can be directory or file)
    validate_required_keys(resolved, {"out"}, "resolved config")
    validate_required_keys(resolved["out"], {"path", "root"}, "resolved['out']")
    out_path = (resolved["out"]["root"] / resolved["out"]["path"]).resolve()

    rebuild_func()  # initial build

    try:
        while True:
            time.sleep(interval)

            # 🔁 re-expand every tick so new/removed files are tracked
            included_files = _collect_included_files(resolved)

            logger.trace(f"[watch] Checking {len(included_files)} files for changes")

            changed: list[Path] = []
            for f in included_files:
                # skip files that are inside or equal to the output path
                if f == out_path or f.is_relative_to(out_path):
                    continue  # ignore output files/folders
                old_m = mtimes.get(f)
                if not f.exists():
                    if old_m is not None:
                        changed.append(f)
                        mtimes.pop(f, None)
                    continue
                new_m = f.stat().st_mtime
                if old_m is None or new_m > old_m:
                    changed.append(f)
                    mtimes[f] = new_m

            if changed:
                logger.info(
                    "\n🔁 Detected %d modified file(s). Rebuilding...", len(changed)
                )
                rebuild_func()
                # refresh timestamps after rebuild
                mtimes = {f: f.stat().st_mtime for f in included_files if f.exists()}
    except KeyboardInterrupt:
        logger.info("\n🛑 Watch stopped.")


def _get_metadata_from_header(script_path: Path) -> tuple[str, str]:
    """Extract version and commit from standalone script.

    Prefers in-file constants (__version__, __commit__) if present;
    falls back to commented header tags.
    """
    logger = getAppLogger()
    version = "unknown"
    commit = "unknown"

    logger.trace("reading commit from header:", script_path)

    with suppress(Exception):
        text = script_path.read_text(encoding="utf-8")

        # --- Prefer Python constants if defined ---
        const_version = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", text)
        const_commit = re.search(r"__commit__\s*=\s*['\"]([^'\"]+)['\"]", text)
        if const_version:
            version = const_version.group(1)
        if const_commit:
            commit = const_commit.group(1)

        # --- Fallback: header lines ---
        if version == "unknown" or commit == "unknown":
            for line in text.splitlines():
                if line.startswith("# Version:") and version == "unknown":
                    version = line.split(":", 1)[1].strip()
                elif line.startswith("# Commit:") and commit == "unknown":
                    commit = line.split(":", 1)[1].strip()

    return version, commit


def get_metadata() -> Metadata:
    """Return (version, commit) tuple for this tool.

    - Standalone script → parse from header
    - Source installed → read pyproject.toml + git
    """
    script_path = Path(__file__)
    logger = getAppLogger()
    logger.trace("get_metadata ran from:", Path(__file__).resolve())

    # --- Heuristic: standalone script lives outside `src/` ---
    if globals().get("__STANDALONE__", False):
        version, commit = _get_metadata_from_header(script_path)
        logger.trace(f"got standalone version {version} with commit {commit}")
        return Metadata(version, commit)

    # --- Modular / source installed case ---

    # Source package case
    version = "unknown"
    commit = "unknown"

    # Try pyproject.toml for version
    root = Path(__file__).resolve().parents[2]
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        logger.trace(f"trying to read metadata from {pyproject}")
        text = pyproject.read_text()
        match = re.search(r'(?m)^\s*version\s*=\s*["\']([^"\']+)["\']', text)
        if match:
            version = match.group(1)

    # Try git for commit
    with suppress(Exception):
        logger.trace("trying to get commit from git")
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],  # noqa: S607
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        commit = result.stdout.strip()

    logger.trace(f"got package version {version} with commit {commit}")
    return Metadata(version, commit)


# === serger.selftest ===
# src/serger/selftest.py
"""Self-test functionality for verifying stitching works correctly."""


# Expected exit code from test script (42 * 2 = 84)
EXPECTED_EXIT_CODE = 84


def _create_test_package(pkg_dir: Path) -> None:
    """Create test package modules for selftest.

    Args:
        pkg_dir: Directory where test package modules should be created

    Raises:
        PermissionError: If unable to write files (environment issue)
        OSError: If directory operations fail (environment issue)
    """
    logger = getAppLogger()
    logger.trace("[SELFTEST] _create_test_package: pkg_dir=%s", pkg_dir)

    # base.py - simple module with a constant
    base_file = pkg_dir / "base.py"
    logger.trace("[SELFTEST] Creating base.py at %s", base_file)
    base_file.write_text(
        '"""Base module for selftest."""\nBASE_VALUE = 42\n',
        encoding="utf-8",
    )

    # utils.py - module that uses base
    utils_file = pkg_dir / "utils.py"
    logger.trace("[SELFTEST] Creating utils.py at %s", utils_file)
    utils_file.write_text(
        '"""Utils module for selftest."""\n'
        "from testpkg.base import BASE_VALUE\n\n"
        "def get_value() -> int:\n"
        "    return BASE_VALUE * 2\n",
        encoding="utf-8",
    )

    # main.py - entry point that uses utils
    main_file = pkg_dir / "main.py"
    logger.trace("[SELFTEST] Creating main.py at %s", main_file)
    main_file.write_text(
        '"""Main module for selftest."""\n'
        "from testpkg.utils import get_value\n\n"
        "def main(args: list[str] | None = None) -> int:\n"
        "    result = get_value()\n"
        "    print(f'Result: {result}')\n"
        "    return result\n",
        encoding="utf-8",
    )

    logger.debug(
        "[SELFTEST] Created test package modules: %s, %s, %s",
        base_file.name,
        utils_file.name,
        main_file.name,
    )


def _create_build_config(
    test_pkg_dir: Path, out_file: Path, tmp_dir: Path
) -> RootConfigResolved:
    """Create build configuration for test package stitching.

    Args:
        test_pkg_dir: Directory containing test package modules
        out_file: Path where stitched output should be written
        tmp_dir: Temporary directory root for path resolution

    Returns:
        RootConfigResolved configuration for stitching

    Raises:
        RuntimeError: If config construction fails (program bug)
    """
    logger = getAppLogger()
    logger.trace(
        "[SELFTEST] _create_build_config: test_pkg_dir=%s, out_file=%s, tmp_dir=%s",
        test_pkg_dir,
        out_file,
        tmp_dir,
    )

    try:
        include_pattern = str(test_pkg_dir / "*.py")
        logger.trace("[SELFTEST] Resolving include pattern: %s", include_pattern)
        include_resolved = make_includeresolved(include_pattern, tmp_dir, "code")
        logger.trace("[SELFTEST] Resolved include: %s", include_resolved)

        logger.trace("[SELFTEST] Resolving output path: %s", out_file)
        out_resolved = make_pathresolved(out_file, tmp_dir, "code")
        logger.trace("[SELFTEST] Resolved output: %s", out_resolved)

        # Order entries should be file paths relative to tmp_dir (config_root)
        # Since include pattern is testpkg_dir/*.py, files are under testpkg_dir
        order_entries = [
            str((test_pkg_dir / "base.py").relative_to(tmp_dir)),
            str((test_pkg_dir / "utils.py").relative_to(tmp_dir)),
            str((test_pkg_dir / "main.py").relative_to(tmp_dir)),
        ]
        config = {
            "package": "testpkg",
            "order": order_entries,
            "include": [include_resolved],
            "exclude": [],
            "out": out_resolved,
            # Don't care about user's gitignore in selftest
            "respect_gitignore": False,
            "log_level": DEFAULT_LOG_LEVEL,
            "strict_config": DEFAULT_STRICT_CONFIG,
            "dry_run": False,
            "watch_interval": DEFAULT_WATCH_INTERVAL,
            "__meta__": {"cli_root": tmp_dir, "config_root": tmp_dir},
            # Required fields with defaults
            "internal_imports": DEFAULT_INTERNAL_IMPORTS[DEFAULT_STITCH_MODE],
            "external_imports": DEFAULT_EXTERNAL_IMPORTS[DEFAULT_STITCH_MODE],
            "stitch_mode": DEFAULT_STITCH_MODE,
            "module_mode": DEFAULT_MODULE_MODE,
            "comments_mode": DEFAULT_COMMENTS_MODE,
            "docstring_mode": DEFAULT_DOCSTRING_MODE,
            "post_processing": cast(
                "Any",
                {
                    "enabled": True,
                    "category_order": [],
                    "categories": {},
                },
            ),
        }
        logger.trace(
            "[SELFTEST] Build config created: package=%s, order=%s",
            "testpkg",
            config["order"],
        )
        return cast("RootConfigResolved", config)
    except Exception as e:
        xmsg = f"Config construction failed: {e}"
        logger.trace("[SELFTEST] Config construction error: %s", e, exc_info=True)
        raise RuntimeError(xmsg) from e


def _execute_selftest_build(build_cfg: RootConfigResolved) -> None:
    """Execute stitch build in both dry-run and real modes.

    Args:
        build_cfg: Build configuration to execute

    Raises:
        RuntimeError: If build execution fails (program bug)
    """
    # run_build will validate required keys, but we need package for this function
    validate_required_keys(build_cfg, {"package"}, "build_cfg")
    logger = getAppLogger()
    logger.trace(
        "[SELFTEST] _execute_selftest_build: package=%s", build_cfg.get("package")
    )

    for dry_run in (True, False):
        build_cfg["dry_run"] = dry_run
        phase = "dry-run" if dry_run else "real"
        logger.debug("[SELFTEST] Running stitch build (%s mode)", phase)
        logger.trace(
            "[SELFTEST] Build config: package=%s, out=%s, include_count=%d",
            build_cfg.get("package"),
            build_cfg.get("out"),
            len(build_cfg.get("include", [])),
        )

        phase_start = time.time()
        try:
            run_build(build_cfg)
            phase_elapsed = time.time() - phase_start
            logger.trace(
                "[SELFTEST] Build phase '%s' completed in %.3fs",
                phase,
                phase_elapsed,
            )
        except Exception as e:
            phase_elapsed = time.time() - phase_start
            logger.trace(
                "[SELFTEST] Build phase '%s' failed after %.3fs: %s",
                phase,
                phase_elapsed,
                e,
                exc_info=True,
            )
            xmsg = f"Stitch build failed ({phase} mode): {e}"
            raise RuntimeError(xmsg) from e


def _verify_compiles(stitched_file: Path) -> None:
    """Verify that the stitched file compiles without syntax errors.

    Args:
        stitched_file: Path to stitched Python file

    Raises:
        RuntimeError: If compilation fails (program bug - stitched output invalid)
    """
    logger = getAppLogger()
    file_size = stitched_file.stat().st_size
    logger.trace(
        "[SELFTEST] _verify_compiles: file=%s, size=%d bytes",
        stitched_file,
        file_size,
    )

    try:
        py_compile.compile(str(stitched_file), doraise=True)
        logger.debug(
            "[SELFTEST] Stitched file compiles successfully: %s", stitched_file
        )
    except py_compile.PyCompileError as e:
        lineno = getattr(e, "lineno", "unknown")
        logger.trace("[SELFTEST] Compilation error: %s at line %s", e.msg, lineno)
        xmsg = f"Stitched file has syntax errors at line {lineno}: {e.msg}"
        raise RuntimeError(xmsg) from e


def _verify_executes(stitched_file: Path) -> None:
    """Verify that the stitched file executes and produces expected output.

    Args:
        stitched_file: Path to stitched Python file

    Raises:
        FileNotFoundError: If python3 is not found (environment issue)
        RuntimeError: If execution fails or produces unexpected output (program bug)
        AssertionError: If output validation fails (program bug)
    """
    logger = getAppLogger()
    logger.trace("[SELFTEST] _verify_executes: file=%s", stitched_file)

    python_cmd = ["python3", str(stitched_file)]
    logger.trace("[SELFTEST] Executing: %s", " ".join(python_cmd))

    try:
        exec_start = time.time()
        result = subprocess.run(  # noqa: S603
            python_cmd,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        exec_elapsed = time.time() - exec_start
        logger.trace(
            "[SELFTEST] Execution completed in %.3fs: exit=%d, "
            "stdout_len=%d, stderr_len=%d",
            exec_elapsed,
            result.returncode,
            len(result.stdout),
            len(result.stderr),
        )

        # Check that expected output is present
        output = result.stdout
        expected_output = f"Result: {EXPECTED_EXIT_CODE}"
        if expected_output not in output:
            logger.trace(
                "[SELFTEST] Output mismatch: expected=%r, got_stdout=%r, got_stderr=%r",
                expected_output,
                output,
                result.stderr,
            )
            xmsg = (
                f"Unexpected output from stitched script. "
                f"Expected '{expected_output}' in stdout, but got: {output!r}. "
                f"stderr: {result.stderr!r}, exit code: {result.returncode}"
            )
            raise AssertionError(xmsg)

        # Exit code 84 is expected (the return value of main())
        # Any other non-zero exit code indicates an error
        if result.returncode not in {EXPECTED_EXIT_CODE, 0}:
            logger.trace(
                "[SELFTEST] Unexpected exit code: got=%d, expected=%s",
                result.returncode,
                {EXPECTED_EXIT_CODE, 0},
            )
            xmsg = (
                f"Stitched script execution failed with exit code "
                f"{result.returncode} (expected {EXPECTED_EXIT_CODE} or 0). "
                f"stderr: {result.stderr!r}"
            )
            raise RuntimeError(xmsg)

        logger.debug(
            "[SELFTEST] Stitched file executes correctly: exit=%d, output=%r",
            result.returncode,
            output.strip(),
        )

    except FileNotFoundError as e:
        # python3 not found - environment issue
        logger.trace("[SELFTEST] python3 not found: %s", e)
        xmsg = (
            f"python3 interpreter not found. Please ensure Python 3 is installed "
            f"and available in your PATH. Error: {e}"
        )
        raise FileNotFoundError(xmsg) from e

    except subprocess.TimeoutExpired as e:
        logger.trace("[SELFTEST] Execution timed out after 10s")
        xmsg = "Stitched script execution timed out after 10 seconds"
        raise RuntimeError(xmsg) from e


def _verify_content(stitched_file: Path) -> None:
    """Verify that key content markers are present in stitched file.

    Args:
        stitched_file: Path to stitched Python file

    Raises:
        AssertionError: If expected markers are not found (program bug)
    """
    logger = getAppLogger()
    logger.trace("[SELFTEST] _verify_content: file=%s", stitched_file)

    content = stitched_file.read_text(encoding="utf-8")
    content_size = len(content)
    line_count = content.count("\n") + 1
    logger.trace(
        "[SELFTEST] Content size: %d bytes, %d lines", content_size, line_count
    )

    expected_markers = [
        "# === testpkg.base ===",
        "# === testpkg.utils ===",
        "# === testpkg.main ===",
        "BASE_VALUE = 42",
        "def get_value()",
        "def main(",
    ]
    logger.trace("[SELFTEST] Checking %d content markers", len(expected_markers))

    for marker in expected_markers:
        if marker not in content:
            logger.trace("[SELFTEST] Missing marker: %r", marker)
            xmsg = (
                f"Expected marker '{marker}' not found in stitched output. "
                f"This indicates the stitching process did not include "
                f"expected content."
            )
            raise AssertionError(xmsg)

    logger.debug(
        "[SELFTEST] All content markers verified (%d markers)",
        len(expected_markers),
    )


def run_selftest() -> bool:  # noqa: PLR0915
    """Run a lightweight functional test of the stitching functionality.

    Creates a simple test package with multiple Python modules, stitches them
    together, and verifies the output compiles and executes correctly.

    Returns:
        True if selftest passes, False otherwise
    """
    logger = getAppLogger()

    # Always run selftest with at least DEBUG level, then revert
    with logger.useLevel("DEBUG", minimum=True):
        logger.info("🧪 Running self-test...")

        # Log environment info for GitHub issue reporting
        try:
            metadata = get_metadata()
            logger.debug(
                "[SELFTEST] Environment: %s %s, Python %s (%s) on %s",
                PROGRAM_DISPLAY,
                metadata,
                platform.python_version(),
                platform.python_implementation(),
                platform.system(),
            )
            logger.debug(
                "[SELFTEST] Python details: %s",
                sys.version.replace("\n", " "),
            )
        except Exception:  # noqa: BLE001
            # Metadata is optional for selftest, continue if it fails
            logger.trace("[SELFTEST] Failed to get metadata (non-fatal)")

        start_time = time.time()
        tmp_dir: Path | None = None
        stitched_file: Path | None = None

        try:
            logger.trace("[SELFTEST] Creating temporary directory")
            tmp_dir = Path(tempfile.mkdtemp(prefix=f"{PROGRAM_SCRIPT}-selftest-"))
            test_pkg_dir = tmp_dir / "testpkg"
            out_dir = tmp_dir / "out"
            test_pkg_dir.mkdir()
            out_dir.mkdir()

            logger.debug("[SELFTEST] Temp dir: %s", tmp_dir)
            logger.trace(
                "[SELFTEST] Test package dir: %s, Output dir: %s",
                test_pkg_dir,
                out_dir,
            )

            # --- Phase 1: Create test package modules ---
            phase_start = time.time()
            logger.debug("[SELFTEST] Phase 1: Creating test package modules")
            _create_test_package(test_pkg_dir)
            logger.debug(
                "[SELFTEST] Phase 1 completed in %.3fs",
                time.time() - phase_start,
            )

            # --- Phase 2: Prepare stitch config ---
            phase_start = time.time()
            logger.debug("[SELFTEST] Phase 2: Preparing stitch configuration")
            stitched_file = out_dir / "testpkg.py"
            build_cfg = _create_build_config(test_pkg_dir, stitched_file, tmp_dir)
            logger.debug(
                "[SELFTEST] Phase 2 completed in %.3fs, output will be: %s",
                time.time() - phase_start,
                stitched_file,
            )

            # --- Phase 3: Execute build (both dry and real) ---
            phase_start = time.time()
            logger.debug("[SELFTEST] Phase 3: Executing stitch build")
            _execute_selftest_build(build_cfg)
            logger.debug(
                "[SELFTEST] Phase 3 completed in %.3fs",
                time.time() - phase_start,
            )

            # --- Phase 4: Validate stitched output ---
            phase_start = time.time()
            logger.debug("[SELFTEST] Phase 4: Validating stitched output")
            if not stitched_file.exists():
                xmsg = (
                    f"Expected stitched output file missing: {stitched_file}. "
                    f"This indicates the build process did not create the output file."
                )
                raise RuntimeError(xmsg)  # noqa: TRY301

            file_size = stitched_file.stat().st_size
            logger.debug(
                "[SELFTEST] Stitched file exists: %s (%d bytes)",
                stitched_file,
                file_size,
            )
            logger.trace(
                "[SELFTEST] Stitched file path (absolute): %s",
                stitched_file.resolve(),
            )

            _verify_compiles(stitched_file)
            _verify_executes(stitched_file)
            _verify_content(stitched_file)
            logger.debug(
                "[SELFTEST] Phase 4 completed in %.3fs",
                time.time() - phase_start,
            )

            elapsed = time.time() - start_time
            logger.info(
                "✅ Self-test passed in %.2fs — %s is working correctly.",
                elapsed,
                PROGRAM_DISPLAY,
            )
            logger.trace("[SELFTEST] Total test duration: %.6fs", elapsed)

        except (PermissionError, OSError, FileNotFoundError) as e:
            # Environment issues: file system permissions, temp dir creation,
            # python3 not found, missing dependencies, etc.
            if isinstance(e, FileNotFoundError) and "python3" in str(e).lower():
                msg_template = (
                    "Self-test failed due to missing dependency or tool "
                    "(this is likely a problem with your environment, not with %s): %s"
                )
            else:
                msg_template = (
                    "Self-test failed due to environment issue (this is likely "
                    "a problem with your system setup, not with %s): %s"
                )
            logger.errorIfNotDebug(msg_template, PROGRAM_DISPLAY, e)
            logger.debug(
                "[SELFTEST] Environment issue details: error=%s, tmp_dir=%s",
                e,
                tmp_dir,
            )
            return False

        except RuntimeError as e:
            # Program bugs: build failures, compilation errors, execution errors
            stitched_file_info = str(stitched_file) if stitched_file else "N/A"
            logger.errorIfNotDebug(
                "Self-test failed (this appears to be a bug in %s): %s",
                PROGRAM_DISPLAY,
                e,
            )
            logger.debug(
                "[SELFTEST] Program bug details: error=%s, tmp_dir=%s, "
                "stitched_file=%s",
                e,
                tmp_dir,
                stitched_file_info,
            )
            return False

        except AssertionError as e:
            # Program bugs: validation failures, content mismatches
            stitched_file_info = str(stitched_file) if stitched_file else "N/A"
            logger.errorIfNotDebug(
                "Self-test failed validation (this appears to be a bug in %s): %s",
                PROGRAM_DISPLAY,
                e,
            )
            logger.debug(
                "[SELFTEST] Validation failure: error=%s, tmp_dir=%s, stitched_file=%s",
                e,
                tmp_dir,
                stitched_file_info,
            )
            return False

        except Exception as e:
            # Unexpected program bugs: should never happen
            logger.exception(
                "Unexpected self-test failure (this is a bug in %s). "
                "Please report this traceback in a GitHub issue:",
                PROGRAM_DISPLAY,
            )
            logger.debug(
                "[SELFTEST] Unexpected error: type=%s, error=%s, tmp_dir=%s",
                type(e).__name__,
                e,
                tmp_dir,
            )
            return False

        else:
            return True

        finally:
            if tmp_dir and tmp_dir.exists():
                logger.trace("[SELFTEST] Cleaning up temp dir: %s", tmp_dir)
                shutil.rmtree(tmp_dir, ignore_errors=True)


# === serger.cli ===
# src/serger/cli.py


# --------------------------------------------------------------------------- #
# CLI setup and helpers
# --------------------------------------------------------------------------- #


class HintingArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        # Build known option strings: ["-v", "--verbose", "--log-level", ...]
        known_opts: list[str] = []
        for action in self._actions:
            known_opts.extend([s for s in action.option_strings if s])

        hint_lines: list[str] = []
        # Argparse message for bad flags is typically
        # "unrecognized arguments: --inclde ..."
        if "unrecognized arguments:" in message:
            bad = message.split("unrecognized arguments:", 1)[1].strip()
            # Split conservatively on whitespace
            bad_args = [tok for tok in bad.split() if tok.startswith("-")]
            for arg in bad_args:
                close = get_close_matches(arg, known_opts, n=1, cutoff=0.6)
                if close:
                    hint_lines.append(f"Hint: did you mean {close[0]}?")

        # Print usage + the original error
        self.print_usage(sys.stderr)
        full = f"{self.prog}: error: {message}"
        if hint_lines:
            full += "\n" + "\n".join(hint_lines)
        self.exit(2, full + "\n")


def _setup_parser() -> argparse.ArgumentParser:
    """Define and return the CLI argument parser."""
    parser = HintingArgumentParser(prog=PROGRAM_SCRIPT)

    # --- Positional shorthand arguments ---
    parser.add_argument(
        "positional_include",
        nargs="*",
        metavar="INCLUDE",
        help="Positional include paths or patterns (shorthand for --include).",
    )
    parser.add_argument(
        "positional_out",
        nargs="?",
        metavar="OUT",
        help=(
            "Positional output file or directory (shorthand for --out). "
            "Use trailing slash for directories (e.g., 'dist/'), "
            "otherwise treated as file."
        ),
    )

    # --- Standard flags ---
    parser.add_argument(
        "--include",
        nargs="+",
        help="Override include patterns. Format: path or path:dest",
    )
    parser.add_argument("--exclude", nargs="+", help="Override exclude patterns.")
    parser.add_argument(
        "-o",
        "--out",
        help=(
            "Override output file or directory. "
            "Use trailing slash for directories (e.g., 'dist/'), "
            "otherwise treated as file. "
            "Examples: 'dist/serger.py' (file) or 'bin/' (directory)."
        ),
    )
    parser.add_argument("-c", "--config", help="Path to build config file.")

    parser.add_argument(
        "--add-include",
        nargs="+",
        help=(
            "Additional include paths (relative to cwd). "
            "Format: path or path:dest. Extends config includes."
        ),
    )
    parser.add_argument(
        "--add-exclude",
        nargs="+",
        help="Additional exclude patterns (relative to cwd). Extends config excludes.",
    )

    parser.add_argument(
        "--watch",
        nargs="?",
        type=float,
        metavar="SECONDS",
        default=None,
        help=(
            "Rebuild automatically on changes. "
            "Optionally specify interval in seconds"
            f" (default config or: {DEFAULT_WATCH_INTERVAL}). "
        ),
    )

    # --- Gitignore behavior ---
    gitignore = parser.add_mutually_exclusive_group()
    gitignore.add_argument(
        "--gitignore",
        dest="respect_gitignore",
        action="store_true",
        help="Respect .gitignore when selecting files (default).",
    )
    gitignore.add_argument(
        "--no-gitignore",
        dest="respect_gitignore",
        action="store_false",
        help="Ignore .gitignore and include all files.",
    )
    gitignore.set_defaults(respect_gitignore=None)

    # --- Color ---
    color = parser.add_mutually_exclusive_group()
    color.add_argument(
        "--no-color",
        dest="use_color",
        action="store_const",
        const=False,
        help="Disable ANSI color output.",
    )
    color.add_argument(
        "--color",
        dest="use_color",
        action="store_const",
        const=True,
        help="Force-enable ANSI color output (overrides auto-detect).",
    )
    color.set_defaults(use_color=None)

    # --- Version and verbosity ---
    parser.add_argument("--version", action="store_true", help="Show version info.")

    log_level = parser.add_mutually_exclusive_group()
    log_level.add_argument(
        "-q",
        "--quiet",
        action="store_const",
        const="warning",
        dest="log_level",
        help="Suppress non-critical output (same as --log-level warning).",
    )
    log_level.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const="debug",
        dest="log_level",
        help="Verbose output (same as --log-level debug).",
    )
    log_level.add_argument(
        "--log-level",
        choices=LEVEL_ORDER,
        default=None,
        dest="log_level",
        help="Set log verbosity level.",
    )
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="Run a built-in sanity test to verify tool correctness.",
    )

    # --- Build execution mode ---
    build_mode = parser.add_mutually_exclusive_group()
    build_mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate build actions without copying or deleting files.",
    )
    build_mode.add_argument(
        "--validate-config",
        action="store_true",
        help=(
            "Validate configuration file and resolved settings without "
            "executing a build. Validates config syntax, file collection, "
            "and path resolution (includes CLI arguments and environment variables)."
        ),
    )
    parser.add_argument(
        "--disable-build-timestamp",
        action="store_true",
        help="Disable build timestamps for deterministic builds (uses placeholder).",
    )
    return parser


def _normalize_positional_args(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
) -> None:
    """Normalize positional arguments into explicit include/out flags."""
    logger = getAppLogger()
    includes: list[str] = getattr(args, "positional_include", [])
    out_pos: str | None = getattr(args, "positional_out", None)

    # If no --out, assume last positional is output if we have ≥2 positionals
    if not getattr(args, "out", None) and len(includes) >= 2 and not out_pos:  # noqa: PLR2004
        out_pos = includes.pop()

    # If --out provided, treat all positionals as includes
    elif getattr(args, "out", None) and out_pos:
        logger.trace(
            "Interpreting all positionals as includes since --out was provided.",
        )
        includes.append(out_pos)
        out_pos = None

    # Conflict: can't mix --include and positional includes
    if getattr(args, "include", None) and (includes or out_pos):
        parser.error(
            "Cannot mix positional include arguments with --include; "
            "use --out for destination or --add-include to extend."
        )

    # Internal sanity check
    assert not (getattr(args, "out", None) and out_pos), (  # only for dev # noqa: S101
        "out_pos not cleared after normalization"
    )

    # Assign normalized values
    if includes:
        args.include = includes
    if out_pos:
        args.out = out_pos


# --------------------------------------------------------------------------- #
# Main entry helpers
# --------------------------------------------------------------------------- #


@dataclass
class _LoadedConfig:
    """Container for loaded and resolved configuration data."""

    config_path: Path | None
    root_cfg: RootConfig
    resolved: RootConfigResolved
    config_dir: Path
    cwd: Path


def _initialize_logger(args: argparse.Namespace) -> None:
    """Initialize logger with CLI args, env vars, and defaults."""
    logger = getAppLogger()
    log_level = logger.determineLogLevel(args=args)
    logger.setLevel(log_level)
    logger.enable_color = getattr(args, "enable_color", logger.determineColorEnabled())
    logger.trace("[BOOT] log-level initialized: %s", logger.levelName)

    logger.debug(
        "Runtime: Python %s (%s)\n    %s",
        platform.python_version(),
        platform.python_implementation(),
        sys.version.replace("\n", " "),
    )


def _validate_includes(
    root_cfg: RootConfig,
    resolved: RootConfigResolved,
    args: argparse.Namespace,
) -> bool:
    """
    Validate that the build has include patterns.

    Returns True if validation passes, False if we should abort.
    Logs appropriate warnings/errors.
    """
    logger = getAppLogger()

    # The presence of "include" key (even if empty) signals intentional choice:
    #   {"include": []}                    → include:[] in config → no check
    #
    # Missing "include" key likely means forgotten:
    #   {} or ""                           → no include key → check
    #   {"log_level": "debug"}             → no include key → check
    has_explicit_include_key = "include" in root_cfg

    # Check if CLI provides includes
    has_cli_includes = bool(
        getattr(args, "add_include", None) or getattr(args, "include", None)
    )

    # Check if config has no includes
    config_missing_includes = not resolved.get("include")

    if (
        not has_explicit_include_key
        and not has_cli_includes
        and config_missing_includes
    ):
        # Determine if we should error or warn based on strict_config
        any_strict = resolved.get("strict_config", True)

        if any_strict:
            # Error: config has no includes and strict_config=true
            logger.error(
                "No include patterns found "
                "(strict_config=true prevents continuing).\n"
                "   Use 'include' in your config or pass "
                "--include / --add-include.",
            )
            return False

        # Warning: config has no includes but strict_config=false
        logger.warning(
            "No include patterns found.\n"
            "   Use 'include' in your config or pass "
            "--include / --add-include.",
        )

    return True


def _validate_package(  # noqa: PLR0912
    root_cfg: RootConfig,
    resolved: RootConfigResolved,
    _args: argparse.Namespace,
) -> bool:
    """
    Primary validation: Check that the build has a package name (required for
    stitch builds).

    This is the detailed validation that provides helpful error messages with
    context:
    - Lists available modules/packages found in source_bases
    - Explains why auto-detection failed (multiple modules, no modules, etc.)
    - Suggests solutions based on the specific situation
    - Respects strict_config to determine error vs warning

    This runs early in the CLI flow (after config resolution) to fail fast with
    actionable guidance. A defensive check in run_build() serves as a safety net
    for direct calls or edge cases.

    Note: Package is only required for stitch builds (which need includes).
    If there are no includes, package validation is skipped.

    Returns True if validation passes, False if we should abort.
    Logs appropriate warnings/errors.
    """
    logger = getAppLogger()

    # Package is only required for stitch builds (which need includes)
    # If there are no includes (config or CLI), skip package validation
    # Note: CLI includes are merged during resolve_config, so resolved.get("include")
    # should already include them. We check both resolved and args to be safe.
    config_includes = resolved.get("include", [])
    has_includes = len(config_includes) > 0
    has_cli_includes = bool(
        getattr(_args, "include", None) or getattr(_args, "add_include", None)
    )
    # If no includes at all, package is not required
    if not has_includes and not has_cli_includes:
        # No includes means no stitch build, so package is not required
        return True
    # If CLI provides includes, skip validation (package will be inferred from
    # CLI includes during resolution). This handles the case where CLI includes
    # are provided but package hasn't been resolved yet.
    if has_cli_includes:
        return True

    # The presence of "package" key (even if None) signals intentional choice:
    #   {"package": None}                  → package:null in config → no check
    #
    # Missing "package" key likely means forgotten or couldn't be auto-detected:
    #   {}                                 → no package key → check
    #   {"log_level": "debug"}             → no package key → check
    has_explicit_package_key = "package" in root_cfg

    # Check if package is missing in resolved config
    package = resolved.get("package")
    config_missing_package = not package

    if not has_explicit_package_key and config_missing_package:
        # Collect context for better error messages
        source_bases = resolved.get("source_bases", [])
        config_dir: Path | None = None
        meta = resolved.get("__meta__")
        if meta and isinstance(meta, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
            config_dir_raw = meta.get("config_root")
            if isinstance(config_dir_raw, Path):  # pyright: ignore[reportUnnecessaryIsInstance]
                config_dir = config_dir_raw

        # Get all modules found in source_bases for helpful error messages
        all_modules: list[str] = []
        if source_bases and config_dir:
            all_modules = _get_first_level_modules_from_bases(source_bases, config_dir)
            # Remove duplicates while preserving order
            seen: set[str] = set()
            unique_modules: list[str] = []
            for mod in all_modules:
                if mod not in seen:
                    seen.add(mod)
                    unique_modules.append(mod)
            all_modules = unique_modules

        # Build helpful error message based on what was found
        if not source_bases:
            msg = (
                "No package name found.\n"
                "   Use 'package' in your config, or set 'source_bases' to enable "
                "auto-detection."
            )
        elif len(all_modules) == 0:
            msg = (
                "No package name found. No modules found in source_bases: "
                f"{source_bases}.\n"
                "   Use 'package' in your config, or ensure source_bases contain "
                "Python modules/packages."
            )
        elif len(all_modules) == 1:
            # This shouldn't happen (should have been auto-detected), but provide
            # helpful message
            msg = (
                f"No package name found. Found single module '{all_modules[0]}' "
                f"in source_bases: {source_bases}.\n"
                "   This should have been auto-detected. Please specify 'package' "
                "explicitly or report this as a bug."
            )
        else:
            # Multiple modules found - explain why auto-detection failed
            modules_str = ", ".join(f"'{m}'" for m in all_modules)
            msg = (
                f"No package name found. Found multiple modules in source_bases "
                f"{source_bases}: {modules_str}.\n"
                "   Please specify 'package' explicitly in your config to "
                "indicate which module to use."
            )

        # Determine if we should error or warn based on strict_config
        any_strict = resolved.get("strict_config", True)

        if any_strict:
            # Error: config has no package and strict_config=true
            logger.error(msg)
            return False

        # Warning: config has no package but strict_config=false
        logger.warning(msg)

    return True


def _handle_early_exits(args: argparse.Namespace) -> int | None:
    """
    Handle early exit conditions (version, selftest, Python version check).

    Returns exit code if we should exit early, None otherwise.
    """
    logger = getAppLogger()

    # --- Version flag ---
    if getattr(args, "version", None):
        meta = get_metadata()
        standalone = " [standalone]" if globals().get("__STANDALONE__", False) else ""
        logger.info(
            "%s %s (%s)%s", PROGRAM_DISPLAY, meta.version, meta.commit, standalone
        )
        return 0

    # --- Python version check ---
    if get_sys_version_info() < (3, 10):
        logger.error("%s requires Python 3.10 or newer.", PROGRAM_DISPLAY)
        return 1

    # --- Self-test mode ---
    if getattr(args, "selftest", None):
        return 0 if run_selftest() else 1

    return None


def _load_and_resolve_config(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
) -> _LoadedConfig:
    """Load config, normalize args, and resolve final configuration."""
    logger = getAppLogger()

    # --- Load configuration ---
    config_path: Path | None = None
    root_cfg: RootConfig | None = None
    config_result = load_and_validate_config(args)
    if config_result is not None:
        config_path, root_cfg, _validation_summary = config_result

    logger.trace("[CONFIG] log-level re-resolved from config: %s", logger.levelName)

    # --- Normalize shorthand arguments ---
    _normalize_positional_args(args, parser)
    cwd = Path.cwd().resolve()
    config_dir = config_path.parent if config_path else cwd

    # --- CLI-only mode fallback ---
    # Remove early bailout check - let downstream logic (auto-include, file
    # collection) handle validation. This allows pyproject.toml-based configless
    # builds to proceed and fail with more appropriate error messages if needed.
    if root_cfg is None:
        logger.info("No config file found — using CLI-only mode.")
        root_cfg = cast_hint(RootConfig, {})

    # --- Resolve config with args and defaults ---
    resolved = resolve_config(root_cfg, args, config_dir, cwd)

    return _LoadedConfig(
        config_path=config_path,
        root_cfg=root_cfg,
        resolved=resolved,
        config_dir=config_dir,
        cwd=cwd,
    )


def _execute_build(
    resolved: RootConfigResolved,
    args: argparse.Namespace,
    argv: list[str] | None,
) -> None:
    """Execute build either in watch mode or one-time mode."""
    watch_enabled = getattr(args, "watch", None) is not None or (
        "--watch" in (argv or [])
    )

    resolved["dry_run"] = getattr(args, "dry_run", DEFAULT_DRY_RUN)
    resolved["validate_config"] = getattr(args, "validate_config", False)

    if watch_enabled:
        watch_interval = resolved["watch_interval"]
        watch_for_changes(
            lambda: run_build(resolved),
            resolved,
            interval=watch_interval,
        )
    else:
        run_build(resolved)


# --------------------------------------------------------------------------- #
# Main entry
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:  # noqa: PLR0911, PLR0912
    logger = getAppLogger()  # init (use env + defaults)

    try:
        parser = _setup_parser()
        args = parser.parse_args(argv)

        # --- Early runtime init (use CLI + env + defaults) ---
        _initialize_logger(args)

        # --- Handle early exits (version, selftest, etc.) ---
        early_exit_code = _handle_early_exits(args)
        if early_exit_code is not None:
            return early_exit_code

        # --- Load and resolve configuration ---
        config = _load_and_resolve_config(args, parser)

        # --- Validate includes ---
        if not _validate_includes(config.root_cfg, config.resolved, args):
            return 1

        # --- Validate package ---
        if not _validate_package(config.root_cfg, config.resolved, args):
            return 1

        # --- Validate-config notice ---
        if getattr(args, "validate_config", None):
            logger.info("🔍 Validating configuration...")

        # --- Dry-run notice ---
        if getattr(args, "dry_run", None):
            logger.info("🧪 Dry-run mode: no files will be written or deleted.\n")

        # --- Config summary ---
        if config.config_path:
            logger.detail("🔧 Using config: %s", config.config_path.name)
        else:
            logger.detail("🔧 Running in CLI-only mode (no config file).")
        logger.detail("📁 Config root: %s", config.config_dir)
        logger.detail("📂 Invoked from: %s", config.cwd)

        # --- Execute build ---
        _execute_build(config.resolved, args, argv)

    except (FileNotFoundError, ValueError, TypeError, RuntimeError) as e:
        # controlled termination
        silent = getattr(e, "silent", False)
        if not silent:
            try:
                logger.errorIfNotDebug(str(e))
            except Exception:  # noqa: BLE001
                safeLog(f"[FATAL] Logging failed while reporting: {e}")
        return getattr(e, "code", 1)

    except Exception as e:  # noqa: BLE001
        # unexpected internal error
        try:
            logger.criticalIfNotDebug("Unexpected internal error: %s", e)
        except Exception:  # noqa: BLE001
            safeLog(f"[FATAL] Logging failed while reporting: {e}")

        return getattr(e, "code", 1)

    else:
        return 0


# === serger.__init__ ===
# src/serger/__init__.py

"""Serger — Stitch your module into a single file.

Full developer API
==================
This package re-exports all non-private symbols from its submodules,
making it suitable for programmatic use, custom integrations, or plugins.
Anything prefixed with "_" is considered internal and may change.

Highlights:
    - main()              → CLI entrypoint
    - run_build()         → Execute a build configuration
    - resolve_config()    → Merge CLI args with config files
    - get_metadata()      → Retrieve version / commit info
"""


__all__ = [  # noqa: RUF022
    # actions
    "get_metadata",
    "watch_for_changes",
    # build
    "run_build",
    # cli
    "main",
    # config
    "find_config",
    "IncludeResolved",
    "load_and_validate_config",
    "load_config",
    "MetaBuildConfigResolved",
    "OriginType",
    "parse_config",
    "PathResolved",
    "resolve_build_config",
    "resolve_config",
    "RootConfig",
    "RootConfigResolved",
    "validate_config",
    # constants
    "DEFAULT_ENV_DISABLE_BUILD_TIMESTAMP",
    "DEFAULT_ENV_LOG_LEVEL",
    "DEFAULT_ENV_RESPECT_GITIGNORE",
    "DEFAULT_ENV_WATCH_INTERVAL",
    "DEFAULT_LOG_LEVEL",
    "DEFAULT_OUT_DIR",
    "DEFAULT_RESPECT_GITIGNORE",
    "DEFAULT_STRICT_CONFIG",
    "DEFAULT_WATCH_INTERVAL",
    # logs
    "getAppLogger",
    # meta
    "Metadata",
    "PROGRAM_CONFIG",
    "PROGRAM_DISPLAY",
    "PROGRAM_ENV",
    "PROGRAM_PACKAGE",
    "PROGRAM_SCRIPT",
    # selftest
    "run_selftest",
    # utils
    "is_excluded",
    "make_includeresolved",
    "make_pathresolved",
]


# --- import shims for single-file runtime ---
def _create_pkg_module(pkg_name: str) -> types.ModuleType:
    """Create or get a package module and set up parent relationships."""
    _mod = sys.modules.get(pkg_name)
    if not _mod:
        _mod = types.ModuleType(pkg_name)
        _mod.__package__ = pkg_name
        sys.modules[pkg_name] = _mod
    # Set up parent-child relationships for nested packages
    if "." in pkg_name:
        _parent_pkg = ".".join(pkg_name.split(".")[:-1])
        _child_name = pkg_name.split(".")[-1]
        _parent = sys.modules.get(_parent_pkg)
        if _parent:
            setattr(_parent, _child_name, _mod)
    return _mod


def _setup_pkg_modules(  # noqa: C901, PLR0912
    pkg_name: str, module_names: list[str], name_mapping: dict[str, str] | None = None
) -> None:
    """Set up package module attributes and register submodules."""
    _mod = sys.modules.get(pkg_name)
    if not _mod:
        return
    # Copy attributes from all modules under this package
    _globals = globals()
    # Debug: log what's in globals for this package
    # Note: This copies all globals to the package module
    for _key, _value in _globals.items():
        setattr(_mod, _key, _value)
    # Set up package attributes for nested packages BEFORE registering
    # modules (so packages are available when modules are registered)
    _seen_packages: set[str] = set()
    for _name in module_names:
        if _name != pkg_name and _name.startswith(pkg_name + "."):
            # Extract parent package (e.g., mypkg.public from
            # mypkg.public.utils)
            _name_parts = _name.split(".")
            if len(_name_parts) > 2:  # noqa: PLR2004
                # Has at least one intermediate package
                _parent_pkg = ".".join(_name_parts[:-1])
                if (
                    _parent_pkg.startswith(pkg_name + ".")
                    and _parent_pkg not in _seen_packages
                ):
                    _seen_packages.add(_parent_pkg)
                    _pkg_obj = sys.modules.get(_parent_pkg)
                    if _pkg_obj and _pkg_obj != _mod:
                        # Set parent package as attribute
                        _pkg_attr_name = _name_parts[1]
                        if not hasattr(_mod, _pkg_attr_name):
                            setattr(_mod, _pkg_attr_name, _pkg_obj)
    # Register all modules under this package
    for _name in module_names:
        # Try to find module by transformed name first
        _module_obj = sys.modules.get(_name)
        if not _module_obj and name_mapping:
            # If not found, try to find by original name
            _original_name = name_mapping.get(_name)
            if _original_name:
                _module_obj = sys.modules.get(_original_name)
                if not _module_obj:
                    # Also check globals() for module object
                    # Module objects might be in globals()
                    # with their original names
                    _last_part = _original_name.split(".")[-1]
                    _module_obj = _globals.get(_last_part)
                if _module_obj:
                    # Register with transformed name
                    sys.modules[_name] = _module_obj
        # If still not found, use package module
        if not _module_obj:
            sys.modules[_name] = _mod
    # Set submodules as attributes on parent package
    for _name in module_names:
        if _name != pkg_name and _name.startswith(pkg_name + "."):
            _submodule_name = _name.split(".")[-1]
            # Try to get actual module object
            _module_obj = sys.modules.get(_name)
            if not _module_obj and name_mapping:
                _original_name = name_mapping.get(_name)
                if _original_name:
                    _module_obj = sys.modules.get(_original_name)
                    if not _module_obj:
                        # Also check globals()
                        _last_part = _original_name.split(".")[-1]
                        _module_obj = _globals.get(_last_part)
            # Use actual module object if found, otherwise package
            _target = _module_obj if _module_obj else _mod
            if not hasattr(_mod, _submodule_name) or isinstance(
                getattr(_mod, _submodule_name, None), types.ModuleType
            ):
                setattr(_mod, _submodule_name, _target)


_create_pkg_module("apathetic_logging")
_create_pkg_module("apathetic_schema")
_create_pkg_module("apathetic_utils")
_create_pkg_module("serger")
_create_pkg_module("serger.config")
_create_pkg_module("serger.utils")

_setup_pkg_modules(
    "apathetic_logging",
    [
        "apathetic_logging.__init__",
        "apathetic_logging.constants",
        "apathetic_logging.dual_stream_handler",
        "apathetic_logging.get_logger",
        "apathetic_logging.logger",
        "apathetic_logging.logger_namespace",
        "apathetic_logging.logging_std_camel",
        "apathetic_logging.logging_utils",
        "apathetic_logging.namespace",
        "apathetic_logging.registry",
        "apathetic_logging.registry_data",
        "apathetic_logging.safe_logging",
        "apathetic_logging.tag_formatter",
    ],
    None,
)
_setup_pkg_modules(
    "apathetic_schema", ["apathetic_schema.__init__", "apathetic_schema.schema"], None
)
_setup_pkg_modules(
    "apathetic_utils",
    [
        "apathetic_utils.__init__",
        "apathetic_utils.ci",
        "apathetic_utils.files",
        "apathetic_utils.matching",
        "apathetic_utils.paths",
        "apathetic_utils.system",
        "apathetic_utils.text",
        "apathetic_utils.types",
    ],
    None,
)
_setup_pkg_modules(
    "serger",
    [
        "serger.__init__",
        "serger.actions",
        "serger.build",
        "serger.cli",
        "serger.constants",
        "serger.logs",
        "serger.main_config",
        "serger.meta",
        "serger.module_actions",
        "serger.selftest",
        "serger.stitch",
        "serger.verify_script",
    ],
    None,
)
_setup_pkg_modules(
    "serger.config",
    [
        "serger.config.__init__",
        "serger.config.config_loader",
        "serger.config.config_resolve",
        "serger.config.config_types",
        "serger.config.config_validate",
    ],
    None,
)
_setup_pkg_modules(
    "serger.utils",
    [
        "serger.utils.__init__",
        "serger.utils.utils_installed_packages",
        "serger.utils.utils_matching",
        "serger.utils.utils_modules",
        "serger.utils.utils_paths",
        "serger.utils.utils_types",
        "serger.utils.utils_validation",
    ],
    None,
)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
