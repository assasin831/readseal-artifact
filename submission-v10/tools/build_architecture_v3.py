"""V4 native draw.io and vector PDF, retaining the generated V3 framework.

The whole graph feeds analysis; declarations feed binding, not graph analysis.
Both read witnesses reach the read join. Source reuse never feeds output join.
"""
from pathlib import Path
import json
import math
import xml.etree.ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

ROOT=Path(__file__).resolve().parents[1]
W,H=1000,535
INK='#262B30'; MUTED='#555F65'; TEAL='#267B83'; PALE='#EDF5F5'; GRAY='#E7E9EB'
FONT='FigureSans'; BOLD='FigureSansBold'
fontdir=Path('C:/Windows/Fonts')
if fontdir.is_dir():normal,bold=fontdir/'arial.ttf',fontdir/'arialbd.ttf'
else:
    from matplotlib import font_manager
    normal=font_manager.findfont('DejaVu Sans')
    bold=font_manager.findfont(font_manager.FontProperties(family='DejaVu Sans',weight='bold'))
pdfmetrics.registerFont(TTFont(FONT,str(normal)))
pdfmetrics.registerFont(TTFont(BOLD,str(bold)))
cells=[]


def box(id,x,y,w,h,label='',fill='none',stroke=INK,size=21,bold=False,dash=False,shape='rectangle',align='center',color=INK):
    cells.append(dict(kind='box',id=id,x=x,y=y,w=w,h=h,label=label,fill=fill,stroke=stroke,
                      size=size,bold=bold,dash=dash,shape=shape,align=align,color=color))


def text(id,x,y,w,h,label,size=21,bold=False,align='left',color=INK):
    box(id,x,y,w,h,label,stroke='none',size=size,bold=bold,align=align,color=color)


def line(id,points,color=INK,dash=False,arrow=True,width=1.6):
    cells.append(dict(kind='line',id=id,points=points,color=color,dash=dash,arrow=arrow,width=width))


text('panel-a',0,0,1000,30,'(a) Derive the read boundary; bind the complete invocation',23,True)
box('whole-graph',0,50,377,113,stroke='#909A9F')
text('graph-title',12,52,340,28,'Supported child graph',21,True)
box('input',14,92,40,35,'x',fill=PALE)
box('view',82,92,65,35,'view',fill=PALE)
box('conv',176,92,69,35,'conv',fill=PALE)
box('tail',284,92,78,35,'tail',fill=GRAY)
line('graph-data1',[(54,109),(82,109)])
line('graph-data2',[(147,109),(176,109)])
line('graph-data3',[(245,109),(284,109)])
line('generated-cut',[(264,87),(264,133)],TEAL,True,False,2)
text('cut-label',111,134,258,25,'cut after last read',20.3,False,'right',TEAL)
line('entire-graph-to-analysis',[(377,110),(421,110)])
text('schemas',402,44,264,29,'Pinned operator contracts',20.3,False,'center')
line('schema-input',[(534,73),(534,87)])
box('analysis',421,87,226,50,'Read-set analysis',fill='#FFFFFF',size=21)
line('analysis-to-bind',[(647,112),(704,112)])
line('declarations-to-bind',[(629,174),(680,174),(680,142),(704,142)],color=MUTED)
text('declarations',388,147,255,49,'Declared native contracts\nand topology',20.3,False,'center',MUTED)
box('binding',704,47,296,146,stroke='#909A9F')
text('binding-title',720,54,266,28,'Checked plan',22,True)
text('binding-lines',720,85,266,97,'Code + model state\nComplete reader set\nInput publication k',21)
line('divider',[(0,213),(1000,213)],color='#C2C9CC',arrow=False,width=.8)

