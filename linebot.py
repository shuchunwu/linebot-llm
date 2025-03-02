import os
import json
import requests

class LineBot:
    """
    LineBot class to handle LINE API request and response.
    """
    def __init__(self):
        self.line_chanel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
        self.line_api_reply_endpoint = "https://api.line.me/v2/bot/message/reply"

    def extract_message(self, body):
        """
        extract message from LINE API request body

        Args:
            body: request body from LINE API

        Returns:
            self-defined (dictionary): dictionary of extracted message
        """
        parsed = json.loads(body)
        print(parsed)
        event = parsed["events"][0]
        reply_token = event["replyToken"]
        message_type = event["message"]["type"]
        message_text = event["message"].get("text", "")
        user_id = event["source"]["userId"]
        group_id = event["source"]["groupId"] if event["source"]["type"] == "group" else ""

        if message_type == "text":
            return {
                "message": message_text,
                "message_type": message_type,
                "reply_token": reply_token,
                "user_id": user_id,
                "group_id": group_id
            }
        
        return {}

    def reply_message(self, reply_token, message):
        """
        reply message to LINE API

        Args:
            reply_token (string): reply token from LINE API
            message (string): message to be replied
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.line_chanel_access_token}"
        }
        data = {
            "replyToken": reply_token,
            "messages": [
                {
                    "type": "text",
                    "text": message,
                }
            ]
        }
        res = requests.post(self.line_api_reply_endpoint, headers=headers, data=json.dumps(data))
        print("Response " + res.text)
