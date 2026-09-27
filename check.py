"""Sanity-checks the generated SVGs: bounds, overflow, clipping.

Run after build.py. Estimates text extents with the same metrics build.py uses,
so a run that passes here should not clip on GitHub either.
"""
import glob
import re
import sys

from icons import ICONS

MA = 0.602
SANS_RATIO = 0.52  # -apple-system / Segoe UI average advance ratio
problems = []


def mono_w(t, size, ls=0.0):
    return len(t) * MA * size + max(len(t) - 1, 0) * ls


def plain(t):
    return (t.replace('&amp;', '&').replace('&#183;', '·').replace('&mdash;', '—')
             .replace('&middot;', '·'))


def check(path):
    src = open(path, encoding='utf-8').read()
    W, H = (float(v) for v in re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', src).groups())
    name = path.split('/')[-1]
    clipped = '<clipPath' in src
    boxes = []

    for tag, attrs in re.findall(r'<(rect|circle|line|ellipse)\s([^>]*?)>', src):
        a = dict(re.findall(r'([\w-]+)="([^"]*)"', attrs))
        if tag == 'rect' and a.get('width') and float(a['width']) > W:
            problems.append(f'{name}: rect wider than viewBox ({a["width"]} > {W})')
        if tag == 'ellipse' and not clipped:
            cx, rx = float(a['cx']), float(a['rx'])
            if cx - rx < 0 or cx + rx > W:
                problems.append(f'{name}: unclipped ellipse escapes viewBox')

    for m in re.finditer(r'<text x="([\d.-]+)" y="([\d.-]+)"([^>]*)>(.*?)</text>', src, re.S):
        x, y = float(m.group(1)), float(m.group(2))
        attrs, inner = m.group(3), m.group(4)
        a = dict(re.findall(r'([\w-]+)="([^"]*)"', attrs))
        size, ls = float(a.get('font-size', 12)), float(a.get('letter-spacing', 0))
        anchor = a.get('text-anchor', 'start')
        text = re.sub(r'\s+', ' ', plain(re.sub(r'<[^>]+>', '', inner))).strip()
        w = mono_w(text, size, ls) if 'Menlo' in a.get('font-family', '') \
            else len(text) * SANS_RATIO * size
        x0 = x - w / 2 if anchor == 'middle' else x - w if anchor == 'end' else x
        if x0 < -0.5:
            problems.append(f'{name}: text "{text[:36]}" starts at {x0:.0f}, outside viewBox')
        if x0 + w > W + 0.5:
            problems.append(f'{name}: text "{text[:36]}" ends at {x0 + w:.0f} > {W}, CLIPS')
        if not 0 < y < H:
            problems.append(f'{name}: text "{text[:36]}" baseline y={y} outside 0..{H:.0f}')
        boxes.append((y - size * 0.8, y + size * 0.25, x0, x0 + w, text))

    for i, (t0, b0, l0, r0, s0) in enumerate(boxes):
        for t1, b1, l1, r1, s1 in boxes[i + 1:]:
            if t0 < b1 and t1 < b0 and l0 < r1 and l1 < r0:
                problems.append(f'{name}: "{s0[:24]}" overlaps "{s1[:24]}"')

    return W, H


for p in sorted(glob.glob('assets/*.svg')):
    w, h = check(p)
    print(f'  {p:30} {w:>4.0f} x {h:<4.0f}')

src = open('build.py', encoding='utf-8').read()
groups = re.search(r'GROUPS = \[(.*?)\n\]', src, re.S).group(1)
unknown = set(re.findall(r"'([a-z][a-z0-9]*)'", groups)) - set(ICONS)
if unknown:
    problems.append(f'build.py GROUPS reference unknown icons: {sorted(unknown)}')

print()
if problems:
    print('FAIL')
    for x in problems:
        print('  -', x)
    sys.exit(1)
print(f'OK - no overflow or clipping; {len(ICONS)} icon names resolve')
