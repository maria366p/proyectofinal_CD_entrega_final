import os
from typing import List

import pandas as pd
from fastapi import FastAPI, HTTPException

from data_model import DataModel
from prediction_model import PredictionModel

app = FastAPI(title="API de detección de pagos duplicados")
prediction_model = PredictionModel()
COLA_PATH = "data/cola_demo.csv"  # sintética; en el Banco sería la cola real


def nivel(p: float) -> str:
    # mismos cortes que en el dashboard
    return "alto" if p >= 0.8 else ("medio" if p >= 0.5 else "bajo")


@app.get("/")
def read_root():
    return {"message": "API de detección de pagos duplicados"}


@app.get("/ping")
def ping():
    return {"ok": True, "env": os.environ.get("ENV", "local")}


@app.post("/predict")
def make_predictions(X: List[DataModel]):
    data = pd.DataFrame([x.model_dump() for x in X])
    # si las fechas vienen al revés los días quedan negativos y el modelo no los vio nunca
    if (pd.to_datetime(data["fecha_factura_nueva"]) < pd.to_datetime(data["fecha_factura_anterior"])).any():
        raise HTTPException(status_code=422, detail="La factura nueva no puede ser anterior a la factura anterior")
    probabilidades = prediction_model.get_duplicate_probability(data)
    return [{"proveedor_id": x.proveedor_id, "probabilidad_duplicado": round(float(p), 4),
             "alerta": int(p >= 0.5), "nivel": nivel(float(p))} for x, p in zip(X, probabilidades)]


@app.get("/casos")
def casos(n: int = 50):
    if not os.path.exists(COLA_PATH):
        raise HTTPException(status_code=404, detail="No hay una cola de revisión cargada")
    cola = pd.read_csv(COLA_PATH).sort_values("puntaje", ascending=False).head(max(1, min(n, 500)))
    return cola.to_dict(orient="records")
