#!/usr/bin/env python3
import json, pathlib, re, collections, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "daily_questions"

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

def norm(s):
    return re.sub(r"[^0-9A-Za-z가-힣]+", "", str(s)).lower()

def track(subject):
    for name, subjects in TRACK_SUBJECTS.items():
        if subject in subjects:
            return name
    return "미분류"

files = sorted(DATA.glob("20??-??-??.json"))
if not files:
    print("[FAIL] no DAILY files")
    sys.exit(1)

base_seen = {}
sim_seen = {}
scope_days = collections.defaultdict(list)
all_tracks = collections.Counter()
all_subjects = collections.Counter()
warnings = []

for path in files:
    obj = json.loads(path.read_text(encoding="utf-8"))
    qs = obj.get("questions", [])
    base_pos = collections.Counter(q.get("answer") for q in qs)
    sim_pos = collections.Counter(q.get("remediation", {}).get("similar", {}).get("answer") for q in qs)
    day_tracks = collections.Counter()
    day_units = collections.Counter()

    for q in qs:
        qid = q.get("id","?")
        nq = norm(q.get("question",""))
        ns = norm(q.get("remediation", {}).get("similar", {}).get("question",""))
        if nq in base_seen:
            print(f"[FAIL] exact base-question duplicate: {qid} == {base_seen[nq]}")
            sys.exit(1)
        if ns in sim_seen:
            print(f"[FAIL] exact similar-question duplicate: {qid} == {sim_seen[ns]}")
            sys.exit(1)
        base_seen[nq] = qid
        sim_seen[ns] = qid

        sc = q.get("scope", {})
        subject = sc.get("subject","")
        unit = sc.get("unit","")
        chapter = sc.get("chapter","")
        part = sc.get("part","")
        tr = track(subject)
        day_tracks[tr] += 1
        all_tracks[tr] += 1
        all_subjects[subject] += 1
        day_units[(subject,unit)] += 1
        scope_days[(subject,unit,chapter,part)].append(obj.get("date"))

    print(f"[DAY] {obj.get('date')}  questions={len(qs)}")
    print("      tracks=" + ", ".join(f"{k}:{v}" for k,v in day_tracks.items()))
    print("      base-answer-pos=" + "/".join(str(base_pos.get(i,0)) for i in range(1,5)))
    print("      similar-answer-pos=" + "/".join(str(sim_pos.get(i,0)) for i in range(1,5)))

for scope_key, dates in scope_days.items():
    unique = sorted(set(dates))
    if len(unique) >= 3:
        warnings.append(f"scope repeated on {len(unique)} days: {' > '.join(scope_key)} :: {', '.join(unique)}")

print("[CUMULATIVE] tracks=" + ", ".join(f"{k}:{v}" for k,v in all_tracks.items()))
print("[CUMULATIVE] subjects=" + ", ".join(f"{k}:{v}" for k,v in all_subjects.items()))
if warnings:
    print("[WARN] repeated scopes requiring intentional-review check:")
    for w in warnings:
        print("       " + w)
else:
    print("[OK] no scope repeated across 3+ distinct DAILY dates")
print(f"[OK] audited {len(files)} DAILY files / {len(base_seen)} base questions")
