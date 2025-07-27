import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(
    page_title="📊 Superstore BI Dashboard",
    page_icon="📦",
    layout="wide"
)

# Load Dataset
@st.cache_data
def load_data():
    df = pd.read_csv("C:\\Users\\PMLS\\Downloads\\archive (15)\\Global_Superstore2.csv", encoding='latin1', parse_dates=['Order Date', 'Ship Date'])
    return df

df = load_data()

# Sidebar Filters
st.sidebar.title("🔎 Filter Your View")
region = st.sidebar.multiselect("🌍 Region", df['Region'].dropna().unique(), default=df['Region'].dropna().unique())
segment = st.sidebar.multiselect("👥 Segment", df['Segment'].dropna().unique(), default=df['Segment'].dropna().unique())
category = st.sidebar.multiselect("📚 Category", df['Category'].dropna().unique(), default=df['Category'].dropna().unique())
date_range = st.sidebar.date_input("📆 Order Date Range", [df['Order Date'].min(), df['Order Date'].max()])

# Filtered Data
filtered_df = df[
    (df['Region'].isin(region)) &
    (df['Segment'].isin(segment)) &
    (df['Category'].isin(category)) &
    (df['Order Date'] >= pd.to_datetime(date_range[0])) &
    (df['Order Date'] <= pd.to_datetime(date_range[1]))
]

# Dashboard Title
st.title("📦 Superstore BI Dashboard")
page = st.sidebar.radio("📄 Page", ["General Overview", "Detailed Analysis"])

# ========== KPIs Section ==========
def draw_kpis():
    total_sales = filtered_df['Sales'].sum()
    total_profit = filtered_df['Profit'].sum()
    avg_shipping = filtered_df['Shipping Cost'].mean()
    total_orders = filtered_df['Order ID'].nunique()

    st.markdown("### 📊 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Total Sales", f"${total_sales:,.0f}")
    with col2:
        st.metric("📈 Total Profit", f"${total_profit:,.0f}")
    with col3:
        st.metric("🚚 Avg Shipping", f"${avg_shipping:.2f}")
    with col4:
        st.metric("🧾 Total Orders", total_orders)

# ========== General Overview ==========
if page == "General Overview":
    draw_kpis()
    st.markdown("---")

    # Sales by Region
    st.subheader("🌍 Sales by Region")
    region_sales = filtered_df.groupby("Region")["Sales"].sum().reset_index()
    fig = px.bar(region_sales, x="Region", y="Sales", color="Region", text_auto=".2s",
                 template="plotly_dark", title="Sales by Region")
    st.plotly_chart(fig, use_container_width=True)

    # Yearly Sales
    st.subheader("📆 Yearly Sales Trend")
    df_year = filtered_df.copy()
    df_year['Year'] = df_year['Order Date'].dt.year
    year_sales = df_year.groupby('Year')['Sales'].sum().reset_index()
    fig = px.line(year_sales, x="Year", y="Sales", markers=True, line_shape="linear",
                  title="Yearly Sales", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # Top States by Profit
    st.subheader("🏙️ Top 10 States by Profit")
    top_states = filtered_df.groupby("State")["Profit"].sum().sort_values(ascending=False).head(10).reset_index()
    fig = px.bar(top_states, x="Profit", y="State", orientation="h", color="Profit",
                 text_auto=".2s", title="Top 10 States by Profit", template="ggplot2")
    st.plotly_chart(fig, use_container_width=True)

# ========== Detailed Analysis ==========
elif page == "Detailed Analysis":
    st.header("📦 Detailed Insights")
    st.markdown("---")

    # Treemap - Sales by Category/Sub-category
    st.subheader("📚 Sales by Category and Sub-Category")
    cat_sales = filtered_df.groupby(['Category', 'Sub-Category'])['Sales'].sum().reset_index()
    fig = px.treemap(cat_sales, path=['Category', 'Sub-Category'], values='Sales',
                     color='Sales', color_continuous_scale='blues',
                     title="Sales Distribution by Category & Sub-Category")
    st.plotly_chart(fig, use_container_width=True)

    # Scatter - Discount vs Profit
    st.subheader("🔁 Discount vs Profit")
    fig = px.scatter(filtered_df, x="Discount", y="Profit", size="Sales", color="Category",
                     hover_data=["Sub-Category", "Region"], size_max=40,
                     title="Discount Impact on Profit", template="seaborn")
    st.plotly_chart(fig, use_container_width=True)

    # Pie Chart - Sales by Ship Mode
    st.subheader("🚚 Sales Distribution by Ship Mode")
    ship_sales = filtered_df.groupby("Ship Mode")["Sales"].sum().reset_index()
    fig = px.pie(ship_sales, names='Ship Mode', values='Sales', hole=0.4,
                 title="Sales by Shipping Method", color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig, use_container_width=True)

    # Heatmap - Profit by Region and Segment
    st.subheader("🔥 Profit Heatmap by Region and Segment")
    heat_data = filtered_df.groupby(['Region', 'Segment'])['Profit'].sum().reset_index()
    heat_pivot = heat_data.pivot(index="Region", columns="Segment", values="Profit").fillna(0)
    z = heat_pivot.values
    x = list(heat_pivot.columns)
    y = list(heat_pivot.index)
    z_text = [[f"${v:,.0f}" for v in row] for row in z]

    fig = go.Figure(data=go.Heatmap(
        z=z, x=x, y=y, text=z_text, texttemplate="%{text}",
        colorscale="RdYlGn", hoverongaps=False,
        hovertemplate="Region: %{y}<br>Segment: %{x}<br>Profit: %{z:$,.0f}<extra></extra>",
        colorbar=dict(title="Profit")
    ))
    fig.update_layout(
        title="💵 Annotated Profit Heatmap",
        xaxis_title="Segment",
        yaxis_title="Region",
        template="plotly_dark",
        font=dict(color="white", size=12),
        margin=dict(l=80, r=20, t=50, b=50)
    )
    st.plotly_chart(fig, use_container_width=True)
