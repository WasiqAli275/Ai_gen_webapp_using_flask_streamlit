# %% [markdown]
# # Credit Card Fraud Detection
# ## Anomaly Detection on Imbalanced Data
# **Dataset**: [Credit Card Fraud Dataset](https://www.kaggle.com/datasets/wasiqaliyasir/cerditcard-fraud-dataset)

# %% [code]
# Import Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import RobustScaler
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (classification_report, confusion_matrix, 
                            precision_recall_curve, average_precision_score)
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import make_pipeline
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

# %% [markdown]
# ## Load & Inspect Data

# %% [code]
df = pd.read_csv('/kaggle/input/cerditcard-fraud-dataset/Creditcard_Frauddetection.csv')
print(f"Dataset shape: {df.shape}")
print("\nFirst 5 rows:")
display(df.head())

# %% [markdown]
# ## Data Exploration

# %% [code]
print("\nDataset info:")
df.info()

print("\nClass distribution:")
class_dist = df['Class'].value_counts(normalize=True)
print(f"Legitimate (0): {class_dist[0]*100:.2f}%")
print(f"Fraudulent (1): {class_dist[1]*100:.2f}%")

print("\nDescriptive statistics:")
display(df.describe())

# %% [markdown]
# ## Visualize Distributions

# %% [code]
plt.figure(figsize=(15, 15))
plt.subplot(3, 2, 1)
sns.histplot(df['Amount'], kde=True)
plt.title('Transaction Amount')
plt.xlabel('Amount ($)')

for i, col in enumerate(['V1', 'V2', 'V3', 'V4', 'V5'], 2):
    plt.subplot(3, 2, i)
    sns.histplot(df[col], kde=True)
    plt.title(f'Distribution of {col}')
    
plt.tight_layout()
plt.show()

# %% [markdown]
# ## Class Imbalance Plot

# %% [code]
plt.figure(figsize=(10, 6))
ax = sns.countplot(x='Class', data=df)
plt.title('Class Distribution (0=Legit, 1=Fraud)')
plt.xlabel('Class')
plt.ylabel('Count')

for p in ax.patches:
    ax.annotate(f'{p.get_height()}', 
                (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', xytext=(0, 10), 
                textcoords='offset points')
plt.show()

# %% [markdown]
# ## Data Preprocessing

# %% [code]
X = df.drop('Class', axis=1)
y = df['Class']

scaler = RobustScaler()
X['Amount'] = scaler.fit_transform(X['Amount'].values.reshape(-1, 1))

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

print(f"Training set: {X_train.shape}, Test set: {X_test.shape}")

# %% [markdown]
# ## Define Models

# %% [code]
models = {
    "Logistic Regression": LogisticRegression(
        class_weight={0:1, 1:15},
        max_iter=1000,
        random_state=42
    ),
    "Random Forest": RandomForestClassifier(
        class_weight={0:1, 1:15},
        n_estimators=100,
        random_state=42
    ),
    "XGBoost": xgb.XGBClassifier(
        scale_pos_weight=15,
        eval_metric='logloss',
        random_state=42
    ),
    "Isolation Forest": IsolationForest(
        contamination=0.007,
        random_state=42
    )
}

# %% [markdown]
# ## Evaluation Function

# %% [code]
def evaluate_model(model, X_test, y_test, model_name):
    if model_name == "Isolation Forest":
        y_pred = model.predict(X_test)
        y_pred = [1 if x == -1 else 0 for x in y_pred]
    else:
        y_pred = model.predict(X_test)
    
    print(f"\n\033[1m{model_name} Performance:\033[0m")
    print(classification_report(y_test, y_pred))
    
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(4, 3))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Legit', 'Fraud'], 
                yticklabels=['Legit', 'Fraud'])
    plt.title(f'{model_name} Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.show()
    
    if model_name != "Isolation Forest":
        y_prob = model.predict_proba(X_test)[:, 1]
        precision, recall, _ = precision_recall_curve(y_test, y_prob)
        avg_precision = average_precision_score(y_test, y_prob)
        
        plt.figure(figsize=(6, 4))
        plt.plot(recall, precision, marker='.')
        plt.title(f'Precision-Recall (AP={avg_precision:.2f})')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.grid()
        plt.show()

# %% [markdown]
# ## Train & Evaluate Models

# %% [code]
for name, model in models.items():
    if name != "Isolation Forest":
        pipeline = make_pipeline(
            SMOTE(sampling_strategy=0.3, random_state=42),
            model
        )
        pipeline.fit(X_train, y_train)
        evaluate_model(pipeline, X_test, y_test, name)
    else:
        model.fit(X_train)
        evaluate_model(model, X_test, y_test, name)

# %% [markdown]
# ## Key Findings & Recommendations
