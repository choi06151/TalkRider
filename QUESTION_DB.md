# CAR PLAYGROUND — 소재(질문) DB 설계 v0.3

차 안 대화 소재를 **지역 × 카테고리**로 나눠 보관한다. 목적지가 정해지면 해당 지역 소재를 우선 꺼내고, 부족하면 공통(COMMON) 소재로 채운다.
**[제안]** 표시는 사용자가 바꿀 수 있는 기본값이다.

> **v0.3 변경**: 소재에 `audience`(ALL/KID/ADULT/FRIENDS)와 선택 필드 `ages`(PRE/ELEM/TEEN) 추가. 탑승 구성(아이와 함께/어른끼리/친구끼리)과 아이 깨어 있음 여부로 노출 소재를 거른다. 상세는 GDD 18장.

> **v0.2 변경**: 열린 질문(BALANCE/DEBATE/MEMORY)은 정답·클리어 개념 없이 `DONE`/`SKIP`으로 처리하고 답은 **대화 앨범**에 누적한다. 모드 순서는 01 밸런스, 02 숫자 맞히기, 03 찬반 토론, 04 추억 이야기(마지막). QUIZ는 소재가 준비될 때까지 프로토타입에서 제외. 소재에 선택 필드 `short`(찬반 주제의 짧은 이름) 추가. 상세는 GDD 17장.

## 1. 카테고리 = 게임 모드 [제안]
| 모드 | category | answerType | 설명 | 클리어 기준 |
|---|---|---|---|---|
| MODE_01 | BALANCE 밸런스 게임 | CHOICE | A/B 중 가족이 **합의해 하나 선택** | 합의 제출 |
| MODE_02 | QUIZ 상식 퀴즈 | TEXT | 지역·상식 퀴즈, 정답 문자열 판정 | 정답 일치 |
| MODE_03 | ESTIMATE 숫자 맞히기 | NUMBER | 합의한 숫자 1개 제출, 실제 값과 오차 비교 | 허용 오차 이내 |
| MODE_04 | DEBATE 찬반 토론 | OPEN | 정답 없음, 입장 합의 또는 의견 정리 | 합의 제출 |
| MODE_05 | MEMORY 추억 이야기 | OPEN | 정답 없음, 이야기 공유 | 한 번이라도 답하면 인정 |

- OPEN/CHOICE 소재는 정답이 없으므로 **"합의된 답을 한 번 제출하면 해당 문제 성공"** 으로 처리한다 (기존 5문제 중 3문제 이상 성공 = 클리어 규칙 유지).
- 난이도(1~3)는 시간 압박이 아니라 **소재의 깊이** 로 조절한다 (주행 중에는 카운트다운을 쓰지 않는다).
- 해금 순서와 모드 이름은 임시. 쉬운 소재(밸런스)부터 시작하도록 배치했다.

## 2. 폴더 구조 (Android `assets/questions/`)
```
questions/
 ├── regions.json          지역 마스터 (코드, 이름, 별칭)
 ├── modes.json            모드 ↔ category 연결
 ├── common/               지역과 무관한 소재
 │    ├── balance.json  debate.json  memory.json  ...
 ├── daejeon/
 │    ├── balance.json  estimate.json  quiz.json  memory.json
 ├── busan/  jeonju/ ...
 └── validate_questions.py 검증 스크립트
```
- 파일 하나 = 지역 하나 × 카테고리 하나. 앱은 **목적지 지역 폴더 + common만** 읽어 메모리를 아낀다 (Pleos RAM 400MB, 지연 로딩 권장).
- 원본(source of truth)은 JSON(git으로 검수·이력 관리). 소재가 수천 개로 늘면 빌드 단계에서 SQLite(Room 프리패키지)로 변환한다. 앱 코드는 `QuestionRepository` 인터페이스만 본다.