text('panel-b',0,224,1000,32,'(b) Return source storage before private results complete',23,True)
text('native-label',0,284,160,38,'Native engine A',21,True)
text('child-label',0,374,165,27,'Graph child C',21,True)
text('child-via',0,400,170,24,'via view adapter B',20.3,color=MUTED)
box('a-read',177,309,138,17,fill=TEAL,stroke=TEAL)
box('a-private',315,309,506,17,fill=GRAY,stroke='#8D969B')
text('a-read-label',177,279,138,26,'Shared read',20.3,align='center')
text('a-private-label',380,279,380,26,'Private work',21,align='center')
box('a-read-event',308,310,14,14,fill=TEAL,stroke=TEAL,shape='ellipse')
box('a-output-event',813,309,17,17,fill='#FFFFFF',shape='ellipse')
box('c-pending',177,397,188,17,stroke=MUTED,dash=True)
box('c-read',365,397,235,17,fill=TEAL,stroke=TEAL)
box('c-private',600,397,205,17,fill=GRAY,stroke='#8D969B')
text('pending-label',177,350,185,43,'Enrolled;\nnot submitted',20.3,align='center',color=MUTED)
text('prefix-label',365,367,235,26,'Read prefix',21,align='center')
text('suffix-label',600,367,205,26,'Private suffix',21,align='center')
box('c-read-event',593,398,14,14,fill=TEAL,stroke=TEAL,shape='ellipse')
box('c-output-event',797,397,17,17,fill='#FFFFFF',shape='ellipse')
line('a-read-to-join',[(315,328),(315,347),(600,347),(600,447)],TEAL,True,False)
line('c-read-to-join',[(600,414),(600,447)],TEAL,True,False)
box('read-join',594,447,12,12,fill=TEAL,stroke=TEAL,shape='rhombus')
text('read-join-label',422,439,161,30,'Read join',20.3,True,'right',TEAL)
line('reuse-boundary',[(600,459),(600,495)],TEAL,True,False)
line('a-output-to-join',[(830,317.5),(908,317.5),(908,447)],dash=True,arrow=False)
line('c-output-to-join',[(814,405.5),(908,405.5)],dash=True,arrow=False)
box('output-join',902,447,12,12,fill='#FFFFFF',shape='rhombus')
text('output-join-label',826,271,169,30,'Output join',20.3,True,'center')
line('output-to-publication',[(908,459),(908,472)])
box('publication',823,472,170,54,'Publish result\nof k',fill='#FFFFFF',size=20.3,bold=True)
text('source-label',0,465,165,34,'Source slot',21,True)
box('protected',177,468,423,30,'Publication k protected',fill=PALE,stroke=TEAL,size=20.3)
box('reused',600,468,205,30,'May hold k+1',stroke=TEAL,size=20.3,color=TEAL)
text('provenance-note',177,504,628,28,'Storage may change; result provenance remains k.',20.3,align='center',color=MUTED)

