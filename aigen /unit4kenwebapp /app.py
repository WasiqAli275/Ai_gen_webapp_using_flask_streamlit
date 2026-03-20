import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set up some basic configurations
plt.style.use('fivethirtyeight')
sns.set_palette('Set2')

# Page configuration
st.set_page_config(
    page_title="Superstore Data Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load the dataset
@st.cache_data
def load_data():
    # Try to load from a local file first
    try:
        df = pd.read_csv('Sample - Superstore.csv', encoding='ISO-8859-1')
    except:
        # If local file doesn't exist, try to download from a URL
        url = "https://raw.githubusercontent.com/vivek468/Superstore-Dataset/master/Sample%20-%20Superstore.csv"
        df = pd.read_csv(url, encoding='ISO-8859-1')
    
    # Convert date columns to datetime
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    
    # Extract additional date features
    df['Order Year'] = df['Order Date'].dt.year
    df['Order Month'] = df['Order Date'].dt.month
    df['Order Day'] = df['Order Date'].dt.day
    df['Order Day of Week'] = df['Order Date'].dt.dayofweek
    df['Ship Days'] = (df['Ship Date'] - df['Order Date']).dt.days
    
    return df

# Load the data
df = load_data()

# Define analysis functions
def show_basic_info():
    st.write("### Dataset Shape:", df.shape)
    st.write("### First 5 Rows:")
    st.dataframe(df.head())
    
    st.write("### Dataset Info:")
    buffer = pd.io.common.StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()
    st.text(info_str)
    
    st.write("### Missing Values:")
    st.dataframe(df.isnull().sum().to_frame().rename(columns={0: 'Missing Count'}))
    
    st.write("### Duplicate Rows:", df.duplicated().sum())

def show_descriptive_stats():
    st.write("### Descriptive Statistics for Numerical Columns:")
    st.dataframe(df.describe())
    
    st.write("### Descriptive Statistics for Categorical Columns:")
    st.dataframe(df.describe(include=['object']))
    
    st.write("### Unique Values in Categorical Columns:")
    cat_cols = df.select_dtypes(include=['object']).columns
    for col in cat_cols:
        st.write(f"{col}: {df[col].nunique()} unique values")

def show_correlation_analysis():
    # Select only numerical columns for correlation
    num_cols = df.select_dtypes(include=[np.number]).columns
    corr = df[num_cols].corr()
    
    # Create a heatmap
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5, ax=ax)
    ax.set_title('Correlation Matrix of Numerical Features')
    plt.tight_layout()
    st.pyplot(fig)
    
    # Show correlation with target variables (Sales, Profit)
    st.write("### Correlation with Sales:")
    st.dataframe(corr['Sales'].sort_values(ascending=False).to_frame())
    
    st.write("### Correlation with Profit:")
    st.dataframe(corr['Profit'].sort_values(ascending=False).to_frame())

def show_distribution_analysis():
    # Select numerical columns
    num_cols = df.select_dtypes(include=[np.number]).columns
    
    # Create subplots for distribution
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Distribution of Numerical Features', fontsize=16)
    
    # Plot distributions
    for i, col in enumerate(num_cols[:6]):  # Limit to first 6 numerical columns
        row = i // 3
        col_idx = i % 3
        sns.histplot(df[col], kde=True, ax=axes[row, col_idx])
        axes[row, col_idx].set_title(f'Distribution of {col}')
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    st.pyplot(fig)
    
    # Check for skewness
    st.write("### Skewness of Numerical Features:")
    skewness_data = []
    for col in num_cols:
        skewness_data.append({"Feature": col, "Skewness": f"{df[col].skew():.4f}"})
    st.dataframe(pd.DataFrame(skewness_data))

def show_category_analysis():
    # Analyze categorical variables
    cat_cols = ['Ship Mode', 'Segment', 'Category', 'Sub-Category', 'Region']
    
    # Create subplots
    fig, axes = plt.subplots(3, 2, figsize=(18, 18))
    fig.suptitle('Analysis of Categorical Features', fontsize=16)
    
    # Plot count plots
    for i, col in enumerate(cat_cols):
        row = i // 2
        col_idx = i % 2
        if row < 3 and col_idx < 2:
            sns.countplot(y=col, data=df, ax=axes[row, col_idx], order=df[col].value_counts().index)
            axes[row, col_idx].set_title(f'Count of {col}')
    
    # Hide empty subplot
    axes[2, 1].set_visible(False)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    st.pyplot(fig)
    
    # Show value counts
    for col in cat_cols:
        st.write(f"### Value Counts for {col}:")
        st.dataframe(df[col].value_counts().to_frame())

