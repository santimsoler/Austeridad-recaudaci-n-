import numpy as np, pandas as pd, json, io, contextlib, datetime as dt

buf=io.StringIO()
with contextlib.redirect_stdout(buf):
    exec(open('d2.py').read().split('base=idx')[0])
base=idx[(2026,7)]
per=sorted(rec)
vals=[rec[p]/(1e9 if p[0]<=2020 else 1e6)*base/idx[p] for p in per]
pi=pd.PeriodIndex([f"{p[0]}-{p[1]:02d}" for p in per],freq='M')
s=pd.Series(vals,index=pi)
ls=np.log(s)

# ---------- regresores: dias habiles y Semana Santa ----------
def easter(y):
    a=y%19;b=y//100;c=y%100;d=b//4;e=b%4;f=(b+8)//25;g=(b-f+1)//3
    h=(19*a+b-d-g+15)%30;i=c//4;k=c%4;l=(32+2*e+2*i-h-k)%7
    m=(a+11*h+22*l)//451;mo=(h+l-7*m+114)//31;da=((h+l-7*m+114)%31)+1
    return dt.date(y,mo,da)

def weekdays(y,m):
    import calendar
    return sum(1 for d in range(1,calendar.monthrange(y,m)[1]+1)
               if dt.date(y,m,d).weekday()<5)

td=[];ea=[]
for p in per:
    y,m=p
    w=weekdays(y,m)
    td.append(w-21.75)                      # desvio vs promedio de largo plazo
    e=easter(y)
    # fraccion de los 7 dias previos a Pascua que caen en el mes m
    days=[e-dt.timedelta(days=k) for k in range(1,8)]
    ea.append(sum(1 for d in days if d.month==m)/7.0)
td=np.array(td); ea=np.array(ea)

# ---------- filtros ----------
def ma2x12(x):
    w=np.r_[0.5,np.ones(11),0.5]/12
    out=np.full(len(x),np.nan)
    for i in range(6,len(x)-6):
        seg=x[i-6:i+7]
        if not np.isnan(seg).any(): out[i]=(seg*w).sum()
    return out

HEND13=np.array([-0.019, -0.028, 0.0, 0.065, 0.147, 0.214, 0.24,
                 0.214, 0.147, 0.065, 0.0, -0.028, -0.019])
def henderson(x):
    out=np.full(len(x),np.nan)
    for i in range(6,len(x)-6):
        seg=x[i-6:i+7]
        if not np.isnan(seg).any(): out[i]=(seg*HEND13).sum()
    # extremos: extender con MA simple
    for i in list(range(6))+list(range(len(x)-6,len(x))):
        lo,hi=max(0,i-6),min(len(x),i+7)
        seg=x[lo:hi]; seg=seg[~np.isnan(seg)]
        if len(seg): out[i]=seg.mean()
    return out

def seas35(v):
    """filtro estacional 3x5 sobre la serie de un mes dado"""
    n=len(v); out=np.full(n,np.nan)
    ext=np.r_[v[0],v[0],v,v[-1],v[-1]]
    m5=np.array([np.nanmean(ext[i:i+5]) for i in range(n+2)])
    ext2=np.r_[m5[0],m5,m5[-1]]
    for i in range(n): out[i]=np.nanmean(ext2[i:i+3])
    return out

months=np.array([p[1] for p in per])
y=ls.values.copy()
n=len(y)

# ---------- regresion trading-day + Easter sobre serie detrended ----------
tr0=ma2x12(y)
mask=~np.isnan(tr0)
d0=y-tr0
X=np.column_stack([td,ea])
# identificar los coeficientes SOLO con variacion intra-mes (quitar media por mes)
Xc=X.copy(); dc=d0.copy()
for m in range(1,13):
    k=(months==m)&mask
    Xc[k]-=X[k].mean(0); dc[k]-=d0[k].mean()
beta=np.linalg.lstsq(Xc[mask],dc[mask],rcond=None)[0]
tdadj=X@beta
yc=y-tdadj      # serie corregida por calendario

# ---------- iteracion X-11 ----------
seas=np.zeros(n)
for it in range(4):
    x=yc-seas if it else yc
    tr=ma2x12(x) if it==0 else henderson(x)
    si=yc-tr
    # reemplazo de extremos (>2.5 sigma dentro de cada mes)
    si_c=si.copy()
    for m in range(1,13):
        k=months==m; v=si[k]
        sd=np.nanstd(v)
        if sd>0:
            bad=np.abs(v-np.nanmean(v))>2.5*sd
            v=v.copy(); v[bad]=np.nan
            # imputar con media movil de vecinos del mismo mes
            vv=pd.Series(v).interpolate(limit_direction='both').values
            si_c[k]=vv
    newseas=np.full(n,np.nan)
    for m in range(1,13):
        k=months==m
        newseas[k]=seas35(si_c[k])
    # normalizar a media anual cero
    ns=pd.Series(newseas,index=pi)
    norm=ns.groupby(ns.index.year).transform('mean')
    seas=(ns-norm).values
    seas=np.nan_to_num(seas)

sa=np.exp(yc-seas)
trend=np.exp(henderson(yc-seas))
irr=np.exp(yc-seas-np.log(trend))

print(f"Coef. dias habiles: {beta[0]*100:+.2f}% por dia habil adicional")
print(f"Coef. Semana Santa: {beta[1]*100:+.2f}% en el mes que la contiene")
print(f"\nFactores estacionales promedio (ult. 3 anios):")
fs=pd.Series(np.exp(seas),index=pi)
for m in range(1,13):
    v=fs[(fs.index.month==m)&(fs.index.year>=2024)].mean()
    print(f"  {m:02d}: {v:.3f}")

res=pd.DataFrame({'real':s.values,'sa':sa,'trend':trend,'irr':irr},index=pi)
r=res[res.index.year>=2023]
print(f"\n{'Mes':9}{'Real':>7}{'Desest.':>9}{'m/m':>8}{'Tend.':>8}")
prev=None
for i,row in r.iterrows():
    mm=f"{(row['sa']/prev-1)*100:+.1f}%" if prev else ""
    print(f"{str(i):9}{row['real']:7.2f}{row['sa']:9.2f}{mm:>8}{row['trend']:8.2f}")
    prev=row['sa']
res.to_csv('x11_result.csv')
