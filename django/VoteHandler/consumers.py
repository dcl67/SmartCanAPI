from channels.generic.websocket import JsonWebsocketConsumer

# TODO: Import Config models
from Config.models import CanInfo
from .models import Category
from .exceptions import ClientError

class CommanderConsumer(JsonWebsocketConsumer):
    """
    This class represents the consumer sending commands to a SmartCan instance.
    Each instance can be thought of as representing the communication line
    between django and a particular SmartCan.
    So there should be one instnace of this class per connected SmartCan.
    """

    CONFIG_IS_NONE = "CONFIG_IS_NONE"

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = None

    ##### Websocket event handlers

    def connect(self) -> None:
        """
        Called when the ws is handshaking.
        """
        # TODO: Add some check that the can has authenticated with user creds
        self.accept()

        # We're going to want to keep the config accessible
        self.config = None

    def receive_json(self, content) -> None:
        """
        Called when we receive a text frame.
        Channels handles decoding the JSON and gives us it as content.
        This is where we handle any requests from the SmartCan (shouldn't be
        that many commands).
        """
        # Messages have a command we can switch on
        command = content.get("command", None)

        try:
            if command == "config":
                if self.config is None:
                    raise ClientError(self.CONFIG_IS_NONE)
                self.get_can_config()
            elif command == "identify_by_uuid":
                self.config = self.get_config_by_uuid(content["uuid"])

            elif command == "echo":
                self.echo(content["message"])
        except ClientError as c_e:
            # send the error code to the can
            self.send_json({"error": c_e.code})

    def disconnect(self, code) -> None:
        try:
            self.remove_config_cn()
        except ClientError:
            pass

    ##### Helpers for receive_json

    def get_can_config(self) -> str:
        """
        """
        # TODO: Figure out what info from self.config to send
        pass

    def get_config_by_uuid(self, uuid) -> CanInfo:
        """
        Returns the config object with the matching uuid.
        Raises a ClientError if there is no matching uuid or if there is a
        matching uuid but the user does not have the rights to access it.
        """
        pass

    def echo(self, message: str) -> None:
        """
        Simply echos back a message so we can do simple testing.
        """
        self.send_json({
            "message": message
        })

    ##### Handlers for messages sent over the channel layer
        # These helper methods are named by the types we send
        # ex. chat.join becomes chat_join
        # They're how we receive messages from other consumers in django

        # These will be called if we want to operate on our Consumer from
        # somewhere else in the application

    def ws_rotate(self, category: Category):
        """
        Send the bin number for the SmartCan to rotate to.
        Raises ClientError if there is no Config with bin info.
        Raises ValueError if category is None.
        """
        if self.config is None:
            raise ClientError(self.CONFIG_IS_NONE)
        if category is None:
            raise ValueError("category cannot be None or empty")
        self.send_json({
            "command": "rotate",
            "position" : str(category.id)
        })

    ##### Other funcs

    def ask_for_uuid(self):
        """
        Ask the SmartCan to send us back its uuid.
        SmartCan should respond with an identify_by_uuid.
        """
        self.send_json({
            "command": "provide_uuid"
        })

    def remove_config_cn(self):
        """
        Removes the unique channel name from the Config for this can.
        Raises a ClientError if there is not already a config set.
        """
        pass

    def set_config_cn(self):
        """
        Set the unique channel name from the Config for this can.
        Raises a ClientError if the operation fails.
        """
        # TODO: wrap in try/except (raise ClientError on error)
        # self.configuration.channel_name = self.channel_name
        pass
