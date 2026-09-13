#!/usr/bin/env python3
"""Draw the profile card.

One SVG holds the whole profile: the signature line, the name, what I build, the
stack, the work, the principles, and the architecture. It is generated twice per
theme, because GitHub picks the asset by `prefers-color-scheme` and an image
served through its proxy cannot carry a media query of its own.

    python3 tools/build.py

Writes assets/card-dark.svg, assets/card-light.svg, and the link buttons.
Bump ASSET_VERSION in README.md (the ?v=N) whenever a change has to show
immediately — camo caches on the URL, not on the bytes behind it.
"""

import base64
import glob
import io
import os
import re
import xml.sax.saxutils as sx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS_DIR = os.path.join(ROOT, "tools", "icons")
SHOTS_DIR = os.path.join(ROOT, "tools", "shots")
OUT_DIR = os.path.join(ROOT, "assets")

W = 1280
PAD = 56
INNER = W - 2 * PAD

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'DejaVu Sans Mono',monospace"

THEMES = {
    "dark": dict(
        bg="#050B1A", panel="#081428", panel2="#0A1930", border="#1E3A5F",
        border_soft="#152D4A", text="#F5F7FF", muted="#94A3B8", dim="#64748B",
        accent="#18D7FF", accent2="#008CFF", accent3="#1769FF", accent4="#635BFF",
        icon="#CBD5E1", tile="#0E1F38", tile_border="#1E3A5F", halo=".30", hi="#67E8FF",
    ),
    "light": dict(
        bg="#FFFFFF", panel="#F4F8FF", panel2="#EDF4FF", border="#CBDBF2",
        border_soft="#DCE8F8", text="#08101F", muted="#475569", dim="#7C8BA1",
        accent="#0A79C7", accent2="#0B6BD4", accent3="#1B5FD0", accent4="#5B52E8",
        icon="#334155", tile="#FFFFFF", tile_border="#D3E1F5", halo=".10", hi="#8FD4FF",
    ),
}

# ---------------------------------------------------------------- content

# The signature line, the one that runs through the profile picture. Drawn three
# times over itself — a wide blurred bloom, a soft mid stroke, then the hard
# body — which is what makes it read as lit rather than merely coloured.
HERO_WAVE = ("M-60 300 C 200 300, 380 266, 620 256 S 900 300, 1080 208 "
             "S 1240 108, 1345 128")
HERO_WAVE_HI = ("M-60 292 C 200 292, 380 258, 620 248 S 900 292, 1080 200 "
                "S 1240 100, 1345 120")
HERO_WAVE_TR = ("M-60 336 C 220 336, 400 306, 646 296 S 920 338, 1098 250 "
                "S 1250 152, 1345 172")

PRINCIPLES_WAVE = ("M-40 112 C 140 112, 210 78, 372 90 S 628 128, 808 104 "
                   "S 1086 68, 1320 84")

# His own words, from the artwork the profile picture is cut from.
# x, y sampled off PRINCIPLES_WAVE so each node sits ON the line, and spaced so
# the longest label still clears the card's side padding.
PRINCIPLES = [
    (176, 96, "FOUNDER MINDSET"),
    (520, 105, "BETTER EVERYDAY"),
    (862, 97, "IDEAS TO IMPACT"),
    (1072, 78, "PROGRESS OVER PERFECTION"),
]

NAME = "ABDULLAH AL TAMIMI"

# The role line cycles. Every one of these is something the profile or the work
# already says: the GitHub bio names LeafleX, AI & automation and full-stack;
# the three domains are the three products. The first is the fallback — it is
# the only one with opacity 1 in the markup, so a renderer that ignores the
# stylesheet shows it and nothing overlaps.
ROLES = [
    "Technical Founder · Product Engineer",
    "Founder @ LeafleX · Nashrati",
    "AI & Automation · Full-Stack Developer",
    "Healthcare · Education · Government Software",
]
ROLE_SECONDS = 4.5            # each role holds this long
HERO_WAVE_LEN = 1438          # measured off the path; drives the shimmer
REQ_SECONDS = 7.0             # one request, end to end, through the architecture
SWEEP_W = 104                 # width of the band that crosses the request row
NODE_PEAK = 0.03              # where in nodeGlow the lit frame sits, as a fraction

PITCH = "Building the layer between authoritative data and the person who has to act on it."