def show_sales_analysis():
    # Sales by Category
    fig, ax = plt.subplots(figsize=(12, 6))
    category_sales = df.groupby('Category')['Sales'].sum().sort_values(ascending=False)
    sns.barplot(x=category_sales.index, y=category_sales.values, ax=ax)
    ax.set_title('Total Sales by Category')
    ax.set_ylabel('Total Sales')
    ax.set_xlabel('Category')
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
    # Sales by Sub-Category
    fig, ax = plt.subplots(figsize=(14, 8))
    subcat_sales = df.groupby('Sub-Category')['Sales'].sum().sort_values(ascending=False)
    sns.barplot(x=subcat_sales.values, y=subcat_sales.index, ax=ax)
    ax.set_title('Total Sales by Sub-Category')
    ax.set_xlabel('Total Sales')
    ax.set_ylabel('Sub-Category')
    st.pyplot(fig)
    
    # Sales by Region
    fig, ax = plt.subplots(figsize=(10, 6))
    region_sales = df.groupby('Region')['Sales'].sum().sort_values(ascending=False)
    sns.barplot(x=region_sales.index, y=region_sales.values, ax=ax)
    ax.set_title('Total Sales by Region')
    ax.set_ylabel('Total Sales')
    ax.set_xlabel('Region')
    st.pyplot(fig)
    
    # Sales by Segment
    fig, ax = plt.subplots(figsize=(10, 6))
    segment_sales = df.groupby('Segment')['Sales'].sum().sort_values(ascending=False)
    sns.barplot(x=segment_sales.index, y=segment_sales.values, ax=ax)
    ax.set_title('Total Sales by Segment')
    ax.set_ylabel('Total Sales')
    ax.set_xlabel('Segment')
    st.pyplot(fig)

def show_profit_analysis():
    # Profit by Category
    fig, ax = plt.subplots(figsize=(12, 6))
    category_profit = df.groupby('Category')['Profit'].sum().sort_values(ascending=False)
    sns.barplot(x=category_profit.index, y=category_profit.values, ax=ax)
    ax.set_title('Total Profit by Category')
    ax.set_ylabel('Total Profit')
    ax.set_xlabel('Category')
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
    # Profit by Sub-Category
    fig, ax = plt.subplots(figsize=(14, 8))
    subcat_profit = df.groupby('Sub-Category')['Profit'].sum().sort_values(ascending=False)
    sns.barplot(x=subcat_profit.values, y=subcat_profit.index, ax=ax)
    ax.set_title('Total Profit by Sub-Category')
    ax.set_xlabel('Total Profit')
    ax.set_ylabel('Sub-Category')
    ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
    st.pyplot(fig)
    
    # Profit by Region
    fig, ax = plt.subplots(figsize=(10, 6))
    region_profit = df.groupby('Region')['Profit'].sum().sort_values(ascending=False)
    sns.barplot(x=region_profit.index, y=region_profit.values, ax=ax)
    ax.set_title('Total Profit by Region')
    ax.set_ylabel('Total Profit')
    ax.set_xlabel('Region')
    st.pyplot(fig)
    
    # Profit Margin by Category
    fig, ax = plt.subplots(figsize=(12, 6))
    df['Profit Margin'] = df['Profit'] / df['Sales'] * 100
    category_margin = df.groupby('Category')['Profit Margin'].mean().sort_values(ascending=False)
    sns.barplot(x=category_margin.index, y=category_margin.values, ax=ax)
    ax.set_title('Average Profit Margin by Category (%)')
    ax.set_ylabel('Average Profit Margin (%)')
    ax.set_xlabel('Category')
    plt.xticks(rotation=45)
    st.pyplot(fig)

