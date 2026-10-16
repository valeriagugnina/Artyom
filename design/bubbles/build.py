"""Собирает HTML-макет слайдов «бабблы» из ассетов, выгруженных из Figma.

Запуск: python3 build.py  ->  index.html рядом со скриптом.
"""
import json
import re
from html import escape
from pathlib import Path

HERE = Path(__file__).parent
A = json.loads((HERE / "assets.json").read_text(encoding="utf-8"))

# Мастер-иконка «Спорт» в Figma битая: берём гантель из варианта «Sport» (50×50)
SPORT = (
    '<g transform="translate(12 13.3) scale(2.55)"><path d="M28.4 46.0L25.5 43.0L33.0 35.5L15.0 17.5L7.4 25'
    "L4.5 22.0L7.4 18.9L4.5 16.0L8.9 11.5L5.9 8.4L8.9 5.5L12.0 8.4L16.5 4.0L19.4 7.0L22.5 4.0L25.5 7.0"
    "L17.9 14.5L36.0 32.5L43.5 25L46.5 28.0L43.5 31.1L46.5 34.0L42.0 38.5L45.0 41.6L42.0 44.5L39.0 41.6"
    'L34.5 46.0L31.5 43.0L28.4 46.0Z"/></g>'
)

DIRS = [
    {
        "key": "main", "short": "Основное", "name": "Основное направление",
        "sub": "Городская жизнь и общие ценности", "no": "01",
        "icons": ["Активный город", "Общественные пространства", "Уличные события", "Зелёный город",
                  "Городские сообщества", "Принадлежность", "Участие"],
    },
    {
        "key": "inv", "short": "Инвестиции", "name": "Инвестиции и деловая среда",
        "sub": "Возможности территории и развитие экономики", "no": "02",
        "icons": ["Логистический коридор", "Сельское хозяйство", "Промышленное производство",
                  "Жилищное строительство", "Богатые природные ресурсы", "Инвестиционные площадки"],
    },
    {
        "key": "tour", "short": "Туризм", "name": "Туризм и имидж города",
        "sub": "История, природа и впечатления", "no": "03",
        "icons": ["Планёры", "Купцы Колмаковы", "Колмаковский пряник", "Санатории", "Гостевые домики",
                  "Гостиницы", "Термальные источники", "Краеведческий музей", "Свято-Георгиевский храм",
                  "Колмаковский парк", "Центральный парк", "Парк Машиностроителей", "Фестиваль змеев"],
    },
    {
        "key": "youth", "short": "Молодёжь", "name": "Молодёжь и карьера",
        "sub": "Энергия, участие и движение вперёд", "no": "04",
        "icons": ["Момент победы", "Площадка для роста", "Личный рост", "Карьера", "Спорт", "Коворкинги",
                  "Наставники", "Поддержка инициатив", "Движение первых", "Волонтёры"],
    },
]

# Порядок тем на слайдах 14 и 19 (как в исходной презентации)
THEME_ORDER = {
    "main": DIRS[0]["icons"],
    "inv": DIRS[1]["icons"],
    "tour": ["Купцы Колмаковы", "Колмаковский пряник", "Планёры", "Санатории", "Гостевые домики", "Гостиницы",
             "Термальные источники", "Краеведческий музей", "Свято-Георгиевский храм", "Колмаковский парк",
             "Центральный парк", "Парк Машиностроителей", "Фестиваль змеев"],
    "youth": ["Площадка для роста", "Личный рост", "Карьера", "Спорт", "Момент победы", "Коворкинги",
              "Наставники", "Поддержка инициатив", "Движение первых", "Волонтёры"],
}

ALL_ICONS = [n for d in DIRS for n in d["icons"]]
IDS = {name: f"i{n:02d}" for n, name in enumerate(sorted(set(ALL_ICONS), key=ALL_ICONS.index), 1)}


def inner(svg):
    body = re.sub(r"^<svg[^>]*>|</svg>$", "", svg.strip())
    body = re.sub(r"<defs>.*?</defs>", "", body, flags=re.S)
    return re.sub(r'\s(fill|clip-path)="[^"]*"', "", body)


