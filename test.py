import streamlit as st
import seaborn as sns

st.header("this streamlit app is created by wasiq Ali Yasir")
st.text("I am intrested in python leanguage and become a data scientest")

st.header("This is the dataset of iris")

df = sns.load_dataset('iris')
st.write(df[['species', 'sepal_length', 'petal_length']].head(10))

st.bar_chart(df['sepal_length'])
st.line_chart(df['sepal_length'])