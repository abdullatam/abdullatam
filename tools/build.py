#!/usr/bin/env python3
"""Draw the profile card.

One SVG holds the whole profile: the terminal, the name, what I build, the
stack, the work, and the architecture. It is generated twice, once per theme,
because GitHub picks the asset by `prefers-color-scheme` and an image served
through its proxy cannot carry a media query of its own.

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
        icon="#CBD5E1", tile="#0E1F38", tile_border="#1E3A5F", halo=".30",
    ),
    "light": dict(
        bg="#FFFFFF", panel="#F4F8FF", panel2="#EDF4FF", border="#CBDBF2",
        border_soft="#DCE8F8", text="#08101F", muted="#475569", dim="#7C8BA1",
        accent="#0A79C7", accent2="#0B6BD4", accent3="#1B5FD0", accent4="#5B52E8",
        icon="#334155", tile="#FFFFFF", tile_border="#D3E1F5", halo=".10",
    ),
}

# ---------------------------------------------------------------- content

QUERY = "what actually makes regulated software trustworthy?"
CHIPS = ["SCAN", "VERIFY", "EXPLAIN", "REPORT"]
ANSWER = "The source stays authoritative. I build the layer that makes it usable."

NAME = "ABDULLAH AL TAMIMI"
ROLE = "Technical Founder · Product Engineer"
PITCH = "Building the layer between authoritative data and the person who has to act on it."
AFFIL = "9XAI Fellow · Al Hussein Technical University · Jordan"

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


def flow_box(t, x, y, w, h, title, sub):
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="11" '
         f'fill="{t["panel"]}" stroke="{t["border"]}" stroke-width="1"/>']
    o.append(txt(x + w / 2, y + 31, title, size=14.5, fill=t["text"],
                 weight=700, spacing="2.2", anchor="middle"))
    o.append(txt(x + w / 2, y + 52, sub, size=12.5, fill=t["dim"], anchor="middle"))
    return "".join(o)


def arrow(t, x, y):
    return (f'<path d="M{x} {y}h16m-5 -4l5 4l-5 4" fill="none" '
            f'stroke="{t["border"]}" stroke-width="1.6" stroke-linecap="round" '
            f'stroke-linejoin="round"/>')


# ---------------------------------------------------------------- the card


def build_card(theme):
    t = THEMES[theme]
    o = []
    y = 0

    # ---- terminal
    ty = 48
    th = 178
    o.append(f'<rect x="{PAD}" y="{ty}" width="{INNER}" height="{th}" rx="14" '
             f'fill="{t["panel"]}" stroke="{t["border"]}" stroke-width="1"/>')
    o.append(txt(PAD + 28, ty + 44, "❯", size=16, fill=t["accent"],
                 weight=700, family=MONO))
    o.append(txt(PAD + 52, ty + 44, QUERY, size=16.5, fill=t["text"], family=MONO))

    # streaming pill, right aligned
    pw, px = 150, W - PAD - 28 - 150
    o.append(f'<rect x="{px}" y="{ty + 26}" width="{pw}" height="26" rx="13" '
             f'fill="{t["panel2"]}" stroke="{t["border"]}" stroke-width="1"/>')
    o.append(f'<circle cx="{px + 17}" cy="{ty + 39}" r="4" fill="{t["accent"]}"/>')
    o.append(txt(px + 30, ty + 43, "VERIFIED", size=10.5, fill=t["muted"],
                 weight=700, spacing="2", family=MONO))

    cx = PAD + 28
    for i, c in enumerate(CHIPS):
        cw = 13 + 9.1 * len(c)
        o.append(f'<rect x="{cx}" y="{ty + 68}" width="{cw}" height="30" rx="8" '
                 f'fill="{t["panel2"]}" stroke="{t["border"]}" stroke-width="1"/>')
        o.append(txt(cx + cw / 2, ty + 88, c, size=11, fill=t["muted"],
                     weight=700, spacing="1.9", family=MONO, anchor="middle"))
        cx += cw
        if i < len(CHIPS) - 1:
            o.append(txt(cx + 11, ty + 88, "›", size=14, fill=t["dim"],
                         family=MONO, anchor="middle"))
            cx += 22
    o.append(txt(PAD + 28, ty + 142, ANSWER, size=15.5, fill=t["muted"], family=MONO))

    # ---- identity
    y = ty + th + 62
    o.append(f'<rect x="{PAD}" y="{y - 46}" width="5" height="62" rx="2.5" '
             f'fill="url(#accent-{theme})"/>')
    o.append(txt(PAD + 22, y, NAME, size=57, fill=t["text"], weight=800, spacing="7"))
    y += 44
    o.append(txt(PAD + 24, y, ROLE, size=20.5, fill=t["text"], weight=700))
    y += 30
    o.append(txt(PAD + 24, y, PITCH, size=16, fill=t["muted"]))
    y += 27
    o.append(txt(PAD + 24, y, AFFIL, size=13.5, fill=t["dim"]))

    # ---- what I build
    y += 66
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

    y += 32 + 2 * 24 + 10 + 78

    # ---- architecture
    o.append(section(t, y, "ARCHITECTURE"))
    y += 40
    o.append(txt(PAD, y, "the request", size=13, fill=t["dim"]))
    y += 22

    bw, bh, gap = 260, 74, 32
    total = len(REQUEST) * bw + (len(REQUEST) - 1) * gap
    x0 = PAD + (INNER - total) / 2
    for i, (title, sub) in enumerate(REQUEST):
        bx = x0 + i * (bw + gap)
        o.append(flow_box(t, bx, y, bw, bh, title, sub))
        if i < len(REQUEST) - 1:
            o.append(arrow(t, bx + bw + 8, y + bh / 2))

    # the dashed return path, drawn under the row
    ly = y + bh + 30
    o.append(f'<path d="M{x0 + 30} {y + bh} V{ly} H{x0 + total - 30} V{y + bh}" '
             f'fill="none" stroke="{t["border"]}" stroke-width="1.2" '
             f'stroke-dasharray="4 5"/>')
    o.append(txt(W / 2, ly + 26, REQUEST_NOTE, size=13, fill=t["dim"], anchor="middle"))

    y = ly + 62
    o.append(txt(PAD, y, "PLATFORM", size=11, fill=t["accent"], weight=700, spacing="2.4"))
    o.append(txt(PAD + 116, y, "the services every request runs on", size=13, fill=t["dim"]))
    y += 20

    pbw = (INNER - 3 * gap) / 4
    for i, (title, sub) in enumerate(PLATFORM):
        bx = PAD + i * (pbw + gap)
        o.append(flow_box(t, bx, y, pbw, bh, title, sub))
        if i < len(PLATFORM) - 1:
            o.append(arrow(t, bx + pbw + 8, y + bh / 2))

    height = y + bh + 56

    defs = f'''<defs>
    <linearGradient id="accent-{theme}" x1="0%" y1="100%" x2="0%" y2="0%">
      <stop offset="0%" stop-color="{t["accent"]}"/>
      <stop offset="55%" stop-color="{t["accent2"]}"/>
      <stop offset="100%" stop-color="{t["accent4"]}"/>
    </linearGradient>
    <radialGradient id="halo-{theme}" cx="78%" cy="12%" r="52%">
      <stop offset="0%" stop-color="{t["accent2"]}" stop-opacity="{t["halo"]}"/>
      <stop offset="100%" stop-color="{t["bg"]}" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="card-{theme}"><rect x="1" y="1" width="{W - 2}" height="{height - 2}" rx="20"/></clipPath>
  </defs>'''

    body = "".join(o)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {height}" width="{W}" height="{height}" role="img" aria-label="{esc(ALT)}">
  <title>{esc(NAME.title())} — {esc(ROLE)}</title>
  {defs}
  <rect x="1" y="1" width="{W - 2}" height="{height - 2}" rx="20" fill="{t["bg"]}"/>
  <g clip-path="url(#card-{theme})"><rect width="{W}" height="{height}" fill="url(#halo-{theme})"/>{body}</g>
  <rect x="1" y="1" width="{W - 2}" height="{height - 2}" rx="20" fill="none" stroke="{t["border"]}" stroke-width="1.5"/>
</svg>'''


ALT = (
    "A question typed at the top of the card, what actually makes regulated software "
    "trustworthy, routed through four steps, scan, verify, explain, report, and answered: "
    "the source stays authoritative, I build the layer that makes it usable. Abdullah Al "
    "Tamimi, technical founder and product engineer, building the layer between "
    "authoritative data and the person who has to act on it, 9XAI Fellow at Al Hussein "
    "Technical University in Jordan. What I build: healthcare, GS1 pack verification, "
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
    "issue to its root cause, in FastAPI, PostgreSQL, Redis, Docker and pandas. Architecture: "
    "the request travels scan, GS1 DataMatrix, to profile, Supabase row-level security, to "
    "smart view, OpenAI, to report, MedDRA to E2B, and the official leaflet stays the "
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
