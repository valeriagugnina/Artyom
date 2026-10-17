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

def construction(right=42.0, gap=1.6, halo=1.2, windows=True, small_form=False):
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
    if windows == "top": wins = wins[0::3]                # только верхний ряд: два окна
    if windows == "top2":                                 # два ряда пониже — оба выше крыши маленького дома (≈30.4)
        wh2, r0, gap2 = 2.4, y0 + 1.7, 1.7
        wins = [rect2(bx0 + m + c * (ww + m), r0 + r * (wh2 + gap2), bx0 + m + c * (ww + m) + ww, r0 + r * (wh2 + gap2) + wh2)
                for c in range(2) for r in range(2)]
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
    if small_form:                                  # домик единой формы: кровля слита со стенами
        front = house_form(hc, hx1 - hx0 + 1.6, eave - 2.2)
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

def construction_top():
    """У большого дома вернулись два окна в верхнем ряду."""
    return construction(windows="top")

def construction_top2():
    """У большого дома четыре окна в два ряда, ниже по высоте; все выше крыши маленького дома."""
    return construction(windows="top2")

def construction_form():
    """Как construction_top2, но маленький дом — домик единой формы (кровля слита со стенами)."""
    return construction(windows="top2", small_form=True)

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

def scales(top=13.0, inward=0.0, pan_in=0.0):
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
    beam = rect2(8.6 + inward, top, 41.4 - inward, top + 2.6)
    post = rect2(23.7, top + 2.5, 26.3, 38.0)
    base = dome(25.0, BASE, 9.5, 5.8)
    parts = [beam, post, base]
    for xc in (11.5 + inward, 38.5 - inward):
        rim, half, t = 30.6, 6.9 - pan_in, 1.7
        tri = [(xc, top + 2.5), (xc + half, rim), (xc - half, rim)]
        parts += [diff(poly(*tri), poly(*inset(tri, t))), half_ellipse(xc, rim, 7.3 - pan_in, 5.4),
                  rect2(xc - 7.3 + pan_in, rim - 0.01, xc + 7.3 - pan_in, rim + 0.4)]
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

def city3(variant="B", halo=0.7, side_windows=True, tree_k=1.0):
    """A — второй этаж только у центральной «хрущёвки», боковые дома как в исходнике;
    B — всем домам по невысокому второму этажу (D = 5, а не 9).
    Общие правила: левая половина строится, правая — зеркало; линии исходника
    сохраняются и продолжаются параллельно; у центрального дома нет крыши,
    его верх стоит на одной линии с соседями."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2892:571"]["svg"])
    ground, big_t, small_t = P(ds[1]), P(ds[2]), P(ds[4])
    if tree_k != 1.0:                                       # деревья крупнее — растут от основания ствола
        def grow(t):
            x0, y0, x1, y1 = t.bounds; cx = (x0 + x1) / 2
            return tf(t, (tree_k, 0, 0, tree_k, cx - tree_k * cx, y1 - tree_k * y1))
        big_t, small_t = grow(big_t), grow(small_t)
        ground = diff(ground, dilate(union(big_t, small_t), halo))
    trees = union(big_t, small_t)
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
    if side_windows: wall = diff(wall, *ww)
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

# ── круг 4: адаптация под примеры ─────────────────────────────────────────────

def rline(pts, w):
    """Линия по точкам толщиной w с круглыми концами и стыками (как в примерах)."""
    return stroke(line_path(pts), w, cap="round", join="round")

def arc_pts(c, r, a0, a1, n=24):
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
             c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]

def logistics_route(w=3.6, r_pt=5.4, R=7.5):
    """Маршрут «туда и обратно» (по примеру exchange): две точки и два встречных пути
    со стрелками-уголками. Нижний путь — поворот верхнего на 180°."""
    p0 = (10.5, 37.5)                                       # нижняя левая точка
    x = p0[0]; y_h = 12.5                                   # путь вверх, дуга, вправо
    pts = [(x, p0[1] - r_pt - 1.2), (x, y_h + R)] + arc_pts((x + R, y_h + R), R, 180, 270)[1:] + [(29.5, y_h)]
    path = rline(pts, w)
    tip = (29.5 + w * 0.15, y_h); a = 5.6
    head = rline([(tip[0] - a, tip[1] - a), tip, (tip[0] - a, tip[1] + a)], w)
    half = union(path, head, circle(*p0, r_pt))
    return union(half, rot180(half, (25.0, 25.0)))

def logistics_hub(w=3.4, gap=1.8):
    """Склад и дороги по примеру с фермой: три концентрические дуги слева уходят вниз-вправо,
    две встречные дуги справа упираются в них через просвет; дуги проходят перед складом."""
    left = []
    C = (4.0, 66.0)
    for y0 in (27.0, 32.6, 38.2):
        R = C[1] - y0
        a1 = math.degrees(math.asin((C[1] - BASE - 3) / R))
        left.append(rline(arc_pts(C, R, 270, 360 - a1 + 0.0, 40)[0:1] and
                          [(C[0] + R * math.cos(math.radians(t)), C[1] - R * math.sin(math.radians(t))) for t in
                           [90 - (90 - a1) * k / 40 for k in range(41)]], w))
    left = union(*left)
    right = []
    C2 = (46.0, 70.0)
    for y0 in (32.6, 38.2):
        R = C2[1] - y0
        a1 = math.degrees(math.asin((C2[1] - BASE - 3) / R))
        right.append(rline([(C2[0] - R * math.cos(math.radians(t)), C2[1] - R * math.sin(math.radians(t))) for t in
                            [90 - (90 - a1) * k / 40 for k in range(41)]], w))
    right = diff(union(*right), dilate(left, gap))
    keep = Path()                                           # от правых дуг оставляем куски у правого края
    for cnt in right.contours:
        if cnt.bounds[2] > 44: cnt.draw(keep.getPen())
    house = poly((14.0, 14.5), (25.0, 6.0), (36.0, 14.5), (36.0, 30.0), (14.0, 30.0))
    house = diff(house, rect2(21.5, 19.0, 28.5, 30.1))
    roads = canvas_clip(union(left, union(keep, Path())), x0=0, x1=50)
    return union(diff(house, dilate(roads, gap)), roads)

def career():
    """Портфель по примеру: скруглённый корпус, ручка, белая полоса-дуга поперёк, замок-точка."""
    body = rect2(5.5, 15.0, 44.5, 42.0, 5.5)
    handle = diff(rect2(17.5, 7.0, 32.5, 17.0, 4.0), rect2(21.2, 10.6, 28.8, 17.5, 1.2))
    band = Path()                                            # белая дуга: верх и низ — параллельные дуги
    band.moveTo(5.0, 24.0); band.quadTo(25.0, 33.5, 45.0, 24.0); band.lineTo(45.0, 27.6)
    band.quadTo(25.0, 37.1, 5.0, 27.6); band.close()
    dot = circle(25.0, 22.4, 2.0)                            # замок — белая точка над полосой
    return union(diff(body, band, dot), handle)

def bulb_group(cx, cy, k):
    """Лампочка с лучами по примеру bulb: колба-круг со срезом, цоколь, пять лучей-капсул."""
    r = 6.0 * k
    glass = inter(circle(cx, cy, r), rect2(cx - 20, cy - 20, cx + 20, cy + 4.9 * k))
    neck = poly((cx - 3.6 * k, cy + 3.5 * k), (cx + 3.6 * k, cy + 3.5 * k), (cx + 3.0 * k, cy + 4.9 * k), (cx - 3.0 * k, cy + 4.9 * k))
    cap = inter(circle(cx, cy + 7.1 * k, 3.0 * k), rect2(cx - 5 * k, cy + 6.1 * k, cx + 5 * k, cy + 12 * k))
    rays = [rline([(cx, cy - 10 * k), (cx, cy - 9 * k)], 2 * k),
            rline([(cx - 9 * k, cy), (cx - 8 * k, cy)], 2 * k), rline([(cx + 8 * k, cy), (cx + 9 * k, cy)], 2 * k),
            rline([(cx - 7.1 * k, cy - 7.1 * k), (cx - 6.4 * k, cy - 6.4 * k)], 2 * k),
            rline([(cx + 6.4 * k, cy - 6.4 * k), (cx + 7.1 * k, cy - 7.1 * k)], 2 * k)]
    return union(glass, neck, cap, *rays)

def initiatives():
    """Поддержка инициатив: ладонь исходная, лампочка с лучами — по примеру."""
    import re
    hand = P(re.findall(r' d="([^"]+)"', SRC["2888:643"]["svg"])[0])
    return union(hand, bulb_group(27.6, 13.8, 1.12))

def sun():
    """Солнечный город по примеру sun: диск и восемь лучей-капсул с круглыми концами."""
    cx, cy, k = 25.0, 24.35, 2.0
    parts = [circle(cx, cy, 5.0 * k)]
    for j in range(8):
        a = math.radians(j * 45)
        r0, r1 = 7.8 * k, 9.0 * k
        parts.append(rline([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))], 2.0 * k))
    return union(*parts)

def sparkle(cx, cy, R, waist=0.18):
    """Четырёхлучевая искра с вогнутыми сторонами (как в примере sparkles)."""
    p = Path(); p.moveTo(cx, cy - R)
    for (ax, ay), (bx, by) in (((0, -1), (1, 0)), ((1, 0), (0, 1)), ((0, 1), (-1, 0)), ((-1, 0), (0, -1))):
        c = (cx + (ax + bx) * R * waist, cy + (ay + by) * R * waist)
        p.quadTo(*c, cx + bx * R, cy + by * R)
    p.close(); return union(p, Path())

def mentors_sparkle():
    """Наставники с искрами вместо пятиконечной звезды."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2888:639"]["svg"])
    people = union(*[P(d) for d in ds[:4]], poly((10.55, 43.1), (11.49, 34.6), (12.3, 43.1)))
    return union(people, sparkle(36.6, 13.2, 6.6), sparkle(43.0, 6.4, 3.4))

# ── круг 5 ───────────────────────────────────────────────────────────────────

def truck_solid():
    """Грузовик с наклоном, но кузов — один наклонный блок, без полос внутри."""
    return truck_slanted(n=1)

def church3():
    """Как church2 + закрыт просвет-«линза» под центральным барабаном (его низ — дуга)."""
    return union(church2(), rect2(21.63, 24.0, 28.34, 26.4))

def hotel2():
    """Крыша стыкуется со стенами прямым углом: скруглённые концы карниза срезаны по стенам."""
    h = hotel()
    eaves = union(rect2(0, 15.0, 7.976, 21.0), rect2(42.018, 15.0, 50, 21.0))
    return diff(h, eaves)

def initiatives2():
    """Лампочка крупнее (k 1.12 → 1.4), цоколь по-прежнему над ладонью."""
    import re
    hand = P(re.findall(r' d="([^"]+)"', SRC["2888:643"]["svg"])[0])
    k = 1.4
    return union(hand, bulb_group(27.6, 28.6 - 10.1 * k, k))

