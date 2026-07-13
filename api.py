"""
api.py — Flask REST API wrapper for the React frontend.
This file does NOT modify any backend logic. It simply exposes the existing
Chatbot class as REST endpoints consumed by the React frontend.

Run: python api.py
Runs on: http://localhost:5000
"""
import sys, time, datetime
from pathlib import Path
from collections import Counter
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv()

from src.chatbot import Chatbot
from src.utils import get_logger
logger = get_logger(__name__)

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])

# ── Shared state (session-level, single-user dev server) ──────────────────
_chatbot = None
_analytics = {
    "total_questions": 0,
    "languages": [],
    "topics": [],
    "feedback_up": 0,
    "feedback_down": 0,
    "response_times": [],
}
_messages = []
_past_conversations = []


def get_chatbot():
    global _chatbot
    if _chatbot is None:
        _chatbot = Chatbot()
    return _chatbot


# ─────────────────────────────────────────────────────────────────────────────
# STATUS
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/status", methods=["GET"])
def status():
    try:
        chatbot = get_chatbot()
        kb = chatbot.get_knowledge_base_size()
        srcs = chatbot.get_indexed_sources()
        return jsonify({
            "ok": True,
            "knowledge_base_chunks": kb,
            "indexed_sources": srcs,
            "online": kb > 0,
        })
    except Exception as e:
        logger.error(f"Status error: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# CHAT
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
def chat():
    global _analytics, _messages
    data = request.get_json(force=True)
    text = (data.get("message") or "").strip()
    if not text:
        return jsonify({"ok": False, "error": "Empty message"}), 400

    try:
        chatbot = get_chatbot()
        _messages.append({"role": "user", "content": text, "ts": datetime.datetime.now().isoformat()})

        t0 = time.time()
        resp = chatbot.ask(text)
        elapsed = round(time.time() - t0, 2)

        if resp:
            sources = []
            for ch in (resp.sources or []):
                sources.append({
                    "source": ch.source,
                    "page": ch.page,
                    "score": round(ch.score, 3),
                    "text": ch.text[:300],
                })

            bot_msg = {
                "role": "assistant",
                "content": resp.answer,
                "sources": sources,
                "language_name": resp.language_name,
                "ts": datetime.datetime.now().isoformat(),
                "elapsed": elapsed,
            }
            _messages.append(bot_msg)

            # Update analytics
            _analytics["total_questions"] += 1
            _analytics["languages"].append(resp.language_name or "English")
            _analytics["response_times"].append(elapsed)
            words = [w for w in text.lower().split() if len(w) > 4]
            if words:
                _analytics["topics"].append(words[0].capitalize())

            return jsonify({"ok": True, "message": bot_msg, "elapsed": elapsed})
        else:
            return jsonify({"ok": False, "error": "No response from chatbot"}), 500

    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# MESSAGES (history for current session)
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/messages", methods=["GET"])
def get_messages():
    return jsonify({"ok": True, "messages": _messages})


# ─────────────────────────────────────────────────────────────────────────────
# FEEDBACK
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/feedback", methods=["POST"])
def feedback():
    global _analytics
    data = request.get_json(force=True)
    vote = data.get("vote")  # "up" or "down"
    if vote == "up":
        _analytics["feedback_up"] += 1
    elif vote == "down":
        _analytics["feedback_down"] += 1
    else:
        return jsonify({"ok": False, "error": "Invalid vote"}), 400
    return jsonify({"ok": True, "analytics": _analytics})


# ─────────────────────────────────────────────────────────────────────────────
# ANALYTICS
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/analytics", methods=["GET"])
def analytics():
    a = _analytics
    total = a["total_questions"]
    avg_rt = round(sum(a["response_times"]) / max(len(a["response_times"]), 1), 2)
    up = a["feedback_up"]
    dn = a["feedback_down"]
    sat = round((up / max(up + dn, 1)) * 100)

    lang_counter = Counter(a["languages"])
    topic_counter = Counter(a["topics"])

    return jsonify({
        "ok": True,
        "total_questions": total,
        "avg_response_time": avg_rt,
        "satisfaction_pct": sat,
        "feedback_up": up,
        "feedback_down": dn,
        "languages": [{"name": k, "count": v} for k, v in lang_counter.most_common(8)],
        "topics": [{"name": k, "count": v} for k, v in topic_counter.most_common(10)],
        "response_times": a["response_times"][-20:],
        "sessions": len(_past_conversations),
    })


# ─────────────────────────────────────────────────────────────────────────────
# UPLOAD
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/upload", methods=["POST"])
def upload():
    try:
        chatbot = get_chatbot()
        files = request.files.getlist("files")
        if not files:
            return jsonify({"ok": False, "error": "No files uploaded"}), 400

        results = []
        for f in files:
            data = f.read()
            res = chatbot.ingest_uploaded_file(data, f.filename)
            results.append({"filename": f.filename, "success": res.success,
                            "message": getattr(res, "message", "")})

        return jsonify({"ok": True, "results": results})
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# LOAD SAMPLE KB
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/load-sample", methods=["POST"])
def load_sample():
    try:
        chatbot = get_chatbot()
        results = chatbot.load_sample_knowledge_base()
        ok_count = sum(1 for r in results if r.success)
        return jsonify({"ok": True, "loaded": ok_count, "total": len(results)})
    except Exception as e:
        logger.error(f"Load sample error: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# CLEAR CHAT
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/clear", methods=["POST"])
def clear_chat():
    global _messages, _past_conversations
    try:
        chatbot = get_chatbot()
        if _messages:
            first_q = next((m["content"] for m in _messages if m["role"] == "user"), "Session")
            user_count = len([m for m in _messages if m["role"] == "user"])
            _past_conversations.insert(0, {
                "title": first_q[:60] + ("..." if len(first_q) > 60 else ""),
                "time": datetime.datetime.now().strftime("%d %b %Y • %H:%M"),
                "messages": list(_messages),
                "count": user_count,
            })
            _past_conversations = _past_conversations[:15]
        chatbot.clear_chat_history()
        _messages = []
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# CONVERSATION HISTORY
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/history", methods=["GET"])
def history():
    return jsonify({"ok": True, "conversations": _past_conversations})


@app.route("/api/history/restore", methods=["POST"])
def restore_history():
    global _messages
    data = request.get_json(force=True)
    idx = data.get("index", 0)
    if 0 <= idx < len(_past_conversations):
        _messages = list(_past_conversations[idx]["messages"])
        return jsonify({"ok": True, "messages": _messages})
    return jsonify({"ok": False, "error": "Invalid index"}), 400


# ─────────────────────────────────────────────────────────────────────────────
# RESET KNOWLEDGE BASE
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/reset-kb", methods=["POST"])
def reset_kb():
    try:
        chatbot = get_chatbot()
        chatbot.clear_knowledge_base()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    print("Starting Flask API on http://localhost:5000")
    print("React frontend should run on http://localhost:5173")
    app.run(host="0.0.0.0", port=5000, debug=True)
