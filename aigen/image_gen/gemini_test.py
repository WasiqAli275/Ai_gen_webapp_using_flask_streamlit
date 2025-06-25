import google.generativeai as genai

# Step 1: Apna API key set karen
API_KEY = "AIzaSyBqsWxzgz7r5dGcpiJfeUHnZJbxqQQbIyw"  # Yahan apna API key dalen
genai.configure(api_key=API_KEY)

# Step 2: Model ko initialize karen
model = genai.GenerativeModel('gemini-pro')  # Basic text model

# Step 3: Ek simple prompt bhejen
prompt = "Hello Gemini! Mujhe batao ke tum kaam kar rahe ho? 2 sentences mein Urdu Roman mein jawab dena."

try:
    # Response generate karen
    response = model.generate_content(prompt)
    
    # Response print karen
    print("Gemini ka jawab:")
    print(response.text)
    
except Exception as e:
    print("Koi masla hua:", e)
