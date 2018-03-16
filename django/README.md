# Smart Can API Handler for votes and more 


## Main versions

- Django 2.1 

- Python 3.5

## Main endpoints

 - HTTP is at http://IP:8000/api
 - Config is at http://IP:8000/config
 - websocket is at ws://IP:8000/ws 


## Misc. Install Notes

### Redis

 - Redis needs to be installed and running on the local server for websockets
 - For *nix you can download Redis from [here](https://redis.io/download) and follow the install directions
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
    

    
