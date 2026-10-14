from pathlib import Path
import argparse,json,re
from datetime import date
p=argparse.ArgumentParser();p.add_argument('slug');p.add_argument('title');p.add_argument('--kind',choices=['article','song'],default='article');p.add_argument('--topic',default='Reflections');a=p.parse_args()
if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',a.slug):p.error('Use a lowercase slug, e.g. returning-to-writing')
f=Path(__file__).resolve().parents[1]/'content'/f'{a.slug}.md'
if f.exists():p.error('A file with this slug already exists')
meta={'title':a.title,'slug':a.slug,'kind':a.kind,'topic':a.topic,'status':'draft','date':date.today().isoformat(),'description':'','players':[]}
f.write_text('---\n'+json.dumps(meta,ensure_ascii=False,indent=2)+'\n---\n\nWrite here.\n')
print(f)
