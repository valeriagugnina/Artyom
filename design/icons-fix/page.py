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
        '<line class="kc" x1="0" y1="11.55" x2="50" y2="11.55"/><line class="kc" x1="0" y1="38.55" x2="50" y2="38.55"/>'
        '<line class="kc" x1="14.5" y1="0" x2="14.5" y2="50"/><line class="kc" x1="35.5" y1="0" x2="35.5" y2="50"/>'
        '<line class="km" x1="0" y1="8.55" x2="50" y2="8.55"/><line class="km" x1="0" y1="41.55" x2="50" y2="41.55"/>'
        '<line class="km" x1="8.5" y1="0" x2="8.5" y2="50"/><line class="km" x1="41.5" y1="0" x2="41.5" y2="50"/></g>')

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

def sym_r10(node):
    """Иконка такой, какой была в круге 10 (сборка из git, build/r10)."""
    sid = "r-" + node.replace(":", "-")
    if sid not in symbols:
        symbols[sid] = paths_of(open(os.path.join(HERE, f"build/r10/{node.replace(':', '-')}.svg")).read())
    return sid

def sym_var(slug):
    sid = "v-" + slug
    if sid not in symbols:
        symbols[sid] = paths_of(open(os.path.join(HERE, f"build/variants/{slug}.svg")).read())
    return sid

