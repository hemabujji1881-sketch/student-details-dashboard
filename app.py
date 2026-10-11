import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# -------------------- Page setup --------------------
st.set_page_config(
    page_title="Student Performance Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / "data" / "StudentsPerformance.csv"

st.markdown("""
<style>
    .main-header {font-size: 2.25rem; font-weight: 800; margin-bottom: 0.15rem;}
    .sub-header {color: #64748b; margin-bottom: 1.2rem;}
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(59,130,246,.10), rgba(139,92,246,.08));
        border: 1px solid rgba(100,116,139,.20);
        padding: 15px 16px;
        border-radius: 14px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    data = pd.read_csv(path)
    data.columns = [c.strip() for c in data.columns]
    score_cols = ["math score", "reading score", "writing score"]
    for col in score_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    data = data.dropna(subset=score_cols).copy()
    data["average score"] = data[score_cols].mean(axis=1).round(2)
    data["total score"] = data[score_cols].sum(axis=1)
    data["performance band"] = pd.cut(
        data["average score"],
        bins=[-1, 39, 59, 79, 100],
        labels=["Needs support (0–39)", "Developing (40–59)", "Good (60–79)", "Excellent (80–100)"],
    )
    return data

st.markdown('<div class="main-header">🎓 Student Performance Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Explore student exam results. Every sidebar filter updates all KPIs, charts, and the table.</div>', unsafe_allow_html=True)

if not DATA_PATH.exists():
    st.error(f"Dataset not found: {DATA_PATH}. Make sure StudentsPerformance.csv is inside the data folder.")
    st.stop()

df = load_data(str(DATA_PATH))

# -------------------- Sidebar filters --------------------
st.sidebar.title("🔎 Dashboard Filters")
st.sidebar.caption("Selections below apply to every chart and KPI.")

def multi_filter(label, column):
    choices = sorted(df[column].dropna().unique().tolist())
    return st.sidebar.multiselect(label, choices, default=choices, key=f"filter_{column}")

gender_selected = multi_filter("Gender", "gender")
group_selected = multi_filter("Race / ethnicity group", "race/ethnicity")
education_selected = multi_filter("Parent education", "parental level of education")
lunch_selected = multi_filter("Lunch type", "lunch")
prep_selected = multi_filter("Test preparation", "test preparation course")
bands = df["performance band"].dropna().astype(str).unique().tolist()
band_selected = st.sidebar.multiselect(
    "Average-score band",
    options=bands,
    default=bands,
    key="filter_performance_band",
)

score_min, score_max = st.sidebar.slider(
    "Average score range",
    min_value=0,
    max_value=100,
    value=(0, 100),
    step=1,
    key="filter_average_score_range",
)

# One shared filtered dataframe drives the entire dashboard.
filtered = df[
    df["gender"].isin(gender_selected)
    & df["race/ethnicity"].isin(group_selected)
    & df["parental level of education"].isin(education_selected)
    & df["lunch"].isin(lunch_selected)
    & df["test preparation course"].isin(prep_selected)
    & df["performance band"].astype(str).isin(band_selected)
    & df["average score"].between(score_min, score_max)
].copy()

def reset_filters():
    for key in [
        "filter_gender",
        "filter_race/ethnicity",
        "filter_parental level of education",
        "filter_lunch",
        "filter_test preparation course",
        "filter_performance_band",
        "filter_average_score_range",
    ]:
        st.session_state.pop(key, None)

st.sidebar.divider()
st.sidebar.write(f"**Matching students:** {len(filtered):,} / {len(df):,}")
st.sidebar.button(
    "Reset all filters",
    use_container_width=True,
    on_click=reset_filters,
)

if filtered.empty:
    st.warning("No students match these filters. Choose more options in the sidebar.")
    st.stop()

# -------------------- KPI cards --------------------
score_cols = ["math score", "reading score", "writing score"]
avg_score = filtered["average score"].mean()
best_subject = filtered[score_cols].mean().idxmax().replace(" score", "").title()
pass_rate = (filtered["average score"] >= 40).mean() * 100

k1, k2, k3, k4 = st.columns(4)
k1.metric("Students in view", f"{len(filtered):,}", f"{len(filtered) / len(df) * 100:.1f}% of dataset")
k2.metric("Average score", f"{avg_score:.1f} / 100")
k3.metric("Highest-scoring subject", best_subject)
k4.metric("Average score ≥ 40", f"{pass_rate:.1f}%")

st.divider()

# -------------------- Charts --------------------
left, right = st.columns(2)

with left:
    subject_means = filtered[score_cols].mean().rename_axis("Subject").reset_index(name="Average score")
    subject_means["Subject"] = subject_means["Subject"].str.replace(" score", "", regex=False).str.title()
    fig_subject = px.bar(
        subject_means, x="Subject", y="Average score", color="Subject",
        title="Average score by subject", text_auto=".1f",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_subject.update_layout(showlegend=False, yaxis_range=[0, 100], height=370)
    st.plotly_chart(fig_subject, use_container_width=True)

with right:
    gender_means = filtered.groupby("gender", as_index=False)["average score"].mean()
    fig_gender = px.bar(
        gender_means, x="gender", y="average score", color="gender",
        title="Average score by gender", text_auto=".1f",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig_gender.update_layout(showlegend=False, yaxis_range=[0, 100], height=370)
    st.plotly_chart(fig_gender, use_container_width=True)

left, right = st.columns(2)

with left:
    fig_distribution = px.histogram(
        filtered, x="average score", color="gender", nbins=20,
        title="Distribution of average scores", barmode="overlay", opacity=0.75,
        labels={"average score": "Average score", "gender": "Gender"},
    )
    fig_distribution.update_layout(height=370)
    st.plotly_chart(fig_distribution, use_container_width=True)

with right:
    prep_means = filtered.groupby("test preparation course", as_index=False)["average score"].mean()
    fig_prep = px.bar(
        prep_means, x="test preparation course", y="average score",
        color="test preparation course", title="Test preparation vs average score",
        text_auto=".1f", labels={"test preparation course": "Test preparation"},
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig_prep.update_layout(showlegend=False, yaxis_range=[0, 100], height=370)
    st.plotly_chart(fig_prep, use_container_width=True)

left, right = st.columns(2)

with left:
    fig_scatter = px.scatter(
        filtered, x="math score", y="reading score", color="gender",
        size="writing score", hover_data=["race/ethnicity", "test preparation course"],
        title="Math vs reading scores",
        labels={"math score": "Math score", "reading score": "Reading score"},
    )
    fig_scatter.update_layout(height=390)
    st.plotly_chart(fig_scatter, use_container_width=True)

with right:
    heatmap_data = filtered[score_cols].corr()
    heatmap_data.index = ["Math", "Reading", "Writing"]
    heatmap_data.columns = ["Math", "Reading", "Writing"]
    fig_corr = px.imshow(
        heatmap_data, text_auto=".2f", color_continuous_scale="Blues",
        zmin=-1, zmax=1, title="Subject score correlation",
    )
    fig_corr.update_layout(height=390)
    st.plotly_chart(fig_corr, use_container_width=True)

# -------------------- Filtered data table --------------------
st.subheader("📋 Filtered student records")
st.caption("The table below uses the same sidebar selections as every chart above.")
display_columns = [
    "gender", "race/ethnicity", "parental level of education", "lunch",
    "test preparation course", "math score", "reading score", "writing score",
    "average score", "total score", "performance band",
]
st.dataframe(
    filtered[display_columns].sort_values("average score", ascending=False),
    use_container_width=True,
    hide_index=True,
)

csv_bytes = filtered[display_columns].to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download filtered records as CSV",
    data=csv_bytes,
    file_name="filtered_student_performance.csv",
    mime="text/csv",
)

st.caption("Dataset: Students Performance in Exams. Average score is calculated from math, reading, and writing scores.")
