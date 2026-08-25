import numpy as np,pandas as pd
pan=pd.read_csv('panel_mensual.csv',index_col=0); pan.index=pd.PeriodIndex(pan.index,freq='M')
iva=pd.read_csv('iva.csv',index_col=0); iva.index=pd.PeriodIndex(iva.index,freq='M')
comp=pd.read_csv('componentes.csv',index_col=0); comp.index=pd.PeriodIndex(comp.index,freq='M')
leg=pd.read_csv('legcte.csv',index_col=0); leg.index=pd.PeriodIndex(leg.index,freq='M')
x11=pd.read_csv('x11_result.csv',index_col=0); x11.index=pd.PeriodIndex(x11.index,freq='M')
cons=pd.read_csv('consumo_trim.csv',index_col=0); cons.index=pd.PeriodIndex(cons.index,freq='Q')

rl=pd.read_csv('rec_larga_nominal.csv',index_col=0); rl.index=pd.PeriodIndex(rl.index,freq='M')
rl=rl[~rl.index.duplicated(keep='last')].sort_index()
ipcl=pd.read_csv('ipc_empalmado.csv',index_col=0).iloc[:,0]; ipcl.index=pd.PeriodIndex(ipcl.index,freq='M')
defl=(1+ipcl/100).cumprod(); defl=(defl/defl.loc['2026-07'])**-1
m=pd.DataFrame(index=pd.period_range('2004-01','2026-07',freq='M'))
m['ipc_var_largo_pct']=ipcl
m['deflactor_largo']=defl
for c,nm in [('total recursos tributarios','recL_total'),('iva dgi','recL_iva_dgi'),
             ('iva dga','recL_iva_dga'),('ganancias','recL_ganancias'),
             ('creditos y debitos en cta. cte','recL_debcred'),
             ('sistema seguridad social','recL_segsocial'),
             ('derechos de exportacion','recL_dexp'),('bienes personales','recL_bpers')]:
    m[nm+'_real']=rl[c]/1e6*defl
m['ipc_var_pct']=pan['ipc_var']
m['deflactor_jul26']=pan['defl']
m['rec_total_real']=comp['total']
m['rec_nucleo_real']=comp['nucleo']
m['rec_legcte_real']=leg['legcte']
m['rec_desest']=x11['sa']; m['rec_tendencia']=x11['trend']
for c in ['pais','blanqueo','bpers','dexp','dimp']: m['rec_'+c]=comp[c]
for c in ['iva_bruto','iva_neto','iva_dgi','iva_dga']: m[c+'_real']=iva[c]
m['emae']=pan['emae']; m['emae_desest']=pan['emae_sa']
m['supermercados_const']=pan['supermercados']
m['itcrm']=pan['itcrm']; m['empleo_registrado']=pan['empleo']
m['ripte_nivel']=pan['ripte']; m['ripte_real']=pan['ripte']*pan['defl']
fi=pd.read_csv('fiscal_mensual_nominal.csv',index_col=0); fi.index=pd.PeriodIndex(fi.index,freq='M')
ga=pd.read_csv('gasto_antes.csv',index_col=0); ga.index=pd.PeriodIndex(ga.index,freq='M')
ga['gp_h']=ga['gasto_antes']-ga['intereses'].fillna(0)
m['gasto_primario_real']=ga['gp_h']/1e6*defl
m['gasto_total_real']=ga['gasto_antes']/1e6*defl
m['intereses_real']=ga['intereses']/1e6*defl
m['gasto_corriente_real']=ga['gastos_corrientes']/1e6*defl
m['gasto_capital_real']=ga['gastos_capital']/1e6*defl
for c,nm in [('resultado_primario','resultado_primario'),
             ('resultado_financiero','resultado_financiero'),('ingresos_totales','ingresos_totales')]:
    m[nm+'_real']=fi[c]/1e6*defl
m['impulso_fiscal']=np.log(m['gasto_primario_real']).diff(12)*100
m.index.name='periodo'

q=pd.DataFrame(index=pd.period_range('2004Q1','2026Q2',freq='Q'))
q['consumo_privado_desest']=cons.iloc[:,0]
q.index.name='trimestre'

cob=[]
for c in m.columns:
    s=m[c].dropna()
    cob.append([c,'mensual',str(s.index.min()) if len(s) else 'FALTA',
                str(s.index.max()) if len(s) else 'FALTA',len(s)])
for c in q.columns:
    s=q[c].dropna(); cob.append([c,'trimestral',str(s.index.min()),str(s.index.max()),len(s)])
cobdf=pd.DataFrame(cob,columns=['serie','frecuencia','desde','hasta','n_obs'])

with pd.ExcelWriter('/mnt/user-data/outputs/dataset_austeridad.xlsx',engine='openpyxl') as w:
    cobdf.to_excel(w,sheet_name='Cobertura',index=False)
    m.reset_index().astype({'periodo':str}).to_excel(w,sheet_name='Mensual',index=False)
    q.reset_index().astype({'trimestre':str}).to_excel(w,sheet_name='Trimestral',index=False)
print(cobdf.to_string(index=False))
