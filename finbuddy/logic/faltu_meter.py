"""
FinBuddy - Faltu Meter Engine
Detects and scores unnecessary / impulse spending.
"""

FALTU_CATEGORIES = {
    "food delivery": 1.5,
    "entertainment": 1.2,
    "shopping": 1.3,
    "gaming": 1.4,
    "alcohol": 1.5,
    "subscriptions": 1.0,
    "snacks": 1.2,
}

THRESHOLD_LOW = 20
THRESHOLD_MID = 40
THRESHOLD_HIGH = 60


def compute_faltu_score(category_summary, total_expense: float) -> dict:
    """
    Compute a Faltu Score (0–100) based on unnecessary spending percentage.
    Returns a dict with score, breakdown, and message.
    """
    if total_expense <= 0 or category_summary.empty:
        return {
            "score": 0,
            "faltu_amount": 0,
            "faltu_percent": 0,
            "breakdown": {},
            "verdict": "No data",
            "message": "Upload spending data to get your Faltu Score!",
            "emoji": "📊",
        }

    faltu_breakdown = {}
    weighted_faltu = 0.0

    for category, amount in category_summary.items():
        cat_lower = category.lower()
        for key, weight in FALTU_CATEGORIES.items():
            if key in cat_lower:
                faltu_breakdown[category] = amount
                weighted_faltu += amount * weight
                break

    raw_faltu = sum(faltu_breakdown.values())
    faltu_percent = (raw_faltu / total_expense) * 100

    raw_score = min((weighted_faltu / total_expense) * 100, 100)
    score = round(raw_score)

    if faltu_percent < THRESHOLD_LOW:
        verdict = "Controlled Spender 😎"
        message = "You're a finance ninja! Very little wasteful spending."
        color = "#00FFD1"
    elif faltu_percent < THRESHOLD_MID:
        verdict = "Moderate Splurger 🤔"
        message = "Not bad, but you could cut back on a few treats."
        color = "#FFD700"
    elif faltu_percent < THRESHOLD_HIGH:
        verdict = "High Spender 🔥"
        message = "Your wallet is on fire! Time to rethink some habits."
        color = "#FF8C00"
    else:
        verdict = "Swiggy CEO knows you personally 🍔"
        message = "Your food delivery app sends you birthday wishes. Fix this NOW."
        color = "#FF4444"

    return {
        "score": score,
        "faltu_amount": raw_faltu,
        "faltu_percent": faltu_percent,
        "breakdown": faltu_breakdown,
        "verdict": verdict,
        "message": message,
        "color": color,
    }
