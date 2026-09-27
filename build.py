"""Generates every image used by README.md.

GitHub's markdown sanitizer strips style/class/id from raw HTML, so the profile
design has to live inside images. Run `python3 build.py` and commit assets/.

Embedded SVG keeps to a single system font stack (no @font-face, no
foreignObject, no external refs) so it renders identically through
raw.githubusercontent.com + camo, in both GitHub themes.
"""

import html
import os

from icons import ICONS

OUT = 'assets'
W, PAD = 920, 26
RIGHT = W - PAD

# ── tokens ────────────────────────────────────────────────────────────────────
INK, PANEL, BAR = '#0A0F14', '#0D141B', '#0E151D'
LINE, HAIR = '#1B2530', '#16212C'
CHIP, CHIP_LINE = '#16212C', '#223040'
TEAL, TEAL_DIM, SLATE, DIM, BRIGHT = '#2dd4bf', '#14B8A6', '#8FA9BE', '#5A7186', '#E6EDF3'

MONO = "Menlo,Consolas,'DejaVu Sans Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
MA = 0.602  # Menlo advance width ratio, used to size and align text


def esc(t):
    return html.escape(t, quote=False)


def mono_w(text, size, ls=0.0):
    return len(text) * MA * size + max(len(text) - 1, 0) * ls


def txt(x, y, text, *, size, fill, font=MONO, ls=0.0, weight=None, anchor=None):
    """`anchor` maps straight to SVG text-anchor; x stays the true anchor point."""
    a = f' text-anchor="{anchor}"' if anchor else ''
    w = f' font-weight="{weight}"' if weight else ''
    return (f'<text x="{round(x, 2)}" y="{y}" font-family="{font}" font-size="{size}" '
            f'letter-spacing="{ls}" fill="{fill}"{w}{a}>{esc(text)}</text>')


def svg(width, height, title, desc, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}" role="img" aria-labelledby="t d">'
            f'<title id="t">{esc(title)}</title><desc id="d">{esc(desc)}</desc>'
            f'{body}</svg>\n')


def write(name, markup):
    os.makedirs(OUT, exist_ok=True)
    with open(f'{OUT}/{name}', 'w', encoding='utf-8') as f:
        f.write(markup)
    print(f'  {name:24} {len(markup) / 1024:5.1f} KB')


def icon(name, x, y, size, color):
    s = size / 24.0
    paths = ''.join(f'<path d="{d}" fill="{color}"/>' for d in ICONS[name])
    return f'<g transform="translate({x:.2f},{y:.2f}) scale({s:.5f})">{paths}</g>'


def linkedin_mark(x, y, size, color):
    """The 'in' glyph on a 24-unit grid: dot over stem, then a squared arch."""
    def r(ux, uy, uw, uh, rx=0):
        return (f'<rect x="{x + ux * size / 24:.2f}" y="{y + uy * size / 24:.2f}" '
                f'width="{uw * size / 24:.2f}" height="{uh * size / 24:.2f}" '
                f'rx="{rx * size / 24:.2f}" fill="{INK}"/>')
    dot_r = 2.1 * size / 24
    return (f'<rect x="{x:.2f}" y="{y:.2f}" width="{size:.2f}" height="{size:.2f}" '
            f'rx="{5.4 * size / 24:.2f}" fill="{color}"/>'
            f'<circle cx="{x + 7.2 * size / 24:.2f}" cy="{y + 6.6 * size / 24:.2f}" '
            f'r="{dot_r:.2f}" fill="{INK}"/>'
            + r(4.4, 11.2, 3.4, 8.8, 0.6)
            + r(10.6, 11.2, 8.8, 3.0, 0.6)
            + r(16.0, 11.2, 3.4, 8.8, 0.6))


def glyph(kind, x, y, size, color):
    return icon(kind, x, y, size, color) if kind in ICONS else linkedin_mark(x, y, size, color)


def card(title, sub, body, h):
    head = txt(PAD, 34, f'/ {title}', size=11, fill=BRIGHT, ls=1.9)
    if sub:
        head += txt(RIGHT, 34, sub, size=9.5, fill=DIM, ls=1.5, anchor='end')
    return (f'<rect x="0.5" y="0.5" width="{W-1}" height="{h-1}" rx="14" fill="{PANEL}" stroke="{LINE}"/>'
            f'{head}<line x1="{PAD}" y1="48.5" x2="{RIGHT}" y2="48.5" stroke="{LINE}"/>{body}')