def mentors_sparkle2():
    """Искры вместо звезды, крупнее."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2888:639"]["svg"])
    people = union(*[P(d) for d in ds[:4]], poly((10.55, 43.1), (11.49, 34.6), (12.3, 43.1)))
    big = sparkle(37.0, 12.4, 8.2)
    return union(diff(people, dilate(big, 1.0)), big, sparkle(45.2, 3.4, 4.2))

def rocket2(ext=4.5):
    """Выхлоп длиннее на ext (полосы продолжены по своему ходу), срез по-прежнему одной
    вертикалью — ракета в кадре сдвигается вправо, а срез остаётся на направляющей 4."""
    p = src_path("2888:612")
    ends = [((5.0039, 45.0591), (-0.999, 0.02), (5.6973, 42.0522), (-0.997, 0.073)),
            ((5.9414, 40.8784), (-0.995, 0.095), (6.5303, 38.1626), (-0.993, 0.116)),
            ((6.7422, 36.9604), (-0.99, 0.145), (7.2959, 34.189), (-0.988, 0.155))]
    for a, da, b, db in ends:
        p = union(p, poly(add(a, mul(da, -0.3)), add(a, mul(da, ext + 3)), add(b, mul(db, ext + 3)), add(b, mul(db, -0.3))))
    return inter(p, rect2(7.35 - ext, 0, 50, 50))

def glider_b():
    return glider_original_diag()

def capsule(cx, cy, w, h):
    return rect2(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, h / 2)

def pine(tiers, trunk):
    """Иконочная сосна: ярусы-капсулы одной высоты, ствол-прямоугольник."""
    return union(*[capsule(*t) for t in tiers], rect2(*trunk))

def central_park4(halo=0.7):
    """Расположение как в круге 3; деревья перерисованы иконочно — три яруса-капсулы;
    загнутые концы кровли без острого крючка: срезаны по нижней кромке и скруглены."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2892:607"]["svg"])
    pav = P(ds[0])
    orig = pav
    for x0, x1, yl, yr in ((16.2, 18.3, 29.25, 29.15), (33.0, 35.0, 29.15, 29.25)):
        pav = diff(pav, rect2(x0, 28.9, x1, 42.2))
        pav = union(pav, inter(orig, poly((x0, 20), (x1, 20), (x1, yr), (x0, yl))))
    # концы кровли: убираем крючок ниже нижней кромки и скругляем внешний нижний угол
    for xa, xb, cx in ((0, 8.3, 7.12), (41.7, 50, 42.88)):
        pav = diff(pav, rect2(xa, 30.35, xb, 32.5))
        sgn = -1 if cx < 25 else 1
        corner = rect2(min(cx, cx + sgn * 1.2), 29.3, max(cx, cx + sgn * 1.2), 30.5)
        pav = diff(pav, diff(corner, circle(cx, 29.35, 1.0)))
    t1 = pine([(18.0, 9.4, 9.0, 4.6), (15.8, 13.2, 15.0, 4.8), (16.6, 17.3, 17.6, 4.6)], (16.408, 17.0, 18.142, BASE))
    t2 = pine([(35.0, 13.1, 9.5, 4.4), (33.3, 16.8, 15.0, 4.6), (34.0, 20.5, 20.5, 4.4)], (32.985, 20.0, 34.875, BASE))
    t1 = diff(t1, dilate(t2, halo))
    trees = diff(union(t1, t2), dilate(pav, halo, join="miter"))
    return union(pav, trees)

def logistics_loop(w=3.6, r_pt=4.6, R=7.0, a=5.2):
    """Маршрут туда и обратно: две точки, соединённые двумя путями в одно кольцо;
    на верхнем пути стрелка вправо, на нижнем — влево."""
    A, B = (10.0, 40.0), (40.0, 10.0)
    top = [A, (A[0], B[1] + R)] + arc_pts((A[0] + R, B[1] + R), R, 180, 270)[1:] + [B]
    bot = [B, (B[0], A[1] - R)] + arc_pts((B[0] - R, A[1] - R), R, 0, 90)[1:] + [A]
    ring = union(rline(top, w), rline(bot, w))
    mx = 26.5
    heads = union(rline([(mx - a * 0.8, B[1] - a), (mx, B[1]), (mx - a * 0.8, B[1] + a)], w),
                  rline([(50 - mx + a * 0.8, A[1] - a), (50 - mx, A[1]), (50 - mx + a * 0.8, A[1] + a)], w))
    return union(ring, heads, circle(*A, r_pt), circle(*B, r_pt))

def logistics_route2(w=3.6, r_pt=4.4, R=7.5, a=5.0):
    """Как пример exchange, но путь выходит прямо из точки (полностью соединены),
    а стрелка заканчивается напротив второй точки."""
    p0 = (10.5, 37.5); y_h = 12.5
    pts = [p0, (p0[0], y_h + R)] + arc_pts((p0[0] + R, y_h + R), R, 180, 270)[1:] + [(31.0, y_h)]
    tip = (31.0, y_h)
    half = union(rline(pts, w), rline([(tip[0] - a, tip[1] - a), tip, (tip[0] - a, tip[1] + a)], w), circle(*p0, r_pt))
    return union(half, rot180(half, (25.0, 25.0)))

def farm():
    """Ферма — новая иконка по примеру: амбар и поля-полосы. В нашем духе: полосы срезаны
    рамкой (без круглых концов), между амбаром и полями — просвет."""
    w, gap = 3.4, 1.6
    C = (4.0, 66.0); bands = []
    for y0 in (27.0, 32.6, 38.2):
        R = C[1] - y0
        bands.append(stroke(line_path([(C[0] + R * math.cos(math.radians(t)), C[1] - R * math.sin(math.radians(t)))
                                       for t in [91 - 41 * k / 40 for k in range(41)]]), w, cap="butt", join="round"))
    left = union(*bands)
    C2 = (46.0, 70.0); right = []
    for y0 in (32.6, 38.2):
        R = C2[1] - y0
        right.append(stroke(line_path([(C2[0] - R * math.cos(math.radians(t)), C2[1] - R * math.sin(math.radians(t)))
                                       for t in [91 - 30 * k / 40 for k in range(41)]]), w, cap="butt", join="round"))
    right = diff(union(*right), dilate(left, gap))
    keep = Path()
    for cnt in right.contours:
        if cnt.bounds[2] > 44: cnt.draw(keep.getPen())
    fields = canvas_clip(union(left, union(keep, Path())), x0=LEFT, x1=RIGHT)
    barn = poly((14.0, 14.5), (25.0, 6.0), (36.0, 14.5), (36.0, 30.0), (14.0, 30.0))
    barn = diff(barn, rect2(21.5, 19.0, 28.5, 30.1))
    return union(diff(barn, dilate(fields, gap)), fields)

def big_tree(cx, base_y, h):
    """Крупное лиственное дерево из исходника города, увеличенное до высоты h."""
    import re
    t = P(re.findall(r' d="([^"]+)"', SRC["2892:571"]["svg"])[2])      # большое дерево
    x0, y0, x1, y1 = t.bounds; k = h / (y1 - y0)
    return tf(t, (k, 0, 0, k, cx - k * (x0 + x1) / 2, base_y - k * y1))

def city4(variant="C1", halo=0.7):
    """C1: только центральная хрущёвка в конце дорожки и крупные деревья по бокам — ростом
    с дом; дорожка шире и выше. C2: вариант B без окон на боковых домах, деревья крупнее."""
    if variant == "C2":
        return city3("B", side_windows=False, tree_k=1.45)
    # дом: два этажа, 3 × 2 окна, дверь
    hx0, hx1, ht, hb = 13.0, 37.0, 12.0, 33.0
    house = rect2(hx0, ht, hx1, hb)
    wins = [rect2(23.2, hb - 7.0, 26.8, hb + 1)]
    for t in (ht + 2.8, ht + 10.2):
        for x0 in (16.4, 23.2, 30.0):
            if not (x0 == 23.2 and t > ht + 5): wins.append(rect2(x0, t, x0 + 3.6, t + 4.6))
    house = diff(house, *wins)
    # земля с дорожкой: тёмная полоса, белая дорожка от двери вниз и вширь
    ground = rect2(LEFT, hb + halo, RIGHT, BASE)
    road = poly((23.2, hb), (26.8, hb), (35.5, BASE + 0.1), (14.5, BASE + 0.1))
    ground = diff(ground, road)
    trees = union(big_tree(12.6, BASE, 21.5), big_tree(37.4, BASE, 21.5))
    back = diff(union(house, ground), dilate(trees, halo))
    return union(back, trees)

# ── Ф1 · Инвестиции v4: три потока из угла сливаются, стрелка отдельно ────────

def investments4(e=17.0, W0=5.4, wm=0.9, um=40.0, gap=2.6, L=10.0, H=6.4, stem=0.0,
                 k0=0.42, k3=0.48, taper=1.0):
    """Симметрично относительно диагонали из левого нижнего угла. Средний поток идёт
    прямо из угла; боковые входят слева (горизонтально) и снизу (вертикально) и
    заворачивают к среднему, как потоки воздуха. В точке M все три сливаются в одно,
    как полосы в стыке знака. Стрелка — отдельный элемент через просвет."""
    C = (LEFT, BASE)
    a = norm((1.0, -1.0)); n = perp(a)
    M = add(C, mul(a, um))
    R = lambda p: (C[0] - (p[1] - C[1]), C[1] - (p[0] - C[0]))        # отражение через диагональ
    W = lambda t: wm + (W0 - wm) * (1 - t) ** taper
    # средний поток — прямой
    mid = (sub(C, mul(a, 4.0)), None)
    mid_c = (sub(C, mul(a, 4.0)), sub(C, mul(a, 4.0 - um / 3)), sub(M, mul(a, um / 3)), M)
    bands = [P(band_fn(lambda t: point(mid_c, t), W, parts=4))]
    # левый поток: входит слева горизонтально и заворачивает к M
    S = (C[0] - 4.0, C[1] - e)
    dist = math.hypot(*sub(M, S))
    side = bez(S, (1, 0), dist * k0, M, a, dist * k3)
    left = P(band_fn(lambda t: point(side, t), W, parts=6))
    bands += [left, tf(left, (0, -1, -1, 0, C[0] + C[1], C[1] + C[0]))]   # нижний = зеркало левого
    flows = union(*bands)
    if stem > 0:
        flows = union(flows, poly(add(M, mul(n, wm * 1.2)), add(add(M, mul(a, stem)), mul(n, wm * 1.2)),
                                  sub(add(M, mul(a, stem)), mul(n, wm * 1.2)), sub(M, mul(n, wm * 1.2))))
    B = add(M, mul(a, stem + gap))
    head = arrow_head(add(B, mul(a, L)), a, L)          # единая стрелка пака (H = 0.65 L)
    return canvas_clip(union(flows, head), x0=LEFT, y0=0, x1=50, y1=BASE)

def investments5(e=20.5, W0=6.3, wj=1.2, gj=0.45, G0=2.4, um=39.5, gap=2.8, L=10.5, H=6.8,
                 stem=2.0, tip=False, wexp=1.3):
    """Как стык в знаке: средний поток — по диагонали из угла, боковые — её зеркальные
    смещения, шаг p(u) плавно сходится к стыку. Боковые входят в кадр слева (горизонтально)
    и снизу (вертикально). Ширина пера не больше шага минус просвет, поэтому просветы
    видны до самого стыка. В стыке три пера сливаются в одно древко; стрелка — отдельно."""
    C = (LEFT, BASE); a = norm((1.0, -1.0)); n = perp(a)            # n — вниз-вправо
    u0 = 0.7071 * e; p0 = 0.7071 * e; pj = wj + gj
    m0 = -(um - u0) / (p0 - pj)
    def f(sv):                                                        # Эрмит: f(0)=1, f(1)=0, f'(1)=0
        return (2 * sv**3 - 3 * sv**2 + 1) + m0 * (sv**3 - 2 * sv**2 + sv)
    def pitch(u):
        if u <= u0: return p0 + (u0 - u)
        return pj + (p0 - pj) * f((u - u0) / (um - u0))
    def width(u):
        sv = min(1.0, max(0.0, (u - u0) / (um - u0))) if u > u0 else 0.0
        g = gj + (G0 - gj) * (1 - sv)
        w = wj + (W0 - wj) * (1 - sv) ** wexp
        lim = pitch(u) - g; kk = 0.35                               # мягкий минимум — без излома кромки
        sm = -kk * math.log(math.exp(-w / kk) + math.exp(-lim / kk))
        return max(wj, sm)
    us = -4.0
    bands = []
    for sg in (-1, 0, 1):
        ustart = us if sg == 0 else u0 - 5.0
        ctr = lambda t, sg=sg, ustart=ustart: add(add(C, mul(a, ustart + (um - ustart) * t)), mul(n, sg * pitch(ustart + (um - ustart) * t)))
        wid = lambda t, ustart=ustart, sg=sg: (W0 if sg == 0 and ustart + (um - ustart) * t < u0 else width(ustart + (um - ustart) * t))
        bands.append(P(band_fn(ctr, wid, parts=10, n=30)))
    flows = union(*bands)
    J = add(C, mul(a, um)); ws = 3 * wj + 2 * gj
    if stem > 0:
        end = add(J, mul(a, stem))
        if tip: flows = union(flows, poly(add(J, mul(n, ws / 2)), add(end, mul(a, ws * 0.6)), sub(J, mul(n, ws / 2))))
        else: flows = union(flows, poly(add(J, mul(n, ws / 2)), add(end, mul(n, ws / 2)), sub(end, mul(n, ws / 2)), sub(J, mul(n, ws / 2))))
    B = add(J, mul(a, stem + (ws * 0.6 if tip else 0) + gap))
    head = arrow_head(add(B, mul(a, L)), a, L)          # единая стрелка пака (H = 0.65 L)
    return canvas_clip(union(flows, head), x0=LEFT, y0=0, x1=50, y1=BASE)

