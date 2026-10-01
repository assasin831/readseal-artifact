"""r30: relabel the hand-placed baseline that runs on REALBIM's runtime in Fig. 8 (fig7_mixed.pdf):
'Manual-checked' becomes 'REALBIM-manual'. Only the legend label is redacted (no graphics or images);
the new label is set in Carlito, metric-compatible with the Calibri of the original.
Usage: python3 relabel_r30.py <src_dir> <dst_dir>"""
import sys, json, numpy as np, pymupdf as fitz
SRC, DST = sys.argv[1], sys.argv[2]
REG = '/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf'
OLD, NEW = 'Manual-checked', 'REALBIM-manual'
def pix(page):
    pm = page.get_pixmap(dpi=300, alpha=False)
    return np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, 3)
doc = fitz.open(f'{SRC}/fig7_mixed.pdf'); page = doc[0]; before = pix(page)
lines = [l for b in page.get_text('dict')['blocks'] for l in b.get('lines', [])]
edited = [l for l in lines if ''.join(s['text'] for s in l['spans']).strip() == OLD]
assert len(edited) == 1
l = edited[0]; sp = l['spans'][0]
box = fitz.Rect(l['bbox']); box.y0 += box.height*.25; box.y1 -= box.height*.25
page.add_redact_annot(box, fill=False, cross_out=False)
page.apply_redactions(images=0, graphics=0, text=0)
page.insert_font(fontname='rbR30', fontfile=REG)
page.insert_text(fitz.Point(sp['origin']), NEW, fontname='rbR30', fontsize=sp['size'], color=fitz.sRGB_to_pdf(sp['color']))
doc.subset_fonts(); doc.save(f'{DST}/fig7_mixed.pdf', garbage=3, deflate=True); doc.close()
new = fitz.open(f'{DST}/fig7_mixed.pdf'); after = pix(new[0])
mask = np.zeros(before.shape[:2], bool)
r = ((fitz.Rect(l['bbox']) + (-2, -2, 16, 2)) * fitz.Matrix(300/72, 300/72)).irect
mask[max(0, r.y0):r.y1, max(0, r.x0):r.x1] = True
outside = int(np.count_nonzero(np.any(before != after, axis=2) & ~mask))
f = fitz.Font(fontfile=REG)
rep = {'before': OLD, 'after': NEW, 'size': round(sp['size'], 2), 'old_width_pt': round(l['bbox'][2]-l['bbox'][0], 2),
       'new_width_pt': round(f.text_length(NEW, fontsize=sp['size']), 2),
       'pixels_changed_outside_label_box_300dpi': outside, 'old_label_left': OLD in new[0].get_text()}
print(json.dumps(rep, indent=1)); json.dump({'fig7_mixed': rep}, open('relabel_r30_report.json', 'w'), indent=1)
