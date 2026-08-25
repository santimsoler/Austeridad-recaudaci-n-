import re, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, Image, KeepTogether)
AZ=colors.HexColor('#1b4f72'); GRIS=colors.HexColor('#5d6d7e')
S=lambda **k: ParagraphStyle(**k)
body=S(name='b',fontName='Times-Roman',fontSize=10.2,leading=15.2,alignment=4,spaceAfter=7)
h1=S(name='h1',fontName='Helvetica-Bold',fontSize=15,leading=19,textColor=AZ,spaceBefore=20,spaceAfter=3)
h1b=S(name='h1b',fontName='Helvetica-Bold',fontSize=11,leading=14,textColor=GRIS,spaceAfter=12)
h3=S(name='h3',fontName='Helvetica-Bold',fontSize=11.2,leading=14,textColor=colors.HexColor('#222'),spaceBefore=13,spaceAfter=4)
title=S(name='t',fontName='Helvetica-Bold',fontSize=22,leading=26,textColor=AZ,spaceAfter=6)
sub=S(name='s',fontName='Times-Italic',fontSize=11,leading=15,textColor=GRIS,spaceAfter=16)
quote=S(name='q',fontName='Times-Italic',fontSize=11,leading=16,leftIndent=14,rightIndent=14,
        textColor=colors.HexColor('#1a1a1a'),spaceBefore=8,spaceAfter=10,borderPadding=6)
cap=S(name='cap',fontName='Helvetica-Oblique',fontSize=8,leading=11,textColor=GRIS,spaceAfter=12,alignment=1)
note=S(name='n',fontName='Times-Roman',fontSize=8.6,leading=12,alignment=4,spaceAfter=5)
noteh=S(name='nh',fontName='Helvetica-Bold',fontSize=12,leading=15,textColor=AZ,spaceBefore=16,spaceAfter=6)

def inl(t):
    t=t.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    t=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',t)
    t=re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)',r'<i>\1</i>',t)
    t=re.sub(r'—',' — ',t).replace('  ',' ')
    return t

FIG={'GRÁFICO 1':'fig/g1.png','GRÁFICO 2':'fig/g2.png','GRÁFICO 3':'fig/g3.png',
     'GRÁFICO 4':'fig/g4.png','GRÁFICO 5':'fig/g5.png','GRÁFICO 6':'fig/g6.png'}
W=16.0*cm

def img(path,cappy):
    from PIL import Image as PI
    w,h=PI.open(path).size
    im=Image(path,width=W,height=W*h/w)
    return [Spacer(1,4),im,Paragraph(cappy,cap)]

def table(rows):
    data=[[Paragraph(inl(c),S(name='td',fontName='Helvetica-Bold' if i==0 else 'Times-Roman',
           fontSize=8.8,leading=11.5,textColor=colors.white if i==0 else colors.black)) for c in r]
          for i,r in enumerate(rows)]
    t=Table(data,colWidths=[W/len(rows[0])]*len(rows[0]),hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),AZ),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f2f4f6')]),
        ('GRID',(0,0),(-1,-1),.3,colors.HexColor('#c9d0d6')),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),5),
        ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
    return [Spacer(1,3),t,Spacer(1,10)]

def build(md,out):
    lines=md.split('\n'); story=[]; i=0; innotes=False
    while i<len(lines):
        l=lines[i]
        if l.startswith('> ### GRÁFICO'):
            key=l.split('### ')[1].strip(); j=i+1; capt=''
            while j<len(lines) and (lines[j].startswith('>') or lines[j].strip()==''):
                m=re.match(r'>\s*\*\*"(.+?)"\*\*',lines[j])
                if m: capt=m.group(1)
                if lines[j].strip()=='' and j+1<len(lines) and not lines[j+1].startswith('>'): break
                j+=1
            story+=img(FIG[key],f'{key}. {capt}'); i=j; continue
        if l.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].startswith('|'):
                r=[c.strip() for c in lines[i].strip('|').split('|')]
                if not all(set(c)<=set('-: ') for c in r): rows.append(r)
                i+=1
            story+=table(rows); continue
        if l.startswith('> '):
            buf=[]
            while i<len(lines) and lines[i].startswith('>'):
                buf.append(lines[i][1:].strip()); i+=1
            txt=' '.join(x for x in buf if x)
            story.append(Paragraph(inl(txt),quote)); continue
        if l.startswith('# '):
            t=l[2:].strip()
            if t.startswith('NOTAS') or t.startswith('PENDIENTES'):
                innotes=True; story.append(Paragraph(inl(t),noteh))
            elif story: story.append(Paragraph(inl(t),h1))
            else: story.append(Paragraph(inl(t),title))
            i+=1; continue
        if l.startswith('## '):
            t=l[3:].strip()
            story.append(Paragraph(inl(t), h1b if story and isinstance(story[-1],Paragraph) and story[-1].style.name=='h1' else h1))
            i+=1; continue
        if l.startswith('### '):
            story.append(Paragraph(inl(l[4:].strip()),h3)); i+=1; continue
        if l.startswith('*') and l.endswith('*') and len(l)>3 and not l.startswith('**'):
            story.append(Paragraph(inl(l.strip('*')),sub)); i+=1; continue
        if l.strip()=='---':
            i+=1; continue
        if l.strip()=='':
            i+=1; continue
        buf=[l]
        i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r'^(#|\||>|---)',lines[i]):
            buf.append(lines[i]); i+=1
        story.append(Paragraph(inl(' '.join(buf)), note if innotes else body))
    doc=BaseDocTemplate(out,pagesize=A4,leftMargin=2.5*cm,rightMargin=2.5*cm,
                        topMargin=2.2*cm,bottomMargin=2.0*cm,title='La austeridad no se muerde la cola')
    fr=Frame(doc.leftMargin,doc.bottomMargin,doc.width,doc.height,id='n')
    def deco(c,d):
        c.saveState(); c.setFont('Helvetica',7.5); c.setFillColor(GRIS)
        if c.getPageNumber()>1:
            c.drawString(doc.leftMargin,A4[1]-1.5*cm,'La austeridad no se muerde la cola')
            c.setStrokeColor(colors.HexColor('#d5dbe0')); c.setLineWidth(.4)
            c.line(doc.leftMargin,A4[1]-1.65*cm,A4[0]-doc.rightMargin,A4[1]-1.65*cm)
        c.drawCentredString(A4[0]/2,1.2*cm,str(c.getPageNumber()))
        c.restoreState()
    doc.addPageTemplates([PageTemplate(id='n',frames=[fr],onPage=deco)])
    doc.build(story)
