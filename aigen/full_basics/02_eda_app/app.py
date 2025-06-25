from flask import Flask
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import io
import base64


app = Flask(__name__)

def load_dataset():
    # Load the dataset from a CSV file
    df = sns.load_dataset('iris')
    return df

# define a fuction to create a plot
def create_plot():
    df = load_dataset()
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='sepal_length', y='sepal_width', hue='species')
    plt.title('Iris Dataset Sepal Length vs Sepal Width created by Seaborn and deracted by me and name prof.WasiqAliYasir')
    plt.xlabel('Sepal Length')
    plt.ylabel('Sepal Width ')
    
    # Save the plot to a Bytes object
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    # Encode the Bytes object to base64
    base64_image = base64.b64encode(bytes_image.getvalue()).decode('utf-8')
    return base64_image

# define the route
@app.route('/')
def index():
    # Create the plot
    base64_image = create_plot()
    
    # Return the HTML with the embedded image
    return f'''
    <html>
        <head>
            <title>Iris Dataset Plot</title>
        </head>
        <body>
            <h1>Iris Dataset Sepal Length vs Sepal Width</h1>
            <img src="data:image/png;base64,{base64_image}" alt="Iris Dataset Plot">
        </body>
    </html>
    '''
    
# run the app
if __name__ == '__main__':
    app.run(debug=True)

    
