"""Генератор исправленных иконок. Каждая функция возвращает один контур (Path).
Запуск: python3 icons.py [имя ...] — пишет build/<имя>.svg и build/<имя>-grad.svg."""
import json, math, os, sys
from geom import point, tangent, norm, perp, add, sub, mul, band, bez, fit_piece, band_fn
from lib import *

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = json.load(open(os.path.join(HERE, "src/icons_export.json")))

def src_path(node_id):
    """Исходный контур иконки из выгрузки Фигмы (все path внутри svg)."""
    import re
    svg = SRC[node_id]["svg"]
    ds = re.findall(r'<path[^>]* d="([^"]+)"', svg)
    return union(*[P(d) for d in ds])

# ── общие элементы ────────────────────────────────────────────────────────────

def fit_cubic(pts, ts, d0, d3):
    return fit_piece(pts, d0, d3)

def flow_family(spine, pitch0, pitch1, offsets, ease=lambda t: t):
    """Семейство «потоков»: центральная кубика spine и её смещения по нормали
    с шагом, меняющимся от pitch0 до pitch1. offsets — номера полос (…−1, 0, 1…)."""
    ts = [i / 60 for i in range(61)]
    out = []
    for s in offsets:
        pts = []
        for t in ts:
            k = pitch0 + (pitch1 - pitch0) * ease(t)
            pts.append(add(point(spine, t), mul(perp(tangent(spine, t)), s * k)))
        out.append(fit_cubic(pts, ts, tangent(spine, 0), tangent(spine, 1)))
    return out

def arrowhead(tip, angle_deg, length, half):
    a = (math.cos(math.radians(angle_deg)), -math.sin(math.radians(angle_deg)))
    n = perp(a)
    b = sub(tip, mul(a, length))
    return poly(tip, add(b, mul(n, half)), sub(b, mul(n, half))), b, a, n

# ── Ф1 · Инвестиции ───────────────────────────────────────────────────────────

def investments(angle=62, tip=(45.6, 4.3), L=9.6, H=5.5, y_start=41.685,
                w0=3.2, w1=2.1, pitch0=6.0, pitch1=3.2, k0=0.42, k3=0.36):
    # y_start подобран так, что нижняя кромка средней полосы приходит ровно в угол (4; 43.1)
    head, B, a, n = arrowhead(tip, angle, L, H)
    end = add(B, mul(a, 1.2))            # заводим полосы внутрь наконечника
    start = (-1.0, y_start)
    dist = math.hypot(*sub(end, start))
    spine = bez(start, (1, 0), dist * k0, end, a, dist * k3)
    bands = [P(band(c, w0, w1, parts=6)) for c in flow_family(spine, pitch0, pitch1, (-1, 0, 1))]
    return canvas_clip(union(head, *bands))

# ── Элемент движения из знака: крылья «К» ─────────────────────────────────────

def logo_wings():
    """Три верхних и три нижних полосы «К» из знака 1256:712 — без букв «З».
    Где полоса срастается с чашей «З», недостающая кромка достроена кубикой
    по касательным соседних сегментов. Координаты — как в знаке (75×62)."""
    logo = src_path("1256:712")
    # над внутренней верхней полосой: её кромка до (30.76; 26.36), достройка до (45.52; 19.13), дальше — родная
    top = Path(); top.moveTo(-5, 27.5161); top.lineTo(21.0194, 27.5161)
    top.cubicTo(21.0194, 27.5161, 25.2056, 27.738, 30.7579, 26.3622)
    t0, t1 = norm((30.7579 - 25.2056, 26.3622 - 27.738)), norm((50.5875 - 45.52, 15.1782 - 19.1281))
    c = bez((30.7579, 26.3622), t0, 5.4, (45.52, 19.1281), t1, 5.0)
    top.cubicTo(*c[1], *c[2], *c[3])
    top.cubicTo(50.5875, 15.1782, 54.4213, 9.9413, 55.0382, 1.42019)
    top.lineTo(55.0382, -5); top.lineTo(-5, -5); top.close()
    # под внутренней нижней полосой: кромка от стыка до (34.06; 35.90), достройка до (47.46; 43.58), дальше — родная
    bot = Path(); bot.moveTo(-5, 33.685); bot.lineTo(21.0635, 33.685)
    bot.cubicTo(21.7685, 33.685, 29.5682, 33.6407, 34.0629, 35.9041)
    t0, t1 = norm((34.0629 - 29.5682, 35.9041 - 33.6407)), norm((51.6892 - 47.4589, 47.4875 - 43.582))
    c = bez((34.0629, 35.9041), t0, 5.2, (47.4589, 43.582), t1, 4.6)
    bot.cubicTo(*c[1], *c[2], *c[3])
    bot.cubicTo(51.6892, 47.4875, 54.7297, 52.7688, 55.1263, 60.5798)
    bot.lineTo(55.1263, 70); bot.lineTo(-5, 70); bot.close()
    keep = rect2(21.11, -5, 80, 70)        # стыковые торцы полос выравниваем в одну вертикаль
    return diff(inter(logo, keep), top, bot)

def _hull_circle(p, c, r, side):
    """Точка касания на окружности (c, r) для касательной из точки p; side=±1 — с какой стороны."""
    d = sub(c, p); L = math.hypot(*d)
    ang = math.atan2(d[1], d[0]); off = math.asin(min(1.0, r / L))
    th = ang + side * (math.pi / 2 + off) + math.pi
    return (c[0] + r * math.cos(th + math.pi), c[1] + r * math.sin(th + math.pi))

# ── Ф3 · Туризм ───────────────────────────────────────────────────────────────

WING_S = (BASE - TOP) / (60.62419 - 1.42019)      # знак по высоте ровно от 7 до 43.1

def wings_placed(mirror, x0):
    """Крылья «К» в сетке: верх 7, низ 43.1, левый край элемента — x0."""
    s = WING_S
    if mirror:   # зеркально: стык справа, полосы уходят влево — движение вправо
        m = (-s, 0, 0, s, x0 + 75.0 * s, TOP - 1.42019 * s)
    else:
        m = (s, 0, 0, s, x0 - 21.11 * s, TOP - 1.42019 * s)
    return tf(logo_wings(), m)

def tourism(variant="bird"):
    s = WING_S; w = (75.0 - 21.11) * s
    if variant == "logo":            # как в знаке
        return wings_placed(False, (50 - w) / 2)
    if variant == "mirror":          # только элемент, движение вправо
        return wings_placed(True, (50 - w) / 2)
    # птица: зеркальные крылья + голова на стыке полос
    x0 = LEFT
    wings = wings_placed(True, x0)
    jx = x0 + w                                  # торец стыка
    y_top, y_bot = TOP + (27.5161 - 1.42019) * s, TOP + (33.685 - 1.42019) * s
    hc, hr = (jx + 4.3, y_top - 1.2), 3.1        # голова
    a = _hull_circle((jx - 0.6, y_top), hc, hr, -1)
    b = _hull_circle((jx - 0.6, y_bot), hc, hr, +1)
    neck = poly((jx - 0.6, y_top), a, hc, b, (jx - 0.6, y_bot))
    beak = poly((hc[0] + 1.0, hc[1] - 2.95), (RIGHT, hc[1] - 1.3), (hc[0] + 2.7, hc[1] + 0.4))
    return union(wings, neck, circle(*hc, hr), beak)

# ── Логистический коридор ─────────────────────────────────────────────────────

def straight_arrow(x_tail, x_tip, y, stripes=3, w=3.0, g=1.6, L=11.0, H=8.1, solid=False):
    """Горизонтальная стрелка: пучок полос (или сплошное древко) + наконечник.
    x_tip > x_tail — стрелка вправо, иначе влево."""
    sgn = 1 if x_tip > x_tail else -1
    xb = x_tip - sgn * L                      # основание наконечника
    head = poly((x_tip, y), (xb, y - H), (xb, y + H))
    span = stripes * w + (stripes - 1) * g
    parts = [head]
    if solid:
        parts.append(rect2(min(x_tail, xb + sgn), y - span / 2, max(x_tail, xb + sgn), y + span / 2))
    else:
        for i in range(stripes):
            y0 = y - span / 2 + i * (w + g)
            parts.append(rect2(min(x_tail, xb + sgn), y0, max(x_tail, xb + sgn), y0 + w))
    return union(*parts)

