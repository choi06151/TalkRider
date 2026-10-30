# CAR PLAYGROUND

현대자동차그룹 차량용 앱 개발 공모전 출품 프로젝트. 차 안에서 목적지에 맞는 대화 소재를 꺼내 주는 협동형 음성 게임.

## 구성
| 경로 | 내용 |
|---|---|
| `GDD_CAR_PLAYGROUND.md` | 기획서(GDD). 최신 버전은 파일 맨 위 변경 요약 참고 |
| `QUESTION_DB.md` | 소재(질문) DB 설계 |
| `questions/` | 지역 x 카테고리별 소재 JSON, 모드/지역 마스터, 검증 스크립트 |
| `prototype/CAR_PLAYGROUND_prototype.html` | 웹 프로토타입 (파일 하나, HTML+CSS+JS) |

## 프로토타입 열기
`prototype/CAR_PLAYGROUND_prototype.html`을 크롬이나 사파리로 연다. 음성 인식은 크롬에서 잘 되고, 마이크 권한을 허용해야 한다. 마이크가 안 되면 입력창으로 답할 수 있다.

## 소재 검증
```
python questions/validate_questions.py questions
```

## 메모
- 프로토타입은 한 파일이다. 세로 화면(모바일)은 `body.fluid` / `#stage.fluid` 규칙, 가로 화면은 1280x720 무대를 비율에 맞춰 쓴다. 자세한 내용은 GDD 19장.
- 숫자 맞히기 소재의 값은 출처 확인 전 샘플이다 (DRAFT).
