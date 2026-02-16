import json
import os
from datetime import datetime, timedelta, timezone

from core import config
from core.notify import send_slack

KST = timezone(timedelta(hours=9))


def _load_stats():
    """stats.json 로드"""
    if not os.path.exists(config.STATS_FILE):
        return {"attempts": [], "last_report_date": None}
    with open(config.STATS_FILE) as f:
        return json.load(f)


def _save_stats(stats):
    """stats.json 저장"""
    with open(config.STATS_FILE, "w") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def record_attempt(result):
    """시도 결과를 stats.json에 기록"""
    if os.environ.get("CI"):
        return
    stats = _load_stats()
    stats["attempts"].append(
        {
            "ts": datetime.now(KST).isoformat(),
            "result": result,
        }
    )
    _save_stats(stats)


def check_first_run():
    """최초 실행 시 Slack 시작 알림"""
    if os.path.exists(config.STATS_FILE):
        return
    if os.environ.get("CI"):
        _save_stats({"attempts": [], "last_report_date": None})
        return
    send_slack(
        ":rocket: *A1 Grabber 가동 시작!*\n"
        f"• Region: `{config.REGION}`\n"
        f"• Shape: `{config.SHAPE}` ({config.OCPUS} OCPU / {config.MEMORY_IN_GBS}GB)"
    )
    _save_stats({"attempts": [], "last_report_date": None})


def send_daily_report():
    """매일 KST 07시에 지난 24시간 통계 리포트 발송"""
    if os.environ.get("CI"):
        return
    now = datetime.now(KST)
    if now.hour != 7:
        return

    stats = _load_stats()
    today = now.strftime("%Y-%m-%d")
    if stats.get("last_report_date") == today:
        return

    cutoff = (now - timedelta(hours=24)).isoformat()
    recent = [a for a in stats["attempts"] if a["ts"] >= cutoff]

    total = len(recent)
    counts = {}
    for a in recent:
        r = a["result"]
        counts[r] = counts.get(r, 0) + 1

    label = {
        "success": "성공",
        "capacity_shortage": "용량 부족",
        "limit_exceeded": "한도 초과",
        "error": "에러",
        "skipped": "이미 실행 중",
    }
    lines = [f":bar_chart: *일일 리포트* ({today})"]
    lines.append(f"• 총 시도: {total}회")
    for key, count in counts.items():
        lines.append(f"• {label.get(key, key)}: {count}회")

    send_slack("\n".join(lines))

    # 24시간 이전 기록 정리 + 날짜 갱신
    stats["attempts"] = [a for a in stats["attempts"] if a["ts"] >= cutoff]
    stats["last_report_date"] = today
    _save_stats(stats)
