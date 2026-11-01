#!/usr/bin/env python3
"""CAR PLAYGROUND 문항 DB 검증 (v1.0, 45+ 유형 카탈로그 기준).

사용법: python validate_questions.py [questions 폴더]
종료 코드 0 = 오류 없음, 1 = 오류 있음. 경고(WARN)는 종료 코드에 영향 없음.
"""
import json, re, sys
from pathlib import Path

AUDIENCES = {"ALL", "KID", "ADULT", "FRIENDS"}
STATUSES = {"DRAFT", "REVIEWED", "PUBLISHED", "RETIRED"}
MAX_SPOKEN = 90
ID_RE = re.compile(r"^[A-Z]+-[A-Z0-9]+-\d{3}$")
# kind별 필수 필드
NEED = {
    "choice": ["choices"], "predict": ["choices"], "qchoice": ["choices", "answer"],
    "text": ["answers"], "hint": ["answers", "hints"], "number": ["num"],
    "rank": ["choices"], "open": [], "speak": [], "sound": ["audio"],
}


def load(p):
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def main(root):
    cat = load(root / "catalog.json")
    types = {t["id"]: t for t in cat["types"]}
    regions = {r["code"] for r in load(root / "regions.json")["regions"]}
    errors, warns, seen = [], [], set()
    per_type, n = {}, 0
    for path in sorted(root.glob("*/*.json")):
        data = load(path)
        if not path.stem.isupper():
            continue  # 이전 버전(소문자 파일명)은 무시
        folder = path.parent.name.upper()
        for q in data["questions"]:
            n += 1
            qid = q.get("id", "<no id>")
            where = f"{path.relative_to(root)}:{qid}"
            e = lambda m: errors.append(f"{where}: {m}")
            w = lambda m: warns.append(f"{where}: {m}")
            if not ID_RE.match(qid): e("id 형식은 REGION-TYPE-NNN")
            if qid in seen: e("id 중복")
            seen.add(qid)
            t = types.get(q.get("type"))
            if not t: e(f"catalog.json에 없는 type: {q.get('type')}"); continue
            if path.stem != q["type"]: e(f"파일명({path.stem})과 type({q['type']}) 불일치")
            if q.get("region") not in regions: e(f"regions.json에 없는 region: {q.get('region')}")
            if q.get("region") != folder: e(f"폴더({folder})와 region({q.get('region')}) 불일치")
            if q.get("status") not in STATUSES: e(f"status 값 오류: {q.get('status')}")
            aud = q.get("aud", "ALL")
            if aud not in AUDIENCES: e(f"aud 값 오류: {aud}")
            if aud == "KID" and not q.get("retired"): w("KID 문항은 v1.0에서 사용하지 않음(retired 권장)")
            if not t.get("ready", True): continue
            for f in NEED.get(t["kind"], []):
                if not q.get(f): e(f"{t['kind']} 유형에 {f} 필요")
            if t["kind"] in ("choice", "predict", "qchoice", "rank"):
                k = len(q.get("choices", []))
                if k < 2 or k > 5: e("choices는 2~5개")
            if t["kind"] == "qchoice" and q.get("answer") not in [c["id"] for c in q.get("choices", [])]:
                e("answer가 choices의 id가 아님")
            if t["kind"] == "number":
                nm = q.get("num") or {}
                if not all(k in nm for k in ("value", "unit", "tol")): e("num에 value/unit/tol 필요")
            if t["kind"] in ("text", "number", "qchoice", "hint") and q.get("region") and not q.get("sample") and not (q.get("source") and q.get("referenceYear")):
                e("사실 기반 문항은 source와 referenceYear 필요 (샘플이면 sample:true)")
            if q.get("sample"): w("샘플 문항: 출처 확인 전")
            if len(q.get("text", "")) > MAX_SPOKEN: w(f"문장이 {MAX_SPOKEN}자 초과: 음성으로 듣기엔 길어요")
            if not q.get("follow"): w("follow(추가 질문) 없음")
            per_type[q["type"]] = per_type.get(q["type"], 0) + 1
    for tid, t in types.items():
        if t.get("ready", True) and per_type.get(tid, 0) < 2 and tid != "BALP":
            warns.append(f"유형 {tid}: 문항 {per_type.get(tid, 0)}개 (권장 3개 이상)")
    print(f"문항 {n}개 · 유형 {len(per_type)}/{len(types)}")
    for m in warns[:200]: print("WARN ", m)
    for m in errors: print("ERROR", m)
    print(f"오류 {len(errors)} · 경고 {len(warns)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent)))
