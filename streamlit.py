# best and advance webapp for all the users 
## in this webapp we can use all the library in it
### first we add some slightbar in it to change the data according to the user need it can also change it and also change the plots in this webapp
### second we can create create a webapp and addings plots in it 
### third we can also add some of the machine learning models in it 
### also add some prediction in it by using iris data set

import streamlit as  st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier

st.write("""
# Random Forest Classifier App
## Made by. Hadi yasir
This app predicts the type of iris based on sepal width, petal length, and petal width.
""")

st.sidebar.header('Change Iris Parameters')

def User_input_features():
    sepal_length = st.sidebar.slider('Sepal length (cm)', 1.5,15.5,5.4)
    sepal_width = st.sidebar.slider('Sepal width (cm)', 2.0,4.4,3.4)
    petal_length = st.sidebar.slider('petal length', 1.0, 6.9, 1.3)
    petal_width = st.sidebar.slider('petal width', 0.1, 2.5, 0.2)
    data = {'sepal_length': sepal_length,
            'sepal_width': sepal_width,
            'petal_length': petal_length,
            'petal_width': petal_width}
    features = pd.DataFrame(data, index=[0])
    return features

df = User_input_features()

st.subheader('Iris parameters')
st.write(df)

iris = sns.load_dataset('iris')

st.subheader('iris dataset')
st.write(iris.head(10))

st.subheader('plots of plotly')
fig = px.bar(iris, x="species", y="petal_length", color= 'species')
st.plotly_chart(fig)


# st.subheader('plots of plotly')
# sns.barplot(x=iris['species'], y=iris['sepal_width'])
# st.pyplot()


# fig, ax = plt.subplots()
# ax.scatter(x=iris['petal_length'], y=iris['sepal_width'])
# st.pyplot(fig)


st.subheader('plot of matplotlib.pyplot')

df1 = px.data.gapminder()
fig2 = px.scatter(df1, x="gdpPercap", y="lifeExp", animation_frame="year", animation_group="country",
           size="pop", color="continent", hover_name="country",
           log_x=True, size_max=55, range_x=[100,100000], range_y=[25,90])
st.plotly_chart(fig2)


fig4 = px.bar(df1, x="continent", y="pop", color="continent",
  animation_frame="year", animation_group="country", range_y=[0,4000000000])
st.plotly_chart(fig4)


fig5 = px.scatter_3d(iris, x='sepal_length', y='sepal_width', z='petal_width',
                     color='species')
st.plotly_chart(fig5)




x = iris[['sepal_length', 'sepal_width', 'petal_length', 'petal_width']]
y = iris['species']

model = RandomForestClassifier()
model.fit(x, y)

prediction = model.predict(df)
prediction_proba = model.predict_proba(df)
# st.subheader('Class labels and their corresponding index number')
# st.write(iris['species'].unique())

st.subheader('Prediction')
p = st.write(prediction[0])
st.write(p)

st.subheader('Prediction Probability')
st.write(prediction_proba)