def logistics(variant="stripes"):
    w, g = 3.0, 1.6
    span = 3 * w + 2 * g; H = span / 2 + 2.0; L = 11.0
    if variant in ("stripes", "solid"):          # две полные стрелки одна над другой
        ya, yb = TOP + H, BASE - H
        solid = variant == "solid"
        return union(straight_arrow(LEFT, RIGHT, ya, w=w, g=g, L=L, H=H, solid=solid),
                     straight_arrow(RIGHT, LEFT, yb, w=w, g=g, L=L, H=H, solid=solid))
    # «встречные»: стрелки сдвинуты по горизонтали и сведены ближе, наконечник
    # одной стоит над хвостом другой через стандартный зазор 1.6
    gap = 1.6
    total = 2 * span + (H - span / 2) + gap + 2 * (H - span / 2)
    y0 = (TOP + BASE) / 2 - total / 2 + (H - span / 2)
    ya = y0 + span / 2; yb = ya + span / 2 + (H - span / 2) + gap + span / 2
    return union(straight_arrow(LEFT + 8.0, RIGHT, ya, w=w, g=g, L=L, H=H),
                 straight_arrow(RIGHT - 8.0, LEFT, yb, w=w, g=g, L=L, H=H))

def flow_arrow(start, d0, tip, angle, L=9.6, H=5.5, w0=3.2, w1=2.1, pitch0=6.0, pitch1=3.2,
               k0=0.42, k3=0.36, ease=lambda t: t):
    """Стрелка-поток как в «Инвестициях»: три сходящиеся полосы + наконечник.
    start — точка начала средней полосы (за краем, обрезается сеткой), d0 — её направление."""
    head, B, a, n = arrowhead(tip, angle, L, H)
    end = add(B, mul(a, 1.2))
    dist = math.hypot(*sub(end, start))
    spine = bez(start, d0, dist * k0, end, a, dist * k3)
    bands = [P(band(c, w0, w1, parts=6)) for c in flow_family(spine, pitch0, pitch1, (-1, 0, 1), ease)]
    return union(head, *bands)

def rot180(p, c=(25.0, (TOP + BASE) / 2)):
    return tf(p, (-1, 0, 0, -1, 2 * c[0], 2 * c[1]))

def logistics_flow(variant="wave", y_in=22.5, slope=0.45, k=0.5, gap_check=False):
    cy = (TOP + BASE) / 2
    kw = dict(L=10.0, H=6.4, w0=3.0, w1=2.3, pitch0=5.0 if variant != "fan" else 4.4, pitch1=3.6)
    if variant == "fan":        # прямые сходящиеся потоки
        top = flow_arrow((0, TOP + 6.4), (1, 0), (RIGHT, TOP + 6.4), 0, k0=.3, k3=.3, **kw)
    else:   # «волна»: поток входит слева снизу и выравнивается в стрелку вправо; вторая — поворот на 180°
        top = flow_arrow((-2, y_in if y_in is not None else cy - 1.5), (1, -slope), (RIGHT, TOP + 6.4), 0, k0=k, k3=k, **kw)
    top = canvas_clip(top, x1=RIGHT, y0=TOP, y1=BASE)
    bot = rot180(top)
    if gap_check: print("зазор между стрелками", round(min_gap(top, bot), 2))
    return union(top, bot)

# ── Центральный парк ──────────────────────────────────────────────────────────

def rotunda(x0=6.0, x1=44.0, top_end=28.3, top_mid=26.0, th=3.0, plinth=1.4,
            cols=(2.6, 1.8, 3.0, 1.8, 2.6), col_x0=10.3, col_x1=39.7):
    """Ротонда входа: дуга кровли с загнутыми концами, колонны с равным шагом, цоколь.
    Всё симметрично относительно x=25."""
    cx = (x0 + x1) / 2
    ctrl_top = 2 * top_mid - top_end                      # квадратичная дуга через вершину top_mid
    bot_mid = top_mid + th; bot_end = top_end + 1.6
    ix0, ix1 = x0 + 3.6, x1 - 3.6                         # где начинается загиб
    ctrl_bot = 2 * bot_mid - bot_end
    tip_y = top_end + 3.2
    roof = Path()
    roof.moveTo(x0, top_end)
    roof.quadTo(cx, ctrl_top, x1, top_end)
    roof.cubicTo(x1, top_end + 1.4, x1 - 0.1, tip_y - 0.6, x1 - 0.9, tip_y)          # правый загиб
    roof.cubicTo(x1 - 1.6, tip_y - 0.9, x1 - 2.4, bot_end - 0.05, ix1, bot_end)
    roof.quadTo(cx, ctrl_bot, ix0, bot_end)
    roof.cubicTo(x0 + 2.4, bot_end - 0.05, x0 + 1.6, tip_y - 0.9, x0 + 0.9, tip_y)   # левый загиб
    roof.cubicTo(x0 + 0.1, tip_y - 0.6, x0, top_end + 1.4, x0, top_end)
    roof.close()
    g = ((col_x1 - col_x0) - sum(cols)) / (len(cols) - 1)  # равные просветы между колоннами
    parts = [roof, rect2(7.4, BASE - plinth, 42.6, BASE)]
    def bot_y(x):    # нижняя дуга кровли (квадратичная, ix0 → ix1)
        t = (x - ix0) / (ix1 - ix0); u = 1 - t
        return u * u * bot_end + 2 * u * t * ctrl_bot + t * t * bot_end
    x = col_x0
    for w in cols:   # колонна заходит в кровлю на 0.8 — без «ступенек» над кровлей
        top = max(bot_y(x), bot_y(x + w)) - 0.8
        parts.append(rect2(x, top, x + w, BASE - plinth + 0.01)); x += w + g
    return union(*parts)

def central_park(dy2=-1.0):
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2892:607"]["svg"])
    t1, t2 = P(ds[1]), move(P(ds[2]), 0, dy2)
    # стволы продлеваем вниз за кровлю — их срежет просвет, а не «упрёт» в кровлю
    t1 = union(t1, rect2(16.408, 25.5, 18.142, 28.0))
    t2 = union(t2, rect2(33.105, 25.5 + dy2, 34.749, 28.0))
    pav = rotunda()
    t1 = diff(t1, dilate(t2, GAP))          # правое дерево ниже — оно впереди
    trees = diff(union(t1, t2), dilate(pav, GAP))
    return union(trees, pav)

# ── Комфортный и гостеприимный город ──────────────────────────────────────────

HALO = 0.7    # обводка-просвет у «домовых» иконок пака (замер по исходнику)

def quad(a, b, c, d): return poly(a, b, c, d)

