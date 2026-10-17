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
        "2888:677"}                                     # старое «Участие» убрано из набора

REBUILT = {   # узел → функция новой версии
    "4254:1269": lambda: I.investments3(theta=20, s=0.88, tip=(46, 9.8)),
    "4254:3107": I.tourism2, "2888:570": I.logistics_route,
    "2892:607": I.central_park3, "2892:571": lambda: I.city3("B"), "2888:583": I.construction_plain,
    "2888:595": I.active_city, "4254:3034": I.youth_runner, "2892:580": I.church2,
    "2891:614": I.hotel, "2888:632": I.coworking, "2888:612": I.rocket, "2892:626": I.kite,
    "4254:3191": I.scales, "2891:591": I.glider, "4254:3005": I.truck_slanted, "2888:639": I.mentors,
    "2888:616": I.career, "2888:643": I.initiatives, "4254:3189": I.sun,
}
LEFT_CUT = {"2888:612"}    # ракета: срез выхлопа — на левую направляющую 4, низ — на базу
RENAME = {"4254:3193": "Участие",                     # две ладошки — это «Участие»
          "2888:677": "Участие · старый вариант"}

FLOAT = {"2888:570", "2888:612", "2888:620", "2888:660", "2888:665", "2888:673", "2888:677",
         "2891:586", "2891:591", "2892:626", "4254:3019", "4254:3086", "4254:3110", "4254:3189",
         "4254:3193", "4254:3107"}
ROUND = {"2888:620", "2891:586", "4254:3019", "4254:3110", "4254:3189"}
FULL = {"4254:1269": None,                              # Ф1: полосы срезаны рамкой — как построено
        "4254:3034": (TOP, BASE)}                       # Ф2: полосы сверху по направляющей 7, ноги на базе

A_TARGET = 1300.0     # площадь рамки «квадратной» иконки ≈ 36 × 36
F_REF = 0.5           # эталонная плотность заливки

def ink_ratio(p):
    x0, y0, x1, y1 = p.bounds
    svg_ = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1 - x0} {y1 - y0}" width="200" height="{max(1, int(200 * (y1 - y0) / (x1 - x0)))}">'
            f'<path d="{to_d(p)}" fill="#000"/></svg>')
    a = np.array(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg_.encode()))).convert("RGBA"))[..., 3]
    return float((a > 127).mean())

def place(node, p):
    x0, y0, x1, y1 = p.bounds; w, h = x1 - x0, y1 - y0
    if node in FULL:
        if FULL[node] is None: return 1.0, 0.0, 0.0, "как построено"
        t, b = FULL[node]; s = (b - t) / h
        return s, 25 - s * (x0 + x1) / 2, b - s * y1, "по высоте поля"
    if node in LEFT_CUT:
        s = min(39.1 / h, (RIGHT - LEFT) / w)
        return s, LEFT - s * x0, BASE - s * y1, "срез по левой направляющей"
    f = ink_ratio(p)
    area = A_TARGET * (F_REF / f) ** 0.25
    if node in ROUND: area *= 1.10
    s = math.sqrt(area / (w * h))
    hmax = 38.0 if node in ROUND else (39.1 if h / w >= 1.3 and node not in FLOAT else BASE - TOP)
    s = min(s, (RIGHT - LEFT) / w, hmax / h)
    dx = 25 - s * (x0 + x1) / 2
    if node in FLOAT: dy = (TOP + BASE) / 2 - s * (y0 + y1) / 2
    else: dy = BASE - s * y1
    return s, dx, dy, f"плотность {f:.2f}"

VARIANTS = {   # узел → дополнительные варианты для страницы (в пак не идут)
    "4254:1269": [("investments-flat", lambda: I.investments3(theta=0, s=0.649, tip=(46, 23.0), clip=False), "float")],
    "2892:571": [("city-a", lambda: I.city3("A"), None)],
    "2891:591": [("glider-orig", I.glider_original_diag, None)],
    "2888:570": [("logistics-hub", I.logistics_hub, "ground")],
    "2888:639": [("mentors-sparkle", I.mentors_sparkle, None)],
}

def variant_place(node, mode, p):
    if mode == "float":                                     # просто вписать по центру поля
        x0, y0, x1, y1 = p.bounds; w, h = x1 - x0, y1 - y0
        s = min((RIGHT - LEFT) / w, (BASE - TOP) / h)
        return s, 25 - s * (x0 + x1) / 2, (TOP + BASE) / 2 - s * (y0 + y1) / 2
    if mode == "ground": node = "—"                          # обычная «стоящая» посадка на базу
    s, dx, dy, _ = place(node, p); return s, dx, dy

def main():
    out = os.path.join(HERE, "build/pack"); os.makedirs(out, exist_ok=True)
    meta = []
    for node, v in I.SRC.items():
        if node in SKIP: continue
        p = REBUILT[node]() if node in REBUILT else I.src_path(node)
        s, dx, dy, note = place(node, p)
        q = tf(p, (s, 0, 0, s, dx, dy))
        name = RENAME.get(node, v["name"].replace("Иконки/", ""))
        slug = node.replace(":", "-")
        open(os.path.join(out, f"{slug}.svg"), "w").write(svg(q))
        b = q.bounds
        meta.append(dict(node=node, name=name, old=v["name"], rebuilt=node in REBUILT, scale=round(s, 4),
                         dx=round(dx, 3), dy=round(dy, 3), bounds=[round(x, 2) for x in b], note=note,
                         float=node in FLOAT))
        print(f"{name[:34]:36s} s={s:.3f}  x {b[0]:5.2f}…{b[2]:5.2f}  y {b[1]:5.2f}…{b[3]:5.2f}  {note}")
    json.dump(meta, open(os.path.join(HERE, "build/pack.json"), "w"), ensure_ascii=False, indent=1)
    vd = os.path.join(HERE, "build/variants"); os.makedirs(vd, exist_ok=True)
    for node, vs in VARIANTS.items():
        for slug, fn, mode in vs:
            p = fn(); s, dx, dy = variant_place(node, mode, p)
            open(os.path.join(vd, f"{slug}.svg"), "w").write(svg(tf(p, (s, 0, 0, s, dx, dy))))
            print("вариант", slug, round(s, 3))

if __name__ == "__main__":
    main()
