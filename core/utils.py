import streamlit as st
import pandas as pd

# ── utils.py ─────────────────────────────────────────────────────────────────

def portion_round(val):
    """
    Round continuous values to the nearest 0.25 precision for a pragmatic UI.
    """
    return round(val * 4) / 4


def apply_custom_css():
    """
    Inject modern, professional dark-theme CSS and utility classes.
    """
    st.markdown("""
<style>
/* ── modern typography ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: 'Inter', -apple-system, system-ui, sans-serif;
}

/* ── sidebar refinement ── */
[data-testid="stSidebar"] {
    background-color: #0d1117;
    border-right: 1px solid #30363d;
}
[data-testid="stSidebar"] h1 {
    font-size: 1.4rem !important;
    font-weight: 700;
    margin-bottom: 2rem;
    background: linear-gradient(90deg, #58a6ff, #1f6feb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ── headings ── */
h1 { color: #58a6ff; font-weight: 800; font-size: 1.8rem; letter-spacing: -0.01em; }
h2, h3 { color: #79c0ff; font-weight: 600; letter-spacing: -0.01em; }

/* ── metric cards (native) ── */
[data-testid="metric-container"] {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 1.2rem;
    transition: transform 0.2s ease;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    border-color: #58a6ff;
}

/* ── custom data cards (div-based) ── */
.food-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-left: 4px solid #58a6ff;
    border-radius: 8px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    transition: all 0.2s ease;
}
.food-card:hover {
    background: #1c2128;
    border-color: #58a6ff;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

/* ── dataframe styling ── */
[data-testid="stDataFrame"] {
    border-radius: 8px;
    border: 1px solid #30363d;
    overflow: hidden;
}

/* ── sidebar selectbox logic ── */
.stSelectbox label {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #8b949e;
}
</style>
""", unsafe_allow_html=True)


def plotly_dark_theme(fig):
    """
    Apply a consistent dark theme and margins to a Plotly figure.
    """
    fig.update_layout(
        paper_bgcolor="#161b22",
        plot_bgcolor="#0d1117",
        font=dict(color="#c9d1d9", family="Inter"),
        margin=dict(t=50, b=40, l=40, r=20),
        xaxis=dict(gridcolor="#30363d"),
        yaxis=dict(gridcolor="#30363d"),
        hoverlabel=dict(bgcolor="#161b22", font_size=12)
    )
    return fig


def render_card(title, value, description=None, color="#58a6ff"):
    """
    Render a sleek UI card with a title and value.
    """
    st.markdown(f"""
    <div class="food-card">
        <h4 style="margin:0; color:{color}; font-size:1.1rem;">{title}</h4>
        <h2 style="margin:5px 0; color:#c9d1d9;">{value}</h2>
        {f'<small style="color:#8b949e;">{description}</small>' if description else ''}
    </div>
    """, unsafe_allow_html=True)


def csv_download(df, label, filename):
    """
    Standard csv download button.
    """
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(label=label, data=csv, file_name=filename, mime='text/csv')


# ── Constants ──

RDA_VALUES = {
    "calories": 2000,
    "protein": 50,
    "fat": 65,
    "carbs": 300,
    "fiber": 25,
    "sugar": 50,
    "sodium": 2300
}

GOAL_WEIGHTS = {
    "Weight Loss": {"fiber": 0.4, "calories": 0.4, "fat": 0.2, "protein": 0.0, "carbs": 0.0},
    "Muscle Gain": {"protein": 0.5, "carbs": 0.3, "fat": 0.2, "fiber": 0.0, "calories": 0.0},
    "Maintenance": {"protein": 0.2, "fiber": 0.2, "fat": 0.2, "calories": 0.2, "carbs": 0.2}
}

ACTIVITY_FACTORS = {
    "Sedentary": 1.2,
    "Light": 1.375,
    "Moderate": 1.55,
    "Active": 1.725
}

MACRO_SPLITS = {
    "Weight Loss": {"protein": 0.30, "carbs": 0.40, "fat": 0.30, "tdee_mult": 0.80},
    "Muscle Gain": {"protein": 0.35, "carbs": 0.45, "fat": 0.20, "tdee_mult": 1.10},
    "Maintenance": {"protein": 0.25, "carbs": 0.50, "fat": 0.25, "tdee_mult": 1.00}
}
