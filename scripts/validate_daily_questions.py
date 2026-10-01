#!/usr/bin/env python3
import json, pathlib, sys, datetime, math, re

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "daily_questions"

def fail(msg):
    print(f"[FAIL] {msg}")
    sys.exit(1)

manifest_path = DATA / "manifest.json"
if not manifest_path.exists():
    fail("manifest.json missing")

manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
if manifest.get("days") != 30:
    fail("manifest days must be 30")

default_count = int(manifest.get("defaultQuestionsPerDay", manifest.get("questionsPerDay", 20)))
max_count = int(manifest.get("maxQuestionsPerDay", 60))
if default_count < 1 or max_count < default_count:
    fail("invalid default/max question counts")


TRACK_SUBJECTS = {
    "법·감독·정관·선거": {
        "새마을금고법", "새마을금고법 시행령", "새마을금고법 시행규칙",
        "감독기준", "감독기준 시행세칙", "정관", "선거"
    },
    "여신": {"여신"},
    "수신·출자": {"수신", "출자"},
    "AML·세무·공제": {"자금세탁방지", "AML", "세무", "공제"},
    "새마을금고론": {"새마을금고론"},
    "인사·복무·직제·내부통제": {
        "인사", "복무", "직제", "내부통제", "개인정보보호",
        "사업계획·예산", "보수", "퇴직급여", "감사"
    },
}

def track_for_subject(subject):
    for track, subjects in TRACK_SUBJECTS.items():
        if subject in subjects:
            return track
    return None

plan_by_date = {x["date"]: x for x in manifest.get("plan", [])}
latest = manifest.get("latest")
try:
    datetime.date.fromisoformat(latest)
except Exception:
    fail("latest must be YYYY-MM-DD")

daily_paths = sorted(DATA.glob("20??-??-??.json"))
latest_path = DATA / f"{latest}.json"
if not latest_path.exists():
    fail(f"latest DAILY file missing: {latest}.json")
future_files = [p.name for p in daily_paths if p.stem > latest]
if future_files:
    fail(f"future DAILY files must not be pre-published beyond manifest.latest: {future_files}")

seen_ids = set()
seen_question_texts = {}
seen_similar_texts = {}

def normalize_text(value):
    return re.sub(r"[^0-9A-Za-z가-힣]+", "", str(value)).lower()

def check_answer_distribution(path_name, answers, label):
    counts = [answers.count(i) for i in (1,2,3,4)]
    total = len(answers)
    expected = total / 4
    tolerance = max(2, math.ceil(total * 0.15))
    if min(counts) == 0:
        fail(f"{path_name}: {label} answer position missing; counts={counts}")
    if max(abs(c - expected) for c in counts) > tolerance:
        fail(f"{path_name}: {label} answer positions too skewed; counts={counts}")

