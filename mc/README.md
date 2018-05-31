SmartCanPi
==========
Code that will run on the raspberry pi for SmartCan.
Controls the motors and connects to the API via the Requests library.

Dev Setup
-----
1) Install Python 3.6
2) Navigate to the root directory of this project, create a virtual environment with the command `virtualenv --python=/usr/bin/python3.6 venv`
3) Activate the env with `source env/bin/activate`
4) run `pip install -r requirements.txt`

RPi Setup
-----

### Setting the python path
- Add the following to ~/.bashrc:
  `export PYTHONPATH={absolute path to the SmartCanAPI folder}`
- ex. /home/pi/SmartCanAPI/

### Building and Installing Python 3.6
- Follow the directions [here](https://stackoverflow.com/questions/41328451/ssl-module-in-python-is-not-available-when-installing-package-with-pip3)
- Use this as `python3`, without the 3 it will use python 2.7

### Connecting to the VPN
- Connect to the drexel VPN using the instructions [here](https://cs.uwaterloo.ca/twiki/view/CF/OpenConnect)

### Updating the Display Driver
- When conencting to the touchscreen for the first time, the dispolay will not scale and the colors will be skewed
- Follow the directions here to fix [this](https://l.messenger.com/l.php?u=https%3A%2F%2Flearn.adafruit.com%2Fadafruit-5-800x480-tft-hdmi-monitor-touchscreen-backpack%2Fraspberry-pi-config&h=ATNNiakcMEXnlUXH9UhTrdifml1isr4NaiATVXG2S6Lccxp58UHybRU88G4lbiSennek2EE7IUzxtAsWVdacy8aE_jSGUycsASCPVtAUPriutNh0cMx5MuUU)

Testing
-------

### Running tests in dev env
- Tests run via python unittest:
  `python -m unittest mc.scpi.resistor_reader`

### Referencing the scpi files
- These files are above the testing module's top-level, so to access them, be sure you set `$PYTHONPATH` to the mc dir

### Testing with ws
The websocket code doesn't know what redis server you are on, so make sure that any testing you do involving the rPI has the rPI targeting the same redis server as your django server is connected to. In most cases this should mean just test against the EC2 server when dealing with websockets.

Misc
----
- **WARNING: Unplug power before messing with GPIO ports, we don't want to kill another RPi**

- The ".keep" files simply prevent the directory from being empty and therefore not kept in source due to how git treats empty folders.
