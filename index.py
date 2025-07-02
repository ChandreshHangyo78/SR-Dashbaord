import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the Excel file
@st.cache_data

def load_data():
    xls = pd.ExcelFile("Sales Realization Report-Jun'25.xlsx")
    summary_df = xls.parse('Sales Realisation Summary')
    hub_wise_df = xls.parse('Hub Wise Sales Realisation', skiprows=1)
    return summary_df, hub_wise_df

summary_df, hub_wise_df = load_data()

# Page title
st.title("Sales Realisation Dashboard - June 2025")

# Clean columns
summary_df.columns = summary_df.columns.astype(str)
date_cols = [col for col in summary_df.columns if "2025" in col and not col.endswith("07-01 00:00:00")]

# Sidebar filters
hubs = summary_df['Hub Name'].dropna().unique()
selected_hubs = st.sidebar.multiselect("Select Hubs", hubs, default=hubs[:5])

# Filtered Data
filtered_df = summary_df[summary_df['Hub Name'].isin(selected_hubs)]

# Only show KPIs: MTD SR, Highest, Lowest
st.subheader("Summary KPIs")
for hub in selected_hubs:
    mtd = summary_df.loc[summary_df['Hub Name'] == hub, 'MTD SR'].values[0]
    st.metric(label=f"{hub} - MTD SR", value=f"{mtd:.2f}")

# Line chart: Full daily SR for selected hubs (exclude zero-only days)
st.subheader("Full Day-wise Sales Realisation Trend")
trend_df = filtered_df.set_index('Hub Name')[date_cols].transpose()
trend_df.index = pd.to_datetime(trend_df.index)

# Drop days where all selected hubs have zero SR
non_zero_days = trend_df[(trend_df != 0).any(axis=1)]

fig, ax = plt.subplots(figsize=(16, 8))
for hub in non_zero_days.columns:
    ax.plot(non_zero_days.index, non_zero_days[hub], marker='o', label=hub)
    for x, y in zip(non_zero_days.index, non_zero_days[hub]):
        ax.annotate(f"{x.strftime('%b-%d')}", xy=(x, y), textcoords="offset points", xytext=(0,5), ha='center', fontsize=8)

ax.set_title("Full Daily SR Trends")
ax.set_ylabel("Sales Realisation")
ax.set_xlabel("Date")
ax.legend()
st.pyplot(fig)

# Detail check per hub
st.subheader("Detailed Hub-wise Data View")
selected_hub = st.selectbox("Choose a Hub to inspect", hubs)
hub_details = summary_df[summary_df['Hub Name'] == selected_hub].T
hub_details.columns = [selected_hub]
st.dataframe(hub_details.dropna())
