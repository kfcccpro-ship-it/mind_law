# 새마을금고법 학습 마인드맵

새마을금고법을 5개 영역·32개 학습카드로 구조화한 비공식 학습용 웹앱입니다.

- 배포: `https://kfcccpro-ship-it.github.io/mind_law/`
- 기준: 새마을금고법 및 시행령 2026.03.15 시행본을 2026.09.29 기준 재검토
- 문의: https://open.kakao.com/o/gEtSyUPi

## 소스 구조

- `course.json` — **법령 학습 콘텐츠의 단일 원본**
- `src/app.template.html` — UI/마인드맵 엔진 원본
- `scripts/build.py` — 검증 후 `index.html` 생성
- `index.html` — GitHub Pages 배포 파일(직접 편집 금지)
- `.github/workflows/validate.yml` — push/PR 시 자동 검증
- `.github/workflows/rebuild.yml` — `course.json`·템플릿 수정 시 `index.html` 자동 재생성·커밋

## 수정·배포 원칙

1. 내용 수정은 `course.json`, UI 수정은 `src/app.template.html`에서 한다.
2. `python3 scripts/build.py`로 `index.html`을 생성한다.
3. `python3 scripts/build.py --check`와 `node --check` 검사를 통과시킨다.
4. `course.json` 또는 템플릿만 수정해도 `rebuild.yml`이 `index.html`을 자동 재생성해 커밋한다.
5. `main` 루트의 `index.html`이 갱신되면 GitHub Pages가 배포한다.

> 비공식 학습자료입니다. 실무 적용 전 국가법령정보센터의 현행 법령과 해당 금고 정관·내부규정을 확인하세요.