def career2():
    """Портфель: углы строже (как у прежней «Карьеры»), ручка входит в корпус прямо —
    прямые стойки, скруглены только верхние углы; белая дуга и замок как в круге 4."""
    body = rect2(5.5, 15.0, 44.5, 42.0, 2.6)
    outer = Path()                                           # ручка: верхние углы r=2.4, низ прямой и уходит в корпус
    x0, x1, y0, y1, r = 17.5, 32.5, 7.0, 16.0, 2.4; k = 0.5523
    outer.moveTo(x0, y1); outer.lineTo(x0, y0 + r); outer.cubicTo(x0, y0 + r - k * r, x0 + r - k * r, y0, x0 + r, y0)
    outer.lineTo(x1 - r, y0); outer.cubicTo(x1 - r + k * r, y0, x1, y0 + r - k * r, x1, y0 + r); outer.lineTo(x1, y1); outer.close()
    handle = diff(outer, rect2(21.0, 10.5, 29.0, 16.5))
    band = Path()
    band.moveTo(5.0, 24.0); band.quadTo(25.0, 33.5, 45.0, 24.0); band.lineTo(45.0, 27.6)
    band.quadTo(25.0, 37.1, 5.0, 27.6); band.close()
    return union(diff(body, band, circle(25.0, 22.4, 2.0)), handle)

def sun2():
    """Солнце того же размера, лучи — прямоугольники с острыми углами."""
    cx, cy, k = 25.0, 24.35, 2.0
    parts = [circle(cx, cy, 5.0 * k)]
    for j in range(8):
        a = math.radians(j * 45)
        r0, r1 = 7.8 * k - k, 9.0 * k + k                    # та же длина, что у капсул вместе с круглыми концами
        parts.append(stroke(line_path([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)),
                                       (cx + r1 * math.cos(a), cy + r1 * math.sin(a))]), 2.0 * k, cap="butt"))
    return union(*parts)

def logistics_boxes(w=3.6, R=4.5):
    """По примеру replace: два груза-квадрата по диагонали и два встречных Г-образных пути.
    Квадраты со скруглёнными углами, пути с прямыми концами и острым наконечником."""
    box = rect2(LEFT, TOP, LEFT + 14.5, TOP + 14.5, 2.6)
    yc = TOP + 7.25
    # путь: снизу вверх по x=39, поворот налево по дуге R, влево к наконечнику
    x = 39.0
    pts = [(x, 25.2), (x, yc + R)] + arc_pts((x - R, yc + R), R, 0, -90)[1:] + [(27.2, yc)]
    path = stroke(line_path(pts), w, cap="butt", join="round")
    head = poly((21.6, yc), (27.6, yc - 5.0), (27.6, yc + 5.0))
    half = union(box, path, head)
    return union(half, rot180(half, (25.0, (TOP + BASE) / 2)))

# ── круг 6 ───────────────────────────────────────────────────────────────────

ARROW_K = 0.65            # единая стрелка пака: сплошной треугольник, полуширина = 0.65 длины
ARROW_R = 0.075           # углы стрелки чуть скруглены: радиус = 0.075 длины

def round_poly(pts, r):
    """Многоугольник со скруглёнными углами (дуги радиуса r, касательные к сторонам)."""
    n_ = len(pts); p = Path(); first = True
    for i in range(n_):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n_]
        u, v = norm(sub(a, b)), norm(sub(c, b))
        th = math.acos(max(-1.0, min(1.0, u[0] * v[0] + u[1] * v[1])))   # внутренний угол
        t = r / math.tan(th / 2)
        p1, p2 = add(b, mul(u, t)), add(b, mul(v, t))
        h = 4 / 3 * math.tan((math.pi - th) / 4) * r
        if first: p.moveTo(*p1); first = False
        else: p.lineTo(*p1)
        q1, q2 = add(p1, mul(u, -h)), add(p2, mul(v, -h))
        p.cubicTo(*q1, *q2, *p2)
    p.close(); return union(p, Path())

def arrow_head(tip, d, L):
    """Единый наконечник: треугольник длиной L по направлению d, углы чуть скруглены.
    Остриё скругления не укорачивает: треугольник удлинён так, чтобы кончик дуги стоял в tip."""
    d = norm(d); n = perp(d); r = L * ARROW_R
    half = math.atan(ARROW_K)
    ext = r / math.sin(half) - r                        # на столько дуга отступает от вершины
    tip2 = add(tip, mul(d, ext)); L2 = L + ext; b = sub(tip2, mul(d, L2))
    return round_poly([tip2, add(b, mul(n, L2 * ARROW_K)), sub(b, mul(n, L2 * ARROW_K))], r)

def logistics_route3(w=3.6, r_pt=4.4, R=7.5, L=7.6, gap=1.6):
    """Маршрут: точки отделены от путей просветом, пути с прямыми концами и мягким
    поворотом, наконечник — единая стрелка пака."""
    p0 = (10.5, 37.5); y_h = 12.5
    start = (p0[0], p0[1] - r_pt - gap)
    tip = (50 - p0[0] - r_pt - gap - 0.4, y_h)                # остриё не доходит до второй точки на просвет
    base = (tip[0] - L, y_h)
    pts = [start, (p0[0], y_h + R)] + arc_pts((p0[0] + R, y_h + R), R, 180, 270)[1:] + [(base[0] + 0.3, y_h)]
    half = union(stroke(line_path(pts), w, cap="butt", join="round"), arrow_head(tip, (1, 0), L), circle(*p0, r_pt))
    return union(half, rot180(half, (25.0, 25.0)))

def farm2(w=3.4, gap=1.6):
    """Ферма: правые поля заканчиваются прямым срезом поперёк полосы, на ровном
    просвете от левых — а не обрезаны по кривой."""
    C = (4.0, 66.0); bands = []
    for y0 in (27.0, 32.6, 38.2):
        R = C[1] - y0
        bands.append(stroke(line_path([(C[0] + R * math.cos(math.radians(t)), C[1] - R * math.sin(math.radians(t)))
                                       for t in [91 - 41 * k / 40 for k in range(41)]]), w, cap="butt", join="round"))
    left = union(*bands)
    lpts = contour_points(left, 0.2)
    C2 = (46.0, 70.0); right = []
    for y0 in (32.6, 38.2):
        R = C2[1] - y0
        pts = []
        for k in range(200):
            t = 91 - 40 * k / 199
            q = (C2[0] - R * math.cos(math.radians(t)), C2[1] - R * math.sin(math.radians(t)))
            if min(math.dist(q, z) for z in lpts[::3]) < w / 2 + gap + 0.6: break
            pts.append(q)
        if len(pts) > 2: right.append(stroke(line_path(pts), w, cap="butt", join="round"))
    fields = canvas_clip(union(left, *right), x0=LEFT, x1=RIGHT)
    barn = poly((14.0, 14.5), (25.0, 6.0), (36.0, 14.5), (36.0, 30.0), (14.0, 30.0))
    barn = diff(barn, rect2(21.5, 19.0, 28.5, 30.1))
    return union(diff(barn, dilate(fields, gap)), fields)

def church5(side_k=1.15, slit=0.7, base_extra=1.5, no_eaves=True):
    """Прежний облик храма: карниз с выступами, свод, белая «галочка» над входом.
    Каждая маковка слита со своим барабаном и отделена от кровли ровной прорезью slit;
    у центральной прорезь идёт по дуге свода. Боковые маковки крупнее в side_k раз."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2892:580"]["svg"])
    main = P(ds[0]); main.fillType = pathops.FillType.EVEN_ODD; main = union(main, Path())
    main = diff(main, rect2(15.6, 27.5, 18.69, 28.70), rect2(31.30, 27.5, 34.4, 28.70))   # ступеньки кровли
    main = union(main, rect2(18.69, 27.9, 31.30, 28.75), rect2(7.13, 30.1, 42.89, 31.2))  # свод на карнизе, карниз со стенами
    if no_eaves:                                                   # линия кровли — одна прямая без ступенек
        main = union(diff(main, rect2(0, 26.0, 7.13, 32.0), rect2(42.89, 26.0, 50, 32.0)), rect2(7.13, 27.9, 42.89, 30.2))
    domes = []
    for onion, drum, (x0, x1) in ((3, 2, (10.34, 14.88)), (4, 1, (35.07, 39.63))):
        d = union(P(ds[onion]), P(ds[drum]), rect2(x0, 25.4, x1, 26.7))
        cx = (x0 + x1) / 2
        domes.append(tf(d, (side_k, 0, 0, side_k, cx - side_k * cx, 28.31 - side_k * 28.31)))
    domes.append(union(P(ds[6]), P(ds[5]), rect2(21.63, 20.9, 28.34, 26.4)))
    out = union(main, *[diff(d, dilate(main, slit)) for d in domes])
    if no_eaves:                         # без крошечных выступов карниза слева и справа
        out = diff(out, rect2(0, 26.0, 7.13, 32.0), rect2(42.89, 26.0, 50, 32.0))
    if base_extra:                       # выше за счёт стен: окна и дверь вытягиваются, галочка на месте
        y = 39.0
        upper = inter(out, rect2(0, 0, 50, y)); lower = move(inter(out, rect2(0, y, 50, 50)), 0, base_extra)
        band = diff(rect2(7.13, y - 0.1, 42.89, y + base_extra + 0.1),
                    rect2(12.32, y - 1, 14.63, y + base_extra + 1), rect2(35.38, y - 1, 37.69, y + base_extra + 1),
                    rect2(21.5, y - 1, 28.5, y + base_extra + 1))
        out = union(upper, lower, band)
    return out

def mentors4(r=3.4):
    """Как mentors3, но плечо — мягкая дуга радиуса r, как у плеч ребёнка;
    слева прямая линия до основания, без зазубрины в углу."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2888:639"]["svg"])
    adult = union(P(ds[1]), poly((10.55, 43.1), (11.49, 34.6), (12.3, 43.1)))
    A, B = (11.2, 26.0), (8.4, 43.1)
    adult = diff(adult, poly(A, B, (0, 43.1), (0, 20), (11.2, 20)))
    adult = union(adult, inter(poly(A, B, (22, 43.1), (22, 24)), dilate(adult, 0.01)))
    adult = union(adult, poly(A, B, (14.0, 43.1), (14.0, 25.4)))
    corner = inter(rect2(6, 21, 17, 33), diff(adult, opening(adult, r)))   # скругляем только плечо
    adult = diff(adult, corner)
    people = union(adult, P(ds[0]), P(ds[2]), P(ds[3]))
    big = sparkle(37.0, 12.4, 8.2)
    return union(diff(people, dilate(big, 1.0)), big, sparkle(45.2, 3.4, 4.2))

def hand_original():
    import re
    return P(re.findall(r' d="([^"]+)"', SRC["2888:643"]["svg"])[0])

def initiatives4(k=1.12):
    """Исходная ладонь в полный размер кадра; лампочка с лучами вписана над ней в поле."""
    return union(hand_original(), bulb_group(27.6, 28.6 - 10.1 * k, k))

def mutual_help2(hw=17.5):
    """Та же исходная ладонь; сердце соразмерно лампочке с лучами."""
    import re
    heart = P(re.findall(r' d="([^"]+)"', SRC["4254:3105"]["svg"])[1])
    x0, y0, x1, y1 = heart.bounds; k = hw / (x1 - x0)
    heart = tf(heart, (k, 0, 0, k, 27.6 - k * (x0 + x1) / 2, 28.4 - k * y1))
    return union(hand_original(), heart)

