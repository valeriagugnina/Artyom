"""Выравнивание всего пака: каждая иконка в кадре 50×50 по сетке и одинаковая по
визуальному объёму. Перерисованные иконки берутся из icons.py, остальные — из выгрузки.

Правила:
  • поле: x 4…46, база 43.1, верх 7 (высоким и круглым формам — свес до 4 / 6);
  • «стоящие» иконки встают на базу 43.1, «парящие» центрируются по высоте поля;
  • по горизонтали — центр рамки на x = 25;
  • масштаб — до одинаковой площади рамки с поправкой на плотность заливки
    (плотная форма кажется крупнее, ажурная — мельче), с ограничением полем.
Запуск: python3 normalize.py → build/pack/*.svg и build/pack.json"""
import io, json, math, os
import numpy as np, cairosvg
from PIL import Image
from lib import *
import icons as I

HERE = os.path.dirname(os.path.abspath(__file__))
SKIP = {"1256:712", "4268:5960", "1482:1399", "1482:1400", "1482:1401",
        "2888:677",                                     # старое «Участие» убрано из набора
        "2888:660", "4254:1272"}                        # мегафон и монеты — не подходят к набору (круг 11)

REBUILT = {   # узел → функция новой версии
    "4254:1269": I.investments_traced, "4254:3021": I.elevator2,
    "4254:3107": I.tourism4, "2888:570": I.logistics_route3,
    "2892:607": lambda: I.central_park8(cw=18.0, tx=9.6), "2888:599": I.public_spaces2, "2891:595": I.green_city3, "4254:3118": I.machinists_park3, "4254:3193": I.participation4, "2892:596": lambda: I.forest4(d=1.0), "2892:571": I.comfort_city5, "2888:583": I.construction_form,
    "2888:595": I.active_city, "4254:3034": I.youth_runner, "2892:580": I.church5,
    "2891:614": I.hotel3, "2888:612": I.rocket3, "2892:626": I.kite,
    "4254:3191": I.scales2, "2891:591": I.glider_b, "4254:3005": I.truck3, "4254:3003": I.train3, "2888:639": I.mentors4,
    "2888:616": I.career3, "2888:643": I.initiatives4, "4254:3105": I.mutual_help2, "4254:3189": I.sun4,
    "2891:599": I.sanatorium3, "2892:612": I.park_columns, "4254:3026": I.tractor3, "4254:3023": I.combine5, "2891:608": I.rest_base5,
}
SAME_AS = {"4254:3105": "2888:643", "new:farm": "2888:587"}   # ладонь с сердцем ставится в кадр так же, как ладонь с лампочкой
WIDTH_AS = {}   # (монитор вернулся к исходнику)
HEIGHT_AS = {}
NEW = [("new:farm", "Ферма", I.farm7)]                     # новые иконки — компонентов в Фигме ещё нет
FILL = set()
TALL_FIT = set()
TOP_FIT = {}
LEFT_CUT = set()    # ракета: срез выхлопа — на левую направляющую 4, низ — на базу
RENAME = {"4254:3193": "Участие",                     # две ладошки — это «Участие»
          "2888:677": "Участие · старый вариант"}

FLOAT = {"2888:570", "2888:612", "2888:620", "2888:660", "2888:665", "2888:673", "2888:677",
         "2891:586", "2891:591", "2892:626", "4254:3019", "4254:3086", "4254:3110", "4254:3189",
         "4254:3193", "4254:3107"}
ROUND = {"2888:620", "2891:586", "4254:3019", "4254:3110", "4254:3189"}
POINTY = {"2892:596", "2891:608", "2892:580", "2888:591", "2891:595", "2892:607", "2888:583", "new:farm", "2888:574"}   # острые и круглые верхушки
FULL = {}                       # Ф2: полосы сверху по направляющей 7, ноги на базе

SQ = BASE - TOP        # сторона единого квадрата: 36,1
HB = 27.0              # общая высота горизонтальных иконок и транспорта (зелёные линии 11,55 и 38,55)
VB = 21.0              # общая ширина вертикальных иконок (зелёные линии 14,5 и 35,5)
H_MIN, V_MAX = 1.25, 0.8
MB = 33.0              # своя сетка массивных форм (оранжевые линии 8,55 и 41,55)
MASSIVE = {"2888:620", "2891:586", "4254:3019", "2888:673", "4254:3189", "4254:3110",
           "2888:643", "4254:3193", "2888:669", "2888:616"}   # + портфель — плотный прямоугольник      # ладони — плотные, тоже в своей сетке 33
