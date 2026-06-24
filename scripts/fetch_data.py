"""
청약홈 API 데이터 수집 스크립트
매일 새벽 GitHub Actions에서 실행

확인된 엔드포인트 (2026-06-24 기준):
  - getAPTLttotPblancDetail    : 아파트 분양정보 (총 ~2800건)
  - getAPTLttotPblancMdl       : 타입별 분양가/세대수 (~14000건)
  - getRemndrLttotPblancDetail : 무순위/잔여세대 (~1600건)
  - getAPTLttotPblancCmpet     : 경쟁률 (~53000건)
  - getAPTSpsplyReqstStus      : 특별공급 신청현황 (~12000건)
  - getAptLttotPblancScore     : 당첨가점 (~28000건)
  - getAPTPrzwnerAreaStat      : 연령별/지역별 당첨자 통계
  - getAPTApsPrzwnerStat       : 지역별 당첨가점 통계

환경변수:
  - API_KEY : 공공데이터포털 서비스키
"""
import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_KEY   = os.environ.get("API_KEY", "")
BASE      = "https://api.odcloud.kr/api"
DATA_DIR  = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

DELAY     = 0.5   # 요청 간 딜레이 (초)
PER_PAGE  = 100   # 페이지당 건수


# ── 공통 ──────────────────────────────────────────

def fetch_all(endpoint: str, extra_params: dict | None = None) -> list:
    """전체 페이지 수집 — 실패 시 빈 리스트 반환"""
    url = f"{BASE}/{endpoint}"
    params = {"page": 1, "perPage": PER_PAGE, "serviceKey": API_KEY}
    if extra_params:
        params.update(extra_params)

    all_data: list = []
    while True:
        try:
            r = requests.get(url, params=params, timeout=15)
            r.raise_for_status()
            d = r.json()
        except Exception as e:
            print(f"  [오류] p{params['page']}: {e}")
            break

        items = d.get("data", [])
        all_data.extend(items)
        total = d.get("totalCount", 0)
        print(f"  p{params['page']}: {len(items)}건 수집 (누적 {len(all_data)}/{total})")

        if len(all_data) >= total or not items:
            break
        params["page"] += 1
        time.sleep(DELAY)

    return all_data


def save(filename: str, data: list):
    """기존 파일 보존 — 데이터 없으면 덮어쓰지 않음"""
    path = DATA_DIR / filename
    if not data:
        print(f"  [경고] 데이터 없음 — {filename} 유지")
        return
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  OK {filename}: {len(data)}건 저장")


# ── 수집 함수 ──────────────────────────────────────

def fetch_apt():
    print("\n[1] 아파트 분양정보")
    data = fetch_all("ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail")
    save("apt.json", data)
    return data


def fetch_apt_type():
    print("\n[2] 타입별 분양가/세대수")
    data = fetch_all("ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancMdl")
    save("apt_type.json", data)
    return data


def fetch_residual():
    print("\n[3] 무순위/잔여세대")
    data = fetch_all("ApplyhomeInfoDetailSvc/v1/getRemndrLttotPblancDetail")
    save("residual.json", data)
    return data


def fetch_competition():
    print("\n[4] 경쟁률")
    data = fetch_all("ApplyhomeInfoCmpetRtSvc/v1/getAPTLttotPblancCmpet")
    save("competition.json", data)
    return data


def fetch_spsply():
    print("\n[5] 특별공급 신청현황")
    data = fetch_all("ApplyhomeInfoCmpetRtSvc/v1/getAPTSpsplyReqstStus")
    save("spsply.json", data)
    return data


def fetch_score():
    print("\n[6] 당첨가점")
    data = fetch_all("ApplyhomeInfoCmpetRtSvc/v1/getAptLttotPblancScore")
    save("score.json", data)
    return data


def fetch_winner_stat():
    print("\n[7] 지역별 당첨가점 통계 (score.html용)")
    data = fetch_all("ApplyhomeStatSvc/v1/getAPTApsPrzwnerStat")
    save("winner_stat.json", data)
    return data


# ── 메인 ──────────────────────────────────────────

def main():
    if not API_KEY:
        raise SystemExit("[오류] API_KEY 환경변수가 없습니다.")

    print("=" * 55)
    print("aptpass.kr 청약 데이터 수집 시작")
    print("=" * 55)

    fetch_apt()
    fetch_apt_type()
    fetch_residual()
    fetch_competition()
    fetch_spsply()
    fetch_score()
    fetch_winner_stat()

    print("\n" + "=" * 55)
    print("데이터 수집 완료")
    print("=" * 55)


if __name__ == "__main__":
    main()
