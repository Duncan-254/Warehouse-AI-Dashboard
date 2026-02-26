# dashboard.py
# Run with: streamlit run dashboard.py

import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from datetime import datetime
import os

CSV_PATH = "attendance_logs.csv"

st.set_page_config(page_title="Warehouse AI Dashboard", layout="wide")
st.title("Warehouse AI Attendance Dashboard")
st.markdown("**Managerial Overview** — Total activity, employee breakdown, peak times")

# Load CSV
@st.cache_data(ttl=10)
def load_data():
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        return df
    return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("No data yet. Run main.py to start detection and generate logs.")
    st.stop()

# ── TOTAL DETECTIONS ──
st.subheader("Total Detections (High-level Throughput)")
today = datetime.now().strftime("%Y-%m-%d")
today_df = df[df['Timestamp'].dt.date == pd.to_datetime(today).date()]

col1, col2, col3 = st.columns(3)
col1.metric("Today", len(today_df))
col2.metric("All Time", len(df))
col3.metric("Unique Names Today", len(today_df['Name'].unique()) if 'Name' in df else 0)

# ── EMPLOYEE BAR CHART ──
st.subheader("Employee Bar Chart – Breakdown of Presence by Individual")

if 'Name' in df.columns and not df.empty:
    counts = df['Name'].value_counts().reset_index()
    counts.columns = ['Name', 'Count']

    bar = alt.Chart(counts).mark_bar().encode(
        x='Count:Q',
        y=alt.Y('Name:N', sort='-x'),
        color='Count:Q',
        tooltip=['Name', 'Count']
    ).properties(
        title="Presence by Individual",
        height=400
    )

    st.altair_chart(bar, use_container_width=True)
else:
    st.info("No name data yet.")

# ── ACTIVITY HEATMAP ──
st.subheader("Activity Heatmap – Peak Detection Times")

if not df.empty:
    df['Hour'] = df['Timestamp'].dt.hour
    df['Date'] = df['Timestamp'].dt.date.astype(str)

    heat = df.groupby(['Date', 'Hour']).size().reset_index(name='Count')

    fig = px.density_heatmap(
        heat,
        x='Hour',
        y='Date',
        z='Count',
        color_continuous_scale='YlOrRd',
        title="Peak Times Heatmap",
        labels={'Hour': 'Hour (0-23)', 'Date': 'Date', 'Count': 'Detections'}
    )

    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data for heatmap.")

st.caption(f"Last refresh: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")