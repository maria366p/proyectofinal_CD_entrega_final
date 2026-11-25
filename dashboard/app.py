# el dashboard no carga el modelo: todo lo pide a la API para que haya un solo modelo
import os
from datetime import date, datetime

import altair as alt
import pandas as pd
import requests
import streamlit as st

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")
PROVEEDORES_PATH = "data/proveedores_demo.csv"  # sintéticos: el repo es público
DECISIONES_PATH = "data/decisiones.csv"
DECISIONES_GRUPOS_PATH = "data/decisiones_grupos.csv"
META_PRECISION = 0.30  # meta del KPI de la entrega 1

st.set_page_config(page_title="Monitor de pagos duplicados", layout="wide")


@st.cache_data(ttl=300)
def cargar_cola():
    r = requests.get(f"{API_URL}/casos", params={"n": 500}, timeout=5)
    r.raise_for_status()
    cola = pd.DataFrame(r.json())
    for c in ["fecha_factura_anterior", "fecha_factura_nueva"]:
        cola[c] = pd.to_datetime(cola[c])
    cola["dias"] = (cola["fecha_factura_nueva"] - cola["fecha_factura_anterior"]).dt.days
    cola["nivel"] = pd.cut(cola["puntaje"], [-0.01, 0.5, 0.8, 1.0], labels=["bajo", "medio", "alto"]).astype(str)
    cola = cola.sort_values("puntaje", ascending=False).reset_index(drop=True)
    cola.insert(0, "caso", [f"C-{i + 1:04d}" for i in range(len(cola))])
    return cola


def api_activa():
    try:
        return requests.get(f"{API_URL}/ping", timeout=3).ok
    except requests.RequestException:
        return False


def leer(path):
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()


def guardar(path, fila):
    pd.DataFrame([fila]).to_csv(path, mode="a", header=not os.path.exists(path), index=False)


def motivos(fila):
    # mismas variables del modelo, en palabras del analista
    m = []
    dias = (pd.to_datetime(fila["fecha_factura_nueva"]) - pd.to_datetime(fila["fecha_factura_anterior"])).days
    a = str(fila["numero_factura_anterior"]).upper().replace("-", "").replace(" ", "").lstrip("0")
    b = str(fila["numero_factura_nueva"]).upper().replace("-", "").replace(" ", "").lstrip("0")
    if a == b:
        m.append("El número de factura es el mismo si se quitan guiones y espacios")
    if dias <= 7:
        m.append(f"Llegó {dias} días después de la anterior, por el mismo monto")
    elif min(abs(dias - p) for p in (30, 91, 365)) > 7:
        m.append(f"{dias} días entre facturas: no coincide con una cuota mensual ni trimestral")
    if fila["canal_anterior"] != fila["canal_nuevo"]:
        m.append(f"Cambió de canal ({fila['canal_anterior']} a {fila['canal_nuevo']})")
    if fila["metodo_anterior"] != fila["metodo_nuevo"]:
        m.append(f"Cambió el método de creación ({fila['metodo_anterior']} a {fila['metodo_nuevo']})")
    if fila["facturas_previas_proveedor"] < 50:
        m.append("Proveedor con poca historia de facturas")
    return m or ["Ningún motivo fuerte por sí solo; el puntaje sale de la combinación de variables"]


# encabezado y filtros 
st.title("Monitor de pagos y proveedores duplicados")
st.caption("Procurement S2PA · el repositorio público usa datos sintéticos (DEMO_xxx)")

if not api_activa():
    st.error(f"No hay conexión con la API en {API_URL}. Préndela con `uvicorn main:app` o con docker compose.")
    st.stop()

cola = cargar_cola()
proveedores = pd.read_csv(PROVEEDORES_PATH)
decisiones = leer(DECISIONES_PATH)

with st.sidebar:
    st.header("Filtros de la cola")
    niveles = st.multiselect("Nivel de riesgo", ["alto", "medio", "bajo"], default=["alto", "medio"])
    monedas = st.multiselect("Moneda", sorted(cola["moneda"].unique()), default=sorted(cola["moneda"].unique()))
    canales = st.multiselect("Canal de la factura nueva", sorted(cola["canal_nuevo"].unique()),
                             default=sorted(cola["canal_nuevo"].unique()))
    monto_min = st.number_input("Monto mínimo (CAD)", min_value=0, value=10000, step=5000)
    f_ini, f_fin = st.date_input("Fecha de la factura nueva",
                                 (cola["fecha_factura_nueva"].min().date(), cola["fecha_factura_nueva"].max().date()))
    solo_pendientes = st.checkbox("Ocultar casos ya revisados", value=True)
    st.divider()
    st.caption(f"API: {API_URL} · conectada")