def city(top_a=15.5, apex=11.5, vp_y=27.8, center_top=19.0, wall_drop=3.0):
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2892:571"]["svg"])
    src = [P(d) for d in ds]
    ground_trees = union(*src[0:6])                    # тротуары с деревьями — как были
    trees = union(*src[2:6])
    # ── левый дом: торец (в профиль к нам) + уходящая к перспективе стена
    xa, xb = 3.84, 10.16
    fb_a, fb_b = 36.18, 33.52                          # низ торца — как был
    ft_a, ft_b = top_a, top_a - 0.72                   # верх торца — тот же наклон, выше
    face = quad((xa, ft_a), (xb, ft_b), (xb, fb_b), (xa, fb_a))
    # окна торца: 2 этажа × 2 окна, по линиям наклона верха и низа
    def on_face(x, v):
        t = (x - xa) / (xb - xa)
        top, bot = ft_a + (ft_b - ft_a) * t, fb_a + (fb_b - fb_a) * t
        return (x, top + (bot - top) * v)
    wins = []
    for v0, v1 in ((0.13, 0.36), (0.50, 0.73)):
        for x0, x1 in ((5.0, 6.55), (7.45, 9.0)):
            wins.append(quad(on_face(x0, v0), on_face(x1, v0), on_face(x1, v1), on_face(x0, v1)))
    face = diff(face, *wins)
    # стена вдоль улицы: верх и низ сходятся в точку схода (25; vp_y)
    xn, xf = xb + HALO, 17.73
    nt, nb = ft_b + 0.18, 33.07
    k = (xf - xn) / (25 - xn)
    ftop, fbot = nt + (vp_y - nt) * k, nb + (vp_y - nb) * k
    if wall_drop is not None: ftop = nt + wall_drop     # смягчённая перспектива верхней кромки
    def on_wall(x, v):
        t = (x - xn) / (xf - xn)
        top, bot = nt + (ftop - nt) * t, nb + (fbot - nb) * t
        return (x, top + (bot - top) * v)
    wall = quad((xn, nt), (xf, ftop), (xf, fbot), (xn, nb))
    wwins = []
    for v0, v1 in ((0.12, 0.36), (0.50, 0.74)):
        for x0, x1 in ((12.0, 13.56), (14.35, 15.61), (16.23, 17.2)):
            wwins.append(quad(on_wall(x0, v0), on_wall(x1, v0), on_wall(x1, v1), on_wall(x0, v1)))
    wall = diff(wall, *wwins)
    # кровля: скат над торцом до конька над углом + узкий скат вдоль стены
    e = HALO
    roof = poly((3.5, ft_a - e - 0.15), (10.05, apex), (xf - 0.8, ftop - e - 0.05), (xf + 0.09, ftop - e + 0.95),
                (13.38, nt - e + (ftop - nt) * (13.38 - xn) / (xf - xn) - 0.27), (10.67, ft_b - e - 0.05), (3.5, ft_a - e + 0.03))
    left = union(face, wall, roof)
    # ── центральный дом в конце улицы: два этажа
    cb = 31.81; ct = center_top
    cbody = rect2(18.23, ct, 31.67, cb)
    cw = []
    fh = (cb - ct)
    for v0, v1 in ((0.12, 0.40), (0.55, 0.83)):
        y0, y1 = ct + fh * v0, ct + fh * v1
        for x0, x1 in ((19.99, 21.94), (27.98, 29.93)):
            cw.append(rect2(x0, y0, x1, y1))
        if v0 < 0.5: cw.append(rect2(24.02, y0, 25.93, y1))
    cw.append(rect2(24.03, ct + fh * 0.55, 25.93, cb + 1))         # дверь до низа
    cbody = diff(cbody, *cw)
    slab = rect2(17.59, ct - e - 1.07, 32.32, ct - e)
    center = union(cbody, slab)
    sides = diff(union(left, flip_x(left)), dilate(center, HALO))   # центральный дом отделён тем же просветом
    houses = diff(union(sides, center), dilate(trees, HALO))
    return union(houses, ground_trees)

# ── Жилищное строительство ────────────────────────────────────────────────────

def seg_band(a, b, w):
    """Прямая полоса толщиной w от точки a до точки b (торцы перпендикулярны)."""
    d = norm(sub(b, a)); n = mul(perp(d), w / 2)
    return poly(add(a, n), add(b, n), sub(b, n), sub(a, n))

def construction(right=42.0, gap=1.6, halo=1.2, windows=True):
    # ── кран
    mx0, mx1, rail = 14.14, 20.95, 1.85          # мачта: две стойки и решётка
    jib_t, jib_b = 12.8, 14.8                    # стрела
    mast_bot = 43.1
    rails = union(rect2(mx0, jib_b - 0.01, mx0 + rail, mast_bot), rect2(mx1 - rail, jib_b - 0.01, mx1, mast_bot))
    zig, y, step, k = [], jib_b, 4.6, 0
    while y < mast_bot:                          # раскосы под 45°-ish, ровным шагом
        x_from, x_to = (mx0 + rail / 2, mx1 - rail / 2) if k % 2 == 0 else (mx1 - rail / 2, mx0 + rail / 2)
        zig.append(seg_band((x_from, y), (x_to, y + step), 1.3)); y += step; k += 1
    lattice = inter(union(*zig), rect2(mx0, jib_b, mx1, mast_bot))
    mast = union(rails, lattice)
    # оголовок: треугольная рама — внешний треугольник минус два внутренних,
    # толщина тяг и стойки постоянная, конёк острый
    A = (18.83, 6.6); L = (9.2, jib_t); R = (right, jib_t)
    pl, pr, tl, tr = A[0] - 0.83, A[0] + 0.83, 1.7, 1.6
    def inner(Pa, Pb, t, x_post):
        """Внутренний треугольник между тягой Pa→Pb (толщина t), стойкой x_post и стрелой."""
        d = norm(sub(Pb, Pa)); n = perp(d)
        if n[1] < 0: n = mul(n, -1)                 # внутрь рамы — вниз
        q = add(Pa, mul(n, t))
        p1 = add(q, mul(d, (x_post - q[0]) / d[0]))
        p2 = add(q, mul(d, (jib_t - q[1]) / d[1]))
        return poly(p1, p2, (x_post, jib_t))
    top = diff(poly(A, R, L), inner(A, L, tl, pl), inner(A, R, tr, pr))
    jib = rect2(10.0, jib_t, right, jib_b)
    weight = rect2(7.98, 12.34, 11.72, 16.59)
    trolley = rect2(right - 2.9, jib_b - 0.01, right, jib_b + 1.7)
    roof_y = 20.2                                   # верх дома: крюк не доходит до крыши на gap
    hook = rect2(right - 2.3, jib_b + 1.6, right - 0.6, roof_y - gap)
    crane = union(mast, jib, weight, top, trolley, hook)
    # ── дом: левая грань — через стандартный просвет от мачты, правая — по концу стрелы
    bx0, bx1 = mx1 + gap, right                    # карниз: от просвета у мачты до конца стрелы
    ov = 0.7                                         # одинаковый вынос карниза с обеих сторон
    slab = rect2(bx0, roof_y, bx1, roof_y + 2.0)
    bx0, bx1 = bx0 + ov, bx1 - ov
    body = rect2(bx0, roof_y + 1.99, bx1, BASE)
    ww, wh = 3.6, 3.4
    m = (bx1 - bx0 - 2 * ww) / 3                     # поля = промежутку
    y0 = roof_y + 2.0; gy = (BASE - y0 - 3 * wh) / 4
    wins = [rect2(bx0 + m + c * (ww + m), y0 + gy + r * (wh + gy), bx0 + m + c * (ww + m) + ww, y0 + gy + r * (wh + gy) + wh)
            for c in range(2) for r in range(3)]
    house_big = union(slab, diff(body, *wins) if windows else body)
    # ── домик: строго симметричный, скаты одного уклона, «галочка» кровли той же толщины
    hx0, hx1, eave, hap = 12.4, 23.6, 37.6, 34.0
    hc = (hx0 + hx1) / 2
    small = poly((hx0, BASE), (hx0, eave), (hc, hap), (hx1, eave), (hx1, BASE))
    sl = norm((hc - hx0, hap - eave))               # направление ската вверх
    nrm = (sl[1], -sl[0])                            # нормаль наружу (вверх-влево для левого ската)
    t, over = 1.8, 1.6
    # «галочка» кровли: разность двух вложенных треугольников, отнесённых от скатов
    # на halo и halo+t; концы срезаны перпендикулярно скату на выносе over
    def roof_tri(o):
        h = o / math.cos(math.atan2(eave - hap, hc - hx0))   # вертикальный сдвиг линии ската
        k = (eave - hap) / (hc - hx0)
        return poly((hc - 40, hap - h + 40 * k), (hc, hap - h), (hc + 40, hap - h + 40 * k))
    band_ = diff(roof_tri(halo + t), roof_tri(halo))
    sl = norm((hc - hx0, hap - eave)); nv = (-sl[1], sl[0])
    endL = sub((hx0, eave), mul(sl, over))
    cutL = poly(add(endL, mul(nv, 20)), add(endL, mul(nv, -20)), add(add(endL, mul(nv, -20)), mul(sl, 60)), add(add(endL, mul(nv, 20)), mul(sl, 60)))
    chev = inter(band_, inter(cutL, flip_x(cutL, hc)))
    front = union(small, chev)
    back = union(crane, house_big)
    back = diff(back, dilate(front, halo, join="miter"))
    return union(back, front)

# ── Активный спортивный город: бегун с «тупыми» окончаниями ───────────────────

