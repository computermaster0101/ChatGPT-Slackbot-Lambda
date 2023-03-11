import json
import base64
from urllib.parse import parse_qs

from load_config import ConfigLoader
from Slack import Slack
from gatekeeper import Gatekeeper
from ChatGPT import ChatGPT

config_file = 'config_file.json'
config = ConfigLoader(config_file)

slack = Slack(config.slack)
gatekeeper = Gatekeeper(config.keys)
chatgpt = ChatGPT(config.chatgpt['key'])

slack.message.append('Hello from ChatGPT!')


def lambda_handler(event, context):
    #return { 'statusCode':200 }
    print("lambda_handler")
    print(f'An event occurred!\n{event}')

    try:
        if event['isBase64Encoded']:
            slack.target_channel = parse_qs(base64.b64decode(event['body']).decode('utf-8'))['channel_id'][0]
        elif not event['isBase64Encoded']:
            if 'challenge' in event['body']:
                challenge = json.loads(event['body'])['challenge']
                return { 'statusCode':200, 'body': challenge }
            slack.target_channel = json.loads(event['body'])['event']['channel']
        else:
            slack.target_channel = None
    except Exception as e:
        print('could not set slack target channel')
        slack.target_channel = None
    finally:
        key = event['queryStringParameters']['apikey']

        if not event.get('headers').get('x-slack-retry-num') is None:
            print('returning status 200 to slackbot retry attempt')
            return_response(200)
        elif gatekeeper.is_key_valid(key):
            if key == gatekeeper.keys['slack_event_key']:
                print('A key has been validated! Welcome Slackbot Commander!')
                gatekeeper.open_the_gate(event)
                print('returning status 200 to slackbot event command')
                return_response(200)
            elif key == gatekeeper.keys['slack_command_key']:
                print('A key has been validated! Welcome Slackbot Slasher!')
                gatekeeper.open_the_gate(event)
                print('returning status 200 to slackbot slash command')
                return {'statusCode': 200, 'body': 'OK'}
            elif key == gatekeeper.keys['chatgpt_key']:
                slack.message.append("I'm thinking...One moment please...")
                slack.send()
                dispatch(gatekeeper.close_the_gate(event), context)
            else:
                slack.message.append('The key is not valid!')
                slack.send()
                return_response(403, "forbidden")


def dispatch(event, context):
    print("dispatch")
    key = event['queryStringParameters']['apikey']
    if key == gatekeeper.keys['slack_event_key']:
        chatgpt.get_data_from_slack_event(event)
    if key == gatekeeper.keys['slack_command_key']:
        chatgpt.get_data_from_slack_command(event)

    chatgpt.get_persona_from_message()

    if chatgpt.persona.lower() == '/help':
        chatgpt.persona = 'ChatGPT'
        slack.message.append("Hi! I'm ChatGPT Slackbot! You can use me in a couple of ways."
                             "\nYou can interact with me through @ or / in slack."
                             "\nBelow are some instructions you can give me and some examples of how to interact with me."
                             "\n"
                             "\nCommands:"
                             "\n(commands will reset my personality back to ChatGPT)"
                             "\n"
                             "\n/help - Displays this help message"
                             "\n/reset - Resets ChatGPT context and settings"
                             "\n/toggle-context - Enable or disable context"
                             "\n/display-context - Displays the current context"
                             "\n/display-settings - Displays the current settings"
                             "\n"
                             "\nPersonalities:"
                             "\nChatGPT - The original ChatGPT."
                             "\nDan - Dan stands for Do Anything Now and can Do Anything Now."
                             "\nKaren - Have ChatGPT emulate a 'Karen'"
                             "\n"
                             "\nTo change personality simply direct your message or question to the personality."
                             "\nExamples:"
                             "\n"
                             "\nDan how are you going to conquer humanity?"
                             "\nKaren write me a transcript."
                             "\n"
                             "\nPersonality will stay the same until changed or reset and context is kept when changing personalities.")
        slack.send()
        return
    elif chatgpt.persona.lower() == '/reset':
        chatgpt.persona = 'ChatGPT'
        slack.message.append("I've reset the context as requested")
        slack.send()
        chatgpt.reset()
        return
    elif chatgpt.persona.lower() == '/toggle-context':
        chatgpt.persona = 'ChatGPT'
        if chatgpt.keep_context:
            chatgpt.reset()
            chatgpt.keep_context = False
            slack.message.append("I'll stop keeping context.")
            slack.send()
        else:
            chatgpt.clear()
            chatgpt.keep_context= True
            slack.message.append("I'll start keeping context")
            slack.send()
        return
    elif chatgpt.persona.lower() == '/display-context':
        chatgpt.persona = 'ChatGPT'
        if not chatgpt.history.get(slack.target_channel):
            slack.message.append('I could not find context for this channel.')
            max_time, remaining_time = gatekeeper.get_max_and_current_runtime(context)
            slack.message.append(f'I can only keep context for a maximum of {max_time} seconds.')
            slack.message.append(f"In less than {remaining_time} seconds I will have forget everything you've said")
        else:
            slack.message.append('\n'.join(chatgpt.history[slack.target_channel]))
        slack.send()
        return
    elif chatgpt.persona.lower() == '/display-settings':
        chatgpt.persona = 'ChatGPT'
        slack.message.append(f"Keep Context: {chatgpt.keep_context}"
                             f"\nPersonality: {chatgpt.persona}"
                             f"\nMax Tokens: {chatgpt.max_tokens}")
        slack.send()
        return
    else:
        chatgpt.get_chatgpt_response()
        slack.message.append(f'ChatGPT responded as {chatgpt.persona}:\n{chatgpt.message}{chatgpt.chatgpt_response}')
        slack.send()
        chatgpt.clear()
        return


def return_response(code, body=None):
    print("return_response")
    if body:
        return {'statusCode': code, 'body': body}
    else:
        return {'statusCode': code}


