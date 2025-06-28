# import all libraries and create a web app that can predict the iris data set by using seaborn and predict it my using sklearn machine learning model and
# it can also check it how it the best fit of the data set and also deploy the best ml model in it
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# heading
st.write("""
         # Explore different ML model and datasets
         check it how is the best in this things?
         """)

# data set k name ak box daal k sibebar pay laga de
dataset_name = st.sidebar.selectbox(
    'Select Dataset',
    ('Iris', 'Breast canser', 'wine')
)

# our ise ka necha Classifrier ka nam se ik our dabe me dal doo.
Classifier_name = st.sidebar.selectbox(
    'Select classifier',
    ('MNN', 'SVM', 'Random forest')
)

# ab hame ik function define karna hai dataset ko load karna ke liya.
def get_dataset(dataset_name):
    data = None
    if dataset_name == "Iris":
        data = datasets.load_iris()
    elif dataset_name == "Wine":
        data = datasets.load_wine()
    else:
        data = datasets.load_breast_cancer()
    x = data.data
    y = data.target
    return x, y

# ab is function ko bula le gai or x,y variable k equal rakh layn gay
x, y = get_dataset(dataset_name)

# ab hum apnay data set ki shape ko app pay print kr dayn gai
st.write('Shape of dataset:', x.shape)
st.write('Number of classes:', len(np.unique(y)))

# next hum different classifier k parameter ko user input may add karayn gay
def add_parameter_ui(classifier_name):
    params = dict() # Create an empty dictionary
    if classifier_name == 'SVM':
        c = st.sidebar.slider('c', 0.01, 10.0)
        params['c'] = c # its the number of corrct classification
    elif classifier_name == 'KNN':
        k = st.sidebar.slider('k', 1, 15)
        params['k'] = k # its the number of nearest neighbour
    else:
        max_depth = st.sidebar.slider('max_depth', 2, 15)
        params['max_depth'] = max_depth # depth of every tree that grow in random forest
        n_estimatosr = st.sidebar.slider('n_estimators', 1, 100)
        params['n_estimators'] = n_estimatosr # number of trees
        return params

# ab is function ko bula le gai our param ke equal rakha le gai
params = add_parameter_ui(Classifier_name)

# abb hum classifier banaya gai base on classifier name and params
def get_classifier(classifier_name, params):
    clf = None
    if classifier_name == 'SVM':
        clf = SVC(C=params['C'])
    elif classifier_name == 'KNN':
        clf = KNeighborsClassifier(n_neighbors=params['k'])
    else:
        clf = clf = RandomForestClassifier(n_estimators=params['n_estimators'],
                                           max_depth=params['max_depth'], random_state=1234)
        return clf

# ab id function ko bula lay gayn or clf varialbe k equal rakh layn gay
clf = get_classifier(Classifier_name, params)

# split the data in test train in to 80/20 ratio
X_test, X_train, y_test, y_train = train_test_split(x, y, test_size=0.2, random_state=1234)

# traning the classifier
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

# modle ke accuracy score check kr layna ha or isay app pay kr dayna ha
acc = accuracy_score(y_test, y_pred)
st.write(f'Classifier = {Classifier_name}')
st.write(f'Accuracy = {acc}')
#### PLOT DATAWET ####
# ab hum apna data saray features ko 2 dimenssional plot pay draw kr dayn gay using pca
pca = PCA(2)
x_projected = pca.fit_transform(x)

# ab hum apna data 0 or 1 dimension may slice kar dayn gay
x1 = x_projected[:, 0]
x2 = x_projected[:, 1]

fig = plt.scatter(x1, x2,
                  c=y, alpha=0.8,
                  cmap = 'viridis')

plt.xlabel('Principal component 1')
plt.ylabel('Principal component 2')
plt.colorbar()

# plot show()
st.pyplot(fig)

