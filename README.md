# OCI A1 Provisioner

OCI Always Free 인스턴스(A1 Flex / Micro)를 자동으로 확보하는 스크립트.

용량 부족 시 크론으로 반복 실행하여 빈자리가 나면 자동 생성합니다.

## 기능

- A1 Flex / Micro 인스턴스 자동 생성
- 용량 부족(`Out of host capacity`) 시 자동 재시도
- 이미 실행 중인 인스턴스가 있으면 스킵
- Slack 웹훅 알림 (가동 시작, 확보 성공, 일일 리포트)
- 날짜별 로그 파일 자동 생성 (`logs/YYYY-MM-DD.log`)
- 시도 통계 기록 (`stats.json`)

## 사전 준비

- Python 3.8+
- OCI 계정 (Always Free 티어)
- OCI API 키: OCI 콘솔 > 프로필 > API 키 > API 키 추가에서 생성

## 설정

```bash
cp .env.example .env
# .env 파일에 OCI 인증 정보 및 인스턴스 설정 입력
```

### OCI 인증 (필수)

| 변수 | 설명 |
|---|---|
| `OCI_USER_OCID` | OCI 사용자 OCID |
| `OCI_FINGERPRINT` | API 키 지문 |
| `OCI_TENANCY_OCID` | 테넌시 OCID |
| `OCI_REGION` | 리전 (예: `ap-chuncheon-1`) |
| `OCI_KEY_FILE` | API 프라이빗 키 경로 |
| `SSH_PUBLIC_KEY` | 인스턴스에 등록할 SSH 퍼블릭 키 |

### A1 Flex 인스턴스 설정 (필수)

| 변수 | 설명 | 예시 |
|---|---|---|
| `A1_DISPLAY_NAME` | 인스턴스 이름 | `a1-main` |
| `A1_SHAPE` | Shape | `VM.Standard.A1.Flex` |
| `A1_OCPUS` | OCPU 수 (최대 4) | `4` |
| `A1_MEMORY_IN_GBS` | 메모리 GB (최대 24) | `24` |
| `A1_BOOT_VOLUME_SIZE_IN_GBS` | 부트 볼륨 GB | `100` |
| `A1_SUBNET_DISPLAY_NAME` | 서브넷 이름 | `퍼블릭 서브넷-main-vcn` |
| `A1_IMAGE_OS` | OS | `Oracle Linux` |
| `A1_IMAGE_OS_VERSION` | OS 버전 | `9` |

### Micro 인스턴스 설정 (필수)

| 변수 | 설명 | 예시 |
|---|---|---|
| `MICRO_DISPLAY_NAME` | 인스턴스 이름 | `micro-main` |
| `MICRO_SHAPE` | Shape | `VM.Standard.E2.1.Micro` |

### 선택

| 변수 | 설명 |
|---|---|
| `SLACK_WEBHOOK_URL` | Slack 알림 웹훅 URL (미설정 시 알림 비활성) |

## 실행

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python main.py
```

## 크론 설정 (5분마다)

```bash
crontab -e
```

```
*/5 * * * * cd /path/to/oci-a1-provisioner && .venv/bin/python main.py
```

## Slack 알림

`SLACK_WEBHOOK_URL`을 설정하면 다음 알림이 발송됩니다:

- **가동 시작** — 최초 실행 시 리전, Shape, 스펙 정보
- **인스턴스 확보 성공** — 생성된 인스턴스 ID, 리전
- **일일 리포트** — 매일 07시(KST) 지난 24시간 시도 통계

## 구조

```
├── main.py                  # 엔트리포인트
├── stats.py                 # 시도 기록 + 일일 리포트
├── requirements.txt
├── .env.example
├── .gitignore
├── core/
│   ├── __init__.py
│   ├── config.py            # .env 로드 + 설정
│   ├── log.py               # 날짜별 로그 (logs/YYYY-MM-DD.log)
│   └── notify.py            # Slack 웹훅 알림
├── provisioner/
│   ├── __init__.py
│   ├── a1.py                # A1 Flex 인스턴스 생성
│   └── micro.py             # Micro 인스턴스 생성
```
