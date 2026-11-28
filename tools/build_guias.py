#!/usr/bin/env python3
"""Genera las guías de Enciclopedias Sí a partir de tools/guias/*.md.

Cada .md empieza con líneas «clave: valor» hasta una línea «---».
Claves: slug, title, description, h1, eyebrow, image, alt, related
(related: «Nombre|https://url|frase» separados por « ;; »).
El cuerpo admite: ## y ### títulos, párrafos, listas con «- »,
**negrita**, *cursiva* y [texto](url).

Salida: <slug>/index.html, guias/index.html y sitemap.xml.
Uso: python3 tools/build_guias.py
"""
import html, json, os, re, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "guias")
BASE = "https://enciclopedias.si"
TODAY = datetime.date.today().isoformat()

CSS = """*{box-sizing:border-box}html{scroll-padding-top:90px}body{margin:0;background:#f5f7fa;color:#142d43;font:16px/1.7 Arial,sans-serif}a{color:#0a6f7c}.wrap{max-width:1100px;margin:auto;padding:0 27px}header{background:#fff;border-bottom:1px solid #dce4eb;position:sticky;top:0;z-index:5}header .wrap{min-height:66px;display:flex;justify-content:space-between;align-items:center;gap:20px}.brand{font-size:23px;font-weight:800;letter-spacing:-1px;display:flex;align-items:center;gap:9px;color:#142d43;text-decoration:none}.brand b{font-size:12px;color:#128390;letter-spacing:0}.book{font-size:28px;color:#128390}nav{display:flex;gap:22px;font-size:13px;font-weight:bold}nav a{color:#142d43;text-decoration:none}.crumbs{font-size:12px;color:#6a7d8e;margin:22px 0 0}.crumbs a{color:#6a7d8e}.hero{display:grid;grid-template-columns:1.2fr 1fr;gap:34px;align-items:center;padding:18px 0 10px}.eyebrow{font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#087d8c;font-weight:bold}h1{font-size:clamp(32px,4vw,48px);line-height:1.06;letter-spacing:-1.6px;margin:12px 0}.lead{font-size:17px;color:#4f6577;margin:0}.hero img{width:100%;height:300px;object-fit:cover;border-radius:12px;display:block}.layout{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:40px;padding:26px 0 40px}article{background:#fff;border:1px solid #dce4eb;border-radius:12px;padding:10px 38px 30px}article h2{font-size:26px;line-height:1.2;letter-spacing:-.6px;margin:32px 0 8px}article h3{font-size:19px;margin:24px 0 4px}article p,article li{color:#253f55}article li{margin:5px 0}.toc{background:#eef5f8;border-radius:10px;padding:14px 20px;margin:24px 0 6px;font-size:14px}.toc strong{display:block;margin-bottom:4px}.toc ol{margin:0;padding-left:20px}aside .box{background:#fff;border:1px solid #dce4eb;border-radius:12px;padding:18px 20px;margin-bottom:18px;position:sticky;top:90px}aside h2{font-size:15px;margin:0 0 10px;letter-spacing:0}aside ul{list-style:none;margin:0;padding:0}aside li{border-top:1px solid #edf2f5;padding:9px 0;font-size:14px;line-height:1.4}aside li:first-child{border-top:0}aside li a{font-weight:bold;text-decoration:none}aside li span{display:block;color:#6a7d8e;font-size:12px}.more{padding:10px 0 40px}.more h2{font-size:24px;letter-spacing:-.5px}.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}.cards a{display:block;background:#fff;border:1px solid #dce4eb;border-radius:10px;padding:15px 17px;text-decoration:none;color:#142d43}.cards a b{display:block;font-size:15px;margin-bottom:4px}.cards a span{font-size:13px;color:#6a7d8e;line-height:1.45;display:block}.meta{font-size:12px;color:#6a7d8e;margin-top:26px;border-top:1px solid #edf2f5;padding-top:12px}footer{padding:23px 0;border-top:1px solid #d6e2ea;font-size:12px;color:#6d8596}footer .wrap{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}footer a{color:#6d8596}@media(max-width:900px){.layout{grid-template-columns:1fr}aside .box{position:static}.hero{grid-template-columns:1fr}.hero img{height:220px}}@media(max-width:650px){.wrap{padding:0 16px}header .wrap{flex-wrap:wrap;padding:10px 16px}nav{gap:14px;font-size:12px;width:100%;overflow-x:auto}article{padding:6px 18px 22px}article h2{font-size:22px}}"""


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: '<a href="%s">%s</a>' % (m.group(2).replace('"', "%22"), m.group(1)), t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*", r"<em>\1</em>", t)
    return t


