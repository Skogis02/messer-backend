import json
from channels.generic.websocket import WebsocketConsumer


def login_required(endpoint):
    def protected_endpoint(*args, **kwargs):
        self = args[0]
        assert type(self) == APIConsumer, TypeError("Missing arg 'self'!")
        if not self.user.is_authenticated:
            self.send("Authentication required: Please log in.")
            return
        endpoint(*args, **kwargs)

    return protected_endpoint


class APIConsumer(WebsocketConsumer):
    """
        Requires the following endpoints:

        - Sending a message
        - Making a friends request

        Future:

        - Reacting to a message
        - Searching for usernames
        - Login/Logout/Register

        A message is expected to use the following format:

        {
        type: "<TYPE>",
        value: {<OBJECT>}
        }

        """

    def __init__(self):
        super().__init__(self)
        self.user = None
        self.endpoints = {
            "send_message": self.send_message,
            "send_friends_request": None,
        }

    def connect(self):
        user = self.scope["user"]
        print(user)
        self.accept()
        self.user = self.scope['user']

    def receive(self, text_data=None, bytes_data=None):
        try:
            msg = json.loads(text_data)
        except json.JSONDecodeError as e:
            print(e)
            self.send("Invalid format.")
            return
        if 'endpoint' not in msg:
            self.send("Missing key 'endpoint'.")
            return
        elif 'data' not in msg:
            self.send("Missing key 'data''.")
            return
        msg_endpoint, msg_data = msg['endpoint'], msg['data']
        if msg_endpoint not in self.endpoints:
            self.send("'Invalid endpoint.")
            return
        endpoint = self.endpoints[msg_endpoint]
        endpoint(msg_data)
        return

    @login_required
    def send_message(self, data):

        """
        Required fields:

        -'friend'
        -'content'
        """

        if 'friend' not in data:
            self.send("Object 'data' missing key 'friend'.")
            return
        elif 'content' not in data:
            self.send("Object 'data' missing key 'content'.")
            return
        friend_username = data['friend']
        friend_queryset = self.user.friends.filter(username=friend_username)
        if not friend_queryset.exists():
            self.send("The provided user is not in your friends list.")
        self.send(f"sending message to {friend_username}")








