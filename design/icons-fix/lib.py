"""Примитивы для сборки иконок: контуры через skia-pathops (булевы операции,
обводка с нужными окончаниями), ввод/вывод SVG-путей через fontTools."""
import math, io
import pathops
from pathops import Path, PathOp, LineCap, LineJoin
from fontTools.svgLib.path import parse_path
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

INK = "#0E0E0E"
LEFT, RIGHT, TOP, BASE = 4.0, 46.0, 7.0, 43.1   # ключевые линии сетки 50×50

GRADIENTS = {
    "blue":  ("#003DA5", "#2CD5C4", "#00A9E0"),
    "green": ("#00843D", "#47D7AC", "#DDF314"),
    "red":   ("#E4002B", "#FFC851", "#FF6900"),
}

def P(d, m=None):
    """d-строка → Path; m — аффинная матрица (a, b, c, d, e, f)."""
    p = Path()
    pen = p.getPen()
    if m: pen = TransformPen(pen, m)
    parse_path(d, pen)
    return p

def union(*ps):
    ps = [p for p in ps if p is not None]
    out = ps[0]
    for p in ps[1:]:
        out = pathops.op(out, p, PathOp.UNION)
    return out

def diff(a, *bs):
    for b in bs:
        a = pathops.op(a, b, PathOp.DIFFERENCE)
    return a

def inter(a, b):
    return pathops.op(a, b, PathOp.INTERSECTION)

def poly(*pts):
    p = Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    p.close(); return p

def rect(x, y, w, h, r=0.0):
    if r <= 0:
        return poly((x, y), (x + w, y), (x + w, y + h), (x, y + h))
    r = min(r, w / 2, h / 2); k = r * 0.5523
    p = Path()
    p.moveTo(x + r, y); p.lineTo(x + w - r, y)
    p.cubicTo(x + w - r + k, y, x + w, y + r - k, x + w, y + r); p.lineTo(x + w, y + h - r)
    p.cubicTo(x + w, y + h - r + k, x + w - r + k, y + h, x + w - r, y + h); p.lineTo(x + r, y + h)
    p.cubicTo(x + r - k, y + h, x, y + h - r + k, x, y + h - r); p.lineTo(x, y + r)
    p.cubicTo(x, y + r - k, x + r - k, y, x + r, y); p.close()
    return p

def rect2(x0, y0, x1, y1, r=0.0):
    return rect(x0, y0, x1 - x0, y1 - y0, r)

def circle(cx, cy, r):
    k = r * 0.5523; p = Path()
    p.moveTo(cx + r, cy)
    p.cubicTo(cx + r, cy + k, cx + k, cy + r, cx, cy + r)
    p.cubicTo(cx - k, cy + r, cx - r, cy + k, cx - r, cy)
    p.cubicTo(cx - r, cy - k, cx - k, cy - r, cx, cy - r)
    p.cubicTo(cx + k, cy - r, cx + r, cy - k, cx + r, cy)
    p.close(); return p

def line_path(pts, closed=False):
    p = Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    if closed: p.close()
    return p

def stroke(p, width, cap="butt", join="miter", miter=4.0):
    caps = {"butt": LineCap.BUTT_CAP, "round": LineCap.ROUND_CAP, "square": LineCap.SQUARE_CAP}
    joins = {"miter": LineJoin.MITER_JOIN, "round": LineJoin.ROUND_JOIN, "bevel": LineJoin.BEVEL_JOIN}
    q = Path(); q.addPath(p)
    q.stroke(width, caps[cap], joins[join], miter)
    q.convertConicsToQuads()
    return union(q, Path())   # приводим к простому контуру без самопересечений

def tf(p, m):
    q = Path(); p.draw(TransformPen(q.getPen(), m)); return q

def move(p, dx, dy): return tf(p, (1, 0, 0, 1, dx, dy))
def flip_x(p, axis=25.0): return tf(p, (-1, 0, 0, 1, 2 * axis, 0))
def scale(p, s, cx=25.0, cy=25.0): return tf(p, (s, 0, 0, s, cx - s * cx, cy - s * cy))

def canvas_clip(p, x0=LEFT, y0=0.0, x1=50.0, y1=BASE):
    return inter(p, rect2(x0, y0, x1, y1))

class _Round(SVGPathPen):
    def __init__(self, nd=2):
        super().__init__(None, ntos=lambda v: (f"{v:.{nd}f}".rstrip("0").rstrip(".") or "0"))

def to_d(p, nd=2):
    pen = _Round(nd); p.draw(pen); return pen.getCommands()

def bounds(p): return p.bounds

def svg(p, fill=INK, size=50, grad=None):
    d = to_d(p)
    if grad:
        a, b, c = GRADIENTS[grad]
        defs = (f'<defs><linearGradient id="g" x1="0" y1="50" x2="50" y2="0" gradientUnits="userSpaceOnUse">'
                f'<stop stop-color="{a}"/><stop offset=".35" stop-color="{b}"/><stop offset=".7" stop-color="{c}"/>'
                f'</linearGradient></defs>')
        return (f'<svg width="{size}" height="{size}" viewBox="0 0 50 50" fill="none" xmlns="http://www.w3.org/2000/svg">'
                f'{defs}<path d="{d}" fill="url(#g)"/></svg>')
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 50 50" fill="none" xmlns="http://www.w3.org/2000/svg">'
            f'<path d="{d}" fill="{fill}"/></svg>')

def contour_points(p, step=0.25):
    """Точки вдоль контура (для замеров зазоров)."""
    pts = []
    for contour in p.contours:
        cur = None
        for verb, seg in contour.segments:
            if verb == "moveTo": cur = seg[0]
            elif verb == "lineTo":
                a, b = cur, seg[0]; n = max(1, int(math.dist(a, b) / step))
                pts += [(a[0] + (b[0]-a[0])*i/n, a[1] + (b[1]-a[1])*i/n) for i in range(n)]; cur = b
            elif verb in ("curveTo", "qCurveTo"):
                ctrl = [cur] + list(seg)
                if verb == "qCurveTo" and len(ctrl) == 3:
                    q0, q1, q2 = ctrl; ctrl = [q0, (q0[0]+2/3*(q1[0]-q0[0]), q0[1]+2/3*(q1[1]-q0[1])),
                                               (q2[0]+2/3*(q1[0]-q2[0]), q2[1]+2/3*(q1[1]-q2[1])), q2]
                if len(ctrl) == 4:
                    n = 40
                    for i in range(n):
                        t = i / n; u = 1 - t
                        pts.append(tuple(u**3*ctrl[0][k] + 3*u*u*t*ctrl[1][k] + 3*u*t*t*ctrl[2][k] + t**3*ctrl[3][k] for k in (0, 1)))
                cur = seg[-1]
            elif verb == "closePath": pass
    return pts

def min_gap(p, q):
    a, b = contour_points(p), contour_points(q)
    return min(math.dist(x, y) for x in a[::2] for y in b[::2])

def dilate(p, r, join="round"):
    """Контур, раздутый на r (для «просвета» между передним и задним планом)."""
    q = Path(); q.addPath(p)
    q.stroke(2 * r, LineCap.ROUND_CAP if join == "round" else LineCap.BUTT_CAP,
             LineJoin.ROUND_JOIN if join == "round" else LineJoin.MITER_JOIN, 4)
    q.convertConicsToQuads()
    return union(p, q)

GAP = 1.6   # стандартный просвет пака
