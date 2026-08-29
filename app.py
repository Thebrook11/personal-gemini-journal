import streamlit as st
from google import genai
import datetime
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(
    page_title="MindPulse AI - Multimodal Wellness Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- High-End Workspace UI Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .gradient-header {
        background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 50%, #172554 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 28px 32px;
        border-radius: 20px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
    }
    
    .metric-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        padding: 16px;
        border-radius: 14px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Management ---
if "journal_db" not in st.session_state:
    st.session_state.journal_db = [
        {"date": "2026-08-25", "mood_score": 7, "mood": "Optimistic", "entry": "Started a new project, felt productive.", "feedback": "Great focus. Maintain steady milestones."},
        {"date": "2026-08-26", "mood_score": 5, "mood": "Stressed", "entry": "Faced unexpected bugs in deployment.", "feedback": "Breathe. High-pressure states require breaks."},
        {"date": "2026-08-27", "mood_score": 8, "mood": "Calm", "entry": "Went for an evening run, clear mind.", "feedback": "Physical movement strongly stabilizes focus."},
        {"date": "2026-08-28", "mood_score": 6, "mood": "Reflective", "entry": "Reviewing long-term goals.", "feedback": "Strategic alignment prevents burnout."}
    ]

# --- Sidebar: Configuration & Analytics ---
with st.sidebar:
    st.markdown("### ⚙️ Workspace Configuration")
    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        placeholder="Paste AI Studio Key...",
        help="Free key from https://aistudio.google.com"
    )
    
    st.markdown("---")
    st.markdown("### 📊 Live Analytics")
    total_entries = len(st.session_state.journal_db)
    avg_mood = sum(item["mood_score"] for item in st.session_state.journal_db) / max(total_entries, 1)
    
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        st.metric("Total Logs", total_entries)
    with col_sb2:
        st.metric("Avg Wellness", f"{avg_mood:.1f}/10")
        
    st.markdown("---")
    st.caption("Engine: **Gemini 3.6 Flash Multimodal** | Architecture: **Zero-Leak Memory State**")

# --- Main App Hero Header ---
st.markdown("""
<div class="gradient-header">
    <h1 style="color: #c7d2fe; margin: 0; font-size: 30px; font-weight: 800;">🧠 MindPulse AI — Cognitive Wellness & Growth Hub</h1>
    <p style="color: #94a3b8; margin: 6px 0 0 0; font-size: 15px;">Multimodal reflection engine combining vision, sentiment telemetry, and algorithmic habit formation.</p>
</div>
""", unsafe_allow_html=True)

# --- Tabs Structure ---
tab_reflect, tab_trends, tab_report = st.tabs(["✍️ Multimodal Journal", "📈 Wellness Telemetry", "📑 Executive Growth Report"])

