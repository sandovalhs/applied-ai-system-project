"""
logger.py — Logging & Observability

Responsibility: Write a structured log entry at every stage boundary in
the pipeline so developers can trace exactly what happened for any
given query — what prefs were extracted, which songs were retrieved,
what Claude returned, and any errors along the way.

All log entries go to both the console (INFO level) and a log file
(logs/rag_pipeline.log) so they survive after the Streamlit session
ends. The log file is created automatically if it doesn't exist.
"""

import logging
from typing import List, Dict, Tuple, Optional


def get_logger(name: str = "rag_pipeline") -> logging.Logger:
    """
    Create and return a configured Logger instance.

    Sets up two handlers:
    - StreamHandler writing INFO+ messages to stdout (visible in
      terminal and Streamlit's server logs).
    - FileHandler writing DEBUG+ messages to logs/rag_pipeline.log
      (full trace including raw Claude responses).

    Calling this function multiple times with the same name returns the
    same logger without adding duplicate handlers.

    Parameters
    ----------
    name : str
        Logger name. Use the default for the main pipeline; pass a
        different name in tests to avoid polluting the real log file.

    Returns
    -------
    logging.Logger
    """
    ...


def log_query(logger: logging.Logger, user_query: str) -> None:
    """
    Log the raw user query at the start of a pipeline run.

    Records the query text and a timestamp. This is the first log entry
    for every request, making it easy to find the start of each run in
    the log file.

    Parameters
    ----------
    logger : logging.Logger
    user_query : str
        Raw natural language input from the user.
    """
    ...


def log_prefs(logger: logging.Logger, prefs: dict) -> None:
    """
    Log the structured prefs dict produced by the NL parser.

    Records each key-value pair so developers can see what Claude
    inferred from the user's query. If validate_prefs() changed any
    values, those corrections were logged inside validate_prefs() and
    this log shows the final, cleaned version.

    Parameters
    ----------
    logger : logging.Logger
    prefs : dict
        Validated prefs dict from validate_prefs().
    """
    ...


def log_candidates(
    logger: logging.Logger,
    candidates: List[Tuple[Dict, float, str]],
) -> None:
    """
    Log the top candidate songs returned by the retriever.

    Records each candidate's title, artist, and score. Useful for
    debugging cases where the final Claude picks don't match what you'd
    expect from the retrieval stage.

    Parameters
    ----------
    logger : logging.Logger
    candidates : list of (song_dict, score, reason_string) tuples
    """
    ...


def log_response(logger: logging.Logger, raw_response: str) -> None:
    """
    Log Claude's full raw text response from the generation stage.

    This is written at DEBUG level to the file only (not stdout) since
    it can be long. Invaluable for debugging parse_claude_response()
    failures when Claude deviates from the expected output format.

    Parameters
    ----------
    logger : logging.Logger
    raw_response : str
        Unmodified text from the Claude API response.
    """
    ...


def log_error(
    logger: logging.Logger,
    error: Exception,
    context: str,
    query: Optional[str] = None,
) -> None:
    """
    Log an exception with enough context to reproduce the failure.

    Records the exception type, message, traceback, the pipeline stage
    where it occurred (context), and optionally the original query.
    Errors are written at ERROR level so they stand out in the log file.

    This function does not re-raise — callers decide whether to surface
    the error to the user or degrade gracefully.

    Parameters
    ----------
    logger : logging.Logger
    error : Exception
        The caught exception.
    context : str
        A short label for where the error occurred, e.g. "parse_query"
        or "generate_recommendations".
    query : str, optional
        The original user query, if available, to aid reproduction.
    """
    ...
