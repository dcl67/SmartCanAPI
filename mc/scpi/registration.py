import getpass
import json
import os
import sys
import uuid

import requests

class Registration():
    """A class for registering a can with the django server.
    
    Raises:
        UserWarning -- Warns if config cannot be saved to disk
    """

    # TODO: Update with public address
    def __init__(self, config_file_name: str='config.json', 
                 hostname: str='localhost'):
        """        
        Keyword Arguments:
            config_file_name {str} -- File name, should contain extension. (default: {'config.json'})
            hostname {str} -- The API hostname, should not contain protocol or port. (default: {'localhost'})
        """

        self.config = None
        self.config_file_name = config_file_name
        self.hostname = hostname

    def create_config(self, b_uuid: uuid.UUID=None, num_bins: int=3):
        """Tries to create a new config and save it to disk.
        
        Keyword Arguments:
            b_uuid {uuid.UUID} -- The bin's UUID that doubles as its username (default: {None})
            num_bins {int} -- The number of bins that the can has (default: {3})
        
        Returns:
            Bool -- True if the config was saved to disk, False otherwise.
        """

        if not b_uuid:
            b_uuid = uuid.uuid4()

        config = {'uuid': str(b_uuid), 'num_bins': num_bins}
        self.config = config
        return self.try_save_config()

    def is_registered(self):
        """Determines if the smartcan is registered.
        
        Returns:
            Bool -- True if registered (config file exists and contains a pw), 
                    otherwise False
        """

        return self.try_load_config() and self.config['pass'] != None

    # TODO: See if there is a way to do this securely
    def prompt_owner_creds(self):
        '''
        Returns a tuple of the owner's credentials as input by the user.
        '''
        print("A can owner's account credentials are required to register a can.")
        print(f"""This can will be registered as the user: '{self.config['uuid']}'""")
        print("Please enter the can owner's username and password below:")
        owner_user = input("Username: ")
        owner_pw = getpass.getpass()
        return (owner_user, owner_pw)

    def register(self):
        '''
        Creates a new registration on the server for the can.
        Should be called after a config is generated.
        '''
        if not self.try_load_config():
            print("No configuration found on disk, creating new configuration.")
            if not self.create_config():
                raise UserWarning("Config could not be saved to disk.")

        endpoint = f'''config/register/submit/{self.config['uuid']}'''
        url = requests.compat.urljoin(f'https://{self.hostname}:8000', endpoint)
        auth = self.prompt_owner_creds()
        r = requests.post(url, {'number_bins': self.config['num_bins']}, auth=auth)
        r.raise_for_status()

        can_pw = r.json()['password']
        self.config['pass'] = can_pw
        self.try_save_config()
        
    def try_load_config(self):
        '''
        Loads the JSON config file.
        Returns True if config was successfully loaded, false otherwise
        '''
        script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        config_loc = os.path.join(script_dir, self.config_file_name)

        try:
            with open(config_loc) as config_file:
                self.config = json.load(config_file)
                return True
        except:
            return False

    def try_save_config(self):
        """
        Tries to save the current config to disk at config_file_name.
        
        Returns:
            Bool -- True if the config was saved, False otherwise
        """

        try:
            with open(self.config_file_name, 'w') as config_file:
                json.dump(self.config, config_file)
            return True
        except:
            return False


def main():
    '''
    Script goes throught the registration process. The script will first authenticate
    with owner credentials. The can will recieve its newly created credentials 
    from the server as a response from the register POST.
    '''
    registration = Registration()
    if not registration.is_registered():
        registration.register()
    print("Now do other stuff...")

if __name__ == "__main__":
    main()
