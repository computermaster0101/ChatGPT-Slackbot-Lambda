import json
import boto3


class Gatekeeper:
    def __init__(self, keys):
        print('Gatekeeper.__init__')
        self.keys = keys
        self.function_name= 'ChatGPT-Slackbot'
        self.lambda_client = boto3.client('lambda')

    def is_key_valid(self, api_key):
        print('Gatekeeper.is_key_valid')
        if api_key in self.keys.values():
            return True
        else:
            return False

    def open_the_gate(self, event):
        print('Gatekeeper.open_the_gate')
        event['queryStringParameters']['tmpkey'] = event['queryStringParameters']['apikey']
        event['queryStringParameters']['apikey'] = self.keys['chatgpt_key']

        self.lambda_client.invoke(
            FunctionName=self.function_name,
            InvocationType='Event',
            Payload=json.dumps(event)
        )

    def close_the_gate(self, event):
        print('Gatekeeper.close_the_gate')
        event['queryStringParameters']['apikey'] = event['queryStringParameters']['tmpkey']
        return event

    def get_max_and_current_runtime(self,context):
        function_response = self.lambda_client.get_function(
            FunctionName=self.function_name
        )
        function_timeout = function_response['Configuration']['Timeout']
        remaining_time_in_ms = context.get_remaining_time_in_millis()
        remaining_time_in_sec = remaining_time_in_ms / 1000
        return function_timeout, remaining_time_in_sec