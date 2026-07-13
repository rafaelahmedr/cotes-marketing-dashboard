import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
import io
import os
import html
import json
import hashlib
import hmac
from datetime import date
from pathlib import Path

st.set_page_config(
    page_title="Cotes · Marketing Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Load logo ──────────────────────────────────────────────────────────────────
def get_logo_b64():
    paths = [
        str(Path(__file__).parent / "Cotes_Logo_Inverted.png"),
    ]
    for p in paths:
        if os.path.exists(p):
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return None

LOGO_B64 = get_logo_b64()
if LOGO_B64:
    LOGO_HTML = f"<img src='data:image/png;base64,{LOGO_B64}' style='width:120px;display:block;margin:0 auto 14px auto;'>"
else:
    LOGO_HTML = """
    <svg width='120' height='36' viewBox='0 0 120 36' xmlns='http://www.w3.org/2000/svg'
         style='display:block;margin:0 auto 14px auto;'>
      <rect width='120' height='36' rx='5' fill='#1a1a1a'/>
      <text x='60' y='25' font-family='Arial Black,Arial' font-weight='900'
            font-size='18' letter-spacing='3.5' fill='white' text-anchor='middle'>COTES</text>
    </svg>"""

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

*, html, body, [class*="css"] { font-family:'Inter',sans-serif; box-sizing:border-box; }
.stApp { background:#0d1117; }
#MainMenu, footer, header { visibility:hidden; }
.block-container { padding:0 !important; margin:0 !important; max-width:100% !important; }
section[data-testid="stSidebar"] { display:none !important; }
div[data-testid="collapsedControl"] { display:none !important; }
[data-testid="stVerticalBlock"] > div { gap:0 !important; }
[data-testid="column"] { padding:0 5px !important; }

/* ── LEFT PANEL ── */
/* Background/border live on the whole left column so the panel text AND the
   Reset/Admin buttons sit on one continuous surface. */
.st-key-left_wrap {
    background:#161b22;
    border-right:2px solid #21262d;
    padding:22px 16px 24px 16px;
    min-height:100vh;
}
.left-panel {
    padding:0;
}
.dash-title {
    font-size:1.5rem; font-weight:800; color:#ffffff;
    line-height:1.2; margin-bottom:10px; text-align:center;
}
.dash-desc {
    font-size:0.73rem; color:#c9d1d9; line-height:1.65; margin-bottom:4px;
}
.panel-section-title {
    font-size:0.82rem; font-weight:700; color:#e85d4a;
    margin:14px 0 6px 0; letter-spacing:0.01em;
}
.panel-text {
    font-size:0.72rem; color:#c9d1d9; line-height:1.55; margin-bottom:4px;
}
.panel-ul {
    margin:4px 0 0 0; padding-left:15px;
    list-style:disc; color:#c9d1d9;
}
.panel-ul li {
    font-size:0.72rem; line-height:1.55; margin-bottom:7px; color:#c9d1d9;
}
.panel-ul li b { color:#e6edf3; }
.panel-ul.sub { padding-left:14px; margin-top:5px; list-style:circle; }
.panel-ul.sub li { margin-bottom:5px; }

/* Colour legend */
.legend-row {
    display:flex; align-items:center; gap:8px;
    font-size:0.72rem; color:#c9d1d9; margin-bottom:6px;
}
.legend-dot {
    width:11px; height:11px; border-radius:50%; flex-shrink:0;
}
.legend-name { font-weight:600; color:#e6edf3; }
.legend-desc { color:#8b949e; font-size:0.67rem; }
.panel-divider { border:none; border-top:1px solid #21262d; margin:12px 0; }

/* ── FILTER BAR ── */
.filter-label {
    font-size:0.62rem; font-weight:700; letter-spacing:0.1em;
    text-transform:uppercase; color:#8b949e; margin-bottom:2px; padding-left:2px;
}
.stSelectbox > div > div {
    background:#1c2128 !important; border:1px solid #30363d !important;
    border-radius:5px !important; min-height:36px !important;
}
div[data-baseweb="select"] span { color:#e6edf3 !important; font-size:0.8rem !important; }

/* ── KPI CARDS ── */
.kpi-card {
    background:#161b22; border:1px solid #21262d; border-radius:7px;
    padding:12px 10px 10px 10px; text-align:center;
    min-height:90px; display:flex; flex-direction:column;
    justify-content:center; align-items:center;
}
.kpi-label {
    font-size:0.58rem; font-weight:700; letter-spacing:0.13em;
    text-transform:uppercase; color:#8b949e; margin-bottom:4px;
}
.kpi-value { font-size:1.5rem; font-weight:700; color:#e6edf3; line-height:1; }
.kpi-unit  { font-size:0.6rem; color:#8b949e; margin-top:2px; }
.kpi-delta { font-size:0.62rem; font-weight:600; margin-top:3px; }
.kpi-delta.good { color:#22c55e; }
.kpi-delta.bad  { color:#ef4444; }
.kpi-bar {
    width:80%; height:4px; background:#21262d; border-radius:3px;
    margin-top:5px; overflow:hidden;
}
.kpi-bar > div { height:100%; border-radius:3px; }

/* ── CHART CARDS ── */
.chart-card {
    background:#161b22; border:1px solid #21262d; border-radius:7px;
    padding:12px 12px 0px 12px; margin-bottom:8px; overflow:hidden;
}
/* Plotly iframe Streamlit injects ~32px whitespace below — pull it up */
[data-testid="stPlotlyChart"] {
    margin-bottom:-32px !important;
    padding-bottom:0 !important;
    line-height:0 !important;
}
[data-testid="stPlotlyChart"] > div {
    margin-bottom:0 !important;
    padding-bottom:0 !important;
}
.chart-title {
    font-size:0.85rem; font-weight:700; color:#e6edf3;
    text-align:center; margin-bottom:2px;
}
.chart-sub {
    font-size:0.62rem; color:#8b949e; text-align:center; margin-bottom:4px;
}

/* ── BEST CAMPAIGN SPOTLIGHT ── */
.spotlight-card {
    background:linear-gradient(135deg,#1b2230,#161b22);
    border:1px solid #30363d; border-left:4px solid #e85d4a;
    border-radius:8px; padding:14px 30px; margin-bottom:8px;
    display:flex; align-items:center; justify-content:space-between;
    gap:20px; flex-wrap:wrap;
}
.sp-badge {
    display:inline-block; font-size:0.58rem; font-weight:800; letter-spacing:0.14em;
    color:#e85d4a; background:rgba(232,93,74,0.12);
    border:1px solid rgba(232,93,74,0.35);
    padding:3px 9px; border-radius:20px; margin-bottom:7px;
}
.sp-name { font-size:1.35rem; font-weight:800; color:#ffffff; line-height:1.15; }
.sp-sub  { font-size:0.66rem; color:#8b949e; margin-top:4px; }
.sp-stats { display:flex; gap:26px; flex-wrap:wrap; }
.sp-stat  { text-align:right; }
.sp-stat-label {
    font-size:0.55rem; font-weight:700; letter-spacing:0.12em;
    text-transform:uppercase; color:#8b949e; margin-bottom:2px;
}
.sp-stat-val { font-size:1.05rem; font-weight:700; color:#e6edf3; }
.spotlight-empty { color:#8b949e; font-size:0.8rem; }

/* ── LEFT-PANEL ACTION BUTTONS (Reset / Admin / Export) ── */
/* All three share one look: identical box, centered label, equal spacing. */
.st-key-left_wrap [data-testid="stButton"],
.st-key-left_wrap [data-testid="stDownloadButton"] {
    width:100% !important; display:block !important; margin:0 0 12px 0 !important;
}
.st-key-left_wrap [data-testid="stButton"] > button,
.st-key-left_wrap [data-testid="stDownloadButton"] > button {
    background:#e85d4a !important; color:#ffffff !important;
    border:none !important; font-weight:800 !important;
    font-size:0.85rem !important; letter-spacing:0.1em !important;
    text-transform:uppercase !important;
    width:100% !important; box-sizing:border-box !important;
    height:46px !important; min-height:46px !important;
    padding:0 12px !important; border-radius:6px !important;
    margin:0 !important; cursor:pointer !important;
    display:flex !important; align-items:center !important; justify-content:center !important;
    gap:6px !important; line-height:1 !important;
    box-shadow:0 1px 2px rgba(0,0,0,0.25) !important;
    transition:background .15s ease, transform .05s ease !important;
}
/* Label text inside the button — keep it on one centered line */
.st-key-left_wrap [data-testid="stButton"] > button p,
.st-key-left_wrap [data-testid="stDownloadButton"] > button p,
.st-key-left_wrap [data-testid="stButton"] > button div,
.st-key-left_wrap [data-testid="stDownloadButton"] > button div {
    margin:0 !important; font-weight:800 !important; text-align:center !important;
    width:100% !important;
    white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important;
}
/* Extra separation above the first button (Reset) from the legend above it */
.st-key-left_wrap [data-testid="stButton"]:first-of-type { margin-top:18px !important; }
.st-key-left_wrap [data-testid="stButton"] > button:hover,
.st-key-left_wrap [data-testid="stDownloadButton"] > button:hover { background:#c9402f !important; }
.st-key-left_wrap [data-testid="stButton"] > button:active,
.st-key-left_wrap [data-testid="stDownloadButton"] > button:active { transform:translateY(1px) !important; }

/* Kill Streamlit's iframe padding under plotly charts */
[data-testid="stPlotlyChart"] { margin-bottom:0 !important; padding-bottom:0 !important; }
[data-testid="stPlotlyChart"] > div { margin-bottom:0 !important; }
.js-plotly-plot, .plot-container { margin-bottom:0 !important; }

/* ── SECTION DIVIDER ── */
.sec-div { border:none; border-top:1px solid #21262d; margin:8px 0 8px 0; }

/* ── STICKY TOP (filters + KPI cards pinned on scroll) ── */
/* Pin the flex-child wrapper that holds our keyed container. It is a direct
   child of the tall column block, so it has room to travel while pinned.
   Scoped via `> div > [stVerticalBlock].st-key-sticky_top` so it matches only
   our block's wrapper, not the outer columns row. */
[data-testid="stVerticalBlock"] > div:has(> div > [data-testid="stVerticalBlock"].st-key-sticky_top),
[data-testid="stVerticalBlock"] > div:has(> [data-testid="stVerticalBlock"].st-key-sticky_top) {
    position:sticky !important; top:0 !important; z-index:999;
    background:#0d1117;
    padding:8px 0 6px 0;
    box-shadow:0 6px 12px -6px rgba(0,0,0,0.6);
}
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
BU_MAPPING = [
    ('W2M','Cotes Group'),('WDD','WDD'),('Wind Europe 2024 Bilbao','WE'),
    ('WindEurope','WE'),('Wind Europe','WE'),('WE_ACP','WE'),('WE_','WE'),
    ('BD_','WDD'),('GERMAN - BD','WDD'),('ENGLISH - BD','WDD'),('FRENCH - BD','WDD'),
    ('DANISH - BD','WDD'),('Business Development','Installers'),
    ('GERMAN - WATER DAMAGE','WDD'),('ENGLISH - WATER DAMAGE','WDD'),
    ('FRENCH - WATER DAMAGE','WDD'),('DANISH - WATER DAMAGE','WDD'),
    ('WATER DAMAGE - DANISH','WDD'),('DK_Cotes','Cotes Group'),
    ('Cotes Brand','Cotes Group'),('McFly','Installers'),('TBM Boosting','Installers'),
    ('Battery Manufacturing','BM'),('O&M_Boost','WE'),('Display - Retargeting','WE'),
    ('Website visits','Cotes Group'),('Brand awareness','Cotes Group'),
    ('Engineers (EU)','WE'),('Boost_Post','Cotes Group'),
    ('Quality Assurance','Cotes Group'),('DK_Food','Cotes Group'),
]

BU_META = {
    "WDD":         {"color":"#f0a500", "label":"WDD",         "desc":"Water Damage Drying"},
    "WE":          {"color":"#58a6ff", "label":"WE",          "desc":"Wind Energy"},
    "Cotes Group": {"color":"#e85d4a", "label":"Cotes Group", "desc":"General / Group"},
    "Installers":  {"color":"#34d399", "label":"Installers",  "desc":"Installer Network"},
    "BM":          {"color":"#a78bfa", "label":"BM",          "desc":"Battery Manufacturing"},
}
DONUT_COLORS = ["#58a6ff","#f0a500","#34d399","#e85d4a","#a78bfa","#f472b6"]

CT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#8b949e", family="Inter", size=10),
)

# Precompute lowercased keys once so assign_bu doesn't re-.lower() them per row
BU_MAPPING_LC = [(key.lower(), bu) for key, bu in BU_MAPPING]

def assign_bu(campaign):
    s = str(campaign).lower()
    for key, bu in BU_MAPPING_LC:
        if key in s: return bu
    return 'Other'

def fmt(v):
    if v >= 1_000_000: return f"{v/1_000_000:.2f}M"
    if v >= 1_000:     return f"{v/1_000:.1f}K"
    return f"{v:,.0f}"

# ── PDF export ───────────────────────────────────────────────────────────────
def build_pdf(filters: list, kpis: list, bu_rows: list, ch_rows: list) -> bytes:
    """Render a one-page summary of the currently filtered view to PDF bytes.

    filters : list of (label, value) shown as the applied-filter context.
    kpis    : list of (label, value) for the KPI strip.
    bu_rows : [(BusinessUnit, Impressions, Clicks, Spend), ...]
    ch_rows : [(Channel, Impressions, Clicks, Spend), ...]
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                    TableStyle)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=18*mm, rightMargin=18*mm,
                            topMargin=16*mm, bottomMargin=16*mm,
                            title="Cotes Marketing Dashboard — Report")
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=18,
                        textColor=colors.HexColor("#e85d4a"), spaceAfter=2)
    sub = ParagraphStyle("sub", parent=styles["Normal"], fontSize=9,
                         textColor=colors.HexColor("#666666"), spaceAfter=10)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=12,
                        spaceBefore=12, spaceAfter=6)

    story: list = [Paragraph("Cotes Marketing Dashboard", h1)]
    filt_txt = " &nbsp;·&nbsp; ".join(f"<b>{k}:</b> {v}" for k, v in filters)
    story.append(Paragraph("Filtered view — " + filt_txt, sub))

    def make_table(header, rows, col_widths=None):
        data = [header] + rows
        t = Table(data, colWidths=col_widths, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#161b22")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, colors.HexColor("#f4f5f7")]),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d0d7de")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        return t

    story.append(Paragraph("Key Metrics", h2))
    story.append(make_table(["Metric", "Value"],
                            [[l, v] for l, v in kpis],
                            col_widths=[90*mm, 84*mm]))

    if bu_rows:
        story.append(Paragraph("Business Units", h2))
        story.append(make_table(["Business Unit", "Impressions", "Clicks", "Spend (DKK)"],
                                bu_rows))
    if ch_rows:
        story.append(Paragraph("Channels", h2))
        story.append(make_table(["Channel", "Impressions", "Clicks", "Spend (DKK)"],
                                ch_rows))

    story.append(Spacer(1, 12))
    doc.build(story)
    return buf.getvalue()

# ── Data load ──────────────────────────────────────────────────────────────────
REQUIRED_COLS = ["Date", "Campaign", "Traffic source"]

class MissingColumns(Exception):
    """Raised when the uploaded file is missing columns the dashboard needs."""

@st.cache_data(ttl=3600)
def load_data(file):
    """Return (dataframe, n_dropped_dates). Raises MissingColumns if required
    columns are absent so the caller can show a friendly message."""
    xl = pd.ExcelFile(file, engine="openpyxl")
    sheet = "Cotes_CampaignData" if "Cotes_CampaignData" in xl.sheet_names else xl.sheet_names[0]
    df = xl.parse(sheet)
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(how="all")

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise MissingColumns(missing)

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    # Drop rows whose date couldn't be parsed — otherwise they vanish silently
    # from every time/Year/Month view and the totals don't reconcile.
    n_dropped = int(df["Date"].isna().sum())
    if n_dropped:
        df = df[df["Date"].notna()]

    for col in ["Cost (*)","Clicks","CPC (*)","CPM (*)","CTR","Impressions"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    if "CTR" in df.columns and df["CTR"].max() <= 1.0:
        df["CTR"] = df["CTR"] * 100
    df["Traffic source"] = df["Traffic source"].astype(str).str.strip().str.title()
    df["BusinessUnit"]   = df["Campaign"].apply(assign_bu)
    df["Year"]           = df["Date"].dt.year.astype("Int64")
    df["Month"]          = df["Date"].dt.strftime("%B")
    df["MonthNum"]       = df["Date"].dt.month
    return df, n_dropped

# ── SharePoint connection (optional; falls back to manual upload) ───────────────
# Reads the Excel file directly from SharePoint via Microsoft Graph, using an
# app-only login. Configure the [sharepoint] block in .streamlit/secrets.toml:
#
#   [sharepoint]
#   tenant_id     = "..."                       # Directory ID from IT
#   client_id     = "..."                        # Application ID from IT
#   client_secret = "..."                        # client secret from IT
#   site_url      = "https://COMPANY.sharepoint.com/sites/Marketing"
#   file_path     = "Documents/Reports/Cotes_CampaignData.xlsx"  # path within the site
#
# If this block is missing, the app just shows the upload box as before.
def sharepoint_configured() -> bool:
    try:
        sp = st.secrets["sharepoint"]
    except Exception:
        return False
    needed = ("tenant_id", "client_id", "client_secret", "site_url", "file_path")
    return all(str(sp.get(k, "")).strip() for k in needed)

@st.cache_data(ttl=3600, show_spinner="Loading data from SharePoint…")
def fetch_sharepoint_bytes() -> bytes:
    import msal, requests
    from urllib.parse import urlparse
    sp = st.secrets["sharepoint"]

    # 1) Log in as the app and get an access token
    app = msal.ConfidentialClientApplication(
        client_id=sp["client_id"],
        authority=f"https://login.microsoftonline.com/{sp['tenant_id']}",
        client_credential=sp["client_secret"],
    )
    token = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"]) or {}
    if "access_token" not in token:
        raise RuntimeError(token.get("error_description", "Could not authenticate to Microsoft Graph."))
    headers = {"Authorization": f"Bearer {token['access_token']}"}
    GRAPH = "https://graph.microsoft.com/v1.0"

    # 2) Resolve the SharePoint site id from its URL
    parsed = urlparse(sp["site_url"])
    host = parsed.netloc
    site_path = parsed.path  # e.g. /sites/Marketing
    r = requests.get(f"{GRAPH}/sites/{host}:{site_path}", headers=headers, timeout=30)
    r.raise_for_status()
    site_id = r.json()["id"]

    # 3) Download the file by its path within the site's default document library
    file_path = str(sp["file_path"]).lstrip("/")
    r = requests.get(f"{GRAPH}/sites/{site_id}/drive/root:/{file_path}:/content",
                     headers=headers, timeout=60)
    r.raise_for_status()
    return r.content

# ── Data source: SharePoint first, manual upload as fallback ────────────────────
uploaded = None
if sharepoint_configured():
    try:
        uploaded = io.BytesIO(fetch_sharepoint_bytes())
    except Exception as e:
        st.error(f"Could not load the file from SharePoint: {e}")
        st.caption("You can upload the file manually below instead.")

if uploaded is None:
    with st.sidebar:
        up_side = st.file_uploader("Upload Excel", type=["xlsx"])
        if up_side: uploaded = up_side

if uploaded is None:
    st.markdown("""
    <div style='display:flex;flex-direction:column;align-items:center;
                justify-content:center;height:88vh;gap:16px'>
      <div style='font-size:2.5rem'>📊</div>
      <div style='color:#8b949e;font-size:1.05rem;font-weight:600'>Cotes Marketing Dashboard</div>
      <div style='color:#3b4460;font-size:0.82rem'>Upload your Funnel export to get started</div>
    </div>""", unsafe_allow_html=True)
    up2 = st.file_uploader("Upload Funnel .xlsx export", type=["xlsx"], key="main_upload")
    if up2: uploaded = up2
    if uploaded is None: st.stop()

try:
    df_raw, n_dropped_dates = load_data(uploaded)
except MissingColumns as e:
    st.error("The uploaded file is missing required columns: "
             + ", ".join(e.args[0]) + ".")
    st.caption("Expected at least these columns: " + ", ".join(REQUIRED_COLS)
               + ". Please upload the standard Funnel export.")
    st.stop()

if n_dropped_dates:
    st.caption(f"⚠️ {n_dropped_dates:,} row(s) skipped due to unparseable dates.")

# Global benchmarks
_c = df_raw["Clicks"].sum(); _i = df_raw["Impressions"].sum(); _s = df_raw["Cost (*)"].sum()
GLOBAL_CTR = (_c / _i * 100) if _i > 0 else 0
GLOBAL_CPC = (_s / _c)       if _c > 0 else 0

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in [("f_bu","All"),("f_year","All"),("f_month","All"),("f_ch","All")]:
    if k not in st.session_state: st.session_state[k] = v
if "is_admin" not in st.session_state: st.session_state.is_admin = False

# Metric keys used for targets (label, unit, direction where "higher"=more is better)
TARGET_METRICS = [
    ("spend",       "Spend Target (DKK)",  "DKK", "lower"),
    ("impressions", "Impressions Target",  "",    "higher"),
    ("clicks",      "Clicks Target",       "",    "higher"),
    ("ctr",         "CTR Target (%)",      "%",   "higher"),
    ("cpc",         "CPC Target (DKK)",    "DKK", "lower"),
]

# ── Persistent, admin-managed targets ────────────────────────────────────────
TARGETS_FILE = Path(__file__).parent / "targets.json"

_METRIC_KEYS = {m[0] for m in TARGET_METRICS}

def _normalize_targets(data: dict) -> dict:
    """Coerce the stored file into the current shape: {BU: {year: {metric: value}}}.

    An older format stored targets flat per BU ({BU: {metric: value}}) with no
    year. Those pre-dated per-year targets, so we can't know which year they
    meant — drop them rather than mis-attribute them to a year.
    """
    clean = {}
    for bu, by_year in (data or {}).items():
        if not isinstance(by_year, dict):
            continue
        # Old flat format: values are metric keys, not year keys → discard.
        if any(k in _METRIC_KEYS for k in by_year):
            continue
        years = {y: v for y, v in by_year.items() if isinstance(v, dict) and v}
        if years:
            clean[bu] = years
    return clean

def load_targets() -> dict:
    try:
        with open(TARGETS_FILE, "r", encoding="utf-8") as f:
            return _normalize_targets(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_targets(data: dict) -> None:
    # Write to a temp file then atomically replace, so a crash or a concurrent
    # save can never leave targets.json half-written (which load_targets would
    # silently reset to {}).
    tmp = TARGETS_FILE.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, TARGETS_FILE)

def check_admin(username: str, password: str) -> bool:
    """Verify credentials against .streamlit/secrets.toml [admin] block.

    Note: this is a single shared admin secret for an internal tool. The hash is
    an unsalted SHA-256 and there is no rate limiting — it is NOT suitable for
    per-user accounts or public exposure.
    """
    try:
        admin = st.secrets["admin"]
    except Exception:
        return False
    pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    user_ok = hmac.compare_digest(str(username), str(admin.get("username", "")))
    pass_ok = hmac.compare_digest(pw_hash, str(admin.get("password_hash", "")))
    return user_ok and pass_ok

month_order = ["January","February","March","April","May","June",
               "July","August","September","October","November","December"]
all_bu     = ["All"] + sorted([x for x in df_raw["BusinessUnit"].dropna().unique() if x != "Other"])
all_years  = ["All"] + [str(y) for y in sorted(df_raw["Year"].dropna().unique(), reverse=True)]
all_months = ["All"] + [m for m in month_order if m in df_raw["Month"].dropna().unique().tolist()]
all_ch     = ["All"] + sorted(df_raw["Traffic source"].dropna().unique().tolist())

# Persisted, admin-managed targets — source of truth, survives restarts
saved_targets = load_targets()

# ── Admin panel (modal popup) ────────────────────────────────────────────────
@st.dialog("Admin · KPI Targets / Budget", width="large")
def admin_dialog():
    if not st.session_state.is_admin:
        st.caption("Targets are set by an admin and shown read-only on the KPI cards. "
                   "Log in to edit them.")
        with st.form("admin_login"):
            lu = st.text_input("User ID", key="login_user")
            lp = st.text_input("Password", type="password", key="login_pass")
            if st.form_submit_button("Log in"):
                if check_admin(lu, lp):
                    st.session_state.is_admin = True
                    st.rerun()
                else:
                    st.error("Invalid user ID or password.")
        return

    top = st.columns([3, 1])
    top[0].success("Signed in as admin — saved changes are permanent.")
    if top[1].button("Log out"):
        st.session_state.is_admin = False
        st.rerun()

    bu_choices = [b for b in all_bu if b != "All"]
    if not bu_choices:
        st.caption("No business units available in the current data.")
        return

    # Years available to set: whatever the data has, plus the current and next
    # year so an admin can set targets ahead of any data arriving.
    this_year = date.today().year
    year_choices = sorted(
        {y for y in all_years if y != "All"} | {str(this_year), str(this_year + 1)},
        reverse=True)

    esel = st.columns(2)
    with esel[0]:
        default_bu = (bu_choices.index(st.session_state.f_bu)
                      if st.session_state.f_bu in bu_choices else 0)
        edit_bu = st.selectbox("Business Unit to edit", bu_choices,
            index=default_bu, key="target_bu_sel")
    with esel[1]:
        default_yr = (year_choices.index(st.session_state.f_year)
                      if st.session_state.f_year in year_choices else 0)
        edit_year = st.selectbox("Year to edit", year_choices,
            index=default_yr, key="target_yr_sel")

    cur = saved_targets.get(edit_bu, {}).get(edit_year, {})
    with st.form("target_form"):
        tcols = st.columns(len(TARGET_METRICS))
        new_vals = {}
        for c, (key, label, unit, _dir) in zip(tcols, TARGET_METRICS):
            step = 0.1 if key in ("ctr", "cpc") else 1000.0
            new_vals[key] = c.number_input(
                label, min_value=0.0, step=step,
                value=float(cur.get(key, 0.0)), key=f"tgt_{key}_{edit_bu}_{edit_year}")
        if st.form_submit_button("Save targets"):
            clean = {k: v for k, v in new_vals.items() if v > 0}
            by_year = saved_targets.setdefault(edit_bu, {})
            if clean:
                by_year[edit_year] = clean
            else:
                by_year.pop(edit_year, None)   # all zeroed → clear this year
            if not by_year:
                saved_targets.pop(edit_bu, None)
            save_targets(saved_targets)
            st.success(f"Targets saved for {edit_bu} · {edit_year}.")
            st.rerun()
    st.caption("Targets are set per Business Unit **per year**. They show on the KPI "
               "cards only when that single Business Unit and that Year are selected, "
               "with Month set to “All” (i.e. viewing the whole year).")

# ══════════════════════════════════════════════════════════════════════
# LAYOUT
# ══════════════════════════════════════════════════════════════════════
left_col, main_col = st.columns([1, 5.8], gap="small")

# ── LEFT PANEL ─────────────────────────────────────────────────────────────────
with left_col.container(key="left_wrap"):
    legend_rows = "".join([
        f"""<div class='legend-row'>
              <div class='legend-dot' style='background:{m["color"]}'></div>
              <div>
                <span class='legend-name'>{m["label"]}</span>
                <span class='legend-desc'> — {m["desc"]}</span>
              </div>
            </div>"""
        for bu, m in BU_META.items()
    ])

    st.markdown(f"""
    <div class='left-panel'>
      {LOGO_HTML}
      <div class='dash-title'>Marketing<br>Dashboard</div>
      <div class='dash-desc'>
        This is a consolidated overview of marketing performance across our
        business units, industries, social media channels, and time.
      </div>

      <hr class='panel-divider'>
      <div class='panel-section-title'>Filters (Top Bar)</div>
      <div class='panel-text'>
        Use the slicers at the top to filter the data shown across the entire dashboard.
      </div>

      <hr class='panel-divider'>
      <div class='panel-section-title'>Key Metrics Explained</div>
      <ul class='panel-ul'>
        <li><b>Impressions:</b> Number of times an ad was shown to users.</li>
        <li><b>Clicks:</b> Number of times an user has clicked on an ad.</li>
        <li><b>CTR (Click-Through Rate):</b> Percentage of impressions that resulted in a click</li>
      </ul>

      <hr class='panel-divider'>
      <div class='panel-section-title'>Industry Colours</div>
      {legend_rows}
    </div>
    """, unsafe_allow_html=True)

    if st.button("RESET FILTERS", key="reset_btn"):
        for k in ["f_bu","f_year","f_month","f_ch"]:
            st.session_state[k] = "All"
        st.rerun()

    admin_label = "🔐 ADMIN PANEL" if not st.session_state.is_admin else "🔓 ADMIN PANEL"
    if st.button(admin_label, key="admin_btn"):
        admin_dialog()

    # Filled in later, once the filtered data & KPIs exist (main column runs
    # after this block, so we reserve a slot here and populate it below).
    export_slot = st.empty()

# ── MAIN CONTENT ───────────────────────────────────────────────────────────────
with main_col:

    # Everything rendered into this container stays pinned to the top on scroll
    sticky = st.container(key="sticky_top")

    # ── Filter bar ──────────────────────────────────────────────────────
    with sticky:
        fa, fb, fc, fd = st.columns(4)
        with fa:
            st.markdown("<div class='filter-label'>Business Unit</div>", unsafe_allow_html=True)
            st.session_state.f_bu = st.selectbox("bu", all_bu,
                index=all_bu.index(st.session_state.f_bu) if st.session_state.f_bu in all_bu else 0,
                label_visibility="collapsed", key="sel_bu")
        with fb:
            st.markdown("<div class='filter-label'>Year</div>", unsafe_allow_html=True)
            st.session_state.f_year = st.selectbox("yr", all_years,
                index=all_years.index(st.session_state.f_year) if st.session_state.f_year in all_years else 0,
                label_visibility="collapsed", key="sel_yr")
        with fc:
            st.markdown("<div class='filter-label'>Month</div>", unsafe_allow_html=True)
            st.session_state.f_month = st.selectbox("mo", all_months,
                index=all_months.index(st.session_state.f_month) if st.session_state.f_month in all_months else 0,
                label_visibility="collapsed", key="sel_mo")
        with fd:
            st.markdown("<div class='filter-label'>Channel</div>", unsafe_allow_html=True)
            st.session_state.f_ch = st.selectbox("ch", all_ch,
                index=all_ch.index(st.session_state.f_ch) if st.session_state.f_ch in all_ch else 0,
                label_visibility="collapsed", key="sel_ch")

    # ── Apply filters ────────────────────────────────────────────────────
    mask = pd.Series(True, index=df_raw.index)
    if st.session_state.f_bu    != "All": mask &= df_raw["BusinessUnit"]   == st.session_state.f_bu
    if st.session_state.f_year  != "All": mask &= df_raw["Year"]           == int(st.session_state.f_year)
    if st.session_state.f_month != "All": mask &= df_raw["Month"]          == st.session_state.f_month
    if st.session_state.f_ch    != "All": mask &= df_raw["Traffic source"] == st.session_state.f_ch
    df = df_raw[mask]

    if df.empty:
        st.warning("No data for current filters.")
        st.stop()

    # ── KPI strip ────────────────────────────────────────────────────────
    total_spend  = df["Cost (*)"].sum()
    total_clicks = df["Clicks"].sum()
    total_imp    = df["Impressions"].sum()
    avg_ctr      = (total_clicks / total_imp * 100) if total_imp > 0 else 0
    avg_cpc      = (total_spend / total_clicks)      if total_clicks > 0 else 0

    ctr_vs    = avg_ctr - GLOBAL_CTR
    cpc_vs    = avg_cpc - GLOBAL_CPC
    ctr_cls   = "good" if ctr_vs >= 0 else "bad"
    cpc_cls   = "good" if cpc_vs <= 0 else "bad"
    ctr_delta = f"{'▲' if ctr_vs>=0 else '▼'} {abs(ctr_vs):.3f}% vs avg"
    cpc_delta = f"{'▼' if cpc_vs<=0 else '▲'} {abs(cpc_vs):.2f} DKK vs avg"

    # Targets are set per BU per year, so they only apply when a single BU and a
    # single full year are in view: one BU, one Year, and Month = "All".
    active_targets = {}
    if (st.session_state.f_bu != "All"
            and st.session_state.f_year != "All"
            and st.session_state.f_month == "All"):
        active_targets = (saved_targets.get(st.session_state.f_bu, {})
                          .get(st.session_state.f_year, {}))

    def target_html(actual, target, direction):
        """Return % of target + progress bar, or None if no target set."""
        if not target or target <= 0:
            return None
        pct = actual / target * 100
        good = (actual >= target) if direction == "higher" else (actual <= target)
        cls = "good" if good else "bad"
        arrow = "▲" if good else "▼"
        bar = max(0.0, min(100.0, pct))
        bar_color = "#22c55e" if good else "#ef4444"
        return (f"<div class='kpi-delta {cls}'>{arrow} {pct:.0f}% of target</div>"
                f"<div class='kpi-bar'><div style='width:{bar:.0f}%;background:{bar_color}'></div></div>")

    # (metric_key, label, display_value, unit, actual_value, fallback_delta, fallback_cls)
    cards = [
        ("spend",       "Total Spend", fmt(total_spend),  "DKK", total_spend,  "",        ""),
        ("impressions", "Impressions", fmt(total_imp),    "",    total_imp,    "",        ""),
        ("clicks",      "Clicks",      fmt(total_clicks), "",    total_clicks, "",        ""),
        ("ctr",         "Avg. CTR",    f"{avg_ctr:.2f}%", "",    avg_ctr,      ctr_delta, ctr_cls),
        ("cpc",         "Avg. CPC",    f"{avg_cpc:.2f}",  "DKK", avg_cpc,      cpc_delta, cpc_cls),
    ]
    directions = {k: d for k, _l, _u, d in TARGET_METRICS}
    with sticky:
        st.markdown("<hr class='sec-div'>", unsafe_allow_html=True)
        cols = st.columns(5)
        for col, (key, label, val, unit, actual, fb_delta, fb_cls) in zip(cols, cards):
            th = target_html(actual, active_targets.get(key, 0), directions[key])
            if th:
                delta_html = th
            elif fb_delta:
                delta_html = f"<div class='kpi-delta {fb_cls}'>{fb_delta}</div>"
            else:
                delta_html = ""
            with col:
                st.markdown(f"""
                <div class='kpi-card'>
                  <div class='kpi-label'>{label}</div>
                  <div class='kpi-value'>{val}</div>
                  <div class='kpi-unit'>{unit}</div>
                  {delta_html}
                </div>""", unsafe_allow_html=True)

    # ── Export PDF Report ────────────────────────────────────────────────
    # Summary of the currently filtered view. Built lazily on click so the
    # (relatively expensive) reportlab render only runs when requested.
    def build_report_pdf():
        bu = (df[df["BusinessUnit"] != "Other"]
              .groupby("BusinessUnit")
              .agg(Impressions=("Impressions", "sum"),
                   Clicks=("Clicks", "sum"), Spend=("Cost (*)", "sum"))
              .sort_values("Spend", ascending=False).reset_index())
        ch = (df.groupby("Traffic source")
              .agg(Impressions=("Impressions", "sum"),
                   Clicks=("Clicks", "sum"), Spend=("Cost (*)", "sum"))
              .sort_values("Spend", ascending=False).reset_index())
        filters = [
            ("Business Unit", st.session_state.f_bu),
            ("Year", st.session_state.f_year),
            ("Month", st.session_state.f_month),
            ("Channel", st.session_state.f_ch),
        ]
        kpis = [(label, f"{val} {unit}".strip())
                for (_k, label, val, unit, *_rest) in cards]
        bu_rows = [[r.BusinessUnit, fmt(r.Impressions), fmt(r.Clicks), fmt(r.Spend)]
                   for r in bu.itertuples()]
        ch_rows = [[r._1, fmt(r.Impressions), fmt(r.Clicks), fmt(r.Spend)]
                   for r in ch.itertuples()]
        return build_pdf(filters, kpis, bu_rows, ch_rows)

    export_slot.download_button(
        "📄 EXPORT PDF REPORT",
        data=build_report_pdf(),
        file_name="cotes_marketing_report.pdf",
        mime="application/pdf",
        use_container_width=True,
        key="export_pdf_btn",
    )

    st.markdown("<hr class='sec-div'>", unsafe_allow_html=True)

    # ── Row 1: Industry bars + Donuts ────────────────────────────────────
    r1a, r1b, r1c = st.columns([2.1, 2.1, 1.25])

    N_BU   = max(1, len([x for x in df["BusinessUnit"].unique() if x != "Other"]))
    # DON_H is fixed (independent of BAR_H) so the donut stack — and the Top
    # Campaign card rendered below it — never move.
    DON_H  = 130
    # Grow the bar-chart cards to fill the same height as the 3-donut stack on
    # the right, so the space under the bars isn't wasted. Row height is driven
    # by the (unchanged) donut column, so this fills the gap without pushing
    # anything below it down.
    BAR_H  = max(N_BU * 56 + 16, 3 * DON_H - 10)

    def bu_bar(data_col, title):
        d = df.groupby("BusinessUnit")[data_col].sum().reset_index()
        d = d[d["BusinessUnit"] != "Other"].sort_values(data_col)
        fig = go.Figure(go.Bar(
            x=d[data_col], y=d["BusinessUnit"], orientation="h",
            marker_color=[BU_META.get(b,{"color":"#555"})["color"] for b in d["BusinessUnit"]],
            text=[fmt(v) for v in d[data_col]],
            textposition="outside", textfont=dict(size=9, color="#8b949e"),
            cliponaxis=False,
        ))
        fig.update_layout(**CT, height=BAR_H, showlegend=False,
                          margin=dict(l=4, r=36, t=6, b=6))
        fig.update_xaxes(showgrid=True, gridcolor="#21262d", zeroline=False, showticklabels=False)
        fig.update_yaxes(showgrid=False, tickfont=dict(size=10, color="#c9d1d9"), automargin=True)
        return fig

    with r1a:
        st.markdown("<div class='chart-card'><div class='chart-title'>Industries by Impressions</div>", unsafe_allow_html=True)
        st.plotly_chart(bu_bar("Impressions","Industries by Impressions"),
                        use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div>", unsafe_allow_html=True)

    with r1b:
        st.markdown("<div class='chart-card'><div class='chart-title'>Industries by Clicks</div>", unsafe_allow_html=True)
        st.plotly_chart(bu_bar("Clicks","Industries by Clicks"),
                        use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div>", unsafe_allow_html=True)

    with r1c:
        def donut(labels, values, title, h):
            fig = go.Figure(go.Pie(
                labels=labels, values=values, hole=0.52,
                marker_colors=DONUT_COLORS, textfont_size=8,
                textinfo="percent", hoverinfo="label+percent+value",
                # Hide labels on slices under 3% so tiny wedges don't overlap
                texttemplate="%{percent}", textposition="inside",
                insidetextorientation="horizontal",
            ))
            fig.update_traces(
                texttemplate=["%{percent}" if (v / (sum(values) or 1)) >= 0.03 else ""
                              for v in values])
            fig.update_layout(**CT, height=h,
                margin=dict(l=4, r=4, t=6, b=28),
                legend=dict(orientation="h", y=-0.18,
                            font=dict(size=8, color="#8b949e"),
                            xanchor="center", x=0.5))
            return fig

        ch = df.groupby("Traffic source")["Cost (*)"].sum().reset_index()
        st.markdown("<div class='chart-card'><div class='chart-title'>Channels by Cost</div>", unsafe_allow_html=True)
        st.plotly_chart(donut(ch["Traffic source"], ch["Cost (*)"], "Channels by Cost", DON_H),
                        use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div>", unsafe_allow_html=True)

        if "Media type" in df.columns:
            mc = df.groupby("Media type")["Cost (*)"].sum().reset_index()
            st.markdown("<div class='chart-card'><div class='chart-title'>Media Type by Cost</div>", unsafe_allow_html=True)
            st.plotly_chart(donut(mc["Media type"], mc["Cost (*)"], "", DON_H),
                            use_container_width=True, config={"displayModeBar":False})
            st.markdown("</div>", unsafe_allow_html=True)

            mt = (df.groupby("Media type")
                    .agg(_clicks=("Clicks","sum"), _imp=("Impressions","sum"))
                    .reset_index())
            mt["CTR"] = (mt["_clicks"] / mt["_imp"].replace(0, pd.NA) * 100).fillna(0)
            st.markdown("<div class='chart-card'><div class='chart-title'>Media Type by CTR</div>", unsafe_allow_html=True)
            st.plotly_chart(donut(mt["Media type"], mt["CTR"], "", DON_H),
                            use_container_width=True, config={"displayModeBar":False})
            st.markdown("</div>", unsafe_allow_html=True)

    # ── Best Campaign spotlight (fills the space under the industry bars) ──
    # "Best" is a blended, min-max-normalized score across the metrics that
    # matter, so no single dimension (raw clicks / a tiny high-CTR campaign /
    # a cheap-but-idle one) can win on its own.
    def best_campaign(data):
        camp = (data.groupby("Campaign")
                    .agg(Impr=("Impressions", "sum"), Clicks=("Clicks", "sum"),
                         Spend=("Cost (*)", "sum"))
                    .reset_index())
        # Need clicks (and impressions) for CTR/CPC to be meaningful.
        camp = camp[(camp["Clicks"] > 0) & (camp["Impr"] > 0)]
        if camp.empty:
            return None
        camp["CTR"] = camp["Clicks"] / camp["Impr"] * 100
        camp["CPC"] = camp["Spend"] / camp["Clicks"]

        def norm(s):
            lo, hi = s.min(), s.max()
            return (s - lo) / (hi - lo) if hi > lo else pd.Series(1.0, index=s.index)

        score = (0.35 * norm(camp["Clicks"])
                 + 0.30 * norm(camp["CTR"])
                 + 0.20 * (1 - norm(camp["CPC"]))   # cheaper CPC → higher score
                 + 0.15 * norm(camp["Impr"]))
        return camp.assign(Score=score).loc[score.idxmax()]

    bc = best_campaign(df)
    # Full-width card so it spans under the bars AND the donuts — no empty
    # cell on the right.
    if bc is None:
        st.markdown("<div class='spotlight-card'>"
                    "<div class='spotlight-empty'>No campaign with clicks for the "
                    "current filters.</div></div>", unsafe_allow_html=True)
    else:
        stats = [
            ("Spend",       f"{fmt(bc['Spend'])} DKK"),
            ("Impressions", fmt(bc["Impr"])),
            ("Clicks",      fmt(bc["Clicks"])),
            ("CTR",         f"{bc['CTR']:.2f}%"),
            ("CPC",         f"{bc['CPC']:.2f} DKK"),
        ]
        stat_html = "".join(
            f"<div class='sp-stat'><div class='sp-stat-label'>{l}</div>"
            f"<div class='sp-stat-val'>{v}</div></div>" for l, v in stats)
        st.markdown(f"""
        <div class='spotlight-card'>
          <div>
            <div class='sp-badge'>★ TOP CAMPAIGN</div>
            <div class='sp-name'>{html.escape(str(bc['Campaign']))}</div>
            <div class='sp-sub'>Best overall performer — blended score of clicks, CTR, CPC &amp; reach</div>
          </div>
          <div class='sp-stats'>{stat_html}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr class='sec-div'>", unsafe_allow_html=True)

    # ── Row 2: Time series ────────────────────────────────────────────────
    t = (df.groupby("Date")
           .agg(Impressions=("Impressions","sum"), Clicks=("Clicks","sum"), Cost=("Cost (*)","sum"))
           .reset_index().sort_values("Date"))
    t["CTR"] = (t["Clicks"]/t["Impressions"]*100).fillna(0)

    def area_chart(x, y, title, color, yformat=","):
        rgb = tuple(int(color[i:i+2], 16) for i in (1,3,5))
        # With a single data point a line has nothing to draw — show a marker
        # so the chart doesn't look empty/broken.
        mode = "lines" if len(x) > 1 else "markers"
        f = go.Figure(go.Scatter(
            x=x, y=y, mode=mode,
            line=dict(color=color, width=1.5),
            marker=dict(color=color, size=7),
            fill="tozeroy", fillcolor=f"rgba({rgb[0]},{rgb[1]},{rgb[2]},0.08)",
        ))
        f.update_layout(**CT, height=195, margin=dict(l=4,r=8,t=30,b=4),
            title=dict(text=title, font=dict(size=11,color="#e6edf3",weight=700),
                       x=0.5, xanchor="center", y=0.97))
        f.update_xaxes(showgrid=False, tickfont=dict(size=8), tickformat="%b %Y", tickangle=-30)
        f.update_yaxes(showgrid=True, gridcolor="#21262d", tickfont=dict(size=8), tickformat=yformat)
        return f

    t2a, t2b, t2c = st.columns(3)
    with t2a:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.plotly_chart(area_chart(t["Date"], t["Impressions"], "Impressions Over Time", "#58a6ff"),
                        use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div>", unsafe_allow_html=True)
    with t2b:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.plotly_chart(area_chart(t["Date"], t["Clicks"], "Clicks Over Time", "#f0a500"),
                        use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div>", unsafe_allow_html=True)
    with t2c:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.plotly_chart(area_chart(t["Date"], t["CTR"], "CTR Over Time", "#34d399", yformat=".2f"),
                        use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div>", unsafe_allow_html=True)


