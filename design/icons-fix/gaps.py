"""Замер белых просветов в иконке: растр 20 px/ед., скелет белых областей,
удвоенная дистанция до чёрного = ширина просвета."""
import io, numpy as np, cairosvg
from PIL import Image
from scipy import ndimage
from skimage.morphology import skeletonize

def gap_widths(svg, lo=0.3, hi=2.5):
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=1000, output_height=1000)
    a = np.array(Image.open(io.BytesIO(png)).convert("RGBA"))[..., 3] > 127
    ys, xs = np.where(a)
    if len(xs) == 0: return np.array([])
    sub = ~a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    dt = ndimage.distance_transform_edt(sub)
    w = 2 * dt[skeletonize(sub)] / 20
    return w[(w > lo) & (w < hi)]

def report(name, svg):
    w = gap_widths(svg)
    if len(w) == 0: return f"{name[:38]:40s} —"
    h, _ = np.histogram(w, bins=[0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1, 2.5])
    return f"{name[:38]:40s} med {np.median(w):.2f}  0.3|0.6|0.9|1.2|1.5|1.8|2.1 {list(h)}"

if __name__ == "__main__":
    import json
    src = json.load(open("src/icons_export.json"))
    for k, v in src.items():
        if k in ("1256:712", "4268:5960"): continue
        print(report(v["name"], v["svg"]))