def section(shape, T, d, s, L=12.0):
    """Сечение фигуры прямой, перпендикулярной оси d, на расстоянии s от кончика T.
    Возвращает две крайние точки (по нормали) или None."""
    c = add(T, mul(d, s)); n = perp(d)
    strip = poly(add(add(c, mul(n, -L)), mul(d, -0.01)), add(add(c, mul(n, L)), mul(d, -0.01)),
                 add(add(c, mul(n, L)), mul(d, 0.01)), add(add(c, mul(n, -L)), mul(d, 0.01)))
    cut = inter(shape, strip)
    best = None
    for cnt in cut.contours:                       # кусок сечения, ближайший к оси
        q = Path(); q.addPath(cnt) if hasattr(q, "addPath") else None
        pts = contour_points(cnt, 0.02)
        if not pts: continue
        proj = [((p[0]-c[0])*n[0] + (p[1]-c[1])*n[1]) for p in pts]
        lo, hi = min(proj), max(proj)
        dist = 0 if lo <= 0 <= hi else min(abs(lo), abs(hi))
        if best is None or dist < best[0]: best = (dist, lo, hi)
    if best is None or best[0] > 1.5: return None
    return add(c, mul(n, best[1])), add(c, mul(n, best[2]))

def blunt_tip(shape, T, d_in, w_end, extra=0.6, shorten=0.45, y_floor=None, toe=0.0, floor_cut=False):
    """Срезает острый кончик конечности и заменяет его плавно сужающимся торцом
    ширины w_end с прямым срезом. d_in — направление от кончика внутрь конечности."""
    d = norm(d_in)
    s_cut = None
    for k in range(1, 800):                       # где ширина = w_end + extra
        s = k * 0.02; sec = section(shape, T, d, s)
        if sec and math.dist(*sec) >= w_end + extra: s_cut = s; A, B = sec; break
    if s_cut is None: raise ValueError(f'не нашли сечение у кончика {T}')
    m_cut = mul(add(A, B), 0.5)
    A2, B2 = section(shape, T, d, s_cut + 1.5)
    m2 = mul(add(A2, B2), 0.5)
    out = norm(sub(m_cut, m2))                      # ось конечности у кончика, наружу
    # отрезаем кончик: только тот кусок фигуры за линией сечения, на котором лежит T
    n = perp(d); c = add(T, mul(d, s_cut))
    hp = poly(add(c, mul(n, -60)), add(c, mul(n, 60)), add(add(c, mul(n, 60)), mul(d, -60)), add(add(c, mul(n, -60)), mul(d, -60)))
    beyond = inter(shape, hp)
    best = None
    for cnt in beyond.contours:
        pts = contour_points(cnt, 0.1)
        dist = min(math.dist(T, q) for q in pts) if pts else 1e9
        if best is None or dist < best[0]: best = (dist, cnt)
    tipc = Path(); best[1].draw(tipc.getPen())
    shape = diff(shape, tipc)
    ne = perp(out)
    L = s_cut * (1 - shorten)                     # острый кончик визуально короче своей длины
    if y_floor is not None and not floor_cut:     # нижний угол торца — ровно на базовой линии
        L = (y_floor - m_cut[1] - abs(ne[1]) * w_end / 2) / out[1]
    if floor_cut:                                 # продлеваем за базу и режем по ней горизонтально
        L = (y_floor - m_cut[1]) / out[1] + 2.0
    ce = add(m_cut, mul(out, L))
    E1, E2 = add(ce, mul(ne, w_end / 2)), sub(ce, mul(ne, w_end / 2))
    # следим, чтобы торец смотрел на A/B без перекрута
    if math.dist(E1, A) > math.dist(E2, A): E1, E2 = E2, E1
    if toe:                                       # «стамеска»: нижний угол вытянут, срез косой
        if E1[1] > E2[1]: E1, E2 = add(E1, mul(out, toe)), sub(E2, mul(out, toe * 0.3))
        else: E2, E1 = add(E2, mul(out, toe)), sub(E1, mul(out, toe * 0.3))
    cap = poly(A, E1, E2, B)
    blunt_tip.log.append((T, round(s_cut, 2), round(math.dist(A, B), 2)))
    shape = union(shape, cap)
    return shape

def tip_cap(shape, T, d_in, s_cut, L, toe=0.0, floor=None):
    """Заменяет острый кончик конечности. Сечение на расстоянии s_cut от кончика T
    по направлению d_in (внутрь конечности); кусок фигуры за сечением с кончиком
    убирается; на его место — торец той же ширины длиной L вдоль оси конечности.
    toe — «стамеска»: нижний угол торца выдвигается на toe, верхний отступает.
    floor — торец продлевается за базовую линию и срезается по ней горизонтально."""
    d = norm(d_in)
    A, B = section(shape, T, d, s_cut)
    A2, B2 = section(shape, T, d, s_cut + 2.0)
    out = norm(sub(mul(add(A, B), .5), mul(add(A2, B2), .5)))    # ось у кончика, наружу
    n = perp(d); c = add(T, mul(d, s_cut))
    hp = poly(add(c, mul(n, -60)), add(c, mul(n, 60)), add(add(c, mul(n, 60)), mul(d, -60)), add(add(c, mul(n, -60)), mul(d, -60)))
    beyond = inter(shape, hp)
    best = None
    for cnt in beyond.contours:
        pts = contour_points(cnt, 0.1)
        dist = min(math.dist(T, q) for q in pts) if pts else 1e9
        if best is None or dist < best[0]: best = (dist, cnt)
    tipc = Path(); best[1].draw(tipc.getPen())
    shape = diff(shape, tipc)
    if floor is not None: L = max(L, (floor - min(A[1], B[1])) / max(out[1], 1e-3) + 2.0)
    EA, EB = add(A, mul(out, L)), add(B, mul(out, L))
    if toe:
        if EA[1] > EB[1]: EA, EB = add(EA, mul(out, toe)), sub(EB, mul(out, toe * 0.3))
        else: EB, EA = add(EB, mul(out, toe)), sub(EA, mul(out, toe * 0.3))
    shape = union(shape, poly(A, EA, EB, B))
    if floor is not None: shape = inter(shape, rect2(-10, -10, 60, floor))
    return shape

def oblique_cut(shape, T, d_in, s, angle):
    """Срезает кончик конечности прямой под углом angle (в градусах экрана),
    проходящей через середину сечения на расстоянии s от кончика T.
    Родное сужение конечности сохраняется — меняется только сам кончик."""
    d = norm(d_in)
    A, B = section(shape, T, d, s)
    m = mul(add(A, B), .5)
    u = (math.cos(math.radians(angle)), math.sin(math.radians(angle)))
    nrm = perp(u)
    if (T[0] - m[0]) * nrm[0] + (T[1] - m[1]) * nrm[1] < 0: nrm = mul(nrm, -1)   # нормаль — к кончику
    hp = poly(add(m, mul(u, -40)), add(m, mul(u, 40)), add(add(m, mul(u, 40)), mul(nrm, 40)), add(add(m, mul(u, -40)), mul(nrm, 40)))
    beyond = inter(shape, hp)
    best = None
    for cnt in beyond.contours:
        pts = contour_points(cnt, 0.1)
        dist = min(math.dist(T, q) for q in pts) if pts else 1e9
        if best is None or dist < best[0]: best = (dist, cnt)
    tipc = Path(); best[1].draw(tipc.getPen())
    return diff(shape, tipc)

def soften(p, r):
    """Скругляет выпуклые углы радиусом r (морфологическое «открытие»)."""
    q = Path(); q.addPath(p); q.stroke(2 * r, LineCap.BUTT_CAP, LineJoin.MITER_JOIN, 4); q.convertConicsToQuads()
    core = diff(p, union(q, Path()))
    return dilate(core, r)

blunt_tip.log = []

def sharp_knee(shape, P1, d1, P2, d2, box):
    """Колено острым углом: продолжаем кромку бедра (P1, d1) и голени (P2, d2)
    до пересечения, внутри box заменяем завиток на чистый угол."""
    from geom import intersect
    K = intersect(P1, d1, P2, d2)
    fill = poly(sub(P1, mul(d1, 3)), P1, K, P2, sub(P2, mul(d2, 3)))
    # внешняя сторона обеих кромок — вне колена
    n1, n2 = perp(d1), perp(d2)
    far = 20
    out1 = poly(sub(P1, mul(d1, far)), add(P1, mul(d1, far)), add(add(P1, mul(d1, far)), mul(n1, -far)), add(sub(P1, mul(d1, far)), mul(n1, -far)))
    out2 = poly(sub(P2, mul(d2, far)), add(P2, mul(d2, far)), add(add(P2, mul(d2, far)), mul(n2, far)), add(sub(P2, mul(d2, far)), mul(n2, far)))
    local = diff(inter(union(shape, fill), box), out1, out2)
    return union(diff(shape, box), local)

