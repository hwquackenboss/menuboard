#!/usr/bin/env python3
"""
build.py — Menuboard builder
Reads every .html file from ./pages/ (sorted by filename) and
writes a self-contained index.html that cycles through them.

Usage:
    python3 build.py
    python3 build.py --duration 10      # seconds per slide (default: 8)
    python3 build.py --fit cover        # "contain" or "cover" for image slides
    python3 build.py --watch            # rebuild automatically when pages/ changes
"""

import os
import sys
import time
import argparse
import hashlib

PAGES_DIR = os.path.join(os.path.dirname(__file__), "pages")
OUTPUT    = os.path.join(os.path.dirname(__file__), "index.html")

# ── Template ──────────────────────────────────────────────────────────────────

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Menuboard</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html, body {{ width:100%; height:100%; background:#000; overflow:hidden; }}

  #slideshow {{ position:relative; width:100vw; height:100vh; }}

  .slide {{
    position: absolute;
    inset: 0;
    width: 100%; height: 100%;
    opacity: 0;
    transition: opacity 1s ease-in-out;
    pointer-events: none;
    border: none;
    background: #000;
  }}
  .slide.active {{
    opacity: 1;
    pointer-events: auto;
  }}

  /* Each page is sandboxed in an iframe that fills the slide */
  .slide iframe {{
    width: 100%; height: 100%;
    border: none;
    background: #000;
  }}

  #progress {{
    position: fixed;
    bottom: 0; left: 0;
    height: 3px;
    background: rgba(255,255,255,0.45);
    width: 0%;
    z-index: 100;
  }}
</style>
</head>
<body>

<div id="slideshow">
{slides}
</div>
<div id="progress"></div>

<script>
const DURATION = {duration}; // ms

const slides     = document.querySelectorAll('.slide');
const progressEl = document.getElementById('progress');
let current = 0, timer;

function show(index) {{
  slides.forEach(s => s.classList.remove('active'));
  current = ((index % slides.length) + slides.length) % slides.length;
  slides[current].classList.add('active');
  animateProgress();
}}

function animateProgress() {{
  progressEl.style.transition = 'none';
  progressEl.style.width = '0%';
  void progressEl.offsetWidth;
  progressEl.style.transition = `width ${{DURATION}}ms linear`;
  progressEl.style.width = '100%';
}}

function next() {{ show(current + 1); }}

function startAuto() {{
  clearInterval(timer);
  timer = setInterval(next, DURATION);
}}

document.addEventListener('keydown', e => {{
  if (e.key === 'ArrowRight' || e.key === ' ') {{ clearInterval(timer); next(); startAuto(); }}
  if (e.key === 'ArrowLeft')                   {{ clearInterval(timer); show(current - 1); startAuto(); }}
  if (e.key === 'f' || e.key === 'F')          {{ document.documentElement.requestFullscreen?.(); }}
}});

show(0);
startAuto();
</script>
</body>
</html>
"""

SLIDE_TEMPLATE = """\
  <div class="slide" data-page="{name}">
    <iframe src="pages/{filename}" scrolling="no"></iframe>
  </div>"""

# ── Builder ───────────────────────────────────────────────────────────────────

def get_pages():
    if not os.path.isdir(PAGES_DIR):
        print(f"  Creating {PAGES_DIR}/")
        os.makedirs(PAGES_DIR)
        return []
    files = sorted(
        f for f in os.listdir(PAGES_DIR)
        if f.lower().endswith(".html")
    )
    return files

def build(duration_ms=80000):
    pages = get_pages()

    if not pages:
        print("  No .html files found in pages/ — nothing to build.")
        return None

    slides_html = "\n".join(
        SLIDE_TEMPLATE.format(name=os.path.splitext(f)[0], filename=f)
        for f in pages
    )

    output = HTML_TEMPLATE.format(
        slides=slides_html,
        duration=duration_ms,
    )

    with open(OUTPUT, "w", encoding="utf-8") as fh:
        fh.write(output)

    print(f"  Built {OUTPUT}  ({len(pages)} slide{'s' if len(pages) != 1 else ''})")
    for f in pages:
        print(f"    • {f}")

    return output

def dir_hash():
    """Fingerprint the pages/ directory so we can detect changes."""
    pages = get_pages()
    h = hashlib.md5()
    for f in pages:
        h.update(f.encode())
        path = os.path.join(PAGES_DIR, f)
        try:
            h.update(str(os.path.getmtime(path)).encode())
        except OSError:
            pass
    return h.hexdigest()

def watch(duration_ms=80000, interval=3):
    print(f"  Watching pages/ for changes (every {interval}s) — Ctrl+C to stop")
    last = None
    try:
        while True:
            current = dir_hash()
            if current != last:
                build(duration_ms)
                last = current
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n  Stopped.")

# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build slideshow from pages/ directory.")
    parser.add_argument("--duration", type=int, default=8,
                        help="Seconds per slide (default: 8)")
    parser.add_argument("--watch", action="store_true",
                        help="Watch pages/ and rebuild on changes")
    args = parser.parse_args()

    duration_ms = args.duration * 1000

    if args.watch:
        watch(duration_ms)
    else:
        build(duration_ms)