revisados = set(decisiones["caso"]) if len(decisiones) else set()
filtro = (cola["nivel"].isin(niveles) & cola["moneda"].isin(monedas) & cola["canal_nuevo"].isin(canales)
          & (cola["monto_cad"] >= monto_min)
          & cola["fecha_factura_nueva"].between(pd.Timestamp(f_ini), pd.Timestamp(f_fin)))
if solo_pendientes:
    filtro &= ~cola["caso"].isin(revisados)
vista = cola[filtro]

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Resumen", "Cola de casos", "Proveedores", "Evaluar un par", "Seguimiento del KPI"])

#  resumen 
with tab1:
    alertas = cola[cola["puntaje"] >= 0.5]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pares puntuados", f"{len(cola):,}")
    c2.metric("Alertas (puntaje ≥ 0,5)", f"{len(alertas):,}", f"{len(alertas) / len(cola):.1%} de la cola", delta_color="off")
    c3.metric("Monto en alertas (CAD)", f"{alertas['monto_cad'].sum():,.0f}")
    c4.metric("Casos revisados", f"{len(revisados):,}", f"de {len(alertas)} alertas", delta_color="off")

    izq, der = st.columns(2)
    with izq:
        st.subheader("Distribución del puntaje")
        hist = alt.Chart(cola).mark_bar().encode(
            x=alt.X("puntaje:Q", bin=alt.Bin(maxbins=20), title="Puntaje"),
            y=alt.Y("count():Q", title="Pares"),
            color=alt.Color("nivel:N", scale=alt.Scale(domain=["alto", "medio", "bajo"],
                                                        range=["#1F3864", "#4C72B0", "#C9D6EA"]), title="Nivel"))
        st.altair_chart(hist, width="stretch")
    with der:
        st.subheader("Alertas por mes")
        por_mes = (alertas.assign(mes=alertas["fecha_factura_nueva"].dt.to_period("M").dt.to_timestamp())
                   .groupby("mes").agg(alertas=("caso", "size"), monto=("monto_cad", "sum")).reset_index())
        linea = alt.Chart(por_mes).mark_line(point=True).encode(
            x=alt.X("mes:T", title="Mes"), y=alt.Y("alertas:Q", title="Alertas"),
            tooltip=["mes:T", "alertas:Q", alt.Tooltip("monto:Q", format=",.0f", title="Monto CAD")])
        st.altair_chart(linea, width="stretch")

    st.subheader("Proveedores con más monto en alerta")
    top_prov = (alertas.groupby("proveedor_id").agg(alertas=("caso", "size"), monto=("monto_cad", "sum"))
                .sort_values("monto", ascending=False).head(10).reset_index())
    barras = alt.Chart(top_prov).mark_bar(color="#4C72B0").encode(
        x=alt.X("monto:Q", title="Monto en alerta (CAD)"), y=alt.Y("proveedor_id:N", sort="-x", title=None),
        tooltip=["proveedor_id", "alertas", alt.Tooltip("monto:Q", format=",.0f")])
    st.altair_chart(barras, width="stretch")

