"""Convert Lucide (ISC) / Tabler (MIT) outline icons into TikZ macros.
Every SVG element is converted to absolute lines and cubic Beziers (arcs included), so the
output needs no TikZ library.  Icons live in a 24x24 box with y pointing down; the caller
flips it (yscale=-1).  Usage: python3 svg2tikz.py L:gpu T:steering-wheel ... > fig1_icons.tex"""
import math, re, sys, xml.etree.ElementTree as ET
ROOT = 'icons'   # folder holding the unpacked lucide-static-1.49.0 and tabler-icons-3.48.0 npm packages
SETS = {'L': ROOT + '/lucide-static-1.49.0/package/icons/',
        'T': ROOT + '/tabler-icons-3.48.0/package/icons/outline/'}
NARGS = dict(M=2, L=2, H=1, V=1, C=6, S=4, Q=4, T=2, A=7, Z=0)
NUM = re.compile(r'[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?')

def f(x):
    s = ('%.3f' % x).rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s

def tokens(d):
    i, cmd, argi = 0, None, 0
    while i < len(d):
        ch = d[i]
        if ch.isspace() or ch == ',': i += 1; continue
        if ch.isalpha(): cmd, argi = ch, 0; yield ch; i += 1; continue
        if cmd.upper() == 'A' and argi % 7 in (3, 4):
            yield float(ch); i += 1
        else:
            m = NUM.match(d, i); yield float(m.group()); i = m.end()
        argi += 1

def arc_to_cubics(x1, y1, rx, ry, phi, fa, fs, x2, y2):
    if (x1, y1) == (x2, y2): return []
    if rx == 0 or ry == 0: return [('L', x2, y2)]
    rx, ry = abs(rx), abs(ry); p = math.radians(phi); cp, sp = math.cos(p), math.sin(p)
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p, y1p = cp * dx + sp * dy, -sp * dx + cp * dy
    lam = x1p**2 / rx**2 + y1p**2 / ry**2
    if lam > 1: rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx**2 * ry**2 - rx**2 * y1p**2 - ry**2 * x1p**2
    den = rx**2 * y1p**2 + ry**2 * x1p**2
    co = math.sqrt(max(0, num / den)) * (-1 if fa == fs else 1)
    cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
    cx, cy = cp * cxp - sp * cyp + (x1 + x2) / 2, sp * cxp + cp * cyp + (y1 + y2) / 2
    ang = lambda ux, uy, vx, vy: math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
    t1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not fs and dt > 0: dt -= 2 * math.pi
    if fs and dt < 0: dt += 2 * math.pi
    n = max(1, math.ceil(abs(dt) / (math.pi / 2) - 1e-9)); d = dt / n
    k = 4 / 3 * math.tan(d / 4); segs = []
    pt = lambda t: (cx + rx * math.cos(t) * cp - ry * math.sin(t) * sp, cy + rx * math.cos(t) * sp + ry * math.sin(t) * cp)
    der = lambda t: (-rx * math.sin(t) * cp - ry * math.cos(t) * sp, -rx * math.sin(t) * sp + ry * math.cos(t) * cp)
    for i in range(n):
        a, b = t1 + i * d, t1 + (i + 1) * d
        (ax, ay), (bx, by) = pt(a), pt(b); (dax, day), (dbx, dby) = der(a), der(b)
        segs.append(('C', ax + k * dax, ay + k * day, bx - k * dbx, by - k * dby, bx, by))
    return segs

