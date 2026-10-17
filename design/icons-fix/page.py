"""Страница согласования правок иконок: было/стало, варианты, разбор пака.
Иконки встраиваются как <symbol> прямо из src/icons_export.json и build/*.svg."""
import json, os, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = json.load(open(os.path.join(HERE, "src/icons_export.json")))

def paths_of(svg):
    """Все path из svg без атрибута fill — цвет задаёт страница (чёрный или градиент)."""
    out = []
    for m in re.finditer(r"<path([^>]*)/>", svg):
        attrs = m.group(1)
        d = re.search(r' d="([^"]+)"', attrs).group(1)
        rule = re.search(r'fill-rule="([^"]+)"', attrs)
        out.append(f'<path d="{d}"' + (f' fill-rule="{rule.group(1)}"' if rule else "") + "/>")
    return "".join(out)

symbols = {}
def sym_src(node, sid): symbols[sid] = paths_of(SRC[node]["svg"]); return sid
def sym_build(name, sid): symbols[sid] = paths_of(open(os.path.join(HERE, f"build/{name}.svg")).read()); return sid

KEYS = ('<g class="keys">'
        '<line x1="4" y1="0" x2="4" y2="50"/><line x1="46" y1="0" x2="46" y2="50"/>'
        '<line x1="0" y1="4" x2="50" y2="4"/><line x1="0" y1="46" x2="50" y2="46"/>'
        '<line class="kb" x1="0" y1="7" x2="50" y2="7"/><line class="kb" x1="0" y1="43.1" x2="50" y2="43.1"/>'
        '<line class="kb" x1="6.95" y1="0" x2="6.95" y2="50"/><line class="kb" x1="43.05" y1="0" x2="43.05" y2="50"/>'
        '<line class="kc" x1="0" y1="12.05" x2="50" y2="12.05"/><line class="kc" x1="0" y1="38.05" x2="50" y2="38.05"/>'
        '<line class="kc" x1="14.5" y1="0" x2="14.5" y2="50"/><line class="kc" x1="35.5" y1="0" x2="35.5" y2="50"/></g>')

def big(sid, label, tag=""):
    t = f'<span class="tag">{tag}</span>' if tag else ""
    sizes = "".join(f'<svg class="ico sm" width="{s}" height="{s}" viewBox="0 0 50 50" aria-hidden="true"><use href="#{sid}"/></svg>'
                    for s in (50, 32, 24))
    return (f'<figure class="tile"><div class="art"><svg class="ico" viewBox="0 0 50 50" role="img" aria-label="{html.escape(label)}">'
            f'<use href="#{sid}"/>{KEYS}</svg></div>'
            f'<figcaption><span class="cap">{label}</span>{t}</figcaption>'
            f'<div class="sizes" aria-label="50, 32 и 24 px">{sizes}</div></figure>')

def thumb(sid, name, keys=False):
    return (f'<figure class="thumb"><svg class="ico" viewBox="0 0 50 50" role="img" aria-label="{html.escape(name)}">'
            f'<use href="#{sid}"/>{KEYS if keys else ""}</svg><figcaption>{name}</figcaption></figure>')

# ── круг 2: правки по замечаниям ─────────────────────────────────────────────
META = {m["node"]: m for m in json.load(open(os.path.join(HERE, "build/pack.json")))}
def sym_pack(node):
    sid = "n-" + node.replace(":", "-")
    if sid not in symbols:
        symbols[sid] = paths_of(open(os.path.join(HERE, f"build/pack/{node.replace(':', '-')}.svg")).read())
    return sid
def sym_before(node):
    sid = "b-" + node.replace(":", "-")
    if sid not in symbols: sym_src(node, sid)
    return sid

def sym_var(slug):
    sid = "v-" + slug
    if sid not in symbols:
        symbols[sid] = paths_of(open(os.path.join(HERE, f"build/variants/{slug}.svg")).read())
    return sid

