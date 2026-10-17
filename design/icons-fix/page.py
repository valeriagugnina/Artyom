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

# ── правки ────────────────────────────────────────────────────────────────────
ICONS = [
    dict(slug="inv", node="4254:1269", title="Ф1 · Инвестиции",
         ask="Сделать по скетчу: три фирменных потока снизу-слева сходятся в стрелку.",
         after=[("investments", "Стало", "")],
         notes=["Три полосы входят из-за левого края и из-под базовой линии и сходятся в наконечник, как на скетче.",
                "Полосы сужаются с 3,2 до 2,1, шаг между ними с 6,0 до 3,2: поток собирается к стрелке.",
                "Нижняя кромка средней полосы приходит ровно в угол сетки (4; 43,1).",
                "Наконечник: наклон 62°, длина 9,6, основание 11. Этот же наконечник стоит в «Логистике»."]),
    dict(slug="tour", node="4254:3107", title="Ф3 · Туризм",
         ask="Взять элемент движения из знака, крылья «К», и развернуть его вправо.",
         after=[("tourism-mirror", "A · движение вправо", "рекомендую"),
                ("tourism-logo", "B · как в знаке", ""),
                ("tourism", "C · с головой птицы", "")],
         notes=["Полосы взяты из знака без искажений: три верхние и три нижние полосы «К» в тех же пропорциях. Там, где полоса срасталась с «З», кромка достроена по касательным.",
                "Элемент вписан по высоте ровно от 7 до 43,1, концы полос стоят на направляющих.",
                "A смотрит вправо: полосы сходятся в точку справа, как стрелка. B повторяет знак. C оставляет птицу из текущей версии, но с точными полосами."]),
    dict(slug="log", node="2888:570", title="Логистический коридор",
         ask="Две стрелки, влево и вправо, в стиле нашей системы.",
         after=[("logistics", "A · встречные потоки", "рекомендую"),
                ("logistics-straight", "B · прямые потоки", "")],
         notes=["Две встречные стрелки из фирменных полос: поток входит из-за края и выравнивается в наконечник.",
                "Нижняя стрелка повторяет верхнюю с поворотом на 180°, поэтому композиция уравновешена.",
                "Наконечник и сужение полос те же, что в «Инвестициях»: иконки читаются как одна семья.",
                "B проще и строже, но ближе к стандартным библиотекам иконок."]),
    dict(slug="park", node="2892:607", title="Центральный парк",
         ask="Стволы не должны упираться во вход, отступы привести к системе.",
         after=[("park", "Стало", "")],
         notes=["Деревья стоят за ротондой: стволы заканчиваются в 1,6 от кровли, а не упираются в неё (было 0,28).",
                "Между кронами тоже ровно 1,6.",
                "Ротонда стала симметричной: колонны 2,6 · 1,8 · 3,0 · 1,8 · 2,6 с равными просветами 4,4. Было 3,4–6,6, и боковые колонны стояли на разном расстоянии от центра.",
                "Цоколь 1,4 вместо 0,85: не пропадает на 24 px."]),
    dict(slug="city", node="2892:571", title="Комфортный и гостеприимный город",
         ask="Слишком горизонтально. Дома выше, двухэтажные, чтобы иконка вписалась в квадрат.",
         after=[("city", "Стало", "")],
         notes=["Все три дома двухэтажные: два ряда окон на торцах, на стенах вдоль улицы и на центральном доме.",
                "Высота композиции 31,6 вместо 21,5 (по вертикали от 11,5 до 43,1), иконка стала почти квадратной.",
                "Перспектива смягчена, чтобы высокие стены не заваливались к центру.",
                "Все просветы 0,7, как были в исходнике: кровля, деревья, центральный дом. Тротуары и деревья не менялись."]),
    dict(slug="cons", node="2888:583", title="Жилищное строительство",
         ask="Края дома согласовать с краном, поправить уголок у крыши и кривой домик.",
         after=[("construction", "Стало", "")],
         notes=["Правый край дома совпадает с концом стрелы крана (x = 42). Левый край карниза стоит в 1,6 от мачты: раньше карниз подходил к ней на 0,87.",
                "Карниз выступает одинаково с обеих сторон, на 0,7. Кривой уголок справа убран.",
                "Окна 2 × 3 с равными полями и промежутками. Было 2,8 слева и 5,3 справа.",
                "Крюк не доходит до крыши ровно на 1,6.",
                "Домик симметричный: конёк по центру, оба ската одного уклона, «галочка» кровли толщиной 1,8 с острым коньком. Оголовок крана перерисован с тягами постоянной толщины."]),
    dict(slug="run", node="2888:595", title="Активный спортивный город",
         ask="У человечка слишком острые руки и ноги, сделать окончания квадратнее.",
         after=[("active", "Стало", "")],
         notes=["Кисти и стопы заканчиваются прямым срезом шириной 1,9–2,4 со скруглением 0,45 вместо иглы.",
                "Толчковая нога стоит на базовой линии 43,1 (была 43,9).",
                "Голова, корпус и поза не менялись."]),
]

for it in ICONS:
    it["b"] = sym_src(it["node"], f"b-{it['slug']}")
    it["a"] = [(sym_build(n, f"a-{it['slug']}-{i}"), lab, tag) for i, (n, lab, tag) in enumerate(it["after"])]

