# Deteccion de pagos y proveedores duplicados en las compras del Banco

Proyecto final de MINE-4101 Ciencia de Datos Aplicada (Uniandes, 2026-20).

## Integrantes

- Jorge Acosta Villate
- Andrés Camilo Beltrán Córdoba
- Mateo Bernal Bonil
- María Paula Ospina Plazas

## Alcance

Trabajamos con el area de Procurement S2PA del Banco. Hoy las facturas de proveedores se revisan a mano y despues de pagarlas, entonces los pagos dobles y los proveedores repetidos en el maestro se detectan tarde o no se detectan. El producto de datos tiene tres partes:

1. Modelo. Un Random Forest que le da a cada par de facturas aprobadas (mismo proveedor, mismo monto, 90 dias o menos) un puntaje de riesgo de ser un cobro repetido. Además, una agrupacion aglomerativa que junta las llaves de proveedor que parecen ser la misma empresa.
2. API REST (FastAPI) que recibe un par de facturas y devuelve el puntaje, y entrega la cola de casos.
3. Dashboard (Streamlit) con el resumen, la cola, los grupos de proveedores y un formulario para probar un par. El analista marca si cada caso es o no un pago doble.

## Conclusiones principales

- El modelo prioriza mucho mejor que la regla de la entrega 1. En prueba tiene F1 de 0,44 y precision de 0,51, y la regla tiene F1 de 0,23 y precision de 0,155 (McNemar p < 0,001). De los 50 pares de prueba con puntaje mas alto, 84% tenian friccion (IC 95% por bootstrapping: 72% a 92%).
- Ojo: esas metricas son contra una etiqueta aproximada (una de las dos facturas fue anulada, disputada o rechazada), porque el Banco no marca los duplicados. La precision real sale de la revision que le mandamos al Banco.
- Revisar la cola vale la pena. Un caso cuesta entre 6 y 72 CAD de tiempo de analista, entonces con que mas o menos 3% de los casos sean pagos dobles ya se paga la revision.
- Hay 48 grupos de llaves que serian la misma empresa, con el 10,7% del gasto aprobado, todavia sin validar.
- H1, H3 y H4 se apoyan y H2 en parte (cambiar de canal entre las dos facturas si se asocia con mas friccion). Las asociaciones son debiles.

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
- `api/` : aPI en FastAPI con el modelo guardado y su Dockerfile
- `dashboard/` : dashboard en Streamlit y su Dockerfile
- `docker-compose.yml` : levanta la API y el dashboard juntos
- `requirements.txt` : librerias para correr los notebooks

## Como correrlo

### Notebooks

```bash
pip install -r requirements.txt
```

Los datos del Banco no estan en el repo (son confidenciales). Hay que poner el archivo en `data/raw/Spend_FA_x_Transit_x_User_ID.xlsx` y correr los notebooks en orden: 01, 02, 03, 04 y 05. El 02 crea `data/processed/pares.parquet`, que usan el 03 y el 05. El 03 se demora unos minutos por los GridSearchCV.

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

Los proveedores se cambiaron por seudonimos (`PROV_xxxx`) y se quitaron los datos personales. La API y el dashboard del repo funcionan con datos sinteticos (`DEMO_xxx`) que se generan en el notebook 05.

Video de la entrega final: [enlace a YouTube]
