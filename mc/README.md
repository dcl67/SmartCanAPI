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

### VPN on rPI
- Connect to the drexel VPN using the instructions [here](https://cs.uwaterloo.ca/twiki/view/CF/OpenConnect)

Testing
-------

### Running tests
- Tests run via python unittest
- Ex. `python -m unittest mc.scpi.resistor_reader`

### Referencing the scpi files
- These files are above the testing module's top-level, so to access them, the parent folder needs to be added to path
- This can be accomplished with code:
  ```python
  import sys
  sys.path.append("..") 
  ```

### Testing with ws
The websocket code doesn't know what redis server you are on, so make sure that any testing you do involving the rPI has the rPI targeting the same redis server as your django server is connected to. In most cases this should mean just test against the EC2 server when dealing with websockets.

Misc
----
- The ".keep" files simply prevent the directory from being empty and therefore not kept in source due to how git treats empty folders.
