
import streamlit as st
import sqlite3
import pandas as pd
import altair as alt
from pathlib import Path
import sys

project_dir = Path(__file__).resolve().parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from hadoop.company_counts import run_hadoop_company_counts

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Job Market Analytics",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------

st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #e6f4ff;
}
[data-testid="stSidebar"] * {
    color: #1f2937;
}
.main-title {
    font-size: 36px;
    font-weight: 700;
    margin-bottom: 0px;
}
.subtitle {
    color: #666;
    font-size: 16px;
    margin-bottom: 25px;
}
.kpi-card {
    padding: 18px;
    border-radius: 10px;
    background-color: #f8f9fa;
    border: 1px solid #e5e7eb;
    text-align: center;
}
.kpi-title {
    font-size: 14px;
    color: #666;
}
.kpi-value {
    font-size: 28px;
    font-weight: 700;
    margin-top: 5px;
}
.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-top: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

@st.cache_data
def load_jobs():
    with sqlite3.connect("data/jobmarket.db") as conn:
        return pd.read_sql_query("SELECT * FROM jobs", conn)

df = load_jobs()

# ---------------------------------------------------------
# DATA CLEANING
# ---------------------------------------------------------

for column in ["title", "company", "location", "remote"]:
    df[column] = df[column].fillna("").astype(str)

df["posted"] = pd.to_datetime(df["posted"], errors="coerce")

# ---------------------------------------------------------
# HADOOP MAPREDUCE: FILTERED COMPANY COUNTS
# ---------------------------------------------------------

@st.cache_data(show_spinner=False)
def get_hadoop_company_counts(companies):
    return run_hadoop_company_counts(companies)


def get_precomputed_demo_company_counts(scenario):
    with sqlite3.connect("data/jobmarket.db") as conn:
        table_exists = conn.execute(
            """
            SELECT 1
            FROM sqlite_master
            WHERE type = 'table' AND name = 'demo_company_counts'
            """
        ).fetchone()
        if not table_exists:
            return None

        rows = conn.execute(
            """
            SELECT company, jobs
            FROM demo_company_counts
            WHERE scenario = ?
            """,
            (scenario,)
        ).fetchall()

    if not rows:
        return None

    return pd.DataFrame(
        [row for row in rows if row[0] is not None],
        columns=["Company", "Jobs"]
    )



# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    '<div class="main-title">📊 Job Market Analytics Dashboard</div>',
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------

st.sidebar.header("🎛️ Filters")
st.sidebar.markdown("### Job Search")

search = st.sidebar.text_input(
    "Job Role",
    placeholder="Example: Data Analyst"
)

location = st.sidebar.text_input(
    "Location",
    placeholder="Example: Mumbai"
)

company = st.sidebar.text_input(
    "Company",
    placeholder="Example: Google"
)

work_type = st.sidebar.selectbox(
    "Work Type",
    ["All", "Remote", "Onsite"]
)

st.sidebar.markdown("### Posted Date")

valid_dates = df["posted"].dropna()

if not valid_dates.empty:
    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()

    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
else:
    date_range = None

# ---------------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------------

filtered_df = df.copy()

if search:
    filtered_df = filtered_df[
        filtered_df["title"].str.contains(
            search, case=False, na=False
        )
    ]

if location:
    filtered_df = filtered_df[
        filtered_df["location"].str.contains(
            location, case=False, na=False
        )
    ]

if company:
    filtered_df = filtered_df[
        filtered_df["company"].str.contains(
            company, case=False, na=False
        )
    ]

if work_type == "Remote":
    filtered_df = filtered_df[
        filtered_df["remote"].str.lower() == "true"
    ]
elif work_type == "Onsite":
    filtered_df = filtered_df[
        filtered_df["remote"].str.lower() == "false"
    ]

if date_range and len(date_range) == 2:
    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)

    filtered_df = filtered_df[
        (filtered_df["posted"] >= start_date)
        & (filtered_df["posted"] < end_date)
    ]

# ---------------------------------------------------------
# KPI SECTION
# ---------------------------------------------------------

