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
# Временные главные иконки направлений: варианты Money и Award из набора Icons (50×50)
TMP_MONEY = (
    '<g transform="translate(22 22.9) scale(2.2)"><path fill-rule="evenodd" d="M35.9 17.1V16.0C35.9 11.1 28.5 7.4 18.8 7.4'
    "C9.0 7.4 1.6 11.1 1.6 16.0L1.6 23.8C1.6 27.9 6.7 31.1 14.1 32.1L14.1 33.2C14.1 38.1 21.5 41.8 31.3 41.8"
    "C41.0 41.8 48.4 38.1 48.4 33.2L48.4 25.3C48.4 21.3 43.5 18.1 35.9 17.1ZM10.9 28.3C7.1 27.2 4.7 25.4 4.7 23.8"
    "L4.7 21.0C6.3 22.2 8.4 23.1 10.9 23.7L10.9 28.3ZM26.6 23.7C29.1 23.1 31.2 22.2 32.8 21.0V23.8C32.8 25.4 30.4 27.2 26.6 28.3"
    "L26.6 23.7ZM23.4 37.6C19.6 36.6 17.2 34.8 17.2 33.2V32.3C17.7 32.4 18.2 32.4 18.8 32.4C19.5 32.4 20.2 32.4 21.0 32.3"
    "C21.8 32.6 22.6 32.8 23.4 33.0L23.4 37.6ZM23.4 28.9C21.9 29.1 20.3 29.3 18.8 29.3C17.2 29.3 15.6 29.1 14.1 28.9"
    "L14.1 24.3C15.6 24.5 17.2 24.6 18.8 24.6C20.3 24.6 21.9 24.5 23.4 24.3L23.4 28.9ZM35.9 38.3C32.8 38.7 29.7 38.7 26.6 38.3"
    "L26.6 33.6C28.1 33.8 29.7 33.9 31.3 33.9C32.8 33.9 34.4 33.8 35.9 33.6L35.9 38.3ZM45.3 33.2C45.3 34.8 42.9 36.6 39.1 37.6"
    'L39.1 33.1C41.6 32.5 43.7 31.5 45.3 30.4V33.2Z"/></g>'
)
TMP_AWARD = (
    '<g transform="translate(22 18.7) scale(2.2)"><path d="M45.3 12.5L40.6 12.5L40.6 9.4C40.6 9.0 40.5 8.6 40.2 8.3'
    "C39.9 8.0 39.5 7.8 39.1 7.8L10.9 7.8C10.5 7.8 10.1 8.0 9.8 8.3C9.5 8.6 9.4 9.0 9.4 9.4L9.4 12.5L4.7 12.5"
    "C3.9 12.5 3.1 12.8 2.5 13.4C1.9 14.0 1.6 14.8 1.6 15.6L1.6 18.8C1.6 20.8 2.4 22.8 3.9 24.3C4.6 25.0 5.4 25.6 6.4 26.0"
    "C7.3 26.4 8.3 26.6 9.4 26.6H10.1C11.0 29.5 12.8 32.1 15.1 34.0C17.5 35.9 20.4 37.1 23.4 37.4L23.4 42.2L18.8 42.2"
    "C18.3 42.2 17.9 42.4 17.6 42.6C17.4 42.9 17.2 43.3 17.2 43.8C17.2 44.2 17.4 44.6 17.6 44.9C17.9 45.1 18.3 45.3 18.8 45.3"
    "L31.3 45.3C31.7 45.3 32.1 45.1 32.4 44.9C32.6 44.6 32.8 44.2 32.8 43.8C32.8 43.3 32.6 42.9 32.4 42.6C32.1 42.4 31.7 42.2 31.3 42.2"
    "L26.6 42.2L26.6 37.4C32.8 36.8 38.0 32.4 39.9 26.6L40.6 26.6C42.7 26.6 44.7 25.7 46.1 24.3C47.6 22.8 48.4 20.8 48.4 18.8"
    "L48.4 15.6C48.4 14.8 48.1 14.0 47.5 13.4C46.9 12.8 46.1 12.5 45.3 12.5ZM9.4 23.4C8.1 23.4 6.9 22.9 6.1 22.1"
    "C5.2 21.2 4.7 20.0 4.7 18.8L4.7 15.6L9.4 15.6L9.4 21.9C9.4 22.4 9.4 22.9 9.5 23.4H9.4ZM45.3 18.8C45.3 20.0 44.8 21.2 43.9 22.1"
    'C43.1 22.9 41.9 23.4 40.6 23.4H40.5C40.6 22.9 40.6 22.3 40.6 21.7L40.6 15.6L45.3 15.6L45.3 18.8Z"/></g>'
)

