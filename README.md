# Austeridad y recaudación en Argentina, 2004-2026

**Pablo Santiago Martínez Soler** — 2026

Datos, código y documentación del trabajo **"La austeridad no se muerde la cola"**, una verificación empírica del argumento según el cual el ajuste fiscal se autofrustra: menos gasto → menos actividad → menos recaudación → más déficit.

## Resultado principal

Para que el ajuste se autofrustre, cada peso que el Estado deja de gastar tendría que destruir **más de 4,5 pesos de actividad económica**. Ninguna estimación disponible para Argentina se acerca a ese valor: la más alta de toda la literatura local es 2,3. Y, de hecho, la actividad está 7,5% por encima de diciembre de 2023 tras la mayor contracción del gasto de la serie.

## Qué hay acá

| Carpeta | Contenido |
|---|---|
| `datos/` | Dataset consolidado (38 series mensuales, 2004-2026) y series intermedias en CSV |
| `codigo/` | Scripts de parseo, deflactado, desestacionalización y estimación |
| `documento/` | Versión técnica completa (12 pág.) y nota de divulgación (3 pág.) |
| `graficos/` | Gráficos en PNG a 200 dpi |

## Fuentes

- **ARCA** — recaudación tributaria mensual por impuesto, 2004-2026 (267 informes mensuales parseados)
- **Secretaría de Hacienda** — esquema ahorro-inversión del Sector Público Nacional, 2004-2026 (270 meses)
- **INDEC** — EMAE general y sectorial, IPC, oferta y demanda global, supermercados, trabajo registrado
- **BCRA** — índice de tipo de cambio real multilateral
- **DNIAF** — anexo estadístico de recaudación, causas de variación, escalas y deducciones de Ganancias

Todas las fuentes son públicas y de acceso libre.

## Decisiones metodológicas que conviene conocer

**Deflactor.** Todas las series están expresadas en pesos de julio de 2026. El tramo 2007-2015 usa índices de precios alternativos al oficial, por la intervención del INDEC en ese período. El resto usa IPC oficial.

**Unidades.** Las planillas anuales de ARCA de 2019 y 2020 están expresadas en miles de pesos; el resto, en millones. Si no se corrige, la serie se rompe.

**Gasto público.** Los informes en formato AIF reportan "gastos primarios después de figurativos", que duplica transferencias entre jurisdicciones. La serie de este repositorio usa **gastos antes de figurativos menos intereses**, definición homogénea disponible en los 270 meses. Con ese criterio el gasto primario real cae 27,4% en 2024, coincidiendo con lo reportado por el Ministerio de Economía.

**Desestacionalización.** X-11 implementado en numpy (media móvil 2×12, filtro estacional 3×5, reemplazo de extremos a 2,5σ, Henderson de 13 términos, corrección por días hábiles y Semana Santa). No es X-13ARIMA-SEATS: carece de extensión ARIMA, por lo que los últimos tres o cuatro puntos se revisan con datos nuevos.

**Errores estándar.** Newey-West calculados a mano. Antes de usar estos resultados en un trabajo académico conviene replicarlos con `statsmodels` o EViews.

## Limitaciones declaradas

- **Septiembre de 2007** falta en la serie fiscal. Viene en PDF y la reconstrucción no alineaba; se prefirió dejar el hueco visible antes que estimar un valor.
- **Las proyecciones locales** se estiman sobre 41 observaciones trimestrales. Los coeficientes no significativos indican falta de potencia, no ausencia de efecto.
- **La descomposición del canal de consumo** usa ventas en supermercados como proxy de consumo de bienes. El control absorbe tendencia además de composición; el resultado es indicativo, no concluyente.
- **El factor de retenciones** de la serie a legislación constante (1,25 en 2025 y 1,28 en 2026) es una aproximación propia, no una estimación oficial.
- **EMAE, supermercados, empleo y salarios** terminan en mayo de 2026; el consumo privado trimestral, en el primer trimestre de 2026.

## Cómo reproducir

```bash
pip install pandas numpy openpyxl matplotlib reportlab
python codigo/parse_rec.py        # recaudación mensual desde los informes de ARCA
python codigo/parse_all_fisc.py   # cuentas fiscales desde el esquema ahorro-inversión
python codigo/fix_gasto.py        # gasto primario con definición homogénea
python codigo/panel.py            # panel de series macro
python codigo/build_master.py     # dataset consolidado
python codigo/canal1.py           # elasticidad recaudación-actividad
python codigo/lpq.py              # proyecciones locales trimestrales
python codigo/graf.py             # gráficos
```

Los scripts de parseo requieren los archivos originales de ARCA y Hacienda, que no se incluyen por su tamaño. El dataset ya construido está en `datos/`.

## Correcciones

Los errores detectados después de la publicación se registran acá, con fecha y descripción. Si encontrás uno, abrí un issue.

*(sin correcciones al momento)*

## Licencia

Datos y documentos bajo **CC BY 4.0**: se pueden reutilizar citando la fuente. Código bajo **MIT**.

## Cita sugerida

> Martínez Soler, Pablo Santiago (2026). *La austeridad no se muerde la cola: verificación empírica del argumento del círculo vicioso fiscal en Argentina, 2004-2026.* Repositorio de datos y código. https://github.com/santimsoler/Austeridad-recaudaci-n-
