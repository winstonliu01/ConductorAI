import logging
from typing import Optional


def setup_logging(log_level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """
    Configures the global logging settings for the application.

    Args:
        log_level (int): Logging severity level (e.g., logging.DEBUG, logging.INFO).
        log_file (Optional[str]): Optional file path to write logs to. If None,
                                  logs are only printed to the console.

    Returns:
        None
    """
    handlers: list[logging.Handler] = [logging.StreamHandler()]

    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers,
        force=True
    )
