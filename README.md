# CAR PLAYGROUND

현대자동차그룹 차량용 앱 개발 공모전(Pleos Playground) 출품 프로젝트. 동승자 성인 2~5명이 화면 없이 말로 즐기는 차 안 대화 애플리케이션. 점수, 레벨, 시간제한이 없고 추천 모드와 자유 모드로 이용한다.

## 구성
| 경로 | 내용 |
|---|---|
| `PLAN_기획서.md` | 22항목 기획서 초안 (제출용) |
| `GDD_CAR_PLAYGROUND.md` | 제품 설계서 v1.0 |
| `QUESTION_DB.md` | 문항 DB 가이드 |
| `questions/catalog.json` | 7그룹 46유형 카탈로그 |
| `questions/<지역>/<유형>.json` | 문항 데이터 (common, daejeon, busan, jeonju) |
| `questions/validate_questions.py` | 문항 검증 스크립트 |
| `prototype/CAR_PLAYGROUND_prototype.html` | 웹 프로토타입 (파일 하나) |

## 프로토타입 열기
`prototype/CAR_PLAYGROUND_prototype.html`을 크롬이나 사파리로 연다. 음성 인식은 크롬에서 잘 되고 마이크 권한이 필요하다. 마이크가 안 되면 입력창으로 답한다. 상단의 “정차 중 / 주행 중” 토글로 주행 중 음성 전용 화면을 확인할 수 있다.

## 문항 검증
```
python questions/validate_questions.py questions
```

## 메모
- 사실형 문항(상식, 숫자, 가격)은 출처 확인 전 샘플(`sample:true`)이다.
- 소리 7종은 음원 확보 후 활성화한다(현재 준비 중).
- 이전 게임형 프로토타입(v0.x)은 git 기록에 있다.
