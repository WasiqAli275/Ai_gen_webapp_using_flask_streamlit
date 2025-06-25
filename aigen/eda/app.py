# flask_iris_app.py

from flask import Flask, render_template
import seaborn as sns
import pandas as pd

import matplotlib
matplotlib.use("Agg")  # ✅ Fix: use non-GUI backend
import matplotlib.pyplot as plt
import io
import base64


app = Flask(__name__)

# Load the dataset once
iris_df = sns.load_dataset("iris")

# Utility function to generate plot images and return them as base64 strings
def plot_to_img(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return img_base64

@app.route("/")
def index():
    # Basic statistics
    summary = iris_df.describe().to_html(classes="table table-striped")
    nulls = iris_df.isnull().sum().to_frame(name='Null Count').to_html(classes="table table-bordered")

    # Plot 1: Count Plot
    fig1, ax1 = plt.subplots()
    sns.countplot(data=iris_df, x="species", palette="Set2", ax=ax1)
    count_plot = plot_to_img(fig1)
    plt.close(fig1)

    # Plot 2: Correlation Heatmap
    fig2, ax2 = plt.subplots()
    sns.heatmap(iris_df.drop("species", axis=1).corr(), annot=True, cmap="coolwarm", ax=ax2)
    heatmap_plot = plot_to_img(fig2)
    plt.close(fig2)

    return render_template("index.html",
                           tables=[summary, nulls],
                           count_plot=count_plot,
                           heatmap_plot=heatmap_plot)

if __name__ == "__main__":
    app.run(debug=True)