G = lambda n, lab="": ("pack", n, lab or META[n]["name"].split(" · ")[-1], "")
ICONS4 = [
    dict(slug="grid", node="2888:616", title="Сетка: три класса иконок", nb=True,
         ask="Квадрат — и по горизонтали, и по вертикали; по центру. Прямые края — на голубом, круглые и острые — до красного. У горизонтальных одна высота, у вертикальных одна ширина — новые линии.",
         after=[G("2888:616", "Квадратная"), G("4254:3005", "Горизонтальная"), G("2888:574", "Вертикальная"), G("2888:620", "Круглая")],
         notes=["Все иконки теперь по центру квадрата, а не на базе.",
                "Квадратные (пропорция 0,8–1,18) — большая сторона на голубом квадрате 36,1. Меньшая сторона по центру: растянуть её до квадрата можно только искажением или перерисовкой.",
                "Горизонтальные (шире 1,18) — одна высота 26 между зелёными линиями 12,05 и 38,05: комбайн, трактор, грузовик, поезд, ферма, Колмаков и другие.",
                "Вертикальные (уже 0,8) — одна ширина 21 между зелёными линиями 14,5 и 35,5: колос и «Движение первых».",
                "Круглые формы — до красного (42). Острая или круглая верхушка — вверх до красного, плоский низ на голубой базе."]),
    dict(slug="bld", node="2892:573", title="Здания — рядом", nb=True,
         ask="Музей, храм и другие здания — единый стиль: расположить рядом.",
         after=[G("2892:573", "Музей"), G("2892:580", "Храм"), G("2891:614", "Гостиницы"), G("2891:599", "Санатории"),
                G("2888:578", "Промышленное"), G("2891:608", "Базы отдыха"), G("new:farm", "Ферма"), G("2888:583", "Стройка"),
                G("2892:571", "Комфортный город"), G("2892:612", "Вход в парк")],
         notes=["Задний домик теперь одной формы — как у «Промышленного производства»: скат, свесы со скруглёнными концами, кровля слита со стенами. Так нарисованы амбар фермы, маленький дом стройки, база отдыха и дома «Комфортного города»."]),
    dict(slug="trees", node="2888:587", title="Деревья — рядом", nb=True,
         ask="Деревья в одной стилистике, эталон — «Богатые природные ресурсы»; композиции разные.",
         after=[G("2888:587", "Ресурсы"), G("2888:599", "Общественные"), G("2891:595", "Город парков"), G("2892:607", "Центральный парк"),
                G("4254:3118", "Парк Машиностроителей"), G("2892:571", "Комфортный город"), G("2892:596", "Лес с елями"), G("2891:608", "Базы отдыха")],
         notes=["Лиственное дерево одно на весь пак — из «Ресурсов»: крона-облако, ствол с ветками-прорезями и ромбом. Композиции свои: скамейка, дома, ротонда, холмы, дорожка.",
                "У маленьких деревьев прорези веток расширены, чтобы не исчезали в мелком размере.",
                "Ель одна: «Лес с елями» вернул к исходнику, и та же ель стоит за базой отдыха.",
                "Центральный парк стал горизонтальной иконкой: ротонда и два дерева пака над кровлей."]),
    dict(slug="inv", node="4254:1269", title="Инвестиции · ваш рисунок в векторе",
         ask="Перевести в вектор, сохранив все детали, геометрию чуть поправить — дальше поправите сами.",
         notes=["Контур построен по точкам вашего рисунка: три потока, прорези, сужающиеся до острия, стрелка с вогнутыми «крыльями».",
                "Поправлено: кромки — гладкие кривые без изломов, прорези сужаются ровно, наконечник симметричен (крылья расходились на 12 px), края кадра — прямые срезы.",
                "Отдельные файлы: investments-vector-large.svg (в масштабе рисунка, синий) и investments-vector-50.svg (в кадре 50 × 50)."]),
    dict(slug="city", node="2892:571", title="Комфортный и гостеприимный город · по вашему рисунку",
         ask="Привести к общему виду: дерево как наши, домики и расстояния поправить.",
         notes=["Композиция вашего рисунка: холм, извилистая дорожка к арке, три дома, дерево.",
                "Дерево — дерево пака. Дома — единой формы домика, окна одного размера.",
                "Просветы ровные: дома, земля и дерево разделены одинаковой линией, между домами — чуть шире."]),
    dict(slug="palm", node="4254:3193", title="Участие",
         ask="Первая ладошка залитая, вторая контурная — поменять местами.",
         notes=["Передняя ладонь залита, пальцы разделены просветом 1,3. Задняя — контуром той же толщины, отделена от передней тем же просветом."]),
    dict(slug="tour", node="4254:3107", title="Туризм",
         ask="Фрагменты полос сзади увеличить и обрезать — сейчас слишком мелкие.",
         notes=["Полосы знака увеличены в 1,55 раза от стыка у самолёта и обрезаны прежней рамкой: фрагменты крупнее, линии толще. Самолёт прежний."]),
    dict(slug="tech", node="4254:3023", title="Техника — одна высота", nb=True,
         ask="Комбайн, трактор, грузовик и поезд — горизонтальные, одной высоты.",
         after=[G("4254:3023", "Комбайн"), G("4254:3026", "Трактор"), G("4254:3005", "Грузовик"), G("4254:3003", "Поезд")],
         notes=["Все четыре — в горизонтальном классе: верх и низ на зелёных линиях 12,05 и 38,05."]),
]
ICONS = []
for it in ICONS4 + ICONS:
    it["b"] = None if it.get("nb") else sym_before(it["node"])
    after = it.get("after") or [("pack", it["node"], "Стало", "")]
    it["a"] = [((sym_pack(k) if kind == "pack" else sym_var(k)), lab, tag) for kind, k, lab, tag in after]

