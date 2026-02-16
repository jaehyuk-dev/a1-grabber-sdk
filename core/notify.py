import json
import urllib.request

from core import config
from core.log import logger


def send_slack(text):
    """Slack 웹훅으로 메시지 발송"""
    if not config.SLACK_WEBHOOK_URL:
        return

    payload = json.dumps({"text": text}).encode()
    req = urllib.request.Request(
        config.SLACK_WEBHOOK_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        logger.warning(f"Slack 알림 실패: {e}")