WHAT = [
    ("HEALTHCARE", "GS1 pack verification, MedDRA-coded adverse-event reporting, E2B / CIOMS export"),
    ("EDUCATION", "Teacher and institutional analytics over Moodle, without recomputing its grades"),
    ("GOVERNMENT", "Citizen-feedback intelligence — classification, personas, root-cause tracing"),
    ("INTERFACE", "Arabic-first and RTL by default, down to the relational model underneath"),
]

STACK = [
    ("INTERFACE", [
        ("typescript", "TYPESCRIPT"), ("react", "REACT"), ("vite", "VITE"),
        ("tailwindcss", "TAILWIND"), ("framer", "FRAMER MOTION"), ("i18next", "I18NEXT"),
        ("leaflet", "LEAFLET"), ("javascript", "JAVASCRIPT"),
    ]),
    ("SYSTEMS", [
        ("python", "PYTHON"), ("fastapi", "FASTAPI"), ("nodedotjs", "NODE.JS"),
        ("php", "PHP"), ("postgresql", "POSTGRESQL"), ("supabase", "SUPABASE"),
        ("docker", "DOCKER"), ("kubernetes", "KUBERNETES"),
    ]),
    ("AI & DATA", [
        ("anthropic", "CLAUDE"), ("langchain", "LANGCHAIN"), ("ollama", "OLLAMA"),
        ("pytorch", "YOLO"), ("mongodb", "MONGODB"), ("redis", "REDIS"),
        ("git", "GIT"), ("github", "GITHUB"),
    ]),
]

WORK_IMAGES = [
    dict(
        title="NASHRATI",
        desc=["Official drug leaflets, turned into something a patient can act on:",
              "scan the pack, verify it, read it against your own profile."],
        stack="React 19 · Supabase · OpenAI · GS1 DataMatrix · MedDRA",
        shots=["nashrati-home.png", "nashrati-twin.png"], kind="phones",
    ),
    dict(
        title="LCMS GATE",
        desc=["Teacher and institution reporting over a real Moodle — saved",
              "templates, AND/OR filters, per-question statistics."],
        stack="FastAPI · React 19 · PHP plugin · PostgreSQL · Docker",
        shots=["lcms-reports.png"], kind="wide",
    ),
]

WORK_TEXT = [
    dict(
        title="TERHAL",
        desc=["Ma'an governorate beyond Petra: plan a trip and book a local",
              "guide at a price you can see up front."],
        stack="FastAPI · PostgreSQL · React 18 · Leaflet · OpenAI vision",
    ),
    dict(
        title="VOC-360",
        desc=["National citizen-experience platform that ingests public feedback,",
              "classifies it, and traces each issue to its root cause."],
        stack="FastAPI · PostgreSQL · Redis · Docker · pandas",
    ),
]

REQUEST = [("SCAN", "GS1 DataMatrix"), ("PROFILE", "Supabase RLS"),
           ("SMART VIEW", "OpenAI"), ("REPORT", "MedDRA → E2B")]
REQUEST_NOTE = "the official leaflet stays the authoritative source at every step"
PLATFORM = [("POSTGRESQL", "relational store"), ("SUPABASE AUTH", "identity"),
            ("OPENAI", "summarisation"), ("I18NEXT", "Arabic / English RTL")]

LINKS = [("linkedin", "LINKEDIN"), ("email", "EMAIL"),
         ("leaflex", "LEAFLEX"), ("build", "HOW IT'S BUILT")]

# ---------------------------------------------------------------- helpers


def esc(s):
    return sx.escape(str(s))


def load_icons():
    out = {}
    for f in glob.glob(os.path.join(ICONS_DIR, "*.svg")):
        slug = os.path.splitext(os.path.basename(f))[0]
        m = re.search(r'<path[^>]*\sd="([^"]+)"', open(f, encoding="utf-8").read())
        if m:
            out[slug] = m.group(1)
    return out


ICONS = load_icons()
_SHOT_CACHE = {}


def shot(name):
    """Base64 the screenshot once, reuse it across both themes."""
    if name not in _SHOT_CACHE:
        from PIL import Image
        im = Image.open(os.path.join(SHOTS_DIR, name)).convert("RGB")
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=82, optimize=True, progressive=True)
        _SHOT_CACHE[name] = ("data:image/jpeg;base64,"
                             + base64.b64encode(buf.getvalue()).decode())
    return _SHOT_CACHE[name]


