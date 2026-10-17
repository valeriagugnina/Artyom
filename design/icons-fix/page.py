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

ICONS = [
    dict(slug="inv", node="4254:1269", title="Ф1 · Инвестиции",
         ask="Взять одно крыло полос, как у самолётика, сделать крупнее, вывести из угла и добавить стрелку.",
         after=[("pack", "4254:1269", "A · вверх-вправо", "рекомендую"), ("var", "investments-flat", "B · горизонтально", "")],
         notes=["Взято верхнее крыло «К» из знака целиком: три полосы с родным сужением, от широких концов к стыку.",
                "Крыло крупнее, чем в «Туризме»: масштаб 0,88 против 0,61. Оно выходит из левого нижнего угла, концы полос срезает рамка.",
                "Из стыка растёт стрелка с наклоном 20°. В варианте B всё горизонтально, ровно как летит самолётик."]),
    dict(slug="log", node="2888:570", title="Логистический коридор",
         ask="Стрелки грубые и некрасивые, переделать. Пришлю примеры.",
         notes=["Пока сделал тоньше: древко 3, наконечник 11 × 8.",
                "Это временная версия. Переделаю, когда пришлёте примеры."]),
    dict(slug="park", node="2892:607", title="Центральный парк",
         ask="Деревья стоят за входной группой: она залита целиком, деревья отделены от неё горизонтальными линиями. Правое дерево чуть крупнее.",
         notes=["Ротонда залита целиком: кровля и цоколь идут сплошной полосой, ничем не разрезаны.",
                "Второй и четвёртый столбы — стволы за ротондой. Они отделены от неё только горизонтальными просветами 0,7: над кровлей, под кровлей и над цоколем.",
                "Правое дерево увеличено на 15% от основания ствола и стало выше. Между кронами просвет 0,7."]),
    dict(slug="city", node="2892:571", title="Комфортный и гостеприимный город",
         ask="Не многоэтажный дом: хрущёвке немножко добавить второй этаж и свести линии.",
         after=[("var", "city-a", "A · этаж только хрущёвке", ""), ("pack", "2892:571", "B · всем по невысокому этажу", "")],
         notes=["A: второй этаж только у центральной хрущёвки, боковые дома как в исходнике. Верх хрущёвки стоит на одной линии с коньками соседних крыш.",
                "B: всем домам по невысокому второму этажу, вдвое ниже прошлой версии. Верх хрущёвки стоит на одной линии с верхом стен соседних домов.",
                "В обоих вариантах окна второго этажа — копии окон первого, все линии параллельны исходным, крыши у хрущёвки нет."]),
    dict(slug="cons", node="2888:583", title="Жилищное строительство",
         ask="Убрать окна у большого дома, чтобы все дома были без окон.",
         notes=["Окна убраны, остальное как вы утвердили."]),
    dict(slug="run", node="2888:595", title="Активный спортивный город",
         ask="Тянущуюся руку сделать как у бегуна в «Молодёжи», что-то среднее.",
         notes=["Кисть вытянутой руки скруглена по ширине руки, как в «Молодёжи».",
                "Колено, ноги и вторая рука не менялись."]),
    dict(slug="church", node="2892:580", title="Свято-Георгиевский храм",
         ask="Убрать перемычку между крышей и храмом, соединить купола с основаниями.",
         notes=["Карниз слит со стенами, белой линии под ним больше нет.",
                "Каждый купол слит со своим барабаном, а барабаны — с кровлей. Лишних перемычек не осталось."]),
    dict(slug="hotel", node="2891:614", title="Гостиницы",
         ask="Убрать тонкую перемычку на двери.",
         notes=["Дверь стала одним проёмом шириной с окно, 5,5, без перемычки посередине. До пола, как и было."]),
    dict(slug="cowork", node="2888:632", title="Коворкинги",
         ask="Зачем подставка снизу? Пусть будет просто компьютер.",
         notes=["Убрал отдельную клавиатуру снизу, остался монитор на ножке.",
                "Пришлёте референсы — перерисую."]),
    dict(slug="ment", node="2888:639", title="Наставники",
         ask="Человечек со звёздочкой должен быть соотнесён с бегущим.",
         notes=["Головы взрослого и бегуна почти одного размера в итоговом кадре (8,3 и 8,0), кисти скруглены одинаково.",
                "Убрал тонкий белый клин внизу корпуса взрослого: силуэт цельный, как у бегуна.",
                "Если нужно сильнее, скажите что: толщину рук, пропорции корпуса или позу."]),
    dict(slug="rocket", node="2888:612", title="Личный рост",
         ask="Выхлоп слева выровнять по квадрату, срез ровный, ракету чуть крупнее.",
         notes=["Три полосы выхлопа срезаны одной вертикалью, срез стоит на левой направляющей 4.",
                "Иконка крупнее: масштаб 0,99 вместо 0,91."]),
    dict(slug="kite", node="2892:626", title="Фестиваль воздушных змеев",
         ask="Нашёл сам: хвосты змея обрезаны вразнобой.",
         notes=["Верхний хвост продлён по своему ходу, оба хвоста срезаны одной вертикалью."]),
    dict(slug="scales", node="4254:3191", title="Баланс",
         ask="Весы плохо встают по сетке, странный прямоугольник. Навершие убрать или сделать прямым.",
         notes=["Собрал заново геометрично: прямая балка без навершия, прямая стойка, основание-полуовал.",
                "Чаши одинаковые и симметричные, подвесы — треугольники со сторонами одной толщины 1,7."]),
    dict(slug="glider", node="2891:591", title="Планёры",
         ask="Похож ли на планёр, который делали в Заводоуковске? Развернуть по диагонали в правый верхний угол и поправить по сетке.",
         after=[("pack", "2891:591", "A · силуэт А-7", "рекомендую"), ("var", "glider-orig", "B · прежний силуэт", "")],
         notes=["В 1941 году в Заводоуковск эвакуировали авиазавод, он стал заводом № 499 и выпускал десантный планёр Антонова А-7 и учебный А-2.",
                "У А-7 размах 19 м при длине 11,5 м, высокоплан, фюзеляж «гондола с балкой». В прежней иконке короткие крылья (размах в 1,2 раза больше длины) и острый нос, как у истребителя.",
                "A — силуэт по А-7: длинное узкое крыло, тупой нос, тонкая балка к хвосту. Толщины чуть утрированы, чтобы читалось на 24 px.",
                "B — прежний силуэт, просто развёрнут. Оба летят в правый верхний угол и стоят по центру поля."]),
    dict(slug="truck", node="4254:3005", title="Грузовик",
         ask="Попробовать наклон, чтобы смотрелся стильнее, в движении.",
         notes=["Кузов из трёх наклонных секций с просветом 1,6, как на вашем референсе.",
                "Задняя стенка кабины и окно наклонены так же. Нос кабины и колёса не менялись."]),
]
for it in ICONS:
    it["b"] = sym_before(it["node"])
    after = it.get("after") or [("pack", it["node"], "Стало", "")]
    it["a"] = [((sym_pack(k) if kind == "pack" else sym_var(k)), lab, tag) for kind, k, lab, tag in after]