def active_city():
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2888:595"]["svg"])
    r, head = P(ds[0]), P(ds[1])                   # голову не трогаем — она круглая
    # колено: кромка бедра приходит в (35.24; 28.94), кромка голени уходит из (34.46; 31.81)
    r = sharp_knee(r, (35.2395, 28.9352), norm((35.2395 - 33.5, 28.9352 - 27.74)),
                   (34.4641, 31.8112), norm((36.3313 - 34.4641, 30.0924 - 31.8112)),
                   rect2(34.3, 28.3, 37.6, 31.75))
    # рука вперёд — как у «Молодёжи»: конец скруглён полукругом по ширине руки
    d_h = norm((-0.74, 0.67)); A, B = section(r, (45.45, 12.3), d_h, 1.9)
    r = oblique_cut(r, (45.45, 12.3), d_h, 1.9, math.degrees(math.atan2(*reversed(perp(d_h)))))
    r = union(r, circle(*mul(add(A, B), .5), math.dist(A, B) / 2))
    r = oblique_cut(r, (12.55, 23.3), (0.73, -0.68), 3.4, 85)    # рука назад
    r = oblique_cut(r, (24.55, 39.2), (0.62, -0.78), 3.2, 80)    # нога вперёд — в носок
    r = oblique_cut(r, (4.55, 43.9), (0.75, -0.66), 4.6, 0)      # толчковая — ровно «по земле»
    return union(soften(r, 0.35), head)

def youth_runner():
    """Ф2 · Молодёжь: те же окончания ног, что у «Активного города»."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["4254:3034"]["svg"])
    body, rest = P(ds[0]), union(*[P(d) for d in ds[1:]])
    body = oblique_cut(body, (23.1, 37.7), (0.8, -0.6), 3.0, 80)
    body = oblique_cut(body, (6.15, 43.9), (0.7, -0.71), 3.6, 0)
    return union(soften(body, 0.35), rest)

# ── Ф1 · Инвестиции v2: перья сходятся в точку, из неё растёт стрелка ─────────

def investments2(angle=50, tip=(45.6, 4.5), L=7.0, H=4.4, Ls=6.5, pj=1.25, ratio=0.72,
                 S=(-1.0, 44.0), d0=18, k0=0.45, k3=0.42, p0=13.0, expo=2.0, w0=4.6, wexpo=0.8):
    """Перья — одно семейство, как крыло «К» в знаке: средняя линия-хребет,
    крайние перья смещены по нормали на шаг p(t). Шаг сходится от p0 у края
    до pj в стыке, ширина пера = ratio·шаг — перья не слипаются до самого стыка.
    Из стыка растёт древко шириной во все три пера и аккуратный наконечник."""
    a = (math.cos(math.radians(angle)), -math.sin(math.radians(angle)))
    n = perp(a)
    B = sub(tip, mul(a, L)); J = sub(B, mul(a, Ls))
    ws = 2 * pj + ratio * pj                       # ширина пучка в стыке = ширина древка
    head = poly(tip, add(B, mul(n, H)), sub(B, mul(n, H)))
    shaft = poly(add(J, mul(n, ws / 2)), add(add(B, mul(a, 0.3)), mul(n, ws / 2)),
                 sub(add(B, mul(a, 0.3)), mul(n, ws / 2)), sub(J, mul(n, ws / 2)))
    dd = (math.cos(math.radians(d0)), -math.sin(math.radians(d0)))
    Je = add(J, mul(a, 0.3))
    dist = math.hypot(*sub(Je, S))
    spine = bez(S, dd, dist * k0, Je, a, dist * k3)
    pitch = lambda t: pj + (p0 - pj) * (1 - t) ** expo
    bands = []
    for s_ in (-1, 0, 1):
        ctr = lambda t, s_=s_: add(point(spine, t), mul(perp(tangent(spine, t)), s_ * pitch(t)))
        if w0 is None: wid = lambda t: ratio * pitch(t)
        else: wid = lambda t: min(ratio * pj + (w0 - ratio * pj) * (1 - t) ** wexpo, pitch(t) - (1 - ratio) * pj)
        bands.append(P(band_fn(ctr, wid, parts=8)))
    investments2.bands = bands
    return canvas_clip(union(head, shaft, *bands))

# ── Ф3 · Туризм v2: крылья «К» сходятся в самолётик ────────────────────────────

def plane_right(nose_x, cy, length):
    """Силуэт планёра из пака (2891:591), развёрнутый носом вправо."""
    g = src_path("2891:591"); x0, y0, x1, y1 = g.bounds
    s = length / (y1 - y0)
    # поворот на 90° по часовой: (x, y) → (−y, x); нос (верх) смотрит вправо
    m = (0, s, -s, 0, nose_x + s * y0, cy - s * (x0 + x1) / 2)
    return tf(g, m)

def airplane(nose_x, cy, Lp=15.0, span=17.0, tspan=6.4, f=1.3):
    """Самолётик сверху, нос вправо: фюзеляж-капсула, стреловидные крылья и стабилизатор."""
    x0 = nose_x - Lp
    X = lambda u: x0 + u * Lp
    body = union(rect2(X(0.03), cy - f, nose_x - f * 1.6, cy + f),
                 poly((nose_x - f * 1.6, cy - f), (nose_x - f * 0.35, cy - f * 0.55), (nose_x, cy),
                      (nose_x - f * 0.35, cy + f * 0.55), (nose_x - f * 1.6, cy + f)))
    parts = [body]
    for sg in (-1, 1):
        parts.append(poly((X(0.66), cy + sg * f * 0.5), (X(0.40), cy + sg * span / 2), (X(0.29), cy + sg * span / 2),
                          (X(0.43), cy + sg * f * 0.5)))
        parts.append(poly((X(0.20), cy + sg * f * 0.5), (X(0.05), cy + sg * tspan / 2), (X(0.0), cy + sg * tspan / 2),
                          (X(0.03), cy + sg * f * 0.5)))
    return union(*parts)

def tourism2(Lp=15.0, span=17.0, gap=0.9, wing_w=32.86, plane_dx=0.0):
    s = wing_w / (75.0 - 21.11)
    h = (60.62419 - 1.42019) * s
    y0 = (TOP + BASE) / 2 - h / 2
    m = (-s, 0, 0, s, LEFT + 75.0 * s, y0 - 1.42019 * s)      # зеркально: стык справа
    wings = tf(logo_wings(), m)
    cy = y0 + ((27.5161 + 33.685) / 2 - 1.42019) * s           # середина стыка
    plane = airplane(RIGHT + plane_dx, cy, Lp, span)
    wings = diff(wings, dilate(plane, gap, join="miter"))       # полосы уходят под самолётик
    return union(wings, plane)

# ── Логистика v2: две обычные стрелки ⇄ ────────────────────────────────────────

def logistics2(t=5.0, hb=14.5, hl=11.0, y1=17.0, y2=33.1):
    def arrow(x_tail, x_tip, y):
        sg = 1 if x_tip > x_tail else -1
        xb = x_tip - sg * hl
        return union(poly((x_tip, y), (xb, y - hb / 2), (xb, y + hb / 2)),
                     rect2(min(x_tail, xb + sg * 0.2), y - t / 2, max(x_tail, xb + sg * 0.2), y + t / 2))
    return union(arrow(LEFT, RIGHT, y1), arrow(RIGHT, LEFT, y2))

# ── Центральный парк v2: исходник, стволы проходят сквозь ротонду до земли ──────

def central_park2(halo=0.7):
    """Исходная иконка. 2-й и 4-й столбы — это стволы: ствол идёт от кроны до земли
    одним элементом, кровля и цоколь отделены от него просветом с обеих сторон."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2892:607"]["svg"])
    pav, t1, t2 = P(ds[0]), P(ds[1]), P(ds[2])
    trunks = [(16.408, 18.142), (33.105, 34.749)]       # ширина стволов у основания кроны
    cols = [(16.2, 18.3), (33.0, 35.0)]                  # 2-й и 4-й столбы ротонды (с запасом)
    for x0, x1 in cols:                                   # столбы убираем — их место займут стволы
        pav = diff(pav, rect2(x0, 28.9, x1, 42.2))
    trees = union(t1, t2, *[rect2(x0, 24.0, x1, BASE) for x0, x1 in trunks])
    pav = diff(pav, dilate(union(*[rect2(x0, 24.0, x1, BASE) for x0, x1 in trunks]), halo, join="miter"))
    return union(pav, trees)

