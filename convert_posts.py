#!/usr/bin/env python3
"""Convert Toolsmith blog posts to Field Notes torn-paper design. v2 (slice-based)."""
import os, re, glob, shutil

BLOG_DIR = "blog"
BACKUP_DIR = os.path.join(BLOG_DIR, "_pre_paper_backup")

NEW_FONTS = ('<link href="https://fonts.googleapis.com/css2?'
             'family=Inter:wght@300;400;500;600;700&'
             'family=Kalam:wght@400;700&family=Caveat:wght@500;600;700&'
             'family=Cormorant+Garamond:wght@400;500;600;700&display=swap" rel="stylesheet"/>')

NEW_STYLE = r"""<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--charcoal:#1a1a2e;--navy:#16213e;--gold:#c9a84c;--gold-light:#e8c97a;--white:#f8f6f1;--muted:#9a9db5;--cb:rgba(201,168,76,0.18);--card:#1e2245;--r:12px;--tag-guides:#7fb3e0;--tag-senior:#e8c97a;--tag-compliance:#7ec98a;--body-lh:32px;--line-color:rgba(120,140,165,0.30)}
html{scroll-behavior:smooth}
body{background:var(--charcoal);color:var(--white);font-family:'Inter',sans-serif;font-weight:400;line-height:1.7;overflow-x:hidden}
nav{position:sticky;top:0;z-index:100;display:flex;align-items:center;justify-content:space-between;padding:1rem 5%;background:rgba(26,26,46,0.95);backdrop-filter:blur(20px);border-bottom:1px solid var(--cb)}
.nav-logo{display:flex;align-items:center;gap:.6rem;text-decoration:none}
.nav-logo img{height:36px;width:36px;border-radius:6px;object-fit:cover}
.nav-logo-text{font-family:'Cormorant Garamond',serif;font-size:1.4rem;color:var(--gold);letter-spacing:.04em;font-weight:600}
.nav-back{color:var(--muted);font-size:.85rem;text-decoration:none;letter-spacing:.06em;text-transform:uppercase;font-weight:400;display:flex;align-items:center;gap:.5rem}
.nav-back:hover{color:var(--gold-light)}
.nav-back::before{content:'\2190';font-size:1rem;line-height:1}
.page-bg{padding:3.5rem 1.5rem 5rem;background:radial-gradient(ellipse 70% 40% at 50% 0%,rgba(15,52,96,.4) 0%,transparent 70%),linear-gradient(180deg,var(--charcoal) 0%,var(--navy) 100%)}
.paper{position:relative;max-width:760px;margin:0 auto;background:#f7f3e8;padding:3.75rem 3.75rem 4.25rem;box-shadow:0 30px 70px -15px rgba(0,0,0,0.7),0 6px 18px rgba(0,0,0,0.4);overflow:hidden}
.paper::before{content:'';position:absolute;left:0;right:0;top:-12px;height:14px;background:#f7f3e8;z-index:2;clip-path:polygon(0 100%,2% 30%,4% 90%,6% 20%,8% 80%,10% 40%,12% 95%,14% 25%,16% 85%,18% 35%,20% 90%,22% 20%,24% 80%,26% 45%,28% 95%,30% 25%,32% 85%,34% 30%,36% 90%,38% 40%,40% 95%,42% 20%,44% 80%,46% 35%,48% 90%,50% 25%,52% 85%,54% 40%,56% 95%,58% 20%,60% 80%,62% 35%,64% 90%,66% 30%,68% 85%,70% 45%,72% 95%,74% 25%,76% 80%,78% 35%,80% 90%,82% 20%,84% 85%,86% 40%,88% 95%,90% 25%,92% 80%,94% 35%,96% 90%,98% 30%,100% 95%,100% 100%)}
.paper::after{content:'';position:absolute;left:0;right:0;bottom:-12px;height:14px;background:#f7f3e8;z-index:2;clip-path:polygon(0 0,2% 70%,4% 10%,6% 80%,8% 20%,10% 60%,12% 5%,14% 75%,16% 15%,18% 65%,20% 10%,22% 80%,24% 20%,26% 55%,28% 5%,30% 75%,32% 15%,34% 70%,36% 10%,38% 60%,40% 5%,42% 80%,44% 20%,46% 65%,48% 10%,50% 75%,52% 15%,54% 60%,56% 5%,58% 80%,60% 20%,62% 65%,64% 10%,66% 70%,68% 15%,70% 55%,72% 5%,74% 75%,76% 20%,78% 65%,80% 10%,82% 15%,84% 60%,86% 5%,88% 75%,90% 20%,92% 65%,94% 10%,96% 70%,98% 15%,100% 5%,100% 0)}
.post-meta{position:relative;z-index:1;font-size:.72rem;letter-spacing:.18em;text-transform:uppercase;color:#a89b6a;font-weight:600;margin-bottom:.75rem;display:flex;gap:.6rem;align-items:center;flex-wrap:wrap}
.post-meta .dot{width:3px;height:3px;border-radius:50%;background:#a89b6a}
.post-meta .tag-guides{color:#5a86ac}
.post-meta .tag-senior{color:#a9862f}
.post-meta .tag-compliance{color:#4f8a5a}
.post-meta .read{color:#a89b6a}
.paper h1{position:relative;z-index:1;font-family:'Kalam',cursive;font-size:2.7rem;font-weight:700;line-height:1.15;color:#b5892f;margin-bottom:1.25rem}
.divider{position:relative;z-index:1;width:60px;height:3px;background:var(--gold);margin-bottom:1.75rem;border-radius:2px}
.post-content{position:relative;font-size:16px;line-height:var(--body-lh);color:#2b2b28}
.post-content::before{content:'';position:absolute;left:-1rem;right:-1rem;top:0;bottom:0;background-image:repeating-linear-gradient(transparent,transparent calc(var(--body-lh) - 1px),var(--line-color) calc(var(--body-lh) - 1px),var(--line-color) var(--body-lh));pointer-events:none;z-index:0}
.post-content p,.post-content h2,.post-content h3,.post-content ul,.post-content ol,.post-content blockquote,.post-content .cta-card,.post-content .post-share,.post-content .post-footer,.post-content img,.post-content figure{position:relative;z-index:1}
.post-content p{margin:0 0 var(--body-lh);color:#2b2b28}
.post-content img{max-width:100%;height:auto;border-radius:6px;margin:0 0 var(--body-lh);display:block}
.post-content figure{margin:0 0 var(--body-lh)}
.post-content figcaption{font-size:.85rem;color:#8a7a4a;font-style:italic;margin-top:.4rem;text-align:center}
.post-content a{color:#9a6b1a;text-decoration:underline;text-decoration-color:rgba(154,107,26,0.4);text-underline-offset:2px}
.post-content a:hover{color:#7a5410}
.post-content h2{font-family:'Kalam',cursive;font-size:1.6rem;font-weight:700;color:#1a1a17;margin:var(--body-lh) 0 .25rem;line-height:1.2}
.post-content h3{font-family:'Kalam',cursive;font-size:1.3rem;font-weight:700;color:#3a3a34;margin:1.25rem 0 .25rem;line-height:1.2}
.post-content ul,.post-content ol{margin:0 0 var(--body-lh);padding:0;list-style:none}
.post-content ul li,.post-content ol li{position:relative;padding-left:1.5rem;line-height:var(--body-lh);color:#2b2b28}
.post-content ul li::before{content:'\2713';position:absolute;left:0;color:var(--gold);font-weight:700}
.post-content ol{counter-reset:item}
.post-content ol li{counter-increment:item}
.post-content ol li::before{content:counter(item) '.';position:absolute;left:0;color:#9a6b1a;font-weight:700}
.post-content strong{color:#1a1a17;font-weight:600}
.post-content em{color:#5a5240;font-style:italic}
.post-content blockquote{border-left:3px solid var(--gold);padding-left:1.25rem;margin:0 0 var(--body-lh);font-family:'Caveat',cursive;font-size:1.5rem;line-height:var(--body-lh);color:#5a5240}
.post-content blockquote p{font-family:'Caveat',cursive;font-size:1.5rem;color:#5a5240;margin:0}
.cta-card{background:var(--card);border-radius:10px;padding:1.75rem;margin:2.5rem 0 1rem;text-align:center}
.cta-card h3{font-family:'Kalam',cursive;font-size:1.4rem;color:var(--white);margin:0 0 .6rem;font-weight:700}
.cta-card p{color:var(--muted);font-size:.95rem;margin-bottom:1.25rem;line-height:1.6}
.cta-btn{display:inline-block;background:linear-gradient(135deg,var(--gold),var(--gold-light));color:var(--charcoal);padding:.8rem 1.75rem;border-radius:8px;font-weight:600;font-size:.85rem;letter-spacing:.05em;text-transform:uppercase;text-decoration:none}
.cta-btn:hover{opacity:.9;color:var(--charcoal)}
.post-share{margin-top:2rem;padding-top:1.5rem;border-top:1px solid rgba(0,0,0,0.1);text-align:center}
.post-share p{color:#8a7a4a;font-size:.82rem;letter-spacing:.06em;text-transform:uppercase;margin-bottom:1rem;font-weight:600}
.share-btns{display:flex;gap:.75rem;justify-content:center;flex-wrap:wrap}
.share-btn{display:inline-flex;align-items:center;gap:.5rem;background:rgba(201,168,76,.12);border:1px solid rgba(201,168,76,.5);color:#9a6b1a;padding:.6rem 1.2rem;border-radius:8px;font-size:.85rem;text-decoration:none}
.share-btn:hover{background:rgba(201,168,76,.22)}
.post-footer{margin-top:1.5rem;padding-top:1.5rem;border-top:1px solid rgba(0,0,0,0.1);text-align:center}
.post-footer p{color:#5a5240;font-size:.9rem;margin-bottom:1rem}
.post-footer a{color:#9a6b1a}
footer{background:var(--charcoal);border-top:1px solid var(--cb);padding:2.5rem 5%;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem}
.flogo{display:flex;align-items:center;gap:.5rem;font-family:'Cormorant Garamond',serif;color:var(--gold);font-size:1.1rem;font-weight:600}
.flogo img{height:28px;width:28px;border-radius:4px;object-fit:cover}
.fnote{color:var(--muted);font-size:.8rem}
.flinks{display:flex;gap:1.5rem}
.flinks a{color:var(--muted);font-size:.8rem;text-decoration:none}
.flinks a:hover{color:var(--gold)}
@media (max-width:640px){.page-bg{padding:2rem .75rem 3rem}.paper{padding:2.5rem 1.5rem 3rem}.paper h1{font-size:2.1rem}.post-content h2{font-size:1.4rem}}
</style>"""


