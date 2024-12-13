import numpy as np
import pandas as pd
import streamlit as st
#import pandas_profiling # issue is resolved if we use ydata_profiling
from ydata_profiling import ProfileReport # having issue
from streamlit_pandas_profiling import st_profile_report
import seaborn as sns
# title of web app
st.markdown('''
            # **Exploratory Data Analysis (EDA) web application**
            This is developed by prof. Wasiq Ali yasir called **EDA app**
            ''')
# how to upload a file from pc
with st.sidebar.header("upload your dataset(.csv)"):
    uploaded_file = st.sidebar.file_uploader("upload your file", type=['csv'])
    df = sns.load_dataset('titanic')
    st.sidebar.markdown("[Example CSV file](https://github.com/WasiqAli275)")
# profile report for pandas
if uploaded_file is not None:
    @st.cache # used to improve speed in your data
    def load_csv():
        csv = pd.read_csv(uploaded_file)
        return csv
    df = load_csv()
    pr = ProfileReport(df, explorative=True)
    st.header('**Input DF**')
    st.write(df)
    st.write('---')
    st.header('**Profiling report with pandas**')
    st_profile_report(pr)
else:
    st.info('Awatring for CSV file, upload it or you want more work?')
    if st.button('press to use example data'):
        # example dataset
        @st.cache # used to improve speed in your data        
        
        def load_data():
            a = pd.DataFrame(np.random.rand(100, 5),
                                columns=['age', 'banana', 'cat', 'deutchland', 'ear'])
            return a
        df = load_data()
        pr = ProfileReport(df, explorative=True)
        st.header('**Input DataFrame**')
        st.write(df)
        st.write('---')
        st.header('**Profiling report with pandas**')
        st_profile_report(pr)