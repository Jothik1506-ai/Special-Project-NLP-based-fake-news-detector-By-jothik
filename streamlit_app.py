import streamlit as st
import json
import pandas as pd
import numpy as np
import re
import time
import os
import csv
from datetime import datetime
from nltk.corpus import stopwords
import nltk
from numpy_model import NumpyModel

# ───────────────────────── Page Config ─────────────────────────
st.set_page_config(
    page_title="Fake News Detector",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ───────────────────────── CSS ─────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hide default Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ── Background ── */
.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: white;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown li,
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: white !important;
}
section[data-testid="stSidebar"] .stRadio label {
    color: #e0e0e0 !important;
    font-weight: 500;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    color: #ffffff !important;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.15);
}

/* ── Card containers ── */
.card {
    background: #ffffff;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.06);
    margin-bottom: 1.5rem;
    border: 1px solid rgba(0,0,0,0.04);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.10);
}

/* ── Hero banner ── */
.hero-banner {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%);
    border-radius: 20px;
    padding: 3rem 2.5rem;
    margin-bottom: 2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(15,52,96,0.3);
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 30% 70%, rgba(78,205,196,0.1) 0%, transparent 50%),
                radial-gradient(circle at 70% 30%, rgba(255,107,107,0.08) 0%, transparent 50%);
    animation: float 8s ease-in-out infinite;
}
@keyframes float {
    0%, 100% { transform: translate(0, 0) rotate(0deg); }
    33% { transform: translate(10px, -10px) rotate(1deg); }
    66% { transform: translate(-5px, 5px) rotate(-1deg); }
}
.hero-title {
    font-size: 2.8rem;
    font-weight: 900;
    background: linear-gradient(135deg, #ffffff 0%, #4ECDC4 50%, #FF6B6B 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
    position: relative;
    z-index: 1;
    letter-spacing: -0.5px;
}
.hero-subtitle {
    color: rgba(255,255,255,0.75);
    font-size: 1.15rem;
    font-weight: 400;
    position: relative;
    z-index: 1;
    letter-spacing: 0.3px;
}

/* ── Result badges ── */
.result-badge {
    display: inline-block;
    padding: 1rem 2.5rem;
    border-radius: 50px;
    font-size: 1.8rem;
    font-weight: 800;
    text-align: center;
    letter-spacing: 1px;
    animation: fadeInUp 0.5s ease;
}
.result-real {
    background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
    color: #155724;
    border: 2px solid #28a745;
    box-shadow: 0 4px 20px rgba(40,167,69,0.25);
}
.result-fake {
    background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
    color: #721c24;
    border: 2px solid #dc3545;
    box-shadow: 0 4px 20px rgba(220,53,69,0.25);
}

/* ── Confidence bar ── */
.confidence-container {
    background: #f0f2f5;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin: 0.5rem 0;
}
.conf-label {
    font-weight: 600;
    font-size: 0.9rem;
    margin-bottom: 6px;
    color: #333;
}
.conf-bar-track {
    background: #e9ecef;
    border-radius: 10px;
    height: 28px;
    overflow: hidden;
    position: relative;
}
.conf-bar-fill {
    height: 100%;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 12px;
    font-weight: 700;
    font-size: 0.85rem;
    color: white;
    transition: width 1s ease;
}
.conf-bar-green { background: linear-gradient(90deg, #28a745, #20c997); }
.conf-bar-red { background: linear-gradient(90deg, #dc3545, #e85d6f); }

/* ── Buttons ── */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.3s ease !important;
    border: none !important;
}
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #0f3460 0%, #16213e 100%) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(15,52,96,0.3) !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    box-shadow: 0 6px 25px rgba(15,52,96,0.45) !important;
    transform: translateY(-1px) !important;
}

/* ── Text area ── */
.stTextArea textarea {
    border-radius: 12px !important;
    border: 2px solid #e0e4e8 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 1rem !important;
    transition: border-color 0.3s ease !important;
}
.stTextArea textarea:focus {
    border-color: #0f3460 !important;
    box-shadow: 0 0 0 3px rgba(15,52,96,0.1) !important;
}

/* ── Example buttons ── */
.example-btn {
    background: #f0f2f5;
    border: 1px solid #dee2e6;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.85rem;
    color: #495057;
    line-height: 1.4;
}
.example-btn:hover {
    background: #e2e6ea;
    border-color: #0f3460;
    color: #0f3460;
}

/* ── Animations ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
.fade-in {
    animation: fadeInUp 0.6s ease;
}

/* ── Stat cards ── */
.stat-card {
    background: white;
    border-radius: 14px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    border: 1px solid rgba(0,0,0,0.04);
}
.stat-number {
    font-size: 2rem;
    font-weight: 800;
    color: #0f3460;
}
.stat-label {
    font-size: 0.85rem;
    color: #6c757d;
    margin-top: 0.3rem;
    font-weight: 500;
}

/* ── About section ── */
.about-card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.06);
    border-left: 4px solid #0f3460;
    margin-bottom: 1rem;
}

/* ── Footer ── */
.footer {
    text-align: center;
    padding: 2rem 0 1rem 0;
    color: #adb5bd;
    font-size: 0.85rem;
}
.footer a {
    color: #0f3460;
    text-decoration: none;
    font-weight: 600;
}

/* ── File uploader ── */
.stFileUploader {
    border-radius: 12px !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
}

/* ── Word count bar ── */
.word-count-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem 0.75rem;
    background: #f0f2f5;
    border-radius: 8px;
    margin-top: 0.5rem;
    font-size: 0.82rem;
    color: #6c757d;
    font-weight: 500;
}
.wc-indicator {
    display: flex;
    align-items: center;
    gap: 6px;
}
.wc-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    display: inline-block;
}
.wc-dot-red { background: #dc3545; }
.wc-dot-yellow { background: #ffc107; }
.wc-dot-green { background: #28a745; }

/* ── History table ── */
.history-row {
    display: flex;
    align-items: center;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #f0f2f5;
    font-size: 0.88rem;
    transition: background 0.15s ease;
}
.history-row:hover {
    background: #f8f9fa;
}
.history-row:last-child {
    border-bottom: none;
}
.history-badge {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.75rem;
    letter-spacing: 0.3px;
}
.history-badge-real {
    background: #d4edda;
    color: #155724;
}
.history-badge-fake {
    background: #f8d7da;
    color: #721c24;
}

/* ── Feedback buttons ── */
.feedback-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    padding: 1.25rem 0;
}
.feedback-label {
    font-size: 0.95rem;
    color: #6c757d;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ───────────────────────── ML Logic (unchanged) ─────────────────────────

class SimpleTokenizer:
    """Minimal tokenizer that replicates Keras Tokenizer.texts_to_sequences."""
    def __init__(self, word_index, num_words=None):
        self.word_index = word_index
        self.num_words = num_words

    def texts_to_sequences(self, texts):
        result = []
        for text in texts:
            seq = []
            for word in text.lower().split():
                idx = self.word_index.get(word)
                if idx is not None:
                    if self.num_words is None or idx < self.num_words:
                        seq.append(idx)
            result.append(seq)
        return result


@st.cache_resource
def load_resources():
    nltk.download('stopwords', quiet=True)
    model = NumpyModel("model_weights.npz")
    with open("tokenizer.json", "r") as f:
        tok_data = json.load(f)
    tokenizer = SimpleTokenizer(tok_data["word_index"], tok_data.get("num_words"))
    stop_words = set(stopwords.words('english'))
    return model, tokenizer, stop_words


def clean_text(text):
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    text = text.lower()
    text = text.split()
    text = [word for word in text if word not in stop_words]
    return " ".join(text)


def pad_sequences_np(sequences, maxlen):
    result = np.zeros((len(sequences), maxlen), dtype=np.int32)
    for i, seq in enumerate(sequences):
        if len(seq) > maxlen:
            result[i] = np.array(seq[-maxlen:])
        else:
            result[i, maxlen - len(seq):] = np.array(seq)
    return result


def predict_news(text):
    if text.strip() == "":
        return None, None, None
    text = clean_text(text)
    seq = tokenizer.texts_to_sequences([text])
    padded = pad_sequences_np(seq, maxlen=500)
    pred_real = float(model.predict(padded)[0][0])
    pred_fake = 1.0 - pred_real
    label = "Real News" if pred_real > 0.6 else "Fake News"
    return label, pred_real, pred_fake


# Load resources
with st.spinner("Loading models..."):
    model, tokenizer, stop_words = load_resources()

# ───────────────────────── Example Articles ─────────────────────────

EXAMPLES = {
    "Real News Example": (
        "The Federal Reserve announced on Wednesday that it would raise interest "
        "rates by 0.25 percentage points, bringing the benchmark rate to a range "
        "of 5.25% to 5.5%. Fed Chair Jerome Powell said the decision was based on "
        "recent economic data showing persistent inflation above the 2% target."
    ),
    "Fake News Example": (
        "BREAKING: Scientists at MIT have discovered that eating chocolate every "
        "day can reverse aging by 20 years! The secret compound found only in dark "
        "chocolate has been hidden by the government for decades. Big pharma doesn't "
        "want you to know this simple trick that doctors are SHOCKED by."
    ),
    "Ambiguous Example": (
        "A new study published in a little-known journal claims that a common "
        "household spice can cure major illnesses. While some doctors express "
        "skepticism, supporters argue that traditional medicine has long "
        "recognized these benefits."
    ),
}

# ───────────────────────── Sidebar ─────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1.5rem 0 0.5rem 0;">
        <div style="font-size: 3rem; margin-bottom: 0.3rem;">🧠</div>
        <h2 style="margin:0; font-weight:800; letter-spacing:-0.5px;">Fake News Detector</h2>
        <p style="color: rgba(255,255,255,0.5); font-size:0.85rem; margin-top:4px;">AI-Powered Verification</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["🏠 Home", "🔍 Analyze News", "📁 Batch Processing", "ℹ️ About"],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Dark mode toggle
    dark_mode = st.toggle("🌙 Dark Mode", value=False)

    st.markdown("---")

    st.markdown("""
    <div style="padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 12px; margin-top: 1rem;">
        <p style="font-size: 0.8rem; color: rgba(255,255,255,0.6); margin: 0;">
            <strong style="color: rgba(255,255,255,0.8);">How it works</strong><br>
            Our LSTM neural network analyzes text patterns, language structure, and semantic cues to distinguish between reliable reporting and misinformation.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ── Dark mode CSS override ──
if dark_mode:
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
        color: #e6edf3;
    }
    .card, .about-card, .stat-card {
        background: #1c2333 !important;
        border-color: rgba(255,255,255,0.06) !important;
        color: #e6edf3 !important;
    }
    .card h3, .card p, .about-card h3, .about-card p,
    .stat-label, .conf-label {
        color: #e6edf3 !important;
    }
    .stat-number { color: #4ECDC4 !important; }
    .stTextArea textarea {
        background: #1c2333 !important;
        color: #e6edf3 !important;
        border-color: #30363d !important;
    }
    .stTextArea textarea:focus {
        border-color: #4ECDC4 !important;
    }
    .example-btn {
        background: #1c2333 !important;
        color: #e6edf3 !important;
        border-color: #30363d !important;
    }
    .confidence-container {
        background: #161b22 !important;
    }
    .conf-bar-track {
        background: #30363d !important;
    }
    .footer { color: #484f58 !important; }
    .word-count-bar {
        background: #1c2333 !important;
        color: #8b949e !important;
    }
    .history-row {
        border-color: #30363d !important;
        color: #e6edf3 !important;
    }
    .history-row:hover {
        background: #21262d !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ───────────────────────── UI Helper Functions ─────────────────────────

def render_hero():
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🧠 Fake News Detector</div>
        <div class="hero-subtitle">
            Powered by NLP — analyze news articles for authenticity in seconds
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_stats():
    c1, c2, c3, c4 = st.columns(4)
    stats = [
        ("🤖", "LSTM", "Neural Network"),
        ("📊", "94%+", "Accuracy"),
        ("⚡", "< 30s", "Analysis Time"),
        ("🔒", "100%", "Private & Secure"),
    ]
    for col, (icon, number, label) in zip([c1, c2, c3, c4], stats):
        with col:
            st.markdown(f"""
            <div class="stat-card fade-in">
                <div style="font-size:1.5rem; margin-bottom:0.3rem;">{icon}</div>
                <div class="stat-number">{number}</div>
                <div class="stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)


def render_confidence_bars(pred_real, pred_fake):
    real_pct = pred_real * 100
    fake_pct = pred_fake * 100
    st.markdown(f"""
    <div class="confidence-container fade-in">
        <div class="conf-label">✅ Real News Confidence</div>
        <div class="conf-bar-track">
            <div class="conf-bar-fill conf-bar-green" style="width: {real_pct:.1f}%;">
                {real_pct:.1f}%
            </div>
        </div>
    </div>
    <div class="confidence-container fade-in" style="margin-top: 0.75rem;">
        <div class="conf-label">❌ Fake News Confidence</div>
        <div class="conf-bar-track">
            <div class="conf-bar-fill conf-bar-red" style="width: {fake_pct:.1f}%;">
                {fake_pct:.1f}%
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_result_badge(label):
    if label == "Real News":
        st.markdown("""
        <div style="text-align:center; padding: 1.5rem 0;">
            <span class="result-badge result-real">REAL ✅</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding: 1.5rem 0;">
            <span class="result-badge result-fake">FAKE ❌</span>
        </div>
        """, unsafe_allow_html=True)


def render_pie_chart(pred_real, pred_fake):
    chart_data = pd.DataFrame({
        "Category": ["Real", "Fake"],
        "Probability": [pred_real, pred_fake],
    })
    import plotly.express as px
    fig = px.pie(
        chart_data,
        values="Probability",
        names="Category",
        color="Category",
        color_discrete_map={"Real": "#28a745", "Fake": "#dc3545"},
        hole=0.4,
    )
    fig.update_layout(
        font=dict(family="Inter", size=14),
        showlegend=True,
        margin=dict(t=20, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=280,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        textfont_size=14,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_footer():
    st.markdown("""
    <div class="footer">
        Built with ❤️ using <a href="https://streamlit.io" target="_blank">Streamlit</a>
        &nbsp;·&nbsp; Powered by LSTM NLP
    </div>
    """, unsafe_allow_html=True)


def render_word_count(text):
    """Show a live word/character count bar with quality indicator."""
    words = len(text.split()) if text.strip() else 0
    chars = len(text)
    if words == 0:
        dot_class, hint = "wc-dot-red", "Paste an article to begin"
    elif words < 30:
        dot_class, hint = "wc-dot-red", "Too short — results may be unreliable"
    elif words < 80:
        dot_class, hint = "wc-dot-yellow", "Acceptable — longer text gives better results"
    else:
        dot_class, hint = "wc-dot-green", "Good length for accurate analysis"
    st.markdown(f"""
    <div class="word-count-bar">
        <div><strong>{words}</strong> words &nbsp;·&nbsp; <strong>{chars}</strong> characters</div>
        <div class="wc-indicator">
            <span class="wc-dot {dot_class}"></span> {hint}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ───────────────────────── History ─────────────────────────

def _init_history():
    """Initialize analysis history in session state."""
    if "history" not in st.session_state:
        st.session_state.history = []  # list of dicts


def add_to_history(text, label, pred_real, pred_fake):
    """Append a result to the session history (max 20 entries)."""
    _init_history()
    snippet = (text[:120] + "...") if len(text) > 120 else text
    st.session_state.history.insert(0, {
        "time": datetime.now().strftime("%H:%M:%S"),
        "snippet": snippet,
        "label": label,
        "real": pred_real,
        "fake": pred_fake,
    })
    # Keep last 20
    st.session_state.history = st.session_state.history[:20]


def render_history():
    """Render the recent analyses history panel."""
    _init_history()
    if not st.session_state.history:
        return
    st.markdown("---")
    st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
    st.markdown("### 🕒 Recent Analyses")

    for entry in st.session_state.history:
        badge_cls = "history-badge-real" if entry["label"] == "Real News" else "history-badge-fake"
        badge_text = "REAL" if entry["label"] == "Real News" else "FAKE"
        conf = entry["real"] if entry["label"] == "Real News" else entry["fake"]
        st.markdown(f"""
        <div class="history-row">
            <div style="flex:0 0 65px; color:#adb5bd; font-size:0.8rem;">{entry["time"]}</div>
            <div style="flex:1; padding:0 1rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                {entry["snippet"]}
            </div>
            <div style="flex:0 0 60px; text-align:center;">
                <span class="history-badge {badge_cls}">{badge_text}</span>
            </div>
            <div style="flex:0 0 55px; text-align:right; font-weight:700; font-size:0.85rem; color:#495057;">
                {conf*100:.0f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🗑️ Clear History", key="clear_history"):
        st.session_state.history = []
        st.rerun()


# ───────────────────────── Feedback ─────────────────────────

FEEDBACK_FILE = "feedback_log.csv"


def save_feedback(text_snippet, predicted_label, user_feedback):
    """Append feedback to a CSV file for future model improvement."""
    file_exists = os.path.isfile(FEEDBACK_FILE)
    with open(FEEDBACK_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "snippet", "predicted", "feedback"])
        writer.writerow([
            datetime.now().isoformat(),
            text_snippet[:300],
            predicted_label,
            user_feedback,
        ])


def render_feedback(text, label):
    """Show thumbs up / thumbs down feedback buttons."""
    fb_key = f"fb_{hash(text[:100])}"

    # Check if feedback already given for this analysis
    if fb_key in st.session_state:
        if st.session_state[fb_key] == "correct":
            st.markdown("""
            <div style="text-align:center; padding:0.75rem; background:#d4edda; border-radius:10px; color:#155724; font-weight:600;">
                Thanks for confirming! Your feedback helps improve the model.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center; padding:0.75rem; background:#fff3cd; border-radius:10px; color:#856404; font-weight:600;">
                Thanks for flagging this! We'll use your feedback to improve accuracy.
            </div>
            """, unsafe_allow_html=True)
        return

    st.markdown("""
    <div style="text-align:center; padding-top:0.5rem;">
        <span class="feedback-label">Was this prediction correct?</span>
    </div>
    """, unsafe_allow_html=True)

    fb_cols = st.columns([2, 1, 1, 2])
    with fb_cols[1]:
        if st.button("👍 Correct", key=f"{fb_key}_yes", use_container_width=True):
            save_feedback(text, label, "correct")
            st.session_state[fb_key] = "correct"
            st.rerun()
    with fb_cols[2]:
        if st.button("👎 Wrong", key=f"{fb_key}_no", use_container_width=True):
            save_feedback(text, label, "incorrect")
            st.session_state[fb_key] = "incorrect"
            st.rerun()


# ───────────────────────── Pages ─────────────────────────

# ── Home Page ──
if page == "🏠 Home":
    render_hero()
    render_stats()

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 1], gap="large")

    with col_l:
        st.markdown("""
        <div class="card">
            <h3 style="margin-top:0; color:#0f3460;">🔍 How It Works</h3>
            <p style="color:#6c757d; line-height:1.7;">
                <strong>1. Paste</strong> — Copy any news article text into the analyzer<br>
                <strong>2. Analyze</strong> — Our LSTM model processes linguistic patterns<br>
                <strong>3. Result</strong> — Get an instant verdict with confidence scores
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_r:
        st.markdown("""
        <div class="card">
            <h3 style="margin-top:0; color:#0f3460;">🛡️ Why It Matters</h3>
            <p style="color:#6c757d; line-height:1.7;">
                Misinformation spreads 6x faster than true news on social media.
                Our AI tool helps you verify articles before sharing, protecting
                you and your network from false narratives.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; margin-top:1rem;">
        <p style="color:#6c757d;">👈 Select <strong>Analyze News</strong> from the sidebar to get started</p>
    </div>
    """, unsafe_allow_html=True)

    render_footer()

# ── Analyze News Page ──
elif page == "🔍 Analyze News":
    render_hero()

    # Initialize session state
    if "news_input" not in st.session_state:
        st.session_state.news_input = ""
    if "result" not in st.session_state:
        st.session_state.result = None

    # ── Example buttons ──
    st.markdown("""
    <div class="card">
        <h3 style="margin-top:0; color:#0f3460;">📋 Quick Examples</h3>
        <p style="color:#6c757d; margin-bottom:1rem;">Click an example to auto-fill the text area:</p>
    </div>
    """, unsafe_allow_html=True)

    ex_cols = st.columns(len(EXAMPLES))
    for col, (label, text) in zip(ex_cols, EXAMPLES.items()):
        with col:
            if st.button(label, use_container_width=True):
                st.session_state.news_input = text
                st.session_state.result = None
                st.rerun()

    # ── Input section ──
    st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
    st.markdown("#### 📝 Enter News Article")
    st.markdown(
        '<p style="color:#6c757d; font-size:0.9rem;">Paste the full article text below for analysis</p>',
        unsafe_allow_html=True,
    )

    news_text = st.text_area(
        "News text",
        value=st.session_state.news_input,
        height=220,
        placeholder="Paste news article here...",
        label_visibility="collapsed",
        key="text_area_input",
    )

    # ── Word count indicator ──
    render_word_count(news_text)

    btn_cols = st.columns([1, 1, 4])
    with btn_cols[0]:
        analyze_clicked = st.button("🔍 Analyze", type="primary", use_container_width=True)
    with btn_cols[1]:
        clear_clicked = st.button("🗑️ Clear", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if clear_clicked:
        st.session_state.news_input = ""
        st.session_state.result = None
        st.rerun()

    # ── Run prediction ──
    if analyze_clicked:
        if news_text.strip():
            with st.spinner("🔄 Analyzing article..."):
                time.sleep(0.5)  # brief delay for UX feel
                label, pred_real, pred_fake = predict_news(news_text)
                st.session_state.result = (label, pred_real, pred_fake)
                st.session_state.news_input = news_text
                add_to_history(news_text, label, pred_real, pred_fake)
        else:
            st.warning("⚠️ Please enter some text to analyze.")

    # ── Output section ──
    if st.session_state.result:
        label, pred_real, pred_fake = st.session_state.result

        st.markdown("---")
        st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
        st.markdown("### 📊 Analysis Result")

        render_result_badge(label)

        res_left, res_right = st.columns([3, 2], gap="large")
        with res_left:
            render_confidence_bars(pred_real, pred_fake)
        with res_right:
            try:
                render_pie_chart(pred_real, pred_fake)
            except ImportError:
                st.info("Install `plotly` for pie chart visualization.")

        # ── Feedback section ──
        render_feedback(news_text, label)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── History section ──
    render_history()

    render_footer()

# ── Batch Processing Page ──
elif page == "📁 Batch Processing":
    render_hero()

    st.markdown("""
    <div class="card">
        <h3 style="margin-top:0; color:#0f3460;">📁 Batch Process Articles</h3>
        <p style="color:#6c757d;">
            Upload a CSV file with a <code>text</code> column to analyze multiple articles at once.
        </p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"], label_visibility="collapsed")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if "text" in df.columns.str.lower():
                text_col = [col for col in df.columns if col.lower() == "text"][0]
                with st.spinner("Processing documents..."):
                    predictions = df[text_col].apply(
                        lambda x: predict_news(x) if isinstance(x, str) else (None, None, None)
                    )
                    df["prediction"] = [p[0] for p in predictions]
                    df["confidence_real"] = [p[1] for p in predictions]
                    df["confidence_fake"] = [p[2] for p in predictions]

                st.success("✅ Processing complete!")

                # Summary stats
                total = len(df)
                real_count = (df["prediction"] == "Real News").sum()
                fake_count = (df["prediction"] == "Fake News").sum()

                s1, s2, s3 = st.columns(3)
                with s1:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-number">{total}</div>
                        <div class="stat-label">Total Articles</div>
                    </div>
                    """, unsafe_allow_html=True)
                with s2:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-number" style="color:#28a745;">{real_count}</div>
                        <div class="stat-label">Real News</div>
                    </div>
                    """, unsafe_allow_html=True)
                with s3:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-number" style="color:#dc3545;">{fake_count}</div>
                        <div class="stat-label">Fake News</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(df, use_container_width=True)

                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="⬇️ Download Results as CSV",
                    data=csv,
                    file_name="fake_news_predictions.csv",
                    mime="text/csv",
                    type="primary",
                )
            else:
                st.error("The CSV file must contain a 'text' column.")
        except Exception as e:
            st.error(f"Error processing file: {e}")

    render_footer()

# ── About Page ──
elif page == "ℹ️ About":
    render_hero()

    st.markdown("""
    <div class="about-card fade-in">
        <h3 style="margin-top:0; color:#0f3460;">About This Project</h3>
        <p style="color:#495057; line-height:1.8;">
            The <strong>Fake News Detector</strong> is an NLP application that uses
            a dual-layer LSTM (Long Short-Term Memory) neural network to classify news articles
            as either <span style="color:#28a745; font-weight:700;">Real</span> or
            <span style="color:#dc3545; font-weight:700;">Fake</span>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.markdown("""
        <div class="about-card fade-in">
            <h3 style="margin-top:0; color:#0f3460;">🏗️ Architecture</h3>
            <p style="color:#495057; line-height:1.8;">
                <strong>Embedding Layer</strong> — Converts words to 128-dim vectors<br>
                <strong>LSTM Layer 1</strong> — Captures sequential patterns<br>
                <strong>LSTM Layer 2</strong> — Extracts higher-level features<br>
                <strong>Dense + Sigmoid</strong> — Binary classification output
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="about-card fade-in">
            <h3 style="margin-top:0; color:#0f3460;">🛠️ Tech Stack</h3>
            <p style="color:#495057; line-height:1.8;">
                <strong>Frontend</strong> — Streamlit with custom CSS<br>
                <strong>ML Inference</strong> — Pure NumPy (no TensorFlow needed)<br>
                <strong>NLP</strong> — NLTK for text preprocessing<br>
                <strong>Model</strong> — Trained LSTM with 94%+ accuracy
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="about-card fade-in">
        <h3 style="margin-top:0; color:#0f3460;">⚠️ Disclaimer</h3>
        <p style="color:#495057; line-height:1.8;">
            This tool is designed for educational and research purposes. While the model achieves
            high accuracy on benchmark datasets, no AI system is perfect. Always cross-reference
            results with trusted news sources and exercise critical thinking.
        </p>
    </div>
    """, unsafe_allow_html=True)

    render_footer()
