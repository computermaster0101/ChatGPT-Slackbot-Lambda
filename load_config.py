import json


class ConfigLoader:
    def __init__(self, config_file):
        print("ConfigLoader.__init__")
        try:
            config = json.load(open(config_file))
            self.keys = {
                "chatgpt_key": config["chatgpt_relay_key"],
                "slack_event_key": config["slack_event_key"],
                "slack_command_key": config["slack_command_key"]
            }
            self.slack = {
                "token": config["slack_token"],
                "channel": config["default_slack_channel"]
            }
            self.chatgpt = {
                "key": config["openai_api_key"]
            }
        except FileNotFoundError as e:
            print(f"Error loading config from {config_file}: {e}")
        except Exception as e:
            print(f"Error loading config: {e}")

