import json
import os
import hmac
import hashlib
import time
from typing import Dict, Any
from base64 import b64decode
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .slack_bot import SlackWordCountBot

def verify_slack_signature(event: Dict[str, Any]) -> bool:
    """Verify that the request actually came from Slack"""
    slack_signing_secret = os.environ['SLACK_SIGNING_SECRET'].encode('utf-8')
    slack_signature = event['headers'].get('x-slack-signature', '')
    slack_request_timestamp = event['headers'].get('x-slack-request-timestamp', '')
    
    # Verify request is not too old
    if abs(time.time() - int(slack_request_timestamp)) > 60 * 5:
        return False
        
    sig_basestring = f"v0:{slack_request_timestamp}:{event['body']}"
    my_signature = 'v0=' + hmac.new(
        slack_signing_secret,
        sig_basestring.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(my_signature.encode('utf-8'), slack_signature.encode('utf-8'))

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda handler for Slack events"""
    # Initialize response
    response = {
        'statusCode': 200,
        'body': json.dumps({'ok': True})
    }
    
    # Verify the request came from Slack
    if not verify_slack_signature(event):
        response['statusCode'] = 403
        response['body'] = json.dumps({'error': 'Invalid signature'})
        return response
    
    # Parse the request body
    body = json.loads(event['body'])
    
    # Handle Slack URL verification challenge
    if 'challenge' in body:
        response['body'] = json.dumps({'challenge': body['challenge']})
        return response
    
    # Initialize Slack client
    slack_bot_token = os.environ['SLACK_BOT_TOKEN']
    bot = SlackWordCountBot(slack_bot_token)
    
    # Process the event
    if 'event' in body:
        slack_event = body['event']
        
        # Handle message events (both channel messages and DMs)
        if (slack_event['type'] == 'message' or slack_event['type'] == 'message.im') and 'subtype' not in slack_event:
            channel = slack_event.get('channel')
            user = slack_event.get('user')
            text = slack_event.get('text')
            
            if channel and user and text:
                try:
                    # Process the message using existing SlackWordCountBot logic
                    bot.process_message_event(slack_event)
                except Exception as e:
                    print(f"Error processing message: {str(e)}")
                    response['statusCode'] = 500
                    response['body'] = json.dumps({'error': 'Internal server error'})
    
    return response