def txt(x, y, s, size=15, fill="#fff", weight=400, family=SANS,
        anchor="start", spacing=None, opacity=None):
    a = [f'x="{x}"', f'y="{y}"', f'font-family="{family}"', f'font-size="{size}"',
         f'fill="{fill}"']
    if weight != 400:
        a.append(f'font-weight="{weight}"')
    if anchor != "start":
        a.append(f'text-anchor="{anchor}"')
    if spacing:
        a.append(f'letter-spacing="{spacing}"')
    if opacity:
        a.append(f'opacity="{opacity}"')
    return f'<text {" ".join(a)}>{esc(s)}</text>'


def section(t, y, label):
    """A small-caps section label with a rule running to the right edge."""
    o = [txt(PAD, y, label, size=12, fill=t["dim"], weight=700, spacing="3.6")]
    x0 = PAD + 11 * len(label) + 26
    o.append(f'<line x1="{x0}" y1="{y - 5}" x2="{W - PAD}" y2="{y - 5}" '
             f'stroke="{t["border_soft"]}" stroke-width="1"/>')
    return "".join(o)


def tile(t, cx, y, slug, label):
    """One rounded icon tile with its name beneath."""
    s, o = 62, []
    x = cx - s / 2
    o.append(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="15" '
             f'fill="{t["tile"]}" stroke="{t["tile_border"]}" stroke-width="1"/>')
    d = ICONS.get(slug)
    if d:
        k = 26 / 24
        o.append(f'<g transform="translate({cx - 13},{y + 18}) scale({k})">'
                 f'<path d="{d}" fill="{t["icon"]}"/></g>')
    o.append(txt(cx, y + s + 20, label, size=9.5, fill=t["dim"],
                 weight=600, spacing="1.3", anchor="middle"))
    return "".join(o)


def wave(theme, paths, widths=(34, 15, 8), hi=None, trail=None, dy=0, shimmer=False):
    """The glowing line. Bloom, mid stroke, body — then a hairline highlight."""
    g = f'url(#accent-{theme})'
    o = [f'<g transform="translate(0,{dy})" fill="none" stroke-linecap="round">']
    o.append(f'<path d="{paths}" stroke="{g}" stroke-width="{widths[0]}" '
             f'stroke-opacity=".45" filter="url(#bloom-{theme})"/>')
    o.append(f'<path d="{paths}" stroke="{g}" stroke-width="{widths[1]}" '
             f'stroke-opacity=".85" filter="url(#soft-{theme})"/>')
    o.append(f'<path d="{paths}" stroke="{g}" stroke-width="{widths[2]}"/>')
    if hi:
        o.append(f'<path d="{hi}" stroke="{THEMES[theme]["hi"]}" '
                 f'stroke-width="1.6" stroke-opacity=".55"/>')
    if trail:
        o.append(f'<path d="{trail}" stroke="{g}" stroke-width="3" '
                 f'stroke-opacity=".40"/>')
    if shimmer:
        # A short bright dash walking the full length, so the line reads as lit
        # rather than painted. One dash, one gap, the pattern as long as the
        # path — which is what makes the loop seamless.
        o.append(f'<path class="shimmer" d="{paths}" '
                 f'stroke="{THEMES[theme]["hi"]}" stroke-width="4" '
                 f'stroke-opacity=".9" filter="url(#soft-{theme})"/>')
    o.append("</g>")
    return "".join(o)


def flow_box(t, x, y, w, h, title, sub, glow=None):
    """A node. `glow` adds a lit copy of the border that the stylesheet fades
    up as the request pulse reaches it; it is opacity 0 in the markup, so a
    renderer that ignores the stylesheet just gets the diagram."""
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="11" '
         f'fill="{t["panel"]}" stroke="{t["border"]}" stroke-width="1"/>']
    if glow:
        o.append(f'<rect class="{glow}" x="{x}" y="{y}" width="{w}" height="{h}" '
                 f'rx="11" fill="{t["accent"]}" fill-opacity=".08" '
                 f'stroke="{t["accent"]}" stroke-width="1.8" opacity="0"/>')
    o.append(txt(x + w / 2, y + 31, title, size=14.5, fill=t["text"],
                 weight=700, spacing="2.2", anchor="middle"))
    o.append(txt(x + w / 2, y + 52, sub, size=12.5, fill=t["dim"], anchor="middle"))
    return "".join(o)


