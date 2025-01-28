import asyncio
import logging
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.errors import SlackApiError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SlackWordCountBot')

class SlackWordCountBot:
    def __init__(self, bot_token: str, app_token: str):
        """Initialize the bot with both bot token and app-level token."""
        logger.info("[SlackBot] Initializing bot with provided tokens")
        self.client = WebClient(token=bot_token)
        self.socket_client = SocketModeClient(
            app_token=app_token,
            web_client=self.client
        )
        logger.info("[SlackBot] Initialization complete")
        
    def count_words(self, text: str) -> int:
        """Count words in a message."""
        return len(text.split())
    
    async def handle_message(self, channel: str, user: str, text: str):
        """Handle incoming message and respond with word count."""
        logger.info(f"[SlackBot] Processing message: '{text[:50]}...' from user {user}")
        word_count = self.count_words(text)
        try:
            response = f"Your message contains {word_count} words."
            logger.info(f"[SlackBot] Sending response to channel {channel}")
            await self.client.chat_postMessage(
                channel=channel,
                text=response,
                thread_ts=None  # Will create a new message, not a thread
            )
            logger.info("[SlackBot] Response sent successfully")
        except SlackApiError as e:
            error_msg = e.response['error']
            logger.error(f"[SlackBot] Error sending message: {error_msg}")
            raise  # Re-raise to allow proper error handling
            
    def process_event(self, client: SocketModeClient, req: SocketModeRequest):
        """Process incoming Socket Mode events."""
        logger.info(f"[SlackBot] Received event: {req.type}")
        logger.debug(f"[SlackBot] Full event payload: {req.payload}")
        
        if req.type == "events_api":
            # Acknowledge the request
            response = SocketModeResponse(envelope_id=req.envelope_id)
            client.send_socket_mode_response(response)
            logger.info("[SlackBot] Acknowledged event request")
            
            # Process the event
            event = req.payload["event"]
            logger.info(f"[SlackBot] Event type: {event.get('type')}")
            
            if event["type"] == "message" and "subtype" not in event:
                channel = event.get("channel")
                user = event.get("user")
                text = event.get("text")
                
                # Get bot's own user ID if we haven't stored it yet
                if not hasattr(self, 'bot_user_id'):
                    try:
                        auth_response = self.client.auth_test()
                        self.bot_user_id = auth_response["user_id"]
                        logger.info(f"[SlackBot] Bot user ID: {self.bot_user_id}")
                    except Exception as e:
                        logger.error(f"[SlackBot] Error getting bot user ID: {str(e)}")
                        self.bot_user_id = None

                # Ignore messages from the bot itself
                if user == self.bot_user_id:
                    logger.info("[SlackBot] Ignoring message from self")
                    return
                
                if channel and user and text:
                    logger.info(f"[SlackBot] Processing message: '{text}' from user {user} in channel {channel}")
                    # Run handle_message directly without create_task
                    word_count = self.count_words(text)
                    response = f"Your message contains {word_count} words."
                    try:
                        self.client.chat_postMessage(
                            channel=channel,
                            text=response
                        )
                        logger.info(f"[SlackBot] Sent response: {response}")
                    except Exception as e:
                        logger.error(f"[SlackBot] Error sending response: {str(e)}")
                else:
                    logger.warning(f"[SlackBot] Incomplete message event received: channel={channel}, user={user}, has_text={bool(text)}")
            else:
                logger.info(f"[SlackBot] Skipping non-message event or message with subtype: {event.get('subtype', 'no subtype')}")
                    
    def start(self):
        """Start the Socket Mode client."""
        logger.info("[SlackBot] Starting Socket Mode client...")
        try:
            self.socket_client.socket_mode_request_listeners.append(self.process_event)
            logger.info("[SlackBot] Added event listener")
            self.socket_client.connect()
            logger.info("[SlackBot] Socket Mode connection initiated")
        except Exception as e:
            logger.error(f"[SlackBot] Failed to start Socket Mode client: {str(e)}")
            raise