DIRS = [
    {
        "key": "main", "short": "Основное", "name": "Основное направление",
        "sub": "Городская жизнь и общие ценности", "no": "01", "main": "mark",
        "icons": ["Активный город", "Общественные пространства", "Уличные события", "Зелёный город",
                  "Городские сообщества", "Принадлежность", "Участие"],
    },
    {
        "key": "inv", "short": "Инвестиции", "name": "Инвестиции и деловая среда",
        "sub": "Возможности территории и развитие экономики", "no": "02", "main": "tmp-money",
        "icons": ["Логистический коридор", "Сельское хозяйство", "Промышленное производство",
                  "Жилищное строительство", "Богатые природные ресурсы", "Инвестиционные площадки"],
    },
    {
        "key": "tour", "short": "Туризм", "name": "Туризм и имидж города",
        "sub": "История, природа и впечатления", "no": "03", "main": None,
        "icons": ["Купцы Колмаковы", "Колмаковский пряник", "Планёры", "Санатории", "Гостевые домики",
                  "Гостиницы", "Термальные источники", "Краеведческий музей", "Свято-Георгиевский храм",
                  "Колмаковский парк", "Центральный парк", "Парк Машиностроителей", "Фестиваль змеев"],
    },
    {
        "key": "youth", "short": "Молодёжь", "name": "Молодёжь и карьера",
        "sub": "Энергия, участие и движение вперёд", "no": "04", "main": "tmp-award",
        "icons": ["Площадка для роста", "Личный рост", "Карьера", "Спорт", "Момент победы", "Коворкинги",
                  "Наставники", "Поддержка инициатив", "Движение первых", "Волонтёры"],
    },
]

# Иконки туризма, нарисованные по фотографиям (элеватор ещё рисуется)
PHOTO_BASED = ["Краеведческий музей", "Купцы Колмаковы", "Колмаковский пряник", "Парк Машиностроителей",
               "Свято-Георгиевский храм", "Центральный парк", "Элеватор"]

ALL_ICONS = [n for d in DIRS for n in d["icons"]]
IDS = {name: f"i{n:02d}" for n, name in enumerate(ALL_ICONS, 1)}
GROUP = {n: d["key"] for d in DIRS for n in d["icons"]}


def strip(svg):
    body = re.sub(r"^<svg[^>]*>|</svg>$", "", svg.strip())
    return re.sub(r"<defs>.*?</defs>", "", body, flags=re.S)


def sprite():
    out = []
    for name, sid in IDS.items():
        body = SPORT if name == "Спорт" else re.sub(r'\s(fill|clip-path)="[^"]*"', "", strip(A[name]))
        out.append(f'<symbol id="{sid}" viewBox="0 0 154 154">{body}</symbol>')
    logo = re.sub(r'\sclip-path="[^"]*"', "", strip(A["logo"]))
    mark = re.search(r'<path d="([^"]*)" fill="url\(#[^)]*\)"', logo).group(1)
    out.append(f'<symbol id="mark" viewBox="0 0 154 154"><g transform="translate(22 31.5) scale(1.45)">'
               f'<path d="{mark}"/></g></symbol>')
    out.append(f'<symbol id="tmp-money" viewBox="0 0 154 154">{TMP_MONEY}</symbol>')
    out.append(f'<symbol id="tmp-award" viewBox="0 0 154 154">{TMP_AWARD}</symbol>')
    logo = logo.replace('fill="#151F6D"', 'style="fill:var(--lt)"')
    logo = re.sub(r'fill="url\(#[^)]*\)"', 'style="fill:var(--lm)"', logo)
    out.append(f'<symbol id="logo" viewBox="0 0 330 63">{logo}</symbol>')
    shape = re.sub(r'\sfill="url\(#[^)]*\)"', "", strip(A["shapeValeria"]))
    out.append(f'<symbol id="flow" viewBox="0 0 632 674">{shape}</symbol>')
    air = strip(A["airflow"]).replace(' fill="white"', "")
    out.append(f'<symbol id="air" viewBox="0 0 1020 1080">{air}</symbol>')
    # градиенты иконок — как в исходной системе; у основного и инвестиций одинаковый
    grads = {
        "blue": ["#003DA5", "#2CD5C4", "#00A9E0"],
        "tour": ["#00843D", "#47D7AC", "#DDF314"],
        "youth": ["#E4002B", "#FFC851", "#FF6900"],
    }
    for key, (a, b, c) in grads.items():
        out.append(
            f'<linearGradient id="gr-{key}" x1="0" y1="1" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{a}"/><stop offset=".35" stop-color="{b}"/>'
            f'<stop offset=".7" stop-color="{c}"/></linearGradient>'
        )
    return '<svg class="sprite" aria-hidden="true" focusable="false"><defs>' + "".join(out) + "</defs></svg>"