def show_time_series_analysis():
    # Sales and Profit over time
    df_time = df.set_index('Order Date')
    monthly_sales = df_time['Sales'].resample('M').sum()
    monthly_profit = df_time['Profit'].resample('M').sum()
    
    fig, ax1 = plt.subplots(figsize=(14, 7))
    
    ax1.plot(monthly_sales.index, monthly_sales.values, color='blue', label='Sales')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Sales', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    
    ax2 = ax1.twinx()
    ax2.plot(monthly_profit.index, monthly_profit.values, color='red', label='Profit')
    ax2.set_ylabel('Profit', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    
    plt.title('Monthly Sales and Profit Over Time')
    plt.grid(True)
    st.pyplot(fig)
    
    # Sales by Year
    fig, ax = plt.subplots(figsize=(10, 6))
    yearly_sales = df.groupby('Order Year')['Sales'].sum()
    sns.barplot(x=yearly_sales.index, y=yearly_sales.values, ax=ax)
    ax.set_title('Total Sales by Year')
    ax.set_ylabel('Total Sales')
    ax.set_xlabel('Year')
    st.pyplot(fig)
    
    # Sales by Month
    fig, ax = plt.subplots(figsize=(12, 6))
    monthly_avg = df.groupby('Order Month')['Sales'].mean()
    sns.barplot(x=monthly_avg.index, y=monthly_avg.values, ax=ax)
    ax.set_title('Average Sales by Month')
    ax.set_ylabel('Average Sales')
    ax.set_xlabel('Month')
    st.pyplot(fig)

def show_customer_analysis():
    # Top customers by sales
    top_customers = df.groupby('Customer Name')['Sales'].sum().sort_values(ascending=False).head(10)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(x=top_customers.values, y=top_customers.index, ax=ax)
    ax.set_title('Top 10 Customers by Total Sales')
    ax.set_xlabel('Total Sales')
    ax.set_ylabel('Customer Name')
    st.pyplot(fig)
    
    # Customer segment analysis
    segment_customers = df.groupby('Segment')['Customer ID'].nunique()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=segment_customers.index, y=segment_customers.values, ax=ax)
    ax.set_title('Number of Customers by Segment')
    ax.set_ylabel('Number of Customers')
    ax.set_xlabel('Segment')
    st.pyplot(fig)
    
    # Customer frequency
    customer_freq = df['Customer ID'].value_counts()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(customer_freq, bins=20, kde=True, ax=ax)
    ax.set_title('Distribution of Purchase Frequency')
    ax.set_xlabel('Number of Purchases')
    ax.set_ylabel('Number of Customers')
    st.pyplot(fig)

def show_product_analysis():
    # Top products by sales
    top_products = df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False).head(10)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(x=top_products.values, y=top_products.index, ax=ax)
    ax.set_title('Top 10 Products by Total Sales')
    ax.set_xlabel('Total Sales')
    ax.set_ylabel('Product Name')
    st.pyplot(fig)
    
    # Most profitable products
    top_profit_products = df.groupby('Product Name')['Profit'].sum().sort_values(ascending=False).head(10)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(x=top_profit_products.values, y=top_profit_products.index, ax=ax)
    ax.set_title('Top 10 Products by Total Profit')
    ax.set_xlabel('Total Profit')
    ax.set_ylabel('Product Name')
    st.pyplot(fig)
    
    # Products with highest quantity sold
    top_quantity = df.groupby('Product Name')['Quantity'].sum().sort_values(ascending=False).head(10)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(x=top_quantity.values, y=top_quantity.index, ax=ax)
    ax.set_title('Top 10 Products by Quantity Sold')
    ax.set_xlabel('Total Quantity')
    ax.set_ylabel('Product Name')
    st.pyplot(fig)

def show_shipping_analysis():
    # Shipping mode distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.countplot(x='Ship Mode', data=df, order=df['Ship Mode'].value_counts().index, ax=ax)
    ax.set_title('Distribution of Shipping Modes')
    ax.set_ylabel('Count')
    ax.set_xlabel('Ship Mode')
    st.pyplot(fig)
    
    # Shipping days distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(df['Ship Days'], bins=20, kde=True, ax=ax)
    ax.set_title('Distribution of Shipping Days')
    ax.set_xlabel('Number of Days to Ship')
    ax.set_ylabel('Frequency')
    st.pyplot(fig)
    
    # Shipping days by ship mode
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(x='Ship Mode', y='Ship Days', data=df, ax=ax)
    ax.set_title('Shipping Days by Ship Mode')
    ax.set_ylabel('Number of Days to Ship')
    ax.set_xlabel('Ship Mode')
    st.pyplot(fig)

