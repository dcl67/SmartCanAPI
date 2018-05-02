SmartCanPi
==========
Code that will run on the raspberry pi for SmartCan.
Controls the motors and connects to the API via the Requests library.

Setup
-----
1) Install Python 3.6
2) Navigate to the root directory of this project, create a virtual environment with the command "virtualenv --python=/usr/bin/python3.6 venv"
3) Activate the env with "source env/bin/activate"
4) run "pip install -r requirements.txt"

### Python 3.6 on the rPi
- Follow the directions [here](https://raspberrypi.stackexchange.com/questions/59381/how-do-i-update-my-rpi3-to-python-3-6)
- Replace the version number for python in the URL with 3.6.5

Misc
----
- The ".keep" files simply prevent the directory from being empty and therefore not kept in source due to how git treats empty folders.
