#!/usr/bin/env python3
"""Índice por contenido de las webs pequeñas de la red.

En las webs con pocas páginas, el título no basta (p. ej. Freud aparece dentro de
«El psicoanálisis y sus desarrollos» en Psycholopedia). Aquí se leen las palabras de
cada página (título, descripción, encabezados y texto) y se guarda un índice invertido
por inicio de palabra:
  search/c/docs.json  -> [[título, sitio, ruta, idioma], ...]
  search/c/<3 letras>.json -> {"palabra": [doc, veces, doc, veces, ...], ...}
Uso: python3 tools/build_content.py            (descarga las páginas por HTTP)
     LOCAL='psycholopedia.com=/ruta/repo,...' python3 tools/build_content.py   (lee repos locales)
"""
import concurrent.futures as cf, html, json, os, re, shutil, sys, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_index as B

CONTENT_SITES = ['psycholopedia.com', 'leypedia.com', 'ludicopedia.com', 'iapedia.si', 'enfermeria.si',
                 'planetpedia.net', 'saberparainvertir.com']
OUTDIR = os.path.join(B.ROOT, 'search', 'c')
MAX_WORDS = 400
STOP = B.STOP | set('que como mas pero sus son esta este esto estos estas ese esa eso ser han hay fue era sin sobre entre desde hasta tambien muy cada todo toda todos todas otro otra otros otras puede pueden porque cuando donde segun tiene tienen hace parte forma vez anos ano dia this that with from are was were has have its into their they them which also more than been will can not your our you'.split())
DROP = re.compile(r'<(script|style|noscript|svg|nav|footer|header|form)\b.*?</\1>', re.I | re.S)
TAGS = re.compile(r'<[^>]+>')
CRED = re.compile(r'credit|credito|creditos|cookies|buscar|search|/404', re.I)
DESC = re.compile(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)', re.I)


def words_of(raw):
    raw = raw if isinstance(raw, str) else raw.decode('utf-8', 'ignore')
    m = DESC.search(raw)
    main = re.search(r'<main\b.*?</main>', raw, re.I | re.S)
    body = main.group(0) if main else raw
    text = (m.group(1) if m else '') + ' ' + TAGS.sub(' ', DROP.sub(' ', body))
    cnt = {}
    for w in re.split(r'[^a-z0-9]+', B.norm(html.unescape(text))):
        if len(w) < 3 or w in STOP or w.isdigit(): continue
        cnt[w] = cnt.get(w, 0) + 1
    return sorted(cnt.items(), key=lambda x: -x[1])[:MAX_WORDS]


def title_of(raw, name, path):
    raw = raw if isinstance(raw, str) else raw.decode('utf-8', 'ignore')
    m = B.OGT.search(raw.encode()) or B.TITLE.search(raw.encode())
    t = B.clean_title(m.group(1).decode('utf-8', 'ignore'), name) if m else ''
    return t or B.slug_title(path)


def pages_http(dom):
    urls = []
    for sm in B.sitemaps_for(dom):
        urls += B.parse_sitemap(sm)
        if urls: break
    seen, todo = set(), []
    for loc, _ in urls:
        p = urllib.parse.urlparse(loc)
        if p.netloc.replace('www.', '') != dom or B.SKIP.search(p.path) or CRED.search(p.path) or loc in seen: continue
        seen.add(loc); todo.append(loc)
    def one(loc):
        try: return loc, B.get(loc, 400000)[0]
        except Exception: return loc, None
    with cf.ThreadPoolExecutor(B.WORKERS) as ex:
        for loc, raw in ex.map(one, todo):
            if raw: yield urllib.parse.urlparse(loc).path, raw


def pages_local(root):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if not d.startswith(('.', '_')) and d not in ('assets', 'node_modules', 'api')]
        for f in fn:
            if not f.endswith('.html') or f == '404.html': continue
            rel = os.path.relpath(os.path.join(dp, f), root).replace(os.sep, '/')
            path = '/' + (rel[:-len('index.html')] if rel.endswith('index.html') else rel)
            if B.SKIP.search(path) or CRED.search(path): continue
            yield path, open(os.path.join(dp, f), encoding='utf-8', errors='ignore').read()


def main():
    local = dict(x.split('=', 1) for x in os.environ.get('LOCAL', '').split(',') if '=' in x)
    idx = {d: i for i, (d, _) in enumerate(B.SITES)}
    names = dict(B.SITES)
    docs, inv = [], {}
    for dom in CONTENT_SITES:
        if dom not in idx: continue
        n0 = len(docs)
        src = pages_local(local[dom]) if dom in local else pages_http(dom)
        for path, raw in src:
            raw = raw if isinstance(raw, str) else raw.decode('utf-8', 'ignore')
            if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+noindex', raw[:20000], re.I): continue
            di = len(docs)
            docs.append([title_of(raw, names[dom], path), idx[dom], path, B.lang_of(path)])
            for w, c in words_of(raw):
                inv.setdefault(w[:3], {}).setdefault(w, []).extend([di, min(c, 99)])
        print(f'{dom}: {len(docs) - n0} páginas', flush=True)
    shutil.rmtree(OUTDIR, ignore_errors=True); os.makedirs(OUTDIR)
    json.dump(docs, open(os.path.join(OUTDIR, 'docs.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    for k, d in inv.items():
        json.dump(d, open(os.path.join(OUTDIR, k + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(f'{len(docs)} páginas, {len(inv)} archivos')


if __name__ == '__main__':
    main()
