import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, pandas as pd, numpy as np
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,
                     'figure.dpi':200,'font.family':'DejaVu Sans'})
AZ='#1b4f72'; GR='#b0b7bd'; RJ='#b03a2e'; VD='#1e8449'; NA='#e67e22'
m=pd.read_excel('/mnt/user-data/outputs/dataset_austeridad.xlsx',sheet_name='Mensual')
m['periodo']=pd.PeriodIndex(m['periodo'],freq='M'); m=m.set_index('periodo')

# G1 gasto vs EMAE
gp=m['gasto_primario_real'].rolling(12).sum()          # acumulado 12 meses, suaviza estacionalidad
d=pd.concat([gp,m['emae_desest']],axis=1).loc['2023-12':'2026-05'].dropna()
d.columns=['g','e']
g=d['g']/d['g'].iloc[0]*100; e=d['e']/d['e'].iloc[0]*100
fig,ax=plt.subplots(figsize=(7.2,3.5))
x=np.arange(len(d))
ax.bar(x,g,color=GR,width=.82,label='Gasto público real (acumulado 12 meses)')
ax2=ax.twinx()
ax2.plot(x,e,color=AZ,lw=2.8,label='Nivel de actividad (EMAE desest.)')
ax.set_ylabel('Gasto (dic-23 = 100)'); ax2.set_ylabel('Actividad (dic-23 = 100)')
ax.set_ylim(0,118); ax2.set_ylim(96,112)
tk=[i for i,p in enumerate(d.index) if p.month in (1,7)]
ax.set_xticks(tk); ax.set_xticklabels([f"{'ene' if d.index[i].month==1 else 'jul'}-{str(d.index[i].year)[2:]}" for i in tk],fontsize=8)
ax.set_title('El ajuste más grande, y la actividad no cayó',fontweight='bold',loc='left')
ax.annotate('el gasto cae 27%\ny se estabiliza',xy=(13,g.iloc[13]),xytext=(6.5,40),fontsize=8.5,color='#555',
            ha='center',arrowprops=dict(arrowstyle='->',color='#888',lw=.9))
ax2.annotate('la actividad termina\n7,5% arriba',xy=(len(d)-1,e.iloc[-1]),xytext=(len(d)-9.5,110.6),
             fontsize=8.5,color=AZ,ha='center',
             arrowprops=dict(arrowstyle='->',color=AZ,lw=.9,connectionstyle='arc3,rad=-0.25'))
h1,l1=ax.get_legend_handles_labels(); h2,l2=ax2.get_legend_handles_labels()
ax.legend(h1+h2,l1+l2,loc='lower center',frameon=False,ncol=2,bbox_to_anchor=(.5,-.34),fontsize=8.5)
fig.tight_layout(); fig.savefig('fig/g1.png',bbox_inches='tight'); plt.close()

# G2 resultado financiero anual
a=m.groupby(m.index.year)['resultado_financiero_real'].sum()
a=a.loc[2004:2026]
fig,ax=plt.subplots(figsize=(7.2,3.2))
ax.bar(a.index.astype(str),a.values,color=[VD if v>0 else RJ for v in a.values],width=.72)
ax.axhline(0,color='#333',lw=.8)
ax.set_ylabel('Billones de $ de julio 2026')
ax.set_title('Veintitrés años de resultado fiscal',fontweight='bold',loc='left')
ax.tick_params(axis='x',rotation=90,labelsize=7.5)
ax.annotate('último superávit\nantes de 2024: 2010',xy=(6,a.loc[2010]),xytext=(2,28),
            fontsize=8,color='#555',arrowprops=dict(arrowstyle='->',color='#888',lw=.9))
ax.text(.99,-.42,'2026: enero-julio',transform=ax.transAxes,ha='right',fontsize=7.5,color='#777')
fig.tight_layout(); fig.savefig('fig/g2.png',bbox_inches='tight'); plt.close()

# G3 barra partida
fig,ax=plt.subplots(figsize=(7.2,1.9))
ax.barh([0],[13.5],color=NA,height=.5)
ax.barh([0],[5.7],left=13.5,color=AZ,height=.5)
ax.text(6.7,0,'IVA de importaciones\ntipo de cambio y qué se importa',ha='center',va='center',color='w',fontsize=8.5,fontweight='bold')
ax.text(16.3,0,'IVA interno\nevasión',ha='center',va='center',color='w',fontsize=8.5,fontweight='bold')
ax.set_xlim(0,19.2); ax.set_yticks([]); ax.set_xlabel('Caída del ratio IVA / consumo, en puntos porcentuales (total: 19,2%)')
ax.set_title('El mismo número, abierto en dos',fontweight='bold',loc='left')
for s in ['left','bottom']: ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig('fig/g3.png',bbox_inches='tight'); plt.close()

# G4 desvíos por tributo
lab=['Ganancias','Seguridad Social','IVA interno','Débitos y Créditos']
val=[-21.9,-16.1,-4.3,-2.3]
fig,ax=plt.subplots(figsize=(7.2,2.6))
col=[GR,GR,GR,AZ]
ax.barh(lab[::-1],val[::-1],color=col[::-1],height=.62)
for i,v in enumerate(val[::-1]):
    ax.text(v-.5,i,f'{v:.1f}%',va='center',ha='right',fontsize=8.5,
            color=AZ if i==0 else '#555',fontweight='bold' if i==0 else 'normal')
ax.set_xlim(-26,2); ax.axvline(0,color='#333',lw=.8)
ax.set_xlabel('Desvío respecto de lo que predice el nivel de actividad')
ax.set_title('El impuesto que no se puede evadir',fontweight='bold',loc='left')
fig.tight_layout(); fig.savefig('fig/g4.png',bbox_inches='tight'); plt.close()

# G5 escala contrabando
fig,ax=plt.subplots(figsize=(4.6,2.9))
ax.add_patch(plt.Rectangle((0,0),1,1,color=GR))
ax.add_patch(plt.Rectangle((0,0),1,.067,color=RJ))
ax.text(.5,.55,'Recaudación aduanera\n2025',ha='center',va='center',fontsize=9.5,color='#333')
ax.text(1.06,.033,'6,7%  ←  pérdida estimada\npor contrabando',va='center',fontsize=8.5,color=RJ)
ax.set_xlim(0,2.4); ax.set_ylim(-.06,1.1); ax.axis('off')
ax.set_title('Los 2.300 millones, en escala',fontweight='bold',loc='left')
fig.tight_layout(); fig.savefig('fig/g5.png',bbox_inches='tight'); plt.close()

# G6 sectorial
sec=['Agricultura','Minería','Interm. financiera','Transporte','Comercio','Industria','Construcción']
v26=[69.9,30.5,19.5,4.8,-4.8,-11.9,-13.8]
fig,ax=plt.subplots(figsize=(7.2,3.0))
ax.barh(sec[::-1],v26[::-1],color=[VD if v>0 else RJ for v in v26[::-1]],height=.65)
ax.axvline(0,color='#333',lw=.8)
for i,v in enumerate(v26[::-1]):
    ax.text(v+(1.6 if v>0 else -1.6),i,f'{v:+.1f}%',va='center',ha='left' if v>0 else 'right',fontsize=8.5,color='#444')
ax.set_xlim(-22,80)
ax.set_xlabel('Variación 2026 vs 2023, promedio enero-mayo')
ax.set_title('El promedio esconde una recomposición profunda',fontweight='bold',loc='left')
fig.tight_layout(); fig.savefig('fig/g6.png',bbox_inches='tight'); plt.close()
print('ok')
