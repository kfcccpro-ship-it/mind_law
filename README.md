# 새마을금고법 학습 마인드맵

새마을금고법을 5개 영역·32개 학습카드로 구조화한 비공식 학습용 웹앱입니다.

- 배포: `https://kfcccpro-ship-it.github.io/mind_law/`
- 기준: 새마을금고법 및 시행령 2026.03.15 시행본을 2026.09.29 기준 재검토
- 문의: https://open.kakao.com/o/gEtSyUPi

## 현재 학습 구조

- 챕터는 **한 번에 하나만 펼침**: 다른 챕터를 누르면 기존 챕터 하위 노드가 자동으로 접히고 새 챕터가 화면 중심에 맞춰짐
- 상세카드: `핵심 요약 · 교안 원문 → ANKI 핵심단어 빈칸회상 → 쉬운 말 풀이 → 암기 포인트 → 근거조문 원문`
- 현장사례·헷갈림 주의·객관식 확인퀴즈는 사용하지 않음
- 근거조문은 단순 조문번호가 아니라 `legalTexts`에 법령 원문을 저장하고 카드의 `lawKeys`가 이를 참조함

## 소스 구조

- `course.json` — **법령 학습 콘텐츠·ANKI 빈칸·법령 원문의 단일 원본**
- `src/app.template.html` — UI/마인드맵 엔진 원본
- `scripts/build.py` — 검증 후 `index.html` 생성
- `index.html` — GitHub Pages 배포 파일(직접 편집 금지)
- `.github/workflows/validate.yml` — push/PR 시 자동 검증
- `.github/workflows/rebuild.yml` — `course.json`·템플릿 수정 시 `index.html` 자동 재생성·커밋

## 수정·배포 원칙

1. 내용 수정은 `course.json`, UI 수정은 `src/app.template.html`에서 한다.
2. 법령 근거를 바꾸면 `legalTexts`의 원문과 카드 `lawKeys`를 함께 확인한다.
3. `python3 scripts/build.py`로 `index.html`을 생성한다.
4. `python3 scripts/build.py --check`와 `node --check` 검사를 통과시킨다.
5. `course.json` 또는 템플릿만 수정해도 `rebuild.yml`이 `index.html`을 자동 재생성해 커밋한다.
6. `main` 루트의 `index.html`이 갱신되면 GitHub Pages가 배포한다.

> 비공식 학습자료입니다. 실무 적용 전 국가법령정보센터의 현행 법령과 해당 금고 정관·내부규정을 확인하세요.