#!/usr/bin/env python3
"""
The Toolsmith blog post publisher.

What it does:
1. Adds the new post to sitemap.xml
2. Adds a card for the new post to blog.html (newest at the top)

What it does NOT do:
- Commit or push to git (you do that yourself)
- Submit to Google Search Console (you do that yourself)

How to use:
  cd ~/Desktop/toolsmith-site
  python3 publish_post.py \\
    --slug "your-post-url-slug" \\
    --title "Your Post Title" \\
    --summary "One or two sentence summary that shows on the blog landing page." \\
    --date "2026-06-23" \\
    --tag "Senior Living"

Or interactive (no flags):
  python3 publish_post.py

That will prompt you for each piece of info.

Example:
  python3 publish_post.py \\
    --slug "cmms-software-for-senior-living" \\
    --title "Senior Living Maintenance Software: What to Look for in 2026" \\
    --summary "A practical guide for facilities directors at senior living communities." \\
    --date "2026-06-23" \\
    --tag "Senior Living"

Before running this, make sure:
- Your finished post is saved at: blog/<slug>.html
- You ran it from the toolsmith-site folder (not from inside blog/)
"""

import argparse
import os
import re
import sys
from datetime import datetime


SITEMAP_PATH = "sitemap.xml"
BLOG_LANDING_PATH = "blog.html"
BLOG_FOLDER = "blog"
SITE_URL = "https://www.thetoolsmithapp.com"


def fail(message):
    print("ERROR: " + message, file=sys.stderr)
    sys.exit(1)


def ask(prompt, default=None):
    suffix = " [" + default + "]: " if default else ": "
    answer = input(prompt + suffix).strip()
    return answer if answer else default


def get_args():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--slug", help="URL slug (e.g. 'first-post')")
    parser.add_argument("--title", help="Post title")
    parser.add_argument("--summary", help="Short summary for the landing page card")
    parser.add_argument("--date", help="Publish date in YYYY-MM-DD format (defaults to today)")
    parser.add_argument("--tag", help="Category tag (e.g. 'Senior Living')")
    args = parser.parse_args()

    if not args.slug:
        args.slug = ask("Slug (URL piece, like 'first-post')")
    if not args.slug:
        fail("Slug is required")

    if not args.title:
        args.title = ask("Title")
    if not args.title:
        fail("Title is required")

    if not args.summary:
        args.summary = ask("Summary (one or two sentences)")
    if not args.summary:
        fail("Summary is required")

    today = datetime.now().strftime("%Y-%m-%d")
    if not args.date:
        args.date = ask("Date", default=today)

    if not args.tag:
        args.tag = ask("Tag", default="Senior Living")

    return args


def slug_to_filename(slug):
    return os.path.join(BLOG_FOLDER, slug + ".html")


def format_display_date(iso_date):
    """Convert 2026-06-23 to June 23, 2026"""
    try:
        d = datetime.strptime(iso_date, "%Y-%m-%d")
        return d.strftime("%B %-d, %Y")
    except ValueError:
        fail("Date must be in YYYY-MM-DD format, got: " + iso_date)


def update_sitemap(slug, iso_date):
    """Add a new URL entry to sitemap.xml, just before </urlset>."""
    if not os.path.exists(SITEMAP_PATH):
        fail("sitemap.xml not found. Are you in the toolsmith-site folder?")

    with open(SITEMAP_PATH, "r", encoding="utf-8") as f:
        contents = f.read()

    post_url = SITE_URL + "/blog/" + slug

    if post_url in contents:
        print("  Sitemap already has " + post_url + ", skipping")
        return False

    new_entry = (
        "  <url>\n"
        "    <loc>" + post_url + "</loc>\n"
        "    <lastmod>" + iso_date + "</lastmod>\n"
        "    <changefreq>monthly</changefreq>\n"
        "    <priority>0.7</priority>\n"
        "  </url>\n"
    )

    if "</urlset>" not in contents:
        fail("sitemap.xml is malformed (no </urlset> tag found)")

    updated = contents.replace("</urlset>", new_entry + "</urlset>")

    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write(updated)
    print("  Sitemap updated with " + post_url)
    return True


def update_blog_landing(slug, title, summary, iso_date, tag):
    """Add a new card to blog.html and remove the empty-state card if it's there."""
    if not os.path.exists(BLOG_LANDING_PATH):
        fail("blog.html not found. Are you in the toolsmith-site folder?")

    with open(BLOG_LANDING_PATH, "r", encoding="utf-8") as f:
        contents = f.read()

    post_url = "/blog/" + slug

    if 'href="' + post_url + '"' in contents:
        print("  blog.html already has a card for " + post_url + ", skipping")
        return False

    display_date = format_display_date(iso_date)

    # Escape HTML special chars in user input
    def esc(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    card = (
        '    <a href="' + post_url + '" class="post-card">\n'
        '      <div class="post-meta">\n'
        '        <span>' + esc(display_date) + '</span>\n'
        '        <span class="post-meta-dot"></span>\n'
        '        <span class="post-meta-tag">' + esc(tag) + '</span>\n'
        '      </div>\n'
        '      <h2>' + esc(title) + '</h2>\n'
        '      <p>' + esc(summary) + '</p>\n'
        '      <span class="read-more">Read the article \u2192</span>\n'
        '    </a>\n'
    )

    # Remove the empty-state card if it exists (first post being published)
    empty_state_pattern = re.compile(
        r'\s*<div class="posts-empty">.*?</div>\s*',
        re.DOTALL
    )
    if empty_state_pattern.search(contents):
        contents = empty_state_pattern.sub("\n", contents)
        print("  Removed empty-state placeholder from blog.html")

    # Insert new card right after the opening <div class="posts-grid">
    marker = '<div class="posts-grid">'
    if marker not in contents:
        fail('Could not find <div class="posts-grid"> in blog.html')

    # Find the position right after the marker and the newline that follows
    pos = contents.index(marker) + len(marker)
    # Find the next newline so we insert on a fresh line
    insertion = "\n" + card
    updated = contents[:pos] + insertion + contents[pos:]

    with open(BLOG_LANDING_PATH, "w", encoding="utf-8") as f:
        f.write(updated)
    print("  blog.html updated with new card for: " + title)
    return True


def main():
    args = get_args()

    # Verify the post file exists
    post_file = slug_to_filename(args.slug)
    if not os.path.exists(post_file):
        fail(
            "Post file not found at " + post_file + "\n"
            "Make sure you saved your finished post HTML there first."
        )

    print("\nPublishing: " + args.title)
    print("Slug: " + args.slug)
    print("Date: " + args.date + " (" + format_display_date(args.date) + ")")
    print("Tag: " + args.tag)
    print()

    update_sitemap(args.slug, args.date)
    update_blog_landing(args.slug, args.title, args.summary, args.date, args.tag)

    print()
    print("All done. Next steps:")
    print("  1. Check the changes look right (open blog.html and sitemap.xml)")
    print("  2. Commit and push:")
    print("       git add " + post_file + " blog.html sitemap.xml")
    print('       git commit -m "publish blog post: ' + args.title.replace('"', '\\"') + '"')
    print("       git push")
    print("  3. After Vercel deploys (about a minute), submit the new URL to")
    print("     Google Search Console under URL Inspection:")
    print("       " + SITE_URL + "/blog/" + args.slug)


if __name__ == "__main__":
    main()
