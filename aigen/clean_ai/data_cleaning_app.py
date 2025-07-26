import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import base64

def main():
    # Title and Introduction
    st.title("Data Cleaning Web Application")
    st.write("Upload your CSV or Excel file to clean and analyze your data")
    
    # File Upload Section
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", 
                                   type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file is not None:
        # Read the file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Display original data preview
        st.header("Original Data Preview")
        st.write(df.head())
        
        # Display data information
        st.header("Data Information")
        st.write(df.info())
        
        # Display summary statistics
        st.header("Summary Statistics")
        st.write(df.describe())
        
        # Data cleaning options
        st.header("Data Cleaning Options")
        col1, col2 = st.columns(2)
        
        with col1:
            # Handle missing values
            st.subheader("Missing Values")
            show_missing = st.checkbox("Show missing values")
            if show_missing:
                st.write(df.isnull().sum())
            
            # Remove duplicates
            remove_duplicates = st.checkbox("Remove duplicates")
            if remove_duplicates:
                df = df.drop_duplicates()
                st.write("Duplicates removed")
        
        with col2:
            # Data type conversion
            st.subheader("Data Type Conversion")
            numeric_cols = df.select_dtypes(include=['object']).columns
            for col in numeric_cols:
                convert = st.checkbox(f"Convert {col} to numeric", key=col)
                if convert:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Handle outliers
            st.subheader("Outlier Detection")
            show_outliers = st.checkbox("Show outlier detection")
            if show_outliers:
                numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
                for col in numeric_cols:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    outliers = df[~((df[col] >= Q1 - 1.5 * IQR) & (df[col] <= Q3 + 1.5 * IQR))]
                    if not outliers.empty:
                        st.write(f"Outliers found in {col}:")
                        st.write(outliers)
        
        # Display cleaned data
        st.header("Cleaned Data Preview")
        st.write(df.head())
        
        # Download cleaned data
        
        st.header("Download Cleaned Data")
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="cleaned_data.csv">Download CSV File</a>'
        st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()