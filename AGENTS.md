# mind_law 작업 규칙

이 저장소는 `kfcccpro-ship-it/mind_law` 전용이다. 다른 저장소에 파일을 배포하지 않는다.

## 단일 원본
- 법령·학습카드·ANKI 빈칸·근거조문 원문: `course.json`
- UI/엔진: `src/app.template.html`
- 배포본: `index.html` (자동 생성물, 직접 수정 금지)

## UI 핵심 규칙
- depth 1 챕터(A~E)는 한 번에 하나만 펼친다.
- 새 챕터를 선택하면 다른 챕터의 하위 노드를 모두 접고 선택 챕터를 포커스·Auto-Fit 한다.
- 상세카드는 핵심요약 → ANKI 빈칸회상 → 쉬운 말 → 암기포인트 → 근거조문 원문 순서를 유지한다.
- 현장사례, 헷갈림 주의, 객관식 확인퀴즈는 다시 추가하지 않는다.

## 법령 원문 규칙
- 단순 `제9조` 표기만으로 끝내지 않는다.
- 실제 법령 원문은 `course.json > legalTexts`에 저장한다.
- 각 카드는 `lawKeys`로 관련 조문 원문을 연결한다.
- 법령 사실을 바꾸는 경우 새마을금고법/시행령의 최신 시행본을 다시 확인한다.

## 모든 수정 시 필수
1. `course.json` 또는 템플릿을 수정한다.
2. `python3 scripts/build.py` 실행.
3. `python3 scripts/build.py --check` 실행.
4. `python3 scripts/extract_js.py index.html /tmp/mind_law_app.js && node --check /tmp/mind_law_app.js` 실행.
5. 가능하면 PC·모바일 브라우저 상호작용을 회귀 테스트한다.
6. 소스와 생성된 `index.html`을 같은 변경 단위로 `main`에 반영한다.

## 배포
- Pages 주소: `https://kfcccpro-ship-it.github.io/mind_law/`
- main/root의 `index.html`이 공개 배포본이다.
- 카카오 링크는 `course.json > meta.kakaoUrl`에서 관리한다.

## 자동화
- `rebuild.yml`: source 변경 시 `index.html` 자동 재생성 및 main 커밋
- `validate.yml`: source/index 동기화와 JavaScript 구문 자동 검증