# cola 
with tab2:
    st.subheader(f"Cola priorizada · {len(vista):,} casos con los filtros")
    st.dataframe(
        vista[["caso", "proveedor_id", "fecha_factura_anterior", "fecha_factura_nueva", "dias", "monto_cad",
               "moneda", "canal_nuevo", "puntaje", "nivel"]],
        hide_index=True, width="stretch", height=330,
        column_config={
            "puntaje": st.column_config.ProgressColumn("Puntaje", min_value=0, max_value=1, format="%.2f"),
            "monto_cad": st.column_config.NumberColumn("Monto (CAD)", format="%,.0f"),
            "fecha_factura_anterior": st.column_config.DateColumn("Factura anterior"),
            "fecha_factura_nueva": st.column_config.DateColumn("Factura nueva"),
            "dias": "Días", "canal_nuevo": "Canal", "proveedor_id": "Proveedor", "caso": "Caso", "moneda": "Moneda", "nivel": "Nivel"})
    st.download_button("Descargar la cola filtrada (CSV)", vista.to_csv(index=False).encode("utf-8"),
                       "cola_filtrada.csv", "text/csv")

    if len(vista):
        st.divider()
        caso = st.selectbox("Revisar un caso", vista["caso"])
        fila = vista[vista["caso"] == caso].iloc[0]
        st.metric("Puntaje del caso", f"{fila['puntaje']:.2f}", f"nivel {fila['nivel']}", delta_color="off")
        a, b = st.columns(2)
        for col, lado, otro, titulo in [(a, "anterior", "anterior", "Factura anterior"), (b, "nueva", "nuevo", "Factura nueva")]:
            with col.container(border=True):
                st.markdown(f"**{titulo}**")
                st.write(f"Número: {fila[f'numero_factura_{lado}']}")
                st.write(f"Fecha: {fila[f'fecha_factura_{lado}'].date()}")
                st.write(f"Canal: {fila[f'canal_{otro}']} · Método: {fila[f'metodo_{otro}']}")
                st.write(f"Monto: {fila['monto_cad']:,.2f} CAD ({fila['moneda']})")
        st.markdown("**Por qué salió en la cola**")
        for mot in motivos(fila):
            st.write("- " + mot)
        with st.form("decision"):
            # la decisión del analista se guarda porque es la etiqueta real para reentrenar
            decision = st.radio("Decisión del analista", ["Pago doble confirmado", "Cobro legítimo", "No se puede saber"],
                                horizontal=True)
            recuperable = st.number_input("Monto a recuperar (CAD), si es pago doble", min_value=0.0,
                                          value=float(fila["monto_cad"]))
            nota = st.text_input("Comentario")
            if st.form_submit_button("Guardar decisión"):
                guardar(DECISIONES_PATH, {"fecha_registro": datetime.now().isoformat(timespec="seconds"), "caso": caso,
                                          "proveedor_id": fila["proveedor_id"], "puntaje": fila["puntaje"],
                                          "monto_cad": fila["monto_cad"], "decision": decision,
                                          "monto_recuperable": recuperable if decision == "Pago doble confirmado" else 0,
                                          "comentario": nota})
                st.success("Decisión guardada.")

#  proveedores
with tab3:
    grupos = (proveedores.groupby("grupo")
              .agg(llaves=("proveedor_id", "size"), entidad=("entidad", "first"),
                   similitud_min=("similitud_nombre", "min"), gasto_aprobado=("gasto_aprobado", "sum"))
              .sort_values("gasto_aprobado", ascending=False).reset_index())
    dec_g = leer(DECISIONES_GRUPOS_PATH)
    confirmados = dec_g[dec_g["decision"] == "Misma empresa"]["grupo"].unique() if len(dec_g) else []
    c1, c2, c3 = st.columns(3)
    c1.metric("Grupos candidatos", len(grupos))
    c2.metric("Gasto sin validar (CAD)", f"{grupos.loc[~grupos['grupo'].isin(confirmados), 'gasto_aprobado'].sum():,.0f}")
    c3.metric("Gasto consolidado validado (CAD)", f"{grupos.loc[grupos['grupo'].isin(confirmados), 'gasto_aprobado'].sum():,.0f}")
    st.caption("El gasto solo pasa a consolidado cuando el analista confirma que las llaves son la misma empresa.")

    izq, der = st.columns([3, 2])
    with izq:
        st.subheader("Grupos con más gasto")
        st.altair_chart(alt.Chart(grupos.head(15)).mark_bar(color="#4C72B0").encode(
            x=alt.X("gasto_aprobado:Q", title="Gasto aprobado (CAD)"), y=alt.Y("grupo:N", sort="-x", title=None),
            tooltip=["grupo", "llaves", alt.Tooltip("gasto_aprobado:Q", format=",.0f")]), width="stretch")
    with der:
        st.subheader("Revisar un grupo")
        g = st.selectbox("Grupo", grupos["grupo"])
        st.dataframe(proveedores[proveedores["grupo"] == g][["proveedor_id", "entidad", "similitud_nombre", "gasto_aprobado"]],
                     hide_index=True, width="stretch")
        with st.form("grupo"):
            dec = st.radio("¿Son la misma empresa?", ["Misma empresa", "Empresas distintas", "No se puede saber"])
            if st.form_submit_button("Guardar"):
                guardar(DECISIONES_GRUPOS_PATH, {"fecha_registro": datetime.now().isoformat(timespec="seconds"),
                                                 "grupo": g, "decision": dec})
                st.success("Guardado.")
    st.dataframe(grupos, hide_index=True, width="stretch",
                 column_config={"gasto_aprobado": st.column_config.NumberColumn("Gasto aprobado (CAD)", format="%,.0f"),
                                "similitud_min": st.column_config.NumberColumn("Similitud mínima", format="%.2f")})

