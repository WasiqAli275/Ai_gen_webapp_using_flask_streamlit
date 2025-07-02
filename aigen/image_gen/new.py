import google.generativeai as genai

genai.configure(api_key="Enter your own api to run this model")  # Apna API key yahan dalen
# Gemini-1.5-pro ki jagah Gemini-1.0-pro use karen (jo free tier mein zyada requests allow karta hai)
model = genai.GenerativeModel('gemini-1.0-pro')  # Change to older version

response = model.generate_content("Python programming ke bare mein 2 sentences mein batao")
print(response.text)
