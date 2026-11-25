from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field


class DataModel(BaseModel):
    proveedor_id: str = Field(min_length=1, description="Seudónimo del proveedor, por ejemplo PROV_0001")
    numero_factura_anterior: Optional[str] = Field(None, description="Número de la factura anterior")
    numero_factura_nueva: Optional[str] = Field(None, description="Número de la factura nueva")
    fecha_factura_anterior: date
    fecha_factura_nueva: date
    canal_anterior: Literal["csp", "sftp", "ui", "email", "otro"]
    canal_nuevo: Literal["csp", "sftp", "ui", "email", "otro"]
    metodo_anterior: str = Field(min_length=1, description="Creation Method de la factura anterior")
    metodo_nuevo: str = Field(min_length=1, description="Creation Method de la factura nueva")
    moneda: Literal["CAD", "USD", "otra"]
    monto_cad: float = Field(ge=10000, description="Monto de la factura en CAD; el reporte solo trae facturas de 10.000 CAD o más")
    facturas_previas_proveedor: int = Field(ge=0, description="Facturas que el proveedor tenía antes de la factura nueva")

    model_config = {
        "json_schema_extra": {
            "example": {
                "proveedor_id": "PROV_0001",
                "numero_factura_anterior": "INV-2025-0418",
                "numero_factura_nueva": "INV2025-0418",
                "fecha_factura_anterior": "2025-03-10",
                "fecha_factura_nueva": "2025-03-12",
                "canal_anterior": "csp",
                "canal_nuevo": "email",
                "metodo_anterior": "Supplier",
                "metodo_nuevo": "Manual",
                "moneda": "CAD",
                "monto_cad": 45200.0,
                "facturas_previas_proveedor": 12,
            }
        }
    }