G = lambda n, lab="": ("pack", n, lab or META[n]["name"].split(" · ")[-1], "")
R = lambda n, lab="": ("r10", n, lab or META[n]["name"].split(" · ")[-1], "круг 10")
ICONS4 = [
    dict(slug="palm", node="4254:3193", title="Участие",
         ask="Убрать торчащий кусочек пальца у задней руки; контур задней руки сделать чистым и красивым.",
         notes=["Обрывок мизинца задней ладони слева убран — от задней руки остаётся один цельный контур.",
                "Задняя ладонь теперь отрезается не по каждому пальцу передней, а по её общему силуэту: щели между передними пальцами закрыты, поэтому контур идёт целыми дугами, без зубчиков и клинышков.",
                "Ладони стали меньше: они в сетке массивных форм (33, оранжевые линии)."]),
    dict(slug="alley", node="4254:3118", title="Парк Машиностроителей",
         ask="Квадраты у деревьев внизу; аллею вернуть ровно как была; иконка маленькая, теряется.",
         notes=["Холмы, аллея и ступени — исходные, точка в точку (на макете совпадают с исходником полностью). Снято только то, что было выше склона: старые кроны и стволы.",
                "Под старым стволом склон продолжен той же плавной линией, а новый ствол уходит в холм — поэтому у основания нет ни ступенек, ни квадратиков.",
                "Иконка крупнее: она в классе пейзажей — по ширине до красных линий 4–46."]),
    dict(slug="firs", node="2892:596", title="Лес с елями",
         ask="У задних елей артефакты. Задние объединить условно квадратом, переднюю — с обводкой; вторые ярусы задних аккуратно уходят под переднюю.",
         notes=["Задние ели объединены прямоугольником за передней: от низа второго яруса и ниже между ними сплошной фон.",
                "Передняя ель видна целиком и обведена ровным просветом; вторые ярусы задних уходят под неё, мелких обрывков ярусов больше нет.",
                "Задние ели чуть ближе к центру (на 1), чтобы второй ярус заходил под переднюю."]),
    dict(slug="tour", node="4254:3107", title="Туризм",
         ask="Ровно обрезать края воздушных полос; ровное крыло самолёта; иконка воздушная — самолёт чуть крупнее по вертикали.",
         notes=["Все полосы обрезаны одной вертикалью перед хвостом самолёта.",
                "Крылья и стабилизатор ровные: передняя и задняя кромки параллельны, законцовки параллельны фюзеляжу.",
                "Размах крыльев 21 вместо 17, фюзеляж длиннее на 1 — самолёт крупнее по вертикали."]),
    dict(slug="tech", node="4254:3005", title="Транспорт — одна высота", nb=True,
         ask="Все одной высоты; трактор и поезд по ширине голубых линий, грузовик и комбайн — по красным; у комбайна увеличить середину.",
         after=[G("4254:3003", "Поезд"), G("4254:3026", "Трактор"), G("4254:3005", "Грузовик"), G("4254:3023", "Комбайн")],
         notes=["Все четыре — высотой 27, ровно между зелёными линиями 11,55 и 38,55.",
                "Поезд и трактор — по ширине голубого квадрата 6,95–43,05; грузовик и комбайн — по красным линиям 4–46.",
                "Чтобы пропорции сошлись без искажения, иконки удлинены вставкой посередине, колёса и кабины не тронуты: у трактора длиннее капот, у грузовика — кузов, у комбайна — корпус с бункером между колёсами. Поезд по пропорциям подошёл сам."]),
    dict(slug="farm", node="new:farm", title="Ферма", nb=True,
         ask="Амбар чуть шире.",
         after=[R("new:farm", "Ферма"), G("new:farm", "Ферма"), G("2888:587", "Ресурсы — пара")],
         notes=["Стены амбара 26 вместо 20, дверь пропорционально шире. Поля прежние, ферма стоит в кадре ровно как «Ресурсы»."]),
    dict(slug="bld", node="2892:573", title="Здания — в ряд", nb=True,
         ask="Храм не выровнен с музеем, гостиница и санаторий тоже — выровнять здания.",
         after=[G("2892:573", "Музей"), G("2892:580", "Храм"), G("2891:614", "Гостиницы"), G("2891:599", "Санатории"),
                G("4254:3021", "Элеватор"), G("2892:612", "Вход в парк"), G("2888:578", "Промышленное"), G("2891:608", "Базы отдыха"), G("2888:583", "Стройка")],
         notes=["Раньше здания стояли по центру квадрата, поэтому низ у всех был на разной высоте. Теперь у зданий своё правило — как ряд домов на одной улице.",
                "Все стоят на одной земле — оранжевой линии 41,55.",
                "Плоский верх (музей, элеватор, вход в парк) — ровно на оранжевой 8,55: высота 33.",
                "Фронтон, купола, кровля, кран (храм, гостиница, санаторий, база, стройка) — до голубой 7: высота 34,55.",
                "У склада свесы кровли и у базы ель выходят до красных линий."]),
    dict(slug="hotel", node="2891:614", title="Гостиницы", rb=True,
         ask="Убрать нижний постамент; поправить угол стыка крыши со стенами.",
         notes=["Низ — одна ровная линия: у двери были выступы-ступеньки, их больше нет.",
                "Крыша отделена от стен сплошным просветом, он проходит насквозь до краёв; торцы кровли срезаны вертикально по стенам. Раньше в углах крыша держалась на волоске.",
                "Межэтажная линия тоже больше не доходит до края волоском — заканчивается за 1,3 от стены."]),
    dict(slug="green", node="2891:595", title="Город парков", rb=True,
         ask="Дерево криво обрезано.",
         notes=["Крона срезана одной ровной горизонталью над домами (на просвет от самого высокого дома), слева и справа одинаково. Ствол идёт вниз между домами до земли."]),
    dict(slug="city", node="2892:571", title="Комфортный и гостеприимный город", rb=True,
         ask="Дом с аркой поехал — перерисовать аккуратно; дерево — со стволом.",
         notes=["Земля с ровным верхом: все дома стоят на одной горизонтали, дом с аркой больше не перекошен.",
                "Главный дом сдвинут вправо — между ним и левым домиком виден ствол дерева.",
                "Дорожка заново: гладкая линия из арки вниз, плавно расширяется к краю, без зазубрин."]),
    dict(slug="inv", node="4254:1269", title="Инвестиции", rb=True,
         ask="Просто нарисовать вектор поверх рисунка.",
         notes=["Достал ваш рисунок из переписки и обвёл автоматически (potrace) — вектор один в один, расхождение с рисунком 0,19% площади.",
                "Правка только у рамки: левый и нижний срезы выпрямлены."]),
    dict(slug="sizes", node="2888:643", title="Размеры: ладони, парки, пряник", nb=True,
         ask="Ладони крупные — меньше; центральный парк маленький — крупнее и проще; общественные пространства маленькие; пряник по горизонтали — по максимуму.",
         after=[G("2888:643", "Поддержка инициатив"), G("4254:3105", "Взаимопомощь"), G("2888:669", "Волонтёры"), G("4254:3193", "Участие"),
                G("2892:607", "Центральный парк"), G("2888:599", "Общественные пространства"), G("2891:586", "Пряник Колмакова"), G("2888:616", "Карьера")],
         notes=["Ладони — в сетке массивных форм 33 (оранжевые линии), стали меньше на 8–9%. «Взаимопомощь» стоит ровно как «Поддержка инициатив»: ладонь одна и та же.",
                "Центральный парк проще: у ротонды три одинаковых столба, тонких «стволов-столбов» больше нет; деревья крупнее (крона 18), стоят за кровлей.",
                "Парки и аллея — класс пейзажей: по ширине до красных 4–46 или по высоте до оранжевых, смотря что раньше. Центральный парк, общественные пространства и Парк Машиностроителей заметно крупнее.",
                "Пряник Колмакова — по ширине до красных линий 4–46, максимально широкий.",
                "Портфель (плотный прямоугольник) перевёл в массивные формы 33 — он был самым тяжёлым рядом с соседями.",
                "Круглые массивные (мяч, солнце, ориентир, второй пряник) теперь ровно по оранжевым линиям, без выхода за них на 4%, — на 4% меньше."]),
    dict(slug="gone", node="2888:660", title="Убраны из пака", nb=True,
         ask="Мегафон и монетки сюда не подходят — убрать из пака.",
         after=[R("2888:660", "Городские сообщества · мегафон"), R("4254:1272", "Капитал · монеты")],
         notes=["Обе иконки убраны из пака: в листе и в переносе в Фигму их больше нет. Компоненты в Фигме я не трогаю — удалить их или оставить в архиве, решите при переносе."]),
]
ICONS = []
for it in ICONS4 + ICONS:
    it["b"] = None if it.get("nb") else sym_r10(it["node"])
    after = it.get("after") or [("pack", it["node"], "Стало", "")]
    it["a"] = [({"pack": sym_pack, "r10": sym_r10}.get(kind, sym_var)(k), lab, tag) for kind, k, lab, tag in after]

