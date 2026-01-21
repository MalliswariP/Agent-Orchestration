import streamlit as st
import requests


API_URL = "https://agent-orchestration-xgsn.onrender.com"

st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="🧠",
    layout="wide"
)

# ---------- GLOBAL CSS (Dark Gradient + Glass UI) ----------
st.markdown("""
<style>

/* ===== GLOBAL BACKGROUND ===== */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #040404 0%, #0b0f0d 40%, #000000 100%);
    color: #e6e6e6;
    padding-top: 30px;
}

/* ===== CENTER HEADER ===== */
h2 {
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    letter-spacing: 0.4px;
}

p {
    font-family: 'Inter', sans-serif;
}

/* ===== SEARCH TEXTAREA ===== */
textarea {
    border-radius: 12px !important;
    background-color: rgba(22, 26, 24, 0.9) !important;
    border: 1px solid rgba(0, 255, 140, 0.35) !important;
    color: white !important;
    font-size: 16px !important;
    padding: 12px;
    resize: none !important;
    box-shadow: 0 0 10px rgba(0, 255, 140, 0.06);
}

/* ===== RUN BUTTON ===== */
.stButton button {
    background: linear-gradient(90deg, #00ff99, #48ffcb);
    border-radius: 8px;
    border: none;
    padding: 10px 14px;
    font-size: 16px;
    font-weight: 600;
    color: #000;
    letter-spacing: 0.3px;
    cursor: pointer;
    width: 100%;
    box-shadow: 0 0 12px rgba(0,255,140,0.35);
}
.stButton button:hover {
    box-shadow: 0 0 20px rgba(0,255,140,0.55);
    transform: translateY(-1px);
}

/* ===== TABS ===== */
.stTabs [data-baseweb="tab-list"] {
    justify-content: center;
    margin-top: 20px;
}
.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(0,255,160,0.25);
    border-radius: 8px;
    padding: 8px 18px;
    color: #aaffdf;
    font-size: 15px;
    font-weight: 500;
}
.stTabs [data-baseweb="tab"]:hover {
    border-color: #00ff9e;
    color: #00ff9e;
}

/* ===== RESULT CARD ===== */
.card {
    background: rgba(18, 20, 20, 0.65);
    border: 1px solid rgba(0,255,160,0.25);
    border-radius: 12px;
    padding: 18px;
    margin-top: 18px;
    font-size: 16px;
}

/* ===== CARD TITLE ===== */
.title {
    font-size: 20px;
    font-weight: 600;
    color: #00ffbf;
    margin-bottom: 6px;
    font-family: 'Inter', sans-serif;
}

/* ===== ALIGN OUTPUT WITH INPUT ===== */
[data-testid="stTabs"] {
    max-width: 850px;
    margin: 0 auto;
}
textarea, .stButton {
    max-width: 850px;
    margin: 0 auto;
}
            /* ================= REMOVE TOP WHITE BAR ================= */
header[data-testid="stHeader"] {
    background: transparent !important;
    color: transparent !important;
    height: 0px !important;
}

[data-testid="stToolbar"] {
    display: none !important;
}

/* Remove extra top padding */
.css-18e3th9 {
    padding-top: 0 !important;
}

.block-container {
    padding-top: 10px !important;
}

</style>
""", unsafe_allow_html=True)



# ---------- HEADER ----------
st.markdown(
    "<h2 style='text-align:center; font-family:Verdana;'>🧠 Multi-Agent Research + Summarize + Email System</h2>"
    "<p style='text-align:center; color:#ccc; font-size:14px;'>Gemini + Wikipedia + WebSearch + Arxiv</p>",
    unsafe_allow_html=True
)


# ---------- INPUT ----------
col1, col2, col3 = st.columns([1,2,1])
with col2:
    query = st.text_area(
        "Enter your query:",
        height=110,
        placeholder="Ex: Research blockchain, summarize quantum computing, email about AI in healthcare"
    )

with col2:
    run = st.button("Run Agents", use_container_width=True)


# ---------- QUIT IF EMPTY ----------
if run and not query.strip():
    st.warning("Please enter a valid query")
    st.stop()


# ---------- CALL BACKEND ----------
if run:
    with st.spinner("AI Agents Working..."):
        resp = requests.post(API_URL, json={"query": query})
        if resp.status_code != 200:
            st.error("Backend error occurred")
            st.write(resp.text)
            st.stop()

        data = resp.json()

    # ---------- TABS LAYOUT ----------
    tab1, tab2, tab3 = st.tabs(["📚 Research", "✍️ Summary", "✉️ Email"])

    # -------- TAB 1: RESEARCH --------
    with tab1:
        research = data.get("research")
        if research:
            wiki = research.get("wiki_web")
            arxiv = research.get("arxiv")

            if wiki:
                st.markdown("<div class='card'><div class='title'>Wikipedia + Web Results</div>" + wiki + "</div>", unsafe_allow_html=True)

            if arxiv:
                st.markdown("<div class='card'><div class='title'>Arxiv (Top-5 Papers)</div>" + arxiv + "</div>", unsafe_allow_html=True)

    # -------- TAB 2: SUMMARY --------
    with tab2:
        summary = data.get("summary")
        if summary:
            st.markdown("<div class='card'><div class='title'>Structured Summary</div>" + summary + "</div>", unsafe_allow_html=True)

    # -------- TAB 3: EMAIL --------
    with tab3:
        email = data.get("email")
        if email:
            email = email.replace("\n", "<br>")
            st.markdown("<div class='card'><div class='title'>Formal Email</div>" + email + "</div>", unsafe_allow_html=True)
