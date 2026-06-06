import logging


def init_logger(
    service_name: str,
    log_level: int = logging.INFO,
    log_fmt: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    third_party_logger_names: list[str] | None = None,
) -> None:
    if third_party_logger_names is None:
        third_party_logger_names = []

    # setup stream handler
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    formatter = logging.Formatter(log_fmt)
    handler.setFormatter(formatter)

    # configure loggers
    root_logger = logging.getLogger(service_name)
    third_party_loggers = [
        logging.getLogger(third_party_logger_name) for third_party_logger_name in third_party_logger_names
    ]
    for logger in [root_logger, *third_party_loggers]:
        if handler not in logger.handlers:
            logger.handlers.clear()
        if not logger.hasHandlers():
            logger.setLevel(log_level)
            logger.addHandler(handler)