TRANSPORT = {"4254:3005", "4254:3003", "4254:3026", "4254:3023"}
EAVES = {"2888:578"}                                          # склад: свесы со скруглёнными концами
FORCE_SQUARE = {"2891:579", "2891:608", "2892:596"}                       # Колмаков, база отдыха — в квадратный класс
HW_MAX = 38.0          # широкие с косыми/круглыми боками могут чуть выйти за голубой
# Здания — ряд: низ на оранжевой 41,55; плоский верх — на оранжевой 8,55 (высота 33),
# фронтон, купола, кровля, кран — до голубой 7 (высота 34,55); ширина до 38, свесы склада — до красных.
BUILD_BASE, BUILD_FLAT, BUILD_PEAK = 41.55, 33.0, 34.55
BUILDINGS = {"2892:573": "flat", "4254:3021": "flat", "2892:612": "flat",
             "2891:614": "peak", "2891:599": "peak", "2892:580": "peak", "2891:608": "peak-wide", "2888:583": "peak",
             "2888:578": "eaves"}
# Пейзажи (деревья, холмы, аллея) — ажурные, поэтому крупнее: ширина до красных 42, высота до оранжевых 33.
LANDSCAPE = {"2892:607", "2888:599", "4254:3118"}
WIDE_MAX = {"2891:586"}     # Колмаковский пряник (овал) — максимально широкий: 4…46
A_TARGET = 1300.0     # (прежнее правило по площади — не используется)
F_REF = 0.5           # эталонная плотность заливки

def ink_ratio(p):
    x0, y0, x1, y1 = p.bounds
    svg_ = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1 - x0} {y1 - y0}" width="200" height="{max(1, int(200 * (y1 - y0) / (x1 - x0)))}">'
            f'<path d="{to_d(p)}" fill="#000"/></svg>')
    a = np.array(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg_.encode()))).convert("RGBA"))[..., 3]
    return float((a > 127).mean())

