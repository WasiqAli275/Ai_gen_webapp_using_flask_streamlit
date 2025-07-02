# we can create a streamlit webapp and add titanic data set in it by using seaborn and firstly, we can add some slideber
# in it and also add some machine learning models in it for the prediction and also we can change the machine learning models and
# its accuracy according to the needs and also have a fuction to change the parameter in it of this webapp
import streamlit as st
import seaborn as sns
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score



# make containers
header = st.container()
datasets = st.container()
featuress = st.container()
modle_traning = st.container()

with header:
    st.title('kashti ki app')
    st.text('In this project we will work on kashti data')
    
with datasets:
    st.header('Kashti was drown in the see')
    st.text('we will work with titanic dataset')
    # import data
    
    df = sns.load_dataset('titanic')
    df = df.dropna()
    st.write(df.head(10))
    st.subheader('how many humans in there are')
    st.bar_chart(df['sex'].value_counts())

    # other charts
    st.subheader("According to class header")
    st.bar_chart(df['class'].value_counts())
    # barchart
    st.bar_chart(df['age'].sample(10))

with featuress:
    st.header('There are our app features')
    st.text('there are so many features we can add, very easy')
    st.markdown("1. **featutrs 1:** tell us i don't no")
    st.markdown("1. **featutrs 2:** tell us who are you")

with modle_traning:
    st.header('What happend in kashti data? model traning')
    st.text('In this we can increase our parameters')
    # making columns
    input, display = st.columns(2)
    
    # pehly column main ap k selection points hun
    max_depth = input.slider("How many people do you know?", min_value=10, max_value=100, value=20, step=5)
    
    
# n_estimeters
n_estimators = input.selectbox("How many tree should be there in a RF?", options=[50,100,200,300,'No limit'])

# adding list of features
input.write(df.columns)

# input fretures from user

input_features = input.text_input('Which features we should use?')


# machine learning model
model = RandomForestRegressor(max_depth=max_depth, n_estimators=n_estimators)

# yaha per hum ik condition lagaya gai
if n_estimators == 'No limit':
    model = RandomForestRegressor(max_depth=max_depth)
else:
    model = RandomForestRegressor(max_depth=max_depth, n_estimators=n_estimators)
    
    
# define x and y
X = df[[input_features]]
y = df[['fare']]

# fit a model
model.fit(X, y)
pred= model.predict(y)



# display matrices
display.subheader("Mean absolute error of the model is: ")
display.write(mean_absolute_error(y, pred))
display.subheader("Mean squared error of the model is: ")
display.write(mean_squared_error(y, pred))
display.subheader("R squared score of the model is: ")
display.write(r2_score(y, pred))