CROWNS = {
    # лепестки (x, y, r) в долях полуширины u; середина кроны залита эллипсом (rx, ry)
    "cloud": ([(0, -0.95, 0.52), (-0.50, -0.42, 0.50), (0.50, -0.42, 0.50),
               (-0.50, 0.22, 0.50), (0.50, 0.22, 0.50), (0, 0.42, 0.50)], (0.75, 0.95)),
    "low": ([(0, -0.62, 0.42), (-0.52, -0.27, 0.42), (0.52, -0.27, 0.42),
             (-0.55, 0.30, 0.45), (0.55, 0.30, 0.45)], (0.72, 0.72)),
}

def cloud_crown(cx, cy, u, kind="cloud", sy=1.0):
    """Крона «облаком», как у деревьев в остальном паке: лепестки по контуру,
    середина залита — без глубоких выемок-«треф». u — полуширина кроны;
    sy < 1 — крона приплюснута по вертикали (как у сосен)."""
    lobes, (rx, ry) = CROWNS[kind]
    parts = [ellipse(cx + x * u, cy + y * u * sy, r * u, r * u * sy) for x, y, r in lobes]
    parts.append(ellipse(cx, cy, rx * u, ry * u * sy))
    return union(*parts)

def oval_crown(cx, cy, u):
    """Крона из овалов: высокий центральный овал и два боковых пониже."""
    return union(ellipse(cx, cy - 0.35 * u, 0.62 * u, 0.95 * u),
                 ellipse(cx - 0.45 * u, cy + 0.15 * u, 0.55 * u, 0.7 * u),
                 ellipse(cx + 0.45 * u, cy + 0.15 * u, 0.55 * u, 0.7 * u))

def central_park6(halo=0.7, u=6.95, cy=13.4, tw=1.88, kind="cloud", sy=0.72):
    """Два одинаковых дерева с кроной-облаком, стоят симметрично (2-й и 4-й столбы
    исходника были сдвинуты несимметрично — стволы выровнены по оси ротонды)."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2892:607"]["svg"])
    pav = P(ds[0]); orig = pav
    xs = (17.26, 50 - 17.26)                                   # центры стволов, зеркально относительно 25
    for x0, x1 in ((16.2, 18.3), (32.9, 35.0)):              # убираем 2-й и 4-й столбы исходника
        pav = diff(pav, rect2(x0, 28.9, x1, 42.2))
        yl, yr = (29.25, 29.15) if x0 < 25 else (29.15, 29.25)
        pav = union(pav, inter(orig, poly((x0, 20), (x1, 20), (x1, yr), (x0, yl))))
    for xa, xb, cx in ((0, 8.3, 7.12), (41.7, 50, 42.88)):   # концы кровли — как в круге 5
        pav = diff(pav, rect2(xa, 30.35, xb, 32.5))
        sgn = -1 if cx < 25 else 1
        corner = rect2(min(cx, cx + sgn * 1.2), 29.3, max(cx, cx + sgn * 1.2), 30.5)
        pav = diff(pav, diff(corner, circle(cx, 29.35, 1.0)))
    crown = (lambda x: oval_crown(x, cy, u)) if kind == "oval" else (lambda x: cloud_crown(x, cy, u, kind, sy))
    trees = union(*[union(crown(x), rect2(x - tw / 2, cy, x + tw / 2, BASE)) for x in xs])
    trees = diff(trees, dilate(pav, halo, join="miter"))
    return union(pav, trees)

def drop_small(p, amin=0.6):
    """Убрать мелкие чёрные щепки (контуры-заливки площадью меньше amin)."""
    keep = []; cs = list(p.contours)
    for c in cs:
        q = Path(); c.draw(q.getPen())
        x0, y0, x1, y1 = q.bounds
        if (x1 - x0) * (y1 - y0) >= amin or c.clockwise != cs[0].clockwise: keep.append(q)
    out = Path()
    for q in keep: q.draw(out.getPen())
    out.fillType = pathops.FillType.EVEN_ODD
    return union(out, Path())

def capital_orig(gap=0.9):
    """Капитал — исходник. Передняя стопка без изменений; задняя собрана целиком
    (та же стопка, сдвинутая назад, бок на 0.46 выше — как в исходнике) и отрезана
    от передней тем же просветом 0.9 — без обрезков перегородок у стыка."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["4254:1272"]["svg"])
    front = P(ds[0]); front.fillType = pathops.FillType.EVEN_ODD; front = union(front, Path())
    subs = ["M" + x for x in ds[0].split("M") if x.strip()]
    outer = P(subs[0])
    dx, dyt, dyp = 19.457 - 30.5469, 9.95508 - 24.5205, 22.2852 - 36.3877
    cx, rx, ry = 19.457, 12.0118, 5.082
    body = union(ellipse(cx, 15.0371, rx, ry), rect2(cx - rx, 15.0371, cx + rx, 24.7393), ellipse(cx, 24.7393, rx, ry))
    panels = [move(P(m), dx, dyp) for m in subs[1:]]
    # центральная и правая панели задней стопки почти скрыты передней — сливаем их в одну,
    # чтобы у стыка не торчал обрубок перегородки
    fx, frx, fry = 30.5469, 12.0118, 5.082
    below = lambda c: diff(rect2(fx - frx, c, fx + frx, 60), ellipse(fx, c, frx, fry))
    band = move(diff(below(33.474), below(37.052)), dx, dyp)
    merged = inter(band, rect2(16.7734, 0, 29.2969, 50))
    back = diff(body, *panels, merged)
    back = drop_small(diff(back, dilate(outer, gap)))
    return union(back, front)

def career3(w=2.15, sag=9.5):
    """Портфель круга 6, но белая дуга тоньше и ровной толщины — как линии баскетбольного
    мяча (≈2 в итоговом размере): обводка средней линии, а не разность двух сдвинутых дуг."""
    p = career2()
    body = rect2(5.5, 15.0, 44.5, 42.0, 2.6)
    filled = union(p, inter(body, rect2(5.5, 20.0, 44.5, 40.0)))       # закрыли старую дугу
    filled = diff(filled, circle(25.0, 22.4, 2.0))
    c = Path(); c.moveTo(2.0, 24.4); c.quadTo(25.0, 24.4 + 2 * sag * 0.5, 48.0, 24.4)
    band = stroke(c, w, cap="butt")
    return diff(filled, band, circle(25.0, 22.6, 2.0))

def sanatorium2(bk=1.12, kx=1.0, ky=1.25, halo=0.7, clear=0.15):
    """Санаторий: стены прямые и стоят на базе (в исходнике здание висело на 0.9 выше,
    а у стен были наплывы от старых деревьев). Здание крупнее в bk раз; ели выше (ky)
    и придвинуты к зданию вплотную — стоят перед его углами, просвет 0.7 не задевает окна."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2891:599"]["svg"])
    top = P(ds[3])
    pediment = inter(P(ds[2]), rect2(0, 0, 50, 21.75))
    walls = rect2(12.0, 21.7, 38.05, BASE)
    plinth = rect2(10.87, 41.9, 39.19, BASE)
    holes = [rect2(15.4, 31.98, 20.41, 36.89), rect2(29.67, 31.98, 34.64, 36.89),
             rect2(15.4, 24.04, 20.56, 29.1), rect2(29.52, 24.04, 34.59, 29.1),
             rect2(22.44, 32.63, 27.74, BASE + 1)]
    house = union(top, pediment, diff(union(walls, plinth), *holes))
    house = tf(house, (bk, 0, 0, bk, 25 - bk * 25, BASE - bk * BASE))
    win_l = 25 - (25 - 15.4) * bk                                # левый край левых окон
    trees = []
    for i, sgn in ((0, 1), (1, -1)):
        t = P(ds[i]); x0, _, x1, _ = t.bounds; bx = (x0 + x1) / 2; hw = (x1 - x0) / 2 * kx
        cx = win_l - halo - clear - hw if sgn > 0 else 50 - (win_l - halo - clear - hw)
        trees.append(tf(t, (kx, 0, 0, ky, cx - kx * bx, BASE - ky * BASE)))
    trees = union(*trees)
    return union(diff(house, dilate(trees, halo, join="miter")), trees)

def rest_base2(halo=0.7):
    """База отдыха: дом — ровный пятиугольник без «ступни» слева, окно — четыре ровные
    створки по оси конька (в исходнике створки разного размера и кривой подоконник);
    кровля-галочка и ель — исходные, ель отделена от дома прежним просветом."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2891:608"]["svg"])
    roof, tree = P(ds[2]), P(ds[1])
    ax = 21.2
    body = poly((9.98, BASE), (9.98, 35.66), (ax, 24.6), (32.47, 35.74), (32.47, BASE))
    body = diff(body, inter(rect2(ax - 3, 20, ax + 3, 28), diff(body, opening(body, 1.3))))   # мягкий конёк
    pw, mul_, top_, h_ = 2.6, 1.1, 29.9, 4.5
    xs = (ax - mul_ / 2 - pw, ax + mul_ / 2)
    panes = [rect2(x, y, x + pw, y + h_) for x in xs for y in (top_, top_ + h_ + mul_)]
    body = diff(body, *panes)
    house = union(roof, body)
    tree = diff(tree, dilate(house, halo))
    return union(house, tree)

def convex_hull(p):
    from scipy.spatial import ConvexHull
    pts = contour_points(p, 0.1)
    h = ConvexHull(pts)
    return poly(*[tuple(pts[i]) for i in h.vertices])

