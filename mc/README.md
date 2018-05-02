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
- Follow the directions [here](https://stackoverflow.com/questions/41328451/ssl-module-in-python-is-not-available-when-installing-package-with-pip3)

Misc
----
- The ".keep" files simply prevent the directory from being empty and therefore not kept in source due to how git treats empty folders.