_sc = [m["scale"] for m in META.values() if not m["rebuilt"]]
SCALE_LO, SCALE_HI = (f"{min(_sc):.2f}".replace(".", ","), f"{max(_sc):.2f}".replace(".", ","))
SMALL = ["2892:571", "2891:586", "4254:3019", "2891:599", "4254:3193"]
GAPS = json.load(open(os.path.join(HERE, "build/gaps.json")))

PACK = [m for m in META.values()]
for m in PACK:
    if not m.get("new"): sym_before(m["node"])
    sym_pack(m["node"])

def section(it):
    tiles = ("" if it.get("nb") else big(it["b"], "Было")) + "".join(big(sid, lab, tag) for sid, lab, tag in it["a"])
    notes = "".join(f"<li>{n}</li>" for n in it["notes"])
    wide = " wide" if len(it["a"]) > 1 else ""
    return (f'<section class="icon{wide}" id="{it["slug"]}"><header class="ih"><h2>{it["title"]}</h2>'
            f'<p class="ask">{it["ask"]}</p></header>'
            f'<div class="tiles">{tiles}</div><ul class="notes">{notes}</ul></section>')

def small_row(node):
    sid = "n-" + node.replace(":", "-")
    sizes = "".join(f'<svg class="ico" width="{z}" height="{z}" viewBox="0 0 50 50" aria-hidden="true"><use href="#{sid}"/></svg>' for z in (24, 32, 50))
    return f'<figure class="srow"><div class="sz">{sizes}</div><figcaption>{html.escape(META[node]["name"])}</figcaption></figure>'

def rz_cell(m):
    sn = "n-" + m["node"].replace(":", "-")
    return f'<svg class="rz" viewBox="0 0 50 50" role="img" aria-label="{html.escape(m["name"])}"><use href="#{sn}"/></svg>'

def pack_cell(m):
    sb, sn = "b-" + m["node"].replace(":", "-"), "n-" + m["node"].replace(":", "-")
    mark = '<span class="dot" title="перерисована"></span>' if m["rebuilt"] else ""
    was_use = "" if m.get("new") else f'<use href="#{sb}"/>'
    return (f'<figure class="cell"><div class="cv"><svg class="ico was" viewBox="0 0 50 50" aria-hidden="true">{was_use}{KEYS}</svg>'
            f'<svg class="ico now" viewBox="0 0 50 50" role="img" aria-label="{html.escape(m["name"])}"><use href="#{sn}"/>{KEYS}</svg></div>'
            f'<figcaption>{mark}{html.escape(m["name"])}</figcaption></figure>')

defs = "".join(f'<symbol id="{k}" viewBox="0 0 50 50">{v}</symbol>' for k, v in symbols.items())
grads = ("".join(
    f'<linearGradient id="g{n}" x1="4" y1="46" x2="46" y2="4" gradientUnits="userSpaceOnUse">'
    f'<stop stop-color="{a}"/><stop offset=".35" stop-color="{b}"/><stop offset=".7" stop-color="{c}"/></linearGradient>'
    for n, (a, b, c) in (("Blue", ("#003DA5", "#2CD5C4", "#00A9E0")),
                         ("Green", ("#00843D", "#47D7AC", "#DDF314")),
                         ("Red", ("#E4002B", "#FFC851", "#FF6900")))))

TOC = "".join(f'<a href="#{it["slug"]}">{it["title"]}</a>' for it in ICONS4) + " · " + "".join(f'<a href="#{it["slug"]}">{it["title"].replace("Ф1 · ", "").replace("Ф3 · ", "").replace("Ф2 · ", "")}</a>' for it in ICONS)