# ── Комфортный город v3: исходник + надстроенный этаж, строгая геометрия ───────

def city2(D=9.0, halo=0.7):
    """Левая половина строится, правая — точное зеркало. Каждый дом получает ещё
    один этаж высотой D: все линии параллельны исходным, окна второго этажа —
    копии окон первого. У центрального дома нет крыши."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2892:571"]["svg"])
    ground, big_tree, small_tree = P(ds[1]), P(ds[2]), P(ds[4])
    trees = union(big_tree, small_tree)
    lin = lambda p0, p1: (lambda x: p0[1] + (p1[1] - p0[1]) * (x - p0[0]) / (p1[0] - p0[0]))
    # торец
    fx0, fx1 = 3.84, 10.16
    f_top = lin((fx0, 25.74), (fx1, 25.02)); f_bot = lin((fx0, 36.18), (fx1, 33.52))
    face = poly((fx0, f_top(fx0) - D), (fx1, f_top(fx1) - D), (fx1, f_bot(fx1)), (fx0, f_bot(fx0)))
    fw = []
    for x0, x1 in ((5.0, 6.6), (7.4, 9.0)):              # по два окна на этаж
        for dy in (0.0, -D):
            fw.append(poly((x0, f_top(x0) + 1.7 + dy), (x1, f_top(x1) + 1.7 + dy),
                           (x1, f_top(x1) + 4.9 + dy), (x0, f_top(x0) + 4.9 + dy)))
    face = diff(face, *fw)
    # стена вдоль улицы
    wx0, wx1 = fx1 + halo, 17.73
    w_top = lin((10.96, 25.2), (17.73, 26.61)); w_bot = lin((10.96, 33.07), (17.73, 30.17))
    wall = poly((wx0, w_top(wx0) - D), (wx1, w_top(wx1) - D), (wx1, w_bot(wx1)), (wx0, w_bot(wx0)))
    ww = []
    for x0, x1 in ((12.0, 13.56), (14.35, 15.61), (16.23, 17.2)):
        for dy in (0.0, -D):                               # окна: верх/низ параллельны кромкам стены
            t0, b0 = w_top(x0) + 1.74 + dy, w_top(x1) + 1.74 + dy
            ww.append(poly((x0, t0), (x1, b0), (x1, b0 + 3.17 - (w_top(x1) - w_top(x0)) * 0.0 - 0.0 + (w_bot(x1) - w_bot(x0)) * 0.0),
                           (x0, t0 + 3.17)))
    wall = diff(wall, *ww)
    # крыша: карнизы параллельны верху торца и стены на расстоянии halo, конёк над углом
    e_front = lambda x: f_top(x) - D - halo
    e_side = lambda x: w_top(x) - D - halo
    # точка, где карнизы встречаются над углом
    cx = (e_side(0) - e_front(0)) / ((e_front(1) - e_front(0)) - (e_side(1) - e_side(0)))
    C = (cx, e_front(cx))
    apex = (10.05, 21.58 - D)
    L = 3.5
    roof = poly((L, e_front(L) - 0.18), apex, (wx1, e_side(wx1) - 1.0), (wx1, e_side(wx1)), C, (L, e_front(L)))
    house = diff(union(face, wall, roof), dilate(trees, halo))
    left = union(house, ground, trees)
    # центральный дом: 2 этажа, без крыши
    cx0, cx1, cb = wx1 + halo, 50 - wx1 - halo, 31.81
    ct = 24.99 - 4.8
    body = rect2(cx0, ct, cx1, cb)
    cw = [rect2(24.03, 29.25, 25.97, cb + 1)]
    for dy in (0.0, -4.8):
        for x0, x1 in ((19.99, 21.94), (28.06, 30.01)):
            cw.append(rect2(x0, 26.2 + dy, x1, 28.35 + dy))
    cw.append(rect2(24.03, 26.2 - 4.8, 25.97, 28.35 - 4.8))
    cw.append(rect2(24.03, 26.2, 25.97, 28.35))
    center = diff(body, *cw)
    center = diff(center, dilate(union(trees, flip_x(trees)), halo))   # деревья впереди дома
    return union(left, flip_x(left), center)

# ── Свято-Георгиевский храм: проще ───────────────────────────────────────────────

def church():
    """Убран козырёк над входом (белая «галочка» над аркой) и ступеньки кровли
    по бокам от центрального свода: карниз идёт ровной линией, свод встаёт прямо на него."""
    import re
    svg0 = SRC["2892:580"]["svg"]
    ds = re.findall(r' d="([^"]+)"', svg0)
    subs = ["M" + x for x in ds[0].split("M") if x.strip()]
    body = [x for x in subs if not x.startswith("M18.7695 34.063")]   # без «галочки»
    main = P("".join(body))
    main.fillType = pathops.FillType.EVEN_ODD
    main = union(main, Path())
    # ступеньки 15.77–18.70 и 31.29–34.19 над карнизом (27.92 → 28.71) убираем
    main = diff(main, rect2(15.6, 27.5, 18.69, 28.70), rect2(31.30, 27.5, 34.4, 28.70))
    main = union(main, rect2(18.69, 27.9, 31.30, 28.75))           # свод опирается на карниз
    rest = [P(d) for d in ds[1:]]
    return union(main, *rest)

# ── круг 3 ───────────────────────────────────────────────────────────────────

def central_park3(halo=0.7, grow=1.15):
    """Исходник. Деревья стоят ЗА входной группой: ротонда целиком залита и ничем
    не разрезана, а стволы (2-й и 4-й столбы) отделены от неё только горизонтальными
    просветами — над кровлей, под кровлей и над цоколем. Правое дерево крупнее."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2892:607"]["svg"])
    pav, t1, t2 = P(ds[0]), P(ds[1]), P(ds[2])
    orig = pav
    for x0, x1, yl, yr in ((16.2, 18.3, 29.25, 29.15), (33.0, 35.0, 29.15, 29.25)):   # 2-й и 4-й столбы — стволы
        pav = diff(pav, rect2(x0, 28.9, x1, 42.2))
        # нижняя кромка кровли над бывшим столбом — по линии соседних пролётов, без ступеньки
        pav = union(pav, inter(orig, poly((x0, 20), (x1, 20), (x1, yr), (x0, yl))))
    bx = (33.105 + 34.749) / 2                              # правое дерево растёт от основания ствола
    t2 = tf(t2, (grow, 0, 0, grow, bx - grow * bx, 26.0 - grow * 26.0))
    w2 = (34.749 - 33.105) * grow / 2
    trunks = union(rect2(16.408, 24.0, 18.142, BASE), rect2(bx - w2, 24.0, bx + w2, BASE))
    t1 = diff(t1, dilate(t2, halo))                         # между кронами тот же просвет
    trees = union(t1, t2, trunks)
    trees = diff(trees, dilate(pav, halo, join="miter"))    # ротонда впереди — режет только по горизонтали
    central_park3.gap = min_gap(diff(P(ds[1]), Path()), t2)
    return union(pav, trees)

def church2():
    """Без просвета между карнизом и стенами; купола слиты с барабанами, барабаны — с кровлей."""
    c = church()
    bridges = [rect2(7.13, 30.1, 42.89, 31.2),                       # карниз и стены — одно целое
               rect2(10.34, 25.4, 14.88, 26.7), rect2(10.34, 28.1, 14.88, 28.9),   # левый купол
               rect2(35.07, 25.4, 39.63, 26.7), rect2(35.07, 28.1, 39.63, 28.9),   # правый купол
               rect2(21.63, 20.9, 28.34, 22.2), rect2(21.63, 24.8, 28.34, 25.8)]   # центральный
    return union(c, *bridges)