## 3. 소재 스키마
```json
{
  "id": "DAEJEON-BAL-001",
  "category": "BALANCE",
  "region": "DAEJEON",
  "tags": ["대전", "성심당", "빵"],
  "difficulty": 1,
  "audience": "ALL",
  "ages": null,
  "text": "화면에 보여줄 문장",
  "spokenText": "TTS로 읽을 문장 (없으면 text 사용, 90자 이내 권장)",
  "answerType": "CHOICE",
  "choices": [{"id": "A", "label": "튀김소보로"}, {"id": "B", "label": "부추빵"}],
  "answer": null,
  "answers": null,
  "hints": [],
  "followUps": ["대화를 이어가는 멘트"],
  "reveal": "정답/실제 값 공개 멘트 ({value} {unit} {sourceTitle} {referenceYear} 치환)",
  "source": null,
  "status": "PUBLISHED",
  "origin": "AI_DRAFT_HUMAN_REVIEW",
  "locale": "ko-KR",
  "updatedAt": "2026-10-30"
}
```
- `audience`: `ALL`(기본, 누구와 들어도 됨) / `KID`(아이용, 아이가 깨어 있을 때만) / `ADULT`(아이 없을 때) / `FRIENDS`(친구끼리만). `ages`는 KID 전용 선택 필드로 `PRE`·`ELEM`·`TEEN` 중 허용 연령대(없으면 전 연령).
- ESTIMATE: `answer = {value, unit, tolerancePct, scoring}`, `scoring`은 `WITHIN_TOLERANCE`(기본).
- QUIZ: `answers = ["정답", "동의어", ...]`
- `source = {title, publisher, url, referenceYear}`
- `status`: DRAFT → REVIEWED → PUBLISHED → RETIRED. **앱은 PUBLISHED만 노출한다.**
- `origin`: `HUMAN`, `AI_DRAFT_HUMAN_REVIEW`, `AI_GENERATED_RUNTIME` (실시간 생성은 OPEN 소재만 허용).

## 4. 품질·안전 규칙
1. **사실 소재(NUMBER, TEXT)는 출처와 기준 연도가 없으면 게시 금지.** 검증 스크립트가 오류로 막는다. AI가 만든 숫자는 반드시 사람이 출처로 확인한다.
2. 숫자 소재는 `reveal`에서 출처와 기준 연도를 함께 읽어준다 (예: "…기준").
3. 가족 동승을 전제로 **정치·종교·성별·세대 갈등, 외모 비교, 사고·질병 같은 민감 소재 금지.**
4. 읽는 문장은 **한 번 듣고 이해되는 길이**(90자 이내 권장, 데이터 상수로 조정). 철자·글자 모양에 의존하는 문제는 지양.
5. 운전자에게 계산·긴 기억·빠른 반응을 요구하지 않는다. 답은 항상 선택·한마디·대략적 추정.
6. 지역 소재는 실존 장소·상품을 쓰되 광고처럼 들리지 않게, 선호를 묻는 형태(밸런스·추억)를 우선한다.

## 5. 소재 선택 로직 (SelectionPolicy)
입력: 모드(category), 난이도, 목적지 지역, 최근 출제 이력, 게임당 문제 수(5).
1. 목적지 → `RegionResolver`로 지역 코드 결정. 못 찾으면 COMMON만 사용. (목적지 조회 가능 여부는 Pleos NaviHelper 문서 확인 후 확정, 프로토타입은 수동 선택 + Mock)
2. 후보 = (해당 지역 ∪ COMMON) ∩ category ∩ PUBLISHED ∩ 난이도 ± 허용.
2-1. **대상 필터**: 아이가 깨어 있으면 ALL+KID(연령 일치), 어른끼리/아이 잠듦은 ALL+ADULT, 친구끼리는 ALL+ADULT+FRIENDS.
3. 최근 출제 이력(예: 최근 50문제)은 제외.
4. 지역 소재를 우선해 **최대 3문제**, 나머지는 COMMON으로 채운다 [제안]. 지역 소재가 없으면 COMMON 5문제.
5. 후보가 5개 미만이면 난이도 허용 범위를 넓혀 채운다.

## 6. 소재 제작 파이프라인
1. AI로 지역·카테고리별 초안 대량 생성 (`status: DRAFT`, `origin: AI_DRAFT_HUMAN_REVIEW`)
2. 사람이 사실·민감성·길이 확인 → 사실 소재는 출처 기입 → `REVIEWED`
3. `validate_questions.py` 통과 → `PUBLISHED`
4. 오래된 수치(기준 연도 경과)는 `RETIRED` 또는 갱신

## 7. 현재 샘플 상태 (2026-10-30)
- 소재 14개, 지역 4곳(COMMON, 대전, 부산, 전주), 카테고리 4종.
- BALANCE/DEBATE/MEMORY는 선호·의견형이라 사실 검증 없이 게시 가능으로 표기했다. 실제 앱 반영 전 한 번 더 읽어보고 어색한 문장은 수정할 것.
- **ESTIMATE(성심당 소금빵)는 `DRAFT`·값 없음.** 공개 자료의 출처를 확인해 채우기 전에는 앱에 나오지 않는다. QUIZ 샘플은 아직 없음.
- 게임당 5문제를 채우려면 모드별 COMMON 소재가 최소 5개씩 필요하다 (현재 BALANCE 4, DEBATE 2, MEMORY 2, ESTIMATE 0, QUIZ 0). 검증 스크립트가 부족분을 경고한다.

## 8. 검증
`python validate_questions.py questions/` — id 형식·중복, category/answerType/폴더명 일치, 선택지 2개, 사실 소재의 출처·값 필수, 읽는 문장 길이, 모드별 분량.
