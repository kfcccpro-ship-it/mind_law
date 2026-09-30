#!/usr/bin/env python3
import json, pathlib, sys, datetime

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

plan_by_date = {x["date"]: x for x in manifest.get("plan", [])}
latest = manifest.get("latest")
try:
    datetime.date.fromisoformat(latest)
except Exception:
    fail("latest must be YYYY-MM-DD")

seen_ids = set()
for path in sorted(DATA.glob("20??-??-??.json")):
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

    for q in qs:
        required = ["id","question","choices","answer","explanation","source","point","remediation"]
        missing = [k for k in required if k not in q]
        if missing:
            fail(f"{path.name}: {q.get('id','?')} missing {missing}")
        if q["id"] in seen_ids:
            fail(f"duplicate id: {q['id']}")
        seen_ids.add(q["id"])
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

print(f"[OK] {len(seen_ids)} daily questions validated; default={default_count}, max={max_count}")
