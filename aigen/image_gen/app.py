from flask import Flask
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Initialize Flask app
app = Flask(__name__)



# Load your API key from .env file (recommended)
load_dotenv()
api_key = os.getenv("new_api_key")

# Configure Gemini with your API key
genai.configure(api_key=api_key)

# Choose model (Gemini Pro)
model = genai.GenerativeModel("gemini-pro")

# Send a prompt to the model
response = model.generate_content("Explain black holes in simple words.")

# Print the result
print(response.text)