def show_discount_analysis():
    # Discount distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(df['Discount'], bins=20, kde=True, ax=ax)
    ax.set_title('Distribution of Discounts')
    ax.set_xlabel('Discount')
    ax.set_ylabel('Frequency')
    st.pyplot(fig)
    
    # Impact of discount on sales and profit
    discount_impact = df.groupby('Discount').agg({'Sales': 'sum', 'Profit': 'sum', 'Quantity': 'sum'}).reset_index()
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    ax1.bar(discount_impact['Discount'], discount_impact['Sales'], alpha=0.7, color='blue', label='Sales')
    ax1.set_xlabel('Discount')
    ax1.set_ylabel('Sales', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    
    ax2 = ax1.twinx()
    ax2.plot(discount_impact['Discount'], discount_impact['Profit'], color='red', marker='o', label='Profit')
    ax2.set_ylabel('Profit', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    
    plt.title('Impact of Discount on Sales and Profit')
    plt.grid(True)
    st.pyplot(fig)
    
    # Profit margin by discount level
    df['Profit Margin'] = df['Profit'] / df['Sales'] * 100
    discount_margin = df.groupby('Discount')['Profit Margin'].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(x='Discount', y='Profit Margin', data=discount_margin, marker='o', ax=ax)
    ax.set_title('Average Profit Margin by Discount Level')
    ax.set_xlabel('Discount')
    ax.set_ylabel('Average Profit Margin (%)')
    plt.grid(True)
    st.pyplot(fig)

def show_geographical_analysis():
    # Sales by State
    state_sales = df.groupby('State')['Sales'].sum().sort_values(ascending=False).head(15)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(x=state_sales.values, y=state_sales.index, ax=ax)
    ax.set_title('Top 15 States by Total Sales')
    ax.set_xlabel('Total Sales')
    ax.set_ylabel('State')
    st.pyplot(fig)
    
    # Profit by State
    state_profit = df.groupby('State')['Profit'].sum().sort_values(ascending=False).head(15)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(x=state_profit.values, y=state_profit.index, ax=ax)
    ax.set_title('Top 15 States by Total Profit')
    ax.set_xlabel('Total Profit')
    ax.set_ylabel('State')
    st.pyplot(fig)
    
    # Sales by City
    city_sales = df.groupby('City')['Sales'].sum().sort_values(ascending=False).head(15)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(x=city_sales.values, y=city_sales.index, ax=ax)
    ax.set_title('Top 15 Cities by Total Sales')
    ax.set_xlabel('Total Sales')
    ax.set_ylabel('City')
    st.pyplot(fig)

def show_inferential_stats():
    # Hypothesis testing: Is there a significant difference in profit between different segments?
    segments = df['Segment'].unique()
    segment_profits = [df[df['Segment'] == segment]['Profit'] for segment in segments]
    
    # ANOVA test
    f_stat, p_val = stats.f_oneway(*segment_profits)
    st.write("### ANOVA test for profit across segments:")
    st.write(f"F-statistic: {f_stat:.4f}")
    st.write(f"P-value: {p_val:.4f}")
    if p_val < 0.05:
        st.write("Result: There is a significant difference in profit between segments.")
    else:
        st.write("Result: There is no significant difference in profit between segments.")
    
    # T-test: Is there a significant difference in sales between the East and West regions?
    east_sales = df[df['Region'] == 'East']['Sales']
    west_sales = df[df['Region'] == 'West']['Sales']
    
    t_stat, p_val = stats.ttest_ind(east_sales, west_sales)
    st.write("### T-test for sales between East and West regions:")
    st.write(f"T-statistic: {t_stat:.4f}")
    st.write(f"P-value: {p_val:.4f}")
    if p_val < 0.05:
        st.write("Result: There is a significant difference in sales between East and West regions.")
    else:
        st.write("Result: There is no significant difference in sales between East and West regions.")
    
    # Chi-square test: Is there a significant association between Ship Mode and Segment?
    contingency_table = pd.crosstab(df['Ship Mode'], df['Segment'])
    chi2, p_val, dof, expected = stats.chi2_contingency(contingency_table)
    
    st.write("### Chi-square test for association between Ship Mode and Segment:")
    st.write(f"Chi-square statistic: {chi2:.4f}")
    st.write(f"P-value: {p_val:.4f}")
    if p_val < 0.05:
        st.write("Result: There is a significant association between Ship Mode and Segment.")
    else:
        st.write("Result: There is no significant association between Ship Mode and Segment.")

def show_summary():
    st.write("# SUPERSTORE DATASET - EXPLORATORY DATA ANALYSIS SUMMARY")
    st.write("=" * 60)
    
    st.write("## DATASET OVERVIEW:")
    st.write(f"Total Records: {df.shape[0]:,}")
    st.write(f"Total Features: {df.shape[1]}")
    st.write(f"Date Range: {df['Order Date'].min().date()} to {df['Order Date'].max().date()}")
    
    st.write("## KEY METRICS:")
    st.write(f"Total Sales: ${df['Sales'].sum():,.2f}")
    st.write(f"Total Profit: ${df['Profit'].sum():,.2f}")
    st.write(f"Average Order Value: ${df['Sales'].mean():.2f}")
    st.write(f"Average Profit per Order: ${df['Profit'].mean():.2f}")
    st.write(f"Overall Profit Margin: {(df['Profit'].sum() / df['Sales'].sum() * 100):.2f}%")
    
    st.write("## TOP PERFORMERS:")
    st.write(f"Top Selling Category: {df.groupby('Category')['Sales'].sum().idxmax()}")
    st.write(f"Most Profitable Category: {df.groupby('Category')['Profit'].sum().idxmax()}")
    st.write(f"Top Selling Sub-Category: {df.groupby('Sub-Category')['Sales'].sum().idxmax()}")
    st.write(f"Most Profitable Sub-Category: {df.groupby('Sub-Category')['Profit'].sum().idxmax()}")
    st.write(f"Top Customer: {df.groupby('Customer Name')['Sales'].sum().idxmax()}")
    st.write(f"Top Selling State: {df.groupby('State')['Sales'].sum().idxmax()}")
    
    st.write("## KEY INSIGHTS:")
    st.write(f"1. {df['Ship Mode'].value_counts().index[0]} is the most common shipping method.")
    st.write(f"2. {df['Segment'].value_counts().index[0]} segment represents the largest customer base.")
    st.write(f"3. Average shipping time is {df['Ship Days'].mean():.1f} days.")
    st.write(f"4. {df[df['Profit'] < 0].shape[0]} orders resulted in a loss ({df[df['Profit'] < 0].shape[0]/df.shape[0]*100:.1f}% of all orders).")
    st.write(f"5. {df[df['Discount'] > 0].shape[0]/df.shape[0]*100:.1f}% of orders included a discount.")

# Main app
def main():
    st.title("Superstore Data Analysis Dashboard")
    st.markdown("Explore the Superstore dataset through various visualizations and analyses.")
    
    # Sidebar with navigation options
    st.sidebar.title("Navigation")
    
    # Create a selectbox for navigation
    analysis_options = [
        "Summary",
        "Basic Info",
        "Descriptive Statistics",
        "Correlation Analysis",
        "Distribution Analysis",
        "Category Analysis",
        "Sales Analysis",
        "Profit Analysis",
        "Time Series Analysis",
        "Customer Analysis",
        "Product Analysis",
        "Shipping Analysis",
        "Discount Analysis",
        "Geographical Analysis",
        "Inferential Statistics"
    ]
    
    selected_analysis = st.sidebar.selectbox("Select Analysis", analysis_options)
    
    # Display the selected analysis
    if selected_analysis == "Summary":
        show_summary()
    elif selected_analysis == "Basic Info":
        show_basic_info()
    elif selected_analysis == "Descriptive Statistics":
        show_descriptive_stats()
    elif selected_analysis == "Correlation Analysis":
        show_correlation_analysis()
    elif selected_analysis == "Distribution Analysis":
        show_distribution_analysis()
    elif selected_analysis == "Category Analysis":
        show_category_analysis()
    elif selected_analysis == "Sales Analysis":
        show_sales_analysis()
    elif selected_analysis == "Profit Analysis":
        show_profit_analysis()
    elif selected_analysis == "Time Series Analysis":
        show_time_series_analysis()
    elif selected_analysis == "Customer Analysis":
        show_customer_analysis()
    elif selected_analysis == "Product Analysis":
        show_product_analysis()
    elif selected_analysis == "Shipping Analysis":
        show_shipping_analysis()
    elif selected_analysis == "Discount Analysis":
        show_discount_analysis()
    elif selected_analysis == "Geographical Analysis":
        show_geographical_analysis()
    elif selected_analysis == "Inferential Statistics":
        show_inferential_stats()
    
    # Add a footer
    st.sidebar.markdown("---")
    st.sidebar.info("This dashboard was created using Streamlit. Data source: Superstore Dataset.")

if __name__ == "__main__":
    main()
