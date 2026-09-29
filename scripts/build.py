#!/usr/bin/env python3
from pathlib import Path
import json, sys, re
ROOT=Path(__file__).resolve().parents[1]
COURSE=ROOT/'course.json'; TEMPLATE=ROOT/'src/app.template.html'; OUT=ROOT/'index.html'

def validate(data):
    errors=[]
    meta=data.get('meta',{})
    for k in ('id','title','subtitle'):
        if not meta.get(k): errors.append(f'meta.{k} missing')
    branches=data.get('branches')
    if not isinstance(branches,list) or not branches: errors.append('branches missing')
    legal_texts=data.get('legalTexts')
    if not isinstance(legal_texts,dict) or not legal_texts: errors.append('legalTexts missing')
    ids=set(); cards=0
    def addid(x,kind):
        i=x.get('id')
        if not i or not re.fullmatch(r'[A-Za-z0-9._-]+',i): errors.append(f'invalid {kind} id: {i!r}')
        elif i in ids: errors.append(f'duplicate id: {i}')
        else: ids.add(i)
    for b in branches or []:
        addid(b,'branch')
        cats=b.get('c')
        if not isinstance(cats,list) or not cats: errors.append(f"{b.get('id')}: categories missing"); continue
        for cat in cats:
            addid(cat,'category')
            nodes=cat.get('c')
            if not isinstance(nodes,list) or not nodes: errors.append(f"{cat.get('id')}: cards missing"); continue
            for n in nodes:
                cards+=1; addid(n,'card')
                c=n.get('card',{})
                if not isinstance(c.get('s'),list) or not c.get('s'): errors.append(f"{n.get('id')}: card.s missing")
                if not c.get('e'): errors.append(f"{n.get('id')}: card.e missing")
                if not c.get('l'): errors.append(f"{n.get('id')}: legal/source reference missing")
                recall=c.get('recall')
                if not isinstance(recall,list) or len(recall)<2:
                    errors.append(f"{n.get('id')}: recall needs at least 2 ANKI items")
                else:
                    for ri,item in enumerate(recall):
                        if not item.get('prompt') or not item.get('answer'):
                            errors.append(f"{n.get('id')}: recall[{ri}] missing prompt/answer")
                            continue
                        answer=str(item.get('answer','')).strip()
                        if re.fullmatch(r'제\\s*\\d+(?:조(?:의\\d+)?|항|호)(?:제?\\d+(?:항|호))*',answer):
                            errors.append(f"{n.get('id')}: recall[{ri}] must test a concept, not a bare article number ({answer})")
                law_keys=c.get('lawKeys')
                if not isinstance(law_keys,list) or not law_keys:
                    errors.append(f"{n.get('id')}: lawKeys missing")
                else:
                    for key in law_keys:
                        if key not in (legal_texts or {}): errors.append(f"{n.get('id')}: unknown law key {key}")
    if cards!=32: errors.append(f'expected 32 cards, got {cards}')
    if errors: raise SystemExit('VALIDATION FAILED\n- '+'\n- '.join(errors))
    return cards

def render():
    data=json.loads(COURSE.read_text(encoding='utf-8')); validate(data)
    template=TEMPLATE.read_text(encoding='utf-8')
    if template.count('__COURSE_JSON__')!=1: raise SystemExit('template must contain one __COURSE_JSON__ token')
    js=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    return template.replace('__COURSE_JSON__',js)

if __name__=='__main__':
    html=render()
    if '--check' in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding='utf-8')!=html:
            raise SystemExit('index.html is out of date. Run: python3 scripts/build.py')
        print('OK: source validated and index.html is current')
    else:
        OUT.write_text(html,encoding='utf-8')
        print(f'Built {OUT}')