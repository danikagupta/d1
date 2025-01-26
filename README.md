Here are the key files in /home/ubuntu/slackbot-wordcount/backend:
1. app/main.py - FastAPI server setup
2. app/slack_bot.py - Slackbot implementation
3. .env - Configuration file for tokens
   
To deploy:
1. Create Slack App with Socket Mode and Event Subscriptions enabled
2. Add bot scopes: chat:write, channels:history, groups:history, im:history
3. Configure .env with tokens
4. Run: poetry run fastapi dev app/main.py


Here's the complete deployment guide for the Slackbot:
1. Create a Slack App:
   - Go to api.slack.com/apps
   - Click "Create New App" > "From Scratch"
   - Name your app and select your workspace
2. Configure App Settings:
   - Enable Socket Mode (under "Socket Mode")
   - Generate and save the App-Level Token (xapp-)
   - Under "OAuth & Permissions", add these Bot Token Scopes:
     * chat:write
     * channels:history
     * groups:history
     * im:history
   - Install the app to your workspace
   - Save the Bot User OAuth Token (xoxb-)
3. Enable Event Subscriptions:
   - Go to "Event Subscriptions"
   - Turn the feature on
   - Under "Subscribe to bot events", add:
     * message.channels
     * message.groups
     * message.im
4. Project Setup:
   - Create project directory:
     
bash
     mkdir slackbot-wordcount
     cd slackbot-wordcount
     
   - Create virtual environment and install dependencies:
     
bash
     poetry init
     poetry add fastapi uvicorn python-dotenv slack-sdk[socket-mode]
     
   - Create .env file with your tokens:
     SLACK_BOT_TOKEN=xoxb-your-token
     SLACK_APP_TOKEN=xapp-your-token
     
5. Run the Bot:
   
bash
   poetry run fastapi dev app/main.py
   
6. Usage:
   - Invite the bot to your channel: /invite @your-bot-name
   - Send any message
   - Bot will respond with word count
