import logging
import json
from pathlib import Path
from jarvis.config import CFG

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "ts": self.formatTime(record),
            "level": record.levelname,
            "msg": record.getMessage(),
            "module": record.module,
        })

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(CFG["logging"]["level"])
    log_path = Path(CFG["logging"]["log_file"])
    fh = logging.FileHandler(log_path)
    fh.setFormatter(JSONFormatter())
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
