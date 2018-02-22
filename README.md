# Smart Can API Handler for votes and more 


## Main versions

    - Django 2.1 

    - Python 3.5


## Misc. Install Notes

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
    

    