def combine2(g=1.34):
    """Комбайн: все вырезы — как у трактора (≈1.3 в итоговом размере; в исходнике 0.75–0.85).
    Порядок слоёв: колёса → жатка → кабина → корпус → бункер; каждый следующий отрезан от
    предыдущих одним и тем же просветом g. Жатка упрощена до цельного блока — тонкий палец
    подающей камеры внутри неё при таком просвете превратился бы в щепку."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["4254:3023"]["svg"])
    wheels = union(P(ds[0]), P(ds[1]))
    header = convex_hull(P(ds[3]))
    cab = P(ds[2]); cab.fillType = pathops.FillType.EVEN_ODD; cab = union(cab, Path())
    cab = diff(cab, poly((36.67, 35.9), (37.49, 36.74), (38.4, 37.9), (44.0, 41.5), (44.0, 30.0), (36.67, 30.0)))   # палец внутри жатки: кромка подающей камеры идёт прямо до просвета
    body, tank = P(ds[4]), P(ds[5])
    front = wheels; out = [wheels]
    for part in (header, cab, body, tank):
        part = diff(part, dilate(front, g))
        out.append(part); front = union(front, part)
    return drop_small(union(*out), 1.0)

def ring_arch(cx, cy, r_in, r_out):
    """Полукольцо-арка над линией cy."""
    return inter(diff(circle(cx, cy, r_out), circle(cx, cy, r_in)), rect2(cx - r_out - 1, cy - r_out - 1, cx + r_out + 1, cy))

def park_gate(g=1.3, pw=11.0, half=13.5, t=3.2, arch="round"):
    """Вход в парк Машиностроителей: ворота — две колонны и арка над проходом.
    Колонна: цоколь, ствол с двумя каннелюрами, цельная капитель без мини-выступов;
    все просветы между частями одинаковые (g). Арка опирается на капители."""
    cxs = (25 - half, 25 + half)
    plinth_h, cap_h = 3.4, 3.4
    R_out = half + t / 2
    if arch == "round": cap_top = TOP - 1.0 + R_out          # полукруглый верх — на 1 выше линии 7
    else: cap_top = 17.0
    cap_bot = cap_top + cap_h
    parts = []
    for cx in cxs:
        plinth = rect2(cx - pw / 2, BASE - plinth_h, cx + pw / 2, BASE)
        shaft_w = pw - 2.4
        s_bot = BASE - plinth_h - g; s_top = cap_bot + g
        shaft = rect2(cx - shaft_w / 2, s_top, cx + shaft_w / 2, s_bot)
        fl = (shaft_w - 2 * g) / 3                                  # три ровные полосы, две каннелюры
        for k in (1, 2):
            x = cx - shaft_w / 2 + k * fl + (k - 1) * g
            shaft = diff(shaft, rect2(x, s_top + 1.5, x + g, s_bot - 1.5))
        cap = rect2(cx - pw / 2, cap_top, cx + pw / 2, cap_bot)
        parts += [plinth, shaft, cap]
    if arch == "round":
        a = ring_arch(25.0, cap_top + 0.01, R_out - t, R_out)
    else:                                                         # пологая арка-сегмент
        sag = cap_top - TOP; rc = (half ** 2 + sag ** 2) / (2 * sag)
        cy = TOP + rc
        a = inter(diff(circle(25, cy, rc + t / 2), circle(25, cy, rc - t / 2)), rect2(0, 0, 50, cap_top + 0.01))
    return union(*parts, a)

def heart_shape(cx, cy, w):
    """Сердце пака (из «Взаимопомощи»), шириной w, центр рамки в (cx, cy)."""
    import re
    h = P(re.findall(r' d="([^"]+)"', SRC["4254:3105"]["svg"])[1])
    x0, y0, x1, y1 = h.bounds; k = w / (x1 - x0)
    return tf(h, (k, 0, 0, k, cx - k * (x0 + x1) / 2, cy - k * (y0 + y1) / 2))

def comfort_city2(g=0.9, heart=True):
    """Комфортный и гостеприимный город: усреднённое классическое здание города —
    портик с фронтоном и круглым окном, четыре колонны, крылья с арочными окнами,
    общий цоколь; рядом сердце."""
    base_top = BASE - 2.6
    ct, cb = 21.2, 23.8                                            # карниз и антаблемент — одна линия
    plinth = rect2(4.0, base_top, 46.0, BASE)
    def arched(x, y0, y1, w):
        return union(rect2(x, y0 + w / 2, x + w, y1), circle(x + w / 2, y0 + w / 2, w / 2))
    parts = [plinth]
    for x0, x1 in ((5.0, 15.0), (35.0, 45.0)):
        wall = rect2(x0, cb + g, x1, base_top - g)
        wins = [arched(xc - 1.35, 27.8, 35.8, 2.7) for xc in (x0 + 3.0, x1 - 3.0)]
        parts += [diff(wall, *wins), rect2(x0 - 0.6, ct, x1 + (0.6 if x0 > 25 else 0.0) - (0 if x0 > 25 else 0), cb)]
    parts[-1] = rect2(35.0, ct, 45.6, cb)
    parts[2] = rect2(4.4, ct, 15.0, cb)
    ent = rect2(15.0 + g, ct, 35.0 - g, cb)
    ped = diff(poly((15.0, ct - g), (25.0, 12.0), (35.0, ct - g)), circle(25.0, 16.9, 1.6))
    n, cw, x0, x1 = 4, 2.6, 16.6, 33.4
    step = (x1 - x0 - cw) / (n - 1)
    cols = [rect2(x0 + i * step, cb + g, x0 + i * step + cw, base_top - g) for i in range(n)]
    house = union(*parts, ent, ped, *cols)
    if heart:
        hrt = heart_shape(40.4, 13.4, 9.0)
        house = union(diff(house, dilate(hrt, 1.3)), hrt)
    return house

def park_columns(g=1.3, inset=1.5, W=15.16, slab=2.84, cham=1.4):
    """Вход в парк Машиностроителей — исходные две колонны, но плотнее: просветы между
    деталями g вместо 1.9, верхняя плита — со скосами снизу (треугольный срез) вместо
    ступеньки, колонны на inset ближе друг к другу."""
    out = []
    for x0 in (4.16 + inset, 30.69 - inset):
        x1 = x0 + W; m = 0.95
        y = BASE
        plinth = rect2(x0, y - 3.79, x1, y); y -= 3.79 + g
        bw = (W - 2 * m - g) / 2                                     # два блока базы и капители
        blocks = lambda yb, yt: [rect2(x0 + m, yt, x0 + m + bw, yb), rect2(x1 - m - bw, yt, x1 - m, yb)]
        base = blocks(y, y - 1.9); y -= 1.9 + g
        top_slab_top = 8.76
        cap_b = top_slab_top + slab + g + 1.9                         # низ блоков капители
        sw = 4.4                                                      # стволы — по центрам блоков
        cs = (x0 + m + bw / 2, x1 - m - bw / 2)
        shafts = [rect2(c - sw / 2, cap_b + g, c + sw / 2, y) for c in cs]
        cap = blocks(cap_b, cap_b - 1.9)
        sb = top_slab_top + slab
        top = poly((x0, top_slab_top), (x1, top_slab_top), (x1, sb - cham), (x1 - cham, sb), (x0 + cham, sb), (x0, sb - cham))
        out += [plinth, *base, *shafts, *cap, top]
    return union(*out)

def combine3(g=1.34):
    """Комбайн: колёса, кабина, корпус и бункер разделены просветами как у трактора (g);
    жатка — исходная: пятиугольник с прорезью, «палец» подающей камеры в нём и ковш внизу,
    со своими исходными зазорами (при g палец и нижняя полка жатки превращаются в щепки)."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["4254:3023"]["svg"])
    wheels = union(P(ds[0]), P(ds[1]))
    cab = P(ds[2]); cab.fillType = pathops.FillType.EVEN_ODD; cab = union(cab, Path())
    header = P(ds[3])
    body, tank = P(ds[4]), P(ds[5])
    cab = diff(cab, dilate(wheels, g))
    front = union(wheels, cab, header); out = [wheels, cab, header]
    for part in (body, tank):
        part = drop_small(diff(part, dilate(front, g)), 0.8)
        if part is tank:                                  # верхний правый угол бункера — ровный, без крючка
            part = diff(part, inter(rect2(22.5, 13.0, 26.0, 17.0), diff(part, opening(part, 1.0))))
        out.append(part); front = union(front, part)
    return union(*out)

def tractor2(g=1.3):
    """Трактор: колёса — ровные круги на прежних центрах; подкрылки — дуги ровно на
    просвете g от колеса, без ступеньки у левого края и крючка у правого."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["4254:3026"]["svg"])
    body = P(ds[2]); body.fillType = pathops.FillType.EVEN_ODD; body = union(body, Path())
    c1, r1 = (13.24, 36.13), 7.83
    c2, r2 = (39.13, 38.43), 5.47
    fill1 = inter(circle(*c1, r1 + g + 0.6), rect2(6.14, 26.0, 22.6, 38.11))
    fill2 = inter(circle(*c2, r2 + g + 0.6), rect2(32.0, 30.0, 44.39, 38.11))
    body = diff(union(body, fill1, fill2), dilate(circle(*c1, r1), g), dilate(circle(*c2, r2), g))
    return union(body, circle(*c1, r1), circle(*c2, r2))

def sanatorium3():
    """Санаторий без елей: только здание (прямые стены на базе, как в круге 7)."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2891:599"]["svg"])
    top = P(ds[3])
    pediment = inter(P(ds[2]), rect2(0, 0, 50, 21.75))
    walls = rect2(12.0, 21.7, 38.05, BASE)
    plinth = rect2(10.87, 41.9, 39.19, BASE)
    holes = [rect2(15.4, 31.98, 20.41, 36.89), rect2(29.67, 31.98, 34.64, 36.89),
             rect2(15.4, 24.04, 20.56, 29.1), rect2(29.52, 24.04, 34.59, 29.1),
             rect2(22.44, 32.63, 27.74, BASE + 1)]
    return union(top, pediment, diff(union(walls, plinth), *holes))

def fir(cx, top, Hc, trunk_h, slope=0.62, tw=2.0, tiers=((0.0, 0.40), (0.22, 0.70), (0.46, 1.0))):
    """Геометричная ель: ярусы — равнобедренные треугольники одного уклона, ствол — прямоугольник."""
    parts = []
    for a, b in tiers:
        ya, yb = top + a * Hc, top + b * Hc; hw = slope * (yb - ya)
        parts.append(poly((cx, ya), (cx + hw, yb), (cx - hw, yb)))
    parts.append(rect2(cx - tw / 2, top + Hc - 0.5, cx + tw / 2, top + Hc + trunk_h))
    return union(*parts)

def firs2(g=1.3, side_k=0.82, dx=12.6, slope=0.74, Hc=27.0, th=6.0,
          tiers=((0.0, 0.38), (0.2, 0.68), (0.42, 1.0))):
    """Лес с елями: три геометричные ели — прямые скаты одного уклона, ярусы ровными
    ступенями, строгая симметрия. Средняя впереди, боковые за ней на просвете g."""
    mid = fir(25.0, BASE - Hc - th, Hc, th, slope=slope, tiers=tiers)
    sides = [fir(25.0 + sg * dx, BASE - (Hc + th) * side_k, Hc * side_k, th * side_k, slope=slope,
                 tw=2.0 * side_k + 0.2, tiers=tiers) for sg in (-1, 1)]
    sides = drop_small(diff(union(*sides), dilate(mid, g, join="miter")), 1.5)
    return union(mid, sides)

def firs3(g=1.3, side_k=0.8, slope=0.5, Hc=28.0, th=6.0, tiers=((0.0, 0.40), (0.24, 0.70), (0.46, 1.0))):
    """Лес с елями: три стройные геометричные ели рядом, без наложения — прямые скаты
    одного уклона, ярусы ровными ступенями, строгая симметрия. Между елями — просвет g."""
    hw_m = slope * (tiers[-1][1] - tiers[-1][0]) * Hc
    mid = fir(25.0, BASE - Hc - th, Hc, th, slope=slope, tiers=tiers)
    dx = hw_m + hw_m * side_k + g
    sides = [fir(25.0 + sg * dx, BASE - (Hc + th) * side_k, Hc * side_k, th * side_k, slope=slope,
                 tw=2.0 * side_k + 0.2, tiers=tiers) for sg in (-1, 1)]
    return union(mid, *sides)

def rest_base3(halo=0.7):
    """База отдыха: как в круге 7 (дом без «ступни», ель исходная), но окно с подоконником —
    верхние створки сливаются с белой полосой подоконника со скруглёнными концами."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2891:608"]["svg"])
    roof, tree = P(ds[2]), P(ds[1])
    ax = 21.2
    body = poly((9.98, BASE), (9.98, 35.66), (ax, 24.6), (32.47, 35.74), (32.47, BASE))
    body = diff(body, inter(rect2(ax - 3, 20, ax + 3, 28), diff(body, opening(body, 1.3))))
    pw, mul_ = 2.5, 1.1
    xl, xr = ax - mul_ / 2 - pw, ax + mul_ / 2
    upper = [rect2(x, 29.9, x + pw, 34.6) for x in (xl, xr)]
    sill = rect2(ax - 5.1, 34.0, ax + 5.1, 35.15, 0.55)
    lower = [rect2(x, 36.25, x + pw, 40.15) for x in (xl, xr)]
    body = diff(body, *upper, sill, *lower)
    house = union(roof, body)
    tree = diff(tree, dilate(house, halo))
    return union(house, tree)

def scales2():
    """Весы ближе к квадрату: балка поднята до верха поля, подвесы длиннее,
    чаши и балка чуть уже — пропорция почти 1 : 1."""
    return scales(top=7.0, inward=1.0, pan_in=0.5)

def elevator2(lift=6.5, cut=24.5):
    """Элеватор ближе к квадрату: силосы выше на lift — верх с крышками и балкой поднят,
    промежуток залит тем же сечением силосов; колос в среднем силосе на месте."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["4254:3021"]["svg"])
    silos = []
    for d in ds[:3]:
        q = P(d); q.fillType = pathops.FillType.EVEN_ODD; silos.append(union(q, Path()))
    band = P(ds[3]); band.fillType = pathops.FillType.EVEN_ODD; band = union(band, Path())
    out = [move(band, 0, -lift)]
    for sp in silos:
        x0, _, x1, _ = sp.bounds
        up = move(inter(sp, rect2(0, 0, 50, cut)), 0, -lift)
        low = inter(sp, rect2(0, cut, 50, 50))
        sec = inter(sp, rect2(0, cut - 0.05, 50, cut + 0.05))
        sx0, _, sx1, _ = sec.bounds
        fill = rect2(sx0, cut - lift - 0.3, sx1, cut + 0.3)
        out.append(union(low, fill, up))
    res = Path()
    for q in out: res = union(res, q) if len(list(res.contours)) else union(q, Path())
    return res

