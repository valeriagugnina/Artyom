"""Точная векторизация рисунка: PNG → контур (potrace) → path в единицах рисунка (px).
Запуск: python3 trace.py рисунок.png выход.svg"""
import sys
import numpy as np
from PIL import Image
import potrace

def trace_png(path, thr=128, turdsize=8, alphamax=1.0, opttolerance=0.2):
    im = Image.open(path).convert("RGBA")
    a = np.array(im).astype(float)
    lum = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    ink = (lum < thr) & (a[..., 3] > 127)
    bmp = potrace.Bitmap(~ink)                                  # potracer считает заливкой False
    pth = bmp.trace(turdsize=turdsize, alphamax=alphamax, opticurve=True, opttolerance=opttolerance)
    parts = []
    for curve in pth:
        sp = curve.start_point
        d = [f"M{sp.x:.2f} {sp.y:.2f}"]
        for seg in curve.segments:
            if seg.is_corner:
                d.append(f"L{seg.c.x:.2f} {seg.c.y:.2f}L{seg.end_point.x:.2f} {seg.end_point.y:.2f}")
            else:
                d.append(f"C{seg.c1.x:.2f} {seg.c1.y:.2f} {seg.c2.x:.2f} {seg.c2.y:.2f} {seg.end_point.x:.2f} {seg.end_point.y:.2f}")
        d.append("Z"); parts.append("".join(d))
    return "".join(parts), im.size

if __name__ == "__main__":
    d, (w, h) = trace_png(sys.argv[1])
    open(sys.argv[2], "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><path d="{d}" fill="#172470" fill-rule="evenodd"/></svg>')
    print("ok", len(d))