# ==================== TAB 1: Multimodal Journal ====================
with tab_reflect:
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        st.markdown("##### 📝 Daily Log & Contextual Intake")
        journal_text = st.text_area(
            "Express your thoughts, milestones, or current mental friction:",
            placeholder="Describe your day, cognitive load, or key achievements...",
            height=160
        )
        
        uploaded_image = st.file_uploader(
            "Attach Visual Context (Daily sketch, workspace setup, or whiteboard note):",
            type=["png", "jpg", "jpeg"]
        )
        
        analyze_btn = st.button("🚀 Analyze & Generate Growth Plan", type="primary", use_container_width=True)

    with col_right:
        st.markdown("##### 🎯 Dynamic Analysis Stream")
        result_placeholder = st.empty()
        result_placeholder.info("Provide your thoughts or visual context on the left to trigger the multi-dimensional analysis pipeline.")

    if analyze_btn:
        if not api_key:
            st.error("⚠️ Please configure your Google Gemini API Key in the sidebar.")
        elif not journal_text.strip() and not uploaded_image:
            st.warning("⚠️ Please provide either text reflections or upload an image.")
        else:
            with st.spinner("Executing Multimodal Analysis via Gemini 3.6 Flash..."):
                try:
                    client = genai.Client(api_key=api_key)
                    
                    system_prompt = """You are MindPulse AI, an advanced cognitive performance and psychological wellness coach.
Analyze the provided journal entry (and any attached image).
Provide output strictly formatted with the following headers:

**📊 Mood Score:** [Give an integer score from 1 to 10 based on sentiment]
**😊 Emotional Sentiment:** [Dominant emotional profile]
**💡 Cognitive Reflection:** [2-3 sentences of deeply insightful, evidence-grounded psychological feedback]
**🎯 High-Impact Action Items:**
- [Micro-Action: Next 2 hours]
- [Macro-Habit: Next 7 days]
**🧘 Mindful Grounding Prompt:** [One reflective question for tomorrow morning]
"""
                    contents_payload = [system_prompt, f"User Journal Entry:\n{journal_text}"]
                    
                    if uploaded_image:
                        import io
                        from PIL import Image
                        img = Image.open(uploaded_image)
                        contents_payload.append(img)
                        contents_payload.append("Analyze the emotional tone and environmental context visible in this image alongside the text.")

                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=contents_payload
                    )
                    
                    ai_reply = response.text
                    today_str = datetime.date.today().strftime("%Y-%m-%d")
                    
                    # Heuristic score extraction for telemetry chart
                    mood_val = 7
                    for token in ai_reply.split():
                        if "/10" in token:
                            try:
                                mood_val = int(token.replace("/10", "").strip("*,"))
                            except:
                                pass
                                
                    st.session_state.journal_db.append({
                        "date": today_str,
                        "mood_score": mood_val,
                        "mood": "Analyzed",
                        "entry": journal_text if journal_text else "[Visual Upload Context]",
                        "feedback": ai_reply
                    })
                    
                    with col_right:
                        st.success("✅ Analysis Complete & Recorded!")
                        st.markdown(f"""
                        <div style="background: #1e293b; border: 1px solid #3b82f6; padding: 18px; border-radius: 12px; font-size: 13px;">
                            {ai_reply}
                        </div>
                        """, unsafe_allow_html=True)
                        
                except Exception as e:
                    st.error(f"Execution Error: {e}")

# ==================== TAB 2: Wellness Telemetry ====================
with tab_trends:
    st.markdown("##### 📈 Longitudinal Sentiment & Wellness Telemetry")
    df = pd.DataFrame(st.session_state.journal_db)
    
    if not df.empty:
        fig = px.line(
            df, 
            x="date", 
            y="mood_score", 
            markers=True,
            title="Cognitive Wellness Progression (Scale 1-10)",
            labels={"date": "Timeline", "mood_score": "Wellness Index"},
            template="plotly_dark"
        )
        fig.update_traces(line_color="#818cf8", line_width=3, marker=dict(size=10, color="#6366f1"))
        fig.update_layout(yaxis_range=[1, 10], margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="#0b0f19", plot_bgcolor="#0b0f19")
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("###### Detailed History Archive")
        st.dataframe(df[["date", "mood_score", "entry"]], use_container_width=True)
    else:
        st.info("No timeline data available yet.")

# ==================== TAB 3: Executive Growth Report ====================
with tab_report:
    st.markdown("##### 📑 Automated Cognitive Performance Summary")
    if st.session_state.journal_db:
        st.markdown("""
        **Summary Insights:**
        - **Consistency Streak:** Active Tracking Recorded
        - **Dominant Trend:** Positive Cognitive Stability
        - **Optimization Priority:** Evening Wind-down Routine & Structured Deep-Work Windows
        """)
        
        report_text = f"MINDPULSE COGNITIVE SUMMARY\nGenerated: {datetime.datetime.now()}\n\n"
        for item in st.session_state.journal_db:
            report_text += f"[{item['date']}] Score: {item['mood_score']}/10\nEntry: {item['entry']}\n\n"
            
        st.download_button(
            label="📥 Download Structured Report (.txt)",
            data=report_text,
            file_name=f"mindpulse_report_{datetime.date.today()}.txt",
            mime="text/plain"
        )
    else:
        st.info("Add entries to generate your performance report.")