def _cr_path(pts, closed_tail=None):
    """Гладкий путь Катмулла — Рома через точки (кубиками). closed_tail — точки замыкания."""
    p = Path(); p.moveTo(*pts[0])
    ext = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(ext) - 2):
        a, b, c, d_ = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        c1 = (b[0] + (c[0] - a[0]) / 6, b[1] + (c[1] - a[1]) / 6)
        c2 = (c[0] - (d_[0] - b[0]) / 6, c[1] - (d_[1] - b[1]) / 6)
        p.cubicTo(*c1, *c2, *c)
    if closed_tail is not None:
        for q in closed_tail: p.lineTo(*q)
        p.close()
    return p

def _cr_fn(pts):
    """Функция точки t∈[0,1] на сплайне Катмулла — Рома (равномерно по сегментам)."""
    ext = [pts[0]] + list(pts) + [pts[-1]]; n = len(pts) - 1
    def f(t):
        u = min(max(t, 0.0), 1.0) * n; i = min(int(u), n - 1); s_ = u - i
        a, b, c, d_ = ext[i], ext[i + 1], ext[i + 2], ext[i + 3]
        c1 = (b[0] + (c[0] - a[0]) / 6, b[1] + (c[1] - a[1]) / 6)
        c2 = (c[0] - (d_[0] - b[0]) / 6, c[1] - (d_[1] - b[1]) / 6)
        return point((b, c1, c2, c), s_)
    return f

def investments6(we=1.3, ge=0.8, L=9.7):
    """Инвестиции по референсу: два потока входят слева, третий — снизу, сходятся в древко.
    Как перья логотипа: у стрелки три параллельные полосы с ровными узкими просветами ge
    входят прямо в основание стрелки (единая стрелка пака). Просветы сужаются от кромки
    кадра к стрелке. Единицы — поле референса 36.1 × 34.26: левый край u=0, низ v=34.26."""
    Hb = 34.26
    d = norm((193.0, -197.0)); nul = norm((-0.7143, -0.6998))
    Bc = (29.27, 6.95)
    half = (3 * we + 2 * ge) / 2
    tT, tB = add(Bc, mul(nul, half)), sub(Bc, mul(nul, half))
    top = [(-1.5, 18.98), (0.0, 18.9), (5.65, 18.53), (12.7, 17.1), (19.4, 14.0), (24.3, 9.4), tT, add(tT, mul(d, 2.5))]
    right = [(17.84, 35.5), (17.84, 34.26), (17.84, 30.9), (18.5, 26.65), (20.5, 21.7), (23.3, 17.1), (27.2, 12.1), tB, add(tB, mul(d, 2.5))]
    solid = union(_cr_path(top + list(reversed(right)), closed_tail=[(-1.5, 35.5)]), Path())
    s1e, s2e = add(Bc, mul(nul, we / 2 + ge / 2)), sub(Bc, mul(nul, we / 2 + ge / 2))
    slit1 = [(-1.5, 26.6), (0.0, 26.35), (5.65, 24.55), (12.0, 21.9), (16.25, 19.05), (20.4, 15.2), add(s1e, mul(d, -3.0)), add(s1e, mul(d, 1.5))]
    w1 = [3.5, 3.5, 2.4, 1.6, 1.15, ge, ge, ge]
    slit2 = [(7.77, 35.5), (7.77, 34.26), (9.2, 30.75), (12.2, 26.15), (16.6, 20.65), (21.4, 16.0), add(s2e, mul(d, -3.0)), add(s2e, mul(d, 1.5))]
    w2 = [4.2, 4.2, 2.6, 1.6, 1.1, ge, ge, ge]
    def wfn(ws):
        n = len(ws) - 1
        return lambda t: ws[min(int(t * n), n - 1)] + (ws[min(int(t * n), n - 1) + 1] - ws[min(int(t * n), n - 1)]) * (t * n - min(int(t * n), n - 1))
    slits = [P(band_fn(_cr_fn(sp), wfn(ws), parts=14, n=24)) for sp, ws in ((slit1, w1), (slit2, w2))]
    head = arrow_head(add(Bc, mul(d, L)), d, L)
    shape = diff(union(solid, head), *slits)
    shape = union(diff(shape, head), head)                         # стрелка сплошная, просветы в неё не заходят
    return inter(shape, rect2(0.0, -5.0, 60.0, Hb))

def investments_ref(px=True):
    """Инвестиции — векторизация рисунка заказчика (поле рисунка 1256 px) с лёгкой правкой
    геометрии: кромки — гладкие сплайны через точки рисунка, прорези сужаются ровно до
    острия, наконечник симметричен относительно своей оси (крылья разошлись на 12 px —
    выровнены), края кадра — прямые срезы. px=False — в единицах иконки (масштаб 36.1/1022)."""
    X0, Y1 = 140.0, 1095.0
    tip = (1162.0, 125.0)
    d = norm((193.0, -197.0)); n = (-d[1], d[0])                    # n — к нижнему крылу
    if n[0] < 0: n = mul(n, -1)
    A = lambda a, b: add(tip, add(mul(d, a), mul(n, b)))             # точка в осях стрелки
    j_up, j_lo = A(-276, -34.7), A(-276, 34.7)                       # стыки древка со стрелкой
    w_up, w_lo = A(-307, -163), A(-307, 163)                         # концы крыльев
    top = [(X0 - 20, 661.0), (X0, 660.0), (300.0, 651.0), (500.0, 612.0), (700.0, 522.0), (850.0, 404.0), j_up]
    right = [(645.0, Y1 + 20), (645.0, Y1), (645.0, 1000.0), (665.0, 880.0), (720.0, 740.0), (800.0, 610.0), (902.0, 468.0), j_lo]
    p = _cr_path(top)
    # наконечник: вогнутый «совок» от стыка к крылу, слегка вогнутая передняя кромка к острию
    def cub(a, b, c, e): p.cubicTo(*b, *c, *e)
    cub(j_up, A(-262, -77), A(-275, -121), w_up)
    cub(w_up, A(-200, -96), A(-100, -40), tip)
    cub(tip, A(-100, 40), A(-200, 96), w_lo)
    cub(w_lo, A(-275, 121), A(-262, 77), j_lo)
    rr = list(reversed(right))
    ext = [rr[0]] + rr + [rr[-1]]
    for i in range(1, len(ext) - 2):
        a, b, c, e = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        p.cubicTo(b[0] + (c[0] - a[0]) / 6, b[1] + (c[1] - a[1]) / 6, c[0] - (e[0] - b[0]) / 6, c[1] - (e[1] - b[1]) / 6, *c)
    p.lineTo(X0 - 20, Y1 + 20); p.close()
    solid = union(p, Path())
    def taper(ws):
        k = len(ws) - 1
        def f(t):
            i = min(int(t * k), k - 1); u = t * k - i
            return ws[i] + (ws[i + 1] - ws[i]) * u
        return f
    s1 = [(X0 - 30, 880.0), (X0, 871.0), (300.0, 822.0), (480.0, 747.0), (600.0, 667.0), (710.0, 548.0)]
    s2 = [(352.0, Y1 + 30), (360.0, Y1), (400.0, 986.0), (485.0, 857.0), (610.0, 702.0), (740.0, 583.0)]
    slit1 = P(band_fn(_cr_fn(s1), taper([98, 98, 66, 47, 27, 0.01]), parts=12, n=24))
    slit2 = P(band_fn(_cr_fn(s2), taper([114, 114, 92, 62, 32, 0.01]), parts=12, n=24))
    out = inter(diff(solid, slit1, slit2), rect2(X0, 0, 1300, Y1))
    if px: return out
    k = 36.1 / 1022.0
    return tf(out, (k, 0, 0, k, -X0 * k, -125.0 * k))

def participation2(w=2.2, g=1.3):
    """Участие: ладони поменялись ролями — передняя залитая, задняя контурная
    (обводка той же толщины w), между ними просвет g."""
    import re
    d = re.findall(r' d="([^"]+)"', SRC["4254:3193"]["svg"])[0]
    subs = ["M" + x for x in d.split("M") if x.strip()]
    outer, inner = P(subs[0]), P(subs[1])
    sil = dilate(inner, w + 0.25)                              # прежний силуэт передней ладони (с запасом — без волосяной кромки)
    front = dilate(inner, (w - g) / 2)                         # залитая: пальцы разделены просветом g
    back_vis = diff(outer, sil)                                # видимая часть задней
    ring = diff(back_vis, erode(union(back_vis, sil), w))      # обводка задней только по её внешнему краю
    ring = opening(diff(ring, dilate(front, g)), 0.3)
    return union(front, drop_small(ring, 1.0))

def erode(p, r):
    edge = Path(); edge.addPath(p)
    edge.stroke(2 * r, LineCap.ROUND_CAP, LineJoin.ROUND_JOIN, 4); edge.convertConicsToQuads()
    return diff(p, edge)

# ── общие детали пака: дерево, ель, домик ─────────────────────────────────────

def _res_tree_raw():
    """Дерево из «Богатых природных ресурсов» (эталон): крона-облако, ствол с ветками-прорезями
    и ромбом; ствол продолжен прямо вниз."""
    src = src_path("2888:587"); out = Path()
    for c in src.contours:
        q = Path(); c.draw(q.getPen())
        if q.bounds[1] < 30: q.draw(out.getPen())
    t = union(out, Path())
    return union(inter(t, rect2(0, 0, 50, 30.5)), rect2(23.14, 30.0, 26.90, 60.0))

RES_TRUNK_X, RES_TOP, RES_W = 25.02, 6.36, 31.24

def tree(cx, top, crown_w, bottom=BASE, slit_min=0.7):
    """Дерево пака: эталонное дерево, крона шириной crown_w, верх кроны top, ствол до bottom.
    При уменьшении прорези веток и ромб расширяются до slit_min, чтобы не превращаться в волосок."""
    k = crown_w / RES_W
    t = tf(_res_tree_raw(), (k, 0, 0, k, cx - k * RES_TRUNK_X, top - k * RES_TOP))
    if k < 1.0 and slit_min > 0:
        r = 0.9
        notch = diff(erode(dilate(t, r), r), t)
        zone = rect2(cx - 0.32 * crown_w, top + 0.38 * crown_w * 0.88, cx + 0.32 * crown_w, top + 0.80 * crown_w * 0.88)
        notch = inter(notch, zone)
        grow = max(0.0, (slit_min - 0.9 * k) / 2)
        if grow > 0: t = diff(t, dilate(notch, grow))
    tw = 1.88 * k
    t = union(t, rect2(cx - tw, top + k * (29.0 - RES_TOP), cx + tw, bottom))
    return inter(t, rect2(cx - crown_w, top - crown_w, cx + crown_w, bottom))

def fir_shape():
    """Ель пака — средняя ель из «Леса с елями» (2892:596)."""
    import re
    return P(re.findall(r' d="([^"]+)"', SRC["2892:596"]["svg"])[2])

def fir_at(cx, top, h, bottom=BASE):
    f = fir_shape(); x0, y0, x1, y1 = f.bounds; k = h / (y1 - y0)
    return tf(f, (k, 0, 0, k, cx - k * (x0 + x1) / 2, top - k * y0))

def _house_raw():
    """Силуэт домика из «Промышленного производства»: скат, свесы со скруглёнными концами, стены."""
    import re
    d = re.findall(r' d="([^"]+)"', SRC["2888:578"]["svg"])[3]
    return P("M" + [x for x in d.split("M") if x.strip()][0])

