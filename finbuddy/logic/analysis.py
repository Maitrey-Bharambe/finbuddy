"""
FinBuddy - Data Analysis Engine
Handles CSV parsing, financial calculations, and summary generation.
"""

import pandas as pd
from datetime import datetime


REQUIRED_COLUMNS = {"Date", "Category", "Amount", "Type"}


def load_csv(file_path: str) -> tuple[pd.DataFrame | None, str]:
    """
    Load and validate a CSV file.
    Returns (dataframe, error_message). If success, error is empty string.
    """
    try:
        df = pd.read_csv(file_path)
        df.columns = [c.strip() for c in df.columns]

        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            return None, f"Missing columns: {', '.join(missing)}"

        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        df.dropna(subset=["Amount"], inplace=True)

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df.dropna(subset=["Date"], inplace=True)

        df["Type"] = df["Type"].str.strip().str.title()

        if df.empty:
            return None, "CSV has no valid data rows after cleaning."

        return df, ""

    except FileNotFoundError:
        return None, "File not found."
    except Exception as e:
        return None, f"Error reading file: {e}"


def compute_summary(df: pd.DataFrame) -> dict:
    """Compute core financial summary from a cleaned dataframe."""
    income_df = df[df["Type"] == "Income"]
    expense_df = df[df["Type"] == "Expense"]

    total_income = income_df["Amount"].sum()
    total_expense = expense_df["Amount"].sum()
    savings = total_income - total_expense
    savings_rate = (savings / total_income * 100) if total_income > 0 else 0

    category_summary = (
        expense_df.groupby("Category")["Amount"]
        .sum()
        .sort_values(ascending=False)
    )

    monthly_expense = (
        expense_df.copy()
        .assign(Month=expense_df["Date"].dt.to_period("M"))
        .groupby("Month")["Amount"]
        .sum()
        .sort_index()
    )

    top_category = category_summary.idxmax() if not category_summary.empty else "N/A"
    top_category_amount = category_summary.max() if not category_summary.empty else 0

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "savings": savings,
        "savings_rate": savings_rate,
        "category_summary": category_summary,
        "monthly_expense": monthly_expense,
        "top_category": top_category,
        "top_category_amount": top_category_amount,
        "num_transactions": len(df),
    }


def build_ai_context(summary: dict) -> str:
    """Build a concise financial context string for AI prompting."""
    cats = summary["category_summary"]
    top_cats = "\n".join(
        [f"  - {cat}: ₹{amt:,.0f}" for cat, amt in cats.head(5).items()]
    ) if not cats.empty else "  No data"

    return f"""Total Income: ₹{summary['total_income']:,.0f}
Total Expense: ₹{summary['total_expense']:,.0f}
Savings: ₹{summary['savings']:,.0f}
Savings Rate: {summary['savings_rate']:.1f}%
Top Spending Category: {summary['top_category']} (₹{summary['top_category_amount']:,.0f})
Category Breakdown:
{top_cats}
Number of Transactions: {summary['num_transactions']}"""
