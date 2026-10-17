"""Генератор исправленных иконок. Каждая функция возвращает один контур (Path).
Запуск: python3 icons.py [имя ...] — пишет build/<имя>.svg и build/<имя>-grad.svg."""
import json, math, os, sys
from geom import point, tangent, norm, perp, add, sub, mul, band, bez, fit_piece
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

def construction(right=42.0, gap=1.6, halo=1.2):
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
    house_big = union(slab, diff(body, *wins))
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

def blunt_tip(shape, T, d_in, w_end, extra=0.6, shorten=0.45, y_floor=None):
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
    # отрезаем всё дальше сечения
    n = perp(d); c = add(T, mul(d, s_cut)); hw = math.dist(A, B) / 2 + 1.2
    mid_off = ((m_cut[0]-c[0])*n[0] + (m_cut[1]-c[1])*n[1])
    c = add(c, mul(n, mid_off))                     # только окрестность кончика, соседей не трогаем
    far = poly(add(c, mul(n, -hw)), add(c, mul(n, hw)), add(add(c, mul(n, hw)), mul(d, -s_cut - 1)), add(add(c, mul(n, -hw)), mul(d, -s_cut - 1)))
    shape = diff(shape, far)
    # новый торец: на расстоянии (s_cut − keep) от сечения по оси, ширина w_end
    ne = perp(out)
    L = s_cut * (1 - shorten)                     # острый кончик визуально короче своей длины
    if y_floor is not None:                       # нижний угол торца — ровно на базовой линии
        L = (y_floor - m_cut[1] - abs(ne[1]) * w_end / 2) / out[1]
    ce = add(m_cut, mul(out, L))
    E1, E2 = add(ce, mul(ne, w_end / 2)), sub(ce, mul(ne, w_end / 2))
    # следим, чтобы торец смотрел на A/B без перекрута
    if math.dist(E1, A) > math.dist(E2, A): E1, E2 = E2, E1
    cap = poly(A, E1, E2, B)
    blunt_tip.log.append((T, round(s_cut, 2), round(math.dist(A, B), 2)))
    shape = union(shape, cap)
    return shape

def soften(p, r):
    """Скругляет выпуклые углы радиусом r (морфологическое «открытие»)."""
    q = Path(); q.addPath(p); q.stroke(2 * r, LineCap.BUTT_CAP, LineJoin.MITER_JOIN, 4); q.convertConicsToQuads()
    core = diff(p, union(q, Path()))
    return dilate(core, r)

blunt_tip.log = []

def active_city():
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2888:595"]["svg"])
    r, head = P(ds[0]), P(ds[1])                   # голову не трогаем — она круглая
    r = blunt_tip(r, (45.45, 12.3), (-0.74, 0.67), 2.1)      # рука вперёд
    r = blunt_tip(r, (12.55, 23.3), (0.73, -0.68), 1.9)      # рука назад
    r = blunt_tip(r, (24.55, 39.2), (0.62, -0.78), 2.2)      # нога вперёд
    r = blunt_tip(r, (4.55, 43.9), (0.75, -0.66), 2.4, y_floor=BASE + 0.13)   # толчковая нога — на базовой линии
    return union(soften(r, 0.45), head)

# ── сборка ─────────────────────────────────────────────────────────────────────

ICONS = {
    "investments": investments,
    "tourism": tourism,
    "tourism-mirror": lambda: tourism("mirror"),
    "tourism-logo": lambda: tourism("logo"),
    "logistics": logistics_flow,
    "logistics-straight": lambda: logistics_flow("fan"),
    "park": central_park,
    "city": city,
    "construction": construction,
    "active": active_city,
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
