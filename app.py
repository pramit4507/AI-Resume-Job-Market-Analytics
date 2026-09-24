"""
app.py — Streamlit frontend for AI Resume & Job Market Analytics.
Run:  streamlit run job_market_analytics/app.py
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Make sure the package directory is importable
sys.path.insert(0, str(Path(__file__).parent))
import analytics as an

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Job Market Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — clean, readable
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
        /* Main background */
        .main { background-color: #f7f9fc; }

        /* Card-style metric boxes */
        [data-testid="metric-container"] {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 16px 20px;
        }
        [data-testid="metric-container"] label {
            font-size: 0.78rem !important;
            color: #64748b !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        [data-testid="metric-container"] [data-testid="stMetricValue"] {
            font-size: 1.6rem !important;
            font-weight: 700;
            color: #1e293b !important;
        }

        /* Section titles */
        .section-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: #1e293b;
            border-left: 4px solid #3b82f6;
            padding-left: 10px;
            margin-top: 8px;
            margin-bottom: 4px;
        }

        /* Divider spacing */
        hr { margin: 2rem 0 1.5rem 0; border-color: #e2e8f0; }

        /* Sidebar */
        [data-testid="stSidebar"] { background-color: #1e293b; }
        [data-testid="stSidebar"] * { color: #f1f5f9 !important; }
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stSlider label { color: #94a3b8 !important; }

        /* Table styling */
        .stDataFrame { border-radius: 8px; overflow: hidden; }

        /* Hide Streamlit branding */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar — navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 📊 Job Market Analytics")
    st.markdown("---")
    section = st.radio(
        "Navigate to",
        [
            "🏠 Overview",
            "📋 Job Roles",
            "🛠️ Technical Skills",
            "🤝 Soft Skills",
            "💰 Salary Analysis",
            "🎓 Education & Experience",
            "🌍 Location & Work Mode",
            "🔗 Skill Combinations",
            "📈 Experience vs Salary",
        ],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption("Dataset: AI Resume & Job Market Analytics")


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
@st.cache_data
def get_data() -> pd.DataFrame:
    return an.load_data()


df = get_data()


# ---------------------------------------------------------------------------
# Helper — consistent chart theme
# ---------------------------------------------------------------------------
CHART_TEMPLATE = "plotly_white"
PRIMARY_COLOR = "#3b82f6"
COLOR_SEQ = px.colors.qualitative.Bold


def section_title(text: str):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def display_table(dataframe: pd.DataFrame, height: int = 350):
    st.dataframe(dataframe, use_container_width=True, height=height, hide_index=True)


# ===========================================================================
# SECTION: Overview
# ===========================================================================
if section == "🏠 Overview":
    st.title("🧠 AI Resume & Job Market Analytics")
    st.markdown(
        "An end-to-end analytical view of **500 AI/tech job postings** — "
        "covering roles, skills, salaries, locations, and more."
    )
    st.markdown("---")

    # --- KPI row ---
    total = an.total_job_postings(df)
    s_stats = an.salary_stats(df)
    exp_stats = an.experience_stats(df)
    roles = df["Job_Title"].nunique()
    locations = df["Location"].nunique()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Postings", f"{total:,}")
    c2.metric("Unique Job Roles", roles)
    c3.metric("Cities Covered", locations)
    c4.metric("Avg Salary (LPA)", f"₹ {s_stats['Average Mid-Point (LPA)']}")
    c5.metric("Avg Experience", f"{exp_stats['Average (yrs)']} yrs")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        section_title("Top Job Roles by Postings")
        role_df = an.postings_by_role(df)
        fig = px.bar(
            role_df.head(10),
            x="Postings",
            y="Job Title",
            orientation="h",
            color="Postings",
            color_continuous_scale="Blues",
            template=CHART_TEMPLATE,
        )
        fig.update_layout(
            height=340,
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=0, r=10, t=10, b=10),
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        section_title("Work Mode Distribution")
        wm = an.work_mode_distribution(df)
        fig2 = px.pie(
            wm,
            names="Work Mode",
            values="Count",
            hole=0.45,
            color_discrete_sequence=COLOR_SEQ,
            template=CHART_TEMPLATE,
        )
        fig2.update_traces(textposition="outside", textinfo="percent+label")
        fig2.update_layout(
            height=340,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=True,
            legend=dict(orientation="h", y=-0.1),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    col_c, col_d = st.columns(2)

    with col_c:
        section_title("Top Locations by Postings")
        loc_df = an.jobs_by_location(df)
        fig3 = px.bar(
            loc_df.head(10),
            x="Location",
            y="Postings",
            color="Postings",
            color_continuous_scale="Teal",
            template=CHART_TEMPLATE,
        )
        fig3.update_layout(
            height=320,
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=10, b=10),
            xaxis_tickangle=-30,
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        section_title("Education Requirement Distribution")
        edu_df = an.education_distribution(df)
        fig4 = px.pie(
            edu_df,
            names="Education",
            values="Count",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel,
            template=CHART_TEMPLATE,
        )
        fig4.update_traces(textposition="outside", textinfo="percent+label")
        fig4.update_layout(
            height=320,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
        )
        st.plotly_chart(fig4, use_container_width=True)


# ===========================================================================
# SECTION: Job Roles
# ===========================================================================
elif section == "📋 Job Roles":
    st.title("📋 Job Roles Analysis")
    st.markdown("---")

    role_df = an.postings_by_role(df)

    col1, col2 = st.columns([3, 2])

    with col1:
        section_title("Number of Postings by Job Role")
        fig = px.bar(
            role_df,
            x="Postings",
            y="Job Title",
            orientation="h",
            color="Postings",
            color_continuous_scale="Blues",
            text="Postings",
            template=CHART_TEMPLATE,
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            height=500,
            coloraxis_showscale=False,
            margin=dict(l=0, r=60, t=10, b=10),
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_title("Data Table")
        role_df["% Share"] = (role_df["Postings"] / role_df["Postings"].sum() * 100).round(1)
        display_table(role_df, height=500)

    st.markdown("---")
    section_title("Average Salary by Job Role")

    sal_role = an.avg_salary_by_role(df)
    fig2 = px.bar(
        sal_role,
        x="Job Title",
        y="Avg Salary (LPA)",
        color="Avg Salary (LPA)",
        color_continuous_scale="Viridis",
        text=sal_role["Avg Salary (LPA)"].apply(lambda v: f"₹{v}"),
        template=CHART_TEMPLATE,
    )
    fig2.update_traces(textposition="outside")
    fig2.update_layout(
        height=380,
        coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=10, b=10),
    )
    st.plotly_chart(fig2, use_container_width=True)


# ===========================================================================
# SECTION: Technical Skills
# ===========================================================================
elif section == "🛠️ Technical Skills":
    st.title("🛠️ Technical Skills Frequency")
    st.markdown("---")

    top_n = st.slider("Number of top skills to display", 5, 40, 20)
    tech_df = an.technical_skill_frequency(df, top_n=top_n)

    col1, col2 = st.columns([3, 2])

    with col1:
        section_title(f"Top {top_n} Technical Skills")
        fig = px.bar(
            tech_df,
            x="Frequency",
            y="Skill",
            orientation="h",
            color="Frequency",
            color_continuous_scale="Turbo",
            text="Frequency",
            template=CHART_TEMPLATE,
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            height=max(400, top_n * 24),
            coloraxis_showscale=False,
            margin=dict(l=0, r=60, t=10, b=10),
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_title("Skill Frequency Table")
        tech_df["% of Jobs"] = (tech_df["Frequency"] / len(df) * 100).round(1)
        display_table(tech_df, height=max(400, top_n * 24))


# ===========================================================================
# SECTION: Soft Skills
# ===========================================================================
elif section == "🤝 Soft Skills":
    st.title("🤝 Soft Skills Frequency")
    st.markdown("---")

    top_n = st.slider("Number of top soft skills to display", 5, 20, 15)
    soft_df = an.soft_skill_frequency(df, top_n=top_n)

    col1, col2 = st.columns([3, 2])

    with col1:
        section_title(f"Top {top_n} Soft Skills")
        fig = px.bar(
            soft_df,
            x="Frequency",
            y="Soft Skill",
            orientation="h",
            color="Frequency",
            color_continuous_scale="Magma",
            text="Frequency",
            template=CHART_TEMPLATE,
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            height=max(350, top_n * 28),
            coloraxis_showscale=False,
            margin=dict(l=0, r=60, t=10, b=10),
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_title("Soft Skill Frequency Table")
        soft_df["% of Jobs"] = (soft_df["Frequency"] / len(df) * 100).round(1)
        display_table(soft_df, height=max(350, top_n * 28))

    st.markdown("---")
    section_title("Soft Skill Distribution — Treemap")
    fig2 = px.treemap(
        soft_df,
        path=["Soft Skill"],
        values="Frequency",
        color="Frequency",
        color_continuous_scale="RdYlGn",
        template=CHART_TEMPLATE,
    )
    fig2.update_layout(height=380, margin=dict(l=0, r=0, t=10, b=10))
    st.plotly_chart(fig2, use_container_width=True)


# ===========================================================================
# SECTION: Salary Analysis
# ===========================================================================
elif section == "💰 Salary Analysis":
    st.title("💰 Salary Analysis")
    st.markdown("---")

    s_stats = an.salary_stats(df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall Min Salary", f"₹ {s_stats['Overall Min (LPA)']} LPA")
    c2.metric("Overall Max Salary", f"₹ {s_stats['Overall Max (LPA)']} LPA")
    c3.metric("Avg Mid-Point", f"₹ {s_stats['Average Mid-Point (LPA)']} LPA")
    c4.metric("Median Mid-Point", f"₹ {s_stats['Median Mid-Point (LPA)']} LPA")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        section_title("Salary Distribution (Mid-Point LPA)")
        fig = px.histogram(
            df,
            x="Salary_Avg_LPA",
            nbins=30,
            color_discrete_sequence=[PRIMARY_COLOR],
            template=CHART_TEMPLATE,
            labels={"Salary_Avg_LPA": "Avg Salary (LPA)"},
        )
        fig.update_layout(
            height=360,
            margin=dict(l=0, r=0, t=10, b=10),
            bargap=0.05,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_title("Salary Range by Job Role (Box Plot)")
        fig2 = px.box(
            df,
            x="Job_Title",
            y="Salary_Avg_LPA",
            color="Job_Title",
            color_discrete_sequence=COLOR_SEQ,
            template=CHART_TEMPLATE,
            labels={
                "Salary_Avg_LPA": "Avg Salary (LPA)",
                "Job_Title": "Job Role",
            },
        )
        fig2.update_layout(
            height=360,
            showlegend=False,
            margin=dict(l=0, r=0, t=10, b=10),
            xaxis_tickangle=-30,
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    section_title("Average Salary by Job Role")

    sal_role = an.avg_salary_by_role(df)
    fig3 = px.bar(
        sal_role,
        x="Job Title",
        y="Avg Salary (LPA)",
        color="Avg Salary (LPA)",
        color_continuous_scale="Plasma",
        text=sal_role["Avg Salary (LPA)"].apply(lambda v: f"₹{v}"),
        template=CHART_TEMPLATE,
    )
    fig3.update_traces(textposition="outside")
    fig3.update_layout(
        height=380,
        coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=10, b=10),
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    section_title("Salary by Work Mode")
    fig4 = px.box(
        df,
        x="Work_Mode",
        y="Salary_Avg_LPA",
        color="Work_Mode",
        color_discrete_sequence=COLOR_SEQ,
        template=CHART_TEMPLATE,
        labels={"Salary_Avg_LPA": "Avg Salary (LPA)", "Work_Mode": "Work Mode"},
    )
    fig4.update_layout(
        height=340,
        showlegend=False,
        margin=dict(l=0, r=0, t=10, b=10),
    )
    st.plotly_chart(fig4, use_container_width=True)


# ===========================================================================
# SECTION: Education & Experience
# ===========================================================================
elif section == "🎓 Education & Experience":
    st.title("🎓 Education & Experience Requirements")
    st.markdown("---")

    # --- Experience KPIs ---
    exp_stats = an.experience_stats(df)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Avg Experience", f"{exp_stats['Average (yrs)']} yrs")
    c2.metric("Min Experience", f"{exp_stats['Minimum (yrs)']} yrs")
    c3.metric("Max Experience", f"{exp_stats['Maximum (yrs)']} yrs")
    c4.metric("Median Experience", f"{exp_stats['Median (yrs)']} yrs")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        section_title("Education Requirement Distribution")
        edu_df = an.education_distribution(df)
        fig = px.pie(
            edu_df,
            names="Education",
            values="Count",
            hole=0.4,
            color_discrete_sequence=COLOR_SEQ,
            template=CHART_TEMPLATE,
        )
        fig.update_traces(textposition="outside", textinfo="percent+label")
        fig.update_layout(
            height=380,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
        display_table(edu_df, height=220)

    with col2:
        section_title("Experience Distribution (Histogram)")
        fig2 = px.histogram(
            df,
            x="Experience_Years",
            nbins=15,
            color_discrete_sequence=["#7c5cd8"],
            template=CHART_TEMPLATE,
            labels={"Experience_Years": "Experience (Years)"},
        )
        fig2.update_layout(
            height=380,
            margin=dict(l=0, r=0, t=10, b=10),
            bargap=0.05,
        )
        st.plotly_chart(fig2, use_container_width=True)

        section_title("Avg Experience by Job Role")
        exp_role = an.avg_experience_by_role(df)
        display_table(exp_role, height=220)

    st.markdown("---")
    section_title("Average Experience by Job Role (Bar)")
    fig3 = px.bar(
        exp_role,
        x="Job Title",
        y="Avg Experience (yrs)",
        color="Avg Experience (yrs)",
        color_continuous_scale="Cividis",
        text=exp_role["Avg Experience (yrs)"].apply(lambda v: f"{v} yrs"),
        template=CHART_TEMPLATE,
    )
    fig3.update_traces(textposition="outside")
    fig3.update_layout(
        height=360,
        coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=10, b=10),
    )
    st.plotly_chart(fig3, use_container_width=True)


# ===========================================================================
# SECTION: Location & Work Mode
# ===========================================================================
elif section == "🌍 Location & Work Mode":
    st.title("🌍 Location & Work Mode Analysis")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        section_title("Job Postings by City")
        loc_df = an.jobs_by_location(df)
        fig = px.bar(
            loc_df,
            x="Postings",
            y="Location",
            orientation="h",
            color="Postings",
            color_continuous_scale="Blues",
            text="Postings",
            template=CHART_TEMPLATE,
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            height=480,
            coloraxis_showscale=False,
            margin=dict(l=0, r=60, t=10, b=10),
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_title("Remote vs Onsite vs Hybrid")
        wm = an.work_mode_distribution(df)
        fig2 = px.pie(
            wm,
            names="Work Mode",
            values="Count",
            hole=0.45,
            color_discrete_sequence=COLOR_SEQ,
            template=CHART_TEMPLATE,
        )
        fig2.update_traces(
            textposition="outside",
            textinfo="percent+label",
        )
        fig2.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=10, b=30),
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)

        section_title("Work Mode Table")
        wm["% Share"] = (wm["Count"] / wm["Count"].sum() * 100).round(1)
        display_table(wm, height=160)

    st.markdown("---")
    section_title("Work Mode Distribution by Job Role (Stacked Bar)")
    wm_role = (
        df.groupby(["Job_Title", "Work_Mode"])
        .size()
        .reset_index(name="Count")
    )
    fig3 = px.bar(
        wm_role,
        x="Job_Title",
        y="Count",
        color="Work_Mode",
        barmode="stack",
        color_discrete_sequence=COLOR_SEQ,
        template=CHART_TEMPLATE,
        labels={"Job_Title": "Job Role", "Count": "Postings", "Work_Mode": "Work Mode"},
    )
    fig3.update_layout(
        height=380,
        margin=dict(l=0, r=0, t=10, b=10),
        xaxis_tickangle=-30,
        legend=dict(orientation="h", y=1.05),
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    section_title("Average Salary by Location (Top 10)")
    sal_loc = (
        df.groupby("Location")["Salary_Avg_LPA"]
        .mean()
        .round(2)
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    sal_loc.columns = ["Location", "Avg Salary (LPA)"]
    fig4 = px.bar(
        sal_loc,
        x="Location",
        y="Avg Salary (LPA)",
        color="Avg Salary (LPA)",
        color_continuous_scale="Sunset",
        text=sal_loc["Avg Salary (LPA)"].apply(lambda v: f"₹{v}"),
        template=CHART_TEMPLATE,
    )
    fig4.update_traces(textposition="outside")
    fig4.update_layout(
        height=360,
        coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=10, b=10),
    )
    st.plotly_chart(fig4, use_container_width=True)


# ===========================================================================
# SECTION: Skill Combinations
# ===========================================================================
elif section == "🔗 Skill Combinations":
    st.title("🔗 Skill Combinations")
    st.markdown("Most frequently co-occurring pairs of technical skills in job postings.")
    st.markdown("---")

    top_n = st.slider("Number of top skill pairs to display", 5, 30, 15)
    combo_df = an.skill_combinations(df, top_n=top_n)

    col1, col2 = st.columns([3, 2])

    with col1:
        section_title(f"Top {top_n} Co-occurring Skill Pairs")
        combo_df["Pair"] = combo_df["Skill A"] + "  +  " + combo_df["Skill B"]
        fig = px.bar(
            combo_df,
            x="Co-occurrences",
            y="Pair",
            orientation="h",
            color="Co-occurrences",
            color_continuous_scale="Teal",
            text="Co-occurrences",
            template=CHART_TEMPLATE,
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            height=max(400, top_n * 28),
            coloraxis_showscale=False,
            margin=dict(l=0, r=60, t=10, b=10),
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_title("Skill Pairs Table")
        display_table(combo_df[["Skill A", "Skill B", "Co-occurrences"]], height=max(400, top_n * 28))


# ===========================================================================
# SECTION: Experience vs Salary
# ===========================================================================
elif section == "📈 Experience vs Salary":
    st.title("📈 Experience vs Salary Relationship")
    st.markdown("---")

    scatter_df = an.experience_salary_scatter(df)

    # Filters
    fc1, fc2 = st.columns(2)
    with fc1:
        roles = ["All Roles"] + sorted(scatter_df["Job_Title"].unique().tolist())
        selected_role = st.selectbox("Filter by Job Role", roles)
    with fc2:
        modes = ["All Modes"] + sorted(scatter_df["Work_Mode"].unique().tolist())
        selected_mode = st.selectbox("Filter by Work Mode", modes)

    filtered = scatter_df.copy()
    if selected_role != "All Roles":
        filtered = filtered[filtered["Job_Title"] == selected_role]
    if selected_mode != "All Modes":
        filtered = filtered[filtered["Work_Mode"] == selected_mode]

    st.markdown(f"**Showing {len(filtered):,} records**")
    st.markdown("---")

    col1, col2 = st.columns([3, 2])

    with col1:
        section_title("Experience (Years) vs Avg Salary (LPA)")
        import numpy as _np

        fig = px.scatter(
            filtered,
            x="Experience_Years",
            y="Salary_Avg_LPA",
            color="Job_Title",
            symbol="Work_Mode",
            hover_data=["Location", "Salary_Min_LPA", "Salary_Max_LPA"],
            color_discrete_sequence=COLOR_SEQ,
            template=CHART_TEMPLATE,
            labels={
                "Experience_Years": "Experience (Years)",
                "Salary_Avg_LPA": "Avg Salary (LPA)",
                "Job_Title": "Job Role",
                "Work_Mode": "Work Mode",
            },
        )
        # Manual OLS trend line (no statsmodels needed)
        _valid = filtered[["Experience_Years", "Salary_Avg_LPA"]].dropna()
        if len(_valid) > 1:
            _m, _b = _np.polyfit(_valid["Experience_Years"], _valid["Salary_Avg_LPA"], 1)
            _xr = _np.linspace(_valid["Experience_Years"].min(), _valid["Experience_Years"].max(), 100)
            fig.add_trace(
                go.Scatter(
                    x=_xr,
                    y=_m * _xr + _b,
                    mode="lines",
                    name="Trend",
                    line=dict(color="black", dash="dash", width=1.5),
                )
            )
        fig.update_layout(
            height=480,
            margin=dict(l=0, r=0, t=10, b=10),
            legend=dict(orientation="v", x=1.01),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_title("Avg Salary by Experience Band")
        bins = [0, 1, 3, 5, 8, 100]
        labels = ["0-1 yr", "1-3 yrs", "3-5 yrs", "5-8 yrs", "8+ yrs"]
        filtered = filtered.copy()
        filtered["Exp Band"] = pd.cut(
            filtered["Experience_Years"], bins=bins, labels=labels, right=True
        )
        band_salary = (
            filtered.groupby("Exp Band", observed=True)["Salary_Avg_LPA"]
            .mean()
            .round(2)
            .reset_index()
        )
        band_salary.columns = ["Experience Band", "Avg Salary (LPA)"]
        fig2 = px.bar(
            band_salary,
            x="Experience Band",
            y="Avg Salary (LPA)",
            color="Avg Salary (LPA)",
            color_continuous_scale="Reds",
            text=band_salary["Avg Salary (LPA)"].apply(lambda v: f"₹{v}"),
            template=CHART_TEMPLATE,
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(
            height=320,
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=10, b=10),
        )
        st.plotly_chart(fig2, use_container_width=True)

        section_title("Correlation Heatmap")
        corr_df = filtered[["Experience_Years", "Salary_Min_LPA", "Salary_Max_LPA", "Salary_Avg_LPA"]].corr().round(3)
        fig3 = px.imshow(
            corr_df,
            text_auto=True,
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            template=CHART_TEMPLATE,
            labels=dict(color="Correlation"),
        )
        fig3.update_layout(
            height=280,
            margin=dict(l=0, r=0, t=10, b=10),
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    section_title("Raw Data Preview (Filtered)")
    disp = filtered[
        ["Job_Title", "Location", "Work_Mode", "Experience_Years",
         "Salary_Min_LPA", "Salary_Max_LPA", "Salary_Avg_LPA"]
    ].rename(columns={
        "Job_Title": "Role",
        "Work_Mode": "Mode",
        "Experience_Years": "Exp (yrs)",
        "Salary_Min_LPA": "Min LPA",
        "Salary_Max_LPA": "Max LPA",
        "Salary_Avg_LPA": "Avg LPA",
    })
    display_table(disp, height=320)
