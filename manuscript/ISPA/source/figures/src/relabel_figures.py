"""Relabel 'BIM + ReadSeal' as the framework name in the vector plot PDFs.
Only text inside the changed lines is removed (redaction without graphics or images);
bars, curves and all other labels are untouched. New text is set in Carlito, which is
metrically compatible with the Calibri of the original labels."""
import sys, json, numpy as np, pymupdf as fitz
SRC, DST = sys.argv[1], sys.argv[2]
REG = '/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf'
BOLD = '/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf'
NAME = 'REALBIM'
def repl(t):
    return t.replace('BIM + ReadSeal', NAME).replace('BIM hold', NAME+' hold').replace('BIM 95th', NAME+' 95th')
report = {}
def pix(page):
    pm = page.get_pixmap(dpi=300, alpha=False)
    return np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, 3)
for stem in ['fig5_delivery', 'fig6_slots', 'fig7_mixed', 'fig2_trace']:
    doc = fitz.open(f'{SRC}/{stem}.pdf'); page = doc[0]; before = pix(page)
    lines = [l for b in page.get_text('dict')['blocks'] for l in b.get('lines', [])]
    if stem == 'fig2_trace':
        edited = [l for l in lines if ''.join(s['text'] for s in l['spans']).strip() in ('BIM +', 'ReadSeal')]
    else:
        edited = [l for l in lines if any(repl(s['text']) != s['text'] for s in l['spans'])]
    assert edited, stem
    for l in edited:
        box = fitz.Rect(l['bbox'])
        if l['dir'] == (1.0, 0.0): box.y0 += box.height*.25; box.y1 -= box.height*.25
        else: box.x0 += box.width*.25; box.x1 -= box.width*.25
        page.add_redact_annot(box, fill=False, cross_out=False)
    page.apply_redactions(images=0, graphics=0, text=0)
    changes = []
    if stem == 'fig2_trace':
        size = edited[0]['spans'][0]['size']
        f = fitz.Font(fontfile=BOLD); L = f.text_length(NAME, fontsize=size)
        ox = sum(l['spans'][0]['origin'][0] for l in edited)/len(edited)
        cy = sum((l['bbox'][1]+l['bbox'][3])/2 for l in edited)/len(edited)
        page.insert_font(fontname='rbB', fontfile=BOLD)
        page.insert_text(fitz.Point(ox, cy+L/2), NAME, fontname='rbB', fontsize=size, rotate=90, color=(0, 0, 0))
        changes.append({'before': 'BIM + / ReadSeal (two lines)', 'after': NAME})
    else:
        page.insert_font(fontname='rbR', fontfile=REG)
        for l in edited:
            for sp in l['spans']:
                new = repl(sp['text'])
                page.insert_text(fitz.Point(sp['origin']), new, fontname='rbR', fontsize=sp['size']*(0.94 if 'hold' in new else 1.0), color=fitz.sRGB_to_pdf(sp['color']))
                if new != sp['text']: changes.append({'before': sp['text'], 'after': new, 'size': round(sp['size'], 2)})
    doc.subset_fonts(); doc.save(f'{DST}/{stem}.pdf', garbage=3, deflate=True); doc.close()
    new = fitz.open(f'{DST}/{stem}.pdf'); after = pix(new[0])
    mask = np.zeros(before.shape[:2], bool)
    for l in edited:
        r = ((fitz.Rect(l['bbox']) + (-2, -2, 16, 2)) * fitz.Matrix(300/72, 300/72)).irect
        mask[max(0, r.y0):r.y1, max(0, r.x0):r.x1] = True
    outside = int(np.count_nonzero(np.any(before != after, axis=2) & ~mask))
    text = new[0].get_text()
    report[stem] = {'changes': changes, 'pixels_changed_outside_label_boxes_300dpi': outside,
                    'old_name_left': bool(__import__('re').search(r'(?<!REAL)BIM|ReadSeal', text))}
    new[0].get_pixmap(dpi=250, alpha=False).save(f'{stem}.png')
print(json.dumps(report, indent=1))
json.dump(report, open('relabel_report.json', 'w'), indent=1)