def path_to_tikz(d):
    out, cur, start, last_c, last_q, cmd = [], (0, 0), (0, 0), None, None, None
    toks = list(tokens(d)); i = 0
    def take(n):
        nonlocal i; v = toks[i:i + n]; i += n; return v
    while i < len(toks):
        if isinstance(toks[i], str): cmd = toks[i]; i += 1
        C, rel = cmd.upper(), cmd.islower()
        if C == 'Z':
            out.append('-- cycle'); cur = start; last_c = last_q = None
            continue
        a = take(NARGS[C]); ox, oy = cur if rel else (0, 0)
        if C == 'M':
            cur = start = (ox + a[0], oy + a[1]); out.append('(%s,%s)' % (f(cur[0]), f(cur[1])))
            cmd = 'l' if rel else 'L'; last_c = last_q = None; continue
        if C in 'LHV':
            x = (ox + a[0]) if C in 'LH' else cur[0]
            y = (oy + a[1]) if C == 'L' else ((oy + a[0]) if C == 'V' else cur[1])
            if C == 'H': x = (cur[0] + a[0]) if rel else a[0]
            if C == 'V': y = (cur[1] + a[0]) if rel else a[0]
            cur = (x, y); out.append('-- (%s,%s)' % (f(x), f(y))); last_c = last_q = None; continue
        if C in 'CS':
            if C == 'C': c1 = (ox + a[0], oy + a[1]); c2 = (ox + a[2], oy + a[3]); e = (ox + a[4], oy + a[5])
            else:
                c1 = (2 * cur[0] - last_c[0], 2 * cur[1] - last_c[1]) if last_c else cur
                c2 = (ox + a[0], oy + a[1]); e = (ox + a[2], oy + a[3])
            out.append('.. controls (%s,%s) and (%s,%s) .. (%s,%s)' % tuple(map(f, (*c1, *c2, *e))))
            last_c, last_q, cur = c2, None, e; continue
        if C in 'QT':
            if C == 'Q': q = (ox + a[0], oy + a[1]); e = (ox + a[2], oy + a[3])
            else: q = (2 * cur[0] - last_q[0], 2 * cur[1] - last_q[1]) if last_q else cur; e = (ox + a[0], oy + a[1])
            c1 = (cur[0] + 2 / 3 * (q[0] - cur[0]), cur[1] + 2 / 3 * (q[1] - cur[1]))
            c2 = (e[0] + 2 / 3 * (q[0] - e[0]), e[1] + 2 / 3 * (q[1] - e[1]))
            out.append('.. controls (%s,%s) and (%s,%s) .. (%s,%s)' % tuple(map(f, (*c1, *c2, *e))))
            last_q, last_c, cur = q, None, e; continue
        if C == 'A':
            e = (ox + a[5], oy + a[6])
            for s in arc_to_cubics(*cur, a[0], a[1], a[2], int(a[3]), int(a[4]), *e):
                if s[0] == 'L': out.append('-- (%s,%s)' % (f(s[1]), f(s[2])))
                else: out.append('.. controls (%s,%s) and (%s,%s) .. (%s,%s)' % tuple(map(f, s[1:])))
            if (cur) == e: pass
            cur = e; last_c = last_q = None; continue
    # a zero-length segment (Lucide's "dot" idiom, e.g. M7 14h.01) becomes a small filled dot
    return ' '.join(out)

def convert(setkey, name):
    root = ET.parse(SETS[setkey] + name + '.svg').getroot(); out = []
    for el in root.iter():
        tag = el.tag.split('}')[-1]; a = el.attrib
        if tag == 'path':
            if a.get('stroke') == 'none': continue          # Tabler's invisible 24x24 frame
            p = path_to_tikz(a['d'])
            m = re.fullmatch(r'\((-?[\d.]+),(-?[\d.]+)\) -- \((-?[\d.]+),(-?[\d.]+)\)', p)
            if m and math.dist(tuple(map(float, m.groups()[:2])), tuple(map(float, m.groups()[2:]))) < 0.05:
                out.append(r'\fill (%s,%s) circle (1);' % m.groups()[:2]); continue
            out.append(r'\draw %s;' % p)
        elif tag == 'circle':
            out.append(r'\draw (%s,%s) circle (%s);' % tuple(f(float(a[k])) for k in ('cx', 'cy', 'r')))
        elif tag == 'ellipse':
            out.append(r'\draw (%s,%s) ellipse (%s and %s);' % tuple(f(float(a[k])) for k in ('cx', 'cy', 'rx', 'ry')))
        elif tag == 'rect':
            rx = float(a.get('rx', 0)); rc = '[rounded corners=%s\\icou]' % f(rx) if rx else ''
            out.append(r'\draw%s (%s,%s) rectangle ++(%s,%s);' % (rc, *(f(float(a.get(k, 0))) for k in ('x', 'y', 'width', 'height'))))
        elif tag == 'line':
            out.append(r'\draw (%s,%s) -- (%s,%s);' % tuple(f(float(a[k])) for k in ('x1', 'y1', 'x2', 'y2')))
        elif tag in ('polyline', 'polygon'):
            v = [float(x) for x in NUM.findall(a['points'])]
            pts = ' -- '.join('(%s,%s)' % (f(v[j]), f(v[j + 1])) for j in range(0, len(v), 2))
            out.append(r'\draw %s%s;' % (pts, ' -- cycle' if tag == 'polygon' else ''))
    return out

if __name__ == '__main__':
    for spec in sys.argv[1:]:
        k, n = spec.split(':')
        print(r'\expandafter\def\csname ico@%s\endcsname{%s}' % ((k + n).replace('-', ''), ' '.join(convert(k, n))))