for path in daily_paths:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("date") != path.stem:
        fail(f"{path.name}: date mismatch")

    plan = plan_by_date.get(path.stem, {})
    expected = int(plan.get("questionCount", default_count))
    if expected > max_count:
        fail(f"{path.name}: expected count {expected} exceeds maxQuestionsPerDay {max_count}")

    qs = obj.get("questions")
    if not isinstance(qs, list) or len(qs) != expected:
        fail(f"{path.name}: exactly {expected} questions required")

    # Mixed DAILY must expose all declared learning tracks with real question counts.
    if plan.get("mode") == "mixed_daily":
        declared = obj.get("trackCounts")
        if not isinstance(declared, dict):
            fail(f"{path.name}: trackCounts required for mixed_daily")
        if sum(int(v) for v in declared.values()) != expected:
            fail(f"{path.name}: trackCounts sum must equal {expected}")

        actual = {k: 0 for k in TRACK_SUBJECTS}
        for q in qs:
            subject = str(q.get("scope", {}).get("subject", "")).strip()
            track = track_for_subject(subject)
            if not track:
                fail(f"{path.name}: unmapped mixed_daily subject: {subject!r}")
            actual[track] += 1

        if set(declared) != set(actual):
            fail(f"{path.name}: trackCounts keys must match canonical six tracks")
        for track, count in actual.items():
            if int(declared.get(track, -1)) != count:
                fail(f"{path.name}: trackCounts mismatch for {track}: declared={declared.get(track)}, actual={count}")
            if count < 1:
                fail(f"{path.name}: mixed_daily track has zero questions: {track}")

        # Avoid long runs from the same subject+unit.
        run_key = None
        run_len = 0
        for q in qs:
            scope = q.get("scope", {})
            key = (scope.get("subject"), scope.get("unit"))
            if key == run_key:
                run_len += 1
            else:
                run_key = key
                run_len = 1
            if run_len > 3:
                fail(f"{path.name}: more than 3 consecutive questions from same subject+unit: {key}")

    check_answer_distribution(path.name, [q.get("answer") for q in qs], "base")
    check_answer_distribution(path.name, [q.get("remediation", {}).get("similar", {}).get("answer") for q in qs], "similar")

    for q in qs:
        required = ["id","question","choices","answer","explanation","source","sourceVersion","sourceExcerpt","point","remediation"]
        missing = [k for k in required if k not in q]
        if missing:
            fail(f"{path.name}: {q.get('id','?')} missing {missing}")
        if q["id"] in seen_ids:
            fail(f"duplicate id: {q['id']}")
        seen_ids.add(q["id"])

        nq = normalize_text(q["question"])
        if nq in seen_question_texts:
            fail(f"duplicate question text: {q['id']} == {seen_question_texts[nq]}")
        seen_question_texts[nq] = q["id"]
        if len(q["choices"]) != 4:
            fail(f"{q['id']}: exactly 4 choices required")
        if q["answer"] not in (1,2,3,4):
            fail(f"{q['id']}: answer must be 1..4")
        if not str(q["explanation"]).strip() or not str(q["source"]).strip():
            fail(f"{q['id']}: explanation/source required")

        scope = q.get("scope", {})
        for k in ("subject","unit","chapter","part"):
            if not str(scope.get(k,"")).strip():
                fail(f"{q['id']}: scope.{k} required")

        r = q["remediation"]
        if not isinstance(r, dict) or not str(r.get("detail","")).strip():
            fail(f"{q['id']}: remediation.detail required")
        if not str(r.get("rule","")).strip():
            fail(f"{q['id']}: remediation.rule required")
        if not str(r.get("why","")).strip():
            fail(f"{q['id']}: remediation.why required")
        if not str(r.get("contrast","")).strip():
            fail(f"{q['id']}: remediation.contrast required")

        recall = r.get("recall", {})
        if not str(recall.get("prompt","")).strip():
            fail(f"{q['id']}: remediation.recall.prompt required")
        if not isinstance(recall.get("answers"), list) or not recall["answers"]:
            fail(f"{q['id']}: remediation.recall.answers required")

        similar = r.get("similar", {})
        if not str(similar.get("question","")).strip():
            fail(f"{q['id']}: remediation.similar.question required")
        if not isinstance(similar.get("choices"), list) or len(similar["choices"]) != 4:
            fail(f"{q['id']}: remediation.similar requires 4 choices")
        if similar.get("answer") not in (1,2,3,4):
            fail(f"{q['id']}: remediation.similar.answer must be 1..4")
        if not str(similar.get("explanation","")).strip():
            fail(f"{q['id']}: remediation.similar.explanation required")

        ns = normalize_text(similar.get("question",""))
        if ns in seen_similar_texts:
            fail(f"duplicate similar question text: {q['id']} == {seen_similar_texts[ns]}")
        seen_similar_texts[ns] = q["id"]

print(f"[OK] {len(seen_ids)} daily questions validated; default={default_count}, max={max_count}")