# ── разбор пака ───────────────────────────────────────────────────────────────
def ids(*nodes): return [(sym_src(n, "r-" + n.replace(":", "-")), SRC[n]["name"].replace("Иконки/", "")) for n in nodes]

REVIEW = [
    dict(title="Две базовые линии", keys=True,
         text="Здания стоят на 43,1, а люди, техника и предметы на 43,9: таких 24 иконки. «Личный рост» и «Участие» опускаются до 45. В одном ряду разница видна. Предлагаю поставить всё на 43,1, а круглым формам оставить свес не больше 0,4.",
         icons=ids("2888:616", "2888:620", "4254:3005", "2888:673")),
    dict(title="Контурные иконки среди залитых", keys=False,
         text="Ладони в «Участии» и «Взаимовыручке» нарисованы контуром, а в «Волонтёрах» и «Взаимопомощи» залиты. Предлагаю перевести их в заливку.",
         icons=ids("2888:677", "4254:3193", "2888:669")),
    dict(title="Тот же острый бегун в «Молодёжи»", keys=False,
         text="В Ф2 у фигуры такие же игольчатые кисти и стопы, как были у «Активного города». Могу применить ту же правку, чтобы бегуны совпадали.",
         icons=ids("4254:3034")),
    dict(title="Детали, которые пропадают на 24–32 px", keys=False,
         text="Зубчатый край и буквы пряников, кресты храма, окна и ёлки санаториев, ферма сцены. В презентации на крупных размерах это читается, в мелких плашках сливается. Можно сделать упрощённые версии для мелкого кегля.",
         icons=ids("2891:586", "4254:3019", "2892:580", "2891:599", "2888:603")),
    dict(title="Повторы по смыслу", keys=False,
         text="Сердце в ладонях есть в «Волонтёрах» и «Взаимопомощи», ладонь в «Участии» и «Взаимовыручке», два варианта пряника. Если иконки встанут рядом, их легко перепутать. Стоит выбрать по одной.",
         icons=ids("2888:669", "4254:3105", "2891:586", "4254:3019")),
    dict(title="«Движение первых» легче остальных", keys=False,
         text="Тонкая стрелка-курсор по весу заметно светлее соседей и читается как указатель интерфейса. Её стоит сделать плотнее или перерисовать на фирменных полосах.",
         icons=ids("2888:665")),
]

def section(it):
    tiles = big(it["b"], "Было") + "".join(big(sid, lab, tag) for sid, lab, tag in it["a"])
    notes = "".join(f"<li>{n}</li>" for n in it["notes"])
    wide = " wide" if len(it["a"]) > 1 else ""
    return (f'<section class="icon{wide}" id="{it["slug"]}"><header class="ih"><h2>{it["title"]}</h2>'
            f'<p class="ask">{it["ask"]}</p></header>'
            f'<div class="tiles">{tiles}</div><ul class="notes">{notes}</ul></section>')

def review_item(r):
    th = "".join(thumb(sid, nm, r["keys"]) for sid, nm in r["icons"])
    return f'<article class="rv"><h3>{r["title"]}</h3><p>{r["text"]}</p><div class="thumbs">{th}</div></article>'

defs = "".join(f'<symbol id="{k}" viewBox="0 0 50 50">{v}</symbol>' for k, v in symbols.items())
grads = ("".join(
    f'<linearGradient id="g{n}" x1="4" y1="46" x2="46" y2="4" gradientUnits="userSpaceOnUse">'
    f'<stop stop-color="{a}"/><stop offset=".35" stop-color="{b}"/><stop offset=".7" stop-color="{c}"/></linearGradient>'
    for n, (a, b, c) in (("Blue", ("#003DA5", "#2CD5C4", "#00A9E0")),
                         ("Green", ("#00843D", "#47D7AC", "#DDF314")),
                         ("Red", ("#E4002B", "#FFC851", "#FF6900")))))

TOC = "".join(f'<a href="#{it["slug"]}">{it["title"].replace("Ф1 · ", "").replace("Ф3 · ", "")}</a>' for it in ICONS)

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
    <span class="eyebrow">Черновик · Иконки · текущий набор</span>
    <h1>Правки иконок</h1>
    <p>Семь иконок перерисованы в коде по вашим замечаниям. Слева текущая версия из Фигмы, справа новая. Под каждой показаны реальные размеры 50, 32 и 24 px. Все числа даны в единицах сетки 50 × 50.</p>
    <p>Выберите варианты для «Туризма» и «Логистики» и отметьте, что поправить. После утверждения перенесу иконки в Фигму, в те же компоненты.</p>
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
  <nav class="toc" aria-label="Иконки">{TOC}<a href="#pack">Разбор пака</a></nav>
  {"".join(section(it) for it in ICONS)}
  <section class="review" id="pack">
    <header><h2>Слабые места пака</h2>
      <p>Это я не трогал, здесь только замечания по всему паку. Скажите, что из этого брать в работу.</p></header>
    <div class="rv-grid">{"".join(review_item(r) for r in REVIEW)}</div>
  </section>
  <aside class="next"><h3>Что дальше</h3>
    <p>Напишите, какие варианты берём, например «Туризм A, Логистика A», и что поправить. Затем я заменю векторы в компонентах на странице «Черновик» и проверю их на слайдах.</p></aside>
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
