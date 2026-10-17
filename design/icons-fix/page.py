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
        '<line class="kb" x1="0" y1="7" x2="50" y2="7"/><line class="kb" x1="0" y1="43.1" x2="50" y2="43.1"/></g>')

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

ICONS4 = [
    dict(slug="grid", node="2891:621", title="Весь пак по квадрату сетки", nb=True,
         ask="Каждая иконка должна быть выровнена по квадрату; оптические поправки — для треугольных и круглых форм.",
         after=[("pack", "2891:621", "Термальные источники", ""), ("pack", "2892:573", "Краеведческий музей", ""),
                ("pack", "2892:596", "Лес с елями", "")],
         notes=["Раньше размер подбирался по площади и плотности заливки, поэтому часть иконок не доставала до полей.",
                "Теперь каждая иконка вписана в квадрат поля: касается полей 4 и 46 или верха 7 и базы 43,1 — смотря что наступит раньше.",
                "Оптика: круглые формы — в квадрат 6–44, острые и полукруглые верхушки (ели, кресты, арки, фронтоны) — на 1 выше линии 7, узкие высокие — до 4.",
                "Термальные источники, музей и ели теперь встали по сетке. Весь пак — ниже."]),
    dict(slug="hands", node="2888:643", title="Поддержка инициатив",
         ask="Обе ладони крупнее, в размер кадра. Ладонь была симпатичнее — снизу баг, взять старую.",
         notes=["Вернул исходную ладонь из Фигмы, без среза запястья.",
                "Ладонь теперь в полную ширину иконки, рядом с ней лампочка с лучами; лучи могут подняться до 5.",
                "Обе иконки с ладонью стоят в кадре одинаково."]),
    dict(slug="help", node="4254:3105", title="Взаимопомощь",
         ask="Та же ладонь, тот же размер.",
         notes=["Та же исходная ладонь в том же масштабе и положении, что в «Поддержке инициатив».",
                "Сердце соразмерно лампочке с лучами."]),
    dict(slug="arrows", node="2888:570", title="Стрелки · логистика и инвестиции", nb=True,
         ask="Стрелку чуть со скруглёнными углами.",
         after=[("pack", "2888:570", "Логистика", ""), ("pack", "4254:1269", "Инвестиции", "")],
         notes=["Единая стрелка пака: тот же треугольник, все три угла чуть скруглены (радиус — 7,5% длины).",
                "Кончик остался на прежнем месте: треугольник удлинён ровно на столько, сколько съело скругление."]),
    dict(slug="farm", node="new:farm", title="Ферма · новая иконка", nb=True,
         ask="По фрейму: поле можно раздвинуть вправо и влево.",
         notes=["Поля раздвинуты до полей кадра 4 и 46: кривые исходных полей растянуты по горизонтали.",
                "Белые просветы заново проведены ровной толщиной 1,4 — от растяжения они не стали толще.",
                "Амбар прежний, отрезан от общего силуэта полей тем же просветом."]),
    dict(slug="park", node="2892:607", title="Центральный парк",
         ask="Деревья одинаковые, без багов; кроны не трефами — овальнее или с кругами посередине.",
         after=[("pack", "2892:607", "А · облако", "в паке"), ("var", "park-oval", "Б · овалы", "")],
         notes=["Оба дерева одинаковые и стоят симметрично. В исходнике 2-я и 4-я колонны были сдвинуты на 1,2 — стволы выровнены по оси ротонды.",
                "Кроны не пересекаются, между ними стандартный просвет 1,6. Срезов одной кроны другой больше нет.",
                "А — облако как у наших деревьев (Парк Машиностроителей): лепестки по краю, середина залита. Б — три овала. В паке стоит А."]),
    dict(slug="church", node="2892:580", title="Свято-Георгиевский храм",
         ask="Вернуть прежний облик: прорези под маковками, галочку над входом; боковые маковки чуть больше.",
         notes=["Вернулись карниз с выступами, свод и белая «галочка» над входом.",
                "Каждая маковка слита со своим барабаном и отделена от кровли ровной прорезью 0,7; у центральной прорезь идёт по дуге свода.",
                "Боковые маковки крупнее в 1,15 раза. Стены выше на 1,5: окна и дверь вытянулись, галочка на месте."]),
    dict(slug="ment", node="2888:639", title="Наставники",
         ask="Плечо забаговано и слишком острое — мягкий полукруг, как у правого человечка, слева прямая линия.",
         notes=["Плечо — мягкая дуга радиуса 3,4, как у плеч ребёнка. Слева прямая линия до основания, зазубрины в углу больше нет."]),
    dict(slug="sun", node="4254:3189", title="Солнечный город",
         ask="Размер солнца и лучей — как было; лучи тоньше, как сейчас.",
         notes=["Диск и лучи — ровно как в исходнике: радиус 10,3, лучи от 12,4 до 18,7.",
                "Лучи тоньше исходных, 3,6 вместо 4,1, углы острые."]),
    dict(slug="cap", node="4254:1272", title="Капитал",
         ask="Вернуть исходные монеты, чуть поправить по сетке.",
         notes=["Исходник без изменений формы. Убраны только обрубки перегородок задней стопки, которые торчали у стыка.",
                "Иконка вписана в квадрат сетки."]),
    dict(slug="cons", node="2888:583", title="Жилищное строительство",
         ask="У большого дома вернуть два окна вверху.",
         notes=["Вернулся верхний ряд: два окна в той же сетке, что были раньше."]),
    dict(slug="career", node="2888:616", title="Карьера",
         ask="Линия у портфеля слишком большая и кривоватая — как у мяча или городских сообществ.",
         notes=["Белая дуга тоньше: около 2 в итоговом размере, как линии баскетбольного мяча (было 3,3).",
                "Толщина ровная по всей длине: раньше это была разность двух сдвинутых дуг, к краям она худела."]),
    dict(slug="san", node="2891:599", title="Санатории",
         ask="Не помещается в сетку. Увеличить, деревья ближе, чтобы были частью композиции.",
         notes=["Здание крупнее в 1,12 раза, стены прямые и стоят на базе (в исходнике здание висело на 0,9 выше, у стен были наплывы).",
                "Ели выше и придвинуты к зданию вплотную — стоят перед его углами, просвет 0,7 не задевает окна.",
                "Иконка теперь вписана в поля 4–46."]),
    dict(slug="base", node="2891:608", title="Базы отдыха",
         ask="Не совсем помещается в сетку.",
         notes=["Убрана «ступня» слева у земли — из-за неё иконка вылезала влево.",
                "Окно — четыре ровные створки по оси конька (в исходнике разного размера и с кривым подоконником); конёк мягкий.",
                "Вписана в поля 4–46, ель с острой верхушкой — на 1 выше линии 7."]),
    dict(slug="comb", node="4254:3023", title="Сельхозтехника · комбайн",
         ask="Вырезы должны совпадать с вырезами у трактора.",
         after=[("pack", "4254:3023", "Стало", ""), ("pack", "4254:3026", "Трактор для сравнения", "")],
         notes=["У трактора все просветы около 1,3, у комбайна были 0,75–0,85. Теперь у комбайна все просветы 1,3 — как у трактора.",
                "Порядок слоёв: колёса, жатка, кабина, корпус, бункер; каждый отрезан от предыдущих одним и тем же просветом.",
                "Жатка упрощена до цельного блока: тонкий палец внутри неё при таком просвете превратился бы в щепку."]),
    dict(slug="city", node="2892:571", title="Комфортный и гостеприимный город",
         ask="Вместо аллеи — классическое здание Заводоуковска, усреднённое, рядом сердечко.",
         notes=["Усреднённое классическое здание: портик с фронтоном и круглым окном, четыре колонны, крылья с арочными окнами, общий цоколь.",
                "Сердце то же, что во «Взаимопомощи», отделено от здания просветом 1,3.",
                "Отличается от «Гостиниц» и «Музея» портиком с колоннами и сердцем."]),
    dict(slug="gate", node="2892:612", title="Вход в парк Машиностроителей",
         ask="Слишком упрощённо, странные мини-выступы сверху у колонн, расстояния, не по сетке.",
         notes=["Теперь это ворота: две колонны и полукруглая арка над проходом.",
                "Капитель цельная, мини-выступов нет. Колонна: цоколь, ствол с двумя каннелюрами, капитель — все просветы одинаковые, 1,3.",
                "Арка опирается на капители; её верх — на 1 выше линии 7, как у других полукруглых форм."]),
]
ICONS = []
for it in ICONS4 + ICONS:
    it["b"] = None if it.get("nb") else sym_before(it["node"])
    after = it.get("after") or [("pack", it["node"], "Стало", "")]
    it["a"] = [((sym_pack(k) if kind == "pack" else sym_var(k)), lab, tag) for kind, k, lab, tag in after]