def arrow(t, x, y, glow=None):
    d = f"M{x} {y}h16m-5 -4l5 4l-5 4"
    o = [f'<path d="{d}" fill="none" stroke="{t["border"]}" stroke-width="1.6" '
         f'stroke-linecap="round" stroke-linejoin="round"/>']
    if glow:
        o.append(f'<path class="{glow}" d="{d}" fill="none" stroke="{t["accent"]}" '
                 f'stroke-width="2.4" stroke-linecap="round" '
                 f'stroke-linejoin="round" opacity="0"/>')
    return "".join(o)


# ---------------------------------------------------------------- the card


def build_card(theme):
    t = THEMES[theme]
    o = []

    # ---- hero: the signature line, with the name sitting clear of it
    o.append(wave(theme, HERO_WAVE, hi=HERO_WAVE_HI, trail=HERO_WAVE_TR, shimmer=True))

    y = 152
    o.append(f'<rect x="{PAD}" y="{y - 48}" width="5" height="64" rx="2.5" '
             f'fill="url(#accent-{theme})"/>')
    o.append(txt(PAD + 22, y, NAME, size=57, fill=t["text"], weight=800, spacing="7"))
    y += 44
    for i, role in enumerate(ROLES):
        o.append(f'<g class="role r{i + 1}" opacity="{1 if i == 0 else 0}">'
                 + txt(PAD + 24, y, role, size=20.5, fill=t["text"], weight=700)
                 + "</g>")
    y += 30
    o.append(txt(PAD + 24, y, PITCH, size=16, fill=t["muted"]))

    # ---- what I build
    y += 179
    o.append(section(t, y, "WHAT I BUILD"))
    y += 38
    for label, desc in WHAT:
        o.append(f'<rect x="{PAD + 1}" y="{y - 11}" width="8" height="8" rx="1.5" '
                 f'fill="{t["accent"]}" transform="rotate(45 {PAD + 5} {y - 7})"/>')
        o.append(txt(PAD + 26, y, label, size=11.5, fill=t["text"], weight=700,
                     spacing="2.5", family=MONO))
        o.append(txt(PAD + 210, y, desc, size=15.5, fill=t["muted"]))
        y += 43

    # ---- stack
    y += 26
    o.append(section(t, y, "STACK"))
    y += 34
    for group, items in STACK:
        o.append(txt(PAD, y, group, size=11, fill=t["accent"], weight=700, spacing="2.4"))
        y += 20
        step = INNER / len(items)
        for i, (slug, label) in enumerate(items):
            o.append(tile(t, PAD + step * (i + 0.5), y, slug, label))
        y += 118

    # ---- selected work
    y += 12
    o.append(section(t, y, "SELECTED WORK"))
    y += 34

    col_w = (INNER - 48) / 2
    for i, item in enumerate(WORK_IMAGES):
        x = PAD + i * (col_w + 48)
        ih = 330
        o.append(f'<rect x="{x}" y="{y}" width="{col_w}" height="{ih}" rx="12" '
                 f'fill="{t["panel"]}" stroke="{t["border"]}" stroke-width="1"/>')
        o.append(f'<clipPath id="clip-{theme}-{i}"><rect x="{x + 1}" y="{y + 1}" '
                 f'width="{col_w - 2}" height="{ih - 2}" rx="11"/></clipPath>')
        o.append(f'<g clip-path="url(#clip-{theme}-{i})">')
        if item["kind"] == "phones":
            pw2, ph = 138, 293
            gap = 26
            sx0 = x + (col_w - (pw2 * 2 + gap)) / 2
            for j, s in enumerate(item["shots"]):
                px2 = sx0 + j * (pw2 + gap)
                py2 = y + (ih - ph) / 2
                o.append(f'<rect x="{px2 - 1}" y="{py2 - 1}" width="{pw2 + 2}" '
                         f'height="{ph + 2}" rx="13" fill="{t["border"]}"/>')
                o.append(f'<clipPath id="ph-{theme}-{i}-{j}"><rect x="{px2}" y="{py2}" '
                         f'width="{pw2}" height="{ph}" rx="12"/></clipPath>')
                o.append(f'<image x="{px2}" y="{py2}" width="{pw2}" height="{ph}" '
                         f'preserveAspectRatio="xMidYMin slice" '
                         f'clip-path="url(#ph-{theme}-{i}-{j})" '
                         f'href="{shot(s)}"/>')
        else:
            o.append(f'<image x="{x + 1}" y="{y + 1}" width="{col_w - 2}" '
                     f'height="{ih - 2}" preserveAspectRatio="xMidYMin slice" '
                     f'href="{shot(item["shots"][0])}"/>')
        o.append("</g>")

        ty2 = y + ih + 40
        o.append(txt(x + col_w / 2, ty2, item["title"], size=18.5, fill=t["accent"],
                     weight=700, spacing="3.4", anchor="middle"))
        for k, line in enumerate(item["desc"]):
            o.append(txt(x + col_w / 2, ty2 + 32 + k * 24, line, size=15,
                         fill=t["text"], anchor="middle"))
        o.append(txt(x + col_w / 2, ty2 + 32 + len(item["desc"]) * 24 + 10,
                     item["stack"], size=13, fill=t["dim"], anchor="middle"))

    y += 330 + 40 + 32 + 2 * 24 + 10 + 62

    for i, item in enumerate(WORK_TEXT):
        x = PAD + i * (col_w + 48)
        o.append(txt(x + col_w / 2, y, item["title"], size=18.5, fill=t["accent"],
                     weight=700, spacing="3.4", anchor="middle"))
        for k, line in enumerate(item["desc"]):
            o.append(txt(x + col_w / 2, y + 32 + k * 24, line, size=15,
                         fill=t["text"], anchor="middle"))
        o.append(txt(x + col_w / 2, y + 32 + len(item["desc"]) * 24 + 10,
                     item["stack"], size=13, fill=t["dim"], anchor="middle"))

    y += 32 + 2 * 24 + 10 + 74

    # ---- how I work: the four principles, sitting on the line
    o.append(section(t, y, "HOW I WORK"))
    y += 22
    o.append(wave(theme, PRINCIPLES_WAVE, widths=(26, 11, 6), dy=y))
    for px3, py3, label in PRINCIPLES:
        o.append(f'<circle cx="{px3}" cy="{y + py3}" r="9" fill="{t["bg"]}" '
                 f'stroke="{t["accent"]}" stroke-width="3"/>')
        o.append(txt(px3, y + py3 - 32, label, size=13, fill=t["text"],
                     weight=700, spacing="2.8", anchor="middle"))
    y += 200

    # ---- architecture
    o.append(section(t, y, "ARCHITECTURE"))
    y += 40
    o.append(txt(PAD, y, "the request", size=13, fill=t["dim"]))
    y += 22

    bw, bh, gap = 260, 74, 32
    total = len(REQUEST) * bw + (len(REQUEST) - 1) * gap
    x0 = PAD + (INNER - total) / 2
    mid = y + bh / 2

    # The rail and the pulse go down FIRST, so every node painted after them
    # occludes the light: it travels the gaps, disappears into a box, and
    # comes out the far side. Where it is along the rail decides the delays
    # below, so both come off the same geometry.
    # When the band's bright edge is over a given x, as a fraction of the
    # cycle. The band starts one width off-screen left and its brightest point
    # sits at 82% of its own width, so both offsets go into the sum — get this
    # wrong and the boxes light progressively later than the light reaches them.
    travel = total + SWEEP_W * 2

    def lit_at(cx):
        return (cx + 0.18 * SWEEP_W) / travel

    box_at = [lit_at(i * (bw + gap) + bw / 2) for i in range(len(REQUEST))]
    arrow_at = [lit_at(i * (bw + gap) + bw + 16) for i in range(len(REQUEST) - 1)]

    o.append(f'<line x1="{x0}" y1="{mid}" x2="{x0 + total}" y2="{mid}" '
             f'stroke="{t["border_soft"]}" stroke-width="1.5"/>')

    for i, (title, sub) in enumerate(REQUEST):
        bx = x0 + i * (bw + gap)
        o.append(flow_box(t, bx, y, bw, bh, title, sub, glow=f"fglow g{i + 1}"))
        if i < len(REQUEST) - 1:
            o.append(arrow(t, bx + bw + 8, mid, glow=f"aglow a{i + 1}"))

    # The request itself: a soft band crossing the row. A dot was the first
    # idea and it was wrong — the boxes cover 1040 of the 1136 units it
    # travels, so it was hidden nine tenths of the way. A band drawn OVER the
    # row is visible the whole crossing and never collides with the labels.
    o.append(f'<rect class="req-sweep" x="{x0 - SWEEP_W}" y="{y - 8}" '
             f'width="{SWEEP_W}" height="{bh + 16}" rx="8" '
             f'fill="url(#sweep-{theme})"/>')

    # the dashed return path, drawn under the row
    ly = y + bh + 30
    o.append(f'<path class="req-return" d="M{x0 + 30} {y + bh} V{ly} '
             f'H{x0 + total - 30} V{y + bh}" '
             f'fill="none" stroke="{t["border"]}" stroke-width="1.2" '
             f'stroke-dasharray="4 5"/>')
    o.append(f'<g class="req-back">'
             f'<circle cx="{x0 + total - 30}" cy="{ly}" r="11" fill="{t["accent"]}" '
             f'opacity=".45" filter="url(#soft-{theme})"/>'
             f'<circle cx="{x0 + total - 30}" cy="{ly}" r="3.6" fill="{t["hi"]}"/></g>')
    o.append(txt(W / 2, ly + 26, REQUEST_NOTE, size=13, fill=t["dim"], anchor="middle"))

    y = ly + 62
    o.append(txt(PAD, y, "PLATFORM", size=11, fill=t["accent"], weight=700, spacing="2.4"))
    o.append(txt(PAD + 116, y, "the services every request runs on", size=13, fill=t["dim"]))
    y += 20

    pbw = (INNER - 3 * gap) / 4
    for i, (title, sub) in enumerate(PLATFORM):
        bx = PAD + i * (pbw + gap)
        o.append(flow_box(t, bx, y, pbw, bh, title, sub, glow=f"pglow p{i + 1}"))
        if i < len(PLATFORM) - 1:
            o.append(arrow(t, bx + pbw + 8, y + bh / 2))

    height = y + bh + 56

    defs = f'''<defs>
    <linearGradient id="accent-{theme}" x1="0%" y1="100%" x2="0%" y2="0%">
      <stop offset="0%" stop-color="{t["accent"]}"/>
      <stop offset="55%" stop-color="{t["accent2"]}"/>
      <stop offset="100%" stop-color="{t["accent4"]}"/>
    </linearGradient>
    <radialGradient id="halo-{theme}" cx="66%" cy="6%" r="58%">
      <stop offset="0%" stop-color="{t["accent2"]}" stop-opacity="{t["halo"]}"/>
      <stop offset="100%" stop-color="{t["bg"]}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="sweep-{theme}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{t["accent"]}" stop-opacity="0"/>
      <stop offset="50%" stop-color="{t["accent"]}" stop-opacity=".20"/>
      <stop offset="82%" stop-color="{t["hi"]}" stop-opacity=".55"/>
      <stop offset="100%" stop-color="{t["hi"]}" stop-opacity="0"/>
    </linearGradient>
    <filter id="bloom-{theme}" x="-20%" y="-400%" width="140%" height="900%">
      <feGaussianBlur stdDeviation="22"/>
    </filter>
    <filter id="soft-{theme}" x="-20%" y="-400%" width="140%" height="900%">
      <feGaussianBlur stdDeviation="8"/>
    </filter>
    <clipPath id="card-{theme}"><rect x="1" y="1" width="{W - 2}" height="{height - 2}" rx="20"/></clipPath>
  </defs>'''

    cycle = ROLE_SECONDS * len(ROLES)
    hold = 100.0 / len(ROLES)           # share of the cycle each role owns
    css = ["<style>"]
    css.append(f""".role{{animation:roleCycle {cycle}s linear infinite}}
@keyframes roleCycle{{
  0%{{opacity:0;transform:translateY(7px)}}
  {hold * 0.10:.2f}%{{opacity:1;transform:translateY(0)}}
  {hold * 0.86:.2f}%{{opacity:1;transform:translateY(0)}}
  {hold:.2f}%{{opacity:0;transform:translateY(-7px)}}
  100%{{opacity:0;transform:translateY(-7px)}}
}}""")
    for i in range(len(ROLES)):
        css.append(f".r{i + 1}{{animation-delay:{i * ROLE_SECONDS:g}s}}")
    css.append(f""".shimmer{{
  stroke-dasharray:210 {HERO_WAVE_LEN};
  animation:shimmerRun {cycle / 2:g}s linear infinite
}}
@keyframes shimmerRun{{
  from{{stroke-dashoffset:{HERO_WAVE_LEN + 210}}}
  to{{stroke-dashoffset:0}}
}}""")
    # The request: one pulse down the rail, each node lighting as it arrives.
    # Delays come from box_at/arrow_at, so moving a box moves its flash too.
    css.append(f""".req-sweep{{animation:reqFlow {REQ_SECONDS:g}s linear infinite}}
@keyframes reqFlow{{
  0%{{transform:translateX(0)}}
  100%{{transform:translateX({total + SWEEP_W * 2:g}px)}}
}}
.req-back{{animation:reqBack {REQ_SECONDS:g}s ease-in-out infinite}}
@keyframes reqBack{{
  0%,62%{{transform:translateX(0);opacity:0}}
  67%{{opacity:1}}
  93%{{opacity:1}}
  100%{{transform:translateX({-(total - 60):g}px);opacity:0}}
}}
.fglow,.aglow{{animation:nodeGlow {REQ_SECONDS:g}s linear infinite}}
@keyframes nodeGlow{{
  0%{{opacity:0}}
  {NODE_PEAK * 100:g}%{{opacity:1}}
  {NODE_PEAK * 100 + 11:g}%{{opacity:0}}
  100%{{opacity:0}}
}}
.req-return{{animation:reqDash 1.1s linear infinite}}
@keyframes reqDash{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:18}}}}
.pglow{{animation:svcPulse {REQ_SECONDS * 1.6:g}s ease-in-out infinite}}
@keyframes svcPulse{{0%,100%{{opacity:0}}50%{{opacity:.5}}}}""")
    for i, f in enumerate(box_at):
        css.append(f".g{i + 1}{{animation-delay:{(f - NODE_PEAK) * REQ_SECONDS:.2f}s}}")
    for i, f in enumerate(arrow_at):
        css.append(f".a{i + 1}{{animation-delay:{(f - NODE_PEAK) * REQ_SECONDS:.2f}s}}")
    for i in range(len(PLATFORM)):
        css.append(f".p{i + 1}{{animation-delay:{i * 0.9:g}s}}")

    # Motion is decoration here; the first role is the one that must survive,
    # and the diagram has to stay readable with every animation switched off.
    others = ",".join(f".r{i + 1}" for i in range(1, len(ROLES)))
    css.append("@media(prefers-reduced-motion:reduce){"
               ".role,.shimmer,.req-sweep,.req-back,.fglow,.aglow,.pglow,.req-return"
               "{animation:none}"
               f".r1{{opacity:1}}{others}{{opacity:0}}"
               ".shimmer,.req-sweep,.req-back{display:none}}")
    css.append("</style>")
    style = "".join(css)

    body = style + "".join(o)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {height}" width="{W}" height="{height}" role="img" aria-label="{esc(ALT)}">
  <title>{esc(NAME.title())} — {esc(ROLES[0])}</title>
  {defs}
  <rect x="1" y="1" width="{W - 2}" height="{height - 2}" rx="20" fill="{t["bg"]}"/>
  <g clip-path="url(#card-{theme})"><rect width="{W}" height="{height}" fill="url(#halo-{theme})"/>{body}</g>
  <rect x="1" y="1" width="{W - 2}" height="{height - 2}" rx="20" fill="none" stroke="{t["border"]}" stroke-width="1.5"/>