_cache = {}
def place(node, p):
    if node in SAME_AS:
        ref = SAME_AS[node]
        if ref not in _cache: _cache[ref] = place(ref, REBUILT[ref]() if ref in REBUILT else I.src_path(ref))
        return _cache[ref][:3] + ("как у " + ref,)
    if node in WIDTH_AS:
        ref = WIDTH_AS[node]
        if ref not in _cache: _cache[ref] = place(ref, REBUILT[ref]())
        rp = REBUILT[ref](); rw = (rp.bounds[2] - rp.bounds[0]) * _cache[ref][0]
        x0, y0, x1, y1 = p.bounds; s = rw / (x1 - x0)
        return s, 25 - s * (x0 + x1) / 2, BASE - s * y1, "шириной как " + ref
    if node in HEIGHT_AS:
        ref = HEIGHT_AS[node]
        if ref not in _cache: _cache[ref] = place(ref, REBUILT[ref]() if ref in REBUILT else I.src_path(ref))
        rp = REBUILT[ref]() if ref in REBUILT else I.src_path(ref)
        rh = (rp.bounds[3] - rp.bounds[1]) * _cache[ref][0]
        x0, y0, x1, y1 = p.bounds; s = rh / (y1 - y0)
        return s, 25 - s * (x0 + x1) / 2, BASE - s * y1, "высотой как " + ref
    x0, y0, x1, y1 = p.bounds; w, h = x1 - x0, y1 - y0
    if node in FULL:
        if FULL[node] is None: return 1.0, 0.0, 0.0, "как построено"
        t, b = FULL[node]; s = (b - t) / h
        return s, 25 - s * (x0 + x1) / 2, b - s * y1, "по высоте поля"
    if node in FILL:
        s = (RIGHT - LEFT) / max(w, h)
        return s, 25 - s * (x0 + x1) / 2, 25 - s * (y0 + y1) / 2, "вписан по большей стороне"
    if node in TOP_FIT:
        s = min((BASE - TOP_FIT[node]) / h, (RIGHT - LEFT) / w)
        return s, 25 - s * (x0 + x1) / 2, BASE - s * y1, "в ширину кадра"
    if node in TALL_FIT:
        s = min(39.1 / h, (RIGHT - LEFT) / w)
        return s, 25 - s * (x0 + x1) / 2, BASE - s * y1, "во всю высоту поля"
    if node in LEFT_CUT:
        s = min(39.1 / h, (RIGHT - LEFT) / w)
        return s, LEFT - s * x0, BASE - s * y1, "срез по левой направляющей"
    # Сетка из трёх классов, всё по центру квадрата (центр по вертикали — 25,05):
    #   квадратные (0,8 < w/h < 1,18) — большая сторона на голубом квадрате 36,1;
    #   горизонтальные (w/h ≥ 1,18) — общая высота HB между зелёными линиями;
    #   вертикальные (w/h ≤ 0,8) — общая ширина VB между зелёными линиями.
    # Прямые края стоят на голубом, круглые и острые выходят до красного (4 и 46):
    # круги — в квадрат 42; острая или круглая верхушка — вверх до 4, плоский низ — на базе.
    a = w / h; cyc = (TOP + BASE) / 2
    if node in BUILDINGS:
        kind = BUILDINGS[node]
        wcap = (RIGHT - LEFT) if kind in ("eaves", "peak-wide") else HW_MAX       # свесы, ель — до красных
        s = min((BUILD_FLAT if kind == "flat" else BUILD_PEAK) / h, wcap / w)
        return s, 25 - s * (x0 + x1) / 2, BUILD_BASE - s * y1, {"flat": "здание · верх 8,55", "peak": "здание · верх до 7", "eaves": "здание · свесы до красных"}[kind.replace("-wide", "")]
    if node in LANDSCAPE:
        s = min((RIGHT - LEFT) / w, MB / h)
        return s, 25 - s * (x0 + x1) / 2, cyc - s * (y0 + y1) / 2, "пейзаж · до красных / оранжевых"
    if node in WIDE_MAX:                                          # пряник-овал — по ширине до красных, насколько можно
        s = min((RIGHT - LEFT) / w, MB / h)
        return s, 25 - s * (x0 + x1) / 2, cyc - s * (y0 + y1) / 2, "по ширине до красных"
    if node in MASSIVE:                                           # массивные — своя сетка, квадрат MB
        s = MB / max(w, h)                                         # круглые тоже ровно по оранжевым линиям
        return s, 25 - s * (x0 + x1) / 2, cyc - s * (y0 + y1) / 2, "массивная" + (" · круг" if node in ROUND else "")
    if node in TRANSPORT:                                         # транспорт — одна высота (зелёные линии);
        s = HB / h                                                 # ширину задаёт сама иконка: поезд и трактор —
        return s, 25 - s * (x0 + x1) / 2, cyc - s * (y0 + y1) / 2, "транспорт · высота по зелёным"   # 36,1, грузовик и комбайн — 42
    if node in EAVES:                                             # свесы кровли — до красного, стены внутри
        s = min((RIGHT - LEFT) / w, SQ / h)
        return s, 25 - s * (x0 + x1) / 2, cyc - s * (y0 + y1) / 2, "квадратная · свесы до красного"
    if node in FORCE_SQUARE:
        s = SQ / max(w, h)
        return s, 25 - s * (x0 + x1) / 2, cyc - s * (y0 + y1) / 2, "квадратная"
    if node in ROUND:
        s = min(42.0 / w, 42.0 / h); cls = "круг · до красной"
        return s, 25 - s * (x0 + x1) / 2, cyc - s * (y0 + y1) / 2, cls
    if a >= H_MIN:
        s = HB / h; cls = "горизонтальная"
        if s * w > HW_MAX: s = HW_MAX / w; cls += " · по ширине"
        return s, 25 - s * (x0 + x1) / 2, cyc - s * (y0 + y1) / 2, cls
    if a <= V_MAX:
        s = min(VB / w, SQ / h); cls = "вертикальная"
        return s, 25 - s * (x0 + x1) / 2, cyc - s * (y0 + y1) / 2, cls
    if node in POINTY:
        s = min(SQ / w, (BASE - 4.0) / h)
        if s * h <= SQ + 1e-6:                                   # верхушка не дотянулась выше — просто по центру
            return s, 25 - s * (x0 + x1) / 2, cyc - s * (y0 + y1) / 2, "квадратная"
        return s, 25 - s * (x0 + x1) / 2, BASE - s * y1, "квадратная · верхушка до красной"
    s = SQ / max(w, h)
    return s, 25 - s * (x0 + x1) / 2, cyc - s * (y0 + y1) / 2, "квадратная"

