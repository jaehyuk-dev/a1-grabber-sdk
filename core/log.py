import logging
import os
from datetime import datetime, timedelta, timezone

from core import config

KST = timezone(timedelta(hours=9))


def setup_logger():
    """날짜별 로그 파일로 로깅 설정"""
    os.makedirs(config.LOG_DIR, exist_ok=True)

    today = datetime.now(KST).strftime("%Y-%m-%d")
    log_file = os.path.join(config.LOG_DIR, f"{today}.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger("oci-a1-provisioner")


logger = setup_logger()
