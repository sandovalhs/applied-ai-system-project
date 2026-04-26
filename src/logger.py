"""
logger.py — Logging & Observability

Writes a structured log entry at every pipeline stage boundary so
developers can trace exactly what happened for any given query.

All entries go to both stdout (INFO+) and logs/rag_pipeline.log (DEBUG+).
The log file is created automatically when the first message is written.
"""

import logging
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_LOG_FILE = Path("logs") / "rag_pipeline.log"
_FMT_CONSOLE = logging.Formatter("%(asctime)s [%(levelname)-8s] %(message)s", "%H:%M:%S")
_FMT_FILE = logging.Formatter("%(asctime)s [%(levelname)-8s] %(name)s — %(message)s")


def get_logger(name: str = "rag_pipeline") -> logging.Logger:
    """
    Return a configured Logger, creating it only once per name.

    Two handlers are attached on first call:
    - StreamHandler  → INFO+ to stdout
    - FileHandler    → DEBUG+ to logs/rag_pipeline.log

    Subsequent calls with the same name return the cached instance
    without adding duplicate handlers.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(_FMT_CONSOLE)

    _LOG_FILE.parent.mkdir(exist_ok=True)
    file_h = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    file_h.setLevel(logging.DEBUG)
    file_h.setFormatter(_FMT_FILE)

    logger.addHandler(console)
    logger.addHandler(file_h)
    return logger


def log_query(logger: logging.Logger, user_query: str) -> None:
    """Log the raw user query — first entry for every pipeline run."""
    logger.info("─" * 60)
    logger.info("NEW QUERY: %s", user_query)


def log_prefs(logger: logging.Logger, prefs: dict) -> None:
    """Log each key-value pair from the validated prefs dict."""
    logger.info("EXTRACTED PREFS:")
    for key, value in prefs.items():
        logger.info("  %-22s %s", f"{key}:", value)


def log_candidates(
    logger: logging.Logger,
    candidates: List[Tuple[Dict, float, str]],
) -> None:
    """Log the title, artist, and score of every retrieved candidate."""
    logger.info("RETRIEVED %d CANDIDATES:", len(candidates))
    for song, score, _ in candidates:
        logger.info("  [%.2f] %s — %s", score, song["title"], song["artist"])


def log_response(logger: logging.Logger, raw_response: str) -> None:
    """Log Claude's full raw generation response at DEBUG level (file only)."""
    logger.debug("CLAUDE RAW RESPONSE:\n%s", raw_response)


def log_error(
    logger: logging.Logger,
    error: Exception,
    context: str,
    query: Optional[str] = None,
) -> None:
    """
    Log an exception with the pipeline stage, message, and optional query.
    The full traceback is written at DEBUG level to the log file.
    Does not re-raise — callers decide how to surface the failure.
    """
    logger.error("ERROR in %s: %s — %s", context, type(error).__name__, error)
    if query:
        logger.error("  query was: %r", query)
    logger.debug(traceback.format_exc())
