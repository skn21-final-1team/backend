import logging
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class KSTFormatter(logging.Formatter):
    def formattime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=KST)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.strftime("%Y-%m-%d %H:%M:%S")


def setup_logging():
    formatter = KSTFormatter(LOG_FORMAT)

    logging.basicConfig(level=logging.INFO, force=True)
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.setFormatter(formatter)

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(name)
        for handler in logger.handlers:
            handler.setFormatter(formatter)
