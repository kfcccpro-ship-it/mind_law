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
if manifest.get("questionsPerDay") != 20:
    fail("questionsPerDay must be 20")

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
    if not isinstance(qs, list) or len(qs) != 20:
        fail(f"{path.name}: exactly 20 questions required")
    for q in qs:
        required = ["id","question","choices","answer","explanation","source","point","remediation"]
        missing = [k for k in required if k not in q]
        if missing:
            fail(f"{path.name}: {q.get('id','?')} missing {missing}")
        if q["id"] in seen_ids:
            fail(f"duplicate id: {q['id']}")
        seen_ids.add(q["id"])
        if not isinstance(q["choices"], list) or len(q["choices"]) != 4:
            fail(f"{q['id']}: exactly 4 choices required")
        if q["answer"] not in (1,2,3,4):
            fail(f"{q['id']}: answer must be 1..4")
        if not str(q["explanation"]).strip() or not str(q["source"]).strip():
            fail(f"{q['id']}: explanation/source required")
        rem = q["remediation"]
        for k in ("detail","recall","similar"):
            if k not in rem:
                fail(f"{q['id']}: remediation.{k} required")
        recall = rem["recall"]
        if not recall.get("prompt") or not isinstance(recall.get("answers"), list) or not recall["answers"]:
            fail(f"{q['id']}: valid remediation.recall required")
        sim = rem["similar"]
        for k in ("question","choices","answer","explanation"):
            if k not in sim:
                fail(f"{q['id']}: remediation.similar.{k} required")
        if not isinstance(sim["choices"], list) or len(sim["choices"]) != 4 or sim["answer"] not in (1,2,3,4):
            fail(f"{q['id']}: similar question must be 4-choice with answer 1..4")

print(f"[OK] {len(seen_ids)} daily questions validated")
