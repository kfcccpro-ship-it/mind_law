#!/usr/bin/env python3
import json
from pathlib import Path
from build import validate
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'course.json').read_text(encoding='utf-8'))
cards=validate(data)
print(f'OK: {cards} cards validated')