def house_form(cx, wall_w, wall_top, bottom=BASE):
    """Домик пака единой формы: стены шириной wall_w, верх стен wall_top, низ bottom."""
    k = wall_w / (41.8213 - 8.19825)
    h = tf(_house_raw(), (k, 0, 0, k, cx - k * 25.01, wall_top - k * 20.43))
    return union(inter(h, rect2(cx - wall_w, wall_top - wall_w, cx + wall_w, bottom)), rect2(cx - wall_w / 2, wall_top + 1, cx + wall_w / 2, bottom))

def rotunda():
    """Ротонда центрального парка (как в круге 7): 2-й и 4-й столбы убраны, концы кровли без крючков."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2892:607"]["svg"])
    pav = P(ds[0]); orig = pav
    for x0, x1 in ((16.2, 18.3), (32.9, 35.0)):
        pav = diff(pav, rect2(x0, 28.9, x1, 42.2))
        yl, yr = (29.25, 29.15) if x0 < 25 else (29.15, 29.25)
        pav = union(pav, inter(orig, poly((x0, 20), (x1, 20), (x1, yr), (x0, yl))))
    for xa, xb, cx in ((0, 8.3, 7.12), (41.7, 50, 42.88)):
        pav = diff(pav, rect2(xa, 30.35, xb, 32.5))
        sgn = -1 if cx < 25 else 1
        corner = rect2(min(cx, cx + sgn * 1.2), 29.3, max(cx, cx + sgn * 1.2), 30.5)
        pav = diff(pav, diff(corner, circle(cx, 29.35, 1.0)))
    return pav

def central_park7(halo=0.7, cw=13.6, gap_above=1.4):
    """Центральный парк — горизонтальная иконка: ротонда и два дерева пака (как в «Ресурсах»);
    стволы — на месте 2-го и 4-го столбов, симметрично; кроны над кровлей."""
    pav = rotunda()
    k = cw / RES_W; crown_h = (30.0 - RES_TOP) * k
    top = 26.05 - gap_above - crown_h
    trees = union(*[tree(x, top, cw) for x in (17.26, 32.74)])
    trees = diff(trees, dilate(pav, halo, join="miter"))
    return union(pav, trees)

def public_spaces2(halo=0.7):
    """Общественные пространства: скамейка исходная, дерево — дерево пака на месте прежнего."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2888:599"]["svg"])
    bench = union(*[P(d) for d in ds[1:]])
    return union(bench, tree(33.8, 10.58, 24.45))

def green_city2(halo=0.7):
    """Город парков: дома исходные впереди, за ними дерево пака; ствол — в просвете между домами."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2891:595"]["svg"])
    houses = []
    for d in ds[:2]:
        q = P(d); q.fillType = pathops.FillType.EVEN_ODD; houses.append(union(q, Path()))
    houses = union(*houses)
    t = tree(21.1, 8.58, 28.0)
    return union(houses, diff(t, dilate(houses, halo, join="miter")))

def machinists_park2():
    """Парк Машиностроителей: холмы и дорожка исходные, деревья — деревья пака на прежних местах."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["4254:3118"]["svg"])
    outer = [P("M" + [x for x in d.split("M") if x.strip()][0]) for d in ds[:2]]   # только внешние силуэты — без старых прорезей
    hills = inter(union(*outer), rect2(0, 37.4, 50, 50))
    steps = union(*[P(d) for d in ds[2:]])
    trees = union(tree(12.95, 14.0, 17.5, 38.0), tree(37.05, 14.0, 17.5, 38.0))
    return union(hills, trees, steps)

def rest_base4(halo=0.7):
    """База отдыха: домик единой формы (как в «Промышленном производстве»), окно с подоконником,
    за домом — ель пака (как в «Лесе с елями»)."""
    ax = 21.2
    house = house_form(ax, 22.5, 27.5)
    pw, mul_ = 2.5, 1.1
    xl, xr = ax - mul_ / 2 - pw, ax + mul_ / 2
    holes = [rect2(x, 30.4, x + pw, 34.6) for x in (xl, xr)] + [rect2(ax - 5.1, 34.0, ax + 5.1, 35.15, 0.55)] + \
            [rect2(x, 36.25, x + pw, 40.15) for x in (xl, xr)]
    house = diff(house, *holes)
    fir = fir_at(37.4, 10.5, 32.6)
    return union(house, diff(fir, dilate(house, halo)))

def farm5(k=1.12, gw=1.4):
    """Ферма: поля прежние, амбар — домик единой формы с дверью."""
    f = farm_fields(k, gw)
    barn = diff(house_form(25.0, 21.0, 16.5, 40.0), rect2(21.8, 23.5, 28.2, 41.0))
    return union(diff(barn, dilate(farm_fields.solid, gw)), f)

def comfort_city3(h=22.0, gap=26.0):
    """Комфортный и гостеприимный город по рисунку заказчика (поле 1256 px), в общем виде пака:
    дерево пака, домики единой формы, ровные просветы h (дома–земля–дерево) и gap (между домами),
    дорожка — плавная белая полоса, сужающаяся к арке."""
    # земля: левый край с мягким углом, верх — плавная линия, правый край с мягким углом
    top = [(60.0, 905.0), (107.0, 900.0), (160.0, 866.0), (300.0, 842.0), (420.0, 826.0), (560.0, 828.0),
           (700.0, 842.0), (760.0, 838.0), (900.0, 852.0), (1050.0, 872.0), (1112.0, 892.0), (1148.0, 935.0), (1160.0, 980.0)]
    ground = union(_cr_path(top, closed_tail=[(1148.0, 1035.0), (107.0, 1035.0)]), Path())
    ground = inter(ground, rect2(107.0, 0, 1148.0, 1035.0))
    corner = 46.0                                               # скругление верхних углов земли
    ground = diff(ground, diff(rect2(107.0, 860.0, 107.0 + corner, 860.0 + corner), circle(107.0 + corner, 860.0 + corner + 30, corner + 30)))
    # дорожка: две плавные кромки (как на рисунке) — снизу широкая, к арке сужается
    left_e = [(418.0, 1080.0), (418.0, 1035.0), (404.0, 998.0), (440.0, 952.0), (560.0, 904.0), (662.0, 868.0), (678.0, 840.0), (678.0, 790.0)]
    right_e = [(777.0, 790.0), (777.0, 842.0), (792.0, 876.0), (735.0, 914.0), (692.0, 955.0), (718.0, 996.0), (850.0, 1035.0), (850.0, 1080.0)]
    road = union(_cr_path(left_e + right_e, closed_tail=[]), Path())
    ground_solid = ground
    ground = diff(ground, road)
    # дома единой формы
    left = diff(house_form(275.0, 260.0, 695.0, 1000.0), rect2(196, 705, 255, 768), rect2(293, 705, 352, 768))
    mid = house_form(729.5, 265.0, 597.0, 1000.0)
    annex = poly((505.0, 676.0), (540.0, 650.0), (600.0, 650.0), (600.0, 1000.0), (505.0, 1000.0))
    mid = union(mid, annex)
    arch = union(rect2(652.0, 736.0, 803.0, 1100.0), circle(727.5, 736.0, 75.5))
    mid = diff(mid, rect2(701.0, 556.0, 758.0, 616.0), arch, rect2(540.0, 711.0, 590.0, 773.0))
    right = union(rect2(887.0, 650.0, 1148.0, 680.0), rect2(887.0, 690.0, 1128.0, 1000.0))
    right = diff(right, rect2(933, 741, 988, 802), rect2(1027, 741, 1083, 802))
    right = diff(right, dilate(mid, gap, join="miter"))
    houses = union(left, mid, right)
    houses = diff(houses, dilate(ground_solid, h))                  # дома стоят за землёй и над дорожкой не свисают
    t = tree(458.0, 185.0, 485.0, 900.0, slit_min=0)
    t = diff(t, dilate(houses, h, join="miter"))
    t = union(diff(t, dilate(road, h)), inter(t, rect2(0, 0, 2000, 840)))
    return union(ground, houses, t)

def tourism3(k=1.55, Lp=15.0, span=17.0, gap=0.9, wing_w=32.86):
    """Туризм: полосы знака крупнее в k раз (увеличены от стыка у самолёта) и обрезаны
    прежней рамкой — фрагменты крупные, линии толще; самолёт прежний."""
    s = wing_w / (75.0 - 21.11)
    h = (60.62419 - 1.42019) * s
    y0 = (TOP + BASE) / 2 - h / 2
    m = (-s, 0, 0, s, LEFT + 75.0 * s, y0 - 1.42019 * s)
    wings = tf(logo_wings(), m)
    cy = y0 + ((27.5161 + 33.685) / 2 - 1.42019) * s
    jx = LEFT + (75.0 - 21.11) * s
    wings = tf(wings, (k, 0, 0, k, jx - k * jx, cy - k * cy))
    wings = inter(wings, rect2(LEFT, y0, jx + 0.01, y0 + h))
    plane = airplane(RIGHT, cy, Lp, span)
    wings = diff(wings, dilate(plane, gap, join="miter"))
    return union(wings, plane)

def resource_fields():
    """Поля из нашей иконки «Богатые природные ресурсы» (2888:587) — как есть, без дерева."""
    src = src_path("2888:587"); out = []
    for c in src.contours:
        if c.bounds[1] > 30:
            q = Path(); c.draw(q.getPen()); out.append(q)
    return union(*out)

def farm3(gap=1.4):
    """Ферма на наших полях: поля взяты из «Богатых природных ресурсов» без изменений,
    вместо дерева — амбар. Амбар отделён от полей тем же просветом, что и ствол дерева."""
    f = resource_fields()
    barn = poly((13.5, 17.5), (25.0, 8.0), (36.5, 17.5), (36.5, 40.0), (13.5, 40.0))
    barn = diff(barn, rect2(21.8, 23.5, 28.2, 41.0))
    return union(diff(barn, dilate(f, gap)), f)

def _cubic_path(c, a=0.0, b=0.0, tail=None):
    """Кубика c с продолжением по касательной на a в начале и на b в конце; tail — точки,
    которыми контур замыкается (для области), иначе — открытая линия."""
    d0 = norm(sub(c[0], c[1])) if math.dist(c[0], c[1]) > 1e-6 else norm(sub(c[0], c[2]))
    d1 = norm(sub(c[3], c[2])) if math.dist(c[3], c[2]) > 1e-6 else norm(sub(c[3], c[1]))
    s0, s1 = add(c[0], mul(d0, a)), add(c[3], mul(d1, b))
    p = Path(); p.moveTo(*s0); p.lineTo(*c[0]); p.cubicTo(*c[1], *c[2], *c[3]); p.lineTo(*s1)
    if tail:
        for q in tail: p.lineTo(*q)
        p.close(); return union(p, Path())
    return p

def farm_fields(k=1.346, gw=1.4):
    """Поля «Богатых природных ресурсов», раздвинутые по ширине кадра: кривые исходника
    растянуты по горизонтали, просветы заново проведены ровной толщины gw."""
    T1 = ((9.46, 32.28), (19.16, 31.0), (28.99, 34.88), (34.83, 42.97))        # верх левого поля
    G1 = ((9.395, 35.295), (16.45, 34.56), (23.365, 37.33), (27.805, 43.08))    # просвет в левом поле
    T2 = ((28.55, 35.0), (32.24, 33.2), (36.37, 32.6), (40.51, 33.32))          # верх правого поля
    G2 = ((32.84, 38.27), (35.375, 37.325), (37.97, 37.165), (40.575, 37.74))   # просвет в правом поле
    sx = lambda c: tuple((25 + k * (x - 25), y) for x, y in c)
    T1, G1, T2, G2 = sx(T1), sx(G1), sx(T2), sx(G2)
    L = _cubic_path(T1, 6, 6, tail=[(45, 60), (-5, 60), (-5, 30)])
    R = _cubic_path(T2, 8, 6, tail=[(55, 30), (55, 60), (15, 60)])
    left = diff(L, stroke(_cubic_path(G1, 6, 4), gw))
    right = diff(R, dilate(L, gw), stroke(_cubic_path(G2, 5, 6), gw))
    frame = rect2(LEFT, 0, RIGHT, BASE)
    farm_fields.solid = inter(union(L, R), frame)             # общий силуэт полей — по нему режется амбар
    return inter(union(left, right), frame)

