from django.urls import path

from channels.routing import ProtocolTypeRouter, URLRouter

from VoteHandler.consumers import CommanderConsumer


application = ProtocolTypeRouter({
    # (http-> django views is added by default)

    #TODO: Wrap in AuthMiddleware
    "websocket": URLRouter([
        path("ws/", CommanderConsumer)
    ])
})