# evaluar un par
with tab4:
    st.subheader("Calcular el puntaje de un par de facturas con la API")
    with st.form("par"):
        c1, c2 = st.columns(2)
        num_a = c1.text_input("Número factura anterior", "INV-2025-0418")
        num_b = c2.text_input("Número factura nueva", "INV2025-0418")
        f_a = c1.date_input("Fecha factura anterior", date(2025, 3, 10))
        f_b = c2.date_input("Fecha factura nueva", date(2025, 3, 12))
        canal_a = c1.selectbox("Canal anterior", ["csp", "sftp", "ui", "email", "otro"])
        canal_b = c2.selectbox("Canal nuevo", ["csp", "sftp", "ui", "email", "otro"], index=3)
        met_a = c1.selectbox("Método anterior", ["Supplier", "Integration", "Manual"])
        met_b = c2.selectbox("Método nuevo", ["Supplier", "Integration", "Manual"], index=2)
        monto = c1.number_input("Monto (CAD)", min_value=10000.0, value=45200.0, step=100.0)
        historia = c2.number_input("Facturas previas del proveedor", min_value=0, value=12)
        moneda = c1.selectbox("Moneda", ["CAD", "USD", "otra"])
        enviar = st.form_submit_button("Calcular puntaje")
    if enviar:
        par = {"proveedor_id": "PROV_0001", "numero_factura_anterior": num_a, "numero_factura_nueva": num_b,
               "fecha_factura_anterior": f_a.isoformat(), "fecha_factura_nueva": f_b.isoformat(),
               "canal_anterior": canal_a, "canal_nuevo": canal_b, "metodo_anterior": met_a, "metodo_nuevo": met_b,
               "moneda": moneda, "monto_cad": monto, "facturas_previas_proveedor": int(historia)}
        r = requests.post(f"{API_URL}/predict", json=[par], timeout=10)
        if r.status_code == 200:
            res = r.json()[0]
            c1, c2 = st.columns([1, 2])
            c1.metric("Probabilidad de pago doble", f"{res['probabilidad_duplicado']:.1%}", f"nivel {res['nivel']}",
                      delta_color="off")
            c1.progress(res["probabilidad_duplicado"])
            c2.markdown("**Motivos**")
            for mot in motivos(par):
                c2.write("- " + mot)
        else:
            st.error(f"La API no aceptó el par: {r.text}")

# seguimiento
with tab5:
    st.subheader("Precisión real de la cola (KPI)")
    if len(decisiones) == 0:
        st.info("Todavía no hay decisiones guardadas. Revisa casos en la pestaña Cola de casos.")
    else:
        concluyentes = decisiones[decisiones["decision"] != "No se puede saber"]
        confirmados = (concluyentes["decision"] == "Pago doble confirmado").sum()
        precision = confirmados / len(concluyentes) if len(concluyentes) else 0
        c1, c2, c3 = st.columns(3)
        c1.metric("Casos revisados", len(decisiones))
        c2.metric("Precisión confirmada", f"{precision:.0%}", f"meta {META_PRECISION:.0%}",
                  delta_color="normal" if precision >= META_PRECISION else "inverse")
        c3.metric("Monto a recuperar (CAD)", f"{decisiones['monto_recuperable'].sum():,.0f}")
        st.dataframe(decisiones, hide_index=True, width="stretch")
        st.download_button("Descargar decisiones (CSV)", decisiones.to_csv(index=False).encode("utf-8"),
                           "decisiones.csv", "text/csv")