def farm4(k=1.346, gw=1.4):
    """Ферма по ширине кадра: наши поля раздвинуты влево и вправо до направляющих 4 и 46,
    амбар прежний."""
    f = farm_fields(k, gw)
    barn = poly((13.5, 17.5), (25.0, 8.0), (36.5, 17.5), (36.5, 40.0), (13.5, 40.0))
    barn = diff(barn, rect2(21.8, 23.5, 28.2, 41.0))
    return union(diff(barn, dilate(farm_fields.solid, gw)), f)

def opening(p, r):
    """Морфологическое открытие: убирает острые хвостики и щепки уже 2r."""
    edge = Path(); edge.addPath(p)
    edge.stroke(2 * r, LineCap.ROUND_CAP, LineJoin.ROUND_JOIN, 4); edge.convertConicsToQuads()
    return dilate(diff(p, edge), r)

def round_tree(circles, trunk):
    return union(*[circle(*c) for c in circles], rect2(*trunk))

def central_park5(halo=0.7):
    """Деревья — ровные круги, как везде в паке; расположение прежнее."""
    p = central_park4()
    import re
    # берём ротонду и стволы из круга 5, кроны заменяем кругами
    t1 = round_tree([(17.4, 11.4, 4.6), (12.2, 15.4, 4.0), (22.6, 15.4, 4.0)], (16.408, 15.0, 18.142, BASE))
    t2 = round_tree([(34.4, 14.6, 4.4), (29.3, 18.4, 3.8), (39.4, 18.4, 3.8)], (32.985, 18.0, 34.875, BASE))
    t1 = diff(t1, dilate(t2, halo))
    ds = re.findall(r' d="([^"]+)"', SRC["2892:607"]["svg"])
    pav = P(ds[0]); orig = pav
    for x0, x1, yl, yr in ((16.2, 18.3, 29.25, 29.15), (33.0, 35.0, 29.15, 29.25)):
        pav = diff(pav, rect2(x0, 28.9, x1, 42.2))
        pav = union(pav, inter(orig, poly((x0, 20), (x1, 20), (x1, yr), (x0, yl))))
    for xa, xb, cx in ((0, 8.3, 7.12), (41.7, 50, 42.88)):
        pav = diff(pav, rect2(xa, 30.35, xb, 32.5))
        sgn = -1 if cx < 25 else 1
        corner = rect2(min(cx, cx + sgn * 1.2), 29.3, max(cx, cx + sgn * 1.2), 30.5)
        pav = diff(pav, diff(corner, circle(cx, 29.35, 1.0)))
    trees = diff(union(t1, t2), dilate(pav, halo, join="miter"))
    return union(pav, trees)

def truck_solid2(halo=0.75):
    """Колёса — ровные круги на прежних центрах; обе арки — один и тот же просвет вокруг колеса."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["4254:3005"]["svg"])
    t = truck_slanted(n=1)
    w1, w2 = P(ds[0]), P(ds[1])
    c1 = ((w1.bounds[0] + w1.bounds[2]) / 2, (w1.bounds[1] + w1.bounds[3]) / 2); r1 = (w1.bounds[2] - w1.bounds[0]) / 2
    c2 = ((w2.bounds[0] + w2.bounds[2]) / 2, (w2.bounds[1] + w2.bounds[3]) / 2); r2 = (w2.bounds[2] - w2.bounds[0]) / 2
    r = (r1 + r2) / 2
    body = diff(t, w1, w2)                                    # кузов без старых колёс
    body = union(body, rect2(c1[0] - r - halo - 0.5, 35.0, c1[0] + r + halo + 0.5, 38.67),   # закрываем старые арки
                 inter(rect2(c2[0] - r - halo - 0.5, 35.0, c2[0] + r + halo + 0.5, 38.63), dilate(body, 0.01)))
    body = inter(body, union(*[c for c in [t]]))              # не выходим за прежний силуэт кузова
    body = union(body, inter(rect2(c1[0] - r - 1.5, 35.0, c1[0] + r + 1.5, 38.67), dilate(t, 3)))
    wheels = union(circle(*c1, r), circle(*c2, r))
    return union(diff(body, dilate(wheels, halo)), wheels)

def church4(base_extra=3.0):
    """Основание — прямоугольник по ширине стен (без карнизных «ушей»), верх основания
    поднят до пяты арки — ступенька под сводом исчезает; храм выше за счёт основания."""
    c = church3()
    top = 27.92
    c = diff(c, rect2(0, 27.0, 7.13, 31.3), rect2(42.89, 27.0, 50, 31.3))  # карнизные выступы
    c = union(c, rect2(7.13, top, 42.89, 31.2))
    # удлиняем основание вниз: всё, что ниже 33, сдвигаем на base_extra, промежуток заливаем
    upper = inter(c, rect2(0, 0, 50, 33.0)); lower = inter(c, rect2(0, 33.0, 50, 50))
    lower = move(lower, 0, base_extra)
    fill = rect2(7.13, 32.9, 42.89, 33.1 + base_extra)        # дверь и окна уезжают вниз целиком
    return union(upper, lower, fill)

def rocket3(body_k=1.15, ex_k=0.85, anchor=(24.6, 26.6)):
    """Ракета симметрична относительно своей оси (x + y = const): берём одну половину
    корпуса и отражаем. Корпус крупнее, выхлоп меньше, концы выхлопа — прежние косые."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2888:612"]["svg"])
    body = P(ds[3]); ex = union(*[P(d) for d in ds[:3]])
    c = 45.0537 + 5.58252                                     # ось через нос под 45°
    half = inter(body, poly((-10, -10), (c + 10, -10), (-10, c + 10)))
    body = union(half, tf(half, (0, -1, -1, 0, c, c)))
    ax, ay = anchor
    body = tf(body, (body_k, 0, 0, body_k, ax - body_k * ax, ay - body_k * ay))
    ex = tf(ex, (ex_k, 0, 0, ex_k, ax - ex_k * ax, ay - ex_k * ay))
    return union(body, diff(ex, dilate(body, 0.01)))

def mentors3():
    """Наставник стоит: опущенная рука — часть корпуса, левая сторона — прямой скос
    от плеча к основанию; второй рукой он пускает искры."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2888:639"]["svg"])
    adult = union(P(ds[1]), poly((10.55, 43.1), (11.49, 34.6), (12.3, 43.1)))
    A, B = (11.2, 26.0), (8.4, 43.1)                          # прямой скос: плечо → основание
    left_cut = poly(A, B, (0, 43.1), (0, 20), (11.2, 20))
    adult = diff(adult, left_cut)
    adult = union(adult, inter(poly(A, B, (22, 43.1), (22, 24)), dilate(adult, 0.01)))
    adult = union(adult, poly(A, B, (14.0, 43.1), (14.0, 25.4)))
    people = union(adult, P(ds[0]), P(ds[2]), P(ds[3]))
    big = sparkle(37.0, 12.4, 8.2)
    return union(diff(people, dilate(big, 1.0)), big, sparkle(45.2, 3.4, 4.2))

def sun3():
    """Диск крупнее (r 12.5), лучи короче (4.5) и ближе к диску (просвет 2.6), углы острые."""
    cx, cy = 25.0, 24.35
    parts = [circle(cx, cy, 12.5)]
    for j in range(8):
        a = math.radians(j * 45)
        parts.append(stroke(line_path([(cx + 15.1 * math.cos(a), cy + 15.1 * math.sin(a)),
                                       (cx + 19.6 * math.cos(a), cy + 19.6 * math.sin(a))]), 3.6, cap="butt"))
    return union(*parts)

def sun4(w=3.6):
    """Размеры исходника: диск r 10.34, лучи от 12.41 до 18.74; лучи тоньше (w вместо 4.14), углы острые."""
    cx, cy = 25.0, 24.35
    parts = [circle(cx, cy, 10.34)]
    for j in range(8):
        a = math.radians(j * 45)
        parts.append(stroke(line_path([(cx + 12.41 * math.cos(a), cy + 12.41 * math.sin(a)),
                                       (cx + 18.74 * math.cos(a), cy + 18.74 * math.sin(a))]), w, cap="butt"))
    return union(*parts)

def hand_adapted():
    """Ладонь чуть ближе к системе: запястье срезано вертикально (а не по диагонали),
    белая линия пальца начинается прямым концом вместо круглого."""
    import re
    hand = P(re.findall(r' d="([^"]+)"', SRC["2888:643"]["svg"])[0])
    hand = union(hand, poly((8.4, 34.13), (12.0, 31.46), (12.0, 41.9), (8.4, 42.61)))
    hand = diff(hand, rect2(0, 0, 8.4, 50))
    hand = union(hand, rect2(20.7, 36.4, 21.45, 38.0))          # закрыли круглый конец линии
    hand = diff(hand, rect2(21.0, 36.547, 21.6, 37.89))          # и открыли прямой
    return hand

def initiatives3():
    k = 1.4
    return union(hand_adapted(), bulb_group(27.6, 28.6 - 10.1 * k, k))

def mutual_help():
    """Взаимопомощь на той же ладони, сердце — соразмерно лампочке в «Поддержке инициатив»."""
    import re
    heart = P(re.findall(r' d="([^"]+)"', SRC["4254:3105"]["svg"])[1])
    x0, y0, x1, y1 = heart.bounds; k = 19.0 / (x1 - x0)
    heart = tf(heart, (k, 0, 0, k, 27.6 - k * (x0 + x1) / 2, 28.4 - k * y1))
    return union(hand_adapted(), heart)

def ellipse(cx, cy, rx, ry):
    k = 0.5523; p = Path(); p.moveTo(cx + rx, cy)
    p.cubicTo(cx + rx, cy + k * ry, cx + k * rx, cy + ry, cx, cy + ry)
    p.cubicTo(cx - k * rx, cy + ry, cx - rx, cy + k * ry, cx - rx, cy)
    p.cubicTo(cx - rx, cy - k * ry, cx - k * rx, cy - ry, cx, cy - ry)
    p.cubicTo(cx + k * rx, cy - ry, cx + rx, cy - k * ry, cx + rx, cy); p.close(); return p

def coin_stack(cx, ytop, ybot, rx=12.0, ry=5.1, gap=0.9, coins=2):
    """Стопка монет: цилиндр, верхняя грань и монеты разделены ровными дугами-просветами."""
    body = union(ellipse(cx, ytop, rx, ry), rect2(cx - rx, ytop, cx + rx, ybot), ellipse(cx, ybot, rx, ry))
    cuts = []
    for j in range(coins):
        y = ytop + (ybot - ytop) * j / coins
        cuts.append(diff(ellipse(cx, y + gap, rx + 0.01, ry), ellipse(cx, y, rx + 1, ry), rect2(0, 0, 50, y)))
    top = ellipse(cx, ytop, rx, ry)
    side = diff(body, *cuts)
    return union(side, top)

def capital():
    """Капитал проще и в системе пака: две стопки монет, без мелких прорезей по рёбрам;
    верх и монеты разделены ровными просветами 0.9, задняя стопка отделена просветом 1.6."""
    front = coin_stack(30.55, 29.6, 38.84)
    back = coin_stack(19.46, 14.04, 23.7)          # чуть выше, чтобы дуга не упиралась в просвет щепкой
    return union(diff(back, dilate(front, 1.6)), front)

def coworking2(bezel=0.8):
    """Монитор без клавиатуры, рамка толще на bezel со всех сторон экрана."""
    import re
    ds = re.findall(r' d="([^"]+)"', SRC["2888:632"]["svg"])
    mon = P(ds[1])
    screen = rect2(7.57 + bezel, 8.85 + bezel, 42.40 - bezel, 29.10 - bezel, 0.8)
    outer = mon
    for c in mon.contours:                                   # силуэт монитора без проёма экрана
        if c.bounds[0] < 6: outer = Path(); c.draw(outer.getPen()); outer = union(outer, Path())
    stand = diff(mon, rect2(0, 0, 50, 32.0))
    return union(diff(inter(outer, rect2(0, 0, 50, 32.1)), screen), stand)

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
