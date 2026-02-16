import os

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# .env 파일 로드
def _load_env(path=".env"):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


_load_env(os.path.join(_BASE_DIR, ".env"))


# === OCI 인증 (.env에서 주입) ===
USER_OCID = os.environ["OCI_USER_OCID"]
FINGERPRINT = os.environ["OCI_FINGERPRINT"]
TENANCY_OCID = os.environ["OCI_TENANCY_OCID"]
REGION = os.environ["OCI_REGION"]
KEY_FILE = os.environ["OCI_KEY_FILE"]
SSH_PUBLIC_KEY = os.environ["SSH_PUBLIC_KEY"]
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")

# === A1 인스턴스 설정 (.env에서 주입) ===
COMPARTMENT_OCID = TENANCY_OCID
DISPLAY_NAME = os.environ["A1_DISPLAY_NAME"]
SHAPE = os.environ["A1_SHAPE"]
OCPUS = int(os.environ["A1_OCPUS"])
MEMORY_IN_GBS = int(os.environ["A1_MEMORY_IN_GBS"])
BOOT_VOLUME_SIZE_IN_GBS = int(os.environ["A1_BOOT_VOLUME_SIZE_IN_GBS"])
SUBNET_DISPLAY_NAME = os.environ["A1_SUBNET_DISPLAY_NAME"]
IMAGE_OS = os.environ["A1_IMAGE_OS"]
IMAGE_OS_VERSION = os.environ["A1_IMAGE_OS_VERSION"]

# === Micro 인스턴스 설정 (.env에서 주입) ===
MICRO_DISPLAY_NAME = os.environ["MICRO_DISPLAY_NAME"]
MICRO_SHAPE = os.environ["MICRO_SHAPE"]

# === 로그 & 통계 ===
LOG_DIR = os.path.join(_BASE_DIR, "logs")
STATS_FILE = os.path.join(_BASE_DIR, "stats.json")