def sprite():
    out = []
    for name, sid in IDS.items():
        body = SPORT if name == "Спорт" else inner(A[name])
        out.append(f'<symbol id="{sid}" viewBox="0 0 154 154">{body}</symbol>')
    logo = re.sub(r"<defs>.*?</defs>", "", A["logo"], flags=re.S)
    logo = re.sub(r"^<svg[^>]*>|</svg>$", "", logo)
    logo = re.sub(r'\sclip-path="[^"]*"', "", logo)
    logo = logo.replace('fill="#151F6D"', 'style="fill:var(--lt)"')
    logo = re.sub(r'fill="url\(#[^)]*\)"', 'style="fill:var(--lm)"', logo)
    out.append(f'<symbol id="logo" viewBox="0 0 330 63">{logo}</symbol>')
    shape = re.sub(r"<defs>.*?</defs>", "", A["shapeValeria"], flags=re.S)
    shape = re.sub(r"^<svg[^>]*>|</svg>$", "", shape)
    shape = re.sub(r'\sfill="url\(#[^)]*\)"', "", shape)
    out.append(f'<symbol id="flow" viewBox="0 0 632 674">{shape}</symbol>')
    air = re.sub(r"^<svg[^>]*>|</svg>$", "", A["airflow"])
    air = air.replace(' fill="white"', "")
    out.append(f'<symbol id="air" viewBox="0 0 1020 1080">{air}</symbol>')
    grads = {
        "main": ["#151F6D", "#1A3C9E", "#00A9E0"],
        "inv": ["#003DA5", "#00A9E0", "#2CD5C4"],
        "tour": ["#00843D", "#36C08E", "#C7E51C"],
        "youth": ["#E4002B", "#FF6900", "#FFB54A"],
        "logo": ["#003DA5", "#2CD5C4", "#00A9E0"],
    }
    for key, (a, b, c) in grads.items():
        out.append(
            f'<linearGradient id="gr-{key}" x1="0" y1="1" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{a}"/><stop offset=".55" stop-color="{b}"/>'
            f'<stop offset="1" stop-color="{c}"/></linearGradient>'
        )
    return '<svg class="sprite" aria-hidden="true" focusable="false"><defs>' + "".join(out) + "</defs></svg>"


def ic(name, tone):
    return (f'<svg class="ic ic--{tone}" viewBox="0 0 154 154" role="img" aria-label="{escape(name)}">'
            f'<use href="#{IDS[name]}"/></svg>')


def dot(name, fill):
    tone = "w" if fill == "g" else "g"
    return f'<span class="dot dot--{fill}">{ic(name, tone)}</span>'


def logo(variant):
    return f'<svg class="logo logo--{variant}" viewBox="0 0 330 63" role="img" aria-label="Заводоуковск"><use href="#logo"/></svg>'


def head(variant, tag, title, sub=None, title_cls=""):
    parts = [logo(variant)]
    if tag:
        parts.append(f'<span class="b b--line-g tag">{escape(tag)}</span>')
    parts.append(f'<h2 class="h1 {title_cls}">{escape(title)}</h2>')
    if sub:
        parts.append(f'<p class="sub">{escape(sub)}</p>')
    return "".join(parts)


# ---------- Слайд 2 · План работы ----------
STAGES = [
    ("01", "Исследование", "done",
     ["Анализ текущего бренда", "Обсуждение редизайна", "Утверждение носителей", "Список и стилистика иконок"],
     "Обсуждение редизайна логотипа, списка и стилистики иконок и носителей бренда."),
    ("02", "Логотип", "done",
     ["Редизайн логотипа", "Обновление системы фирстиля", "Утверждение результата"],
     "Разработка и презентация логотипа и обновлённого фирменного стиля."),
    ("03", "Фирменный стиль", "now",
     ["Набор иконок · 30 шт.", "Презентация фирстиля", "7–8 носителей", "Утверждение результата"],
     "Разработка и презентация системы: иконки, графика и носители."),
    ("04", "Передача", "next",
     ["Финальные правки", "Обновление брендбука", "Папка со всеми материалами"],
     "Финальная сборка и передача всех материалов бренда."),
]
STATE = {"done": "Готово", "now": "В работе", "next": "Далее"}


def slide_plan():
    cols = []
    for no, title, state, tasks, say in STAGES:
        items = "".join(f'<li class="b task">{escape(t)}</li>' for t in tasks)
        cols.append(
            f'<li class="stage is-{state}">'
            f'<div class="stage-head"><span class="num">{no}</span><span class="b state">{STATE[state]}</span></div>'
            f'<span class="b stage-title">{escape(title)}</span>'
            f'<ul class="tasks">{items}</ul>'
            f'<p class="say">{escape(say)}</p></li>'
        )
    return (
        '<div class="slide s-plan d-logo">'
        '<svg class="air" viewBox="0 0 1020 1080" aria-hidden="true"><use href="#air"/></svg>'
        + logo("w")
        + '<span class="b b--line-w now-tag">Сейчас идёт 3 этап</span>'
        '<h2 class="h1 h1--plan">План работы</h2>'
        '<div class="track" aria-hidden="true"></div>'
        f'<ol class="stages">{"".join(cols)}</ol></div>'
    )