def construction_plain():
    """Как утверждено, но у большого дома нет окон — как у маленького."""
    return construction(windows=False)

def hotel():
    """Дверь — один проём шириной с окна, без тонкой перемычки посередине."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2891:614"]["svg"])
    roof, body = P(ds[0]), P(ds[1])
    body = union(body, rect2(20.6, 32.0, 29.4, 41.07))      # заливаем старую двойную дверь
    body = diff(body, rect2(22.23, 32.04, 27.77, 41.2))     # один проём, ширина = окну (5.54)
    return union(roof, body)

def coworking():
    """Монитор на подставке, без отдельной клавиатуры снизу."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2888:632"]["svg"])
    return P(ds[1])

def rocket():
    """Выхлоп обрезан одной вертикалью (потом она встанет на левую направляющую 4)."""
    return inter(src_path("2888:612"), rect2(7.35, 0, 50, 50))

def kite():
    """Оба хвоста змея обрезаны одной вертикалью: верхний продлён по своему ходу."""
    p = src_path("2892:626")
    a, b = (37.3008, 33.4961), (40.042, 36.0508)            # торец верхнего хвоста
    da, db = norm((37.3008 - 29.6828, 33.4961 - 38.838)), norm((40.042 - 31.4391, 36.0508 - 41.1706))
    ext = poly(a, add(a, mul(da, 8)), add(b, mul(db, 8)), b)
    return inter(union(p, ext), rect2(0, 0, 43.2949, 50))

def inset(pts, t):
    """Выпуклый многоугольник, все стороны которого сдвинуты внутрь на t."""
    from geom import intersect
    n = len(pts); cx = sum(p[0] for p in pts) / n; cy = sum(p[1] for p in pts) / n
    lines = []
    for k in range(n):
        a, b = pts[k], pts[(k + 1) % n]; d = norm(sub(b, a)); m = perp(d)
        if (cx - a[0]) * m[0] + (cy - a[1]) * m[1] < 0: m = mul(m, -1)
        lines.append((add(a, mul(m, t)), d))
    return [intersect(*lines[k - 1], *lines[k]) for k in range(n)]