</svg>'''


ALT = (
    "A glowing cyan-to-blue line flows across the top of the card, the same line that "
    "runs through the profile picture, with a bright point of light travelling along "
    "it. Abdullah Al Tamimi. The role beneath the name cycles through four: technical "
    "founder and product engineer; founder at LeafleX and Nashrati; AI and automation "
    "and full-stack developer; healthcare, education and government software. Building the layer between "
    "authoritative data and the person who has to act on it. What I build: healthcare, GS1 pack verification, "
    "MedDRA-coded adverse-event reporting and E2B CIOMS export; education, teacher and "
    "institutional analytics over Moodle without recomputing its grades; government, "
    "citizen-feedback intelligence with classification, personas and root-cause tracing; "
    "interface, Arabic-first and right-to-left by default, down to the relational model "
    "underneath. Stack, interface: TypeScript, React, Vite, Tailwind, Framer Motion, "
    "i18next, Leaflet, JavaScript. Systems: Python, FastAPI, Node.js, PHP, PostgreSQL, "
    "Supabase, Docker, Kubernetes. AI and data: Claude, LangChain, Ollama, YOLO, MongoDB, "
    "Redis, Git, GitHub. Selected work in two columns: Nashrati, official drug leaflets "
    "turned into something a patient can act on — scan the pack, verify it, read it against "
    "your own profile — in React 19, Supabase, OpenAI, GS1 DataMatrix and MedDRA, shown as "
    "two Arabic phone screens. LCMS GATE, teacher and institution reporting over a real "
    "Moodle with saved templates, AND/OR filters and per-question statistics, in FastAPI, "
    "React 19, a PHP plugin, PostgreSQL and Docker, shown as its reports hub. Terhal, Ma'an "
    "governorate beyond Petra: plan a trip and book a local guide at a price you can see up "
    "front, in FastAPI, PostgreSQL, React 18, Leaflet and OpenAI vision. VOC-360, a national "
    "citizen-experience platform that ingests public feedback, classifies it and traces each "
    "issue to its root cause, in FastAPI, PostgreSQL, Redis, Docker and pandas. How I work, "
    "four principles set on the same glowing line: founder mindset, better everyday, ideas to "
    "impact, progress over perfection. Architecture, animated: a band of light crosses the "
    "request row and each step lights as the light reaches it — scan, GS1 DataMatrix, to "
    "profile, Supabase row-level security, to smart view, OpenAI, to report, MedDRA to E2B — "
    "then a pulse returns along the dashed path beneath, where the official leaflet stays the "
    "authoritative source at every step; the platform beneath is PostgreSQL as the relational "
    "store, Supabase Auth for identity, OpenAI for summarisation, and i18next for Arabic and "
    "English right-to-left."
)

# ---------------------------------------------------------------- buttons

BUTTON_ICONS = {
    "linkedin": "M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9h4v12H3zM9 9h3.8v1.7h.05c.53-1 1.83-2.05 3.77-2.05 4.03 0 4.78 2.65 4.78 6.1V21h-4v-5.3c0-1.26-.02-2.9-1.77-2.9-1.77 0-2.04 1.38-2.04 2.8V21H9z",
    "email": "M2 5.5A1.5 1.5 0 0 1 3.5 4h17A1.5 1.5 0 0 1 22 5.5v13a1.5 1.5 0 0 1-1.5 1.5h-17A1.5 1.5 0 0 1 2 18.5zM4.4 6l7.6 5.6L19.6 6zM20 7.9l-7.4 5.45a1 1 0 0 1-1.2 0L4 7.9V18h16z",
    "leaflex": "M12 2 3 6.2v6c0 5 3.8 9.2 9 9.8 5.2-.6 9-4.8 9-9.8v-6zm0 2.2 7 3.3v4.7c0 3.9-2.9 7.2-7 7.8-4.1-.6-7-3.9-7-7.8V7.5zm-1 3.3v4.2l-2.2-2.2-1.4 1.42L12 15.5l4.6-4.6-1.4-1.42L13 11.7V7.5z",
    "build": "M9.4 16.6 4.8 12l4.6-4.6L8 6l-6 6 6 6zm5.2 0 4.6-4.6-4.6-4.6L16 6l6 6-6 6z",
}


def build_button(theme, key, label):
    t = THEMES[theme]
    h = 44
    w = 42 + 9.6 * len(label) + 26
    ic = t["accent"] if key != "build" else t["muted"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(label)}">
  <rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="10" fill="{t["panel"]}" stroke="{t["border"]}" stroke-width="1.5"/>
  <g transform="translate(16,{(h - 20) / 2}) scale({20 / 24})"><path d="{BUTTON_ICONS[key]}" fill="{ic}"/></g>
  {txt(42, h / 2 + 4.5, label, size=12.5, fill=t["text"], weight=700, spacing="1.9", family=SANS)}
</svg>'''


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for theme in THEMES:
        p = os.path.join(OUT_DIR, f"card-{theme}.svg")
        open(p, "w", encoding="utf-8").write(build_card(theme))
        print(f"{os.path.basename(p):24} {os.path.getsize(p) / 1024:8.1f} KB")
        for key, label in LINKS:
            p = os.path.join(OUT_DIR, f"link-{key}-{theme}.svg")
            open(p, "w", encoding="utf-8").write(build_button(theme, key, label))
    print(f"{'link buttons':24} {len(LINKS) * 2:8} files")


if __name__ == "__main__":
    main()
