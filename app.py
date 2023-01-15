from flask import Flask, request
import requests
import json
import config
import openai

app = Flask(__name__)
app.config['SECRET_KEY'] = 'EAAH92KLLZCkwBAAtvVWlKhkChEidNHagIZC7p2WcOU3VMBubEqv1VyneSlfRvhInfo3MbiCxiO2H9DWz9gRIZCdM47J0N12mEk3zswkFZBwqVdjN8UbZBldqPjKtVeiXzlZAJjdtuTAO90ZCGncsOjZBg5U33hy3YWZCDUKasYzlCZAEqUYKxZCbTMRfEZAPkZCkXrjsZD'

#Secret Key for OpenAI
openai.api_key = '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'

#Function to access the Sender API
def callSendAPI(sender_psid, response):
    PAGE_ACCESS_TOKEN = config.PAGE_ACCESS_TOKEN

    payload = {
        'recipient': {'id': sender_psid},
        'message': response,
        'messaging_type': 'RESPONSE'
    }
    headers = {'content-type': 'application/json'}

    url = 'https://graph.facebook.com/v10.0/me/messages?access_token={}'.format(PAGE_ACCESS_TOKEN)
    r = requests.post(url, json=payload, headers=headers)
    print(r.text)



# Function for handling a message from MESSENGER
def handleMessage(sender_psid, received_message):
    # check if received message contains text
    if 'text' in received_message:
        user_input_text = received_message['text'].lower()
        if 'get started' in user_input_text:
            response = {"text": "welcome"}
            
        elif '/help' in user_input_text:
            response = {"text": "Here are the different commands you can ask me:\n/emergency <location>\n/symptoms <symptoms>\n/disease <disease name>"}
        
        # check different medical slash commands
        elif '/emergency' in user_input_text:
            input_text = user_input_text.split('/emergency')
            if len(input_text) > 1:
                ai_response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt= f"input: I need emergency medical assistance. Can you provide me with the contact information for the nearest hospital/emergency services? I live in {input_text[1]} what is the nearest hospital to {input_text[1]}",
                    max_tokens=2000,
                    temperature=1,
                    top_p=1,
                    stream=False,
                    echo=False,
                    logprobs=None,
                    stop=["{}"]
                )
                response = {"text": str(ai_response["choices"][0]["text"])}
            else:
                response = {"text": "Please enter valid emergency format: /emergency <location>"}
        
        elif '/symptoms' in user_input_text:
            input_text = user_input_text.split('/symptoms')
            if len(input_text) > 1:
                ai_response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt= f"input: I have been experiencing {input_text[1]}. Can you tell me what could be causing it?",
                    max_tokens=3000,
                    temperature=1,
                    top_p=1,
                    stream=False,
                    echo=False,
                    logprobs=None,
                    stop=["{}"]
                )
                response = {"text": str(ai_response["choices"][0]["text"])}
            else:
                response = {"text": "Please enter valid symptoms format: /symptoms <symptoms>"}
        
        elif '/disease' in user_input_text:
            input_text = user_input_text.split('/disease')
            if len(input_text) > 1:
                ai_response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt= f"input: I have caught this disease {input_text[1]}. Can you tell me what could be causing it and what I should know about it?",
                    max_tokens=3000,
                    temperature=1,
                    top_p=1,
                    stream=False,
                    echo=False,
                    logprobs=None,
                    stop=["{}"]
                )
                response = {"text": str(ai_response["choices"][0]["text"])}
            else:
                response = {"text": "Please enter valid disease format: /disease <disease name>"}
        
        else:
            # if no slash command was used, send the message to OpenAI for processing
            ai_response = openai.Completion.create(
                model="text-davinci-003",
                prompt=f"input: {user_input_text}",
                max_tokens=3000,
                temperature=1,
                top_p=1,
                stream=False,
                echo=False,
                logprobs=None,
                stop=["{}"]
            )
            response = {"text": str(ai_response["choices"][0]["text"])}
        callSendAPI(sender_psid, response)
    else:
        response = {"text": 'This chatbot only accepts text messages'}
        callSendAPI(sender_psid, response)


@app.route('/', methods=["GET", "POST"])
def home():
    return 'HOME'

@app.route('/webhook', methods=["GET", "POST"])
def index():
    if request.method == 'GET':
        VERIFY_TOKEN = "haihai123"

        if 'hub.mode' in request.args:
            mode = request.args.get('hub.mode')
            print(mode)
        if 'hub.verify_token' in request.args:
            token = request.args.get('hub.verify_token')
            print(token)
        if 'hub.challenge' in request.args:
            challenge = request.args.get('hub.challenge')
            print(challenge)

        if 'hub.mode' in request.args and 'hub.verify_token' in request.args:
            mode = request.args.get('hub.mode')
            token = request.args.get('hub.verify_token')

            if mode == 'subscribe' and token == VERIFY_TOKEN:
                print('WEBHOOK VERIFIED')

                challenge = request.args.get('hub.challenge')

                return challenge, 200
            else:
                return 'ERROR', 403

        return 'SOMETHING', 200


    if request.method == 'POST':
        VERIFY_TOKEN = "haihai123"

        if 'hub.mode' in request.args:
            mode = request.args.get('hub.mode')
            print(mode)
        if 'hub.verify_token' in request.args:
            token = request.args.get('hub.verify_token')
            print(token)
        if 'hub.challenge' in request.args:
            challenge = request.args.get('hub.challenge')
            print(challenge)

        if 'hub.mode' in request.args and 'hub.verify_token' in request.args:
            mode = request.args.get('hub.mode')
            token = request.args.get('hub.verify_token')

            if mode == 'subscribe' and token == VERIFY_TOKEN:
                print('WEBHOOK VERIFIED')

                challenge = request.args.get('hub.challenge')

                return challenge, 200
            else:
                return 'ERROR', 403

        data = request.data
        body = json.loads(data.decode('utf-8'))

        if 'object' in body and body['object'] == 'page':
            entries = body['entry']
            for entry in entries:
                webhook_event = entry['messaging'][0]
                print(webhook_event)

                sender_psid = webhook_event['sender']['id']
                print('Sender PSID: {}'.format(sender_psid))

                if 'message' in webhook_event:
                    handleMessage(sender_psid, webhook_event['message'])

                return 'EVENT_RECEIVED', 200
        else:
            return 'ERROR', 404


if __name__ == '__main__':
    app.run()