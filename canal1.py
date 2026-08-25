import numpy as np,pandas as pd,datetime as dt,calendar
m=pd.read_excel('/mnt/user-data/outputs/dataset_austeridad.xlsx',sheet_name='Mensual')
m['periodo']=pd.PeriodIndex(m['periodo'],freq='M'); m=m.set_index('periodo')
m['nucleo_largo']=m[['recL_iva_dgi_real','recL_ganancias_real','recL_debcred_real','recL_segsocial_real']].sum(axis=1)
d=m[['nucleo_largo','recL_total_real','emae','emae_desest','itcrm','gasto_primario_real']].dropna()
def wd(p):
    return sum(1 for x in range(1,calendar.monthrange(p.year,p.month)[1]+1)
               if dt.date(p.year,p.month,x).weekday()<5)
d['dh']=[wd(p)-21.75 for p in d.index]
est=d[(d.index>=pd.Period('2016-01',freq='M'))&(d.index<=pd.Period('2023-12',freq='M'))]
oos=d[d.index>=pd.Period('2024-01',freq='M')]
def design(x):
    return np.column_stack([np.ones(len(x)),np.log(x['emae']),np.log(x['itcrm']),x['dh']]
                           +[(x.index.month==k).astype(float) for k in range(2,13)])
def nw(X,y,L=6):
    b=np.linalg.lstsq(X,y,rcond=None)[0];e=y-X@b;n,k=X.shape
    Xi=np.linalg.inv(X.T@X);S=X*e[:,None];M=S.T@S
    for l in range(1,L+1):
        w=1-l/(L+1);G=S[l:].T@S[:-l];M+=w*(G+G.T)
    V=Xi@M@Xi*n/(n-k)
    return b,np.sqrt(np.diag(V)),e
for nm,col in [('NUCLEO',' nucleo_largo'),('TOTAL','recL_total_real')]:
    c=col.strip()
    y=np.log(est[c].values);X=design(est)
    b,se,e=nw(X,y)
    print(f"== {nm}  (muestra 2016-2023, n={len(est)})")
    print(f"   elasticidad EMAE = {b[1]:+.3f}  (EE NW {se[1]:.3f}, t={b[1]/se[1]:.2f})")
    print(f"   elasticidad TCR  = {b[2]:+.3f}  (t={b[2]/se[2]:.2f})")
    print(f"   dias habiles     = {b[3]*100:+.2f}% (t={b[3]/se[3]:.2f})")
    print(f"   R2 = {1-e.var()/y.var():.3f}   sigma = {e.std():.4f}")
    yh=design(oos)@b; res=np.log(oos[c].values)-yh
    print(f"   residuo medio fuera de muestra 2024-2026 = {res.mean()*100:+.2f}%  (sd {res.std()*100:.2f}, t={res.mean()/(res.std()/np.sqrt(len(res))):.2f}, n={len(res)})")
    r=pd.Series(res*100,index=oos.index)
    print("   por año:", {y_: round(r[r.index.year==y_].mean(),1) for y_ in sorted(set(r.index.year))})
    print()
