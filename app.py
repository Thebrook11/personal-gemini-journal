import streamlit as st
from google import genai
from PIL import Image
import datetime
import pandas as pd
import plotly.express as px
import re

# --- 1. Page Config ---
st.set_page_config(
    page_title="Personal Gemini Journal",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. Clean High-End UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        border: 1px solid #334155;
        padding: 24px 30px;
        border-radius: 18px;
        margin-bottom: 24px;
    }
    .hero-title {
        color: #c7d2fe;
        font-size: 28px;
        font-weight: 800;
        margin: 0;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 14px;
        margin-top: 6px;
    }
    .reflection-box {
        background: #0f172a;
        border: 1px solid #3b82f6;
        padding: 20px;
        border-radius: 14px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. Key from Secrets ---
api_key = st.secrets.get("GEMINI_API_KEY", "")

# --- 4. Mock History for Instant Graph ---
if "journal_db" not in st.session_state:
    st.session_state.journal_db = [
        {"date": "2026-08-26", "mood_score": 7, "sentiment": "Motivated", "entry": "Kicked off architecture setup.", "feedback": "High focus and clarity."},
        {"date": "2026-08-27", "mood_score": 5, "sentiment": "Overwhelmed", "entry": "Faced environment blockers.", "feedback": "Structured breaks help reduce cognitive load."},
        {"date": "2026-08-28", "mood_score": 8, "sentiment": "Accomplished", "entry": "Resolved blockers, pipeline ready.", "feedback": "Strong resilience loop."}
    ]

# --- 5. Sidebar Live Telemetry ---
with st.sidebar:
    st.markdown("### 📊 Live Analytics")
    total_entries = len(st.session_state.journal_db)
    avg_score = sum(x["mood_score"] for x in st.session_state.journal_db) / max(total_entries, 1)
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Total Logs", total_entries)
    with c2:
        st.metric("Avg Wellness", f"{avg_score:.1f}/10")
        
    st.markdown("---")
    st.markdown("""
    **Core Stack:**
    - **Engine:** `gemini-2.5-flash`
    - **Vision:** Multimodal OCR & Mood Parsing
    - **Security:** In-Memory Zero-Leak Secrets
    """)

# --- 6. Hero Header ---
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🧠 Personal Gemini Journal</div>
    <div class="hero-subtitle">Multimodal cognitive journaling, sentiment telemetry, and algorithmic personal growth.</div>
</div>
""", unsafe_allow_html=True)

# --- 7. Main Tabs ---
tab_log, tab_telemetry, tab_export = st.tabs(["✍️ Reflection Studio", "📈 Longitudinal Telemetry", "📑 Executive Growth Report"])

# TAB 1: Journal Input + Vision
with tab_log:
    col_in, col_out = st.columns([3, 2])
    
    with col_in:
        st.markdown("##### 📝 Daily Log Intake")
        entry_text = st.text_area(
            "Express thoughts, challenges, or daily wins:",
            placeholder="How was your day? What went well or where did you face resistance?",
            height=140
        )
        
        uploaded_image = st.file_uploader(
            "Attach Visual Context (Handwritten note, journal photo, or whiteboard):",
            type=["png", "jpg", "jpeg"]
        )
        
        submit_btn = st.button("🚀 Analyze & Save Reflection", type="primary", use_container_width=True)

    with col_out:
        st.markdown("##### 🎯 Cognitive Insights Stream")
        status_box = st.empty()
        status_box.info("Write your thoughts or upload a note image on the left to start AI analysis.")

    if submit_btn:
        if not api_key:
            st.error("⚠️ API Key bhetli nahi! Streamlit secrets madhe GEMINI_API_KEY set kara.")
        elif not entry_text.strip() and not uploaded_image:
            st.warning("⚠️ Kahi tri text liha kiva photo upload kara.")
        else:
            with st.spinner("Gemini 2.5 Flash analyzing multimodal context..."):
                try:
                    client = genai.Client(api_key=api_key)
                    
                    system_prompt = """You are an advanced cognitive performance and psychological wellness coach.
Analyze the provided journal entry (and any attached image/notes).
Strictly output your response with these exact headers:

**Score:** [Integer between 1 and 10 representing overall mental positivity/clarity]
**😊 Sentiment Profile:** [Single dominant emotion, e.g., Focused, Reflective, Energized, Stressed]
**💡 Cognitive Reflection:** [2-3 empathetic, deeply analytical sentences addressing their state]
**🎯 High-Impact Action Items:**
- [Micro-Action: Next 2 hours]
- [Macro-Habit: Next 7 days]
**🧘 Morning Grounding Prompt:** [One actionable reflection question for tomorrow]
"""
                    payload = [system_prompt, f"User Journal Log:\n{entry_text}"]
                    
                    if uploaded_image:
                        img = Image.open(uploaded_image)
                        payload.append(img)
                        payload.append("Extract text and emotional context from this image and incorporate it into the reflection.")

                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=payload
                    )
                    
                    ai_text = response.text
                    today_str = datetime.date.today().strftime("%Y-%m-%d")
                    
                    score_match = re.search(r"\*\*Score:\*\*\s*(\d+)", ai_text)
                    mood_score = int(score_match.group(1)) if score_match else 7
                    
                    sentiment_match = re.search(r"\*\*😊 Sentiment Profile:\*\*\s*(.+)", ai_text)
                    sentiment_val = sentiment_match.group(1).strip() if sentiment_match else "Reflective"

                    st.session_state.journal_db.append({
                        "date": today_str,
                        "mood_score": mood_score,
                        "sentiment": sentiment_val,
                        "entry": entry_text if entry_text else "[Multimodal Visual Upload]",
                        "feedback": ai_text
                    })
                    
                    with col_out:
                        st.success("✅ Log saved & telemetry updated!")
                        st.markdown(f'<div class="reflection-box">{ai_text}</div>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error: {e}")

# TAB 2: Telemetry Graph
with tab_telemetry:
    st.markdown("##### 📈 Longitudinal Cognitive Telemetry")
    df = pd.DataFrame(st.session_state.journal_db)
    
    if not df.empty:
        fig = px.line(
            df,
            x="date",
            y="mood_score",
            markers=True,
            title="Mental Clarity & Wellness Progression (Scale 1-10)",
            labels={"date": "Timeline", "mood_score": "Cognitive Clarity Score"},
            template="plotly_dark"
        )
        fig.update_traces(line_color="#818cf8", line_width=3, marker=dict(size=10, color="#6366f1"))
        fig.update_layout(yaxis_range=[1, 10], margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="#0b0f19", plot_bgcolor="#0b0f19")
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("###### Complete Archive")
        st.dataframe(df[["date", "mood_score", "sentiment", "entry"]], use_container_width=True)

# TAB 3: Report Download
with tab_export:
    st.markdown("##### 📑 Executive Growth Summary")
    if st.session_state.journal_db:
        st.markdown("""
        **System Highlights:**
        - **Consistency Rate:** Active Routine
        - **Dominant Mental State:** Upward Momentum
        - **Next Focus:** Strategic Rest Windows & Deep Work Sprints
        """)
        
        export_content = f"PERSONAL GEMINI JOURNAL - PROGRESS REPORT\nGenerated: {datetime.datetime.now()}\n\n"
        for item in st.session_state.journal_db:
            export_content += f"[{item['date']}] Score: {item['mood_score']}/10 | State: {item['sentiment']}\nLog: {item['entry']}\nFeedback:\n{item['feedback']}\n{'-'*50}\n"
            
        st.download_button(
            label="📥 Download Complete Report (.txt)",
            data=export_content,
            file_name=f"gemini_journal_report_{datetime.date.today()}.txt",
            mime="text/plain"
        )