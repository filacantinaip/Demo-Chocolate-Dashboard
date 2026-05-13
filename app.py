from datetime import datetime
from zoneinfo import ZoneInfo
import random

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
            line-height: 1.5;
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

        .winner-card {
            background: radial-gradient(circle at top left, rgba(232,255,71,0.18), transparent 35%),
                        linear-gradient(180deg, rgba(26,26,31,0.98) 0%, rgba(18,18,22,0.98) 100%);
            border: 1px solid var(--accent);
            border-radius: 24px;
            padding: 28px;
            text-align: center;
            position: relative;
            overflow: hidden;
            box-shadow: 0 0 34px rgba(232,255,71,0.12);
        }

        .winner-card::before {
            content: "";
            position: absolute;
            inset: 0;
            background-image:
                linear-gradient(rgba(232,255,71,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(232,255,71,0.03) 1px, transparent 1px);
            background-size: 26px 26px;
            pointer-events: none;
        }

        .winner-inner {
            position: relative;
            z-index: 2;
        }

        .winner-label {
            color: var(--accent);
            font-size: 0.75rem;
            letter-spacing: 0.18rem;
            font-weight: 900;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        }

        .winner-title {
            color: var(--text);
            font-size: 1.6rem;
            font-weight: 900;
            margin-bottom: 0.7rem;
        }

        .winner-code {
            display: inline-block;
            background: #0b0b0d;
            color: var(--accent2);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 18px 28px;
            font-size: 3rem;
            font-weight: 900;
            letter-spacing: 0.35rem;
            margin: 0.5rem 0 0.8rem 0;
        }

        .winner-note {
            color: var(--muted);
            font-size: 0.95rem;
            line-height: 1.5;
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
# QUERY PARAMS / WINNER
# ============================================================

winner_from_url = st.query_params.get("winner", None)


# ============================================================
# AUTO REFRESH
# ============================================================
# Só faz refresh automático enquanto ainda não há vencedor.
# Depois do sorteio, paramos o refresh para o código sorteado não desaparecer.

if not winner_from_url:
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

    df["registo_ts"] = pd.to_datetime(
        df["registo_ts"],
        errors="coerce",
        utc=True
    ).dt.tz_convert(TZ)

    df = df.dropna(subset=["registo_ts"])
    df = df.sort_values("registo_ts").reset_index(drop=True)

    df["codigo_curto"] = df["codigo_curto"].astype(str).str.strip().str.upper()
    df = df[df["codigo_curto"].notna()]
    df = df[df["codigo_curto"] != ""]
    df = df[df["codigo_curto"] != "NAN"]

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


def render_winner_card(code):
    st.markdown(
        f"""
        <div class='winner-card'>
            <div class='winner-inner'>
                <div class='winner-label'>Sorteio Agent Q</div>
                <div class='winner-title'>Código vencedor</div>
                <div class='winner-code'>{code}</div>
                <div class='winner-note'>
                    Se este é o teu código, vem ter com a equipa Agent Q para receberes o chocolate.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


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
# SORTEIO
# ============================================================

st.markdown("<div class='section-title'>Sorteio do chocolate</div>", unsafe_allow_html=True)

valid_codes = sorted(df["codigo_curto"].dropna().astype(str).str.strip().str.upper().unique())
valid_codes = [c for c in valid_codes if c and c != "NAN"]

winner_code = winner_from_url

if winner_code:
    render_winner_card(winner_code)

    col_reset, col_space = st.columns([1, 3])
    with col_reset:
        if st.button("Limpar sorteio"):
            if "winner" in st.query_params:
                del st.query_params["winner"]
            st.rerun()

else:
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-inner'>
                <div class='metric-label'>Participantes elegíveis</div>
                <div class='small-note'>
                    Existem <strong>{len(valid_codes)}</strong> códigos válidos para sorteio.
                    O sorteio escolhe aleatoriamente um dos códigos registados.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    col_draw, col_info = st.columns([1, 3])

    with col_draw:
        if st.button("🎲 Sortear vencedor", use_container_width=True):
            if not valid_codes:
                st.warning("Ainda não existem códigos válidos para sortear.")
            else:
                selected = random.choice(valid_codes)
                st.query_params["winner"] = selected
                st.rerun()

    with col_info:
        st.caption(
            "Nota: depois de sorteado, o código fica fixado no URL para não desaparecer com o refresh."
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
    df_plot = df.copy()

    df_plot["registo_ts_plot"] = df_plot["registo_ts"].dt.tz_localize(None)
    event_start_plot = EVENT_START.replace(tzinfo=None)

    fig2 = px.line(
        df_plot,
        x="registo_ts_plot",
        y="ordem",
        markers=True,
        title="Registos acumulados ao longo do tempo"
    )

    fig2.update_traces(
        line_color="#e8ff47",
        marker=dict(size=7, color="#47c8ff")
    )

    fig2.add_shape(
        type="line",
        x0=event_start_plot,
        x1=event_start_plot,
        y0=0,
        y1=1,
        xref="x",
        yref="paper",
        line=dict(
            color="#e8e8f0",
            width=2,
            dash="dash"
        )
    )

    fig2.add_annotation(
        x=event_start_plot,
        y=1,
        xref="x",
        yref="paper",
        text="15h",
        showarrow=False,
        yshift=12,
        font=dict(
            color="#e8e8f0",
            size=12
        )
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
