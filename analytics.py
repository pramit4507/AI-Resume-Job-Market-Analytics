"""
analytics.py — All data-loading and computation functions for
AI Resume & Job Market Analytics.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------
_HERE = Path(__file__).parent
DEFAULT_CSV = _HERE.parent / "AI_Resume_Job_Market_Analytics_500.csv"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def load_data(path: str | None = None) -> pd.DataFrame:
    """Load and lightly clean the CSV. Cached after first call."""
    csv_path = Path(path) if path else DEFAULT_CSV
    df = pd.read_csv(csv_path)

    # Normalise column names
    df.columns = df.columns.str.strip()

    # Numeric salary columns
    for col in ("Salary_Min_LPA", "Salary_Max_LPA", "Experience_Years"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Mid-point salary (used for average-salary analyses)
    df["Salary_Avg_LPA"] = (df["Salary_Min_LPA"] + df["Salary_Max_LPA"]) / 2

    # Parse date
    df["Job_Posting_Date"] = pd.to_datetime(df["Job_Posting_Date"], errors="coerce")

    return df


# ---------------------------------------------------------------------------
# Helper: split comma-separated skill columns
# ---------------------------------------------------------------------------
def _split_col(series: pd.Series) -> pd.Series:
    """Return a flat Series of individual items from a comma-separated column."""
    return (
        series.dropna()
        .str.split(r",\s*")
        .explode()
        .str.strip()
        .loc[lambda s: s != ""]
        .loc[lambda s: s.str.lower() != "none"]
    )


# ---------------------------------------------------------------------------
# 1. Total job postings
# ---------------------------------------------------------------------------
def total_job_postings(df: pd.DataFrame) -> int:
    return len(df)


# ---------------------------------------------------------------------------
# 2. Postings by job role
# ---------------------------------------------------------------------------
def postings_by_role(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df["Job_Title"]
        .value_counts()
        .rename_axis("Job Title")
        .reset_index(name="Postings")
    )


# ---------------------------------------------------------------------------
# 3. Frequency of individual technical skills
# ---------------------------------------------------------------------------
def technical_skill_frequency(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    skills = _split_col(df["Required_Skills"])
    freq = skills.value_counts().head(top_n)
    return freq.rename_axis("Skill").reset_index(name="Frequency")


# ---------------------------------------------------------------------------
# 4. Frequency of soft skills
# ---------------------------------------------------------------------------
def soft_skill_frequency(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    skills = _split_col(df["Soft_Skills"])
    freq = skills.value_counts().head(top_n)
    return freq.rename_axis("Soft Skill").reset_index(name="Frequency")


# ---------------------------------------------------------------------------
# 5. Salary statistics (avg / min / max)
# ---------------------------------------------------------------------------
def salary_stats(df: pd.DataFrame) -> dict:
    return {
        "Overall Min (LPA)": round(df["Salary_Min_LPA"].min(), 2),
        "Overall Max (LPA)": round(df["Salary_Max_LPA"].max(), 2),
        "Average Mid-Point (LPA)": round(df["Salary_Avg_LPA"].mean(), 2),
        "Median Mid-Point (LPA)": round(df["Salary_Avg_LPA"].median(), 2),
    }


# ---------------------------------------------------------------------------
# 6. Average salary by job role
# ---------------------------------------------------------------------------
def avg_salary_by_role(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Job_Title")["Salary_Avg_LPA"]
        .mean()
        .round(2)
        .sort_values(ascending=False)
        .rename_axis("Job Title")
        .reset_index(name="Avg Salary (LPA)")
    )


# ---------------------------------------------------------------------------
# 7. Average experience requirement
# ---------------------------------------------------------------------------
def experience_stats(df: pd.DataFrame) -> dict:
    return {
        "Average (yrs)": round(df["Experience_Years"].mean(), 2),
        "Minimum (yrs)": int(df["Experience_Years"].min()),
        "Maximum (yrs)": int(df["Experience_Years"].max()),
        "Median (yrs)": round(df["Experience_Years"].median(), 2),
    }


def avg_experience_by_role(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Job_Title")["Experience_Years"]
        .mean()
        .round(2)
        .sort_values(ascending=False)
        .rename_axis("Job Title")
        .reset_index(name="Avg Experience (yrs)")
    )


# ---------------------------------------------------------------------------
# 8. Jobs by location
# ---------------------------------------------------------------------------
def jobs_by_location(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df["Location"]
        .value_counts()
        .rename_axis("Location")
        .reset_index(name="Postings")
    )


# ---------------------------------------------------------------------------
# 9. Remote vs on-site distribution
# ---------------------------------------------------------------------------
def work_mode_distribution(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df["Work_Mode"]
        .value_counts()
        .rename_axis("Work Mode")
        .reset_index(name="Count")
    )


# ---------------------------------------------------------------------------
# 10. Education requirement distribution
# ---------------------------------------------------------------------------
def education_distribution(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df["Education"]
        .value_counts()
        .rename_axis("Education")
        .reset_index(name="Count")
    )


# ---------------------------------------------------------------------------
# 11. Skill combinations (top co-occurring pairs)
# ---------------------------------------------------------------------------
def skill_combinations(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    from itertools import combinations

    pair_counts: dict[tuple, int] = {}
    for skills_str in df["Required_Skills"].dropna():
        skills = sorted(
            {s.strip() for s in skills_str.split(",") if s.strip()}
        )
        for pair in combinations(skills, 2):
            pair_counts[pair] = pair_counts.get(pair, 0) + 1

    result = (
        pd.Series(pair_counts, name="Count")
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    result.columns = ["Skill A", "Skill B", "Co-occurrences"]
    return result


# ---------------------------------------------------------------------------
# 12. Relationship between experience and salary
# ---------------------------------------------------------------------------
def experience_salary_scatter(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["Job_Title", "Location", "Work_Mode", "Experience_Years",
            "Salary_Avg_LPA", "Salary_Min_LPA", "Salary_Max_LPA"]
    return df[cols].dropna()