doc=ET.Element('mxfile',host='app.diagrams.net',type='device')
diagram=ET.SubElement(doc,'diagram',id='readseal-v4',name='Checked plan and two lifetimes')
model=ET.SubElement(diagram,'mxGraphModel',page='1',pageWidth=str(W),pageHeight=str(H),grid='1',gridSize='10')
root=ET.SubElement(model,'root');ET.SubElement(root,'mxCell',id='0');ET.SubElement(root,'mxCell',id='1',parent='0')
pdf=canvas.Canvas(str(ROOT/'figures/architecture.pdf'),pagesize=(W,H),initialFontName=FONT,invariant=1)
pdf.setTitle('ReadSeal: checked plan and two distinct completion joins')
for c in cells:
    pdf.saveState()
    if c['kind']=='line':
        pts=c['points'];color=c['color'];width=c['width']
        style=f'edgeStyle=none;rounded=0;strokeColor={color};strokeWidth={width};endArrow={"block" if c["arrow"] else "none"};dashed={int(c["dash"])};'
        connections = {'source':'output-join','target':'publication'} if c['id']=='output-to-publication' else {}
        if connections:style+='exitX=0.5;exitY=1;entryX=0.5;entryY=0;'
        node=ET.SubElement(root,'mxCell',id=c['id'],parent='1',edge='1',style=style,**connections)
        geo=ET.SubElement(node,'mxGeometry',relative='1',attrib={'as':'geometry'})
        for pos,pt in [('sourcePoint',pts[0]),('targetPoint',pts[-1])]:
            ET.SubElement(geo,'mxPoint',x=str(pt[0]),y=str(pt[1]),attrib={'as':pos})
        if len(pts)>2:
            arr=ET.SubElement(geo,'Array',attrib={'as':'points'})
            for x,y in pts[1:-1]:ET.SubElement(arr,'mxPoint',x=str(x),y=str(y))
        pdf.setStrokeColor(HexColor(color));pdf.setFillColor(HexColor(color));pdf.setLineWidth(width)
        if c['dash']:pdf.setDash(4,3)
        p=pdf.beginPath();p.moveTo(pts[0][0],H-pts[0][1])
        for x,y in pts[1:]:p.lineTo(x,H-y)
        pdf.drawPath(p)
        if c['arrow']:
            a,b=pts[-2:];t=math.atan2(b[1]-a[1],b[0]-a[0]);back=(b[0]-8*math.cos(t),b[1]-8*math.sin(t))
            pts2=[b]+[(back[0]+s*3.4*math.sin(t),back[1]-s*3.4*math.cos(t)) for s in (-1,1)]
            p=pdf.beginPath();p.moveTo(pts2[0][0],H-pts2[0][1])
            for x,y in pts2[1:]:p.lineTo(x,H-y)
            p.close();pdf.setDash();pdf.drawPath(p,fill=1,stroke=0)
    else:
        x,y,w,h=c['x'],c['y'],c['w'],c['h'];shape=c['shape'];fill=c['fill'];stroke=c['stroke']
        style=f'shape={shape};rounded=0;whiteSpace=wrap;html=0;fontFamily=Arial;fontSize={c["size"]};fontStyle={int(c["bold"])};align={c["align"]};verticalAlign=middle;fillColor={fill};strokeColor={stroke};strokeWidth=1.5;dashed={int(c["dash"])};fontColor={c["color"]};'
        node=ET.SubElement(root,'mxCell',id=c['id'],parent='1',vertex='1',value=c['label'],style=style)
        ET.SubElement(node,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
        if fill!='none':pdf.setFillColor(HexColor(fill))
        if stroke!='none':pdf.setStrokeColor(HexColor(stroke))
        pdf.setLineWidth(1.5)
        if c['dash']:pdf.setDash(4,3)
        if shape=='ellipse':
            pdf.ellipse(x,H-y-h,x+w,H-y,fill=int(fill!='none'),stroke=int(stroke!='none'))
        elif shape=='rhombus':
            pts=[(x+w/2,y),(x+w,y+h/2),(x+w/2,y+h),(x,y+h/2)]
            p=pdf.beginPath();p.moveTo(pts[0][0],H-pts[0][1])
            for px,py in pts[1:]:p.lineTo(px,H-py)
            p.close();pdf.drawPath(p,fill=int(fill!='none'),stroke=int(stroke!='none'))
        elif fill!='none' or stroke!='none':pdf.rect(x,H-y-h,w,h,fill=int(fill!='none'),stroke=int(stroke!='none'))
        font=BOLD if c['bold'] else FONT;size=c['size'];lines=c['label'].split('\n') if c['label'] else [];leading=size*1.25
        assert len(lines)*leading<=h+10,(c['id'],'text too tall')
        pdf.setFont(font,size);pdf.setFillColor(HexColor(c['color']))
        for i,label in enumerate(lines):
            width=pdfmetrics.stringWidth(label,font,size)
            assert width<=w,(c['id'],'text too wide',width,w)
            tx=x+({'left':0,'center':(w-width)/2,'right':w-width}[c['align']])
            ty=y+h/2-(len(lines)-1)*leading/2+i*leading+size*.34
            pdf.drawString(tx,H-ty,label)
    pdf.restoreState()
pdf.showPage();pdf.save();ET.indent(doc)
ET.ElementTree(doc).write(ROOT/'figures/architecture.drawio',encoding='utf-8',xml_declaration=True)
(ROOT/'figures/architecture-scene.json').write_text(json.dumps(cells,indent=2)+'\n')
print('COMPLETE:',len(cells),'native editable objects')
