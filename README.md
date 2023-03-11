# ChatGPT-Slackbot

## Prerequisites

Before you begin, make sure you have the following:

- An OpenAI Account
- An AWS Account
- A Slack Account

## Setup

Follow these steps to set up the ChatGPT-Slackbot:

1. Create an account and obtain an API key from https://platform.openai.com/ .
   - After creating your account, obtain a key from https://platform.openai.com/account/api-keys
   - Save this key for later. It will be added it to `config_file.json` file as `openai_api_key`

2. Generate the following keys using your preferred password generator such as https://passwordsgenerator.net/. These keys are used to validate access to the Lambda function and should be added to the `config_file.json` file. It is recommended to generate a keys no less than 32 characters with upper and lower case letters and numbers. Symbols in the keys has not been tested. Each key must be unique!
    - `chatgpt_relay_key`
    - `slack_event_key`
    - `slack_command_key`

3. Configure AWS Lambda layer for openai python package
   1. In AWS, Navigate to Lambda > Layers
   2. Select "Create Layer"
   3. Select "Upload a .zip file"
   4. Select `aws_openai_layer.zip` provided in this repository 
   5. Select Compatible architecture "x86_64"
   6. Select Compatible runtimes "Python 3.9"

4. Create a function in AWS Lambda called `ChatGPT-Slackbot`.
    1. Note: The name `ChatGPT-Slackbot` is very important as it is hard-coded into the gatekeeper. 
    2. In AWS, Navigate to Lambda > Functions 
    3. Select "Create Function"
    4. Select "Author from scratch"
    5. Select Runtime "Python 3.9"
    6. Select Architecture "x86_64"
    7. Under Advanced Settings, Select "Enable function URL"
    8. Under Advanced Settings, Select Auth type "None"
    9. Select "Create Function"
    10. Select "Upload from"
    11. Select ".zip file"
    12. Select `lambda_function.zip` provided in this repository 
    13. Enter `openai_api_key`, `chatgpt_relay_key`, `slack_event_key`, `slack_command_key` into `config_file.json`
    14. Scroll down to the bottom to select "Add a layer"
    15. Select "Custom Layers"
    16. Select the "openai" layer created in step 3
    17. Navigate to Lambda > Functions > ChatGPT-Slackbot > Configuration > General Configuration
    18. Select "Edit"
    19. Change Memory to "1024" (Adjust as needed)
    20. Change Timeout to "5 minutes" (Adjust as needed)
    21. Select "Save"


5. Update IAM permissions
   1. In AWS, Navigate to IAM > Roles
   2. Locate the role for the ChatGPT Lambda labeled `ChatGPT-Slackbot-role-xxxxxxxx`
   3. Edit the policy on the role 
   4. Add the following rule to the policy
   ```javascript
     {
       "Effect": "Allow",
       "Action": [
         "lambda:InvokeFunction",
         "lambda:GetFunction"
       ],
       "Resource": "arn:aws:lambda:us-east-1:{AccountNumber}:function:ChatGPT-Slackbot"
     }
   
6. Identify the URLs to use with slack
   - `@chatgpt` will use https://`functionURL`/?apikey=`slack_event_key`
   - `/chatgpt` will use https://`functionURL`/?apikey=`slack_command_key`

7. Create your Slack application.
   1. Navigate to https://api.slack.com/apps
   2. Select `Create New App`
   3. Select Create App "From Scratch"
   4. Enter App Name "ChatGPT"
   5. Select the workspace to develop app in
   6. Select "Create App"
   7. Navigate to Event Subscriptions
   8. Select "Enable Events"
   9. Enter the `@chatgpt` url from step 6 as the Request URL
   10. Subscribe to bot events "app_mention"
   11. Select "Save Changes"
   12. Navigate to "Slash Commands"
   13. Select "Create New Command"
   14. Enter "/ChatGPT" as Command
   15. Enter `/chatgpt` url from step 6 as the Request URL
   16. Enter "Send message to ChatGPT" as the "Short Description"
   17. Select "Save"
   18. Navigate to "OAuth & Permissions"
   19. Under "Scopes" select "Add an OAuth Scope"
   20. Select "chat:write"
   21. Under "OAuth Tokens for Your Workspace" select "Install to Workspace"
   22. Save the `Bot User OAuth Token` as `slack_token` in `config_file.json` within the Lambda

8. Identify the desired Default Slack Channel ID
   1. In slack, right-click on the desired Default Slack Channel
   2. Select "View Channel Details"
   3. "Channel ID" is found at the bottom of the window
   4. Save "Channel ID" as `default_slack_channel` in `config_file.json` within the Lambda

9. ChatGPT Slackbot should now be fully setup
   1. Test with `@ChatGPT /help`
   2. Test with `@chatgpt how far is the sun?`
   3. Test with `/ChatGPT /reset`