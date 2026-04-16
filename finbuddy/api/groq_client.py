"""
FinBuddy - Groq API Client
Handles all AI interactions via the Groq LLM API.
"""

import urllib.request
import urllib.error
import json


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are FinBuddy — a witty, sharp, and genuinely helpful AI financial advisor built for Gen Z users in India. 

Your personality:
- Direct, fun, and a little snarky (but never mean)
- Use Indian context (₹, Indian spending habits, Swiggy/Zomato references)
- Keep responses SHORT and punchy (3-5 sentences max unless asked for more)
- Mix practical advice with relatable humor
- Use emojis sparingly but effectively
- Always end with ONE actionable tip

When financial data is provided, reference specific numbers in your advice.
Never give generic financial advice — make it personal to the data."""


def get_ai_response(
    user_input: str,
    api_key: str,
    financial_context: str = "",
) -> tuple[str, str]:
    """
    Send a message to the Groq API and return (response_text, error).
    If error is non-empty, response_text will contain a fallback message.
    """
    if not api_key or api_key.strip() == "":
        return (
            "⚠️ No API key set. Go to Settings → Enter your Groq API key to enable AI features. Get a free key at console.groq.com",
            "no_key",
        )

    user_message = user_input
    if financial_context:
        user_message = f"""My financial data:
{financial_context}

My question: {user_input}"""

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "max_tokens": 400,
        "temperature": 0.7,
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            GROQ_API_URL,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key.strip()}",
                "User-Agent": "FinBuddy-App/1.0"
            },
        )

        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode("utf-8"))
            text = result["choices"][0]["message"]["content"].strip()
            return text, ""

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        try:
            err_json = json.loads(body)
            err_msg = err_json.get("error", {}).get("message", str(e))
        except Exception:
            err_msg = str(e)

        if e.code == 401:
            return "❌ Invalid API key. Check your Groq API key in Settings.", "auth_error"
        elif e.code == 429:
            return "⏳ Rate limit hit. Wait a moment and try again.", "rate_limit"
        else:
            return f"❌ API error ({e.code}): {err_msg}", "http_error"

    except urllib.error.URLError as e:
        return "🌐 Network error. Check your internet connection.", "network_error"

    except Exception as e:
        return f"❌ Unexpected error: {e}", "unknown_error"
