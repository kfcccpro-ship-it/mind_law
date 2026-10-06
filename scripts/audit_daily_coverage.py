#!/usr/bin/env python3
import json, pathlib, re, collections, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/"daily_questions"
manifest=json.loads((DATA/"manifest.json").read_text(encoding="utf-8"))
published=manifest.get("publishedDays",[])
if not published:
    print(f"[OK] prelaunch/manual mode; no published DAY sets; launchDate={manifest.get('launchDate')}")
    sys.exit(0)

TRACK_SUBJECTS={
 "법·감독·정관·선거":{"새마을금고법","새마을금고법 시행령","새마을금고법 시행규칙","감독기준","감독기준 시행세칙","정관","선거"},
 "여신":{"여신"},"수신·출자":{"수신","출자"},"AML·세무·공제":{"자금세탁방지","AML","세무","공제"},
 "새마을금고론":{"새마을금고론"},
 "인사·복무·직제·내부통제":{"인사","복무","직제","내부통제","개인정보보호","사업계획·예산","보수","퇴직급여","감사"}
}
def norm(s): return re.sub(r"[^0-9A-Za-z가-힣]+","",str(s)).lower()
def track(subject):
    for n,ss in TRACK_SUBJECTS.items():
        if subject in ss:return n
    return "미분류"

base_seen={};sim_seen={};scope_days=collections.defaultdict(list);all_tracks=collections.Counter();all_subjects=collections.Counter();warnings=[]
for entry in sorted(published,key=lambda x:int(x["day"])):
    path=DATA/entry["file"];obj=json.loads(path.read_text(encoding="utf-8"));qs=obj.get("questions",[])
    bp=collections.Counter(q.get("answer") for q in qs);sp=collections.Counter(q.get("remediation",{}).get("similar",{}).get("answer") for q in qs)
    dt=collections.Counter()
    for q in qs:
        qid=q.get("id","?");nq=norm(q.get("question",""));ns=norm(q.get("remediation",{}).get("similar",{}).get("question",""))
        if nq in base_seen: print(f"[FAIL] exact base duplicate: {qid} == {base_seen[nq]}");sys.exit(1)
        if ns in sim_seen: print(f"[FAIL] exact similar duplicate: {qid} == {sim_seen[ns]}");sys.exit(1)
        base_seen[nq]=qid;sim_seen[ns]=qid
        sc=q.get("scope",{});subject=sc.get("subject","");tr=track(subject);dt[tr]+=1;all_tracks[tr]+=1;all_subjects[subject]+=1
        scope_days[(subject,sc.get("unit",""),sc.get("chapter",""),sc.get("part",""))].append(int(obj["day"]))
    print(f"[DAY {int(obj['day']):02d}] questions={len(qs)}")
    print("      tracks="+", ".join(f"{k}:{v}" for k,v in dt.items()))
    print("      base-answer-pos="+"/".join(str(bp.get(i,0)) for i in range(1,5)))
    print("      similar-answer-pos="+"/".join(str(sp.get(i,0)) for i in range(1,5)))
for key,ds in scope_days.items():
    u=sorted(set(ds))
    if len(u)>=3:warnings.append(f"scope repeated on {len(u)} DAYs: {' > '.join(key)} :: {u}")
print("[CUMULATIVE] tracks="+", ".join(f"{k}:{v}" for k,v in all_tracks.items()))
print("[CUMULATIVE] subjects="+", ".join(f"{k}:{v}" for k,v in all_subjects.items()))
for w in warnings: print("[WARN] "+w)
print(f"[OK] audited {len(published)} published DAY sets / {len(base_seen)} base questions")
