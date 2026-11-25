import re

import joblib
import numpy as np
import pandas as pd
from Levenshtein import ratio


def calcular_variables(pares: pd.DataFrame) -> pd.DataFrame:
    # mismas fórmulas del notebook 02: si cambian allá, hay que cambiarlas acá
    dias = (pd.to_datetime(pares["fecha_factura_nueva"]) - pd.to_datetime(pares["fecha_factura_anterior"])).dt.days
    mayus_a = pares["numero_factura_anterior"].str.upper().str.strip()
    mayus_n = pares["numero_factura_nueva"].str.upper().str.strip()
    norm_a = mayus_a.str.replace(r"[^A-Z0-9]", "", regex=True).str.lstrip("0")
    norm_n = mayus_n.str.replace(r"[^A-Z0-9]", "", regex=True).str.lstrip("0")
    return pd.DataFrame({
        "dias_entre_facturas": dias,
        "similitud_numero": [ratio(a, b) if isinstance(a, str) and isinstance(b, str) else np.nan
                             for a, b in zip(mayus_a, mayus_n)],
        "mismo_numero_normalizado": ((norm_a == norm_n) & norm_n.notna()).astype(int),
        "distancia_periodo": np.minimum.reduce([(dias - p).abs() for p in (30, 91, 365)]),
        "mismo_canal": (pares["canal_anterior"] == pares["canal_nuevo"]).astype(int),
        "mismo_metodo": (pares["metodo_anterior"] == pares["metodo_nuevo"]).astype(int),
        "log_monto": np.log10(pares["monto_cad"]),
        "log_historia_proveedor": np.log1p(pares["facturas_previas_proveedor"]),
        "tipo_canal": pares["canal_nuevo"],
        "tipo_moneda": pares["moneda"],
    })


class PredictionModel:

    def __init__(self):
        MODEL_PATH = "model/duplicados_pipeline.joblib"
        self.model = joblib.load(MODEL_PATH)

    def get_duplicate_probability(self, data: pd.DataFrame):
        return self.model.predict_proba(calcular_variables(data))[:, 1]
