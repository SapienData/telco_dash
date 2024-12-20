import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from PIL import Image
import base64


# Load the dataset
data_path = 'mock_telecom_metrics_data.csv'
df = pd.read_csv(data_path)

# Ensure 'Date' is in datetime format
if not pd.api.types.is_datetime64_any_dtype(df['Date']):
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Define the numeric columns
numeric_cols = [
    'ARPU ($)', 'CLV ($)', 'ChurnRate (%)', 'NPS', 'CAC ($)', 'CSAT',
    'UpsellCrosssellRate (%)', 'FCR (%)', 'DataUsage (GB)', 'EngagementRate (%)',
    'ServiceActivations', 'ComplaintResolutionTime (hrs)', 'CustomerRetentionRate (%)',
    'MarketPenetration (%)', 'ARPA ($)', 'CustomerReferralRate (%)'
]

# Convert columns to numeric, handle errors by coercing to NaN
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

# Set the layout for wide display
st.set_page_config(layout="wide")

# Custom HTML for the title
title_html = """
    <div style="background-color:#f0f0f0;padding:10px;border-radius:25px;text-align:;left">
    <h1 style="color:#0073e6;font-family:Arial;">Telecommunications Data Dashboard</h1>
    </div>
"""
st.markdown(title_html, unsafe_allow_html=True)


# Load your logo image
logo_path = "Color logo - no background.png"

# Open the image and convert it to a base64 string
with open(logo_path, "rb") as img_file:
    encoded_string = base64.b64encode(img_file.read()).decode()

# HTML code to position the image at the top right
logo_html = f"""
    <div style="position: fixed; top: 60px; right:10px;">
        <img src="data:image/png;base64,{encoded_string}" width="100">
    </div>
"""

# Render the HTML
st.markdown(logo_html, unsafe_allow_html=True)

# Key metrics calculations
total_revenue = df['ARPU ($)'].sum()
total_clv = df['CLV ($)'].sum()
total_cac = df['CAC ($)'].sum()
total_customers = df['CustomerID'].nunique()

# Assume operational costs for net profit calculation
operational_costs = total_revenue * 0.1
net_profit = total_revenue - total_cac - operational_costs

# Create HTML for styled metric boxes
def styled_metric_box(title, value, background_color="#f0f0f0"):
    return f"""
    <div style="
        background-color: {background_color}; 
        padding: 10px; 
        border-radius: 10px; 
        text-align: center;
        margin: 1em 0;
    ">
        <h3 style="margin: 0; font-size: 1.2em;">{title}</h3>
        <p style="margin: 0; font-size: 1.5em; font-weight: bold;">{value}</p>
    </div>
    """

# Format numbers to remove decimals (use commas for thousands separator)
total_revenue_formatted = f"{int(total_revenue):,}"
total_clv_formatted = f"{int(total_clv):,}"
total_cac_formatted = f"{int(total_cac):,}"
net_profit_formatted = f"{int(net_profit):,}"

# Layout for displaying metrics in separate boxes
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(styled_metric_box("Total Revenue", f"${total_revenue_formatted}"), unsafe_allow_html=True)

with col2:
    st.markdown(styled_metric_box("Total CLV", f"${total_clv_formatted}"), unsafe_allow_html=True)

with col3:
    st.markdown(styled_metric_box("Total CAC", f"${total_cac_formatted}"), unsafe_allow_html=True)

with col4:
    st.markdown(styled_metric_box("Net Profit", f"${net_profit_formatted}"), unsafe_allow_html=True)

with col5:
    st.markdown(styled_metric_box("Total Customers", total_customers), unsafe_allow_html=True)

# Filters
categories = st.multiselect("Select Categories", options=df['Category'].unique(), default=df['Category'].unique())
segments = st.multiselect("Select Segments", options=df['Segment'].unique(), default=df['Segment'].unique())

# Apply filters
filtered_df = df[(df['Category'].isin(categories)) & (df['Segment'].isin(segments))]

# Ensure dates are properly formatted and aggregate data by month and category
filtered_df['Month'] = filtered_df['Date'].dt.to_period('M').dt.to_timestamp()
monthly_df = filtered_df.groupby(['Month', 'Category'])[numeric_cols].mean().reset_index()

# Define a purple color scale
purple_colors = ['#A05195', '#D45087', '#665191', '#F95D6A', '#B39CD0']

# Layout for charts
col6, col7, col8 = st.columns(3)

