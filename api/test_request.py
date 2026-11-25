import requests

url = "http://127.0.0.1:8000/predict"
pares = [
    # debería salir alto: mismo número sin guion y 2 días
    {"proveedor_id": "PROV_0001", "numero_factura_anterior": "INV-2025-0418", "numero_factura_nueva": "INV2025-0418",
     "fecha_factura_anterior": "2025-03-10", "fecha_factura_nueva": "2025-03-12", "canal_anterior": "csp",
     "canal_nuevo": "email", "metodo_anterior": "Supplier", "metodo_nuevo": "Manual", "moneda": "CAD",
     "monto_cad": 45200.0, "facturas_previas_proveedor": 12},
    # debería salir bajo: parece una cuota mensual
    {"proveedor_id": "PROV_0002", "numero_factura_anterior": "100231", "numero_factura_nueva": "100262",
     "fecha_factura_anterior": "2025-02-01", "fecha_factura_nueva": "2025-03-01", "canal_anterior": "sftp",
     "canal_nuevo": "sftp", "metodo_anterior": "Integration", "metodo_nuevo": "Integration", "moneda": "CAD",
     "monto_cad": 18000.0, "facturas_previas_proveedor": 2400},
]

response = requests.post(url, json=pares)
print("Respuesta:", response.json() if response.status_code == 200 else response.text)
