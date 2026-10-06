#!/usr/bin/env python3
import json, pathlib, sys, math, re, datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "daily_questions"

def fail(msg):
    print(f"[FAIL] {msg}")
    sys.exit(1)

manifest_path = DATA / "manifest.json"
if not manifest_path.exists():
    fail("manifest.json missing")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

days = int(manifest.get("days", 0))
if days < 1:
    fail("manifest.days must be positive")
try:
    datetime.date.fromisoformat(manifest.get("launchDate",""))
except Exception:
    fail("launchDate must be YYYY-MM-DD")
if manifest.get("releaseMode") != "manual_flexible":
    fail("releaseMode must be manual_flexible")

default_count = int(manifest.get("defaultQuestionsPerSet", 20))
max_count = int(manifest.get("maxQuestionsPerSet", 60))
if default_count < 1 or max_count < default_count:
    fail("invalid default/max question counts")

if (ROOT / ".daily_staging").exists():
    fail(".daily_staging must not exist in public main")
legacy = sorted(p.name for p in DATA.glob("20??-??-??.json"))
if legacy:
    fail(f"legacy date-named DAY files are not allowed: {legacy}")

TRACK_SUBJECTS = {
    "법·감독·정관·선거": {"새마을금고법","새마을금고법 시행령","새마을금고법 시행규칙","감독기준","감독기준 시행세칙","정관","선거"},
    "여신": {"여신"},
    "수신·출자": {"수신","출자"},
    "AML·세무·공제": {"자금세탁방지","AML","세무","공제"},
    "새마을금고론": {"새마을금고론"},
    "인사·복무·직제·내부통제": {"인사","복무","직제","내부통제","개인정보보호","사업계획·예산","보수","퇴직급여","감사"},
}
def track_for_subject(subject):
    for track, subjects in TRACK_SUBJECTS.items():
        if subject in subjects:
            return track
    return None

plan = manifest.get("plan", [])
plan_by_day = {}
for x in plan:
    d=int(x.get("day",0))
    if d<1 or d>days or d in plan_by_day:
        fail(f"invalid/duplicate plan day: {d}")
    plan_by_day[d]=x

published = manifest.get("publishedDays", [])
if not isinstance(published,list):
    fail("publishedDays must be a list")
pub_by_day={}
pub_files=set()
for e in published:
    if not isinstance(e,dict):
        fail("publishedDays entries must be objects")
    d=int(e.get("day",0)); f=str(e.get("file",""))
    if d<1 or d>days or d in pub_by_day:
        fail(f"invalid/duplicate published day: {d}")
    if not re.fullmatch(r"day-\d{2}\.json", f):
        fail(f"invalid published file name: {f}")
    pub_by_day[d]=e; pub_files.add(f)

active=manifest.get("activeDay")
if active is not None and int(active) not in pub_by_day:
    fail("activeDay must be null or one of publishedDays")

disk_files={p.name for p in DATA.glob("day-??.json")}
if disk_files != pub_files:
    fail(f"published file list mismatch: manifest={sorted(pub_files)}, disk={sorted(disk_files)}")

seen_ids=set(); seen_q={}; seen_sim={}
def norm(v):
    return re.sub(r"[^0-9A-Za-z가-힣]+","",str(v)).lower()
def check_dist(name, answers, label):
    counts=[answers.count(i) for i in (1,2,3,4)]
    total=len(answers)
    expected=total/4
    tolerance=max(2, math.ceil(total*0.15))
    if min(counts)==0:
        fail(f"{name}: {label} answer position missing; counts={counts}")
    if max(abs(c-expected) for c in counts)>tolerance:
        fail(f"{name}: {label} answer positions too skewed; counts={counts}")

for d in sorted(pub_by_day):
    e=pub_by_day[d]
    path=DATA/e["file"]
    if not path.exists():
        fail(f"published file missing: {e['file']}")
    obj=json.loads(path.read_text(encoding="utf-8"))
    if int(obj.get("day",0))!=d:
        fail(f"{path.name}: day mismatch")
    p=plan_by_day.get(d,{})
    expected=int(p.get("questionCount", default_count))
    if expected>max_count:
        fail(f"{path.name}: expected count exceeds max")
    qs=obj.get("questions")
    if not isinstance(qs,list) or len(qs)!=expected:
        fail(f"{path.name}: exactly {expected} questions required")

    if p.get("mode") in ("mixed_set","mixed_daily"):
        declared=obj.get("trackCounts")
        if not isinstance(declared,dict) or sum(int(v) for v in declared.values())!=expected:
            fail(f"{path.name}: valid trackCounts required")
        actual={k:0 for k in TRACK_SUBJECTS}
        run_key=None; run_len=0
        for q in qs:
            sc=q.get("scope",{}); subject=str(sc.get("subject","")).strip()
            tr=track_for_subject(subject)
            if not tr: fail(f"{path.name}: unmapped subject {subject!r}")
            actual[tr]+=1
            key=(subject,sc.get("unit"))
            run_len=run_len+1 if key==run_key else 1; run_key=key
            if run_len>3: fail(f"{path.name}: >3 consecutive same subject+unit")
        if set(declared)!=set(actual):
            fail(f"{path.name}: trackCounts keys mismatch")
        for k,v in actual.items():
            if int(declared.get(k,-1))!=v or v<1:
                fail(f"{path.name}: trackCounts mismatch/zero for {k}")

    check_dist(path.name,[q.get("answer") for q in qs],"base")
    check_dist(path.name,[q.get("remediation",{}).get("similar",{}).get("answer") for q in qs],"similar")

    for q in qs:
        req=["id","question","choices","answer","explanation","source","sourceVersion","sourceExcerpt","point","remediation"]
        miss=[k for k in req if k not in q]
        if miss: fail(f"{path.name}: {q.get('id','?')} missing {miss}")
        qid=q["id"]
        if qid in seen_ids: fail(f"duplicate id: {qid}")
        seen_ids.add(qid)
        nq=norm(q["question"])
        if nq in seen_q: fail(f"duplicate question: {qid} == {seen_q[nq]}")
        seen_q[nq]=qid
        if len(q["choices"])!=4 or q["answer"] not in (1,2,3,4): fail(f"{qid}: invalid base choices/answer")
        sc=q.get("scope",{})
        for k in ("subject","unit","chapter","part"):
            if not str(sc.get(k,"")).strip(): fail(f"{qid}: scope.{k} required")
        r=q["remediation"]
        for k in ("detail","why","rule","contrast"):
            if not str(r.get(k,"")).strip(): fail(f"{qid}: remediation.{k} required")
        recall=r.get("recall",{})
        if not str(recall.get("prompt","")).strip() or not isinstance(recall.get("answers"),list) or not recall["answers"]:
            fail(f"{qid}: recall invalid")
        sim=r.get("similar",{})
        if not str(sim.get("question","")).strip() or not isinstance(sim.get("choices"),list) or len(sim["choices"])!=4 or sim.get("answer") not in (1,2,3,4) or not str(sim.get("explanation","")).strip():
            fail(f"{qid}: similar invalid")
        ns=norm(sim["question"])
        if ns in seen_sim: fail(f"duplicate similar: {qid} == {seen_sim[ns]}")
        seen_sim[ns]=qid

if not published:
    print(f"[OK] prelaunch mode; launchDate={manifest['launchDate']}; no DAY question files published")
else:
    print(f"[OK] {len(published)} DAY sets / {len(seen_ids)} questions validated; activeDay={active}")
