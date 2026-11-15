#!/usr/bin/env python3
"""Construye search/index.json con los títulos de los artículos de todas las webs de la red.

Lee robots.txt / sitemaps de cada dominio, recoge las URL y obtiene el <title> de cada página.
Guarda una caché (search/cache.json) para no volver a descargar páginas que no han cambiado.
Solo usa la biblioteca estándar de Python.
"""
import concurrent.futures as cf, gzip, html, io, json, os, re, sys, time, urllib.parse, urllib.request
import shutil, unicodedata
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'search', 'meta.json')
SHARDS = os.path.join(ROOT, 'search', 's')
CACHE = os.path.join(ROOT, 'search', 'cache.json')
UA = 'EnciclopediasSiIndexer/1.0 (+https://enciclopedias.si/)'
SITES = [
 ('classicapedia.com','Classicapedia'),('pinacopedia.com','Pinacopedia'),('filopedia.com','Filopedia'),
 ('cinematopedia.com','Cinematopedia'),('mythicapedia.com','Mythicapedia'),('newtonpedia.com','Newtonpedia'),
 ('medicapedia.org','Medicapedia'),('psycholopedia.com','Psycholopedia'),('escolapedia.com','Escolapedia'),
 ('leypedia.com','Leypedia'),('culinapedia.com','Culinapedia'),('worldwinepedia.com','WorldWinepedia'),
 ('tenispedia.com','Tenispedia'),('ludicopedia.com','Ludicopedia'),('catdogpedia.com','CatDogpedia'),
 ('iapedia.si','IApedia'),('farmacos.ai','Farmacos.ai'),('enfermeria.si','Enfermería Sí'),
 ('saberinvertir.si','Saber Invertir'),('celebraciones.org','Celebraciones'),
 ('sustainablefashionfest.com','Sustainable Fashion Fest'),('modasostenible.es','Moda Sostenible'),
 ('zodiacopedia.com','Zodiacopedia'),('sitges.si','Sitges'),('santperederibes.si','Sant Pere de Ribes'),
 ('castelldefels.si','Castelldefels'),('vilanova.si','Vilanova i la Geltrú'),('santcugat.si','Sant Cugat'),
 ('garraf.si','Garraf'),('eivissa.si','Eivissa y Formentera'),('planetpedia.net','Planetpedia'),
]
MAX_URLS_PER_SITE = int(os.environ.get('MAX_URLS_PER_SITE', '100000'))
MAX_FETCH_PER_RUN = int(os.environ.get('MAX_FETCH_PER_RUN', '300000'))   # páginas nuevas por ejecución
TIME_BUDGET = int(os.environ.get('TIME_BUDGET', str(5 * 3600)))           # segundos
WORKERS = int(os.environ.get('WORKERS', '10'))
SKIP = re.compile(r'\.(jpe?g|png|gif|webp|svg|pdf|zip|mp3|mp4|xml|json|css|js)(\?|$)|/(wp-admin|wp-json|feed|tag|author|page/\d+|cart|checkout|my-account|aviso-legal|avis-legal|cookies|galetes|privacidad|privacitat|privacy|legal|politica)', re.I)
T0 = time.time()

def get(url, limit=None, timeout=25):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Encoding': 'gzip'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read(limit) if limit else r.read()
        if r.headers.get('Content-Encoding') == 'gzip' or url.endswith('.gz'):
            try: data = gzip.decompress(data)
            except Exception: pass
        return data, r.geturl()

def sitemaps_for(dom):
    found = []
    try:
        txt = get(f'https://{dom}/robots.txt', 200000)[0].decode('utf-8', 'ignore')
        found = [l.split(':', 1)[1].strip() for l in txt.splitlines() if l.lower().startswith('sitemap:')]
    except Exception: pass
    return found or [f'https://{dom}/sitemap.xml', f'https://{dom}/sitemap_index.xml', f'https://{dom}/wp-sitemap.xml']

def parse_sitemap(url, depth=0, seen=None):
    seen = seen if seen is not None else set()
    if url in seen or depth > 3: return []
    seen.add(url)
    try: data = get(url)[0]
    except Exception: return []
    try: root = ET.fromstring(data)
    except ET.ParseError: return []
    tag = root.tag.split('}')[-1]
    out = []
    for node in root:
        loc = lastmod = None
        for ch in node:
            n = ch.tag.split('}')[-1]
            if n == 'loc': loc = (ch.text or '').strip()
            elif n == 'lastmod': lastmod = (ch.text or '').strip()
        if not loc: continue
        if tag == 'sitemapindex': out += parse_sitemap(loc, depth + 1, seen)
        else: out.append((loc, lastmod or ''))
    return out

def lang_of(path):
    m = re.match(r'^/(en|ca|fr|de|it|pt)(/|$)', path)
    return m.group(1) if m else 'es'