def ic(ref, label, cls=""):
    return (f'<svg class="ic {cls}" viewBox="0 0 154 154" role="img" aria-label="{escape(label)}">'
            f'<use href="#{ref}"/></svg>')


def icon(name, cls=""):
    return ic(IDS[name], name, cls)


def main_icon(d):
    """Главная иконка направления в белом круге; для туризма — заглушка."""
    if d["main"] is None:
        return '<span class="dot dot--w"><span class="tbd">иконка<br>в работе</span></span>'
    return f'<span class="dot dot--w">{ic(d["main"], "Главная иконка: " + d["short"])}</span>'


def logo(variant):
    return (f'<svg class="logo logo--{variant}" viewBox="0 0 330 63" role="img" aria-label="Заводоуковск">'
            '<use href="#logo"/></svg>')


def head(tag, title, sub=None, tag_cls="tag"):
    parts = [logo("c"), f'<span class="b {tag_cls}">{escape(tag)}</span>',
             f'<h2 class="h1">{escape(title)}</h2>']
    if sub:
        parts.append(f'<p class="sub">{escape(sub)}</p>')
    return "".join(parts)


# ---------- Слайд 2 · План работы ----------
STAGES = [
    ("01", "Исследование", ["Анализ текущего бренда", "Обсуждение редизайна", "Утверждение носителей",
                            "Список и стилистика иконок"],
     "Согласованы направление редизайна, список иконок и носители"),
    ("02", "Логотип", ["Редизайн логотипа", "Обновление системы фирстиля", "Утверждение результата"],
     "Обновлённый логотип и основа фирменного стиля"),
    ("03", "Фирменный стиль", ["Набор иконок · 30 шт.", "Презентация фирстиля", "7–8 носителей",
                               "Утверждение результата"],
     "Система иконок, фирменная графика и носители"),
    ("04", "Передача", ["Финальные правки", "Обновление брендбука", "Папка со всеми материалами"],
     "Брендбук и все материалы бренда в одной папке"),
]


def slide_plan():
    cards = []
    for no, title, tasks, result in STAGES:
        now = " is-now" if no == "03" else ""
        items = "".join(f'<li class="b step">{escape(t)}</li>' for t in tasks)
        cards.append(
            f'<li class="card{now}"><span class="card-no">{no}</span>'
            f'<h3 class="card-title">{escape(title)}</h3>'
            f'<ul class="steps">{items}</ul>'
            f'<div class="result"><span class="result-label">Результат</span>'
            f'<p>{escape(result)}</p></div></li>'
        )
    return (
        '<div class="slide s-plan">'
        '<svg class="air" viewBox="0 0 1020 1080" aria-hidden="true"><use href="#air"/></svg>'
        + logo("w")
        + '<span class="b tag tag--w">Сейчас: 3 этап</span>'
        '<h2 class="h1 h1--plan">План работы</h2>'
        f'<ol class="cards">{"".join(cards)}</ol></div>'
    )


# ---------- Слайд 14 · Четыре направления ----------
def slide_dirs():
    rows = []
    for d in DIRS:
        themes = "".join(f'<li class="b chip">{icon(n, "ic-" + d["key"])}<span>{escape(n)}</span></li>'
                         for n in d["icons"])
        rows.append(
            f'<section class="dir d-{d["key"]}">'
            f'<div class="b dir-pill">{main_icon(d)}'
            f'<span class="dir-txt"><b>{escape(d["short"])}</b><small>{escape(d["sub"])}</small></span></div>'
            f'<ul class="chips">{themes}</ul></section>'
        )
    return ('<div class="slide s-dirs">' + head("Темы и образы города", "Иконки: четыре направления")
            + f'<div class="dirs">{"".join(rows)}</div></div>')