# ── 1. hero ───────────────────────────────────────────────────────────────────
H = 250
TB, SB, TABW, DOT = 40, 36, 128, 15  # title bar, status bar, tab width, dot pitch
hero = [
    '<defs>',
    '<linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">'
    f'<stop offset="0" stop-color="{TEAL}"/><stop offset="0.32" stop-color="#7fd7c8"/>'
    f'<stop offset="0.68" stop-color="{SLATE}"/><stop offset="1" stop-color="#334155"/></linearGradient>',
    f'<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">'
    f'<stop offset="0" stop-color="{TEAL}" stop-opacity="0.10"/>'
    f'<stop offset="1" stop-color="{TEAL}" stop-opacity="0"/></radialGradient>',
    f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="14"/></clipPath>',
    '</defs>',
    '<g clip-path="url(#frame)">',
    f'<rect width="{W}" height="{H}" fill="{INK}"/>',
    '<ellipse cx="320" cy="120" rx="380" ry="126" fill="url(#glow)"/>',
    f'<rect width="{W}" height="2" fill="url(#edge)"/>',
    # window title bar
    f'<rect y="2" width="{W}" height="{TB - 2}" fill="{BAR}"/>',
    f'<line x1="0" y1="{TB}.5" x2="{W}" y2="{TB}.5" stroke="{LINE}"/>',
]
for i in range(3):
    hero.append(f'<circle cx="{PAD + i * DOT}" cy="{TB / 2 + 2}" r="4.5" fill="#33475A"/>')
TABX = PAD + 3 * DOT + 6
hero += [
    f'<rect x="{TABX}" y="8" width="{TABW}" height="24" rx="6" fill="#101820" stroke="{LINE}"/>',
    txt(TABX + 14, 24, '~/njituew', size=10, fill=SLATE, ls=0.6),
    txt(RIGHT, 24, 'zsh', size=9.5, fill=DIM, ls=1, anchor='end'),
    # prompt, name, role, positioning line
    f'<text x="{PAD}" y="78" font-family="{MONO}" font-size="12" fill="{DIM}">'
    f'<tspan fill="{TEAL}">$</tspan> ./njituew</text>',
    txt(PAD, 130, 'Jahor Makśimavič', size=42, fill=BRIGHT, font=SANS, ls=-0.9, weight=700),
    txt(PAD, 164, 'PYTHON · BACKEND · AI ENGINEERING', size=11.5, fill=TEAL, ls=2.6),
    txt(PAD, 198, 'Python developer. REST APIs, Telegram bots, parsers, PostgreSQL, Docker.',
        size=15, fill=SLATE, font=SANS),
    # tmux-style status bar
    f'<rect y="{H - SB}" width="{W}" height="{SB}" fill="{BAR}"/>',
    f'<line x1="0" y1="{H - SB}.5" x2="{W}" y2="{H - SB}.5" stroke="{LINE}"/>',
    f'<circle cx="{PAD + 6}" cy="{H - SB / 2}" r="4" fill="{TEAL}"/>',
    txt(PAD + 18, H - SB / 2 + 3.5, 'OPEN TO WORK · INTERNSHIPS & JUNIOR BACKEND',
        size=10, fill=SLATE, ls=1.4),
    txt(RIGHT, H - SB / 2 + 3.5, 'HSE UNIVERSITY · B.S. 2027',
        size=10, fill=DIM, ls=1.4, anchor='end'),
    '</g>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="none" stroke="{LINE}"/>',
]
write('hero.svg', svg(W, H, 'Jahor Makśimavič — Python developer',
                      'Python, backend and AI engineering. Open to internships and junior '
                      'backend roles. HSE University, B.S. 2027, Moscow.', ''.join(hero)))

# ── 2. capabilities ───────────────────────────────────────────────────────────
CAPS = [
    ('BACKEND',     'REST API design and development, async Python, auth, clean project structure'),
    ('AI & AGENTS', 'Telegram bots with LLM agents — RAG, vector search, tool calling, LangChain'),
    ('DATA',        'Scrapers and parsers, collection pipelines, Pandas and NumPy analysis'),
    ('DEVOPS',      'Docker deployments, Bash automation, Linux servers'),
    ('HARDWARE',    'Microcontrollers and single-board computers — Arduino, Raspberry Pi, PLD'),
]
ROWH, LABW = 40, 132
body, y = [], 48
for i, (lab, val) in enumerate(CAPS):
    y += ROWH
    if i:
        body.append(f'<line x1="{PAD}" y1="{y - ROWH + .5}" x2="{RIGHT}" y2="{y - ROWH + .5}" stroke="{HAIR}"/>')
    body.append(f'<rect x="{PAD}" y="{y - 24}" width="2" height="16" rx="1" fill="{TEAL_DIM}"/>')
    body.append(txt(PAD + 14, y - 12, lab, size=10.5, fill=TEAL, ls=1.2))
    body.append(txt(PAD + LABW, y - 12, val, size=13.5, fill=SLATE, font=SANS))
