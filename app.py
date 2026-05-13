from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

APPS_SCRIPT_URL = "1Yg3jvcIZofEWmYq1cwodKHwPTJyldkJL1n2CuoJTacc"

EVENT_NAME = "Demo chocolate"

# Muda isto para a hora real da tua apresentação
EVENT_START = datetime(2026, 5, 13, 12, 0, tzinfo=ZoneInfo("Europe/Lisbon"))

REFRESH_SECONDS = 10

st.set_page_config(
    page_title="Demo Chocolate",
    page_icon="🍫",
    layout="wide"
)

st.markdown(
    """
    <style>
        .stApp {
            background: #0f0f11;
            color: #e8e8f0;
        }

        .block-container {
            max-width: 1200px;
            padding-top: 2.5rem;
        }

        .hero-label {
            color: #e8ff47;
            font-size: 0.75rem;
            letter-spacing: 0.2rem;
            font-weight: 800;
            text-transform: uppercase;
        }

        .hero-title {
            font-size: 2.4rem;
            font-weight: 900;
            line-height: 1.05;
            color: #e8e8f0;
            margin-bottom: 0.2rem;
        }

        .hero-sub {
            color: #6b6b80;
            font-size: 0.95rem;
            margin-bottom: 1.4rem;
        }

        .metric-card {
            background: #1a1a1f;
            border: 1px solid #2a2a32;
            border-radius: 18px;
            padding: 18px;
        }

        .metric-label {
            color: #6b6b80;
            font-size: 0.72rem;
            letter-spacing: 0.12rem;
            text-transform: uppercase;
            font-weight: 700;
        }

        .metric-value {
            color: #e8e8f0;
            font-size: 2.2rem;
            font-weight: 900;
            margin-top: 0.25rem;
        }

        .metric-accent {
            color: #e8ff47;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <script>
        setTimeout(function() {{
            window.location.reload();
        }}, {REFRESH_SECONDS * 1000});
    </script>
    """,
    unsafe_allow_html=True
)

@st.cache_data(ttl=8)
def load_data():
    r = requests.get(APPS_SCRIPT_URL, timeout=20)
    r.raise_for_status()

    data = r.json()
    df = pd.DataFrame(data)

    if df.empty:
        return df

    df["registo_ts"] = pd.to_datetime(
        df["registo_ts"],
        errors="coerce",
        utc=True
    ).dt.tz_convert("Europe/Lisbon")

    df = df.dropna(subset=["registo_ts"])
    df = df.sort_values("registo_ts").reset_index(drop=True)

    df["minutos_relativos"] = (
        df["registo_ts"] - EVENT_START
    ).dt.total_seconds() / 60

    def classe_chegada(x):
        if x < -10:
            return "Muito cedo"
        if -10 <= x < -2:
            return "Cedo"
        if -2 <= x <= 5:
            return "Em cima da hora"
        return "Depois da hora"

    df["classe_chegada"] = df["minutos_relativos"].apply(classe_chegada)

    df["ordem"] = range(1, len(df) + 1)

    return df


df = load_data()

st.markdown("<div class='hero-label'>Demo · Apresentação</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-title'>QR do chocolate</div>", unsafe_allow_html=True)
st.markdown(
    f"<div class='hero-sub'>Evento: {EVENT_NAME} · Hora de referência: {EVENT_START.strftime('%d/%m/%Y %H:%M')} · Atualiza automaticamente</div>",
    unsafe_allow_html=True
)

if df.empty:
    st.warning("Ainda não há registos.")
    st.stop()

total = len(df)
muito_cedo = int((df["classe_chegada"] == "Muito cedo").sum())
cedo = int((df["classe_chegada"] == "Cedo").sum())
pontual = int((df["classe_chegada"] == "Em cima da hora").sum())
depois = int((df["classe_chegada"] == "Depois da hora").sum())

media = df["minutos_relativos"].mean()
mediana = df["minutos_relativos"].median()
primeiro = df["registo_ts"].min()
ultimo = df["registo_ts"].max()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>Registos</div>
            <div class='metric-value metric-accent'>{total}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>Antes da hora</div>
            <div class='metric-value'>{muito_cedo + cedo}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>Em cima da hora</div>
            <div class='metric-value'>{pontual}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c4:
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>Depois da hora</div>
            <div class='metric-value'>{depois}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")

c5, c6, c7, c8 = st.columns(4)

c5.metric("Média face à hora", f"{media:.1f} min")
c6.metric("Mediana face à hora", f"{mediana:.1f} min")
c7.metric("Primeiro registo", primeiro.strftime("%H:%M:%S"))
c8.metric("Último registo", ultimo.strftime("%H:%M:%S"))

left, right = st.columns([1.05, 1])

with left:
    fig = px.histogram(
        df,
        x="minutos_relativos",
        color="classe_chegada",
        nbins=20,
        title="Distribuição das chegadas face à hora de início",
        color_discrete_map={
            "Muito cedo": "#47ffb0",
            "Cedo": "#e8ff47",
            "Em cima da hora": "#47c8ff",
            "Depois da hora": "#ff6b47",
        }
    )

    fig.update_layout(
        paper_bgcolor="#1a1a1f",
        plot_bgcolor="#1a1a1f",
        font_color="#e8e8f0",
        legend_title_text="",
        xaxis_title="Minutos face à hora de referência",
        yaxis_title="N.º de pessoas"
    )

    st.plotly_chart(fig, use_container_width=True)

with right:
    fig2 = px.line(
        df,
        x="registo_ts",
        y="ordem",
        markers=True,
        title="Registos acumulados ao longo do tempo"
    )

    fig2.update_traces(line_color="#e8ff47")

    fig2.update_layout(
        paper_bgcolor="#1a1a1f",
        plot_bgcolor="#1a1a1f",
        font_color="#e8e8f0",
        xaxis_title="Hora do registo",
        yaxis_title="Registos acumulados"
    )

    st.plotly_chart(fig2, use_container_width=True)

with st.expander("Ver registos"):
    out = df[[
        "codigo_curto",
        "registo_ts",
        "minutos_relativos",
        "classe_chegada"
    ]].copy()

    out["registo_ts"] = out["registo_ts"].dt.strftime("%d/%m/%Y %H:%M:%S")
    out["minutos_relativos"] = out["minutos_relativos"].round(1)

    st.dataframe(
        out.sort_values("registo_ts", ascending=False),
        use_container_width=True,
        hide_index=True
    )

