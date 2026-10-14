"""Build a Markdown blog. Only explicitly published content enters _site."""
from pathlib import Path
import json, re, html, shutil, argparse
from datetime import date
from urllib.parse import urlparse,parse_qs,quote
from xml.sax.saxutils import escape
import markdown
ROOT=Path(__file__).resolve().parents[1]
config=json.loads((ROOT/'config.json').read_text())
parser=argparse.ArgumentParser();parser.add_argument('--output',default='_site');args=parser.parse_args()
DEST=ROOT/args.output
if DEST.resolve()==ROOT.resolve() or ROOT.resolve() not in DEST.resolve().parents:raise ValueError('Output must be a subdirectory')
if DEST.exists(): shutil.rmtree(DEST)
DEST.mkdir(parents=True,exist_ok=True)
base=config['base_path'].rstrip('/')
def url(p):return base+'/'+p.lstrip('/')
def esc(s):return html.escape(str(s),quote=True)
posts=[]
for f in (ROOT/'content').glob('*.md'):
 raw=f.read_text();match=re.fullmatch(r'---(?:json)?\n(.*?)\n---\n(.*)',raw,re.S)
 if not match:raise ValueError(f'Invalid front matter: {f}')
 meta=json.loads(match[1]);meta['body']=match[2]
 if meta.get('status')!='published':continue
 if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',meta['slug']):raise ValueError('Use lowercase URL slugs')
 if meta.get('date'):date.fromisoformat(meta['date'])
 meta['html']=markdown.markdown(meta['body'],extensions=['extra','sane_lists','toc']).replace('<img ', '<img loading="lazy" decoding="async" ')
 meta['html']=re.sub(r'(src|href)="/assets/',lambda m:m[1]+'="'+url('assets/'),meta['html'])
 text=re.sub('<[^>]+>',' ',meta['html']);text=html.unescape(re.sub(r'\s+',' ',text)).strip()
 meta['excerpt']=meta.get('description') or (text[:155]+'…' if len(text)>155 else text)
 meta['minutes']=max(1,round((len(re.findall(r'[\u4e00-\u9fff]',text))/450+len(re.findall(r'\b[a-zA-Z]+\b',text))/220)))
 meta['lang']='zh-Hans' if len(re.findall(r'[\u4e00-\u9fff]',text))>len(re.findall(r'[a-zA-Z]',text))/3 else 'en'
 posts.append(meta)
