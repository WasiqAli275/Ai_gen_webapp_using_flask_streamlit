# best for checking an web app that is really working or not
import streamlit as st
import seaborn as sns

# st.header mains add heading in the streamlit webapp and text means add text in it
st.header("this streamlit app is created by wasiq Ali Yasir")
st.text("I am intrested in python leanguage and become a data scientest")

st.header("This is the dataset of iris")

#load the data set
df = sns.load_dataset('iris')
st.write(df[['species', 'sepal_length', 'petal_length']].head(10))

# ad the bar_chart and line plot in it 
st.bar_chart(df['sepal_length'])
st.line_chart(df['sepal_length'])
