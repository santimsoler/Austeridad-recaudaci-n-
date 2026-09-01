import numpy as np,pandas as pd
m=pd.read_excel('/mnt/user-data/outputs/dataset_austeridad.xlsx',sheet_name='Mensual')
m['periodo']=pd.PeriodIndex(m['periodo'],freq='M'); m=m.set_index('periodo')
q=pd.DataFrame({'g':m['gasto_primario_real'].groupby(m.index.asfreq('Q')).sum(),
                'y':m['emae_desest'].groupby(m.index.asfreq('Q')).mean(),
                'tc':m['itcrm'].groupby(m.index.asfreq('Q')).mean(),
                'r':m['recL_total_real'].groupby(m.index.asfreq('Q')).sum()})
q.index=pd.PeriodIndex(q.index,freq='Q'); q=q.dropna()
q=q[(q.index>=pd.Period('2016Q1',freq='Q'))&(q.index<=pd.Period('2026Q1',freq='Q'))]
lg,ly,ltc=np.log(q['g']),np.log(q['y']),np.log(q['tc'])
sh=lg.diff()*100
def nw(X,yy,L):
    b=np.linalg.lstsq(X,yy,rcond=None)[0];e=yy-X@b;n,k=X.shape
    Xi=np.linalg.inv(X.T@X);S=X*e[:,None];M=S.T@S
    for l in range(1,L+1):
        w=1-l/(L+1);G=S[l:].T@S[:-l];M+=w*(G+G.T)
    return b,np.sqrt(np.diag(np.abs(Xi@M@Xi*n/(n-k))))
L=2;H=8
print(f"Proyecciones locales trimestrales, 2016Q1-2026Q1 (n={len(q)})")
print("Respuesta acumulada del EMAE a +1% de gasto primario real\n")
print(f"{'h(trim)':>8}{'beta(%)':>10}{'EE':>8}{'t':>7}{'IC95':>18}")
for h in range(0,H+1):
    dep=(ly.shift(-h)-ly.shift(1))*100
    idx=[i for i in dep.dropna().index if i in sh.index and all((i-l) in sh.index and (i-l) in ly.index for l in range(1,L+2))]
    yy=dep.loc[idx].values
    cols=[np.ones(len(idx)),sh.loc[idx].values]
    for l in range(1,L+1):
        cols.append(sh.loc[[i-l for i in idx]].values)
        cols.append((ly.loc[[i-l for i in idx]].values-ly.loc[[i-l-1 for i in idx]].values)*100)
    cols.append((ltc.loc[idx].values-ltc.loc[[i-1 for i in idx]].values)*100)
    X=np.column_stack(cols)
    b,se=nw(X,yy,h+1)
    print(f"{h:>8}{b[1]:10.3f}{se[1]:8.3f}{b[1]/se[1]:7.2f}   [{b[1]-1.96*se[1]:6.2f},{b[1]+1.96*se[1]:6.2f}]")