st.markdown("### 📌 Overview")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Jobs Found</div>
            <div class="kpi-value">{len(filtered_df):,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpi2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Companies</div>
            <div class="kpi-value">{filtered_df["company"].nunique():,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpi3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Locations</div>
            <div class="kpi-value">{filtered_df["location"].nunique():,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpi4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Job Roles</div>
            <div class="kpi-value">{filtered_df["title"].nunique():,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

# ---------------------------------------------------------
# TOP JOB ROLES + TOP COMPANIES
# ---------------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        '<div class="section-title">💼 Top Job Roles</div>',
        unsafe_allow_html=True
    )

    top_roles = (
        filtered_df["title"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    top_roles.columns = ["Job Role", "Jobs"]

    if not top_roles.empty:
        chart_roles = (
            alt.Chart(top_roles)
            .mark_bar()
            .encode(
                x=alt.X("Jobs:Q", title="Number of Jobs"),
                y=alt.Y("Job Role:N", sort="-x", title="Job Role"),
                tooltip=["Job Role", "Jobs"]
            )
            .properties(height=350)
        )

        st.altair_chart(chart_roles, use_container_width=True)
    else:
        st.info("No job roles found.")

with col2:
    st.markdown(
        '<div class="section-title">🏢 Top Companies</div>',
        unsafe_allow_html=True
    )

    try:
        demo_scenario = None
        if (
            not company
            and work_type == "All"
            and not valid_dates.empty
            and date_range
            and len(date_range) == 2
            and date_range[0] == valid_dates.min().date()
            and date_range[1] == valid_dates.max().date()
        ):
            demo_scenario = {
                ("", ""): "all",
                ("engineer", ""): "engineer",
                ("engineer", "mumbai"): "engineer_mumbai",
                ("analyst", ""): "analyst",
                ("analyst", "mumbai"): "analyst_mumbai",
            }.get((search.casefold(), location.casefold()))

        top_companies = (
            get_precomputed_demo_company_counts(demo_scenario)
            if demo_scenario
            else None
        )
        if top_companies is None:
            top_companies = get_hadoop_company_counts(filtered_df["company"])

        top_companies = (
            top_companies
            .sort_values("Jobs", ascending=False)
            .head(10)
        )

        if not top_companies.empty:
            chart_companies = (
                alt.Chart(top_companies)
                .mark_bar()
                .encode(
                    x=alt.X("Jobs:Q", title="Number of Jobs"),
                    y=alt.Y("Company:N", sort="-x", title="Company"),
                    tooltip=["Company", "Jobs"]
                )
                .properties(height=350)
            )

            st.altair_chart(chart_companies, use_container_width=True)
        else:
            st.info("No companies found.")

    except Exception as exc:
        st.error(f"Hadoop company counts failed: {exc}")
        st.exception(exc)

# ---------------------------------------------------------
# LOCATIONS + REMOTE/ONSITE
# ---------------------------------------------------------

st.divider()
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        '<div class="section-title">🌍 Top Job Locations</div>',
        unsafe_allow_html=True
    )

    top_locations = (
        filtered_df["location"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    top_locations.columns = ["Location", "Jobs"]

    if not top_locations.empty:
        chart_locations = (
            alt.Chart(top_locations)
            .mark_bar()
            .encode(
                x=alt.X("Jobs:Q", title="Number of Jobs"),
                y=alt.Y("Location:N", sort="-x", title="Location"),
                tooltip=["Location", "Jobs"]
            )
            .properties(height=350)
        )

        st.altair_chart(chart_locations, use_container_width=True)
    else:
        st.info("No locations found.")

with col2:
    st.markdown(
        '<div class="section-title">🏠 Remote vs Onsite</div>',
        unsafe_allow_html=True
    )

    work_counts = (
        filtered_df["remote"]
        .str.lower()
        .replace({"true": "Remote", "false": "Onsite"})
        .value_counts()
        .reset_index()
    )

    work_counts.columns = ["Work Type", "Jobs"]

    if not work_counts.empty:
        donut = (
            alt.Chart(work_counts)
            .mark_arc(innerRadius=70)
            .encode(
                theta=alt.Theta("Jobs:Q"),
                color=alt.Color(
                    "Work Type:N",
                    legend=alt.Legend(title="Work Type")
                ),
                tooltip=["Work Type", "Jobs"]
            )
            .properties(height=350)
        )

        st.altair_chart(donut, use_container_width=True)
    else:
        st.info("No work-type data found.")

# ---------------------------------------------------------
# HIRING TRENDS
# ---------------------------------------------------------

st.divider()

st.markdown(
    '<div class="section-title">📈 Hiring Trends</div>',
    unsafe_allow_html=True
)

trend = (
    filtered_df.dropna(subset=["posted"])
    .groupby("posted")
    .size()
    .reset_index(name="Jobs")
    .sort_values("posted")
)

if not trend.empty:
    trend_chart = (
        alt.Chart(trend)
        .mark_line(point=True)
        .encode(
            x=alt.X("posted:T", title="Posted Date"),
            y=alt.Y("Jobs:Q", title="Number of Jobs"),
            tooltip=[
                alt.Tooltip("posted:T", title="Date"),
                alt.Tooltip("Jobs:Q", title="Jobs")
            ]
        )
        .properties(height=350)
        .interactive()
    )

    st.altair_chart(trend_chart, use_container_width=True)
else:
    st.info("No hiring trend data found.")

# ---------------------------------------------------------
# JOB RESULTS
# ---------------------------------------------------------

st.divider()

st.markdown(
    '<div class="section-title">📋 Job Results</div>',
    unsafe_allow_html=True
)

st.caption(
    f"Showing up to 200 results from {len(filtered_df):,} matching jobs."
)

display_df = filtered_df.copy()
display_df["posted"] = display_df["posted"].dt.strftime("%Y-%m-%d")

st.dataframe(
    display_df[
        ["title", "company", "location", "remote", "posted"]
    ].head(200),
    use_container_width=True,
    height=400
)

# ---------------------------------------------------------
# EXPORT
# ---------------------------------------------------------

st.divider()

st.markdown(
    '<div class="section-title">⬇️ Export Results</div>',
    unsafe_allow_html=True
)

csv_data = filtered_df.to_csv(index=False)

st.download_button(
    label="📥 Download Filtered Jobs CSV",
    data=csv_data,
    file_name="filtered_jobs.csv",
    mime="text/csv"
)