def replace_between(html, start_regex, end_marker, replacement):
    m = re.search(start_regex, html)
    if not m:
        return html, False
    end_idx = html.find(end_marker, m.end())
    if end_idx == -1:
        return html, False
    end_idx += len(end_marker)
    return html[:m.start()] + replacement + html[end_idx:], True


def convert(path):
    html = open(path, encoding="utf-8").read()
    if 'class="paper"' in html:
        return "skip (already converted)"
    html, _ = replace_between(html, r'<link href="https://fonts\.googleapis\.com/css2\?', 'rel="stylesheet"/>', NEW_FONTS)
    html, ok = replace_between(html, r'<style>', "</style>", NEW_STYLE)
    if not ok:
        return "FAILED: no <style>"
    hero = re.search(r'<section class="post-hero">(.*?)</section>', html, re.S)
    meta_html, h1_html = "", ""
    if hero:
        inner = hero.group(1)
        mm = re.search(r'<div class="post-meta">.*?</div>', inner, re.S)
        if mm: meta_html = mm.group(0)
        hh = re.search(r'<h1>.*?</h1>', inner, re.S)
        if hh: h1_html = hh.group(0)
    art = re.search(r'<article class="post-content">(.*?)</article>', html, re.S)
    if not art:
        return "FAILED: no article body"
    body_html = art.group(1)
    paper = ('<div class="page-bg">\n  <article class="paper">\n    ' + meta_html +
             '\n    ' + h1_html + '\n    <div class="divider"></div>\n    <div class="post-content">\n' +
             body_html + '\n    </div>\n  </article>\n</div>')
    start = re.search(r'<section class="post-hero">', html)
    end_idx = html.find("</main>", start.end()) + len("</main>")
    html = html[:start.start()] + paper + html[end_idx:]
    open(path, "w", encoding="utf-8").write(html)
    return "converted"


def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    posts = [p for p in glob.glob(os.path.join(BLOG_DIR, "*.html")) if os.path.basename(p) != "_template.html"]
    for p in sorted(posts):
        name = os.path.basename(p)
        shutil.copy2(p, os.path.join(BACKUP_DIR, name))
        try:
            result = convert(p)
        except Exception as e:
            result = "ERROR: " + str(e)
        print("%-55s %s" % (name, result))
    print("\nBackups in %s/" % BACKUP_DIR)


if __name__ == "__main__":
    main()