_sc = [m["scale"] for m in META.values() if not m["rebuilt"]]
SCALE_LO, SCALE_HI = (f"{min(_sc):.2f}".replace(".", ","), f"{max(_sc):.2f}".replace(".", ","))
SMALL = ["2892:571", "2891:586", "4254:3019", "2891:599", "4254:3193"]

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
    <span class="eyebrow">Черновик · Иконки · круг 7</span>
    <h1>Правки иконок</h1>
    <p>Седьмой круг по вашим замечаниям. Слева версия из Фигмы, справа новая в итоговом размере и положении в кадре. Под каждой реальные размеры 50, 32 и 24 px.</p>
    <p>Главное в этом круге: весь пак выровнен по квадрату сетки. Коворкинг вернулся к исходнику с подставкой, ракета осталась как в прошлом круге. Всё принятое стоит в общей сетке пака ниже.</p>
  </header>
  <div class="bar" role="toolbar" aria-label="Вид иконок">
    <div class="seg" role="group" aria-label="Цвет">
      <button type="button" id="ink-black" data-ink="black" aria-pressed="true">Чёрный</button>
      <button type="button" id="ink-blue" data-ink="blue" aria-pressed="false">Синий</button>
      <button type="button" id="ink-green" data-ink="green" aria-pressed="false">Зелёный</button>
      <button type="button" id="ink-red" data-ink="red" aria-pressed="false">Красный</button>
    </div>
    <button type="button" class="chk" id="keys" aria-pressed="true">Сетка</button>
    <span class="legend"><span><i style="background:var(--key-a)"></i>поля 4 и 46</span><span><i style="background:var(--key-b)"></i>верх 7, база 43,1</span></span>
  </div>
  <nav class="toc" aria-label="Иконки">{TOC}<a href="#pack">Весь пак</a><a href="#small">Мелкий размер</a><a href="#ask">Что уточнить</a></nav>
  {"".join(section(it) for it in ICONS4)}
  <section class="review" id="pack">
    <header><h2>Весь пак: сетка и объём</h2>
      <p>Все {len(PACK)} иконок в кадрах 50 × 50. Переключите «Было» и «Стало», чтобы увидеть, как они встали. Точкой отмечены перерисованные.</p>
      <ul class="rules">
        <li>Все стоящие иконки встали на одну базу 43,1. Раньше было две базы, 43,1 и 43,9, а «Личный рост» и старое «Участие» опускались до 45.</li>
        <li>Парящие формы отцентрованы по высоте поля 7–43,1: сердце, солнце, мяч, компас, стрелки, самолёт, змей, ракета, ладони.</li>
        <li>По горизонтали каждая иконка стоит по центру кадра.</li>
        <li>Каждая иконка вписана в квадрат поля: касается полей 4 и 46 или верха 7 и базы 43,1 — смотря что наступит раньше.</li>
        <li>Оптические поправки: круглые формы — в квадрат 6–44, острые и полукруглые верхушки — на 1 выше линии 7, узкие высокие — до 4.</li>
        <li>Нетронутые иконки только масштабировались, от {SCALE_LO} до {SCALE_HI}, без искажения пропорций.</li>
      </ul>
      <div class="seg" role="group" aria-label="Версия пака">
        <button type="button" id="pack-was" data-ver="was" aria-pressed="false">Было</button>
        <button type="button" id="pack-now" data-ver="now" aria-pressed="true">Стало</button>
      </div>
    </header>
    <div class="pack" id="packgrid" data-ver="now">{"".join(pack_cell(m) for m in PACK)}</div>
  </section>
  <section class="rv" id="small"><h3>Проверка в мелком размере</h3>
    <p>Я посмотрел весь пак на 24 и 32 px. Почти всё читается. Хуже всего на 24 px мелкие детали сливаются у этих иконок. Детали вам нужны, поэтому я их не трогал. Если понадобится, для мелких плашек можно сделать упрощённые версии.</p>
    <div class="thumbs">{"".join(small_row(n) for n in SMALL)}</div>
  </section>
  <section class="rv" id="ask"><h3>Что уточнить</h3>
    <ul class="rules">
      <li>Центральный парк: кроны «облаком» (А) или овалами (Б)? В паке пока стоит А.</li>
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