PAGE = f"""<title>Правки иконок Заводоуковска</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;500;600&family=Unbounded:wght@500;700&family=JetBrains+Mono:wght@400&display=swap">
<style>
/* Лист согласования: колонка 1120 px; на каждую иконку «было» слева, «стало» справа, под ними размеры и список правок */
:root {{
  --bg: #F2F4F7; --surface: #FFFFFF; --ink: #0F1724; --muted: #5B6575; --line: #DCE1E8;
  --accent: #003DA5; --accent-soft: #E3ECF8; --tile: #FFFFFF; --glyph: #0E0E0E;
  --key-a: #FF2E88; --key-b: #1E9BFF;
  --f-display: "Unbounded", "Golos Text", system-ui, sans-serif;
  --f-body: "Golos Text", system-ui, -apple-system, "Segoe UI", sans-serif;
  --f-mono: "JetBrains Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #0C121C; --surface: #141C29; --ink: #E8EDF4; --muted: #97A3B6; --line: #253043;
  --accent: #6FC3FF; --accent-soft: #17304D; --tile: #FFFFFF; --glyph: #0E0E0E; color-scheme: dark }} }}
:root[data-theme="dark"] {{
  --bg: #0C121C; --surface: #141C29; --ink: #E8EDF4; --muted: #97A3B6; --line: #253043;
  --accent: #6FC3FF; --accent-soft: #17304D; --tile: #FFFFFF; --glyph: #0E0E0E; color-scheme: dark }}
* {{ box-sizing: border-box }}
body {{ background: var(--bg); color: var(--ink); font: 400 15px/1.55 var(--f-body);
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 32px 64px }}
.wrap {{ max-width: 1120px; margin: 0 auto; display: grid; gap: 28px }}
h1, h2, h3 {{ font-family: var(--f-display); font-weight: 700; text-wrap: balance; margin: 0; letter-spacing: -0.01em }}
h1 {{ font-size: clamp(26px, 4.4vw, 40px); line-height: 1.1 }}
h2 {{ font-size: 19px; line-height: 1.25 }}
h3 {{ font-size: 15px; line-height: 1.3 }}
p {{ margin: 0 }}
.eyebrow {{ font: 500 12px/1.2 var(--f-mono); letter-spacing: .06em; text-transform: uppercase; color: var(--muted) }}
.intro {{ display: grid; gap: 12px; max-width: 70ch }}
.intro p {{ color: var(--muted) }}
.bar {{ position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5; background: var(--bg);
  display: flex; flex-wrap: wrap; align-items: center; gap: 10px 18px; padding-block: 10px; border-bottom: 1px solid var(--line) }}
body::before {{ content: ""; position: fixed; inset: 0 0 auto; height: env(safe-area-inset-top, 0px); z-index: 10; background: var(--bg) }}
.seg {{ display: inline-flex; border: 1px solid var(--line); border-radius: 999px; padding: 3px; background: var(--surface) }}
.seg button, .chk {{ font: 500 13px/1 var(--f-body); color: var(--ink); background: none; border: 0; border-radius: 999px; padding: 8px 12px; cursor: pointer }}
.seg button[aria-pressed="true"] {{ background: var(--ink); color: var(--bg) }}
.seg button:focus-visible, .chk:focus-visible, .toc a:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px }}
.chk {{ border: 1px solid var(--line); background: var(--surface); display: inline-flex; gap: 8px; align-items: center }}
.chk[aria-pressed="true"] {{ border-color: var(--accent); color: var(--accent) }}
.legend {{ font: 400 12px/1.4 var(--f-mono); color: var(--muted); display: flex; gap: 14px; flex-wrap: wrap }}
.legend i {{ display: inline-block; width: 14px; height: 2px; vertical-align: middle; margin-right: 6px }}
.toc {{ display: flex; flex-wrap: wrap; gap: 6px 14px; font-size: 13px }}
.toc a {{ color: var(--accent); text-decoration: none; border-bottom: 1px solid transparent }}
.toc a:hover {{ border-bottom-color: currentColor }}
section.icon {{ background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 22px;
  display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 300px); grid-template-areas: "h h" "t n"; gap: 18px 28px }}
section.icon.wide {{ grid-template-columns: minmax(0, 1fr); grid-template-areas: "h" "t" "n" }}
.ih {{ grid-area: h; display: grid; gap: 4px }}
.ask {{ color: var(--muted) }}
.tiles {{ grid-area: t; display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 16px; align-content: start }}
.notes {{ grid-area: n; margin: 0; padding-left: 18px; display: grid; gap: 8px; align-content: start; font-size: 14px }}
.notes li::marker {{ color: var(--accent) }}
.tile {{ margin: 0; display: grid; gap: 8px; min-width: 0; max-width: 340px }}
.art {{ background: var(--tile); border: 1px solid var(--line); border-radius: 4px; aspect-ratio: 1; max-width: 100% }}
.art svg {{ width: 100%; height: 100%; display: block }}
.tile figcaption {{ display: flex; gap: 6px 8px; align-items: flex-start; flex-wrap: wrap; font-size: 13px; font-weight: 500; min-height: 44px }}
.tag {{ font: 500 11px/1 var(--f-mono); letter-spacing: .04em; text-transform: uppercase; color: var(--accent); background: var(--accent-soft); padding: 4px 6px; border-radius: 3px }}
.sizes {{ display: flex; align-items: flex-end; gap: 10px; background: var(--tile); border: 1px solid var(--line); border-radius: 4px; padding: 8px 10px }}
.ico {{ fill: var(--glyph); overflow: visible }}
.keys line {{ stroke: var(--key-a); stroke-width: 1px; vector-effect: non-scaling-stroke; opacity: .7 }}
.keys line.kb {{ stroke: var(--key-b) }}
.keys line.kc {{ stroke: #12A150; stroke-dasharray: 3 3; opacity: .85 }}
.nokeys .keys {{ display: none }}
.thumbs .keys line {{ opacity: .9 }}
[data-ink="blue"] .ico {{ fill: url(#gBlue) }}
[data-ink="green"] .ico {{ fill: url(#gGreen) }}
[data-ink="red"] .ico {{ fill: url(#gRed) }}
.review {{ display: grid; gap: 14px }}
.review > header {{ display: grid; gap: 6px; max-width: 70ch }}
.review > header p {{ color: var(--muted) }}
.rv-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 14px; align-items: start }}
.rv {{ background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 18px; display: grid; gap: 10px; align-content: start; min-width: 0 }}
.rv p {{ font-size: 14px; color: var(--ink) }}
.thumbs {{ display: flex; flex-wrap: wrap; gap: 10px }}
.thumb {{ margin: 0; display: grid; gap: 4px; width: 84px }}
.thumb svg {{ width: 84px; height: 84px; background: var(--tile); border: 1px solid var(--line); border-radius: 4px; display: block }}
.thumb figcaption {{ font-size: 11px; line-height: 1.25; color: var(--muted) }}
.rules {{ margin: 4px 0 6px; padding-left: 18px; display: grid; gap: 6px; font-size: 14px; max-width: 80ch }}
.rules li::marker {{ color: var(--accent) }}
.cmp {{ width: 100%; border-collapse: collapse; font-size: 14px; margin: 4px 0 8px }}
.cmp th, .cmp td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); vertical-align: top }}
.cmp th {{ font-weight: 600; color: var(--muted); font-size: 12.5px }}
.cmp td.n {{ font-variant-numeric: tabular-nums; white-space: nowrap }}
.tw {{ overflow-x: auto }}
.ryz {{ background: #F6F4F1; border-radius: 16px; padding: 28px 20px; display: grid; grid-template-columns: repeat(7, 1fr); gap: 26px 10px; justify-items: center }}
.rz {{ width: 100%; max-width: 76px; aspect-ratio: 1; fill: #3A3A3A }}
@media (max-width: 640px) {{ .ryz {{ grid-template-columns: repeat(5, 1fr); padding: 18px 10px; gap: 16px 6px }} }}
.two {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px }}
@media (max-width: 760px) {{ .two {{ grid-template-columns: 1fr }} }}
.two h4 {{ font: 600 14px/1.3 var(--f-body); margin: 0 0 6px }}
.pack {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(112px, 1fr)); gap: 12px }}
.cell {{ margin: 0; display: grid; gap: 6px; min-width: 0; align-content: start }}
.cv {{ background: var(--tile); border: 1px solid var(--line); border-radius: 4px; width: 100% }}
.cv svg {{ width: 100%; height: auto; aspect-ratio: 1; display: block }}
.review > header .seg {{ justify-self: start }}
.pack[data-ver="now"] .was, .pack[data-ver="was"] .now {{ display: none }}
.cell figcaption {{ font-size: 11.5px; line-height: 1.3; color: var(--muted); display: flex; gap: 6px; align-items: baseline }}
.dot {{ flex: none; width: 7px; height: 7px; border-radius: 50%; background: var(--accent); transform: translateY(-1px) }}
.srow {{ margin: 0; display: grid; gap: 4px; justify-items: start }}
.sz {{ display: flex; align-items: flex-end; gap: 10px; background: var(--tile); border: 1px solid var(--line); border-radius: 4px; padding: 8px 10px }}
.srow figcaption {{ font-size: 11.5px; color: var(--muted); max-width: 150px }}
.grp {{ font-size: 15px; letter-spacing: .02em; color: var(--muted); padding-top: 8px }}
.next {{ background: var(--accent-soft); border-radius: 6px; padding: 18px 20px; display: grid; gap: 6px; max-width: 80ch }}
.num {{ font-family: var(--f-mono); font-variant-numeric: tabular-nums }}
@media (max-width: 760px) {{
  section.icon {{ grid-template-columns: minmax(0, 1fr); grid-template-areas: "h" "t" "n"; padding: 16px }}
  .tiles {{ grid-template-columns: repeat(2, minmax(0, 1fr)) }}
  .rv-grid {{ grid-template-columns: minmax(0, 1fr) }}
}}
@media (prefers-reduced-motion: no-preference) {{ .seg button, .chk {{ transition: background .15s, color .15s }} }}
</style>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>{grads}{defs}</defs></svg>
<div class="wrap" id="root">
  <header class="intro">
    <span class="eyebrow">Черновик · Иконки · круг 9</span>
    <h1>Правки иконок</h1>
    <p>Девятый круг. Иконки в итоговом размере и положении в кадре, под каждой реальные размеры 50, 32 и 24 px. Включите «Сетку», чтобы видеть линии.</p>
    <p>Главное: сетка из трёх классов с новыми зелёными линиями, одна форма дерева, ели и домика на весь пак, здания и деревья выложены рядом.</p>
  </header>
  <div class="bar" role="toolbar" aria-label="Вид иконок">
    <div class="seg" role="group" aria-label="Цвет">
      <button type="button" id="ink-black" data-ink="black" aria-pressed="true">Чёрный</button>
      <button type="button" id="ink-blue" data-ink="blue" aria-pressed="false">Синий</button>
      <button type="button" id="ink-green" data-ink="green" aria-pressed="false">Зелёный</button>
      <button type="button" id="ink-red" data-ink="red" aria-pressed="false">Красный</button>
    </div>
    <button type="button" class="chk" id="keys" aria-pressed="true">Сетка</button>
    <span class="legend"><span><i style="background:var(--key-b)"></i>квадрат 36,1 — прямые края</span><span><i style="background:var(--key-a)"></i>4 и 46 — круглые и острые</span><span><i style="background:#12A150"></i>общая высота горизонтальных и ширина вертикальных</span></span>
  </div>
  <nav class="toc" aria-label="Иконки"><a href="#ryazan">Сравнение с Рязанью</a>{TOC}<a href="#pack">Весь пак</a><a href="#gaps">Уровни просветов</a><a href="#small">Мелкий размер</a><a href="#ask">Что уточнить</a></nav>
  <section class="review" id="ryazan">
    <header><h2>Сравнение с Рязанью</h2>
      <p>Я измерил референс Рязани и наш пак одними и теми же мерками: размер рамки, «масса» заливки, толщина вырезов.</p></header>
    <div class="tw"><table class="cmp">
      <tr><th></th><th>Рязань</th><th>Наш пак, круг 7</th><th>Круг 8 · единый квадрат</th><th>Круг 9 · три класса</th></tr>
      <tr><td>Разброс большей стороны рамки</td><td class="n">4%</td><td class="n">5% (широкие до 42)</td><td class="n">6% (специально ±7%)</td><td class="n">7%</td></tr>
      <tr><td>Разброс «массы» — насколько иконки рядом весят по-разному</td><td class="n">9%</td><td class="n">15%</td><td class="n">11%</td><td class="n">18%</td></tr>
      <tr><td>Плотность заливки</td><td class="n">0,40–0,66</td><td class="n">0,27–0,79</td><td class="n">0,27–0,81</td><td class="n">0,27–0,81</td></tr>
      <tr><td>Толщина вырезов к размеру иконки</td><td class="n">≈ 6%</td><td class="n">≈ 3,3%</td><td class="n">≈ 3,4%</td><td class="n">≈ 3,5%</td></tr>
    </table></div>
    <div class="two">
      <div><h4>Где мы пока слабее</h4><ul class="rules">
        <li><b>Сцены вместо предмета.</b> У Рязани — один предмет или пара (маски, грибы, два дерева). У нас часто сцена: здание с ёлками, кран с домами, дерево с полями, скамейка с деревом. Рамка широкая, а заливки мало.</li>
        <li><b>Разная плотность.</b> Рядом стоят почти контурные (бегун, туризм, силовой спорт, «Движение первых») и почти сплошные (элеватор, портфель, пряник). У Рязани все силуэты сплошные с несколькими вырезами.</li>
        <li><b>Тонкие вырезы, и они разные.</b> У Рязани вырез один, жирный (около 6% размера). У нас 0,7–2,0, в среднем вдвое тоньше: детали мельчат и сливаются на 24 px.</li>
        <li><b>Много мелких деталей.</b> У Рязани 2–3 окна и дверь; у нас по 6 окон, лепнина, узоры пряника, жатка.</li>
        <li><b>Разные «семьи».</b> Деревья нарисованы четырьмя способами, люди — с крупными головами и в разных манерах, здания — с разными окнами, карнизами и цоколями.</li>
        <li><b>Ровное и круглое без правила.</b> У Рязани архитектура — прямые углы и острые купола, живое — круглое (кроны, маски, капля), и это держится везде.</li>
      </ul></div>
      <div><h4>Что можно сделать</h4><ul class="rules">
        <li><b>Сетка из трёх классов</b> — сделана в круге 9. Линии строже, но горизонтальные стали легче (разброс «массы» 18%). Дальше: уплотнить их или поднять общую высоту с 26 до 28.</li>
        <li><b>Один вырез на весь пак</b> — 2,0 (около 5,5% размера) вместо 0,7–2,0; узкий 1,3 оставить только для мелочей. Это самое заметное приближение к Рязани.</li>
        <li><b>Один предмет — одна иконка.</b> Убрать второстепенное из сцен, как с санаторием: ёлки, землю, скамейки — или сделать их частью силуэта.</li>
        <li><b>Плотность 0,4–0,65 для всех.</b> Лёгкие (бегун, туризм, «Движение первых», силовой спорт) — толще; тяжёлые (элеватор, портфель, пряник) — с вырезами.</li>
        <li><b>Наборы-конструкторы.</b> Одно дерево (облако или ель), один человечек с небольшой головой, одни окна, двери и карнизы для всех зданий.</li>
        <li><b>Приёмы Рязани:</b> блик-полумесяц на воде и стекле (термальные источники, лампочка), прямая архитектура и круглое живое, вырез как граница двух планов.</li>
      </ul></div>
    </div>
    <h4 style="font:600 14px/1.3 var(--f-body);margin:8px 0 10px">Наш пак в раскладке референса — без сетки, как рядом с баблами</h4>
    <div class="ryz">{"".join(rz_cell(m) for m in PACK)}</div>
  </section>
  {"".join(section(it) for it in ICONS4)}
  <section class="review" id="pack">
    <header><h2>Весь пак: сетка и объём</h2>
      <p>Все {len(PACK)} иконок в кадрах 50 × 50. Переключите «Было» и «Стало», чтобы увидеть, как они встали. Точкой отмечены перерисованные.</p>
      <ul class="rules">
        <li>Все стоящие иконки встали на одну базу 43,1. Раньше было две базы, 43,1 и 43,9, а «Личный рост» и старое «Участие» опускались до 45.</li>
        <li>Парящие формы отцентрованы по высоте поля 7–43,1: сердце, солнце, мяч, компас, стрелки, самолёт, змей, ракета, ладони.</li>
        <li>По горизонтали каждая иконка стоит по центру кадра.</li>
        <li>Три класса по центру квадрата: квадратные — большая сторона на голубом 36,1; горизонтальные — одна высота 26 (зелёные 12,05–38,05); вертикальные — одна ширина 21 (зелёные 14,5–35,5).</li>
        <li>Прямые края — на голубом, круглые и острые — до красного: круги в 42, острая верхушка вверх до 4 при плоском низе на базе.</li>
        <li>Нетронутые иконки только масштабировались, от {SCALE_LO} до {SCALE_HI}, без искажения пропорций.</li>
      </ul>
      <div class="seg" role="group" aria-label="Версия пака">
        <button type="button" id="pack-was" data-ver="was" aria-pressed="false">Было</button>
        <button type="button" id="pack-now" data-ver="now" aria-pressed="true">Стало</button>
      </div>
    </header>
    <div class="pack" id="packgrid" data-ver="now">{"".join(pack_cell(m) for m in PACK)}</div>
  </section>
  <section class="rv" id="gaps"><h3>Уровни просветов — предложение</h3>
    <p>Сейчас в паке около десяти разных толщин вырезов и просветов: 0,5, 0,7, 0,9, 1,0, 1,25, 1,45, 1,75, 2,0, 2,25, 2,75. Предлагаю четыре уровня (в кадре 50 × 50):</p>
    <ul class="rules">
      <li><b>0,7 — тонкие детали:</b> переплёты окон, прорези веток, швы.</li>
      <li><b>1,0 — внутренние вырезы:</b> окна, двери, линии на предметах.</li>
      <li><b>1,4 — просвет между предметами и частями:</b> дом и земля, колесо и корпус, деревья и здания.</li>
      <li><b>2,0 — крупные линии-вырезы:</b> мяч, портфель, сообщества, колонны.</li>
    </ul>
    <p>Иконки, где сейчас есть толщины вне этих уровней (по замеру): {", ".join(html.escape(r["name"].split(" · ")[-1]) for r in GAPS if r["off"])}. Почти во всех остальных смешаны три-четыре разные толщины. Когда утвердите уровни, пройду весь пак и подгоню каждую иконку.</p>
  </section>
  <section class="rv" id="small"><h3>Проверка в мелком размере</h3>
    <p>Я посмотрел весь пак на 24 и 32 px. Почти всё читается. Хуже всего на 24 px мелкие детали сливаются у этих иконок. Детали вам нужны, поэтому я их не трогал. Если понадобится, для мелких плашек можно сделать упрощённые версии.</p>
    <div class="thumbs">{"".join(small_row(n) for n in SMALL)}</div>
  </section>
  <section class="rv" id="ask"><h3>Что уточнить</h3>
    <ul class="rules">
      <li>Уровни просветов 0,7 / 1,0 / 1,4 / 2,0 — подходят? После этого пройду весь пак.</li>
      <li>Общая высота горизонтальных — 26. Поднять до 28, чтобы они не казались легче квадратных? Тогда грузовик и Парк Машиностроителей станут чуть ниже остальных.</li>
      <li>Пример с документом (file): для какой нашей иконки он? Похожей в паке не нашёл.</li>
      <li>Когда всё устроит, переношу пак в Фигму.</li>
    </ul>
  </section>
  <aside class="next"><h3>Что дальше</h3>
    <p>Если всё устраивает, перенесу пак в Фигму: перерисованные иконки заменю новыми векторами, остальным выставлю тот же масштаб и положение в кадре. Компоненты останутся теми же, поэтому иконки на слайдах обновятся сами.</p></aside>
</div>
<script>
(function () {{
  var root = document.getElementById('root');
  var inks = document.querySelectorAll('[data-ink]');
  inks.forEach(function (b) {{
    if (!b.matches('button')) return;
    b.addEventListener('click', function () {{
      root.setAttribute('data-ink', b.getAttribute('data-ink'));
      inks.forEach(function (x) {{ if (x.matches('button')) x.setAttribute('aria-pressed', String(x === b)); }});
    }});
  }});
  var grid = document.getElementById('packgrid');
  document.querySelectorAll('[data-ver]').forEach(function (b) {{
    if (!b.matches('button')) return;
    b.addEventListener('click', function () {{
      grid.setAttribute('data-ver', b.getAttribute('data-ver'));
      document.querySelectorAll('button[data-ver]').forEach(function (x) {{ x.setAttribute('aria-pressed', String(x === b)); }});
    }});
  }});
  var k = document.getElementById('keys');
  k.addEventListener('click', function () {{
    var on = k.getAttribute('aria-pressed') !== 'true';
    k.setAttribute('aria-pressed', String(on));
    root.classList.toggle('nokeys', !on);
  }});
}})();
</script>
"""

if __name__ == "__main__":
    out = os.path.join(HERE, "review.html")
    open(out, "w").write(PAGE)
    print(out, len(PAGE) // 1024, "KB,", len(symbols), "symbols")
