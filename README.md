SmartCanAPI
===========
Senior Design Project: Smart Can's API for handling 

Django
------
This contains code related to the django instance and is where the REST API code, models, and Consumers live

mc
------
This contains code that runs on the rPi. Includes motor control, websockets, and client-side API

### Testing with ws
The websocket code doesn't know what redis server you are on, so make sure that any testing you do involving the rPI has the rPI targeting the same redis server as your django server is connected to. In most cases this should mean just test against the EC2 server when dealing with websockets.
