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
if manifest.get("questionsPerDay") != 5:
    fail("questionsPerDay must be 5")

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
    qs = obj.get("questions")
    if not isinstance(qs, list) or len(qs) != 5:
        fail(f"{path.name}: exactly 5 questions required")
    for q in qs:
        required = ["id","question","choices","answer","explanation","source","point"]
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

print(f"[OK] {len(seen_ids)} daily questions validated")
