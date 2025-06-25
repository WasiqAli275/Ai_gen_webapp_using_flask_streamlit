import google.generativeai as genai

genai.configure(api_key="AIzaSyBqsWxzgz7r5dGcpiJfeUHnZJbxqQQbIyw")

for model in genai.list_models():
    print(model.name)