def truck_slanted(k=0.30, gap=1.6, n=3, x0=7.6, x1=29.0):
    """Грузовик в движении: кузов из n наклонных секций с просветом gap,
    задняя стенка кабины наклонена так же; кабина спереди и колёса — исходные."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["4254:3005"]["svg"])
    w1, w2, body = P(ds[0]), P(ds[1]), P(ds[2])
    yt, yb = 15.63, 38.67; ym = (yt + yb) / 2
    xs = lambda xm, y: xm + k * (ym - y)                     # наклонная через точку (xm, ym)
    gx = gap * math.sqrt(1 + k * k)                          # просвет по нормали → по горизонтали
    bw = (x1 - x0 - (n - 1) * gx) / n
    blocks = []
    for j in range(n):
        a = x0 + j * (bw + gx); b = a + bw
        blocks.append(poly((xs(a, yt), yt), (xs(b, yt), yt), (xs(b, yb), yb), (xs(a, yb), yb)))
    cab = inter(body, rect2(31.0, 0, 50, 50))                # исходная кабина справа
    rear = x1 + gx                                           # задняя стенка кабины — параллельно секциям
    cab = union(cab, poly((xs(rear, 19.68), 19.68), (33.0, 19.68), (33.0, yb - 0.04), (xs(rear, yb - 0.04), yb - 0.04)))
    cab = diff(cab, poly((-10, -10), (xs(rear, -10), -10), (xs(rear, 60), 60), (-10, 60)))
    win = poly((xs(rear + 1.45, 22.03), 22.03), (38.4, 22.03), (41.27, 29.14), (xs(rear + 1.45, 29.14), 29.14))
    cab = diff(cab, win)
    wheels = union(w1, w2)
    return union(diff(union(*blocks, cab), dilate(wheels, 0.75)), wheels)

def scales():
    """Весы геометрично: прямая балка без навершия, прямая стойка, основание-полуовал,
    одинаковые чаши на треугольных подвесах; всё симметрично."""
    k = 0.5523
    def half_ellipse(cx, cy, rx, ry):                       # нижняя половина эллипса
        p = Path(); p.moveTo(cx - rx, cy)
        p.cubicTo(cx - rx, cy + k * ry, cx - k * rx, cy + ry, cx, cy + ry)
        p.cubicTo(cx + k * rx, cy + ry, cx + rx, cy + k * ry, cx + rx, cy); p.close(); return p
    def dome(cx, cy, rx, ry):                               # верхняя половина эллипса
        p = Path(); p.moveTo(cx - rx, cy)
        p.cubicTo(cx - rx, cy - k * ry, cx - k * rx, cy - ry, cx, cy - ry)
        p.cubicTo(cx + k * rx, cy - ry, cx + rx, cy - k * ry, cx + rx, cy); p.close(); return p
    beam = rect2(8.6, 13.0, 41.4, 15.6)
    post = rect2(23.7, 15.5, 26.3, 38.0)
    base = dome(25.0, BASE, 9.5, 5.8)
    parts = [beam, post, base]
    for xc in (11.5, 38.5):
        rim, half, t = 30.6, 6.9, 1.7
        tri = [(xc, 15.5), (xc + half, rim), (xc - half, rim)]
        parts += [diff(poly(*tri), poly(*inset(tri, t))), half_ellipse(xc, rim, 7.3, 5.4),
                  rect2(xc - 7.3, rim - 0.01, xc + 7.3, rim + 0.4)]
    return union(*parts)

def glider(span=40.0, angle=45.0, cx=25.0, cy=25.05, ratio=1.55, k=1.3):
    """Десантный планёр А-7 (завод № 499, Заводоуковск, 1941–42) сверху:
    размах к длине ≈ 1.65, высокоплан с длинным узким крылом, гондола с балкой,
    тупой нос с кабиной, стабилизатор. Летит по диагонали в правый верхний угол."""
    L = span / ratio
    # локальные координаты: нос вправо (+x), центр в начале координат
    nose, tail = L * 0.5, -L * 0.5
    xw = nose - L * 0.30                                    # передняя кромка крыла у корня
    c_root, c_tip = span * 0.14 * k, span * 0.085 * k
    pod_w, boom_w = span * 0.11 * k, span * 0.045 * k
    parts = []
    # гондола: от носа до задней кромки крыла, нос скруглён
    pod_end = xw - c_root - L * 0.04
    r = pod_w / 2
    parts.append(rect2(pod_end, -r, nose - r, r))
    parts.append(circle(nose - r, 0, r))
    # балка: сужается к хвосту
    parts.append(poly((pod_end + 0.01, -r), (tail + L * 0.06, -boom_w / 2), (tail + L * 0.06, boom_w / 2), (pod_end + 0.01, r)))
    # крыло: прямая передняя кромка, сужение по задней, скруглённые законцовки
    for sg in (-1, 1):
        y_tip = sg * span / 2
        tip = (xw - (c_root - c_tip) * 0.15, y_tip)
        wing = poly((xw, 0), (xw, y_tip - sg * c_tip / 2), (xw - c_tip, y_tip - sg * c_tip / 2), (xw - c_root, 0))
        parts.append(wing)
        parts.append(circle(xw - c_tip / 2, y_tip - sg * c_tip / 2, c_tip / 2))
    # стабилизатор
    ts, tc = span * 0.34, span * 0.09
    xt = tail + tc
    for sg in (-1, 1):
        parts.append(poly((xt, 0), (xt, sg * (ts / 2 - tc * 0.4)), (tail + tc * 0.15, sg * (ts / 2 - tc * 0.4)), (tail, 0)))
        parts.append(circle(xt - tc * 0.42, sg * (ts / 2 - tc * 0.42), tc * 0.42))
    parts.append(rect2(tail, -boom_w / 2, tail + L * 0.07, boom_w / 2))
    g = union(*parts)
    a = math.radians(-angle)                                # минус — против часовой на экране: нос вверх-вправо
    m = (math.cos(a), math.sin(a), -math.sin(a), math.cos(a), cx, cy)
    return tf(g, m)

# ── Ф1 · Инвестиции v3: одно крыло «К» из знака + стрелка ──────────────────────

def logo_upper_arm():
    """Верхнее крыло «К» (три полосы от стыка вверх) — без нижних полос и букв «З».
    Нижняя кромка внешней полосы от стыка до развилки достроена кубикой."""
    w = logo_wings()
    c = bez((21.0, 33.685), (1, 0), 8.0, (43.2286, 30.7559), norm((47.1504 - 43.2286, 29.602 - 30.7559)), 2.0)
    r = Path(); r.moveTo(-5, 33.685); r.lineTo(*c[0]); r.cubicTo(*c[1], *c[2], *c[3])
    r.cubicTo(44.5505, 30.4009, 45.8725, 30.0458, 47.1504, 29.602)
    r.cubicTo(61.3837, 24.8533, 74.5153, 14.6457, 74.9559, 1.42019)
    r.lineTo(80, 1.42019); r.lineTo(80, -5); r.lineTo(-5, -5); r.close()
    return inter(w, r)

def investments3(theta=38.0, s=0.82, L=7.2, H=4.3, tip=(45.6, 4.6), clip=True):
    """Крыло, развёрнутое так, что полосы выходят из левого нижнего угла (их концы
    срезает рамка), а стык смотрит вверх-вправо под углом theta. Из стыка — стрелка."""
    J0 = (21.11, (27.5161 + 33.685) / 2)
    a = (math.cos(math.radians(theta)), -math.sin(math.radians(theta)))
    J = sub(tip, mul(a, L))
    # поворот на 180° вокруг стыка, затем на −theta, масштаб s, перенос стыка в J
    ct, st = math.cos(math.radians(-theta)), math.sin(math.radians(-theta))
    # итоговая матрица: p' = J + s·R(−θ)·(−(p − J0))
    m = (-s * ct, -s * st, s * st, -s * ct, 0, 0)
    m = (m[0], m[1], m[2], m[3], J[0] - (m[0] * J0[0] + m[2] * J0[1]), J[1] - (m[1] * J0[0] + m[3] * J0[1]))
    arm = tf(logo_upper_arm(), m)
    n = perp(a)
    base = sub(J, mul(a, 0.05))
    head = poly(tip, add(base, mul(n, H)), sub(base, mul(n, H)))
    p = union(arm, head)
    return canvas_clip(p) if clip else p

# ── Комфортный город v4: аккуратный второй этаж ─────────────────────────────────

def city3(variant="B", halo=0.7):
    """A — второй этаж только у центральной «хрущёвки», боковые дома как в исходнике;
    B — всем домам по невысокому второму этажу (D = 5, а не 9).
    Общие правила: левая половина строится, правая — зеркало; линии исходника
    сохраняются и продолжаются параллельно; у центрального дома нет крыши,
    его верх стоит на одной линии с соседями."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2892:571"]["svg"])
    ground, big_tree, small_tree = P(ds[1]), P(ds[2]), P(ds[4])
    trees = union(big_tree, small_tree)
    D = 5.0 if variant == "B" else 0.0
    lin = lambda p0, p1: (lambda x: p0[1] + (p1[1] - p0[1]) * (x - p0[0]) / (p1[0] - p0[0]))
    fx0, fx1 = 3.84, 10.16
    f_top = lin((fx0, 25.74), (fx1, 25.02)); f_bot = lin((fx0, 36.18), (fx1, 33.52))
    face = poly((fx0, f_top(fx0) - D), (fx1, f_top(fx1) - D), (fx1, f_bot(fx1)), (fx0, f_bot(fx0)))
    wx0, wx1 = fx1 + halo, 17.73
    w_top = lin((10.96, 25.2), (17.73, 26.61)); w_bot = lin((10.96, 33.07), (17.73, 30.17))
    wall = poly((wx0, w_top(wx0) - D), (wx1, w_top(wx1) - D), (wx1, w_bot(wx1)), (wx0, w_bot(wx0)))
    ww = []
    rows = (0.0, -D) if D else (0.0,)
    for x0, x1 in ((12.0, 13.56), (14.35, 15.61), (16.23, 17.2)):
        for dy in rows:                                     # окна — копии исходного ряда
            t0, t1 = w_top(x0) + 1.74 + dy, w_top(x1) + 1.74 + dy
            ww.append(poly((x0, t0), (x1, t1), (x1, t1 + 3.17), (x0, t0 + 3.17)))
    wall = diff(wall, *ww)
    e_front = lambda x: f_top(x) - D - halo
    e_side = lambda x: w_top(x) - D - halo
    cx = (e_side(0) - e_front(0)) / ((e_front(1) - e_front(0)) - (e_side(1) - e_side(0)))
    C = (cx, e_front(cx)); apex = (10.05, 21.58 - D); L = 3.5
    roof = poly((L, e_front(L) - 0.18), apex, (wx1, e_side(wx1) - 1.0), (wx1, e_side(wx1)), C, (L, e_front(L)))
    house = diff(union(face, wall, roof), dilate(trees, halo))
    left = union(house, ground, trees)
    # центральная «хрущёвка»: верх — на линии конька соседних крыш (A) или верха их стен (B)
    cx0, cx1, cb = wx1 + halo, 50 - wx1 - halo, 31.81
    ct = apex[1] if variant == "A" else w_top(wx1) - D
    body = rect2(cx0, ct, cx1, cb)
    lo_t, lo_b = 26.2, 28.35                               # нижний ряд — как в исходнике
    up_t = ct + (lo_t - 24.99)                             # верхний ряд: тот же отступ от верха, что был
    up_b = up_t + (lo_b - lo_t)
    cw = [rect2(24.03, 29.25, 25.97, cb + 1)]
    for t, b in ((lo_t, lo_b), (up_t, up_b)):
        for x0, x1 in ((19.99, 21.94), (24.03, 25.97), (28.06, 30.01)):
            cw.append(rect2(x0, t, x1, b))
    center = diff(diff(body, *cw), dilate(union(trees, flip_x(trees)), halo))
    return union(left, flip_x(left), center)

def mentors():
    """Наставники: убран тонкий белый клин внизу корпуса взрослого — силуэт цельный,
    как у бегуна. Головы и рука со скруглённой кистью совпадают с бегуном."""
    return union(src_path("2888:639"), poly((10.55, 43.1), (11.49, 34.6), (12.3, 43.1)))

def logistics3():
    """Временная, аккуратнее прежней: тоньше древко, меньше наконечник. Переделаю по референсам."""
    return logistics2(t=3.0, hb=11.0, hl=8.0, y1=18.0, y2=32.1)

def glider_original_diag():
    """Исходный силуэт планёра из пака, развёрнутый носом в правый верхний угол."""
    g = src_path("2891:591"); x0, y0, x1, y1 = g.bounds
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    a = math.radians(45)                                    # нос смотрел вверх → поворот по часовой на 45°
    c, s_ = math.cos(a), math.sin(a)
    return tf(g, (c, s_, -s_, c, 25 - (c * cx - s_ * cy), 25 - (s_ * cx + c * cy)))

# ── сборка ─────────────────────────────────────────────────────────────────────

ICONS = {
    "investments": lambda: investments3(theta=20, s=0.88, tip=(46, 9.8)),
    "investments-flat": lambda: investments3(theta=0, s=0.649, tip=(46, 23.0), clip=False),
    "tourism": tourism2,
    "logistics": logistics2,
    "park": central_park2,
    "city": lambda: city3("B"),
    "city-a": lambda: city3("A"),
    "construction": construction,
    "active": active_city,
    "youth": youth_runner,
    "church": church,
}

def build(names=None):
    os.makedirs(os.path.join(HERE, "build"), exist_ok=True)
    for name, fn in ICONS.items():
        if names and name not in names: continue
        p = fn()
        open(os.path.join(HERE, f"build/{name}.svg"), "w").write(svg(p))
        open(os.path.join(HERE, f"build/{name}-grad.svg"), "w").write(svg(p, grad="blue"))
        b = p.bounds
        print(f"{name:14s} bounds x {b[0]:.2f}..{b[2]:.2f}  y {b[1]:.2f}..{b[3]:.2f}")

if __name__ == "__main__":
    build(sys.argv[1:] or None)
