"""
utils.py
========
Shared utility functions used across the Intelligent Customer Support Chatbot
project: logging configuration, input validation, file validation helpers,
and small text-cleaning utilities.

Keeping these helpers in one module avoids code duplication and gives the
project a single, consistent place to control cross-cutting concerns such as
logging format and validation rules.
"""

import logging
import os
import re
import sys
from pathlib import Path
from typing import Optional


# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #
def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Create (or fetch) a configured logger instance.

    Using a factory function instead of configuring logging globally at
    import time prevents duplicate handlers being attached when Streamlit
    re-executes the script on every UI interaction.

    Args:
        name: Name of the logger, conventionally ``__name__`` of the caller.
        level: Logging level (default: ``logging.INFO``).

    Returns:
        A configured ``logging.Logger`` instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid attaching multiple handlers on Streamlit re-runs.
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

    return logger


logger = get_logger(__name__)


# --------------------------------------------------------------------------- #
# File validation
# --------------------------------------------------------------------------- #
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".docx"}
MAX_FILE_SIZE_MB = 25


class FileValidationError(Exception):
    """Raised when an uploaded file fails validation checks."""


def validate_file(filename: str, file_size_bytes: int) -> None:
    """
    Validate an uploaded file's extension and size before processing.

    Args:
        filename: Original filename, e.g. ``"policy.pdf"``.
        file_size_bytes: Size of the file in bytes.

    Raises:
        FileValidationError: If the extension is unsupported or the file
            is too large or empty.
    """
    if not filename or not filename.strip():
        raise FileValidationError("Filename is empty or invalid.")

    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise FileValidationError(
            f"Unsupported file type '{extension}'. "
            f"Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    if file_size_bytes <= 0:
        raise FileValidationError(f"File '{filename}' appears to be empty.")

    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size_bytes > max_bytes:
        raise FileValidationError(
            f"File '{filename}' exceeds the maximum allowed size of "
            f"{MAX_FILE_SIZE_MB} MB."
        )


def ensure_directory(path: str) -> None:
    """
    Ensure a directory exists, creating it (and parents) if necessary.

    Args:
        path: Directory path to create.
    """
    Path(path).mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------- #
# Text validation / cleaning
# --------------------------------------------------------------------------- #
def validate_user_query(query: str, max_length: int = 2000) -> str:
    """
    Validate and sanitize a raw user query string before it is sent through
    the RAG pipeline.

    Args:
        query: Raw text typed by the user.
        max_length: Maximum allowed character length.

    Returns:
        The trimmed, validated query string.

    Raises:
        ValueError: If the query is empty or exceeds ``max_length``.
    """
    if query is None:
        raise ValueError("Query cannot be None.")

    cleaned = query.strip()
    if not cleaned:
        raise ValueError("Query cannot be empty.")

    if len(cleaned) > max_length:
        raise ValueError(
            f"Query is too long ({len(cleaned)} characters). "
            f"Maximum allowed is {max_length} characters."
        )

    # Strip control characters that could interfere with downstream
    # processing or rendering, while preserving normal Unicode text
    # (including Tamil, Hindi and other scripts).
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", cleaned)
    return cleaned


def clean_text(text: str) -> str:
    """
    Normalize whitespace and remove non-printable artifacts from extracted
    document text.

    Args:
        text: Raw text extracted from a document.

    Returns:
        Cleaned text with normalized whitespace.
    """
    if not text:
        return ""

    # Collapse multiple blank lines / spaces, strip non-printable chars.
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def get_env_var(name: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Safely fetch an environment variable with optional default and
    required-presence enforcement.

    Args:
        name: Environment variable name.
        default: Value to return if the variable is not set.
        required: If True, raises ``EnvironmentError`` when missing.

    Returns:
        The environment variable's value, or the default.

    Raises:
        EnvironmentError: If ``required`` is True and the variable is unset.
    """
    value = os.environ.get(name, default)
    if required and not value:
        raise EnvironmentError(
            f"Required environment variable '{name}' is not set. "
            f"Please add it to your .env file."
        )
    return value


def truncate_text(text: str, max_chars: int = 300) -> str:
    """
    Truncate text to a maximum number of characters, appending an ellipsis
    if truncation occurred. Useful for displaying source previews in the UI.

    Args:
        text: Text to truncate.
        max_chars: Maximum number of characters to keep.

    Returns:
        Truncated text.
    """
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "..."
