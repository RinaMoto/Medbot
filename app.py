from flask import Flask, request
import requests
import json
import config
import openai

app = Flask(__name__)
app.config['SECRET_KEY'] = 'EAAH92KLLZCkwBALdw5EsV6rFY2zgmsuHegmiErk3ZCqtqo3SRbeVJtXi9DZBsLKdZCsDYsGljkEU85CKZAMbZBZBpgt9uPDVPPcyHYUuntZBxPm4ZCYLVZBpThCEfpIh7XvU5MYsB0PZBZAwnEU6fLqcNNUaEqTgmrYPeNAY5iQWMF1wZCTt4deXDfKVVujJ8MW8l0ZAkZD'

#Secret Key for OpenAI
openai.api_key = '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'

#Function to access the Sender API
def callSendAPI(senderPsid, response):
    PAGE_ACCESS_TOKEN = config.PAGE_ACCESS_TOKEN

    payload = {
        'recipient': {'id': senderPsid},
        'message': response,
        'messaging_type': 'RESPONSE'
    }
    headers = {'content-type': 'application/json'}

    url = 'https://graph.facebook.com/v10.0/me/messages?access_token={}'.format(PAGE_ACCESS_TOKEN)
    r = requests.post(url, json=payload, headers=headers)
    print(r.text)



#Function for handling a message from MESSENGER
def handleMessage(senderPsid, receivedMessage):

    #check if received message contains text
    if 'text' in receivedMessage:
        #check which slash command was used
        if '/emergency' in receivedMessage['text']:
            ai_response = openai.Completion.create(
                engine="text-davinci-003",
                prompt= f"input: I need emergency medical assistance. Can you provide me with the contact information for the nearest hospital/emergency services? I live in {receivedMessage['text'].split()[1]} what is the nearest hospital to {receivedMessage['text'].split()[1]}",
                max_tokens=2000,
                temperature=1,
                top_p=1,
                stream=False,
                echo=True,
                logprobs=None,
                stop=["{}"]
            )
            response = {"text": ''.format(str(ai_response))}
        
        elif '/symptoms' in receivedMessage['text']:
            ai_response = openai.Completion.create(
                model="text-davinci-003",
                prompt= f"input: I have been experiencing {receivedMessage['text'].split()[1]}. Can you tell me what could be causing it?",
                max_tokens=3000,
                temperature=1,
                top_p=1,
                stream=False,
                echo=True,
                logprobs=None,
                stop=["{}"]
            )
            response = {"text": str(ai_response)}
        
        elif '/disease' in receivedMessage['text']:
            ai_response = openai.Completion.create(
                model="text-davinci-003",
                prompt= f"input: I have caught this disease {receivedMessage['text'].split()[1]}. Can you tell me what could be causing it and what I should know about it?",
                max_tokens=3000,
                temperature=1,
                top_p=1,
                stream=False,
                echo=True,
                logprobs=None,
                stop=["{}"]
            )
            response = {"text": str(ai_response)}
        
        else:
            #if no slash command was used, send the message to OpenAI for processing
            ai_response = openai.Completion.create(
                model="text-davinci-003",
                prompt=f"input: {receivedMessage['text']}",
                max_tokens=3000,
                temperature=1,
                top_p=1,
                stream=False,
                echo=True,
                logprobs=None,
                stop=["{}"]
            )
            response = {"text": str(ai_response)}
        callSendAPI(senderPsid, response)
    else:
        response = {"text": 'This chatbot only accepts text messages'}
        callSendAPI(senderPsid, response)


@app.route('/', methods=["GET", "POST"])
def home():

    return 'HOME'

@app.route('/webhook', methods=["GET", "POST"])
def index():
    if request.method == 'GET':
        #do something.....
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
        #do something.....
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



        #do something else
        data = request.data
        body = json.loads(data.decode('utf-8'))

        if 'object' in body and body['object'] == 'page':
            entries = body['entry']
            for entry in entries:
                webhookEvent = entry['messaging'][0]
                print(webhookEvent)

                senderPsid = webhookEvent['sender']['id']
                print('Sender PSID: {}'.format(senderPsid))

                if 'message' in webhookEvent:
                    handleMessage(senderPsid, webhookEvent['message'])

                return 'EVENT_RECEIVED', 200
        else:
            return 'ERROR', 404



if __name__ == '__main__':
    app.run()