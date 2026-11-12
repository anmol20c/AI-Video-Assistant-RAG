import os
import re
import io
import json
import tempfile
from datetime import datetime
from xml.sax.saxutils import escape

import streamlit as st
from main import run_pipeline


# -------------------------------------------------------------------
# VYBE AI — immersive video intelligence workspace
# -------------------------------------------------------------------
st.set_page_config(
    page_title="VYBE AI | Video Intelligence",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- DESIGN SYSTEM -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    :root {
      --bg:#070a13; --panel:#11182a; --line:rgba(159,177,255,.16);
      --muted:#9ba8c7; --text:#f4f6ff; --cyan:#6ee7ff;
      --violet:#ad91ff; --pink:#f2a7ee; --green:#61e6b4;
    }
    html, body, [data-testid="stAppViewContainer"] {
      background:
        radial-gradient(ellipse at 12% 0%,rgba(92,73,205,.22),transparent 34%),
        radial-gradient(ellipse at 92% 12%,rgba(29,185,211,.13),transparent 29%),
        var(--bg);
      color:var(--text); font-family:'DM Sans',sans-serif;
    }
    [data-testid="stHeader"] {background:rgba(7,10,19,.72);}
    [data-testid="stSidebar"] {
      background:linear-gradient(180deg,#10172a 0%,#090e1b 100%);
      border-right:1px solid var(--line);
    }
    [data-testid="stMainBlockContainer"] {max-width:1500px;padding-top:1.5rem;padding-bottom:3rem;}
    h1,h2,h3,h4,.brand,.hero-title,.metric-value {font-family:'Space Grotesk',sans-serif!important;}
    p, label, span {letter-spacing:.01em;}
    .brand {font-size:1.05rem;font-weight:700;letter-spacing:.2em;color:#f2f8ff;}
    .brand-mark {
      display:inline-flex;width:35px;height:35px;align-items:center;justify-content:center;
      border-radius:12px;margin-right:9px;color:#07101c;font-weight:900;
      background:linear-gradient(135deg,var(--cyan),var(--violet));
      box-shadow:0 0 28px rgba(110,231,255,.4);
    }
    .hero {
      position:relative;overflow:hidden;padding:42px 42px 38px;border-radius:28px;
      border:1px solid rgba(160,180,255,.22);
      background:linear-gradient(115deg,rgba(28,39,72,.97),rgba(13,21,40,.94) 58%,rgba(39,26,69,.92));
      box-shadow:0 22px 80px rgba(0,0,0,.28);margin-bottom:26px;
      animation:rise .7s ease both;
    }
    .hero:before,.hero:after {content:"";position:absolute;border-radius:50%;filter:blur(45px);pointer-events:none;}
    .hero:before {width:340px;height:340px;right:-90px;top:-190px;background:rgba(110,231,255,.22);animation:drift 8s ease-in-out infinite alternate;}
    .hero:after {width:280px;height:280px;right:190px;bottom:-230px;background:rgba(173,145,255,.25);animation:drift 10s ease-in-out infinite alternate-reverse;}
    .hero-content {position:relative;z-index:1;}
    .eyebrow,.kicker {color:var(--cyan);font-size:.72rem;font-weight:700;letter-spacing:.2em;text-transform:uppercase;}
    .hero-title {font-size:clamp(2.1rem,4.6vw,3.8rem);line-height:1.04;font-weight:700;margin:13px 0;}
    .gradient-text {background:linear-gradient(90deg,#75eaff,#b8a3ff 55%,#f3a9ed);-webkit-background-clip:text;background-clip:text;color:transparent;}
    .hero-sub {color:#b8c4e0;max-width:720px;font-size:1rem;line-height:1.75;}
    .live-pill {display:inline-flex;align-items:center;gap:9px;padding:8px 13px;border:1px solid rgba(110,231,255,.25);border-radius:999px;background:rgba(110,231,255,.07);color:#c5f7ff;font-size:.72rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;}
    .live-dot {width:8px;height:8px;border-radius:50%;background:var(--green);box-shadow:0 0 13px var(--green);animation:pulse 1.5s infinite;}
    .glass-card {background:linear-gradient(145deg,rgba(24,33,57,.88),rgba(13,20,37,.86));border:1px solid var(--line);border-radius:19px;padding:20px 22px;box-shadow:0 12px 38px rgba(0,0,0,.16);height:100%;transition:transform .25s,border-color .25s;}
    .glass-card:hover {transform:translateY(-3px);border-color:rgba(110,231,255,.35);}
    .metric-label {color:var(--muted);font-size:.72rem;text-transform:uppercase;letter-spacing:.13em;}
    .metric-value {color:#f7f8ff;font-size:1.85rem;font-weight:700;margin-top:7px;}
    .metric-note {color:#8492b3;font-size:.77rem;margin-top:3px;}
    .section-title {font-family:'Space Grotesk';font-size:1.45rem;font-weight:700;margin:4px 0 15px;color:#f4f6ff;}
    .soft-note {color:#9ba8c7;font-size:.87rem;line-height:1.65;}
    .chip {display:inline-block;padding:6px 10px;border-radius:8px;margin:4px 5px 0 0;border:1px solid rgba(173,145,255,.22);background:rgba(173,145,255,.08);color:#d9ceff;font-size:.74rem;}
    .feature-row {display:flex;gap:13px;align-items:flex-start;margin:15px 0;}
    .feature-icon {width:36px;height:36px;display:grid;place-items:center;border-radius:11px;background:linear-gradient(135deg,rgba(110,231,255,.16),rgba(173,145,255,.18));font-size:1.15rem;flex-shrink:0;}
    .stButton>button,.stDownloadButton>button {
      border:0!important;border-radius:12px!important;padding:.72rem 1.1rem!important;
      font-weight:700!important;color:#07101c!important;
      background:linear-gradient(100deg,#72e5fb,#b7a1ff)!important;
      box-shadow:0 8px 26px rgba(104,225,253,.17)!important;
      transition:transform .2s ease,box-shadow .2s ease!important;
    }
    .stButton>button:hover,.stDownloadButton>button:hover {transform:translateY(-2px);box-shadow:0 13px 32px rgba(167,139,250,.3)!important;}
    .stTextInput input,.stTextArea textarea,[data-baseweb="select"]>div {
      background:#10182b!important;color:#f4f6ff!important;border-color:rgba(155,174,255,.2)!important;border-radius:11px!important;
    }
    [data-testid="stFileUploader"] {background:rgba(15,23,42,.58);border:1px dashed rgba(110,231,255,.38);border-radius:15px;padding:10px;}
    .stTabs [data-baseweb="tab-list"] {gap:8px;border-bottom:1px solid var(--line);}
    .stTabs [data-baseweb="tab"] {background:rgba(20,29,50,.55);border:1px solid transparent;border-radius:10px 10px 0 0;color:#aab6d2;padding:10px 15px;}
    .stTabs [aria-selected="true"] {color:#c8f7ff!important;border-color:var(--line)!important;}
    [data-testid="stChatMessage"] {background:rgba(19,28,49,.75);border:1px solid var(--line);border-radius:15px;}
    [data-testid="stProgressBar"]>div>div {background:linear-gradient(90deg,#65e5fb,#a88cff,#f0a6ed);}
    .status-strip {padding:12px 15px;border:1px solid var(--line);border-radius:12px;background:rgba(15,23,42,.6);color:#b7c4e2;font-size:.83rem;}
    .footer {text-align:center;color:#65718f;font-size:.76rem;padding:30px 0 8px;}
    @keyframes drift {from{transform:translate(0,0) scale(1)}to{transform:translate(-35px,25px) scale(1.18)}}
    @keyframes pulse {0%,100%{opacity:1;transform:scale(1)}50%{opacity:.45;transform:scale(.8)}}
    @keyframes rise {from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
    @keyframes shimmer {0%{background-position:-500px 0}100%{background-position:500px 0}}
    #MainMenu,footer {visibility:hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------- STATE -----------------------------
for key, default in {
    "result": None,
    "chat_history": [],
    "processed_at": None,
    "language": "english",
    "source_name": "",
    "saved_reports": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def clean_text(value):
    return str(value).strip() if value is not None else ""


def metric_card(label, value, note):
    st.markdown(
        f"""<div class="glass-card"><div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>""",
        unsafe_allow_html=True,
    )


def build_report_text(result, processed_at):
    title = clean_text(result.get("title")) or "Untitled session"
    sections = [
        ("Executive Summary", result.get("summary")),
        ("Action Items", result.get("action_items")),
        ("Key Decisions", result.get("key_decisions")),
        ("Open Questions", result.get("open_questions")),
        ("Full Transcript", result.get("transcript")),
    ]
    body = [f"# {title}", f"Processed: {processed_at or 'N/A'}", ""]
    for heading, content in sections:
        body.extend([f"## {heading}", clean_text(content) or "Not available.", ""])
    return "\n".join(body)


def build_pdf(result, processed_at):
    """Create a downloadable PDF report using ReportLab."""
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase import pdfmetrics

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=17*mm, leftMargin=17*mm,
        topMargin=18*mm, bottomMargin=18*mm,
        title=clean_text(result.get("title")) or "VYBE AI Report",
        author="VYBE AI",
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="VYBETitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=23, leading=28, textColor=colors.HexColor("#25345D"),
        alignment=TA_LEFT, spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="VYBEHeading", parent=styles["Heading2"], fontSize=13,
        leading=17, textColor=colors.HexColor("#4657A5"),
        spaceBefore=13, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="VYBEBody", parent=styles["BodyText"], fontSize=9,
        leading=13, textColor=colors.HexColor("#263248"), spaceAfter=5,
        wordWrap="CJK",
    ))
    story = [
        Paragraph("VYBE AI", ParagraphStyle(
            "brandpdf", parent=styles["Normal"], fontSize=9,
            textColor=colors.HexColor("#168CA7"), spaceAfter=8
        )),
        Paragraph(escape(clean_text(result.get("title")) or "Untitled session"), styles["VYBETitle"]),
        Paragraph(f"Generated on: {escape(processed_at or 'N/A')}", styles["BodyText"]),
        Spacer(1, 8),
    ]
    sections = [
        ("Executive Summary", result.get("summary")),
        ("Action Items", result.get("action_items")),
        ("Key Decisions", result.get("key_decisions")),
        ("Open Questions", result.get("open_questions")),
        ("Full Transcript", result.get("transcript")),
    ]
    for heading, content in sections:
        story.append(Paragraph(escape(heading), styles["VYBEHeading"]))
        raw = clean_text(content) or "Not available."
        # Preserve paragraph breaks while escaping user/transcript content.
        for paragraph in raw.splitlines() or [raw]:
            if paragraph.strip():
                story.append(Paragraph(escape(paragraph).replace("  ", "&nbsp;&nbsp;"), styles["VYBEBody"]))
            else:
                story.append(Spacer(1, 4))
    def footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#DCE4F2"))
        canvas.line(17*mm, 13*mm, A4[0]-17*mm, 13*mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#7A8498"))
        canvas.drawString(17*mm, 8*mm, "VYBE AI • Video Intelligence Report")
        canvas.drawRightString(A4[0]-17*mm, 8*mm, f"Page {document.page}")
        canvas.restoreState()
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    buffer.seek(0)
    return buffer.getvalue()


# ----------------------------- SIDEBAR -----------------------------
with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-mark">✦</span>VYBE AI</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Your intelligence studio")
    st.markdown('<div class="soft-note">Turn long videos, lectures and meetings into searchable knowledge.</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**POWERED WORKFLOWS**")
    st.markdown(
        '<span class="chip">Whisper / Sarvam</span><span class="chip">Groq LLM</span>'
        '<span class="chip">ChromaDB</span><span class="chip">RAG Chat</span>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("**ANALYSIS PIPELINE**")
    for number, label in [
        ("01", "Audio extraction"), ("02", "Speech transcription"),
        ("03", "AI summarization"), ("04", "Insight extraction"),
        ("05", "Vector indexing"), ("06", "Ask your content"),
    ]:
        st.markdown(
            f'<div style="display:flex;gap:12px;align-items:center;margin:13px 0;color:#aab6d2">'
            f'<span style="color:#73e5fb;font-size:.75rem;font-weight:700">{number}</span><span>{label}</span></div>',
            unsafe_allow_html=True,
        )
    st.markdown("---")
    if st.session_state.result:
        st.success("Workspace: analysis ready")
        if st.button("＋ Start a new analysis", use_container_width=True):
            st.session_state.result = None
            st.session_state.chat_history = []
            st.session_state.processed_at = None
            st.session_state.source_name = ""
            st.rerun()
    st.caption("VYBE AI • BUILT WITH PYTHON")


# ----------------------------- HERO -----------------------------
st.markdown(
    """
    <div class="hero"><div class="hero-content">
      <div class="eyebrow">Your content. Understood.</div>
      <div class="hero-title">Meet your new<br><span class="gradient-text">AI Video Assistant.</span></div>
      <div class="hero-sub">Drop in a YouTube link or an audio/video file. Get a polished transcript,
      meeting-ready insights, and a conversational AI that can answer questions from the content itself.</div>
      <br><span class="live-pill"><span class="live-dot"></span> Intelligence workspace online</span>
    </div></div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------- INPUT -----------------------------
left, right = st.columns([1.25, 0.75], gap="large")
with left:
    st.markdown('<div class="kicker">01 / Start with a source</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Bring your content</div>', unsafe_allow_html=True)
    source_type = st.radio("Choose input type", ["YouTube URL", "Upload a file"], horizontal=True, label_visibility="collapsed")
    youtube_url, uploaded_file = "", None
    if source_type == "YouTube URL":
        youtube_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...", help="Paste a public YouTube video URL.")
    else:
        uploaded_file = st.file_uploader(
            "Upload audio or video",
            type=["mp3", "wav", "m4a", "mp4", "mpeg", "mpga", "webm", "ogg", "mov", "avi"],
            help="Supported audio and video formats.",
        )
    language = st.selectbox(
        "Spoken language", ["english", "hinglish"],
        format_func=lambda x: "English · Whisper" if x == "english" else "Hinglish · Sarvam AI",
    )
    process_clicked = st.button("✦  Analyse my content", use_container_width=True)

with right:
    st.markdown('<div class="kicker">02 / What you get</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">From media to meaning</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="glass-card">
          <div class="feature-row"><div class="feature-icon">◈</div><div><b>Executive summary</b><div class="soft-note">A clean overview of the most important discussion.</div></div></div>
          <div class="feature-row"><div class="feature-icon">↗</div><div><b>Actionable intelligence</b><div class="soft-note">Action items, decisions and unanswered questions.</div></div></div>
          <div class="feature-row"><div class="feature-icon">✧</div><div><b>Grounded AI chat</b><div class="soft-note">Ask questions and explore your transcript with RAG.</div></div></div>
          <div class="feature-row"><div class="feature-icon">⇩</div><div><b>Portable reports</b><div class="soft-note">Download a formatted PDF, Markdown report or transcript.</div></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------------------- PROCESSING WITH REAL PROGRESS -----------------------------
if process_clicked:
    if source_type == "YouTube URL" and not youtube_url.strip():
        st.error("Please paste a YouTube URL first.")
    elif source_type == "Upload a file" and uploaded_file is None:
        st.error("Please upload an audio or video file first.")
    else:
        local_source = None
        temp_path = None
        try:
            if source_type == "YouTube URL":
                local_source = youtube_url.strip()
                source_name = youtube_url.strip()
            else:
                os.makedirs("downloads", exist_ok=True)
                suffix = os.path.splitext(uploaded_file.name)[1] or ".mp4"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir="downloads") as temp_file:
                    temp_file.write(uploaded_file.getbuffer())
                    temp_path = temp_file.name
                local_source = temp_path
                source_name = uploaded_file.name

            st.markdown("### ✦ Building your intelligence report")
            progress_bar = st.progress(0)
            progress_label = st.empty()
            progress_detail = st.empty()

            def report_progress(percent, message):
                percent = max(0, min(100, int(percent)))
                progress_bar.progress(percent)
                progress_label.markdown(f"**{percent}%** · {message}")
                progress_detail.markdown(
                    f'<div class="status-strip">{"▰" * (percent // 10)}{"▱" * (10 - percent // 10)} &nbsp; Processing your content securely in this session</div>',
                    unsafe_allow_html=True,
                )

            result = run_pipeline(local_source, language, progress_callback=report_progress)
            progress_bar.progress(100)
            progress_label.success("100% · Your AI analysis is ready!")
            st.session_state.result = result
            st.session_state.chat_history = []
            st.session_state.processed_at = datetime.now().strftime("%d %b %Y, %I:%M %p")
            st.session_state.language = language
            st.session_state.source_name = source_name
            st.toast("Your analysis is ready!")
            st.rerun()
        except Exception as exc:
            st.error(f"Processing failed: {exc}")
            with st.expander("Technical details"):
                st.exception(exc)
        finally:
            # The temporary upload is retained in downloads/ for optional reuse.
            pass

# ----------------------------- RESULTS -----------------------------
result = st.session_state.result
if result:
    st.markdown("---")
    title = clean_text(result.get("title")) or "Untitled session"
    transcript = clean_text(result.get("transcript"))
    summary = clean_text(result.get("summary"))
    action_items = clean_text(result.get("action_items"))
    decisions = clean_text(result.get("key_decisions"))
    questions = clean_text(result.get("open_questions"))
    processed_at = st.session_state.processed_at
    word_count = len(transcript.split()) if transcript else 0
    reading_minutes = max(1, round(word_count / 150)) if word_count else 0

    st.markdown('<div class="kicker">Analysis complete</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title" style="font-size:1.9rem">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="soft-note">Processed {processed_at or ""} · {st.session_state.source_name or "Your source"} · Workspace ready</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4, gap="medium")
    with m1: metric_card("Transcript words", f"{word_count:,}", "Recognised words")
    with m2: metric_card("Reading time", f"{reading_minutes} min", "Estimated reading time")
    with m3: metric_card("AI insight groups", "03", "Summary · decisions · actions")
    with m4: metric_card("Knowledge base", "Ready", "RAG search enabled")

    overview_tab, transcript_tab, insights_tab, chat_tab, exports_tab = st.tabs(
        ["✦ Overview", "≋ Transcript", "◈ Key insights", "⌘ Ask your content", "⇩ Export centre"]
    )

    with overview_tab:
        a, b = st.columns([1.5, .75], gap="large")
        with a:
            st.markdown("#### Executive summary")
            st.markdown(summary or "_No summary was generated._")
            st.markdown("#### At a glance")
            st.markdown(
                '<span class="chip">AI-generated summary</span><span class="chip">Searchable transcript</span><span class="chip">Context-aware Q&A</span>',
                unsafe_allow_html=True,
            )
        with b:
            st.markdown("#### Session snapshot")
            with st.container(border=True):
                st.write("**Source**", st.session_state.source_name or "Not recorded")
                st.write("**Language engine**", "Sarvam AI" if st.session_state.language == "hinglish" else "Whisper")
                st.write("**Processed**", processed_at or "N/A")
                st.write("**Transcript size**", f"{word_count:,} words")

    with transcript_tab:
        st.markdown("#### Full transcript")
        st.caption(f"{word_count:,} words · Use search to jump to matching content")
        search_term = st.text_input("Search transcript", placeholder="Search a word, topic or phrase...")
        if search_term:
            matches = [line for line in transcript.splitlines() if search_term.lower() in line.lower()]
            st.info(f"Found {len(matches)} matching line(s).")
            st.text_area("Search results", value="\n".join(matches) if matches else "No matching lines found.", height=180)
        st.text_area("Transcript", value=transcript, height=480, label_visibility="collapsed")
        st.download_button("↓ Download transcript (.txt)", data=transcript, file_name="vybe_transcript.txt", mime="text/plain")

    with insights_tab:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            st.markdown("#### ↗ Action items")
            with st.container(border=True):
                st.markdown(action_items or "_No action items found._")
            st.markdown("#### Key decisions")
            with st.container(border=True):
                st.markdown(decisions or "_No key decisions found._")
        with c2:
            st.markdown("#### Open questions")
            with st.container(border=True):
                st.markdown(questions or "_No open questions found._")
            st.markdown("#### Session details")
            with st.container(border=True):
                st.write("**Title:**", title)
                st.write("**Processed:**", processed_at)
                st.write("**Language:**", st.session_state.language.title())

    with chat_tab:
        st.markdown("#### Talk to this video")
        st.markdown('<div class="soft-note">Ask specific questions about the content. Answers are generated using the transcript indexed for this session.</div>', unsafe_allow_html=True)
        chat_col, action_col = st.columns([1, .25])
        with action_col:
            if st.button("Clear chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        prompt = st.chat_input("Ask something about this video...")
        if prompt:
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Searching your transcript..."):
                    try:
                        answer = result["rag_chain"].invoke(prompt)
                    except Exception as exc:
                        answer = f"I couldn't complete that answer: {exc}"
                    st.markdown(answer)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})

    with exports_tab:
        st.markdown("#### Your report, ready to take anywhere")
        st.markdown('<div class="soft-note">Download a formatted PDF for sharing, a Markdown report for editing, or individual text files for reference.</div>', unsafe_allow_html=True)
        report_text = build_report_text(result, processed_at)
        d1, d2, d3 = st.columns(3, gap="medium")
        with d1:
            st.markdown("**Complete PDF report**")
            try:
                pdf_bytes = build_pdf(result, processed_at)
                st.download_button(
                    "↓ Download PDF",
                    data=pdf_bytes,
                    file_name="VYBE_AI_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
                st.caption("Includes summary, actions, decisions, questions and transcript.")
            except ImportError:
                st.warning("PDF export requires ReportLab. Install it with: pip install reportlab")
            except Exception as exc:
                st.error(f"Could not build PDF: {exc}")
        with d2:
            st.markdown("**Editable report**")
            st.download_button(
                "↓ Download Markdown",
                data=report_text,
                file_name="VYBE_AI_Report.md",
                mime="text/markdown",
                use_container_width=True,
            )
            st.caption("Best for editing or keeping project notes.")
        with d3:
            st.markdown("**Plain transcript**")
            st.download_button(
                "↓ Download TXT",
                data=transcript,
                file_name="VYBE_Transcript.txt",
                mime="text/plain",
                use_container_width=True,
            )
            st.caption("Lightweight transcript-only export.")
        st.markdown("---")
        st.markdown("#### Export your AI conversation")
        chat_export = "\n\n".join(
            f"{'You' if m['role'] == 'user' else 'VYBE AI'}:\n{m['content']}"
            for m in st.session_state.chat_history
        )
        st.download_button(
            "↓ Download chat history",
            data=chat_export or "No chat messages yet.",
            file_name="VYBE_AI_Chat_History.txt",
            mime="text/plain",
            use_container_width=True,
        )

else:
    st.markdown("---")
    st.markdown(
        """
        <div class="glass-card" style="text-align:center;padding:38px 20px">
          <div style="font-size:2.2rem;margin-bottom:12px">✧</div>
          <div style="font-family:'Space Grotesk';font-size:1.25rem;font-weight:700;color:#eef3ff">
            Your next great insight starts here
          </div>
          <div class="soft-note" style="max-width:590px;margin:9px auto 0">
            Add a YouTube link or upload a recording above. Your transcript, insights,
            progress tracker and AI-powered Q&A will appear here.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="footer">VYBE AI · VIDEO INTELLIGENCE, REIMAGINED ✦</div>', unsafe_allow_html=True)
