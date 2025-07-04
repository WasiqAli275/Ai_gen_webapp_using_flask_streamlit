from flask import Flask, render_template, request, url_for
import openai

# create a flask webapp
app = Flask(__name__)

# laod your openai api key 
openai_api_key = "sk-8IS8CycxhTEPnFbYePUhT3B1bkFJaLhvjZXMFqFiVKp5ytIg"

def genrate_image(prompt):
    client = openai.Openai(api_key=openai_api_key)

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    
    return response.data[0].url

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        prompt = request.form.get('prompt')
        if prompt:
            image_url = genrate_image(prompt)
            if image_url:
                return render_template('index.html', image_url=image_url)
            else:
                return render_template('index.html', error='Failed retry')
        else:
            return render_template('index.html', error='Please enter a prompt')
        
    return render_template('index.html')

if __name__ == '__main__':
    app.run(degug=True)
