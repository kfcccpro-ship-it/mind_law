#!/usr/bin/env python3
from pathlib import Path
import re, sys
src=Path(sys.argv[1]).read_text(encoding='utf-8')
scripts=re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',src,flags=re.S|re.I)
Path(sys.argv[2]).write_text('\n'.join(scripts),encoding='utf-8')
print(f'extracted {len(scripts)} inline script block(s)')