with col6:
    # ARPU over time
    arpu_chart = px.line(monthly_df, x='Month', y='ARPU ($)', color='Category', title='ARPU Over Time', color_discrete_sequence=purple_colors)
    arpu_avg = monthly_df['ARPU ($)'].mean()
    arpu_chart.add_hline(y=arpu_avg, line_dash="dot", annotation_text="Average", annotation_position="bottom right")
    st.plotly_chart(arpu_chart, use_container_width=True)

with col7:
    # CLV over time with a stacked area chart
    clv_chart = px.area(
        monthly_df,
        x='Month',
        y='CLV ($)',
        color='Category',
        title='CLV Over Time',
        color_discrete_sequence=purple_colors,
        line_group='Category',  # Ensure smooth transitions between segments
        markers=True  # Optionally add markers for data points
    )
    
    # Add average line for reference
    clv_avg = monthly_df['CLV ($)'].mean()
    clv_chart.add_hline(y=clv_avg, line_dash="dot", annotation_text="Average", annotation_position="bottom right")

    # Customize the layout for better appearance
    clv_chart.update_layout(
        xaxis_title='Month',
        yaxis_title='CLV ($)',
        showlegend=True
    )

    st.plotly_chart(clv_chart, use_container_width=True)
    
with col8:
    # Churn Rate over time
    churn_chart = px.line(monthly_df, x='Month', y='ChurnRate (%)', color='Category', title='Churn Rate Over Time', color_discrete_sequence=purple_colors)
    churn_avg = monthly_df['ChurnRate (%)'].mean()
    churn_chart.add_hline(y=churn_avg, line_dash="dot", annotation_text="Average", annotation_position="bottom right")
    st.plotly_chart(churn_chart, use_container_width=True)

# Second row of charts
col9, col10, col11 = st.columns(3)

with col9:
    # NPS score over time (converted to column chart)
    nps_chart = px.bar(monthly_df, x='Month', y='NPS', color='Category', title='NPS Score Over Time', color_discrete_sequence=purple_colors)
    st.plotly_chart(nps_chart, use_container_width=True)

with col10:
    # Prepare a stacked area chart for customer retention over time
    retention_rate_chart = px.area(
        monthly_df,
        x='Month',
        y='CustomerRetentionRate (%)',
        color='Category',
        title='Customer Retention Rate Over Time',
        line_group='Category',
        markers=False,
        color_discrete_sequence=px.colors.sequential.Inferno
    )
    
    # Adding an average line can still be done if needed
    retention_avg = monthly_df['CustomerRetentionRate (%)'].mean()
    retention_rate_chart.add_hline(
        y=retention_avg,
        line_dash="dot",
        annotation_text="Average",
        annotation_position="bottom right"
    )

    # Customize the layout for a more aesthetic appearance
    retention_rate_chart.update_layout(
        xaxis_title='Month',
        yaxis_title='Retention Rate (%)',
        showlegend=True,
        margin=dict(l=20, r=20, t=30, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x'
    )
    
    # Render the chart in Streamlit
    st.plotly_chart(retention_rate_chart, use_container_width=True)

with col11:
    # ARPA over time
    arpa_chart = px.line(monthly_df, x='Month', y='ARPA ($)', color='Category', title='ARPA Over Time', color_discrete_sequence=purple_colors)
    arpa_avg = monthly_df['ARPA ($)'].mean()
    arpa_chart.add_hline(y=arpa_avg, line_dash="dot", annotation_text="Average", annotation_position="bottom right")
    st.plotly_chart(arpa_chart, use_container_width=True)

# Aggregate average NPS and Retention Rate by Segment for the bubble chart
segment_agg = filtered_df.groupby('Segment').agg({
    'NPS': 'mean',
    'CustomerRetentionRate (%)': 'mean',
    'ARPU ($)': 'sum'  # Assuming ARPU as the size of the bubble
}).reset_index()

# Place bubble chart and category customer count chart side by side
col12, col13 = st.columns(2)

with col12:
    # Bubble chart for retention rate vs NPS
    bubble_chart = px.scatter(segment_agg, x='NPS', y='CustomerRetentionRate (%)', size='ARPU ($)', color='Segment', 
                              title='Retention Rate vs NPS', color_discrete_sequence=purple_colors, hover_name='Segment')
    st.plotly_chart(bubble_chart, use_container_width=True)

with col13:
    # Total customers by category
    customers_count_by_category = filtered_df['Category'].value_counts().reset_index()
    customers_count_by_category.columns = ['Category', 'Count']  # Rename columns for clarity
    customers_by_category_chart = px.bar(customers_count_by_category, x='Category', y='Count', title='Total Customers by Category')
    st.plotly_chart(customers_by_category_chart, use_container_width=True)
