# 문항 DB 가이드 v1.0

구조: `questions/catalog.json`(그룹·유형 정의) + `questions/<지역>/<유형>.json`(문항). 지역은 common, daejeon, busan, jeonju.

## 문항 공통 필드
`id`(REGION-TYPE-NNN), `type`, `region`, `text`(음성으로 90자 이내 권장), `follow`(추가 질문, 앱은 첫 번째만 한 번 사용), `status`(DRAFT→REVIEWED→PUBLISHED→RETIRED), `aud`(ALL, ADULT, FRIENDS; KID는 retired).

## kind별 추가 필드
| kind | 필드 |
|---|---|
| choice, predict, rank | `choices`[{id,label}] (2~5개) |
| qchoice | `choices`, `answer`(choice id), `reveal` |
| text | `answers`[], `reveal` |
| hint | `answers`, `hints`[] |
| number | `num`{value, unit, tol(%)}, `hints`, `refNote` |
| open, speak | 선택: `items`(단어 목록), `start`(첫 문장) |
| sound | `audio`(음원 경로) — 준비 중 |

## 사실형 문항 규칙
text, number, qchoice는 `source`와 `referenceYear`가 있어야 PUBLISHED 가능. 지금 있는 사실형 문항은 모두 `sample:true`(출처 확인 전)이고 검수 후 제거한다. 가격 문항은 시점에 따라 바뀌므로 기준일을 적는다.

## 검증
`python questions/validate_questions.py questions` — 오류 0이어야 반영. 현재 159문항 · 38/46유형(소리 7종 + 선택 예상하기는 BAL 문항 공유).

## 작성 원칙
점수·시간제한 전제 금지, 순발력 질문 금지, 한 문항 한 번에 듣기 좋은 길이, 특정 개인/집단 비하 금지, 추가 질문은 대답을 강요하지 않는 열린 문장.