def slugify(t):
    t = t.lower()
    for a, b in zip("áéíóúüñàèòïç·", "aeiouunaeoic-"):
        t = t.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:60]


def md(body):
    out, toc, para, items = [], [], [], []

    def flush():
        if para:
            out.append("<p>%s</p>" % inline(" ".join(para)))
            para.clear()
        if items:
            out.append("<ul>%s</ul>" % "".join("<li>%s</li>" % inline(i) for i in items))
            items.clear()

    for line in body.splitlines():
        s = line.strip()
        if not s:
            flush()
        elif s.startswith("### "):
            flush(); out.append("<h3>%s</h3>" % inline(s[4:]))
        elif s.startswith("## "):
            flush(); a = slugify(s[3:]); toc.append((a, s[3:]))
            out.append('<h2 id="%s">%s</h2>' % (a, inline(s[3:])))
        elif s.startswith("- "):
            if para:
                out.append("<p>%s</p>" % inline(" ".join(para))); para.clear()
            items.append(s[2:])
        else:
            if items:
                flush()
            para.append(s)
    flush()
    return "\n".join(out), toc


def words(body):
    return len(re.sub(r"[#*\[\]()]", " ", body).split())


def load():
    pages = []
    for fn in sorted(os.listdir(SRC)):
        if not fn.endswith(".md"):
            continue
        raw = open(os.path.join(SRC, fn), encoding="utf8").read()
        head, body = raw.split("\n---\n", 1)
        meta = {}
        for l in head.splitlines():
            if ":" in l:
                k, v = l.split(":", 1)
                meta[k.strip()] = v.strip()
        meta["related"] = [r.split("|") for r in meta.get("related", "").split(" ;; ") if r]
        meta["body"] = body
        pages.append(meta)
    return pages


def header():
    return ('<header><div class="wrap"><a class="brand" href="/"><span class="book">▥</span>Enciclopedias<b>.si</b></a>'
            '<nav aria-label="Principal"><a href="/#directorio">Explorar la red</a><a href="/guias/">Guías</a>'
            '<a href="/#guias">Guías locales</a><a href="/#proyecto">El proyecto</a></nav></div></header>')


def footer():
    return ('<footer><div class="wrap"><div><strong>Enciclopedias.si</strong> · Conocimiento, cultura y lugares por descubrir.</div>'
            '<div><a href="/">Portada</a> · <a href="/guias/">Todas las guías</a></div></div>'
            '<div class="wrap" style="display:block;margin-top:10px">© 2026 Alejandro Rosàs · Contenido bajo licencia '
            '<a href="https://creativecommons.org/licenses/by-nc/4.0/deed.es" rel="license noopener">CC BY-NC 4.0</a>, salvo indicación en contrario</div></footer>')


def head(title, desc, url, image=None, kind="article"):
    og_img = '<meta property="og:image" content="%s">' % (BASE + "/" + image) if image else ""
    return ('<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title><meta name="description" content="%s"><link rel="canonical" href="%s">'
            '<meta property="og:type" content="%s"><meta property="og:url" content="%s"><meta property="og:title" content="%s">'
            '<meta property="og:description" content="%s">%s<meta property="og:locale" content="es_ES">'
            '<meta property="og:site_name" content="Enciclopedias Sí"><style>%s</style>'
            % (html.escape(title), html.escape(desc), url, kind, url, html.escape(title), html.escape(desc), og_img, CSS))