assert len({p['slug'] for p in posts})==len(posts),'Duplicate slug'
posts.sort(key=lambda p:(p.get('date') or '',p['title']),reverse=True)
articles=[p for p in posts if p['kind']=='article'];songs=[p for p in posts if p['kind']=='song']
def page(title,body,path='',active='',description=None,lang='en'):
 canonical=config['url'].rstrip('/')+url(path)
 nav=''.join(f'<a href="{url(p)}"'+(' aria-current="page"' if active==name else '')+f'>{name}</a>' for name,p in [('Writing','writing/'),('Music','music/'),('About','about/')])
 doc=f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} · {esc(config['title'])}</title><meta name="description" content="{esc(description or config['description'])}"><link rel="canonical" href="{esc(canonical)}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description or config['description'])}"><meta property="og:url" content="{esc(canonical)}"><link rel="icon" href="{url('assets/favicon.svg')}" type="image/svg+xml"><link rel="stylesheet" href="{url('assets/style.css')}"><link rel="alternate" type="application/rss+xml" title="All Undiscovered" href="{url('feed.xml')}"></head><body><a class="skip" href="#main">Skip to content</a><header><a class="brand" href="{url('')}">ALL UNDISCOVERED</a><nav aria-label="Main navigation">{nav}</nav></header><main id="main">{body}</main><footer><span>© Ming Yuan · ALL UNDISCOVERED</span><div class="social"><a href="{url('feed.xml')}">RSS</a><a href="https://soundcloud.com/ming_y">SoundCloud</a><a href="https://www.youtube.com/@ming_y_my">YouTube</a><a href="mailto:my1219share@gmail.com">Get in touch ↗</a></div></footer><script src="{url('assets/filter.js')}" defer></script></body></html>'''
 dest=DEST/path/'index.html';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(doc)
def rows(items):
 return '<ul class="rows">'+''.join(f'''<li class="row" data-topic="{esc(p['topic'])}"><a href="{url(p['slug']+'/')}"><div><span class="eyebrow">{esc(p['topic'])} · {p['minutes']} min read{(' · '+esc(p['date'])) if p.get('date') else ''}</span><h3 lang="{p['lang']}">{esc(p['title'])}</h3><p lang="{p['lang']}">{esc(p['excerpt'])}</p></div><span class="arrow" aria-hidden="true">↗</span></a></li>''' for p in items)+'</ul>'
def cards(items):return '<div class="music-grid">'+''.join(f'''<a class="music-card" href="{url(p['slug']+'/')}"><span class="music-mark" aria-hidden="true">♪</span><div><span class="eyebrow">Original music</span><h3>{esc(p['title'].replace('Album | ','').replace(' (for solo piano)',''))}</h3><p>{esc(p['excerpt'])}</p></div></a>''' for p in items)+'</div>'
featured=[next(p for p in articles if p['slug']==s) for s in ['thelyinglifeofadults','tristanandisolde','charleychinaman']]
page('Home',f'''<section class="hero"><span class="eyebrow">Ming Yuan · The PNW Witch</span><h1>All undiscovered.</h1><p>A place for articles and songs.<br>For paying attention, following a thought,<br>and finding a language of my own.</p><div class="links"><a href="{url('writing/')}">Explore the writing ↗</a><a href="{url('music/')}">Listen to the music ↗</a></div></section><section><div class="section-head"><h2>A few places to begin</h2><a href="{url('writing/')}">All writing →</a></div>{rows(featured)}</section><section><div class="section-head"><h2>In another language</h2><a href="{url('music/')}">All music →</a></div>{cards([next(p for p in songs if p['slug']==s) for s in ['its-time-to-dance','flowing-on-the-stream','tunnel']])}</section>''')
options=''.join(f'<option>{esc(t)}</option>' for t in sorted({p['topic'] for p in articles}))
page('Writing',f'''<div class="page-title"><span class="eyebrow">The written archive</span><h1>Writing</h1><p class="intro">Books, culture, technology, and translation. In English and 中文.</p></div><div class="controls"><input id="search" type="search" aria-label="Search writing" placeholder="Find a title or a thought…"><select id="topic" aria-label="Filter by topic"><option value="">All topics</option>{options}</select></div><p id="result-count" class="meta" aria-live="polite">{len(articles)} pieces</p>{rows(articles)}<p class="empty" id="empty" hidden>No writing matches. Try another word or topic.</p>''','writing/','Writing')
page('Music',f'''<div class="page-title"><span class="eyebrow">Songs, piano & soundtracks</span><h1>Music</h1><p class="intro">Another way to tell a story. Original compositions, with recordings, lyrics, and the notes behind them.</p></div>{cards(songs)}''','music/','Music')
page('About',f'''<article class="reading"><span class="eyebrow">The PNW Witch</span><h1>About this place</h1><div class="prose"><p>I'm Ming Yuan. ALL UNDISCOVERED is my home for articles and songs.</p><p>I write in English and Chinese, about books, culture, technology, and the things that stay with me. I also compose songs, piano pieces, and soundtracks.</p><blockquote>I required a different language, one that was for me a place of affection and reflection.<br>— Antonio Tabucchi</blockquote><p><a href="mailto:my1219share@gmail.com">Get in touch</a> · <a href="https://github.com/mingyuan1219">GitHub</a> · <a href="https://x.com/mingy_my">X</a></p></div></article>''','about/','About')
for p in posts:
 players=''
 for n,src in enumerate(p.get('players',[]),1):
  if urlparse(src).hostname!='w.soundcloud.com':raise ValueError('Unknown music embed')
  track=p.get('recording_links',[])[n-1] if len(p.get('recording_links',[]))>=n else 'https://soundcloud.com/ming_y'
  label='Open recording on SoundCloud ↗' if track!='https://soundcloud.com/ming_y' else 'Visit Ming on SoundCloud ↗'
  players+=f'<div><iframe src="{esc(src)}" title="{esc(p["title"])} recording {n}" loading="lazy" allow="autoplay" referrerpolicy="strict-origin-when-cross-origin"></iframe><a class="player-fallback" href="{esc(track)}">{label}</a></div>'
 active='Music' if p['kind']=='song' else 'Writing';back='music/' if active=='Music' else 'writing/'
 body=f'''<article class="reading"><a class="back" href="{url(back)}">← {active}</a><p class="eyebrow">{esc(p['topic'])}{(' · '+p['date']) if p.get('date') else ''}{(' · '+str(p['minutes'])+' min read') if p['kind']=='article' else ''}</p><h1>{esc(p['title'])}</h1>{('<div class="players">'+players+'</div>') if players else ''}<div class="prose">{p['html']}</div></article>'''
 page(p['title'],body,p['slug']+'/',active,p['excerpt'],p['lang'])
page('Page not found',f'<div class="hero"><h1>A path undiscovered.</h1><p>This page could not be found.</p><a href="{url("")}">Return home →</a></div>','404/')
shutil.copyfile(DEST/'404/index.html',DEST/'404.html')
aliases={a:p['slug']+'/' for p in posts for a in p.get('aliases',[])}
aliases.update({'writings/':'writing/','translation/':'writing/','projects/':'music/','archives/':'writing/','page/2/':'writing/'})
for old,target in aliases.items():
    if '..' in old or old.startswith('/'):raise ValueError('Unsafe alias')
    dest=DEST/old/'index.html';dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url={esc(url(target))}"><link rel="canonical" href="{esc(config["url"].rstrip("/")+url(target))}"><title>Page moved</title></head><body><a href="{esc(url(target))}">Continue to the article</a></body></html>')
shutil.copytree(ROOT/'assets',DEST/'assets',dirs_exist_ok=True)
(DEST/'.nojekyll').touch()
items=''.join(f'<item><title>{escape(p["title"])}</title><link>{escape(config["url"].rstrip("/")+url(p["slug"]+"/"))}</link><guid>{escape(config["url"].rstrip("/")+url(p["slug"]+"/"))}</guid><description>{escape(p["excerpt"])}</description></item>' for p in posts)
(DEST/'feed.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>ALL UNDISCOVERED</title><link>{escape(config["url"]+base+"/")}</link><description>{escape(config["description"])}</description>{items}</channel></rss>')
paths=['','writing/','music/','about/']+[p['slug']+'/' for p in posts]
shutil.copyfile(DEST/'feed.xml',DEST/'atom.xml')
(DEST/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+escape(config['url'].rstrip('/')+url(p))+'</loc></url>' for p in paths)+'</urlset>')
(DEST/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+config['url'].rstrip('/')+url('sitemap.xml')+'\n')
print(f'Built {len(articles)} articles, {len(songs)} music pages into {DEST}')
