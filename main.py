import sys

import oci

from core.log import logger
from provisioner.a1 import create_a1_instance
from stats import check_first_run, record_attempt, send_daily_report

if __name__ == "__main__":
    check_first_run()
    send_daily_report()
    try:
        create_a1_instance()
        record_attempt("success")
    except oci.exceptions.ServiceError as e:
        if "Out of host capacity" in str(e) or e.code == "InternalError":
            logger.info(f"A1 용량 부족 — 다음에 재시도 ({e.message})")
            record_attempt("capacity_shortage")
        elif "LimitExceeded" in str(e):
            logger.warning(f"리소스 한도 초과: {e.message}")
            record_attempt("limit_exceeded")
        else:
            logger.error(f"OCI 에러: {e.message}")
            record_attempt("error")
            sys.exit(1)
    except Exception as e:
        logger.error(f"예외 발생: {e}")
        record_attempt("error")
        sys.exit(1)