VARIANTS = {   # узел → дополнительные варианты для страницы (в пак не идут)
}

def variant_place(node, mode, p):
    if mode == "float":                                     # просто вписать по центру поля
        x0, y0, x1, y1 = p.bounds; w, h = x1 - x0, y1 - y0
        s = min((RIGHT - LEFT) / w, (BASE - TOP) / h)
        return s, 25 - s * (x0 + x1) / 2, (TOP + BASE) / 2 - s * (y0 + y1) / 2
    if mode == "ground": node = "—"                          # обычная «стоящая» посадка на базу
    s, dx, dy, _ = place(node, p); return s, dx, dy

XL = {4.0: "красная 4", 6.95: "голубая 6,95", 8.5: "оранжевая 8,5", 14.5: "зелёная 14,5",
      35.5: "зелёная 35,5", 41.5: "оранжевая 41,5", 43.05: "голубая 43,05", 46.0: "красная 46"}
YL = {4.0: "красная 4", 7.0: "голубая 7", 8.55: "оранжевая 8,55", 11.55: "зелёная 11,55",
      38.55: "зелёная 38,55", 41.55: "оранжевая 41,55", 43.1: "голубая 43,1"}
def grid_check(b, tol=0.06):
    """На каких линиях сетки стоят края рамки иконки. ok — хотя бы по одной оси оба края на линиях
    (вторая ось тогда по центру квадрата) или иконка стоит на линии низом и другой край на линии."""
    hit = lambda v, L: next((n for k, n in L.items() if abs(v - k) <= tol), None)
    l, r, t, bt = hit(b[0], XL), hit(b[2], XL), hit(b[1], YL), hit(b[3], YL)
    cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    ok = bool((l and r) or (t and bt))
    return dict(left=l, right=r, top=t, bottom=bt, cx=round(cx, 2), cy=round(cy, 2), ok=ok)

def main():
    out = os.path.join(HERE, "build/pack"); os.makedirs(out, exist_ok=True)
    meta = []
    items = [(node, v["name"], None) for node, v in I.SRC.items() if node not in SKIP] + NEW
    for node, name0, fn in items:
        v = {"name": name0}
        p = fn() if fn else (REBUILT[node]() if node in REBUILT else I.src_path(node))
        s, dx, dy, note = place(node, p)
        q = tf(p, (s, 0, 0, s, dx, dy))
        name = RENAME.get(node, v["name"].replace("Иконки/", ""))
        slug = node.replace(":", "-")
        open(os.path.join(out, f"{slug}.svg"), "w").write(svg(q))
        b = q.bounds
        meta.append(dict(node=node, name=name, old=v["name"], rebuilt=node in REBUILT or fn is not None, new=fn is not None, scale=round(s, 4),
                         dx=round(dx, 3), dy=round(dy, 3), bounds=[round(x, 2) for x in b], note=note,
                         float=node in FLOAT, grid=grid_check(b)))
        print(f"{name[:34]:36s} s={s:.3f}  x {b[0]:5.2f}…{b[2]:5.2f}  y {b[1]:5.2f}…{b[3]:5.2f}  {note}")
    json.dump(meta, open(os.path.join(HERE, "build/pack.json"), "w"), ensure_ascii=False, indent=1)
    bad = [m for m in meta if not m["grid"]["ok"]]
    print(f"проверка сетки: {len(meta) - len(bad)} из {len(meta)} иконок стоят краями на линиях" +
          ("" if not bad else "; не на линиях: " + ", ".join(m["name"] for m in bad)))
    vd = os.path.join(HERE, "build/variants"); os.makedirs(vd, exist_ok=True)
    for node, vs in VARIANTS.items():
        for slug, fn, mode in vs:
            p = fn(); s, dx, dy = variant_place(node, mode, p)
            open(os.path.join(vd, f"{slug}.svg"), "w").write(svg(tf(p, (s, 0, 0, s, dx, dy))))
            print("вариант", slug, round(s, 3))

if __name__ == "__main__":
    main()
