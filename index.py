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

fig, ax = plt.subplots(figsize=(18, 6))
for hub in non_zero_days.columns:
    ax.plot(non_zero_days.index, non_zero_days[hub], marker='o', label=hub)
    for x, y in zip(non_zero_days.index, non_zero_days[hub]):
        if y != 0:
            label = f"{x.strftime('%b-%d')}\n{y:.1f}"
            ax.annotate(label, xy=(x, y), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)

ax.set_title("Full Daily SR Trends")
ax.set_ylabel("Sales Realisation")
ax.set_xlabel("Date")
ax.legend()
fig.autofmt_xdate()
st.pyplot(fig)

# Comparison Section
st.subheader("Day-wise Sales Comparison by Hub")
comparison_df = filtered_df.set_index('Hub Name')[date_cols].transpose().reset_index()
comparison_df = comparison_df.melt(id_vars='index', var_name='Hub', value_name='Sales')
comparison_df = comparison_df[comparison_df['Sales'] > 0]
comparison_df.rename(columns={'index': 'Date'}, inplace=True)
comparison_df['Date'] = pd.to_datetime(comparison_df['Date'])

fig2, ax2 = plt.subplots(figsize=(18, 6))
sns.barplot(data=comparison_df, x='Date', y='Sales', hue='Hub', ax=ax2)

# Add data labels
for container in ax2.containers:
    ax2.bar_label(container, fmt='%.1f', label_type='edge', fontsize=8, padding=2)

ax2.set_title("Daily Sales Comparison - Bar Chart")
ax2.set_ylabel("Sales Realisation")
ax2.set_xlabel("Date")
fig2.autofmt_xdate()
st.pyplot(fig2)

# Detail check per hub
st.subheader("Detailed Hub-wise Data View")
selected_hub = st.selectbox("Choose a Hub to inspect", hubs)
hub_details = summary_df[summary_df['Hub Name'] == selected_hub].T
hub_details.columns = [selected_hub]
st.dataframe(hub_details.dropna())

# Insights Section
st.subheader("🔍 Key Insights")

insight_points = []

# Top-performing hub by average SR
top_hub_row = summary_df.loc[summary_df['MTD SR'].idxmax()]
top_hub = top_hub_row['Hub Name']
top_value = top_hub_row['MTD SR']
insight_points.append(f"✅ **Top-performing hub** (by average SR): `{top_hub}` with MTD SR of `{top_value:.2f}`.")

# Most consistent hub (lowest std dev across days)
std_devs = summary_df[date_cols].std(axis=1)
consistent_index = std_devs.idxmin()
consistent_hub = summary_df.loc[consistent_index, 'Hub Name']
insight_points.append(f"📉 **Most consistent performer**: `{consistent_hub}` (lowest fluctuation in daily SR values).")

# Most productive day per hub
for hub in selected_hubs:
    row = summary_df[summary_df['Hub Name'] == hub]
    max_day_col = row[date_cols].iloc[0].idxmax()
    max_val = row[max_day_col].values[0]
    insight_points.append(f"📌 **{hub}** had its highest SR of `{max_val:.2f}` on `{pd.to_datetime(max_day_col).strftime('%B %d')}`.")

for point in insight_points:
    st.markdown(point)
