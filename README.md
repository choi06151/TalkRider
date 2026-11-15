# CAR PLAYGROUND

현대자동차그룹 차량용 앱 개발 공모전(Pleos Playground) 출품 프로젝트. 동승자 성인 2~5명이 화면 없이 말로 즐기는 차 안 대화 애플리케이션. 점수, 레벨, 시간제한이 없고 자유 모드로 이용한다. 목적지와 남은 시간은 차량(내비) API에서 자동으로 받는다.

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
`prototype/CAR_PLAYGROUND_prototype.html`을 브라우저로 연다(`prototype/img/` 폴더가 옆에 있어야 한다). 화면은 Figma `Page 5` 프레임 60개를 레이어 그대로(글자 크기·폰트·이미지 배치) 옮긴 것이고, IA(전체 앱 흐름 · 게임별 진행 흐름) 순서로 이어진다. 휴대폰 이미지 저장 화면만 Page 5에 없어 이전 화면을 쓴다.
- 카드·버튼·상단 탭(홈·놀이·기록·설정)을 누르면 다음 화면으로 간다. 게임 화면은 본문이나 “패스”·“다음 문제” 같은 음성 명령 버튼을 누르면 다음 단계, 인트로는 4초 후 자동 시작.
- 게임 중 “멈춤” → 일시정지·이어하기, 왼쪽 위 캐릭터 → 앱 종료(진행 저장) 후 다시 열면 이어하기. 음성 바 왼쪽 아이콘은 홈·놀이·기록.
- ← / Esc 뒤로, → 다음.

### 엽서 QR로 휴대폰에 받기
휴대폰이 PC에 접속해야 하므로 서버로 띄운다.
```
node prototype/serve.js
```
1. 휴대폰과 PC를 같은 Wi-Fi에 연결한다. (Windows 방화벽 창이 뜨면 "개인 네트워크" 허용)
2. PC 브라우저로 터미널에 찍힌 주소(`http://localhost:5173/`)를 연다.
3. 여행 엽서 → QR로 받기 화면의 QR은 PC의 Wi-Fi 주소로 자동 생성된다. 휴대폰 카메라로 찍으면 `postcard.html`이 열리고, “이미지 저장”으로 엽서(앞면·뒷면)를 사진에 저장한다.
- 엽서 이미지: `prototype/postcards/` (Figma Page 5 엽서를 반듯하게 2배 해상도로 내보낸 것)
- QR 생성: `prototype/vendor/qrcode.js` (qrcode-generator, MIT)
- 파일을 그냥 열거나 서버 없이 열면 QR은 보이지만 휴대폰에서는 열리지 않는다. 설정의 “마이크 테스트”로 음성 명령(“다음” “이전” “잠깐” “이어서” “놀이 시작”)을 켠다.
- 안내 음성은 브라우저 내장 음성 중 **남자 목소리**를 먼저 고른다. **Edge**로 열면 신경망 남성 음성 “InJoon / Hyunsu Online (Natural)”이 나와 가장 자연스럽다. 크롬에는 한국어 남자 음성이 없어 “Google 한국의”(여성)로 대체되고 안내 문구가 한 번 뜬다. 주소 뒤에 `?voice=Hyunsu`처럼 붙이면 음성을 직접 고를 수 있다.

## 문항 검증
```
python questions/validate_questions.py questions
```

## 메모
- 사실형 문항(상식, 숫자, 가격)은 출처 확인 전 샘플(`sample:true`)이다.
- 소리 7종은 음원 확보 후 활성화한다(현재 준비 중).
- 이전 게임형 프로토타입(v0.x)은 git 기록에 있다.
