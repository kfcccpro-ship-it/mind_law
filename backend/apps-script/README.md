# DAILY 완료기록 백엔드 설치

GitHub Pages는 정적 사이트이므로 200명의 완료현황을 중앙에서 모으려면 Google Apps Script Web App 1개가 필요합니다.

1. Apps Script에서 새 프로젝트를 만들고 이 폴더의 `Code.gs` 전체를 붙여넣습니다.
2. 편집기에서 `setup()`을 한 번 실행합니다.
3. 반환되는 `sheetUrl`과 `adminKey`를 별도로 보관합니다.
4. **배포 → 새 배포 → 웹 앱**에서 실행 사용자는 '나', 액세스 사용자는 운영상 필요한 범위로 설정합니다.
5. 발급된 `/exec` URL을 `daily_questions/manifest.json`의 `completion.apiUrl`에 넣고 `completion.enabled`를 `true`로 변경합니다.
6. 생성된 Google Sheet의 `ROSTER` 시트 A열에 카카오방 닉네임을 입력합니다. B열에 `false`를 넣은 사람은 활성명단에서 제외됩니다.
7. GitHub Pages의 `/admin/`에서 Web App URL, `adminKey`, 날짜를 입력하면 완료자·미완료자를 확인할 수 있습니다.

## 문항수 확대

`manifest.json`에는 `defaultQuestionsPerDay`와 `maxQuestionsPerDay`가 있습니다. 특정 날짜만 늘리려면 해당 날짜의 plan 항목에 `"questionCount": 30`처럼 넣으면 됩니다. DAILY 화면과 검증기는 실제 문항수를 자동으로 읽기 때문에 20→30→40문항으로 늘려도 별도 UI 수정이 필요 없습니다.

## 개인정보/운영 주의

닉네임과 학습완료 기록을 수집하므로 수강생에게 수집 목적·항목·보관기간을 사전에 안내하는 것이 좋습니다. 이 기록은 참여확인을 돕는 운영자료이며, 정적 웹앱 특성상 부정행위를 완전히 방지하는 시험감독 시스템은 아닙니다.