_sc = [m["scale"] for m in META.values() if not m["rebuilt"]]
SCALE_LO, SCALE_HI = (f"{min(_sc):.2f}".replace(".", ","), f"{max(_sc):.2f}".replace(".", ","))
SMALL = ["2892:571", "2891:586", "4254:3019", "2891:599", "4254:3193"]
_names = {m["name"] for m in META.values()}
GAPS = [r for r in json.load(open(os.path.join(HERE, "build/gaps.json"))) if r["name"] in _names]

PACK = [m for m in META.values()]
for m in PACK:
    if not m.get("new"): sym_before(m["node"])
    sym_pack(m["node"])

def _line(a, b):
    if a and b: return f"{a.split(' ')[0]} {a.split(' ')[1]} — {b.split(' ')[1]}" if a.split(' ')[0] == b.split(' ')[0] else f"{a} — {b}"
    if a or b: return f"{a or 'центр'} — {b or 'центр'}"
    return "по центру"
CHECK_OK = sum(1 for m in PACK if m["grid"]["ok"])
CHECK_ROWS = "".join(
    f'<tr><td>{html.escape(m["name"])}</td><td>{html.escape(m["note"])}</td>'
    f'<td class="n">{_line(m["grid"]["left"], m["grid"]["right"])}</td><td class="n">{_line(m["grid"]["top"], m["grid"]["bottom"])}</td></tr>'
    for m in PACK)

