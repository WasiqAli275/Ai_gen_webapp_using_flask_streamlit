# Flask App for SMS + OpenAI
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/sms", methods=['POST'])
def sms_reply():
    user_msg = request.form.get('Body')
    # Get AI Response (Using OpenAI)
    ai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_msg}]
    ).choices[0].message.content
    
    resp = MessagingResponse()
    resp.message(ai_response)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)