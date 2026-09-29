# mind_law 작업 규칙

이 저장소는 `kfcccpro-ship-it/mind_law` 전용이다. 다른 저장소에 파일을 배포하지 않는다.

## 단일 원본
- 법령·학습카드: `course.json`
- UI/엔진: `src/app.template.html`
- 배포본: `index.html` (자동 생성물, 직접 수정 금지)

## 모든 수정 시 필수
1. 현행 법령 사실을 바꾸는 경우 새마을금고법/시행령의 최신 시행본을 다시 확인한다.
2. `course.json` 또는 템플릿을 수정한다.
3. `python3 scripts/build.py` 실행.
4. `python3 scripts/build.py --check` 실행.
5. `python3 scripts/extract_js.py index.html /tmp/mind_law_app.js && node --check /tmp/mind_law_app.js` 실행.
6. 소스와 생성된 `index.html`을 같은 변경 단위로 `main`에 반영한다.

## 배포
- Pages 주소: `https://kfcccpro-ship-it.github.io/mind_law/`
- main/root의 `index.html`이 공개 배포본이다.
- 카카오 링크는 `course.json > meta.kakaoUrl`에서 관리한다.

## 자동화
- `rebuild.yml`: source 변경 시 `index.html` 자동 재생성 및 main 커밋
- `validate.yml`: source/index 동기화와 JavaScript 구문 자동 검증