# ---------- Слайды 15–18 · Иконки по направлениям ----------
def split_rows(items, cols):
    n_rows = -(-len(items) // cols)
    base, extra = divmod(len(items), n_rows)
    rows, i = [], 0
    for r in range(n_rows):
        take = base + (1 if r < extra else 0)
        rows.append(items[i:i + take])
        i += take
    return rows


DOT_BY_ROWS = {2: 168, 3: 128, 4: 92}


def tile(name, key):
    return (f'<li class="tile"><span class="dot dot--soft">{icon(name, "ic-" + key)}</span>'
            f'<span class="b chip chip--label">{escape(name)}</span></li>')


def slide_group(d):
    cols = 3 if len(d["icons"]) == 6 else 4
    rows = split_rows(d["icons"], cols)
    grid = "".join(f'<ul class="grid-row">{"".join(tile(n, d["key"]) for n in r)}</ul>' for r in rows)
    return (
        f'<div class="slide s-group d-{d["key"]}" style="--cols:{cols};--d:{DOT_BY_ROWS[len(rows)]}px">'
        + head(f'Иконки / {d["no"]}', d["name"], d["sub"])
        + '<div class="group"><div class="hero">'
        '<svg class="hero-flow" viewBox="0 0 632 674" preserveAspectRatio="xMidYMid slice" aria-hidden="true">'
        '<use href="#flow"/></svg>'
        f'<span class="b hero-tag">{escape(d["short"])}</span>'
        f'<div class="hero-dot">{main_icon(d)}</div>'
        '<span class="b hero-name">Главная иконка</span></div>'
        f'<div class="grid">{grid}</div></div></div>'
    )


# ---------- Слайд 17а · Туризм: иконки по фотографиям ----------
def slide_photos():
    def pair(name):
        if name in IDS:
            pic = f'<span class="dot dot--soft">{icon(name, "ic-tour")}</span>'
        else:
            pic = '<span class="dot dot--soft"><span class="tbd tbd--tour">иконка<br>в работе</span></span>'
        return (f'<li class="pair"><div class="pair-media">'
                f'<div class="photo" role="img" aria-label="Место для фото: {escape(name)}">'
                '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 4 7.2 6H4a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h16'
                'a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-3.2L15 4H9Zm3 4.5a4.5 4.5 0 1 1 0 9 4.5 4.5 0 0 1 0-9Zm0 2'
                'a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5Z"/></svg><span>фото</span></div>'
                '<svg class="arrow" viewBox="0 0 48 24" aria-hidden="true"><path d="M2 12h40m-8-8 8 8-8 8"/></svg>'
                f'{pic}</div><span class="b chip chip--label">{escape(name)}</span></li>')
    rows = split_rows(PHOTO_BASED, 4)
    body = "".join(f'<ul class="pair-row">{"".join(pair(n) for n in r)}</ul>' for r in rows)
    return ('<div class="slide s-photos d-tour">'
            + head("Иконки / 03", "Иконки по фотографиям",
                   "Узнаваемые места и традиции Заводоуковска нарисованы с реальных снимков")
            + f'<div class="pairs">{body}</div></div>')


# ---------- Слайд 19 · Все 36 иконок ----------
def slide_all():
    legend = "".join(f'<span class="b lg d-{d["key"]}">{escape(d["short"])}<i>{len(d["icons"])}</i></span>'
                     for d in DIRS)
    cells = "".join(f'<li title="{escape(n)}">{icon(n, "ic-" + GROUP[n])}</li>' for n in ALL_ICONS)
    return ('<div class="slide s-all">' + head("36 иконок / единая система", "Город в деталях")
            + f'<div class="legend">{legend}</div><ul class="all">{cells}</ul></div>')


def frame(no, caption, slide_html):
    return (f'<figure class="shot" id="slide-{no}"><figcaption><span class="shot-no">Слайд {no}</span>'
            f'{escape(caption)}</figcaption><div class="frame">{slide_html}</div></figure>')


def main():
    slides = [frame("2", "План работы", slide_plan()), frame("14", "Иконки: четыре направления", slide_dirs())]
    for no, d in zip(["15", "16", "17", "18"], DIRS):
        slides.append(frame(no, d["name"], slide_group(d)))
        if d["key"] == "tour":
            slides.append(frame("17а", "Туризм: иконки по фотографиям", slide_photos()))
    slides.append(frame("19", "Город в деталях", slide_all()))
    tpl = (HERE / "template.html").read_text(encoding="utf-8")
    page = tpl.replace("{{SPRITE}}", sprite()).replace("{{SLIDES}}", "\n".join(slides))
    (HERE / "index.html").write_text(page, encoding="utf-8")
    print(f"index.html: {len(page) // 1024} KB, {len(IDS)} иконок, {len(slides)} слайдов")


if __name__ == "__main__":
    main()