# ---------- Слайд 14 · Четыре направления ----------
def slide_dirs():
    rows = []
    for d in DIRS:
        themes = "".join(
            f'<li class="b theme">{dot(n, "g")}<span>{escape(n)}</span></li>' for n in THEME_ORDER[d["key"]]
        )
        rows.append(
            f'<section class="dir d-{d["key"]}">'
            f'<div class="b dir-pill">{dot(d["icons"][0], "w")}'
            f'<span class="dir-txt"><b>{escape(d["short"])}</b><small>{escape(d["sub"])}</small></span></div>'
            f'<ul class="themes">{themes}</ul></section>'
        )
    return ('<div class="slide s-dirs">' + head("c", "Темы и образы города", "Иконки: четыре направления")
            + f'<div class="dirs">{"".join(rows)}</div></div>')


# ---------- Слайды 15–18 · Иконки по направлениям ----------
# колонки, диаметр круга, кегль подписи, поля подписи
GRID = {5: (3, 172, 22, "10px 20px"), 6: (3, 172, 22, "10px 20px"),
        9: (5, 136, 19, "9px 16px"), 12: (6, 112, 16, "8px 12px")}


def slide_group(d):
    hero, rest = d["icons"][0], d["icons"][1:]
    cols, size, fs, pad = GRID[len(rest)]
    first, second = rest[:cols], rest[cols:]
    light = "".join(f'<li class="tile">{dot(n, "g")}<span class="b b--line-g tile-name">{escape(n)}</span></li>'
                    for n in first)
    color = "".join(f'<li class="tile">{dot(n, "w")}<span class="b b--white tile-name">{escape(n)}</span></li>'
                    for n in second)
    return (
        f'<div class="slide s-group d-{d["key"]}" style="--cols:{cols};--d:{size}px;--fs:{fs}px;--tp:{pad}">'
        + head("c", f'Иконки / {d["no"]}', d["name"], d["sub"])
        + '<div class="group"><div class="hero">'
        '<svg class="hero-flow" viewBox="0 0 632 674" preserveAspectRatio="none" aria-hidden="true"><use href="#flow"/></svg>'
        f'<span class="b b--white hero-tag">{escape(d["short"])}</span>'
        f'<span class="dot dot--w hero-dot">{ic(hero, "g")}</span>'
        f'<span class="b b--line-w hero-name">{escape(hero)}</span></div>'
        f'<div class="rows"><ul class="row row--light">{light}</ul><ul class="row row--color">{color}</ul></div>'
        "</div></div>"
    )


# ---------- Слайд 19 · Все 36 иконок ----------
def slide_all():
    legend = "".join(
        f'<span class="b b--fill-g d-{d["key"]} lg">{escape(d["short"])}<i>{len(d["icons"])}</i></span>' for d in DIRS
    )
    cells = "".join(
        f'<li class="d-{d["key"]}" title="{escape(n)}">{dot(n, "g")}</li>'
        for d in DIRS for n in THEME_ORDER[d["key"]]
    )
    return ('<div class="slide s-all">' + head("c", "36 иконок / единая система", "Город в деталях", title_cls="h1--big")
            + f'<div class="legend">{legend}</div><ul class="all">{cells}</ul></div>')


def frame(no, caption, slide_html):
    return (f'<figure class="shot" id="slide-{no}"><figcaption><span class="shot-no">Слайд {no}</span>'
            f'{escape(caption)}</figcaption><div class="frame">{slide_html}</div></figure>')


def main():
    slides = [frame("2", "План работы", slide_plan()), frame("14", "Иконки: четыре направления", slide_dirs())]
    for no, d in zip(["15", "16", "17", "18"], DIRS):
        slides.append(frame(no, d["name"], slide_group(d)))
    slides.append(frame("19", "Город в деталях", slide_all()))
    tpl = (HERE / "template.html").read_text(encoding="utf-8")
    page = tpl.replace("{{SPRITE}}", sprite()).replace("{{SLIDES}}", "\n".join(slides))
    (HERE / "index.html").write_text(page, encoding="utf-8")
    print(f"index.html: {len(page) // 1024} KB, {len(IDS)} иконок")


if __name__ == "__main__":
    main()
