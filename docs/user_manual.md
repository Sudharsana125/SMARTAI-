# User Manual — Intelligent Customer Support Chatbot

**Version:** 1.0.0 | **Audience:** End Users & Support Staff

---

## Table of Contents
1. [Getting Started](#getting-started)
2. [Uploading Company Documents](#uploading-company-documents)
3. [Chatting with the Bot](#chatting-with-the-bot)
4. [Understanding Source Citations](#understanding-source-citations)
5. [Multilingual Support](#multilingual-support)
6. [Managing the Knowledge Base](#managing-the-knowledge-base)
7. [Example Conversations](#example-conversations)
8. [Troubleshooting](#troubleshooting)

---

## 1. Getting Started

After the system is installed and running, open your browser and go to:

```
http://localhost:8501
```

You will see two main areas:

| Area | Description |
|------|-------------|
| **Left Sidebar** | Upload documents, view knowledge base status, manage settings |
| **Main Chat Window** | Type questions and read answers with source citations |

---

## 2. Uploading Company Documents

The chatbot answers questions **only from your uploaded documents**. It will never guess or make up information.

### Supported File Types
| Format | Extension | Notes |
|--------|-----------|-------|
| PDF | `.pdf` | Text-based PDFs only (not scanned images) |
| Word Document | `.docx` | Tables and paragraphs both extracted |
| Plain Text | `.txt` | UTF-8 encoding recommended |

### How to Upload

**Step 1 —** Click **"Browse files"** in the left sidebar under **📚 Knowledge Base**

**Step 2 —** Select one or more files (hold Ctrl/Cmd to select multiple)

**Step 3 —** Click the **"📥 Process Uploaded Files"** button

**Step 4 —** Wait for the green success messages confirming each file is indexed

> ✅ **Tip:** The sidebar shows "Indexed Chunks" count — this number increases after each successful upload.

### Loading the Sample Knowledge Base
Click **"🧪 Load Sample Knowledge Base"** to instantly load the pre-built ShopEasy demo documents. Great for testing without your own files.

---

## 3. Chatting with the Bot

**Step 1 —** Type your question in the chat box at the bottom of the screen

**Step 2 —** Press **Enter** or click the send button

**Step 3 —** The bot reads your question, searches the knowledge base, and replies in seconds

### What You Can Ask
- Product information and pricing
- Return and refund policies
- Order tracking and shipping
- Account and membership questions
- Any topic covered in your uploaded documents

### Follow-Up Questions
The bot remembers your conversation. You can ask natural follow-ups:

```
You:  What is the return policy?
Bot:  You can return items within 30 days...

You:  What about defective products?
Bot:  For defective items, you have 48 hours to report...  ← remembers context
```

---

## 4. Understanding Source Citations

Every answer includes a **📎 Sources** panel showing exactly which document(s) the answer came from.

```
📎 Sources (2)
─────────────────────────────────────
1. return_refund_policy.txt  (relevance: 0.87)
   > "Customers may request a return within 30 calendar days..."

2. faq.txt  (relevance: 0.74)
   > "Items must be unused, in their original packaging..."
```

| Field | Meaning |
|-------|---------|
| **Filename** | The document the excerpt came from |
| **Page** | Page number (PDFs only) |
| **Relevance** | Score from 0.0–1.0; higher = more relevant |
| **Preview** | First 300 characters of the matched excerpt |

> 💡 Click the **"📎 Sources"** expander to show or hide citations.

---

## 5. Multilingual Support

The chatbot **automatically detects** the language of your question and replies in the same language. No settings needed.

### Supported Languages (Highlighted)
- 🇮🇳 **Tamil** — Type in Tamil script, get Tamil replies
- 🇮🇳 **Hindi** — Type in Hindi/Devanagari, get Hindi replies
- 🇬🇧 **English** — Default language
- 🇪🇸 Spanish, 🇫🇷 French, 🇩🇪 German, 🇯🇵 Japanese, 🇰🇷 Korean, and 50+ more

### Example
```
நீங்கள்:   என் ஆர்டரை எப்படி ரத்து செய்வது?
봇:        உங்கள் ஆர்டரை 1 மணி நேரத்திற்குள் ரத்து செய்யலாம்...
```

The detected language is shown below each bot reply:
```
🌐 Detected language: Tamil
```

---

## 6. Managing the Knowledge Base

### Sidebar Controls

| Button | Action |
|--------|--------|
| **📥 Process Uploaded Files** | Index newly uploaded documents |
| **🧪 Load Sample Knowledge Base** | Load pre-built demo documents |
| **🗑️ Clear Chat** | Erase conversation history (keeps documents) |
| **⚠️ Reset KB** | Delete ALL indexed documents (start fresh) |

### Viewing Indexed Documents
Expand **"📄 Indexed Documents"** in the sidebar to see the list of all files currently in the knowledge base.

> ⚠️ **Warning:** "Reset KB" permanently deletes all indexed data. You will need to re-upload documents afterwards.

---

## 7. Example Conversations

### English — Order Query
```
User:  How do I track my order?
Bot:   Once your order ships, you'll receive a tracking number via email
       and SMS. You can also track it anytime in My Orders → Track Order.

       📎 Sources (1): faq.txt (relevance: 0.91)
```

### Hindi — Refund Query
```
User:  मुझे रिफंड कब मिलेगा?
Bot:   आपका रिफंड आइटम की जांच के बाद 5-7 कार्य दिवसों में
       प्रोसेस किया जाएगा...

       🌐 Detected language: Hindi
```

### Tamil — Shipping Query
```
User:  டெலிவரி எவ்வளவு நாள் ஆகும்?
Bot:   நிலையான டெலிவரி 3-7 வணிக நாட்கள் ஆகும்...

       🌐 Detected language: Tamil
```

### Follow-Up Example
```
User:  What is your return policy?
Bot:   You can return items within 30 days of delivery...

User:  What if the product is defective?
Bot:   For defective items, report within 48 hours via My Orders →
       Report an Issue with photos. You'll get a full refund or
       free replacement...
```

---

## 8. Troubleshooting

### "The knowledge base is currently empty"
→ Upload documents first using the sidebar, or click **"🧪 Load Sample Knowledge Base"**

### Bot says "I don't have information about that"
→ The answer isn't in your uploaded documents. Upload relevant files and ask again.

### File upload fails
→ Check: file is under 25 MB, format is PDF/DOCX/TXT, PDF is text-based (not a scanned image)

### API Key error on startup
→ Open your `.env` file and ensure `OPENAI_API_KEY=sk-...` is filled in correctly, then restart with `streamlit run app.py`

### Slow first response
→ The embedding model loads on first use. Subsequent responses are faster.

### Wrong language detected
→ Write longer sentences — very short text (1-2 words) may be misdetected. The bot corrects on the next message.

---

*For technical setup instructions, see [README.md](../README.md)*
*For system architecture details, see [technical_documentation.md](technical_documentation.md)*