def section(it):
    tiles = ("" if it.get("nb") else big(it["b"], "Было", "круг 10")) + "".join(big(sid, lab, tag) for sid, lab, tag in it["a"])
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
.keys line.km {{ stroke: #F08A00; stroke-dasharray: 1 3; opacity: .9 }}
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
    <span class="eyebrow">Черновик · Иконки · круг 11</span>
    <h1>Правки иконок</h1>
    <p>Одиннадцатый круг. Слева в каждой карточке — как было в круге 10, справа — как стало, в итоговом размере и положении в кадре. Под каждой иконкой реальные размеры 50, 32 и 24 px. «Сетка» включает все линии.</p>
    <p>Главное: каждая иконка теперь действительно стоит краями на линиях своего класса — это проверяется автоматически, таблица в разделе «Весь пак». Мегафон и монетки убраны. Толщины вырезов — в самом конце, когда утвердите формы и размеры.</p>
  </header>
  <div class="bar" role="toolbar" aria-label="Вид иконок">
    <div class="seg" role="group" aria-label="Цвет">
      <button type="button" id="ink-black" data-ink="black" aria-pressed="true">Чёрный</button>
      <button type="button" id="ink-blue" data-ink="blue" aria-pressed="false">Синий</button>
      <button type="button" id="ink-green" data-ink="green" aria-pressed="false">Зелёный</button>
      <button type="button" id="ink-red" data-ink="red" aria-pressed="false">Красный</button>
    </div>
    <button type="button" class="chk" id="keys" aria-pressed="true">Сетка</button>
    <span class="legend"><span><i style="background:var(--key-b)"></i>квадрат 36,1 — прямые края</span><span><i style="background:var(--key-a)"></i>4 и 46 — круглые и острые</span><span><i style="background:#12A150"></i>горизонтальные и транспорт · вертикальные</span><span><i style="background:#F08A00"></i>массивные формы и здания</span></span>
  </div>
  <nav class="toc" aria-label="Иконки"><a href="#ryazan">Сравнение с Рязанью</a>{TOC}<a href="#pack">Весь пак</a><a href="#check">Проверка сетки</a><a href="#plan">План</a><a href="#gaps">Уровни просветов</a><a href="#small">Мелкий размер</a><a href="#ask">Что уточнить</a></nav>
  <section class="review" id="ryazan">
    <header><h2>Сравнение с Рязанью</h2>
      <p>Я измерил референс Рязани и наш пак одними и теми же мерками: размер рамки, «масса» заливки, толщина вырезов.</p></header>
    <div class="tw"><table class="cmp">
      <tr><th></th><th>Рязань</th><th>Наш пак, круг 7</th><th>Круг 8 · единый квадрат</th><th>Круг 9 · три класса</th><th>Круг 11 · классы и ряды</th></tr>
      <tr><td>Разброс большей стороны рамки</td><td class="n">4%</td><td class="n">5% (широкие до 42)</td><td class="n">6% (специально ±7%)</td><td class="n">7%</td><td class="n">7%</td></tr>
      <tr><td>Разброс «массы» — насколько иконки рядом весят по-разному</td><td class="n">9%</td><td class="n">15%</td><td class="n">11%</td><td class="n">18%</td><td class="n">15%</td></tr>
      <tr><td>Плотность заливки</td><td class="n">0,40–0,66</td><td class="n">0,27–0,79</td><td class="n">0,27–0,81</td><td class="n">0,27–0,81</td><td class="n">0,27–0,82</td></tr>
      <tr><td>Толщина вырезов к размеру иконки</td><td class="n">≈ 6%</td><td class="n">≈ 3,3%</td><td class="n">≈ 3,4%</td><td class="n">≈ 3,5%</td><td class="n">≈ 3,4%</td></tr>
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
        <li><b>Сетка классов</b> — сделана в кругах 9–11. В круге 11 горизонтальные подняты с 26 до 27, пейзажи и пряник крупнее, ладони меньше: разброс «массы» снова 15%. Остаток — это лёгкие контурные иконки (бегун, туризм, «Движение первых», силовой спорт) и тяжёлые (элеватор, склад); их выравнивает уже форма, а не масштаб.</li>
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
        <li>По горизонтали каждая иконка стоит по центру кадра, по вертикали — по центру квадрата (25,05), кроме зданий и острых верхушек.</li>
        <li><b>Квадратные</b> — большая сторона на голубом квадрате 36,1.</li>
        <li><b>Горизонтальные и транспорт</b> — одна высота 27, зелёные линии 11,55–38,55. Ширина транспорта: поезд и трактор — голубые, грузовик и комбайн — красные.</li>
        <li><b>Вертикальные</b> — одна ширина 21, зелёные линии 14,5–35,5.</li>
        <li><b>Массивные</b> (мяч, пряник, сердце, солнце, ориентир, ладони, портфель) — свой квадрат 33, оранжевые линии; круги тоже ровно по оранжевым.</li>
        <li><b>Здания</b> — низ на оранжевой 41,55; плоский верх на оранжевой 8,55, фронтоны, купола и кровли — до голубой 7.</li>
        <li><b>Пейзажи</b> (парки, аллея) — по ширине до красных 4–46 или по высоте до оранжевых.</li>
        <li>Острая или круглая верхушка у квадратных — вверх до красной 4 при плоском низе на голубой 43,1.</li>
        <li>Нетронутые иконки только масштабировались, от {SCALE_LO} до {SCALE_HI}, без искажения пропорций.</li>
      </ul>
      <div class="seg" role="group" aria-label="Версия пака">
        <button type="button" id="pack-was" data-ver="was" aria-pressed="false">Было</button>
        <button type="button" id="pack-now" data-ver="now" aria-pressed="true">Стало</button>
      </div>
    </header>
    <div class="pack" id="packgrid" data-ver="now">{"".join(pack_cell(m) for m in PACK)}</div>
  </section>
  <section class="review" id="check">
    <header><h2>Проверка: на каких линиях стоит каждая иконка</h2>
      <p>Это не сетка поверх: после сборки скрипт берёт рамку каждой иконки и проверяет, на какие линии попадают её края (допуск 0,06). {CHECK_OK} из {len(PACK)} иконок стоят обоими краями хотя бы по одной оси на линиях, вторая ось — по центру. Две оставшиеся стоят в паре: «Взаимопомощь» — ровно как «Поддержка инициатив» (ладонь одна и та же), «Ферма» — ровно как «Ресурсы» (поля одни и те же).</p></header>
    <div class="tw"><table class="cmp">
      <tr><th>Иконка</th><th>Класс</th><th>Слева — справа</th><th>Сверху — снизу</th></tr>
      {CHECK_ROWS}
    </table></div>
  </section>
  <section class="rv" id="plan"><h3>План: как усреднить пак и приблизиться к Рязани</h3>
    <ol class="rules">
      <li><b>Классы и сетки (сделано в кругах 9–11).</b> Квадратные — голубой квадрат 36,1; горизонтальные и транспорт — общая высота 27; вертикальные — общая ширина 21; массивные — свой квадрат 33; здания — в ряд на одной земле; пейзажи — до красных; круглое и острое — до красного. Положение каждой иконки проверяется скриптом.</li>
      <li><b>Семьи (в работе).</b> Одно дерево, одна ель, один домик, одно окно, одна дверь-арка, один человечек. Сейчас готовы дерево, ель и домик; дальше — окна и двери у всех зданий одного размера, люди с небольшой головой как у Рязани.</li>
      <li><b>Крупные формы — облегчить.</b> Мяч, пряники, сердце, ладони, портфель, элеватор: уменьшены своей сеткой; дальше — добавить им по 1–2 крупных выреза, чтобы плотность была 0,5–0,65, как у Рязани.</li>
      <li><b>Мелкие и ажурные — уплотнить.</b> Бегун, «Движение первых», туризм, силовой спорт, наставники: толще линии, меньше пустоты внутри, без тонких хвостиков.</li>
      <li><b>Сцены — к одному предмету.</b> Где в иконке три-четыре объекта, оставить главный и максимум один второстепенный (как в базе отдыха: дом + ель).</li>
      <li><b>Толщины вырезов — в конце.</b> Четыре уровня 0,7 / 1,0 / 1,4 / 2,0 по всем иконкам, когда размеры и формы утверждены.</li>
      <li><b>Проверка рядом с баблами.</b> После каждого шага — лист в раскладке Рязани (ниже, в сравнении) и замер разброса «массы»: цель — около 9%, как у Рязани.</li>
    </ol>
  </section>
  <section class="rv" id="gaps"><h3>Уровни просветов — утверждены, прогон в конце</h3>
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
      <li>Здания теперь стоят на оранжевой 41,55, а не на голубой 43,1 — так ряд зданий одной высоты и по центру квадрата. Если хотите на голубой базе — сдвину все разом.</li>
      <li>Мегафон и монетки: компоненты в Фигме удалить или оставить в архиве?</li>
      <li>Если формы и размеры устраивают — следующий шаг: толщины вырезов по четырём уровням, потом перенос в Фигму.</li>
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
