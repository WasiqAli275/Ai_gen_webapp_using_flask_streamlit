import google.generativeai as genai

genai.configure(api_key="########################") # enter your api to check your model names in it.

for model in genai.list_models():
    print(model.name)
