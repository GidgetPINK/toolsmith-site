#!/usr/bin/env python3
"""Swap DM Sans -> Inter across marketing site HTML. Keeps Cormorant, Kalam, Caveat.
Also ensures Inter is imported where DM Sans was. Backs up originals."""
import os, re, glob, shutil

BACKUP = "_pre_inter_backup"

def process(path):
    html = open(path, encoding="utf-8").read()
    orig = html
    # 1) all DM Sans variants -> Inter
    html = html.replace("'DM Sans', sans-serif", "'Inter', sans-serif")
    html = html.replace("'DM Sans',sans-serif", "'Inter',sans-serif")
    html = html.replace("DM Sans,sans-serif", "Inter,sans-serif")
    html = html.replace("DM Sans, sans-serif", "Inter, sans-serif")
    # 2) make sure Inter is loaded: if the google fonts link requests DM Sans, add Inter
    if "family=Inter" not in html and "fonts.googleapis.com/css2" in html:
        # add Inter to the existing google fonts link
        html = re.sub(r'(fonts\.googleapis\.com/css2\?)', r'\1family=Inter:wght@300;400;500;600;700&', html, count=1)
    changed = html != orig
    if changed:
        open(path, "w", encoding="utf-8").write(html)
    return changed

def main():
    os.makedirs(BACKUP, exist_ok=True)
    # marketing HTML at root + blog (blog already uses Inter, but harmless to run; it has no DM Sans)
    files = glob.glob("*.html") + glob.glob("blog/*.html")
    for f in sorted(files):
        shutil.copy2(f, os.path.join(BACKUP, os.path.basename(f)))
        result = "changed" if process(f) else "no DM Sans"
        print("%-50s %s" % (f, result))
    print("\nBackups in %s/  — DM Sans -> Inter done." % BACKUP)

if __name__ == "__main__":
    main()
