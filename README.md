# Deteccion de pagos y proveedores duplicados en las compras del Banco

Proyecto final de MINE-4101 Ciencia de Datos Aplicada (Uniandes, 2026-20).

## Integrantes

- Jorge Acosta Villate
- Andrés Camilo Beltrán Córdoba
- Mateo Bernal Bonil
- María Paula Ospina Plazas

## Alcance

Hicimos el proyecto con el area de Procurement S2PA del Banco. Hoy las facturas de proveedores se revisan a mano y despues de pagarlas. Por lo tanto, los pagos dobles y los proveedores repetidos en el maestro se detectan tarde o no se detectan. Para esto, el producto de datos tiene tres partes:

1. Modelo. Consiste en un Random Forest que le asigna a cada par de facturas aprobadas (mismo proveedor, mismo monto, 90 dias o menos) un puntaje de riesgo de ser un cobro repetido. Ademas, tiene una agrupacion aglomerativa que junta las llaves de proveedor que parecen ser la misma empresa.
2. API REST (FastAPI). Recibe un par de facturas y devuelve el puntaje, y tambien entrega la cola de casos.
3. Dashboard (Streamlit). Muestra el resumen, la cola, los grupos de proveedores y un formulario para probar un par. Desde aqui, el analista marca si cada caso es o no un pago doble.

## Conclusiones principales

- Contra la etiqueta aproximada (una de las dos facturas fue anulada, disputada o rechazada), el Random Forest prioriza mejor que la regla de la entrega 1. En prueba tiene F1 de 0,44 contra 0,23 (McNemar p < 0,001), y el 84% de los 50 pares con puntaje mas alto tenian friccion.
- Sin embargo, el Banco reviso 30 pares y ninguno de los 24 del modelo fue un pago doble. En cambio, 7 de los 8 pares con el mismo numero de factura (al quitar signos o con un sufijo) eran facturas duplicadas y 4 se pagaron dos veces (85.914 CAD, 2 pendientes de confirmar con payments). Son pocos casos, ya que el IC 95% de la precision de la regla va de 12% a 88%, pero la diferencia con el modelo es clara. Es decir, la etiqueta aproximada mide otra cosa, dado que muchas anulaciones son correcciones.
- Por eso, la cola quedo en dos niveles: primero la regla del numero y despues el modelo, y la API y el dashboard ya trabajan asi. Ademas, la regla aplicada a todo el historico (sin la ventana ni el limite de 90 dias) encuentra 66 pares en 29 proveedores por 8,99 millones de CAD, y 49 de ellos estaban por fuera de la ventana del modelo.
- En cuanto a los proveedores, el Banco confirmo que 17 de 20 grupos son la misma empresa (5,9% del gasto queda consolidado y validado) y va a desactivar 6 llaves duplicadas que no tenia identificadas, con 1,51 millones de CAD de gasto. Las llaves con el nombre Bank of Nova Scotia son compras intragrupo, por lo tanto las excluimos.
- Revisar un caso cuesta entre 6 y 72 CAD. Con la regla del numero el valor esperado es de unos 5.000 CAD por caso, mientras que revisar pares del modelo sin la regla no recupera nada.

Todo el detalle esta en el [reporte final](Reporte_Final.pdf).

## Organizacion del repositorio

- `Reporte_Final.pdf` : reporte de la entrega final (incluye la entrega 1 corregida)
- `presentacion/` : diapositivas de la entrega 1 y de la entrega final
- `USO_IA.md` : declaracion de uso de IA
- `notebooks/01_entendimiento_datos.ipynb` : entrega 1: entendimiento y calidad de los datos (puntos 5 y 6)
- `notebooks/02_preparacion_datos.ipynb` : punto 8: preparacion, pares, etiqueta y variables
- `notebooks/03_modelado.ipynb` : puntos 9 y 10: division, 7 modelos de sklearn y una red neuronal con Keras, prueba, McNemar, bootstrapping, SHAP, hipotesis e impacto
- `notebooks/04_agrupacion_proveedores.ipynb` : agrupacion aglomerativa de proveedores
- `notebooks/05_pipeline_final.ipynb` : punto 11: pipeline final con joblib y datos sinteticos para la demo
- `api/` : API en FastAPI con el modelo guardado y su Dockerfile
- `dashboard/` : dashboard en Streamlit y su Dockerfile
- `docker-compose.yml` : levanta la API y el dashboard juntos
- `requirements.txt` : librerias para correr los notebooks

## Como correrlo

### Notebooks

```bash
pip install -r requirements.txt
```

Los datos del Banco no estan en el repo porque son confidenciales. Primero, hay que poner el archivo en `data/raw/Spend_FA_x_Transit_x_User_ID.xlsx` y la revision del Banco en `data/raw/Revision_casos_duplicados_Banco_respuesta.xlsx`, que la usan el 03 y el 04. Despues, hay que correr los notebooks en orden: 01, 02, 03, 04 y 05. El 02 crea `data/processed/pares.parquet`, que usan el 03 y el 05, y `data/processed/cola_regla_numero.parquet` con los pares de la regla del numero en todo el historico. Por ultimo, el 03 se demora unos minutos por los GridSearchCV.

### API y dashboard

```bash
docker compose up --build
```

- API: http://localhost:8000/docs
- Dashboard: http://localhost:8501

Para probar la API sola: `python api/test_request.py`.

Sin Docker:

```bash
cd api && pip install -r requirements.txt && uvicorn main:app --port 8000
cd dashboard && pip install -r requirements.txt && API_URL=http://localhost:8000 streamlit run app.py
```

## Dependencias

Python 3.13. Notebooks: pandas, numpy, matplotlib, seaborn, scipy, statsmodels, scikit-learn, tensorflow/keras, shap, levenshtein, openpyxl y pyarrow (versiones en `requirements.txt`). API: fastapi, uvicorn, scikit-learn, pandas, joblib y levenshtein. Dashboard: streamlit, altair, pandas y requests.

## Confidencialidad

Cambiamos los proveedores por seudonimos (`PROV_xxxx`) y quitamos los datos personales. Ademas, la API y el dashboard del repo funcionan con datos sinteticos (`DEMO_xxx`), que se generan en el notebook 05.

Video de la entrega final: [enlace a YouTube]
