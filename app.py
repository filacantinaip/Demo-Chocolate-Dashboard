from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# ============================================================
# CONFIGURAÇÃO
# ============================================================

APPS_SCRIPT_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbwf27iC8Y_iczVpY6FsFHVvPzX4v8RkLYbAnvQoC-Uhc5QXzLYIVRkZb5tV49R--ubwAw"
    "/exec?action=rows"
)

EVENT_NAME = "Demo chocolate"
TZ = ZoneInfo("Europe/Lisbon")

# Hora da apresentação: 13/05/2026 às 15:00, hora de Portugal
EVENT_START = datetime(2026, 5, 13, 15, 0, tzinfo=TZ)

REFRESH_SECONDS = 10


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Demo Chocolate",
    page_icon="🍫",
    layout="wide"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
        :root {
            --bg: #0f0f11;
            --surface: #1a1a1f;
            --border: #2a2a32;
            --text: #e8e8f0;
            --muted: #6b6b80;
            --accent: #e8ff47;
            --accent2: #47c8ff;
            --green: #47ffb0;
            --red: #ff6b47;
            --orange: #ff9f47;
        }

        .stApp {
            background: var(--bg);
            color: var(--text);
        }

        .block-container {
            max-width: 1200px;
            padding-top: 3.5rem;
            padding-bottom: 2rem;
        }

        .hero-label {
            color: var(--accent);
            font-size: 0.75rem;
            letter-spacing: 0.2rem;
            font-weight: 800;
            text-transform: uppercase;
            margin-bottom: 0.3rem;
        }

        .hero-title {
            font-size: 2.4rem;
            font-weight: 900;
            line-height: 1.05;
            color: var(--text);
            margin-bottom: 0.2rem;
        }

        .hero-sub {
            color: var(--muted);
            font-size: 0.95rem;
            margin-bottom: 1.4rem;
        }

        .metric-card {
            background: linear-gradient(180deg, rgba(26,26,31,0.98) 0%, rgba(18,18,22,0.98) 100%);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 18px;
            min-height: 112px;
            position: relative;
            overflow: hidden;
        }

        .metric-card::before {
            content: "";
            position: absolute;
            inset: 0;
            background-image:
                linear-gradient(rgba(232,255,71,0.025) 1px, transparent 1px),
                linear-gradient(90deg, rgba(232,255,71,0.025) 1px, transparent 1px);
            background-size: 26px 26px;
            pointer-events: none;
        }

        .metric-inner {
            position: relative;
            z-index: 2;
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.72rem;
            letter-spacing: 0.12rem;
            text-transform: uppercase;
            font-weight: 700;
        }

        .metric-value {
            color: var(--text);
            font-size: 2.2rem;
            font-weight: 900;
            margin-top: 0.25rem;
            line-height: 1;
        }

        .metric-accent {
            color: var(--accent);
        }

        .metric-green {
            color: var(--green);
        }

        .metric-blue {
            color: var(--accent2);
        }

        .metric-red {
            color: var(--red);
        }

        .metric-orange {
            color: var(--orange);
        }

        .small-note {
            color: var(--muted);
            font-size: 0.82rem;
            margin-top: 0.6rem;
        }

        .section-title {
            color: var(--muted);
            font-size: 0.75rem;
            letter-spacing: 0.16rem;
            text-transform: uppercase;
            font-weight: 800;
            margin-top: 1.8rem;
            margin-bottom: 0.8rem;
        }

        div[data-testid="stMetricValue"] {
            color: var(--text);
        }

        div[data-testid="stMetricLabel"] {
            color: var(--muted);
        }

        .stDataFrame {
            background: var(--surface);
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# AUTO REFRESH
# ============================================================

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


# ============================================================
# DATA LOAD
# ============================================================

@st.cache_data(ttl=8)
def load_data():
    """
    Lê os dados do Apps Script.
    Espera receber uma lista JSON de objetos, um por registo.
    """

    r = requests.get(APPS_SCRIPT_URL, timeout=20)

    if r.status_code != 200:
        st.error(f"Erro HTTP ao ler Apps Script: {r.status_code}")
        st.code(r.text[:1000])
        st.stop()

    try:
        data = r.json()
    except Exception:
        st.error("A resposta do Apps Script não é JSON.")
        st.write("URL usado:")
        st.code(APPS_SCRIPT_URL)
        st.write("Primeiros 1000 caracteres da resposta:")
        st.code(r.text[:1000])
        st.stop()

    if isinstance(data, dict):
        st.error(
            "O Apps Script respondeu com um objeto, não com uma lista de registos. "
            "Confirma se o URL termina em ?action=rows."
        )
        st.json(data)
        st.stop()

    df = pd.DataFrame(data)

    if df.empty:
        return df

    # Garante colunas esperadas, mesmo que alguma venha em falta
    expected_cols = [
        "event_id",
        "token_id",
        "codigo_curto",
        "registo_ts",
        "registo_local",
        "origem",
        "claimed",
    ]

    for col in expected_cols:
        if col not in df.columns:
            df[col] = None

    # O HTML envia registo_ts em ISO UTC via new Date().toISOString().
    # Por isso, interpretamos como UTC e convertemos para hora de Portugal.
    df["registo_ts"] = pd.to_datetime(
        df["registo_ts"],
        errors="coerce",
        utc=True
    ).dt.tz_convert(TZ)

    df = df.dropna(subset=["registo_ts"])
    df = df.sort_values("registo_ts").reset_index(drop=True)

    df["minutos_relativos"] = (
        df["registo_ts"] - EVENT_START
    ).dt.total_seconds() / 60

    def classe_chegada(x):
        if pd.isna(x):
            return "Sem hora"
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


# ============================================================
# HELPERS
# ============================================================

def metric_card(label, value, color_class=""):
    return f"""
    <div class='metric-card'>
        <div class='metric-inner'>
            <div class='metric-label'>{label}</div>
            <div class='metric-value {color_class}'>{value}</div>
        </div>
    </div>
    """


def fmt_minutes(x):
    if pd.isna(x):
        return "--"
    return f"{x:.1f} min"


# ============================================================
# LOAD DATA
# ============================================================

df = load_data()

now_pt = datetime.now(TZ)


# ============================================================
# HEADER
# ============================================================

st.markdown("<div class='hero-label'>Agent Q · Demo</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-title'>QR do chocolate</div>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div class='hero-sub'>
        Evento: {EVENT_NAME} · 
        Hora de referência: {EVENT_START.strftime('%d/%m/%Y %H:%M')} · 
        Hora atual: {now_pt.strftime('%d/%m/%Y %H:%M:%S')} · 
        Atualiza a cada {REFRESH_SECONDS}s
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# EMPTY STATE
# ============================================================

if df.empty:
    st.warning("Ainda não há registos.")
    st.stop()


# ============================================================
# METRICS
# ============================================================

total = len(df)

muito_cedo = int((df["classe_chegada"] == "Muito cedo").sum())
cedo = int((df["classe_chegada"] == "Cedo").sum())
pontual = int((df["classe_chegada"] == "Em cima da hora").sum())
depois = int((df["classe_chegada"] == "Depois da hora").sum())

antes_da_hora = muito_cedo + cedo

media = df["minutos_relativos"].mean()
mediana = df["minutos_relativos"].median()

primeiro = df["registo_ts"].min()
ultimo = df["registo_ts"].max()

percent_antes = antes_da_hora / total if total else 0
percent_pontual = pontual / total if total else 0
percent_depois = depois / total if total else 0


# ============================================================
# TOP KPI CARDS
# ============================================================

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        metric_card("Registos", total, "metric-accent"),
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        metric_card("Antes da hora", antes_da_hora, "metric-green"),
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        metric_card("Em cima da hora", pontual, "metric-blue"),
        unsafe_allow_html=True
    )

with c4:
    st.markdown(
        metric_card("Depois da hora", depois, "metric-red"),
        unsafe_allow_html=True
    )


st.write("")


# ============================================================
# SECONDARY METRICS
# ============================================================

c5, c6, c7, c8 = st.columns(4)

with c5:
    st.markdown(
        metric_card("Média face às 15h", fmt_minutes(media), "metric-accent"),
        unsafe_allow_html=True
    )

with c6:
    st.markdown(
        metric_card("Mediana face às 15h", fmt_minutes(mediana), "metric-accent"),
        unsafe_allow_html=True
    )

with c7:
    st.markdown(
        metric_card("Primeiro registo", primeiro.strftime("%H:%M:%S"), "metric-green"),
        unsafe_allow_html=True
    )

with c8:
    st.markdown(
        metric_card("Último registo", ultimo.strftime("%H:%M:%S"), "metric-blue"),
        unsafe_allow_html=True
    )


# ============================================================
# INTERPRETATION
# ============================================================

st.markdown("<div class='section-title'>Leitura rápida</div>", unsafe_allow_html=True)

if mediana < -10:
    leitura = (
        "A mediana indica que a maioria das pessoas aderiu com alguma antecedência. "
        "Para organização de eventos, isto sugere boa capacidade de mobilização antes do início."
    )
elif -10 <= mediana <= 5:
    leitura = (
        "A mediana está próxima da hora de início. "
        "Isto sugere que a adesão acontece sobretudo em cima do evento."
    )
else:
    leitura = (
        "A mediana está depois da hora de início. "
        "Isto sugere adesão tardia ou chegada progressiva após o arranque."
    )

st.markdown(
    f"""
    <div class='metric-card'>
        <div class='metric-inner'>
            <div class='metric-label'>Resumo interpretativo</div>
            <div class='small-note'>{leitura}</div>
            <div class='small-note'>
                Antes da hora: {percent_antes:.0%} · 
                Em cima da hora: {percent_pontual:.0%} · 
                Depois da hora: {percent_depois:.0%}
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CHARTS
# ============================================================

st.markdown("<div class='section-title'>Análise temporal</div>", unsafe_allow_html=True)

left, right = st.columns([1.05, 1])

with left:
    fig = px.histogram(
        df,
        x="minutos_relativos",
        color="classe_chegada",
        nbins=20,
        title="Distribuição das chegadas face às 15h",
        color_discrete_map={
            "Muito cedo": "#47ffb0",
            "Cedo": "#e8ff47",
            "Em cima da hora": "#47c8ff",
            "Depois da hora": "#ff6b47",
            "Sem hora": "#6b6b80",
        }
    )

    fig.add_vline(
        x=0,
        line_width=2,
        line_dash="dash",
        line_color="#e8e8f0",
        annotation_text="15h",
        annotation_position="top"
    )

    fig.update_layout(
        paper_bgcolor="#1a1a1f",
        plot_bgcolor="#1a1a1f",
        font_color="#e8e8f0",
        legend_title_text="",
        xaxis_title="Minutos face à hora de referência",
        yaxis_title="N.º de pessoas",
        margin=dict(l=20, r=20, t=55, b=35)
    )

    fig.update_xaxes(gridcolor="#2a2a32", zerolinecolor="#e8e8f0")
    fig.update_yaxes(gridcolor="#2a2a32")

    st.plotly_chart(fig, use_container_width=True)

with right:
    fig2 = px.line(
        df,
        x="registo_ts",
        y="ordem",
        markers=True,
        title="Registos acumulados ao longo do tempo"
    )

    fig2.update_traces(
        line_color="#e8ff47",
        marker=dict(size=7, color="#47c8ff")
    )

    fig2.add_vline(
        x=EVENT_START,
        line_width=2,
        line_dash="dash",
        line_color="#e8e8f0",
        annotation_text="15h",
        annotation_position="top"
    )

    fig2.update_layout(
        paper_bgcolor="#1a1a1f",
        plot_bgcolor="#1a1a1f",
        font_color="#e8e8f0",
        xaxis_title="Hora do registo",
        yaxis_title="Registos acumulados",
        margin=dict(l=20, r=20, t=55, b=35)
    )

    fig2.update_xaxes(gridcolor="#2a2a32")
    fig2.update_yaxes(gridcolor="#2a2a32")

    st.plotly_chart(fig2, use_container_width=True)


# ============================================================
# TABLE
# ============================================================

with st.expander("Ver registos"):
    out = df[[
        "codigo_curto",
        "registo_ts",
        "minutos_relativos",
        "classe_chegada",
        "claimed",
    ]].copy()

    out["registo_ts"] = out["registo_ts"].dt.strftime("%d/%m/%Y %H:%M:%S")
    out["minutos_relativos"] = out["minutos_relativos"].round(1)

    st.dataframe(
        out.sort_values("registo_ts", ascending=False),
        use_container_width=True,
        hide_index=True
    )
