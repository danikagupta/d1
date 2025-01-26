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
    def __init__(self, bot_token: str, app_token: str = None):
        """Initialize the bot with bot token and optionally app token for socket mode."""
        logger.info("[SlackBot] Initializing bot with provided tokens")
        self.client = WebClient(token=bot_token)
        if app_token:
            self.socket_client = SocketModeClient(
                app_token=app_token,
                web_client=self.client
            )
        else:
            self.socket_client = None
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
            
            # Handle both regular messages and DM messages
            if (event["type"] == "message" or event["type"] == "message.im") and "subtype" not in event:
                channel = event.get("channel")
                user = event.get("user")
                text = event.get("text")
                
                # Log the full event type for debugging
                logger.info(f"[SlackBot] Processing event type: {event['type']} in channel type: {event.get('channel_type', 'unknown')}")
                
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
                    # Extract additional metadata
                    event_ts = event.get("ts", "N/A")
                    team_id = event.get("team", "N/A")
                    channel_type = "DM" if event.get("channel_type") == "im" else "Channel"
                    
                    # Get user info for display name
                    try:
                        user_info = self.client.users_info(user=user)
                        display_name = user_info["user"]["profile"].get("display_name") or user_info["user"]["name"]
                    except Exception as e:
                        logger.error(f"[SlackBot] Error fetching user info: {str(e)}")
                        display_name = user
                    
                    # Format response with metadata
                    word_count = self.count_words(text)
                    response = (
                        f"*Message Analysis*\n"
                        f"• Word Count: {word_count}\n"
                        f"• Original Text: {text}\n"
                        f"• Sent By: {display_name} (ID: {user})\n"
                        f"• Timestamp: {event_ts}\n"
                        f"• Channel Type: {channel_type}\n"
                        f"• Channel/DM ID: {channel}\n"
                        f"• Team ID: {team_id}"
                    )
                    
                    try:
                        self.client.chat_postMessage(
                            channel=channel,
                            text=response,
                            mrkdwn=True  # Enable Slack markdown formatting
                        )
                        logger.info(f"[SlackBot] Sent response with metadata: {response}")
                    except Exception as e:
                        logger.error(f"[SlackBot] Error sending response: {str(e)}")
                else:
                    logger.warning(f"[SlackBot] Incomplete message event received: channel={channel}, user={user}, has_text={bool(text)}")
            else:
                logger.info(f"[SlackBot] Skipping non-message event or message with subtype: {event.get('subtype', 'no subtype')}")
                    
    def start(self):
        """Start the Socket Mode client if configured for socket mode."""
        if not self.socket_client:
            logger.info("[SlackBot] Not starting Socket Mode - running in Lambda mode")
            return
            
        logger.info("[SlackBot] Starting Socket Mode client...")
        try:
            self.socket_client.socket_mode_request_listeners.append(self.process_event)
            logger.info("[SlackBot] Added event listener")
            self.socket_client.connect()
            logger.info("[SlackBot] Socket Mode connection initiated")
        except Exception as e:
            logger.error(f"[SlackBot] Failed to start Socket Mode client: {str(e)}")
            raise
            
    def process_message_event(self, event: dict):
        """Process a single message event from Lambda."""
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
            # Extract additional metadata
            event_ts = event.get("ts", "N/A")
            team_id = event.get("team", "N/A")
            channel_type = "DM" if event.get("channel_type") == "im" else "Channel"
            
            # Get user info for display name
            try:
                user_info = self.client.users_info(user=user)
                display_name = user_info["user"]["profile"].get("display_name") or user_info["user"]["name"]
            except Exception as e:
                logger.error(f"[SlackBot] Error fetching user info: {str(e)}")
                display_name = user
            
            # Format response with metadata
            word_count = self.count_words(text)
            response = (
                f"*Message Analysis*\n"
                f"• Word Count: {word_count}\n"
                f"• Original Text: {text}\n"
                f"• Sent By: {display_name} (ID: {user})\n"
                f"• Timestamp: {event_ts}\n"
                f"• Channel Type: {channel_type}\n"
                f"• Channel/DM ID: {channel}\n"
                f"• Team ID: {team_id}"
            )
            
            try:
                self.client.chat_postMessage(
                    channel=channel,
                    text=response,
                    mrkdwn=True  # Enable Slack markdown formatting
                )
                logger.info(f"[SlackBot] Sent response with metadata: {response}")
            except Exception as e:
                logger.error(f"[SlackBot] Error sending response: {str(e)}")
                raise
