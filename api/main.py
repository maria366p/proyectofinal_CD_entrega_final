import os
import re
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


def numero_base(n) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(n).upper()).lstrip("0")


def mismo_numero_base(a, b) -> bool:
    # en la revisión del Banco 7 de 8 pares con esta regla eran facturas duplicadas
    a, b = numero_base(a), numero_base(b)
    if not a or not b:
        return False
    return a == b or (min(len(a), len(b)) >= 6 and (a.startswith(b) or b.startswith(a)))


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
    salida = []
    for x, p in zip(X, probabilidades):
        regla = mismo_numero_base(x.numero_factura_anterior, x.numero_factura_nueva)
        # la regla del número va primero: el par queda en nivel alto aunque el puntaje sea bajo
        salida.append({"proveedor_id": x.proveedor_id, "probabilidad_duplicado": round(float(p), 4),
                       "regla_numero": int(regla), "alerta": int(regla or p >= 0.5),
                       "nivel": "alto" if regla else nivel(float(p))})
    return salida


@app.get("/casos")
def casos(n: int = 50):
    if not os.path.exists(COLA_PATH):
        raise HTTPException(status_code=404, detail="No hay una cola de revisión cargada")
    cola = pd.read_csv(COLA_PATH)
    cola["regla_numero"] = [int(mismo_numero_base(a, b)) for a, b in zip(cola["numero_factura_anterior"], cola["numero_factura_nueva"])]
    # primero los pares con la regla del número y después por puntaje
    cola = cola.sort_values(["regla_numero", "puntaje"], ascending=False).head(max(1, min(n, 500)))
    return cola.to_dict(orient="records")
