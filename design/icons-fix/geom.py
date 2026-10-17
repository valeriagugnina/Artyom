"""Геометрия для иконок: полосы переменной ширины вдоль кубической кривой Безье.
Смещение контура — по Тиллеру–Хэнсону на подразбитых сегментах, поэтому
на выходе чистые кубические кривые, а не ломаная."""
import math

def lerp(a, b, t): return (a[0] + (b[0]-a[0])*t, a[1] + (b[1]-a[1])*t)
def sub(a, b): return (a[0]-b[0], a[1]-b[1])
def add(a, b): return (a[0]+b[0], a[1]+b[1])
def mul(a, k): return (a[0]*k, a[1]*k)
def norm(v):
    l = math.hypot(*v) or 1.0
    return (v[0]/l, v[1]/l)
def perp(v): return (-v[1], v[0])

def split(c, t):
    p0, p1, p2, p3 = c
    a, b, cc = lerp(p0, p1, t), lerp(p1, p2, t), lerp(p2, p3, t)
    d, e = lerp(a, b, t), lerp(b, cc, t)
    f = lerp(d, e, t)
    return (p0, a, d, f), (f, e, cc, p3)

def point(c, t):
    p0, p1, p2, p3 = c; u = 1-t
    return (u**3*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t**3*p3[0],
            u**3*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t**3*p3[1])

def tangent(c, t):
    p0, p1, p2, p3 = c; u = 1-t
    return norm((3*u*u*(p1[0]-p0[0])+6*u*t*(p2[0]-p1[0])+3*t*t*(p3[0]-p2[0]),
                 3*u*u*(p1[1]-p0[1])+6*u*t*(p2[1]-p1[1])+3*t*t*(p3[1]-p2[1])))

def intersect(p, d, q, e):
    den = d[0]*e[1]-d[1]*e[0]
    if abs(den) < 1e-9: return None
    t = ((q[0]-p[0])*e[1]-(q[1]-p[1])*e[0])/den
    return add(p, mul(d, t))

def offset_cubic(c, w0, w1, side):
    """Смещает кубику на полуширину w0→w1 (side=+1 слева, −1 справа)."""
    p0, p1, p2, p3 = c
    t0, t3 = tangent(c, 0), tangent(c, 1)
    n0, n3 = mul(perp(t0), side), mul(perp(t3), side)
    q0, q3 = add(p0, mul(n0, w0)), add(p3, mul(n3, w1))
    # средний отрезок контрольного многоугольника
    dm = norm(sub(p2, p1)) if math.hypot(*sub(p2, p1)) > 1e-6 else t0
    nm = mul(perp(dm), side)
    wm = (w0+w1)/2
    m1, m2 = add(p1, mul(nm, wm)), add(p2, mul(nm, wm))
    q1 = intersect(q0, t0, m1, dm) or add(p1, mul(n0, w0))
    q2 = intersect(q3, t3, m2, dm) or add(p2, mul(n3, w1))
    return (q0, q1, q2, q3)

def fit_piece(pts, d0, d3):
    """Кубика через крайние точки pts с касательными d0/d3; длины ручек — МНК
    по хордовой параметризации, с ограничением, чтобы не было петель."""
    p0, p3 = pts[0], pts[-1]
    acc = [0.0]
    for a, b in zip(pts, pts[1:]): acc.append(acc[-1] + math.hypot(*sub(b, a)))
    ts = [v / acc[-1] for v in acc]
    A = [[0.0, 0.0], [0.0, 0.0]]; r = [0.0, 0.0]
    for p, t in zip(pts, ts):
        u = 1 - t
        b0, b1, b2, b3 = u**3, 3*u*u*t, 3*u*t*t, t**3
        base = add(mul(p0, b0 + b1), mul(p3, b2 + b3))
        cs = (mul(d0, b1), mul(d3, -b2)); res = sub(p, base)
        for i in range(2):
            for j in range(2): A[i][j] += cs[i][0]*cs[j][0] + cs[i][1]*cs[j][1]
            r[i] += cs[i][0]*res[0] + cs[i][1]*res[1]
    chord = math.hypot(*sub(p3, p0)); det = A[0][0]*A[1][1] - A[0][1]*A[1][0]
    if abs(det) < 1e-9:
        al = be = chord / 3
    else:
        al = (r[0]*A[1][1] - r[1]*A[0][1]) / det
        be = (A[0][0]*r[1] - A[1][0]*r[0]) / det
    lo, hi = 0.05 * chord, 0.75 * chord
    al, be = min(max(al, lo), hi), min(max(be, lo), hi)
    return (p0, add(p0, mul(d0, al)), sub(p3, mul(d3, be)), p3)

def band(c, w_start, w_end, parts=4, n=24):
    """Полоса вдоль кубики c, ширина линейно w_start → w_end. Кромки считаются
    точно (точка ± нормаль·полуширина) и аппроксимируются parts кубиками каждая."""
    W = lambda t: (w_start + (w_end - w_start) * t) / 2
    def edge(t, side): return add(point(c, t), mul(perp(tangent(c, t)), side * W(t)))
    def etan(t, side):
        h = 1e-4; a, b = edge(max(0, t - h), side), edge(min(1, t + h), side)
        return norm(sub(b, a))
    out = {}
    for side in (+1, -1):
        segs = []
        for k in range(parts):
            ta, tb = k / parts, (k + 1) / parts
            pts = [edge(ta + (tb - ta) * i / n, side) for i in range(n + 1)]
            segs.append(fit_piece(pts, etan(ta, side), etan(tb, side)))
        out[side] = segs
    f = lambda p: f"{p[0]:.3f} {p[1]:.3f}"
    left, right = out[+1], out[-1]
    d = "M" + f(left[0][0])
    for q in left: d += " C" + f(q[1]) + " " + f(q[2]) + " " + f(q[3])
    d += " L" + f(right[-1][3])
    for q in reversed(right): d += " C" + f(q[2]) + " " + f(q[1]) + " " + f(q[0])
    return d + " Z"

def bez(p0, d0, k0, p3, d3, k3):
    """Кубика из точек и направлений касательных."""
    d0, d3 = norm(d0), norm(d3)
    return (p0, add(p0, mul(d0, k0)), sub(p3, mul(d3, k3)), p3)
