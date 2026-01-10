import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import calendar
from plotly.subplots import make_subplots
import random

# Page configuration
st.set_page_config(
    page_title="Spotify Active Users Dashboard",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling with Spotify theme
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1DB954;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1DB954;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .metric-card {
        background-color: #191414;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 1rem;
        color: white;
        border-left: 5px solid #1DB954;
    }
    .stProgress > div > div > div > div {
        background-color: #1DB954;
    }
    .spotify-green {
        color: #1DB954;
    }
    .user-tier {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .free-tier {
        background-color: #535353;
        color: white;
    }
    .premium-tier {
        background-color: #1DB954;
        color: black;
    }
    .student-tier {
        background-color: #FFD700;
        color: black;
    }
    .family-tier {
        background-color: #9146FF;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<h1 class="main-header">🎵 Spotify Active Users Dashboard</h1>', unsafe_allow_html=True)
st.markdown("""
This dashboard provides insights into Spotify's daily active users worldwide. 
The data shown is simulated for demonstration purposes, with patterns based on typical streaming service usage trends.
""")

# Sidebar for controls
with st.sidebar:
    st.markdown("<h2 style='color: #1DB954;'>🎵 Spotify</h2>", unsafe_allow_html=True)
    st.markdown("## Dashboard Controls")
    
    # Date range selector
    st.markdown("### 📅 Date Range")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)  # 6 months default
    
    date_range = st.date_input(
        "Select date range:",
        value=(start_date, end_date),
        min_value=end_date - timedelta(days=365),
        max_value=end_date
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = date_range[0], date_range[0] + timedelta(days=30)
    
    # Data granularity
    st.markdown("### 📊 Data Granularity")
    granularity = st.radio(
        "Select time period:",
        ["Daily", "Weekly", "Monthly"],
        index=1
    )
    
    # Region filter
    st.markdown("### 🌍 Regions")
    regions = ["Global", "North America", "Europe", "Asia", "Latin America", "Oceania"]
    selected_regions = st.multiselect(
        "Select regions to display:",
        regions,
        default=["Global", "North America", "Europe"]
    )
    
    # User tier filter
    st.markdown("### 👥 User Tiers")
    user_tiers = ["All", "Free", "Premium", "Student", "Family"]
    selected_tiers = st.multiselect(
        "Select user tiers:",
        user_tiers,
        default=["All"]
    )
    
    # Device type filter
    st.markdown("### 📱 Device Types")
    device_types = ["All", "Mobile", "Desktop", "Web", "Smart Speaker", "Car"]
    selected_devices = st.multiselect(
        "Select device types:",
        device_types,
        default=["All"]
    )
    
    st.markdown("---")
    st.markdown("### 📈 Metrics Display")
    show_active_users = st.checkbox("Active Users", value=True)
    show_streams = st.checkbox("Total Streams", value=True)
    show_listening_time = st.checkbox("Listening Time", value=False)
    show_revenue = st.checkbox("Revenue", value=False)
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info("""
    This dashboard simulates Spotify user activity data for demonstration purposes.
    
    **Note:** Actual Spotify user statistics are proprietary and not publicly available in real-time.
    """)

# Function to generate simulated Spotify data
@st.cache_data
def generate_spotify_data(start_date, end_date, regions, user_tiers, device_types):
    """Generate simulated Spotify user activity data"""
    
    # Create date range
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = []
    
    # Base values for different regions (in millions)
    region_params = {
        "Global": {"base_users": 550, "base_streams": 2000, "growth_rate": 0.0005},
        "North America": {"base_users": 120, "base_streams": 450, "growth_rate": 0.0003},
        "Europe": {"base_users": 150, "base_streams": 550, "growth_rate": 0.0004},
        "Asia": {"base_users": 180, "base_streams": 650, "growth_rate": 0.0008},
        "Latin America": {"base_users": 80, "base_streams": 300, "growth_rate": 0.0010},
        "Oceania": {"base_users": 20, "base_streams": 75, "growth_rate": 0.0002}
    }
    
    # User tier distribution and ARPU (Average Revenue Per User)
    tier_params = {
        "Free": {"share": 0.45, "arpu": 0},
        "Premium": {"share": 0.35, "arpu": 9.99},
        "Student": {"share": 0.10, "arpu": 4.99},
        "Family": {"share": 0.10, "arpu": 15.99}
    }
    
    # Device type distribution
    device_params = {
        "Mobile": {"share": 0.65, "streams_per_user": 3.8},
        "Desktop": {"share": 0.20, "streams_per_user": 2.5},
        "Web": {"share": 0.08, "streams_per_user": 2.0},
        "Smart Speaker": {"share": 0.05, "streams_per_user": 4.5},
        "Car": {"share": 0.02, "streams_per_user": 3.0}
    }
    
    for region in regions:
        if region not in region_params:
            continue
            
        params = region_params[region]
        base_users = params["base_users"] * 1e6  # Convert to actual number
        base_streams = params["base_streams"] * 1e6
        growth_rate = params["growth_rate"]
        
        # Generate time series with trend, seasonality, and randomness
        days = len(date_range)
        
        # Linear growth trend
        trend_component = np.linspace(0, growth_rate * days, days)
        
        # Weekly seasonality (more streaming on weekends)
        day_of_week = np.array([d.weekday() for d in date_range])
        # Higher activity on Fridays, Saturdays
        weekday_factor = np.where(day_of_week == 4, 1.25, 
                                 np.where(day_of_week == 5, 1.30,
                                         np.where(day_of_week == 6, 1.20, 1.0)))
        
        # Monthly seasonality (beginning and end of month effects)
        day_of_month = np.array([d.day for d in date_range])
        month_seasonality = 1 + 0.08 * np.sin(2 * np.pi * day_of_month / 30)
        
        # Holiday effects (simplified)
        months = np.array([d.month for d in date_range])
        holiday_boost = np.where(months == 12, 1.15,  # December holidays
                                np.where(months == 6, 1.05,  # Summer
                                        np.where(months == 1, 0.95, 1.0)))  # Post-holiday slump
        
        # Random noise
        noise = np.random.normal(0, 0.02, days)
        
        # Active users calculation
        users = base_users * (1 + trend_component) * weekday_factor * month_seasonality * holiday_boost * (1 + noise)
        users = np.maximum(users, base_users * 0.9)  # Ensure minimum
        
        # Calculate daily streams (more variable than users)
        streams_noise = np.random.normal(0, 0.05, days)
        daily_streams_per_user = 3.5 * weekday_factor * (1 + streams_noise)
        total_streams = users * daily_streams_per_user
        
        # Calculate listening time (minutes per user per day)
        listening_time_base = 120  # 2 hours average
        listening_time = listening_time_base * weekday_factor * (1 + np.random.normal(0, 0.03, days))
        
        # Calculate daily revenue
        premium_share = 0.35 if region in ["North America", "Europe"] else 0.25
        student_share = 0.15 if region in ["North America", "Europe"] else 0.05
        family_share = 0.10
        
        daily_revenue = (
            users * premium_share * 9.99 / 30 +  # Monthly to daily
            users * student_share * 4.99 / 30 +
            users * family_share * 15.99 / 30
        )
        
        # Generate data for each date
        for i, date in enumerate(date_range):
            # Base entry for region totals
            data.append({
                "Date": date,
                "Region": region,
                "User_Tier": "All",
                "Device_Type": "All",
                "Active_Users": int(users[i]),
                "Total_Streams": int(total_streams[i]),
                "Avg_Listening_Time": listening_time[i],
                "Daily_Revenue": daily_revenue[i],
                "Streams_per_User": daily_streams_per_user[i]
            })
            
            # Add user tier breakdown for a subset of dates (to keep data manageable)
            if i % 7 == 0:  # Weekly breakdown
                for tier, tier_info in tier_params.items():
                    tier_users = int(users[i] * tier_info["share"])
                    if tier_users > 0:
                        data.append({
                            "Date": date,
                            "Region": region,
                            "User_Tier": tier,
                            "Device_Type": "All",
                            "Active_Users": tier_users,
                            "Total_Streams": int(tier_users * daily_streams_per_user[i]),
                            "Avg_Listening_Time": listening_time[i] * (1.1 if tier != "Free" else 0.9),
                            "Daily_Revenue": tier_users * tier_info["arpu"] / 30 if tier_info["arpu"] > 0 else 0,
                            "Streams_per_User": daily_streams_per_user[i] * (1.1 if tier != "Free" else 0.9)
                        })
                
                # Add device type breakdown
                for device, device_info in device_params.items():
                    device_users = int(users[i] * device_info["share"])
                    if device_users > 0:
                        data.append({
                            "Date": date,
                            "Region": region,
                            "User_Tier": "All",
                            "Device_Type": device,
                            "Active_Users": device_users,
                            "Total_Streams": int(device_users * device_info["streams_per_user"]),
                            "Avg_Listening_Time": listening_time[i] * (1.2 if device == "Smart Speaker" else 1.0),
                            "Daily_Revenue": daily_revenue[i] * device_info["share"],
                            "Streams_per_User": device_info["streams_per_user"]
                        })
    
    df = pd.DataFrame(data)
    
    # Add derived columns
    df["Day_of_Week"] = df["Date"].dt.day_name()
    df["Month"] = df["Date"].dt.month_name()
    df["Year"] = df["Date"].dt.year
    df["Quarter"] = df["Date"].dt.quarter
    df["Weekend"] = df["Day_of_Week"].isin(["Saturday", "Sunday"])
    
    return df

# Generate data based on user selections
if selected_regions:
    # Adjust selected tiers
    if "All" in selected_tiers:
        display_tiers = ["All", "Free", "Premium", "Student", "Family"]
    else:
        display_tiers = selected_tiers
    
    # Adjust selected devices
    if "All" in selected_devices:
        display_devices = ["All", "Mobile", "Desktop", "Web", "Smart Speaker", "Car"]
    else:
        display_devices = selected_devices
    
    with st.spinner("Generating Spotify data..."):
        df = generate_spotify_data(start_date, end_date, selected_regions, display_tiers, display_devices)
    
    # Filter data based on user selections
    filtered_df = df[
        (df["User_Tier"].isin(display_tiers)) & 
        (df["Device_Type"].isin(display_devices))
    ].copy()
    
    # Apply granularity
    if granularity == "Weekly":
        filtered_df["Week"] = filtered_df["Date"].dt.isocalendar().week
        filtered_df["Year_Week"] = filtered_df["Year"].astype(str) + "-W" + filtered_df["Week"].astype(str).str.zfill(2)
        group_cols = ["Year_Week", "Region", "User_Tier", "Device_Type"]
        x_axis_col = "Year_Week"
    elif granularity == "Monthly":
        filtered_df["Month_Year"] = filtered_df["Month"] + " " + filtered_df["Year"].astype(str)
        group_cols = ["Month_Year", "Region", "User_Tier", "Device_Type"]
        x_axis_col = "Month_Year"
    else:  # Daily
        group_cols = ["Date", "Region", "User_Tier", "Device_Type"]
        x_axis_col = "Date"
    
    # Aggregate data based on granularity
    df_grouped = filtered_df.groupby(group_cols).agg({
        "Active_Users": "mean",
        "Total_Streams": "mean",
        "Avg_Listening_Time": "mean",
        "Daily_Revenue": "mean",
        "Streams_per_User": "mean"
    }).reset_index()
    
    # Display key metrics
    st.markdown('<h2 class="sub-header">📊 Key Spotify Metrics</h2>', unsafe_allow_html=True)
    
    # Calculate metrics for the most recent date
    latest_date = df["Date"].max()
    latest_data = df[
        (df["Date"] == latest_date) & 
        (df["User_Tier"] == "All") & 
        (df["Device_Type"] == "All")
    ]
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_users = latest_data["Active_Users"].sum() / 1e6  # Convert to millions
        st.markdown(f"""
        <div class="metric-card">
            <h3>🎵 Total Active Users</h3>
            <h2>{total_users:,.0f}M</h2>
            <p>As of {latest_date.strftime('%b %d, %Y')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_streams = latest_data["Total_Streams"].sum() / 1e6  # Convert to millions
        st.markdown(f"""
        <div class="metric-card">
            <h3>▶️ Daily Streams</h3>
            <h2>{total_streams:,.0f}M</h2>
            <p>{latest_data["Streams_per_User"].mean():.1f} per user</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_listening = latest_data["Avg_Listening_Time"].mean()
        hours = int(avg_listening // 60)
        minutes = int(avg_listening % 60)
        st.markdown(f"""
        <div class="metric-card">
            <h3>⏱️ Avg. Listening Time</h3>
            <h2>{hours}h {minutes}m</h2>
            <p>Per user per day</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        daily_rev = latest_data["Daily_Revenue"].sum() / 1e6  # Convert to millions
        monthly_rev = daily_rev * 30
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 Estimated Daily Revenue</h3>
            <h2>${daily_rev:.1f}M</h2>
            <p>~${monthly_rev:.0f}M monthly</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Time series visualization - Active Users
    if show_active_users:
        st.markdown('<h2 class="sub-header">📈 Active Users Over Time</h2>', unsafe_allow_html=True)
        
        # Prepare data for chart (aggregate by region)
        chart_data = df_grouped[df_grouped["User_Tier"] == "All"]
        chart_data = chart_data[chart_data["Device_Type"] == "All"]
        
        fig = px.line(
            chart_data, 
            x=x_axis_col, 
            y="Active_Users",
            color="Region",
            title=f"Spotify Active Users by Region ({granularity} View)",
            labels={"Active_Users": "Active Users", x_axis_col: "Date"},
            height=500,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        
        # Format y-axis
        fig.update_layout(
            yaxis=dict(
                tickformat=".2s",
                title="Active Users"
            ),
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor='rgba(0,0,0,0.05)'
        )
        
        # Add range slider for daily view
        if granularity == "Daily":
            fig.update_xaxes(rangeslider_visible=True)
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Total Streams visualization
    if show_streams:
        st.markdown('<h2 class="sub-header">🎧 Total Streams Over Time</h2>', unsafe_allow_html=True)
        
        # Prepare data for chart
        chart_data = df_grouped[df_grouped["User_Tier"] == "All"]
        chart_data = chart_data[chart_data["Device_Type"] == "All"]
        
        fig = px.area(
            chart_data, 
            x=x_axis_col, 
            y="Total_Streams",
            color="Region",
            title=f"Daily Streams by Region ({granularity} View)",
            labels={"Total_Streams": "Total Streams", x_axis_col: "Date"},
            height=500,
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        
        # Format y-axis
        fig.update_layout(
            yaxis=dict(
                tickformat=".2s",
                title="Total Streams"
            ),
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # User Tier Analysis
    st.markdown('<h2 class="sub-header">👥 User Tier Analysis</h2>', unsafe_allow_html=True)
    
    # Get tier data
    tier_data = df[
        (df["User_Tier"] != "All") & 
        (df["Device_Type"] == "All") &
        (df["Region"] == "Global")
    ].copy()
    
    if not tier_data.empty:
        # Aggregate tier data
        tier_summary = tier_data.groupby(["User_Tier", "Date"]).agg({
            "Active_Users": "sum",
            "Total_Streams": "sum",
            "Daily_Revenue": "sum"
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Latest tier distribution
            latest_tier = tier_summary[tier_summary["Date"] == tier_summary["Date"].max()]
            fig = px.pie(
                latest_tier,
                values="Active_Users",
                names="User_Tier",
                title="User Distribution by Tier (Latest)",
                hole=0.4,
                color="User_Tier",
                color_discrete_map={
                    "Free": "#535353",
                    "Premium": "#1DB954",
                    "Student": "#FFD700",
                    "Family": "#9146FF"
                }
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Tier revenue contribution
            tier_revenue = latest_tier.copy()
            tier_revenue["Revenue_Share"] = tier_revenue["Daily_Revenue"] / tier_revenue["Daily_Revenue"].sum() * 100
            
            fig = px.bar(
                tier_revenue,
                x="User_Tier",
                y="Daily_Revenue",
                title="Daily Revenue by Tier",
                labels={"Daily_Revenue": "Daily Revenue ($)", "User_Tier": "User Tier"},
                color="User_Tier",
                color_discrete_map={
                    "Free": "#535353",
                    "Premium": "#1DB954",
                    "Student": "#FFD700",
                    "Family": "#9146FF"
                }
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Listening Time visualization
    if show_listening_time:
        st.markdown('<h2 class="sub-header">⏱️ Listening Time Analysis</h2>', unsafe_allow_html=True)
        
        # Prepare data
        listening_data = df_grouped[df_grouped["User_Tier"] == "All"]
        listening_data = listening_data[listening_data["Device_Type"] == "All"]
        
        fig = px.line(
            listening_data, 
            x=x_axis_col, 
            y="Avg_Listening_Time",
            color="Region",
            title=f"Average Listening Time by Region ({granularity} View)",
            labels={"Avg_Listening_Time": "Listening Time (Minutes)", x_axis_col: "Date"},
            height=400,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        fig.update_layout(
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Device Type Analysis
    st.markdown('<h2 class="sub-header">📱 Device Type Analysis</h2>', unsafe_allow_html=True)
    
    # Get device data
    device_data = df[
        (df["Device_Type"] != "All") & 
        (df["User_Tier"] == "All") &
        (df["Region"] == "Global")
    ].copy()
    
    if not device_data.empty:
        # Aggregate device data
        device_summary = device_data.groupby(["Device_Type", "Date"]).agg({
            "Active_Users": "sum",
            "Streams_per_User": "mean"
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Device distribution
            latest_device = device_summary[device_summary["Date"] == device_summary["Date"].max()]
            fig = px.bar(
                latest_device,
                x="Device_Type",
                y="Active_Users",
                title="Active Users by Device Type",
                labels={"Active_Users": "Active Users", "Device_Type": "Device Type"},
                color="Device_Type",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Streams per user by device
            fig = px.bar(
                latest_device,
                x="Device_Type",
                y="Streams_per_User",
                title="Streams per User by Device Type",
                labels={"Streams_per_User": "Streams per User", "Device_Type": "Device Type"},
                color="Device_Type",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(xaxis_tickangle=-45, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Weekly Patterns
    st.markdown('<h2 class="sub-header">📅 Weekly Listening Patterns</h2>', unsafe_allow_html=True)
    
    # Calculate average by day of week
    weekly_pattern = df[
        (df["User_Tier"] == "All") & 
        (df["Device_Type"] == "All") &
        (df["Region"] == "Global")
    ].copy()
    
    if not weekly_pattern.empty:
        weekly_avg = weekly_pattern.groupby("Day_of_Week").agg({
            "Active_Users": "mean",
            "Total_Streams": "mean",
            "Avg_Listening_Time": "mean"
        }).reset_index()
        
        # Order days of week
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekly_avg["Day_of_Week"] = pd.Categorical(weekly_avg["Day_of_Week"], categories=days_order, ordered=True)
        weekly_avg = weekly_avg.sort_values("Day_of_Week")
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Active Users by Day of Week", "Listening Time by Day of Week"),
            vertical_spacing=0.15
        )
        
        # Active users chart
        fig.add_trace(
            go.Bar(
                x=weekly_avg["Day_of_Week"],
                y=weekly_avg["Active_Users"],
                name="Active Users",
                marker_color="#1DB954"
            ),
            row=1, col=1
        )
        
        # Listening time chart
        fig.add_trace(
            go.Scatter(
                x=weekly_avg["Day_of_Week"],
                y=weekly_avg["Avg_Listening_Time"],
                name="Listening Time",
                mode="lines+markers",
                line=dict(color="#9146FF", width=3),
                marker=dict(size=8)
            ),
            row=2, col=1
        )
        
        fig.update_layout(height=600, showlegend=False)
        fig.update_yaxes(title_text="Active Users", row=1, col=1)
        fig.update_yaxes(title_text="Minutes", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Regional Comparison
    st.markdown('<h2 class="sub-header">🌍 Regional Comparison</h2>', unsafe_allow_html=True)
    
    # Regional statistics
    regional_stats = df[
        (df["User_Tier"] == "All") & 
        (df["Device_Type"] == "All")
    ].groupby("Region").agg({
        "Active_Users": "mean",
        "Streams_per_User": "mean",
        "Avg_Listening_Time": "mean"
    }).reset_index()
    
    # Sort by active users
    regional_stats = regional_stats.sort_values("Active_Users", ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            regional_stats,
            x="Region",
            y="Active_Users",
            title="Average Active Users by Region",
            labels={"Active_Users": "Avg. Active Users", "Region": "Region"},
            color="Active_Users",
            color_continuous_scale="greens"
        )
        
        # Format y-axis
        fig.update_layout(
            yaxis=dict(tickformat=".2s"),
            coloraxis_showscale=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(
            regional_stats,
            x="Streams_per_User",
            y="Avg_Listening_Time",
            size="Active_Users",
            color="Region",
            title="Streams vs Listening Time by Region",
            labels={
                "Streams_per_User": "Streams per User",
                "Avg_Listening_Time": "Avg. Listening Time (min)",
                "Region": "Region"
            },
            hover_name="Region",
            size_max=60
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.markdown('<h2 class="sub-header">📋 Detailed Data</h2>', unsafe_allow_html=True)
    
    # Let user select which columns to display
    columns_to_show = st.multiselect(
        "Select columns to display:",
        ["Date", "Region", "User_Tier", "Device_Type", "Active_Users", "Total_Streams", 
         "Avg_Listening_Time", "Daily_Revenue", "Streams_per_User", "Day_of_Week"],
        default=["Date", "Region", "Active_Users", "Total_Streams", "Streams_per_User"]
    )
    
    if columns_to_show:
        display_df = df[columns_to_show].copy()
        
        # Format large numbers
        if "Active_Users" in display_df.columns:
            display_df["Active_Users"] = display_df["Active_Users"].apply(
                lambda x: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}K"
            )
        
        if "Total_Streams" in display_df.columns:
            display_df["Total_Streams"] = display_df["Total_Streams"].apply(
                lambda x: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}K"
            )
        
        if "Daily_Revenue" in display_df.columns:
            display_df["Daily_Revenue"] = display_df["Daily_Revenue"].apply(
                lambda x: f"${x/1e6:.2f}M" if x >= 1e6 else f"${x/1e3:.0f}K"
            )
        
        st.dataframe(
            display_df.sort_values("Date", ascending=False).head(100),
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Dataset as CSV",
            data=csv,
            file_name=f"spotify_activity_{start_date}_{end_date}.csv",
            mime="text/csv"
        )
    
    # Insights section
    st.markdown('<h2 class="sub-header">💡 Insights & Analysis</h2>', unsafe_allow_html=True)
    
    # Calculate some insights
    if not df.empty:
        # Overall growth
        earliest_date = df["Date"].min()
        latest_global = df[
            (df["Date"] == latest_date) & 
            (df["Region"] == "Global") & 
            (df["User_Tier"] == "All") & 
            (df["Device_Type"] == "All")
        ]["Active_Users"].sum()
        
        earliest_global = df[
            (df["Date"] == earliest_date) & 
            (df["Region"] == "Global") & 
            (df["User_Tier"] == "All") & 
            (df["Device_Type"] == "All")
        ]["Active_Users"].sum()
        
        total_growth = ((latest_global - earliest_global) / earliest_global * 100) if earliest_global > 0 else 0
        
        # Find region with highest streams per user
        region_streams = regional_stats.copy()
        highest_streams_region = region_streams.loc[region_streams["Streams_per_User"].idxmax(), "Region"]
        highest_streams_value = region_streams["Streams_per_User"].max()
        
        # Find most popular device
        if not device_data.empty:
            latest_device_stats = device_data[device_data["Date"] == device_data["Date"].max()]
            popular_device = latest_device_stats.loc[latest_device_stats["Active_Users"].idxmax(), "Device_Type"]
        
        # Generate insights
        insights = [
            f"📈 **Overall growth:** {total_growth:.1f}% increase from {earliest_date.strftime('%b %d, %Y')} to {latest_date.strftime('%b %d, %Y')}",
            f"🎧 **Most engaged region:** {highest_streams_region} with {highest_streams_value:.1f} streams per user daily",
            f"📱 **Most popular device:** {popular_device if 'popular_device' in locals() else 'Mobile'} accounts for the majority of streaming",
            f"💰 **Revenue drivers:** Premium users generate {tier_revenue['Daily_Revenue'].sum()/1e6:.1f}M daily despite being only {len(tier_revenue[tier_revenue['User_Tier'] == 'Premium'])/len(tier_revenue)*100:.0f}% of users",
            f"📅 **Peak listening:** Highest activity occurs on {weekly_avg.loc[weekly_avg['Active_Users'].idxmax(), 'Day_of_Week'] if 'weekly_avg' in locals() else 'weekends'}"
        ]
        
        for insight in insights:
            st.info(insight)
    
else:
    st.warning("Please select at least one region from the sidebar to display data.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>🎵 Spotify Active Users Dashboard | Simulated Data for Demonstration Purposes</p>
    <p>Note: This dashboard uses simulated data. Actual Spotify user statistics are proprietary.</p>
    <p style="color: #1DB954; font-weight: bold;">Music for everyone. Data for insights.</p>
</div>
""", unsafe_allow_html=True)