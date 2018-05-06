# Smart Can API Handler for votes and more 


## Main versions

- Django 2.1 

- Python 3.6

## Main endpoints

 - HTTP is at http://IP:8000/api
 - Config is at http://IP:8000/config
 - websocket is at ws://IP:8000/ws 

## Linting

 - pip install pylint-django
 - Add this to your VS Code settings:
  ```json
  "python.linting.pylintArgs": [
        "--load-plugins=pylint_django"
    ]
  ```

## Misc. Install Notes

### EC2
 - The package manager is yum
 1) `sudo yum groupinstall "Development Tools"` install gcc and other tools
 2) `sudo yum install python36-devel` config for python development
 2) Use yum to install python36
 3) Use python so install virtualenv, `sudo python3 -m pip virtualenv`
 - You'll want to use a virtual envirnoment like `virtualenv --python=/usr/lib/python3.6 env`

### Redis

 - Redis needs to be installed and running on the local server for websockets
 - For *nix you can download Redis from [here](https://redis.io/download) and follow the install directions
   1) To build, navigate to the download folder and type 'make'
   2) To run Redis: 'cd src' then './redis-server'
 - For Windows download the .exe [here](https://github.com/MicrosoftArchive/redis/releases)

### Installing django channels on windows

- Twisted installs pywin32

- pywin32 is djanky and the install script doesn't put the DLLs in the
      correct location or run the post install script

1) Go to where python is installed. Something like: 
    "C:\Users\karso\Documents\GitHub\SmartCanAPI\env\Scripts" and run the
    "pywin32_postinstall.py" 

2) Go to the pywin32 install folder. Something like:
    "C:\Users\karso\Documents\GitHub\SmartCanAPI\env\Lib\site-packages\pywin32_system32"
    copy the files "pythoncom35.dll" and "pythoncom35.dll" to the folder from
    step 2.
    
### Running Django on Mac
  1) brew install mysql
  2) export PATH=$PATH:/usr/local/mysql/bin
  3) brew install portaudio
    
