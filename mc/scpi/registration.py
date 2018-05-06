"""A module for handling registration on behalf of a SmartCan

Classes:
    Registration -- A class for registering a can with the django server

Exceptions:
    ResponseContainsError -- A JSON network response conained an error field

Functions:
    raise_response_error -- If response data contains an error, raise an error
        with that msg
"""
import getpass
import json
import os
import sys
import uuid
import warnings
from typing import Tuple

import requests


DJANGO_PORT = 8000
# TODO: Set to HTTPS
HOSTNAME = 'http://ec2-34-203-249-228.compute-1.amazonaws.com'
LOGIN_ENDPOINT = 'admin/login/'
REGISTER_ENDPOINT = 'config/register/submit/'


def raise_response_error(response: requests.Response):
    """If response data contains an error, raise an error with that msg"""
    print(response)
    print(response.json())
    if 'error' in response.json():
        raise ResponseContainsError(response)


class ResponseContainsError(Exception):
    """A JSON network response conained an error field

    Args:
        response {[requests.Response]} -- The response that contains the error

    Attributes:
        message {str} -- The error contained in the response
        response {[requests.Response]} -- The response that contains the error
    """
    def __init__(self, response: requests.Response):
        super(ResponseContainsError, self).__init__()
        self.message = "Error was: " + response.json()['error']
        self.response = response


class Registration:
    """A class for registering a can with the django server.

    Raises:
        UserWarning -- Warns if config cannot be saved to disk

    Args:
        config_file_name {str} -- File name, should contain extension.
            (default: {'config.json'})
        hostname {str} -- The API hostname, should not contain protocol or port.
            (default: {'HOSTNAME'})

    Attributes:
        config {Dictionary} -- A dictionary representation of the configuration
        config_file_name {str} -- The filename of the configuration on disk
        hostname {str} -- The hostname of the django server to register with
    """

    def __init__(self, config_file_name: str = 'config.json',
                 hostname: str = HOSTNAME):
        self.config = {}
        self.config_file_name = config_file_name
        self.hostname = hostname
        self._try_load_config()

    def is_registered(self) -> bool:
        """Determines if the smartcan is registered.

        Returns:
            Bool -- True if registered (config file exists and contains a pw),
                otherwise False
        """
        return self._try_load_config() and 'password' in self.config

    def register(self) -> None:
        """Creates a new registration on the server for the can.

        Note: Should be called after a config is generated.

        Raises:
            UserWarning -- Raised if config cannot be saved to disk

        Returns:
            None
        """
        # Load config, and if a new one is created, try to save it to disk
        if not self._try_load_config():
            print("No configuration found on disk, creating new configuration.")
            self._try_create_config()

        # Get a csrftoken so we can POST to django
        client = requests.session()
        login_url = requests.compat.urljoin(f'{self.hostname}:{DJANGO_PORT}', LOGIN_ENDPOINT)
        print("login to " + login_url)
        client.get(login_url).raise_for_status()
        csrftoken = client.cookies['csrftoken']

        # POST to login page with owner credentials
        (user, password) = self._prompt_owner_creds()
        login_data = {
            'username':user,
            'password':password,
            'csrfmiddlewaretoken':csrftoken,
            'next': requests.compat.urljoin(f'{self.hostname}:{DJANGO_PORT}', 'config/')
        }
        login_resp = client.post(login_url, data=login_data)
        login_resp.raise_for_status()

        # POST to registration page while logged in as owner
        register_end = f'''{REGISTER_ENDPOINT}/{self.config['uuid']}'''
        register_url = requests.compat.urljoin(f'{self.hostname}:{DJANGO_PORT}', register_end)
        register_resp = client.get(register_url)
        csrftoken = client.cookies['csrftoken']
        register_data = {
            'number_bins': self.config['num_bins'],
            'csrfmiddlewaretoken': csrftoken
        }
        register_resp = client.post(register_url, register_data)
        register_resp.raise_for_status()
        raise_response_error(register_resp)

        # Update config and try to save it
        can_pw = register_resp.json()['password']
        self.config['password'] = can_pw
        self._try_save_config()

    # TODO: See if there is a way to do this securely
    def _prompt_owner_creds(self) -> Tuple[str, str]:
        """Returns a tuple of the owner's credentials as input by the user.

        Raises:
            UserWarning -- From getpass, if password will be shown on terminal

        Returns:
            Tuple -- (username: str, password: str)
        """
        print("A can owner's account credentials are required to register a can.")
        print(f"""This can will be registered as the user: '{self.config['uuid']}'""")
        print("Please enter the can owner's username and password below:")
        owner_user = input("Username: ")
        owner_pw = getpass.getpass()
        return (owner_user, owner_pw)

    def _try_create_config(self, b_uuid: uuid.UUID = None, num_bins=3) -> bool:
        """Tries to create a new config and save it to disk.

        Keyword Arguments:
            b_uuid {uuid.UUID} -- The bin's UUID that doubles as its username
                (default: {None})
            num_bins {int} -- The number of bins that the can has (default: {3})

        Returns:
            bool -- True if the config was saved to disk, False otherwise.
        """
        if not b_uuid:
            b_uuid = uuid.uuid4()

        config = {'uuid': str(b_uuid), 'num_bins': num_bins}
        self.config = config
        return self._try_save_config()

    def _try_load_config(self) -> bool:
        """
        Tries to load the JSON config file.

        Raises:
            UserWarning -- Raises warning if config cannot be saved to disk

        Returns:
            bool -- True if the config was loaded, False otherwise
        """
        script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        config_loc = os.path.join(script_dir, self.config_file_name)

        try:
            with open(config_loc) as config_file:
                self.config = json.load(config_file)
                return True
        except (IOError, OSError):
            return False

    def _try_save_config(self) -> bool:
        """
        Tries to save the current config to disk at config_file_name.

        Returns:
            bool -- True if the config was saved, False otherwise
        """
        try:
            with open(self.config_file_name, 'w') as config_file:
                json.dump(self.config, config_file)
            return True
        except (IOError, OSError)as err_msg:
            warnings.warn(f"Config could not be saved to disk. Error: {err_msg}")
            return False


def main():
    """Does full registration process

    Script goes throught the registration process. The script will first
    authenticate with owner credentials. The can will recieve its newly created
    credentials from the server as a response from the register POST.
    """
    registration = Registration(config_file_name='test_config.json')
    if not registration.is_registered():
        registration.register()
    print("Now do other stuff...")

if __name__ == "__main__":
    main()
