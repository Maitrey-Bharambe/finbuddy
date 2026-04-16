# FinBuddy 💜 — AI-Powered Desktop Finance App

A gamified, AI-powered personal finance desktop app built with Python + Tkinter.

---

## Features

| Screen | What it does |
|---|---|
| 🏠 Dashboard | Balance overview, savings jars, category bars, streak counter |
| 📊 Analysis | Upload CSV, see pie chart + line graph, category table |
| 🚫 Faltu Meter | Score your unnecessary spending (0–100) |
| 🤖 AI Buddy | Chat with Groq LLM for personalised financial advice |
| ⚙️ Settings | Set your Groq API key |

---

## Setup

### 1. Install dependencies
```bash
pip install pandas matplotlib
```

> Tkinter comes built-in with Python. If missing: `sudo apt-get install python3-tk`

### 2. Run the app
```bash
cd finbuddy
python main.py
```

---

## Using the AI Buddy

1. Get a **free** Groq API key at [console.groq.com](https://console.groq.com)
2. Open FinBuddy → **Settings** → paste your key → **Save Key**
3. Go to **AI Buddy** and start chatting

---

## CSV Format

Your CSV file must have these columns:

```
Date,Category,Amount,Type
2024-01-01,Salary,50000,Income
2024-01-03,Food Delivery,450,Expense
```

A sample file is included at `data/sample.csv`.

---

## Folder Structure

```
finbuddy/
├── main.py              ← Entry point
├── requirements.txt
├── ui/
│   ├── theme.py         ← Colors, fonts, spacing
│   ├── components.py    ← Reusable widgets
│   ├── dashboard.py     ← Dashboard screen
│   ├── upload.py        ← Analysis & CSV screen
│   ├── faltu_meter.py   ← Faltu Meter screen
│   ├── chatbot.py       ← AI chat screen
│   └── settings.py      ← Settings screen
├── logic/
│   ├── analysis.py      ← CSV parsing + financial calculations
│   └── faltu_meter.py   ← Faltu score engine
├── api/
│   └── groq_client.py   ← Groq API integration
└── data/
    └── sample.csv       ← Sample financial data
```

---

## Theme

- **Background:** `#0a0a0f` (deep black)
- **Primary:** `#8A2BE2` (neon purple)
- **Accent:** `#00FFD1` (teal glow)
- Font: Helvetica

---

*Built for Gen Z. No fluff, just financial clarity.*
