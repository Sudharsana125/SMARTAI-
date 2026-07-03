"""
app.py - Ultimate Premium Neon UI v3
"""
import sys, time, datetime
from pathlib import Path
from collections import Counter
import streamlit as st
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv()

from src.chatbot import Chatbot
from src.utils import get_logger
logger = get_logger(__name__)

st.set_page_config(page_title="AI Support Chatbot", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;500;600;700&display=swap');
*{box-sizing:border-box;}
html,body,[class*="css"],.stApp{background:#020209 !important;color:#e2e8f0 !important;font-family:'Inter',sans-serif !important;}
#MainMenu,footer,header{visibility:hidden;}
::-webkit-scrollbar{width:4px;}
::-webkit-scrollbar-thumb{background:linear-gradient(#00fff7,#bf00ff);border-radius:10px;}

.stApp::before{content:'';position:fixed;top:0;left:0;right:0;bottom:0;
background:radial-gradient(ellipse at 15% 25%,rgba(0,255,247,0.08) 0%,transparent 55%),
radial-gradient(ellipse at 85% 75%,rgba(191,0,255,0.08) 0%,transparent 55%);
pointer-events:none;z-index:0;animation:bgPulse 6s ease-in-out infinite alternate;}
@keyframes bgPulse{0%{opacity:.5;}100%{opacity:1;}}

/* LANDING */
.hero-badge{display:inline-block;background:linear-gradient(135deg,rgba(0,255,247,0.1),rgba(191,0,255,0.1));
border:1px solid rgba(0,255,247,0.3);border-radius:50px;padding:8px 28px;
font-size:.78em;letter-spacing:3px;color:#00fff7;text-transform:uppercase;margin-bottom:24px;animation:fadeDown .8s ease;}
@keyframes fadeDown{from{opacity:0;transform:translateY(-15px);}to{opacity:1;transform:translateY(0);}}
@keyframes fadeUp{from{opacity:0;transform:translateY(20px);}to{opacity:1;transform:translateY(0);}}
@keyframes fadeIn{from{opacity:0;}to{opacity:1;}}

.hero-title{font-family:'Orbitron',monospace !important;font-size:3.6em !important;font-weight:900 !important;line-height:1.2 !important;text-align:center !important;animation:fadeDown 1s ease .2s both;}
.cyan-text{background:linear-gradient(90deg,#00fff7,#00ccdd);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 18px rgba(0,255,247,.5));}
.purple-text{background:linear-gradient(90deg,#bf00ff,#8800cc);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 18px rgba(191,0,255,.5));}

.glow-line{width:100px;height:2px;background:linear-gradient(90deg,transparent,#00fff7,#bf00ff,transparent);margin:18px auto 24px auto;animation:glowPulse 2s ease-in-out infinite;}
@keyframes glowPulse{0%,100%{box-shadow:0 0 8px rgba(0,255,247,.4);}50%{box-shadow:0 0 24px rgba(0,255,247,.8),0 0 48px rgba(191,0,255,.4);}}

.hero-desc{text-align:center;color:#64748b;font-size:1em;max-width:560px;margin:0 auto 32px auto;line-height:1.8;animation:fadeUp .8s ease .4s both;}
.powered-line{text-align:center !important;display:block !important;width:100% !important;color:#475569;font-size:.88em;letter-spacing:.5px;margin:0 auto;animation:fadeIn 1s ease .6s both;}

.feat-card{background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);border-radius:16px;padding:22px 14px;text-align:center;transition:all .35s cubic-bezier(.175,.885,.32,1.275);cursor:pointer;height:120px;display:flex;flex-direction:column;align-items:center;justify-content:center;}
.feat-card:hover{background:rgba(0,255,247,.06);border-color:rgba(0,255,247,.4);box-shadow:0 0 28px rgba(0,255,247,.14),0 8px 32px rgba(0,0,0,.3);transform:translateY(-8px) scale(1.03);}
.feat-card .fi{font-size:2em;margin-bottom:8px;}.feat-card .fl{font-size:.82em;font-weight:600;color:#94a3b8;}

.tech-pill{display:inline-block;background:rgba(191,0,255,.08);border:1px solid rgba(191,0,255,.22);color:#d088ff;padding:5px 16px;border-radius:50px;font-size:.78em;font-weight:600;letter-spacing:1px;margin:4px;transition:all .3s;}
.tech-pill:hover{background:rgba(191,0,255,.15);border-color:#bf00ff;box-shadow:0 0 14px rgba(191,0,255,.2);}

/* Buttons */
div[data-testid="stButton"] button[kind="primary"]{
background:linear-gradient(135deg,#00fff7,#00aacc,#bf00ff) !important;border:none !important;
border-radius:50px !important;color:#000 !important;font-family:'Orbitron',monospace !important;
font-weight:700 !important;font-size:.95em !important;padding:14px 36px !important;letter-spacing:2px !important;
box-shadow:0 0 30px rgba(0,255,247,.3),0 0 60px rgba(191,0,255,.15) !important;
transition:all .3s ease !important;animation:btnPulse 3s ease infinite !important;}
@keyframes btnPulse{0%,100%{box-shadow:0 0 25px rgba(0,255,247,.3);}50%{box-shadow:0 0 50px rgba(0,255,247,.6),0 0 80px rgba(191,0,255,.3);}}
div[data-testid="stButton"] button[kind="primary"]:hover{transform:scale(1.06) !important;box-shadow:0 0 60px rgba(0,255,247,.5) !important;}

/* SIDEBAR */
section[data-testid="stSidebar"]{background:rgba(2,2,12,.97) !important;border-right:1px solid rgba(0,255,247,.07) !important;backdrop-filter:blur(20px) !important;}
section[data-testid="stSidebar"] .stButton>button{background:rgba(0,255,247,.04) !important;border:1px solid rgba(0,255,247,.13) !important;color:#00fff7 !important;border-radius:10px !important;font-weight:600 !important;font-size:.85em !important;width:100% !important;transition:all .3s !important;}
section[data-testid="stSidebar"] .stButton>button:hover{background:rgba(0,255,247,.09) !important;border-color:#00fff7 !important;box-shadow:0 0 18px rgba(0,255,247,.18) !important;transform:translateX(4px) !important;}

/* CHAT */
.chat-hdr{background:linear-gradient(135deg,rgba(0,255,247,.05),rgba(191,0,255,.05));border:1px solid rgba(0,255,247,.12);border-radius:20px;padding:20px 30px;margin-bottom:22px;text-align:center;position:relative;overflow:hidden;}
.chat-hdr::before{content:'';position:absolute;top:0;left:-100%;width:100%;height:2px;background:linear-gradient(90deg,transparent,#00fff7,#bf00ff,transparent);animation:scan 4s linear infinite;}
@keyframes scan{to{left:100%;}}
.chat-hdr-title{font-family:'Orbitron',monospace;font-size:1.65em;font-weight:700;background:linear-gradient(90deg,#00fff7,#bf00ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.chat-hdr-sub{color:#334155;font-size:.82em;letter-spacing:1.5px;text-transform:uppercase;margin-top:4px;}

.msg-user{background:linear-gradient(135deg,rgba(191,0,255,.16),rgba(100,0,180,.07));border:1px solid rgba(191,0,255,.24);border-radius:20px 20px 4px 20px;padding:13px 17px;color:#e2d0ff;margin:7px 0;box-shadow:0 4px 20px rgba(191,0,255,.07);animation:msgIn .3s ease;font-size:.96em;line-height:1.6;}
.msg-bot{background:linear-gradient(135deg,rgba(0,255,247,.06),rgba(0,100,180,.04));border:1px solid rgba(0,255,247,.13);border-radius:20px 20px 20px 4px;padding:13px 17px;color:#cce8f0;margin:7px 0;box-shadow:0 4px 20px rgba(0,255,247,.05);animation:msgIn .3s ease;font-size:.96em;line-height:1.75;}
@keyframes msgIn{from{opacity:0;transform:translateY(10px);}to{opacity:1;transform:translateY(0);}}

[data-testid="stChatInput"]{border:1px solid rgba(0,255,247,.18) !important;border-radius:16px !important;background:rgba(0,255,247,.02) !important;}
[data-testid="stChatInput"]:focus-within{border-color:#00fff7 !important;box-shadow:0 0 28px rgba(0,255,247,.14) !important;}

/* ANALYTICS */
.stat-card{background:linear-gradient(135deg,rgba(0,255,247,.06),rgba(0,255,247,.02));border:1px solid rgba(0,255,247,.14);border-radius:18px;padding:22px 14px;text-align:center;transition:all .35s;position:relative;overflow:hidden;}
.stat-card::after{content:'';position:absolute;bottom:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,#00fff7,transparent);animation:glowPulse 3s ease infinite;}
.stat-card:hover{border-color:#00fff7;box-shadow:0 0 36px rgba(0,255,247,.12);transform:translateY(-4px);}
.stat-val{font-family:'Orbitron',monospace;font-size:2.3em;font-weight:900;color:#00fff7;text-shadow:0 0 18px rgba(0,255,247,.5);margin-bottom:5px;}
.stat-lbl{color:#475569;font-size:.75em;text-transform:uppercase;letter-spacing:2px;font-weight:600;}

.pb-wrap{margin-bottom:13px;}
.pb-top{display:flex;justify-content:space-between;color:#94a3b8;font-size:.86em;margin-bottom:5px;}
.pb-bg{background:rgba(255,255,255,.05);border-radius:10px;height:7px;overflow:hidden;}
.pb-fill{height:7px;border-radius:10px;background:linear-gradient(90deg,#00fff7,#0088ff);box-shadow:0 0 10px rgba(0,255,247,.4);}

/* HISTORY */
.sec-head{font-family:'Orbitron',monospace;font-size:1.05em;font-weight:700;color:#00fff7;text-shadow:0 0 14px rgba(0,255,247,.4);letter-spacing:3px;text-transform:uppercase;margin-bottom:16px;padding-bottom:10px;border-bottom:1px solid rgba(0,255,247,.08);}
.hist-meta{color:#334155;font-size:.76em;margin-bottom:10px;}

[data-testid="stMetricValue"]{color:#00fff7 !important;font-family:'Orbitron',monospace !important;text-shadow:0 0 14px rgba(0,255,247,.5) !important;}
hr{border-color:rgba(0,255,247,.06) !important;}
.streamlit-expanderHeader{background:rgba(0,255,247,.03) !important;border:1px solid rgba(0,255,247,.1) !important;border-radius:10px !important;color:#00fff7 !important;}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──────────────────────────────────────────
def init_state():
    for k,v in {
        "started":False,"page":"chat","messages":[],"chatbot":None,"init_error":None,
        "feedback":{},"analytics":{"total_questions":0,"languages":[],"topics":[],"feedback_up":0,"feedback_down":0,"response_times":[]},
        "past_conversations":[]
    }.items():
        if k not in st.session_state:
            st.session_state[k]=v
init_state()

def init_chatbot():
    if st.session_state.chatbot: return
    try:
        st.session_state.chatbot=Chatbot()
    except Exception as exc:
        st.session_state.init_error=str(exc)

def save_conv():
    msgs=st.session_state.messages
    if not msgs: return
    first_q=next((m["content"] for m in msgs if m["role"]=="user"),"Session")
    st.session_state.past_conversations.insert(0,{
        "title":first_q[:60]+("..." if len(first_q)>60 else ""),
        "time":datetime.datetime.now().strftime("%d %b %Y • %H:%M"),
        "messages":msgs.copy(),
        "count":len([m for m in msgs if m["role"]=="user"])
    })
    st.session_state.past_conversations=st.session_state.past_conversations[:15]

# ── LANDING ────────────────────────────────────────────────
def render_landing():
    st.markdown('<div style="height:28px"></div>',unsafe_allow_html=True)
    st.markdown('<div style="text-align:center"><span class="hero-badge">✦ AI & Data Science Project 2026 ✦</span></div>',unsafe_allow_html=True)
    st.markdown("""
    <div class="hero-title">
        <span class="cyan-text">INTELLIGENT</span><br>
        <span class="purple-text">CUSTOMER SUPPORT</span><br>
        <span style="color:#fff;font-size:.65em;letter-spacing:8px;font-weight:400;">CHATBOT</span>
    </div>""",unsafe_allow_html=True)
    st.markdown('<div class="glow-line"></div>',unsafe_allow_html=True)
    # Powered by line - centered properly
    st.markdown("""
    <div style="text-align:center;width:100%;margin:0 auto 32px auto;">
        <span style="color:#475569;font-size:.88em;letter-spacing:.5px;">
            🔮 Powered by&nbsp; <span style="color:#00fff7;">RAG Pipeline</span> &nbsp;•&nbsp;
            <span style="color:#bf00ff;">Google Gemini AI</span> &nbsp;•&nbsp;
            <span style="color:#00fff7;">ChromaDB</span> &nbsp;•&nbsp;
            <span style="color:#bf00ff;">Sentence Transformers</span>
        </span>
    </div>""",unsafe_allow_html=True)

    # Feature cards row 1
    c1,c2,c3,c4=st.columns(4)
    for col,icon,label in [(c1,"🧠","RAG Pipeline"),(c2,"🌐","50+ Languages"),(c3,"📊","Analytics Dashboard"),(c4,"📎","Source Citations")]:
        with col:
            st.markdown(f'<div class="feat-card"><div class="fi">{icon}</div><div class="fl">{label}</div></div>',unsafe_allow_html=True)
    st.markdown('<div style="height:10px"></div>',unsafe_allow_html=True)
    # Feature cards row 2
    c5,c6,c7,c8=st.columns(4)
    for col,icon,label in [(c5,"💬","Smart Memory"),(c6,"📄","PDF/DOCX/TXT"),(c7,"👍","Feedback System"),(c8,"🕐","Chat History")]:
        with col:
            st.markdown(f'<div class="feat-card"><div class="fi">{icon}</div><div class="fl">{label}</div></div>',unsafe_allow_html=True)

    st.markdown('<div style="height:22px"></div>',unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;">
        <span class="tech-pill">🔮 GEMINI AI</span>
        <span class="tech-pill">🗄️ CHROMADB</span>
        <span class="tech-pill">🤗 SENTENCE TRANSFORMERS</span>
        <span class="tech-pill">🐍 PYTHON</span>
        <span class="tech-pill">📊 STREAMLIT</span>
        <span class="tech-pill">🔍 RAG</span>
    </div>""",unsafe_allow_html=True)

    st.markdown('<div style="height:34px"></div>',unsafe_allow_html=True)
    col1,col2,col3=st.columns([1.8,1,1.8])
    with col2:
        if st.button("⚡  LAUNCH  ⚡",type="primary",use_container_width=True):
            st.session_state.started=True
            st.rerun()
    st.markdown('<p style="text-align:center;color:#1e293b;font-size:.78em;margin-top:16px;">Built by Sudharshan • AI & Data Science</p>',unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────────────────
def render_sidebar(chatbot):
    with st.sidebar:
        st.markdown("""<div style="text-align:center;padding:16px 0 10px 0;">
        <div style="font-family:Orbitron,monospace;font-size:1em;font-weight:700;background:linear-gradient(90deg,#00fff7,#bf00ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:2px;">⚡ AI SUPPORT</div>
        <div style="color:#1e293b;font-size:.68em;letter-spacing:1px;margin-top:2px;">CONTROL CENTER</div></div>""",unsafe_allow_html=True)

        kb=chatbot.get_knowledge_base_size()
        sc="#00ff88" if kb>0 else "#ff4466"
        st.markdown(f'<div style="text-align:center;margin-bottom:10px;"><span style="display:inline-block;width:7px;height:7px;background:{sc};border-radius:50%;box-shadow:0 0 7px {sc};margin-right:5px;animation:blink 2s ease infinite;"></span><span style="color:{sc};font-size:.75em;letter-spacing:2px;font-weight:600;">{"ONLINE" if kb>0 else "NO DATA"}</span></div>',unsafe_allow_html=True)
        st.divider()

        st.markdown('<div style="color:#1e293b;font-size:.68em;letter-spacing:2px;margin-bottom:7px;font-weight:600;">NAVIGATE</div>',unsafe_allow_html=True)
        nc1,nc2=st.columns(2)
        with nc1:
            if st.button("💬 Chat",use_container_width=True): st.session_state.page="chat"; st.rerun()
        with nc2:
            if st.button("📊 Stats",use_container_width=True): st.session_state.page="analytics"; st.rerun()
        nc3,nc4=st.columns(2)
        with nc3:
            if st.button("🕐 History",use_container_width=True): st.session_state.page="history"; st.rerun()
        with nc4:
            if st.button("🏠 Home",use_container_width=True): st.session_state.started=False; st.rerun()

        st.divider()
        st.markdown('<div style="color:#1e293b;font-size:.68em;letter-spacing:2px;margin-bottom:7px;font-weight:600;">KNOWLEDGE BASE</div>',unsafe_allow_html=True)
        up=st.file_uploader("",type=["pdf","txt","docx"],accept_multiple_files=True,label_visibility="collapsed")
        if up:
            if st.button("📥 Index Now",use_container_width=True):
                p=st.progress(0)
                for i,f in enumerate(up):
                    r=chatbot.ingest_uploaded_file(f.getvalue(),f.name)
                    p.progress((i+1)/len(up))
                    st.success(f"✅ {f.name}") if r.success else st.error(f"❌ {f.name}")
                p.empty(); st.rerun()

        if st.button("🧪 Load Sample KB",use_container_width=True):
            with st.spinner("Loading..."):
                res=chatbot.load_sample_knowledge_base()
            st.success(f"✅ {sum(1 for r in res if r.success)}/{len(res)} loaded!"); st.rerun()

        st.divider()
        srcs=chatbot.get_indexed_sources()
        c1,c2=st.columns(2)
        with c1:
            st.markdown(f'<div style="background:rgba(0,255,247,.05);border:1px solid rgba(0,255,247,.14);border-radius:10px;padding:10px;text-align:center;"><div style="font-family:Orbitron,monospace;font-size:1.3em;color:#00fff7;text-shadow:0 0 10px #00fff7;">{kb}</div><div style="color:#1e293b;font-size:.65em;margin-top:2px;">CHUNKS</div></div>',unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div style="background:rgba(191,0,255,.05);border:1px solid rgba(191,0,255,.14);border-radius:10px;padding:10px;text-align:center;"><div style="font-family:Orbitron,monospace;font-size:1.3em;color:#bf00ff;text-shadow:0 0 10px #bf00ff;">{len(srcs)}</div><div style="color:#1e293b;font-size:.65em;margin-top:2px;">DOCS</div></div>',unsafe_allow_html=True)

        if srcs:
            with st.expander(f"📄 Files ({len(srcs)})"):
                for s in srcs:
                    st.markdown(f'<div style="color:#00fff7;font-size:.82em;padding:3px 0;border-bottom:1px solid rgba(0,255,247,.05);">▸ {s}</div>',unsafe_allow_html=True)

        st.divider()
        a1,a2=st.columns(2)
        with a1:
            if st.button("🗑️ Clear",use_container_width=True):
                save_conv(); chatbot.clear_chat_history()
                st.session_state.messages=[]; st.session_state.feedback={}; st.rerun()
        with a2:
            if st.button("⚠️ Reset KB",use_container_width=True):
                chatbot.clear_knowledge_base(); st.rerun()

        with st.expander("⚙️ Config"):
            st.markdown(f'<div style="color:#bf00ff;font-size:.8em;">🔮 {chatbot.rag_pipeline.provider.upper()}</div>',unsafe_allow_html=True)
            st.markdown(f'<div style="color:#bf00ff;font-size:.8em;">🤖 {chatbot.rag_pipeline.model_name}</div>',unsafe_allow_html=True)

# ── CHAT ──────────────────────────────────────────────────
def render_chat(chatbot):
    st.markdown("""<div class="chat-hdr">
    <div class="chat-hdr-title">🤖 AI Customer Support</div>
    <div class="chat-hdr-sub">English • Tamil • Hindi • 5+ Languages • Zero Hallucination</div>
    </div>""",unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown('<div style="color:#1e293b;font-size:.72em;letter-spacing:2px;margin-bottom:10px;font-weight:600;">💡 SUGGESTED QUESTIONS — CLICK TO ASK</div>',unsafe_allow_html=True)
        sugs=["What is your return policy?","What are shipping charges?","How do I track my order?","Do you offer EMI?","How to contact support?","Can I exchange a product?"]
        c1,c2,c3=st.columns(3)
        for i,s in enumerate(sugs):
            with [c1,c2,c3][i%3]:
                if st.button(f"💬 {s}",use_container_width=True,key=f"s{i}"):
                    process_msg(chatbot,s); st.rerun()
        st.divider()

    for idx,msg in enumerate(st.session_state.messages):
        if msg["role"]=="user":
            with st.chat_message("user",avatar="👤"):
                st.markdown(f'<div class="msg-user">{msg["content"]}</div>',unsafe_allow_html=True)
        else:
            with st.chat_message("assistant",avatar="🤖"):
                st.markdown(f'<div class="msg-bot">{msg["content"]}</div>',unsafe_allow_html=True)
                if msg.get("sources"):
                    with st.expander(f"📎 {len(msg['sources'])} Source(s)"):
                        for i,ch in enumerate(msg["sources"],1):
                            pg=f" • Page {ch.page}" if ch.page else ""
                            sc="#00fff7" if ch.score>.6 else "#bf00ff" if ch.score>.4 else "#475569"
                            st.markdown(f'<div style="margin:6px 0;padding:10px;background:rgba(0,255,247,.03);border-left:3px solid {sc};border-radius:0 8px 8px 0;"><div style="color:{sc};font-size:.86em;font-weight:600;">{i}. {ch.source}{pg} <span style="color:#334155;">({ch.score:.0%} match)</span></div><div style="color:#475569;font-size:.8em;margin-top:4px;line-height:1.5;">{ch.text[:200]}...</div></div>',unsafe_allow_html=True)
                if msg.get("language_name"):
                    st.markdown(f'<div style="color:#1e293b;font-size:.75em;margin-top:3px;">🌐 {msg["language_name"]}</div>',unsafe_allow_html=True)
                # Feedback
                fb=st.session_state.feedback.get(f"fb_{idx}")
                fc1,fc2,fc3=st.columns([.5,.5,9])
                with fc1:
                    if st.button("👍" if fb!="up" else "✅",key=f"up{idx}"):
                        if fb!="up":
                            st.session_state.feedback[f"fb_{idx}"]="up"
                            st.session_state.analytics["feedback_up"]+=1
                        st.rerun()
                with fc2:
                    if st.button("👎" if fb!="down" else "❌",key=f"dn{idx}"):
                        if fb!="down":
                            st.session_state.feedback[f"fb_{idx}"]="down"
                            st.session_state.analytics["feedback_down"]+=1
                        st.rerun()

    inp=st.chat_input("✨ Ask anything about products, policies, shipping, returns...")
    if inp:
        process_msg(chatbot,inp); st.rerun()

def process_msg(chatbot,text):
    st.session_state.messages.append({"role":"user","content":text})
    t0=time.time()
    try: resp=chatbot.ask(text)
    except Exception as e: st.error(f"Error: {e}"); return
    elapsed=round(time.time()-t0,2)
    if resp:
        st.session_state.messages.append({"role":"assistant","content":resp.answer,"sources":resp.sources,"language_name":resp.language_name})
        a=st.session_state.analytics
        a["total_questions"]+=1
        a["languages"].append(resp.language_name or "English")
        a["response_times"].append(elapsed)
        words=[w for w in text.lower().split() if len(w)>4]
        if words: a["topics"].append(words[0].capitalize())

# ── ANALYTICS ─────────────────────────────────────────────
def render_analytics():
    st.markdown('<div class="sec-head">📊 ANALYTICS DASHBOARD</div>',unsafe_allow_html=True)
    a=st.session_state.analytics
    total=a["total_questions"]
    avg_rt=round(sum(a["response_times"])/max(len(a["response_times"]),1),2)
    up=a["feedback_up"]; dn=a["feedback_down"]
    sat=round((up/max(up+dn,1))*100)

    c1,c2,c3,c4=st.columns(4)
    for col,val,lbl in [(c1,str(total),"QUESTIONS"),(c2,f"{avg_rt}s","AVG RESPONSE"),(c3,f"{sat}%","SATISFACTION"),(c4,str(len(st.session_state.past_conversations)),"SESSIONS")]:
        with col:
            st.markdown(f'<div class="stat-card"><div class="stat-val">{val}</div><div class="stat-lbl">{lbl}</div></div>',unsafe_allow_html=True)

    st.markdown('<div style="height:22px"></div>',unsafe_allow_html=True)
    cl,cr=st.columns(2)

    with cl:
        st.markdown('<div style="color:#00fff7;font-size:.75em;letter-spacing:2px;margin-bottom:12px;font-weight:600;">🌐 LANGUAGES USED</div>',unsafe_allow_html=True)
        if a["languages"]:
            for lang,cnt in Counter(a["languages"]).most_common(6):
                pct=int((cnt/max(total,1))*100)
                st.markdown(f'<div class="pb-wrap"><div class="pb-top"><span>{lang}</span><span style="color:#00fff7;">{cnt} ({pct}%)</span></div><div class="pb-bg"><div class="pb-fill" style="width:{pct}%;"></div></div></div>',unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#1e293b;text-align:center;padding:28px;font-size:.9em;">Start chatting to see language data!</div>',unsafe_allow_html=True)

    with cr:
        st.markdown('<div style="color:#00fff7;font-size:.75em;letter-spacing:2px;margin-bottom:12px;font-weight:600;">👍 FEEDBACK ANALYSIS</div>',unsafe_allow_html=True)
        if up+dn>0:
            up_p=int((up/max(up+dn,1))*100); dn_p=100-up_p
            st.markdown(f'''
            <div style="margin-bottom:14px;"><div class="pb-top"><span>👍 Positive</span><span style="color:#00ff88;">{up} ({up_p}%)</span></div>
            <div class="pb-bg"><div style="height:7px;border-radius:10px;background:linear-gradient(90deg,#00ff88,#00cc66);width:{up_p}%;box-shadow:0 0 10px rgba(0,255,136,.4);"></div></div></div>
            <div><div class="pb-top"><span>👎 Negative</span><span style="color:#ff4466;">{dn} ({dn_p}%)</span></div>
            <div class="pb-bg"><div style="height:7px;border-radius:10px;background:linear-gradient(90deg,#ff4466,#cc2244);width:{dn_p}%;box-shadow:0 0 10px rgba(255,68,102,.4);"></div></div></div>
            <div style="margin-top:16px;padding:14px;background:rgba(0,255,136,.04);border:1px solid rgba(0,255,136,.14);border-radius:12px;text-align:center;">
            <div style="font-family:Orbitron,monospace;font-size:1.7em;color:#00ff88;text-shadow:0 0 14px rgba(0,255,136,.5);">{up_p}%</div>
            <div style="color:#1e293b;font-size:.72em;letter-spacing:1px;margin-top:3px;">SATISFACTION RATE</div></div>''',unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#1e293b;text-align:center;padding:28px;font-size:.9em;">Rate answers with 👍 👎 to see feedback!</div>',unsafe_allow_html=True)

    st.divider()
    st.markdown('<div style="color:#00fff7;font-size:.75em;letter-spacing:2px;margin-bottom:12px;font-weight:600;">🔥 TRENDING TOPICS</div>',unsafe_allow_html=True)
    if a["topics"]:
        tc=Counter(a["topics"]).most_common(8)
        cols=st.columns(min(len(tc),4))
        for i,(t,cnt) in enumerate(tc):
            with cols[i%4]:
                st.markdown(f'<div style="background:rgba(191,0,255,.07);border:1px solid rgba(191,0,255,.18);border-radius:12px;padding:12px;text-align:center;margin-bottom:8px;"><div style="font-family:Orbitron,monospace;font-size:1.4em;color:#bf00ff;text-shadow:0 0 10px rgba(191,0,255,.5);">{cnt}</div><div style="color:#94a3b8;font-size:.8em;margin-top:3px;">{t}</div></div>',unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#1e293b;text-align:center;padding:20px;">Topics appear as you ask questions!</div>',unsafe_allow_html=True)

    if a["response_times"]:
        st.divider()
        st.markdown('<div style="color:#00fff7;font-size:.75em;letter-spacing:2px;margin-bottom:10px;font-weight:600;">⚡ RESPONSE TIME TREND</div>',unsafe_allow_html=True)
        st.line_chart({"Response Time (s)":a["response_times"][-20:]},color="#00fff7")

# ── HISTORY ───────────────────────────────────────────────
def render_history():
    st.markdown('<div class="sec-head">🕐 CONVERSATION HISTORY</div>',unsafe_allow_html=True)
    past=st.session_state.past_conversations

    if st.session_state.messages:
        if st.button("💾 Save Current Session",type="primary"):
            save_conv(); st.success("✅ Saved!"); st.rerun()

    if not past:
        st.markdown("""<div style="text-align:center;padding:70px 20px;">
        <div style="font-size:3.5em;margin-bottom:14px;">🕐</div>
        <div style="color:#1e293b;font-size:1.05em;font-weight:600;">No conversations saved yet</div>
        <div style="color:#0f172a;font-size:.88em;margin-top:7px;">Chat and click Clear to auto-save sessions here</div>
        </div>""",unsafe_allow_html=True)
        return

    st.markdown(f'<div style="color:#1e293b;font-size:.8em;margin-bottom:16px;">{len(past)} conversation(s) saved</div>',unsafe_allow_html=True)

    for i,conv in enumerate(past):
        # Use index + time to make unique title for expander
        expander_label = f"💬  {conv['title']}   |   {conv['time']}   |   {conv['count']} Q&A"
        with st.expander(expander_label):
            st.markdown(f'<div class="hist-meta">📅 {conv["time"]}  •  {conv["count"]} question(s)</div>',unsafe_allow_html=True)
            for msg in conv["messages"]:
                if msg["role"]=="user":
                    st.markdown(f'<div class="msg-user" style="font-size:.87em;margin:4px 0;">👤 {msg["content"]}</div>',unsafe_allow_html=True)
                else:
                    preview=msg["content"][:280]+("..." if len(msg["content"])>280 else "")
                    st.markdown(f'<div class="msg-bot" style="font-size:.87em;margin:4px 0;">🤖 {preview}</div>',unsafe_allow_html=True)
            if st.button("🔄 Restore This Session",key=f"r{i}",use_container_width=True):
                st.session_state.messages=conv["messages"].copy()
                st.session_state.page="chat"; st.rerun()

# ── MAIN ──────────────────────────────────────────────────
def main():
    if not st.session_state.started:
        render_landing(); return

    init_chatbot()
    if st.session_state.init_error:
        st.markdown(f"""<div style="background:rgba(255,50,50,.07);border:1px solid rgba(255,50,50,.28);border-radius:14px;padding:24px;text-align:center;max-width:600px;margin:40px auto;">
        <div style="font-size:2em;margin-bottom:10px;">⚠️</div>
        <div style="color:#ff6680;font-weight:600;margin-bottom:7px;">Initialization Failed</div>
        <div style="color:#94a3b8;font-size:.88em;">{st.session_state.init_error}</div>
        <div style="color:#475569;font-size:.8em;margin-top:9px;">Check your .env — ensure GEMINI_API_KEY is correct</div></div>""",unsafe_allow_html=True)
        if st.button("🏠 Back",type="primary"):
            st.session_state.started=False; st.rerun()
        return

    chatbot=st.session_state.chatbot
    render_sidebar(chatbot)
    pg=st.session_state.page
    if pg=="chat": render_chat(chatbot)
    elif pg=="analytics": render_analytics()
    elif pg=="history": render_history()

if __name__=="__main__":
    main()