_sc = [m["scale"] for m in META.values() if not m["rebuilt"]]
SCALE_LO, SCALE_HI = (f"{min(_sc):.2f}".replace(".", ","), f"{max(_sc):.2f}".replace(".", ","))
SMALL = ["2892:571", "2891:586", "4254:3019", "2891:599", "4254:3193"]

PACK = [m for m in META.values()]
for m in PACK:
    sym_before(m["node"]); sym_pack(m["node"])

def section(it):
    tiles = big(it["b"], "Было") + "".join(big(sid, lab, tag) for sid, lab, tag in it["a"])
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
    return (f'<figure class="cell"><div class="cv"><svg class="ico was" viewBox="0 0 50 50" aria-hidden="true"><use href="#{sb}"/>{KEYS}</svg>'
            f'<svg class="ico now" viewBox="0 0 50 50" role="img" aria-label="{html.escape(m["name"])}"><use href="#{sn}"/>{KEYS}</svg></div>'
            f'<figcaption>{mark}{html.escape(m["name"])}</figcaption></figure>')

defs = "".join(f'<symbol id="{k}" viewBox="0 0 50 50">{v}</symbol>' for k, v in symbols.items())
grads = ("".join(
    f'<linearGradient id="g{n}" x1="4" y1="46" x2="46" y2="4" gradientUnits="userSpaceOnUse">'
    f'<stop stop-color="{a}"/><stop offset=".35" stop-color="{b}"/><stop offset=".7" stop-color="{c}"/></linearGradient>'
    for n, (a, b, c) in (("Blue", ("#003DA5", "#2CD5C4", "#00A9E0")),
                         ("Green", ("#00843D", "#47D7AC", "#DDF314")),
                         ("Red", ("#E4002B", "#FFC851", "#FF6900")))))

TOC = "".join(f'<a href="#{it["slug"]}">{it["title"].replace("Ф1 · ", "").replace("Ф3 · ", "").replace("Ф2 · ", "")}</a>' for it in ICONS)

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
.tile {{ margin: 0; display: grid; gap: 8px; min-width: 0 }}
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
    <span class="eyebrow">Черновик · Иконки · круг 3</span>
    <h1>Правки иконок</h1>
    <p>Третий круг по вашим замечаниям. Слева версия из Фигмы, справа новая в итоговом размере и положении в кадре. Под каждой реальные размеры 50, 32 и 24 px. Числа даны в единицах сетки 50 × 50.</p>
    <p>Где есть варианты, отметил, какой рекомендую. По городу нужен ваш выбор, вопросы собраны внизу страницы.</p>
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
  {"".join(section(it) for it in ICONS)}
  <section class="review" id="pack">
    <header><h2>Весь пак: сетка и объём</h2>
      <p>Все {len(PACK)} иконок в кадрах 50 × 50. Переключите «Было» и «Стало», чтобы увидеть, как они встали. Точкой отмечены перерисованные.</p>
      <ul class="rules">
        <li>Все стоящие иконки встали на одну базу 43,1. Раньше было две базы, 43,1 и 43,9, а «Личный рост» и старое «Участие» опускались до 45.</li>
        <li>Парящие формы отцентрованы по высоте поля 7–43,1: сердце, солнце, мяч, компас, стрелки, самолёт, змей, ракета, ладони.</li>
        <li>По горизонтали каждая иконка стоит по центру кадра.</li>
        <li>Размер подобран по площади и плотности заливки: плотные формы чуть меньше, ажурные чуть крупнее. Высота в пределах 7–43,1, ширина в пределах 4–46. Высоким и круглым формам разрешён свес до 4 и до 6.</li>
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
      <li>Комфортный город: какой вариант ближе, A или B?</li>
      <li>Логистика и коворкинг: жду примеры, по ним перерисую.</li>
      <li>Наставники: хватит ли того, что сделал, или подогнать сильнее?</li>
      <li>Старое «Участие» с хлопком убрал из набора, как вы сказали.</li>
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
