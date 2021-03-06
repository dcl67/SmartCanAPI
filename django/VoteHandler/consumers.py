from channels.generic.websocket import JsonWebsocketConsumer
from contextlib import suppress

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from Config.models import Bin, CanInfo
from .models import Category
from .exceptions import ClientError


class CommanderConsumer(JsonWebsocketConsumer):
    """
    This class represents the consumer sending commands to a SmartCan instance.
    Each instance can be thought of as representing the communication line
    between django and a particular SmartCan.
    So there should be one instnace of this class per connected SmartCan.
    """
    # TODO: Move these CientError constants and the ws constants to a new file
    CONFIG_IS_NONE = "CONFIG_IS_NONE"
    LOGIN_REJECTED = "LOGIN_REJECTED"
    NO_CONFIG_EXISTS = "NO_CONFIG_EXISTS"
    UNKNOWN_CMD = "UNKNOWN_COMMAND"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_info: CanInfo = None
        self.user: User = None

    ##### Websocket event handlers

    def connect(self) -> None:
        '''Called when the ws is handshaking'''
        # Just accept any connection, then ask it to authenticate
        self.accept()
        self.ask_for_identity()
        print(f'Unknown client has connected on channel \'{self.channel_name}\'')

    def receive_json(self, content) -> None:
        """
        Called when we receive a text frame.
        Channels handles decoding the JSON and gives us it as content.
        This is where we handle any requests from the SmartCan (shouldn't be
        that many commands).
        """
        # Messages have a command we can switch on
        command = content.get("command", None)

        # If the aren't authed just keep asking for valid credentials
        # In a production system we would want logic to prevent brute forcing
        if not self.authed() and command != 'identify':
            self.ask_for_identity()

        try:
            if command == 'identify':
                self.identify(content)
            elif command == 'echo':
                self.echo(content)
            else:
                raise ClientError(self.UNKNOWN_CMD)
        except ClientError as c_e:
            # send the error code to the can
            self.send_json({'error': c_e.code})
            if c_e.code == self.LOGIN_REJECTED:
                self.disconnect(401)

    def disconnect(self, code) -> None:
        print(f'Websocket \'{self.channel_name}\' disconnected with code {code}')
        if self.authed():
            try:
                self.remove_config_cn()
            except ClientError:
                pass

    ##### Helpers for receive_json

    def echo(self, content: dict) -> None:
        '''
        Simply echos back a message so we can do simple testing.
        '''
        self.send_json({'message': content.get('message')})

    def identify(self, content: dict) -> None:
        '''
        Called when a can attempts to identify.
        If the credentials are valid, self.user gets a value.
        Raises ClientError if credentials are invalid
        '''
        username = content.get('username')
        password = content.get('password')

        # user is None if the login fails
        self.user = authenticate(username=username, password=password)

        # Kick them off, politely
        if not self.authed():
            print(f'Unknown client failed to identify as {username}')
            raise ClientError(self.LOGIN_REJECTED)

        print(f'Client successfully identified as {username}')
        self.can_info = CanInfo.objects.get(owner=self.user)
        self.set_channel_name()
        self.send_info(f'Authentication as {username} was succesful')

    ##### Handlers for messages sent over the channel layer

        # These helper methods are named by the types we send
        # ex. chat.join becomes chat_join
        # They're how we receive messages from other consumers in django

        # These will be called if we want to operate on our Consumer from
        # somewhere else in the application

    def ws_rotate(self, event):
        """
        Send the bin number for the SmartCan to rotate to based on the
        category provided.

        Raises ClientError if there is no Config with bin info.
        Raises ValueError if there is no category field.
        """
        if self.can_info is None:
            raise ClientError(self.CONFIG_IS_NONE)
        if event.get('category') is None:
            raise ValueError("category cannot be None or empty")

        try:
            bin_num = None
            category = event['category']
            category_name = Category.objects.get(id=category).name
            with suppress(Bin.DoesNotExist):
                bin_num = Bin.objects.get(s_id=self.can_info, category=category).bin_num
            
            # If no matching bin was found, try the default bin
            if bin_num is None:
                default_cat = self.can_info.default_category
                bin_num = Bin.objects.get(s_id=self.can_info, category=default_cat).bin_num
                print(f'No matching bin for {category_name} on can {self.can_info}, '
                      f'defaulting to {default_cat} in bin {bin_num}')
        except Bin.DoesNotExist:
            print(f'No matching default bin for category {default_cat} on bin {self.can_info}')
            return
        except Category.DoesNotExist:
            print(f'Cannot send category to {self.can_info}. No category exists with id {category}')
            return

        print(f'DEBUG: Sending command to rotate to bin #{bin_num} on {self.channel_name}')
        self.send_json({
            "command": "rotate",
            "position" : str(bin_num)
        })

    ##### Other funcs

    def ask_for_identity(self) -> None:
        """
        Ask the SmartCan to send us back its uuid and password.
        SmartCan should respond with an identify.
        """
        self.send_json({
            "command": "identify"
        })

    def authed(self) -> bool:
        '''Whether or not there is a valid user assosciated with this socket'''
        return self.user is not None

    def remove_config_cn(self) -> None:
        """
        Removes the unique channel name from the Config for this can.
        Raises a ClientError if there is not already a can_info set.
        """
        if self.can_info is None or self.can_info.channel_name is None:
            raise ClientError(self.NO_CONFIG_EXISTS)
        self.can_info.channel_name = None
        self.can_info.save()

    def send_info(self, msg) -> None:
        '''Sends an information sting to the client. Useful for debugging.'''
        self.send_json({
            "command": "info",
            "message": msg
        })

    def set_channel_name(self) -> None:
        """
        Set the unique channel name from the Config for this can.
        Raises a ClientError if the operation fails.
        """
        if self.can_info is None:
            raise ClientError(self.NO_CONFIG_EXISTS)
        self.can_info.channel_name = self.channel_name
        self.can_info.save()
