"""Check built pages, internal routes, assets, feeds, and draft exclusion."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse,unquote
import json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];site=ROOT/'_site';cfg=json.loads((ROOT/'config.json').read_text());base=cfg['base_path'].rstrip('/')
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  for attr in ['href','src']:
   if d.get(attr):self.links.append(d[attr])
errors=[]
for f in site.rglob('*.html'):
 p=Links();p.feed(f.read_text())
 for link in p.links:
  u=urlparse(link)
  if u.scheme or u.netloc or not u.path:continue
  path=unquote(u.path)
  if base and path.startswith(base+'/'):path=path[len(base):]
  target=site/path.lstrip('/') if path.startswith('/') else f.parent/path
  if target.is_dir():target=target/'index.html'
  if not target.exists():errors.append(str(f.relative_to(site))+': '+link)
for f in (ROOT/'content').glob('*.md'):
 m=re.fullmatch(r'---(?:json)?\n(.*?)\n---\n(.*)',f.read_text(),re.S);meta=json.loads(m[1]);exists=(site/meta['slug']/'index.html').exists()
 if exists != (meta['status']=='published'):errors.append('Publication state mismatch: '+f.name)
for name in ['feed.xml','sitemap.xml','atom.xml']:ET.parse(site/name)
if errors:raise SystemExit('\n'.join(errors))
print('PASS: internal routes, image/script assets, XML feeds and publication states')
