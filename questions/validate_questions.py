#!/usr/bin/env python3
"""CAR PLAYGROUND 소재 DB 검증 스크립트.

사용법: python validate_questions.py [questions 폴더 경로]
종료 코드 0 = 오류 없음, 1 = 오류 있음. 경고(WARN)는 종료 코드에 영향 없음.
"""
import json
import re
import sys
from pathlib import Path

CATEGORIES = {"BALANCE", "ESTIMATE", "QUIZ", "DEBATE", "MEMORY"}
ANSWER_TYPES = {"CHOICE", "NUMBER", "TEXT", "OPEN"}
CATEGORY_ANSWER_TYPE = {
    "BALANCE": "CHOICE", "ESTIMATE": "NUMBER", "QUIZ": "TEXT",
    "DEBATE": "OPEN", "MEMORY": "OPEN",
}
AUDIENCES = {"ALL", "KID", "ADULT", "FRIENDS"}
AGES = {"PRE", "ELEM", "TEEN"}
STATUSES = {"DRAFT", "REVIEWED", "PUBLISHED", "RETIRED"}
MAX_SPOKEN_CHARS = 90  # 차 안에서 한 번에 듣기 좋은 길이(제안값, 데이터로 조정 가능)
ID_PATTERN = re.compile(r"^[A-Z]+-[A-Z]{3}-\d{3,}$")


def load(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def main(root: Path) -> int:
    errors, warns = [], []
    region_codes = {r["code"] for r in load(root / "regions.json")["regions"]}
    mode_categories = {m["category"] for m in load(root / "modes.json")["modes"]}
    seen_ids = set()
    count = 0
    per_mode = {}
    per_aud = {}

    for path in sorted(root.glob("*/*.json")):
        data = load(path)
        folder_region = path.parent.name.upper()
        for item in data["questions"]:
            count += 1
            qid = item.get("id", "<no id>")
            where = f"{path.relative_to(root)}:{qid}"

            def err(msg):
                errors.append(f"{where}: {msg}")

            def warn(msg):
                warns.append(f"{where}: {msg}")

            if not ID_PATTERN.match(qid):
                err("id 형식은 REGION-CAT-NNN")
            if qid in seen_ids:
                err("id 중복")
            seen_ids.add(qid)

            cat = item.get("category")
            if cat not in CATEGORIES:
                err(f"category 값 오류: {cat}")
                continue
            if cat not in mode_categories:
                err("modes.json에 연결된 모드가 없는 category")
            if item.get("region") not in region_codes:
                err(f"regions.json에 없는 region: {item.get('region')}")
            if item.get("region") != folder_region:
                err(f"폴더({folder_region})와 region({item.get('region')}) 불일치")
            if path.stem.upper() != cat:
                err(f"파일명({path.stem})과 category({cat}) 불일치")
            if item.get("difficulty") not in (1, 2, 3):
                err("difficulty는 1~3")
            atype = item.get("answerType")
            if atype not in ANSWER_TYPES:
                err(f"answerType 값 오류: {atype}")
            elif atype != CATEGORY_ANSWER_TYPE[cat]:
                err(f"{cat}의 answerType은 {CATEGORY_ANSWER_TYPE[cat]}이어야 함")
            aud = item.get("audience", "ALL")
            if aud not in AUDIENCES:
                err(f"audience 값 오류: {aud}")
            ages = item.get("ages")
            if ages:
                if aud != "KID":
                    err("ages는 audience=KID일 때만 사용")
                elif not set(ages) <= AGES:
                    err(f"ages 값 오류: {ages}")
            status = item.get("status")
            if status not in STATUSES:
                err(f"status 값 오류: {status}")

            text = item.get("spokenText") or item.get("text", "")
            if not text:
                err("text 없음")
            elif len(text) > MAX_SPOKEN_CHARS:
                warn(f"읽어줄 문장이 {len(text)}자: {MAX_SPOKEN_CHARS}자 이내 권장")

            if atype == "CHOICE":
                choices = item.get("choices") or []
                ids = [c.get("id") for c in choices]
                if len(choices) != 2 or len(set(ids)) != 2:
                    err("CHOICE는 서로 다른 id의 선택지 2개 필요")
            if atype == "NUMBER":
                ans = item.get("answer") or {}
                for key in ("unit", "tolerancePct", "scoring"):
                    if key not in ans:
                        err(f"NUMBER answer.{key} 필요")
            if atype == "TEXT":
                if not item.get("answers"):
                    err("TEXT는 answers 필요")

            needs_fact = atype in ("NUMBER", "TEXT")
            if needs_fact and status in ("REVIEWED", "PUBLISHED"):
                src = item.get("source") or {}
                if not src.get("title") or not src.get("referenceYear"):
                    err("사실 기반 소재는 source.title과 source.referenceYear 필수")
                if atype == "NUMBER" and (item.get("answer") or {}).get("value") is None:
                    err("PUBLISHED/REVIEWED NUMBER 소재는 answer.value 필수")
            if needs_fact and status == "DRAFT":
                warn("DRAFT 사실 소재: 앱 노출 금지, 출처 확인 후 REVIEWED 이상으로 변경")

            if atype == "OPEN" and not item.get("followUps"):
                warn("OPEN 소재는 followUps(대화 이어가기 멘트) 권장")

            if status == "PUBLISHED":
                per_mode.setdefault((cat, item.get("region")), 0)
                per_mode[(cat, item.get("region"))] += 1
                if item.get("region") == "COMMON":
                    per_aud[(cat, aud)] = per_aud.get((cat, aud), 0) + 1

    # 게임당 5문제 출제 가능 여부 점검 (COMMON + 지역 합산)
    for cat in sorted(CATEGORIES):
        total_common = per_mode.get((cat, "COMMON"), 0)
        if total_common < 5:
            warns.append(f"[분량] {cat} COMMON 게시 소재 {total_common}개: 게임당 5문제 채우려면 최소 5개 필요")

    # 구성별 분량: 아이와 함께 = ALL+KID, 어른끼리 = ALL+ADULT, 친구끼리 = ALL+ADULT+FRIENDS (게임당 5문제)
    for cat in sorted(c for c in CATEGORIES if c != "QUIZ"):
        g = lambda a: per_aud.get((cat, a), 0)
        for label, n in (("아이와 함께", g("ALL") + g("KID")), ("어른끼리", g("ALL") + g("ADULT")),
                         ("친구끼리", g("ALL") + g("ADULT") + g("FRIENDS"))):
            if n < 5:
                warns.append(f"[분량] {cat} {label} 구성 COMMON 소재 {n}개: 게임당 5문제에 부족")

    print(f"검사한 소재: {count}개, 파일 {len(list(root.glob('*/*.json')))}개")
    for w in warns:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"결과: 오류 {len(errors)}건, 경고 {len(warns)}건")
    return 1 if errors else 0


if __name__ == "__main__":
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
    sys.exit(main(base))
