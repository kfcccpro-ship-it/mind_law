from pathlib import Path
import json
D="2026-10-02"
S=Path(".daily_staging")/D
rows=[json.loads(p.read_text(encoding="utf-8")) for p in sorted(S.glob("q*.json"))]
qs=[]
for x in rows:
    qs.append({"id":x["id"],"scope":{"subject":x["sc"][0],"unit":x["sc"][1],"chapter":x["sc"][2],"part":x["sc"][3]},"question":x["q"],"choices":x["c"],"answer":x["a"],"explanation":x["e"],"source":x["s"],"sourceVersion":x["sv"],"sourceExcerpt":x["se"],"point":x["p"],"remediation":{"detail":x["e"],"why":x["w"],"rule":x["r"],"contrast":x["ct"],"sourceExcerpt":x["se"],"recall":{"prompt":x["rp"],"answers":x["ra"]},"similar":{"question":x["sq"],"choices":x["scs"],"answer":x["sa"],"explanation":x["sx"]}}})
meta=json.loads((S/"meta.json").read_text(encoding="utf-8"))
meta["questions"]=qs
mp=Path("daily_questions/manifest.json")
m=json.loads(mp.read_text(encoding="utf-8"))
plan=next(p for p in m["plan"] if p["date"]==D)
expected=int(plan.get("questionCount",m.get("defaultQuestionsPerDay",20)))
assert len(qs)==expected
assert expected<=int(m.get("maxQuestionsPerDay",60))
Path("daily_questions/"+D+".json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
m["latest"]=D
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("assembled",D,len(qs))
