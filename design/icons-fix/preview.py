"""Превью: SVG-строки → PNG-лист с направляющими сетки (4/46, верх 7, база 43.1)."""
import io, cairosvg
from PIL import Image, ImageDraw

def tile(svg, S=360, guides=True, label=""):
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=S, output_height=S)
    im = Image.new("RGB", (S, S), "white")
    ic = Image.open(io.BytesIO(png)).convert("RGBA"); im.paste(ic, (0, 0), ic)
    if guides:
        d = ImageDraw.Draw(im); u = S / 50
        for v in (4, 46):
            d.line([(v * u, 0), (v * u, S)], fill=(255, 0, 120)); d.line([(0, v * u), (S, v * u)], fill=(255, 0, 120))
        d.line([(0, 43.1 * u), (S, 43.1 * u)], fill=(0, 150, 255)); d.line([(0, 7 * u), (S, 7 * u)], fill=(0, 150, 255))
        if label: d.text((6, 6), label, fill=(0, 0, 0))
    return im

def sheet(svgs, out, S=360, guides=True, small=True):
    tiles = [tile(s, S, guides) for s in svgs]
    H = S + (70 if small else 0)
    W = Image.new("RGB", (S * len(tiles) + 10 * (len(tiles) - 1), H), "white")
    for i, (t, s) in enumerate(zip(tiles, svgs)):
        x = i * (S + 10); W.paste(t, (x, 0))
        if small:
            for j, sz in enumerate((50, 32, 24)):
                sm = tile(s, sz, guides=False); W.paste(sm, (x + j * 60, S + 10))
    W.save(out)