def page(p, pages):
    url = "%s/%s/" % (BASE, p["slug"])
    content, toc = md(p["body"])
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": p["h1"], "description": p["description"],
           "inLanguage": "es", "mainEntityOfPage": url, "datePublished": p.get("date", TODAY), "dateModified": TODAY,
           "author": {"@type": "Person", "name": "Alejandro Rosàs"},
           "publisher": {"@type": "Organization", "name": "Enciclopedias Sí", "url": BASE + "/"},
           **({"image": BASE + "/" + p["image"]} if p.get("image") else {})},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Enciclopedias Sí", "item": BASE + "/"},
              {"@type": "ListItem", "position": 2, "name": "Guías", "item": BASE + "/guias/"},
              {"@type": "ListItem", "position": 3, "name": p["h1"], "item": url}]}]
    tochtml = '<div class="toc" role="navigation" aria-label="En esta guía"><strong>En esta guía</strong><ol>%s</ol></div>' % "".join(
        '<li><a href="#%s">%s</a></li>' % (a, inline(t)) for a, t in toc) if len(toc) > 2 else ""
    rel = "".join('<li><a href="%s">%s</a><span>%s</span></li>' % (u, html.escape(n), html.escape(d)) for n, u, d in p["related"])
    others = [o for o in pages if o["slug"] != p["slug"]]
    cards = "".join('<a href="/%s/"><b>%s</b><span>%s</span></a>' % (o["slug"], html.escape(o["h1"]), html.escape(o["description"])) for o in others)
    img = ('<img src="/%s" alt="%s" width="900" height="600" fetchpriority="high">' % (p["image"], html.escape(p.get("alt", "")))) if p.get("image") else ""
    return (head(p["title"], p["description"], url, p.get("image"))
            + "".join('<script type="application/ld+json">%s</script>' % json.dumps(x, ensure_ascii=False) for x in ld)
            + "</head><body>" + header()
            + '<main><div class="wrap"><p class="crumbs"><a href="/">Enciclopedias Sí</a> › <a href="/guias/">Guías</a> › %s</p>' % html.escape(p["h1"])
            + '<div class="hero"><div><span class="eyebrow">%s</span><h1>%s</h1><p class="lead">%s</p></div>%s</div>' % (html.escape(p["eyebrow"]), html.escape(p["h1"]), inline(p["lead"]), img)
            + '<div class="layout"><article>%s%s<p class="meta">Texto original de Enciclopedias Sí · Actualizado el %s.</p></article>' % (tochtml, content, fecha(TODAY))
            + '<aside><div class="box"><h2>Para seguir explorando</h2><ul>%s</ul></div></aside></div></div>' % rel
            + '<section class="more"><div class="wrap"><h2>Otras guías de Enciclopedias Sí</h2><div class="cards">%s</div></div></section></main>' % cards
            + footer() + "</body></html>\n")


MESES = "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split()


def fecha(iso):
    y, m, d = iso.split("-")
    return "%d de %s de %s" % (int(d), MESES[int(m) - 1], y)


def hub(pages):
    url = BASE + "/guias/"
    title = "Guías de Enciclopedias Sí: cultura, ciencia, salud y lugares"
    desc = "Guías originales para empezar con la música clásica, la pintura, la mitología, la psicología, el vino o los mejores rincones del Garraf y de Eivissa."
    cards = "".join('<a href="/%s/"><b>%s</b><span>%s</span></a>' % (o["slug"], html.escape(o["h1"]), html.escape(o["description"])) for o in pages)
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "url": url, "inLanguage": "es",
          "hasPart": [{"@type": "Article", "headline": o["h1"], "url": "%s/%s/" % (BASE, o["slug"])} for o in pages]}
    return (head(title, desc, url, kind="website") + '<script type="application/ld+json">%s</script>' % json.dumps(ld, ensure_ascii=False)
            + "</head><body>" + header()
            + '<main><div class="wrap"><p class="crumbs"><a href="/">Enciclopedias Sí</a> › Guías</p>'
            + '<div style="padding:18px 0 22px;max-width:760px"><span class="eyebrow">Guías de la red</span><h1>Guías para empezar a explorar</h1>'
            + '<p class="lead">Cada guía resume un tema en un solo lugar, con un texto propio escrito para Enciclopedias Sí, y te lleva después a la enciclopedia o a la guía local de la red donde puedes profundizar.</p></div>'
            + '<div class="cards" style="padding-bottom:44px">%s</div></div></main>' % cards + footer() + "</body></html>\n")


def sitemap(pages):
    alt = ('<xhtml:link rel="alternate" hreflang="es" href="%s/"/><xhtml:link rel="alternate" hreflang="en" href="%s/en/"/>'
           '<xhtml:link rel="alternate" hreflang="x-default" href="%s/"/>') % (BASE, BASE, BASE)
    rows = ['<url><loc>%s/</loc><lastmod>%s</lastmod>%s</url>' % (BASE, TODAY, alt),
            '<url><loc>%s/en/</loc><lastmod>%s</lastmod>%s</url>' % (BASE, TODAY, alt),
            '<url><loc>%s/guias/</loc><lastmod>%s</lastmod></url>' % (BASE, TODAY)]
    rows += ['<url><loc>%s/%s/</loc><lastmod>%s</lastmod></url>' % (BASE, p["slug"], TODAY) for p in pages]
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(rows) + "\n</urlset>\n")


def main():
    pages = load()
    for p in pages:
        d = os.path.join(ROOT, p["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf8").write(page(p, pages))
        print("%-45s %5d palabras" % (p["slug"], words(p["body"])))
    os.makedirs(os.path.join(ROOT, "guias"), exist_ok=True)
    open(os.path.join(ROOT, "guias", "index.html"), "w", encoding="utf8").write(hub(pages))
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf8").write(sitemap(pages))


if __name__ == "__main__":
    main()