TITLE = re.compile(rb'<title[^>]*>(.*?)</title>', re.I | re.S)
OGT = re.compile(rb'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)', re.I)
def clean_title(t, site_name):
    t = html.unescape(re.sub(r'\s+', ' ', t)).strip()
    parts = re.split(r'\s+[|·–—-]\s+', t)
    if len(parts) > 1:
        low = site_name.lower().split()[0]
        keep = [p for p in parts if low not in p.lower() and not re.search(r'pedia\b|\.si\b|\.com\b', p, re.I)]
        t = keep[0] if keep else parts[0]
    return t.strip()

def slug_title(path):
    seg = [s for s in path.split('/') if s]
    if not seg: return ''
    s = re.sub(r'\.(html?|php)$', '', seg[-1])
    s = re.sub(r'[-_]+', ' ', urllib.parse.unquote(s)).strip()
    return s[:1].upper() + s[1:]

def fetch_title(url, site_name):
    try:
        data, _ = get(url, 60000)
        m = OGT.search(data) or TITLE.search(data)
        if m: return clean_title(m.group(1).decode('utf-8', 'ignore'), site_name)
    except Exception: pass
    return None

def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')

STOP = set('de del la las el los en y e o u a al un una con por para the of and in on to for at des les le du et di da do dos das der die und von il lo per i'.split())

def shard_key(word):
    """Clave = primeras 3 letras de la palabra (o la palabra entera si tiene 2)."""
    if word in STOP: return None
    return word[:3]

def write_shards(items):
    """Un archivo por cada inicio de palabra (3 letras): el navegador solo descarga el que necesita."""
    shards = {}
    for it in items:
        keys = {shard_key(w) for w in re.split(r'[^a-z0-9]+', norm(it[0])) if len(w) >= 2}
        for k in keys:
            if k: shards.setdefault(k, []).append(it)
    shutil.rmtree(SHARDS, ignore_errors=True); os.makedirs(SHARDS)
    for k, lst in shards.items():
        json.dump(lst, open(os.path.join(SHARDS, k + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    old = os.path.join(ROOT, 'search', 'index.json')
    if os.path.exists(old): os.remove(old)
    json.dump({'generated': time.strftime('%Y-%m-%d'), 'count': len(items), 'sites': [[d, n] for d, n in SITES]},
              open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    big = max(shards.values(), key=len)
    print(f'{len(shards)} archivos de índice; el mayor tiene {len(big)} entradas', flush=True)

def main():
    cache = {}
    if os.path.exists(CACHE):
        try: cache = json.load(open(CACHE, encoding='utf-8'))
        except Exception: cache = {}
    items, newcache, fetched = [], {}, 0
    for si, (dom, name) in enumerate(SITES):
        urls = []
        for sm in sitemaps_for(dom):
            urls += parse_sitemap(sm)
            if urls: break
        seen, clean = set(), []
        for loc, lm in urls:
            p = urllib.parse.urlparse(loc)
            if p.netloc.replace('www.', '') != dom or SKIP.search(p.path) or loc in seen: continue
            seen.add(loc); clean.append((loc, lm))
        clean = clean[:MAX_URLS_PER_SITE]
        todo = [(l, lm) for l, lm in clean if not (l in cache and cache[l][1] == lm)]
        budget_ok = time.time() - T0 < TIME_BUDGET
        todo_fetch = todo[:max(0, MAX_FETCH_PER_RUN - fetched)] if budget_ok else []
        got = {}
        if todo_fetch:
            with cf.ThreadPoolExecutor(WORKERS) as ex:
                futs = {ex.submit(fetch_title, l, name): l for l, _ in todo_fetch}
                for f in cf.as_completed(futs):
                    got[futs[f]] = f.result()
                    if time.time() - T0 > TIME_BUDGET: break
        fetched += len(todo_fetch)
        for loc, lm in clean:
            p = urllib.parse.urlparse(loc)
            if loc in got and got[loc]: title, src = got[loc], 'page'
            elif loc in cache: title, src = cache[loc][0], cache[loc][2] if len(cache[loc]) > 2 else 'page'
            else: title, src = slug_title(p.path), 'slug'
            if not title: continue
            newcache[loc] = [title, lm if (loc in got and got[loc]) or loc in cache else '', src]
            path = p.path + (('?' + p.query) if p.query else '')
            items.append([title, si, path, lang_of(p.path)])
        print(f'{dom}: {len(clean)} urls, {len([l for l in got if got[l]])} títulos nuevos', flush=True)
    items.sort(key=lambda x: (x[0].lower(), x[1]))
    write_shards(items)
    json.dump(newcache, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(f'Total: {len(items)} entradas · {int(time.time()-T0)} s')

if __name__ == '__main__':
    main()