h = y + 16
write('capabilities.svg', svg(W, h, 'Capabilities',
                              'Five areas: backend REST APIs; AI agents and RAG; data scraping and '
                              'analysis; DevOps and automation; microcontrollers and single-board '
                              'computers.', card('CAPABILITIES', 'BACKEND · AI · DATA · DEVOPS · HARDWARE',
                                                ''.join(body), h)))

# ── 3. stack ──────────────────────────────────────────────────────────────────
CH, FS, IPAD, ISLOT, GAP, RPAD = 28, 11.5, 10, 14, 7, 11
GROUPS = [
    ('CORE',  TEAL, [('Python 3.12', 'python'), ('FastAPI', 'fastapi'), ('aiogram 3', 'telegram'),
                     ('SQLAlchemy 2.0', 'sqlalchemy'), ('Pydantic v2', 'pydantic'), ('pytest', 'pytest'),
                     ('REST API', None)]),
    ('DATA',  SLATE, [('PostgreSQL 17', 'postgresql'), ('Pandas', 'pandas'), ('NumPy', 'numpy')]),
    ('INFRA', SLATE, [('Docker', 'docker'), ('Git', 'git'), ('Bash', 'gnubash'), ('Linux', 'linux')]),
    ('AI',    TEAL, [('LangChain', 'langchain'), ('RAG', None), ('vector search', None),
                     ('tool calling', None)]),
]


def chip_w(label):
    return round(IPAD + ISLOT + GAP + mono_w(label, FS) + RPAD)


def chip(label, kind, color, x, y):
    w = chip_w(label)
    p = [f'<rect x="{x}" y="{y}" width="{w}" height="{CH}" rx="6" fill="{CHIP}" stroke="{CHIP_LINE}"/>']
    if kind:
        p.append(icon(kind, x + IPAD, y + (CH - ISLOT) / 2, ISLOT, color))
    else:
        p.append(f'<circle cx="{x + IPAD + ISLOT / 2:.1f}" cy="{y + CH / 2}" r="2.4" fill="{color}"/>')
    p.append(txt(x + IPAD + ISLOT + GAP, y + CH / 2 + 4, label, size=FS, fill=BRIGHT))
    return w, ''.join(p)


def wrap(items, maxw):
    rows, cur, cw = [], [], 0
    for lab, kind in items:
        w = chip_w(lab)
        if cur and cw + 8 + w > maxw:
            rows.append(cur)
            cur, cw = [], 0
        cw += (8 if cur else 0) + w
        cur.append((lab, kind, w))
    if cur:
        rows.append(cur)
    return rows


body, y = [], 48
for name, color, items in GROUPS:
    y += 22
    body.append(txt(PAD, y, name, size=9.5, fill=DIM, ls=1.6))
    for row in wrap(items, RIGHT - PAD):
        y += 12
        x = PAD
        for lab, kind, w in row:
            _, p = chip(lab, kind, color, x, y)
            body.append(p)
            x += w + 8
        y += CH + 8
    y -= 8
h = y + 22
write('stack.svg', svg(W, h, 'Stack',
                       'Core: Python 3.12, FastAPI, aiogram 3, SQLAlchemy 2.0, Pydantic v2, pytest, '
                       'REST API. Data: PostgreSQL 17, Pandas, NumPy. Infra: Docker, Git, Bash, Linux. '
                       'AI: LangChain, RAG, vector search, tool calling.',
                       card('STACK', 'WHAT I WORK WITH DAILY', ''.join(body), h)))

# ── 4. contact chips (wrapped in markdown <a> so they stay clickable) ──────────
CH2, ISLOT2 = 36, 16
for label, kind, sub, color, name in [
    ('Telegram', 'telegram', '@zearbyte', TEAL, 'contact-telegram.svg'),
    ('LinkedIn', 'linkedin', 'egor-glinnik', SLATE, 'contact-linkedin.svg'),
]:
    w = round(IPAD + ISLOT2 + GAP + mono_w(label, 12.5) + 20 + mono_w(sub, 11) + RPAD)
    b = (f'<rect x="0.5" y="0.5" width="{w-1}" height="{CH2-1}" rx="8" fill="{CHIP}" stroke="{CHIP_LINE}"/>'
         + glyph(kind, IPAD, (CH2 - ISLOT2) / 2, ISLOT2, color)
         + txt(IPAD + ISLOT2 + GAP, CH2 / 2 + 4.5, label, size=12.5, fill=BRIGHT)
         + txt(w - RPAD, CH2 / 2 + 4.5, sub, size=11, fill=SLATE, anchor='end'))
    write(name, svg(w, CH2, f'{label} {sub}', f'Contact {label}: {sub}', b))
